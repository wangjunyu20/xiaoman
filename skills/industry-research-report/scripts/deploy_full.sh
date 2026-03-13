#!/bin/bash
# 完整的报告生成+检验+部署流程

set -e

echo "========================================"
echo "📊 投资报告生成部署流程"
echo "========================================"

# 1. 生成报告
echo ""
echo "🔄 步骤1: 生成报告..."
cd /root/.openclaw/workspace_investment/skills/industry-research-report
python3 scripts/generate_reports.py

# 2. 生成所有详情页
echo ""
echo "🔄 步骤2: 生成详情页..."
python3 /tmp/generate_all_details.py

# 3. 生成PDF
if command -v playwright &> /dev/null || python3 -c "import playwright" 2>/dev/null; then
    echo ""
    echo "🔄 步骤3: 生成PDF报告..."
    python3 scripts/generate_pdf.py || {
        echo "⚠️ PDF生成失败，但继续部署网页版"
    }
else
    echo ""
    echo "⚠️ 步骤3: 跳过PDF生成（Playwright未安装）"
fi

# 4. 完整性检验
echo ""
echo "🔍 步骤4: 完整性检验..."
python3 scripts/verify_reports.py || {
    echo "❌ 检验失败，停止部署"
    exit 1
}

# 5. 推送到GitHub
echo ""
echo "🚀 步骤5: 推送到GitHub..."
cd /root/.openclaw/workspace_investment/output/research_reports
git add .
git commit -m "报告更新 - $(date '+%Y%m%d_%H%M') - 包含完整检验"
git push origin main

echo ""
echo "========================================"
echo "✅ 部署完成！"
echo "========================================"
echo "📄 网页版: https://wangjunyu20.github.io/xiaoman/"
echo "📑 PDF版:  https://wangjunyu20.github.io/xiaoman/行业研究报告_$(date '+%Y%m%d').pdf"
