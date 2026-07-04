#!/bin/bash
# 大模型支持下的动作捕捉与视觉合成系统 V1.0
# 部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装"
        exit 1
    fi
    
    log_info "依赖检查通过"
}

# 检查环境变量
check_env() {
    log_info "检查环境变量..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            log_warn ".env 文件不存在，正在从 .env.example 复制..."
            cp .env.example .env
            log_warn "请编辑 .env 文件填入实际配置"
            exit 1
        else
            log_error ".env.example 文件不存在"
            exit 1
        fi
    fi
    
    log_info "环境变量检查通过"
}

# 构建镜像
build_images() {
    log_info "构建Docker镜像..."
    
    # 构建CPU版本
    docker-compose build app
    
    # 构建GPU版本（如果需要）
    if [ "$1" = "--gpu" ]; then
        docker-compose build gpu-service
    fi
    
    log_info "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动基础服务
    docker-compose up -d mysql redis
    
    # 等待数据库就绪
    log_info "等待数据库就绪..."
    sleep 10
    
    # 启动应用服务
    docker-compose up -d app
    
    # 启动GPU服务（如果需要）
    if [ "$1" = "--gpu" ]; then
        docker-compose up -d gpu-service
    fi
    
    # 启动Nginx
    docker-compose up -d nginx
    
    # 启动监控（如果需要）
    if [ "$2" = "--monitor" ]; then
        docker-compose up -d prometheus grafana
    fi
    
    log_info "服务启动完成"
}

# 检查服务状态
check_status() {
    log_info "检查服务状态..."
    
    docker-compose ps
    
    # 检查健康状态
    log_info "等待服务健康检查..."
    sleep 5
    
    # 检查API
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "✅ API服务正常"
    else
        log_error "❌ API服务异常"
    fi
    
    # 检查Nginx
    if curl -f http://localhost:80 > /dev/null 2>&1; then
        log_info "✅ Nginx服务正常"
    else
        log_error "❌ Nginx服务异常"
    fi
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    docker-compose down
    log_info "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    stop_services
    start_services "$@"
    log_info "服务重启完成"
}

# 查看日志
view_logs() {
    if [ -n "$1" ]; then
        docker-compose logs -f "$1"
    else
        docker-compose logs -f
    fi
}

# 备份数据
backup_data() {
    log_info "备份数据..."
    
    BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份数据库
    docker-compose exec mysql mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" mocap_db > "$BACKUP_DIR/database.sql"
    
    # 备份配置
    cp .env "$BACKUP_DIR/"
    cp docker-compose.yml "$BACKUP_DIR/"
    
    log_info "备份完成: $BACKUP_DIR"
}

# 恢复数据
restore_data() {
    if [ -z "$1" ]; then
        log_error "请指定备份目录"
        exit 1
    fi
    
    log_info "恢复数据: $1"
    
    # 恢复数据库
    docker-compose exec -T mysql mysql -u root -p"$MYSQL_ROOT_PASSWORD" mocap_db < "$1/database.sql"
    
    log_info "数据恢复完成"
}

# 显示帮助
show_help() {
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  start    启动服务"
    echo "  stop     停止服务"
    echo "  restart  重启服务"
    echo "  status   查看状态"
    echo "  logs     查看日志"
    echo "  backup   备份数据"
    echo "  restore  恢复数据"
    echo "  build    构建镜像"
    echo "  help     显示帮助"
    echo ""
    echo "选项:"
    echo "  --gpu      启用GPU支持"
    echo "  --monitor  启用监控系统"
    echo ""
    echo "示例:"
    echo "  $0 start --gpu --monitor"
    echo "  $0 logs app"
    echo "  $0 backup"
    echo "  $0 restore backup/20260703_120000"
}

# 主函数
main() {
    check_dependencies
    check_env
    
    case "$1" in
        start)
            start_services "$2" "$3"
            check_status
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services "$2" "$3"
            ;;
        status)
            check_status
            ;;
        logs)
            view_logs "$2"
            ;;
        backup)
            backup_data
            ;;
        restore)
            restore_data "$2"
            ;;
        build)
            build_images "$2"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            show_help
            exit 1
            ;;
    esac
}

main "$@"
