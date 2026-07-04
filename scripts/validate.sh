#!/bin/bash
# 大模型支持下的动作捕捉与视觉合成系统 V1.0
# 配置验证脚本

set -e

echo "🔍 验证项目配置"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

# 检查文件是否存在
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1 缺失${NC}"
        ((ERRORS++))
    fi
}

# 检查目录是否存在
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅ $1/${NC}"
    else
        echo -e "${RED}❌ $1/ 缺失${NC}"
        ((ERRORS++))
    fi
}

# 检查Python语法
check_python_syntax() {
    if python3 -m py_compile "$1" 2>/dev/null; then
        echo -e "${GREEN}✅ $1 语法正确${NC}"
    else
        echo -e "${RED}❌ $1 语法错误${NC}"
        ((ERRORS++))
    fi
}

# 检查Docker语法
check_docker_syntax() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ $1 存在${NC}"
    else
        echo -e "${RED}❌ $1 缺失${NC}"
        ((ERRORS++))
    fi
}

echo "📁 检查核心文件..."
check_file "setup.py"
check_file "requirements.txt"
check_file "README_大模型支持下的动作捕捉与视觉合成数据系统.md"
check_file "LICENSE"

echo ""
echo "📁 检查配置文件..."
check_file ".env.example"
check_file ".gitignore"
check_file "pytest.ini"
check_file ".coveragerc"
check_file "mypy.ini"
check_file "pyproject.toml"

echo ""
echo "📁 检查Docker配置..."
check_file "Dockerfile"
check_file "Dockerfile.gpu"
check_file "docker-compose.yml"
check_file "docker-compose.override.yml"
check_file "docker-compose.prod.yml"

echo ""
echo "📁 检查脚本..."
check_file "scripts/deploy.sh"
check_file "scripts/start.sh"
check_file "scripts/test.sh"
check_file "scripts/validate.sh"

echo ""
echo "📁 检查文档..."
check_file "CHANGELOG.md"
check_file "CONTRIBUTING.md"
check_file "QUICKSTART.md"
check_file "upgrade/UPGRADE_README.md"

echo ""
echo "📁 检查核心模块..."
check_dir "easymocap/llm"
check_dir "easymocap/vlm"
check_dir "easymocap/performance"
check_dir "easymocap/security"
check_dir "easymocap/plugins"
check_dir "apps/api"
check_dir "tests"

echo ""
echo "📁 检查测试文件..."
check_file "tests/conftest.py"
check_file "tests/test_pipeline.py"
check_file "tests/test_llm_service.py"
check_file "tests/test_vlm_service.py"
check_file "tests/test_performance.py"

echo ""
echo "🔍 检查Python语法..."
check_python_syntax "easymocap/llm/service.py"
check_python_syntax "easymocap/vlm/service.py"
check_python_syntax "easymocap/performance/optimizer.py"
check_python_syntax "easymocap/security/secrets.py"
check_python_syntax "easymocap/plugins/manager.py"
check_python_syntax "apps/api/server.py"

echo ""
echo "================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ 所有检查通过！${NC}"
    exit 0
else
    echo -e "${RED}❌ 发现 $ERRORS 个错误${NC}"
    exit 1
fi
