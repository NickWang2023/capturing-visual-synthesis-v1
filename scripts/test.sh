#!/bin/bash
# 大模型支持下的动作捕捉与视觉合成系统 V1.0
# 测试运行脚本

set -e

echo "🧪 运行测试"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查pytest
check_pytest() {
    if ! command -v pytest &> /dev/null; then
        echo -e "${YELLOW}⚠️ pytest未安装，正在安装...${NC}"
        pip install pytest pytest-cov pytest-asyncio
    fi
    echo -e "${GREEN}✅ pytest已安装${NC}"
}

# 运行单元测试
run_unit_tests() {
    echo ""
    echo "运行单元测试..."
    pytest tests/ -v -m "unit" --tb=short
}

# 运行集成测试
run_integration_tests() {
    echo ""
    echo "运行集成测试..."
    pytest tests/ -v -m "integration" --tb=short
}

# 运行性能测试
run_performance_tests() {
    echo ""
    echo "运行性能测试..."
    pytest tests/ -v -m "performance" --tb=short
}

# 运行所有测试
run_all_tests() {
    echo ""
    echo "运行所有测试..."
    pytest tests/ -v --tb=short
}

# 运行测试并生成覆盖率报告
run_tests_with_coverage() {
    echo ""
    echo "运行测试并生成覆盖率报告..."
    pytest tests/ -v --cov=easymocap --cov-report=html --cov-report=xml --tb=short
    
    echo ""
    echo -e "${GREEN}✅ 覆盖率报告已生成${NC}"
    echo "  HTML报告: htmlcov/index.html"
    echo "  XML报告: coverage.xml"
}

# 显示帮助
show_help() {
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  unit        运行单元测试"
    echo "  integration 运行集成测试"
    echo "  performance 运行性能测试"
    echo "  all         运行所有测试"
    echo "  coverage    运行测试并生成覆盖率报告"
    echo "  help        显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 unit"
    echo "  $0 coverage"
}

# 主函数
main() {
    check_pytest
    
    case "$1" in
        unit)
            run_unit_tests
            ;;
        integration)
            run_integration_tests
            ;;
        performance)
            run_performance_tests
            ;;
        all)
            run_all_tests
            ;;
        coverage)
            run_tests_with_coverage
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
