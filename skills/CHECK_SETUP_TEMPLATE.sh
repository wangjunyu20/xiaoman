#!/bin/bash
# Skill自检脚本模板
# 用于快速验证Skill是否配置正确

echo "========================================"
echo "🔍 Skill自检工具"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

CHECKS_PASSED=0
CHECKS_FAILED=0

# 检查函数
check() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅${NC} $2"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}❌${NC} $2"
        ((CHECKS_FAILED++))
    fi
}

warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

echo "📋 检查项目"
echo "----------------------------------------"

# 1. 检查SKILL.md是否存在
if [ -f "SKILL.md" ]; then
    check 0 "SKILL.md 存在"
else
    check 1 "SKILL.md 存在"
fi

# 2. 检查scripts目录
if [ -d "scripts" ]; then
    check 0 "scripts/ 目录存在"
    SCRIPT_COUNT=$(find scripts -type f \( -name "*.py" -o -name "*.sh" -o -name "*.js" \) | wc -l)
    if [ $SCRIPT_COUNT -gt 0 ]; then
        check 0 "包含 $SCRIPT_COUNT 个可执行脚本"
    else
        check 1 "包含可执行脚本"
    fi
else
    check 1 "scripts/ 目录存在"
fi

# 3. 检查references目录
if [ -d "references" ]; then
    check 0 "references/ 目录存在"
    REF_COUNT=$(find references -type f -name "*.md" | wc -l)
    check 0 "包含 $REF_COUNT 个参考文档"
else
    warning "references/ 目录不存在（可选但推荐）"
fi

# 4. 检查依赖（根据Skill类型调整）
# Python依赖示例
if command -v python3 &> /dev/null; then
    check 0 "Python3 已安装"
    
    # 检查特定包（示例）
    # python3 -c "import tushare" 2>/dev/null
    # check $? "tushare 包已安装"
else
    check 1 "Python3 已安装"
fi

# 5. 检查环境变量（根据Skill需求调整）
# if [ -n "$REQUIRED_ENV_VAR" ]; then
#     check 0 "环境变量 REQUIRED_ENV_VAR 已设置"
# else
#     check 1 "环境变量 REQUIRED_ENV_VAR 已设置"
# fi

echo ""
echo "----------------------------------------"
echo "📊 检查结果"
echo "----------------------------------------"
echo -e "通过: ${GREEN}$CHECKS_PASSED${NC}"
echo -e "失败: ${RED}$CHECKS_FAILED${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ 所有检查通过！Skill可以正常使用。${NC}"
    exit 0
else
    echo -e "${RED}❌ 有 $CHECKS_FAILED 项检查失败，请修复后再使用。${NC}"
    exit 1
fi
