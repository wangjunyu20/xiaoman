#!/bin/bash
# 快速测试行情分析器

echo "========================================"
echo "🔍 行情分析器快速测试"
echo "========================================"
echo ""

cd /root/.openclaw/workspace_investment/skills/market-sentiment-analyzer

echo "测试1: 光模块分析"
python3 scripts/analyze.py --industry "光模块" --days 3 2>&1 | grep -E "(reasoning|sentiment_label|主力资金|板块)" | head -10

echo ""
echo "测试2: CPO概念分析"  
python3 scripts/analyze.py --industry "CPO" --days 3 2>&1 | grep -E "(reasoning|主力资金|流出|下跌)" | head -5

echo ""
echo "测试3: 检查输出文件"
ls -la output/cache/*.json 2>/dev/null | head -5

echo ""
echo "========================================"
echo "✅ 测试完成"
echo "========================================"
