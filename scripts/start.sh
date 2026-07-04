#!/bin/bash
# 大模型支持下的动作捕捉与视觉合成系统 V1.0
# 快速启动脚本

set -e

echo "🚀 启动大模型支持下的动作捕捉与视觉合成系统 V1.0"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查Python环境
check_python() {
    echo "检查Python环境..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
    else
        echo "❌ Python3未安装"
        exit 1
    fi
}

# 检查依赖
check_dependencies() {
    echo "检查依赖..."
    
    # 检查核心依赖
    python3 -c "import torch; print(f'✅ PyTorch: {torch.__version__}')" 2>/dev/null || echo "⚠️ PyTorch未安装"
    python3 -c "import cv2; print(f'✅ OpenCV: {cv2.__version__}')" 2>/dev/null || echo "⚠️ OpenCV未安装"
    python3 -c "import fastapi; print(f'✅ FastAPI: {fastapi.__version__}')" 2>/dev/null || echo "⚠️ FastAPI未安装"
}

# 启动API服务器
start_api() {
    echo ""
    echo "启动API服务器..."
    echo "访问地址: http://localhost:8000"
    echo "API文档: http://localhost:8000/docs"
    echo "按 Ctrl+C 停止服务"
    echo ""
    
    python3 -m uvicorn apps.api.server:app --host 0.0.0.0 --port 8000 --reload
}

# 启动GPU服务
start_gpu() {
    echo ""
    echo "启动GPU服务..."
    echo "访问地址: http://localhost:8001"
    echo "按 Ctrl+C 停止服务"
    echo ""
    
    python3 -m uvicorn apps.mocap.service:app --host 0.0.0.0 --port 8001 --reload
}

# 显示帮助
show_help() {
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  api      启动API服务器"
    echo "  gpu      启动GPU服务"
    echo "  check    检查环境"
    echo "  help     显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 api"
    echo "  $0 gpu"
    echo "  $0 check"
}

# 主函数
main() {
    check_python
    
    case "$1" in
        api)
            check_dependencies
            start_api
            ;;
        gpu)
            check_dependencies
            start_gpu
            ;;
        check)
            check_dependencies
            echo ""
            echo "✅ 环境检查完成"
            ;;
        help|--help|-h|"")
            show_help
            ;;
        *)
            echo "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
