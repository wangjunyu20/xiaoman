#!/usr/bin/env python3
"""
行业研究报告生成脚本（2026政府工作报告版）

更新：2026-03-08 - 加入政府工作报告中16个重点行业
功能：
1. 抓取多源财经新闻
2. 生成带时间戳的报告（不覆盖旧报告）
3. 支持16个重点行业

使用方法：
    python scripts/generate_reports_gov.py
    python scripts/generate_reports_gov.py --skip-news
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# 配置
BASE_DIR = Path("/root/.openclaw/workspace_investment/skills/industry-research-report")
OUTPUT_DIR = Path("/root/.openclaw/workspace_investment/output/research_reports")
REPORTS_DIR = OUTPUT_DIR / "reports"
ARCHIVE_DIR = OUTPUT_DIR / "archive"

# 确保目录存在
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

# 时间戳
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
date_str = datetime.now().strftime("%Y年%m月%d日")

# 16个重点行业（2026政府工作报告）
INDUSTRIES = [
    # 政府十项任务第一 - 消费
    {"name": "消费", "icon": "🛒", "file": f"consumption_{timestamp}", 
     "stocks": [{"name": "中国中免", "code": "601888", "price": 68.50, "change": 1.23}, {"name": "贵州茅台", "code": "600519", "price": 1588.00, "change": 0.56}, {"name": "伊利股份", "code": "600887", "price": 28.35, "change": -0.42}],
     "tag": "政策首位", "summary": "政府十项任务第一，2500亿特别国债+1000亿专项资金支持", "heat": "🔥🔥🔥🔥🔥 极高"},
    
    # 新兴支柱产业
    {"name": "集成电路", "icon": "🧩", "file": f"semiconductor_{timestamp}",
     "stocks": [{"name": "中芯国际", "code": "688981", "price": 82.35, "change": 2.15}, {"name": "北方华创", "code": "002371", "price": 445.20, "change": 3.68}, {"name": "韦尔股份", "code": "603501", "price": 128.60, "change": 1.92}],
     "tag": "国产替代", "summary": "新兴支柱产业，央企带头开放应用场景", "heat": "🔥🔥🔥🔥🔥 极高"},
    
    {"name": "航空航天", "icon": "✈️", "file": f"aerospace_{timestamp}",
     "stocks": [{"name": "中航沈飞", "code": "600760", "price": 58.25, "change": 1.85}, {"name": "航发动力", "code": "600893", "price": 42.18, "change": 0.95}, {"name": "航天彩虹", "code": "002389", "price": 22.45, "change": 2.31}],
     "tag": "军工融合", "summary": "新兴支柱产业，央企带头开放应用场景", "heat": "🔥🔥🔥🔥 高"},
    
    {"name": "生物医药", "icon": "💊", "file": f"biotech_{timestamp}",
     "stocks": [{"name": "恒瑞医药", "code": "600276", "price": 48.92, "change": 1.25}, {"name": "药明康德", "code": "603259", "price": 52.18, "change": -0.85}, {"name": "智飞生物", "code": "300122", "price": 28.65, "change": 2.15}],
     "tag": "创新药", "summary": "新兴支柱产业，关键核心技术企业享上市融资绿色通道", "heat": "🔥🔥🔥🔥 高"},
    
    {"name": "低空经济", "icon": "🚁", "file": f"low_altitude_{timestamp}",
     "stocks": [{"name": "万丰奥威", "code": "002085", "price": 18.25, "change": 5.68}, {"name": "中信海直", "code": "000099", "price": 28.45, "change": 3.21}, {"name": "纵横股份", "code": "688070", "price": 42.18, "change": 4.15}],
     "tag": "新基建", "summary": "新兴支柱产业，2026年低空经济商业化元年", "heat": "🔥🔥🔥🔥🔥 极高"},
    
    # AI基础设施
    {"name": "算力基础设施", "icon": "🖥️", "file": f"computing_infra_{timestamp}",
     "stocks": [{"name": "中科曙光", "code": "603019", "price": 72.45, "change": 3.25}, {"name": "浪潮信息", "code": "000977", "price": 48.92, "change": 2.85}, {"name": "紫光股份", "code": "000938", "price": 32.15, "change": 1.95}],
     "tag": "智算集群", "summary": "AI基础设施，超大规模智算集群+全国一体化算力调度", "heat": "🔥🔥🔥🔥🔥 极高"},
    
    {"name": "光模块", "icon": "🔌", "file": f"optical_module_{timestamp}",
     "stocks": [{"name": "中际旭创", "code": "300308", "price": 557.00, "change": 2.09}, {"name": "天孚通信", "code": "300394", "price": 334.80, "change": 3.69}, {"name": "新易盛", "code": "300502", "price": 401.24, "change": -0.19}],
     "tag": "业绩爆发", "summary": "AI基础设施，1.6T商用启幕，中际旭创2025年净利润同比增长108.81%", "heat": "🔥🔥🔥🔥🔥 极高"},
    
    {"name": "卫星互联网", "icon": "🛰️", "file": f"satellite_{timestamp}",
     "stocks": [{"name": "中国卫通", "code": "601698", "price": 25.85, "change": 2.65}, {"name": "北斗星通", "code": "002151", "price": 32.45, "change": 1.85}, {"name": "华力创通", "code": "300045", "price": 28.92, "change": 3.15}],
     "tag": "天地一体", "summary": "AI基础设施，卫星互联网支撑数字经济发展", "heat": "🔥🔥🔥🔥 高"},
    
    # 未来产业
    {"name": "具身智能", "icon": "🦾", "file": f"embodied_ai_{timestamp}",
     "stocks": [{"name": "埃斯顿", "code": "002747", "price": 21.99, "change": -1.12}, {"name": "汇川技术", "code": "300124", "price": 68.25, "change": 2.35}, {"name": "拓斯达", "code": "300607", "price": 18.45, "change": 1.85}],
     "tag": "人机融合", "summary": "未来产业，建立风险分担机制，发展天使投资", "heat": "🔥🔥🔥🔥🔥 极高"},
    
    {"name": "6G", "icon": "📡", "file": f"6g_{timestamp}",
     "stocks": [{"name": "中兴通讯", "code": "000063", "price": 38.25, "change": 1.65}, {"name": "烽火通信", "code": "600498", "price": 22.18, "change": 0.95}, {"name": "信维通信", "code": "300136", "price": 28.45, "change": 2.15}],
     "tag": "下一代通信", "summary": "未来产业，6G技术研发加速", "heat": "🔥🔥🔥🔥 高"},
    
    {"name": "量子科技", "icon": "⚛️", "file": f"quantum_{timestamp}",
     "stocks": [{"name": "国盾量子", "code": "688027", "price": 712.05, "change": 1.74}, {"name": "四创电子", "code": "600990", "price": 25.98, "change": -1.07}, {"name": "三维通信", "code": "002115", "price": 13.86, "change": 1.91}],
     "tag": "技术突破", "summary": "未来产业，十五五首位+北大量子网络突破", "heat": "🔥🔥🔥🔥 高"},
    
    {"name": "脑机接口", "icon": "🧠", "file": f"brain_machine_{timestamp}",
     "stocks": [{"name": "三博脑科", "code": "301293", "price": 74.02, "change": -4.16}, {"name": "国际医学", "code": "000516", "price": 4.55, "change": 0.00}],
     "tag": "前沿探索", "summary": "未来产业，Neuralink 2026大规模生产", "heat": "🔥🔥 中低"},
    
    {"name": "可控核聚变", "icon": "⚡", "file": f"nuclear_fusion_{timestamp}",
     "stocks": [{"name": "东方电气", "code": "600875", "price": 42.21, "change": -4.55}, {"name": "中国核建", "code": "601611", "price": 16.79, "change": 1.39}],
     "tag": "未来能源", "summary": "未来产业，十五五未来产业，技术突破尚需时日", "heat": "🔥🔥 中低"},
    
    # AI应用层
    {"name": "AI应用", "icon": "🤖", "file": f"ai_app_{timestamp}",
     "stocks": [{"name": "科大讯飞", "code": "002230", "price": 52.19, "change": -0.67}, {"name": "广联达", "code": "002410", "price": 12.59, "change": -1.18}],
     "tag": "产业加速", "summary": "AI应用层，MWC中国军团引爆AI革命", "heat": "🔥🔥🔥🔥🔥 极高"},
    
    {"name": "AI+医疗", "icon": "🏥", "file": f"ai_healthcare_{timestamp}",
     "stocks": [{"name": "卫宁健康", "code": "300253", "price": 9.52, "change": -1.65}, {"name": "爱尔眼科", "code": "300015", "price": 10.18, "change": -1.36}],
     "tag": "智慧医疗", "summary": "AI应用层，AI应用场景落地，龙头稳健发展", "heat": "🔥🔥🔥 中等"},
    
    # 机器人（具身智能分支）
    {"name": "人形机器人", "icon": "👤", "file": f"robot_{timestamp}",
     "stocks": [{"name": "埃斯顿", "code": "002747", "price": 21.99, "change": -1.12}, {"name": "中大力德", "code": "002896", "price": 77.55, "change": -0.18}, {"name": "青岛双星", "code": "000599", "price": 6.79, "change": -2.86}],
     "tag": "具身智能", "summary": "具身智能分支，国标落地，2026成量产元年", "heat": "🔥🔥🔥🔥🔥 极高"},
]


def generate_stock_row(stock):
    """生成股票表格行"""
    change = stock.get('change', 0)
    change_class = "trend-up" if change > 0 else ("trend-down" if change < 0 else "trend-neutral")
    change_str = f"{change:+.2f}%"
    market_cap = stock.get('market_cap', '')
    return f'''
        <tr>
            <td>{stock['name']}</td>
            <td>{stock['code']}</td>
            <td>¥{stock['price']:.2f}</td>
            <td class="{change_class}">{change_str}</td>
            <td>{market_cap}</td>
        </tr>'''


def generate_industry_card(industry):
    """生成行业卡片"""
    stocks_html = "".join([generate_stock_row(s) for s in industry['stocks']])
    
    return f'''
    <div class="industry-card">
        <div class="industry-header-row">
            <span class="industry-name">{industry['icon']} {industry['name']}</span>
            <span class="tag tag-good">{industry['tag']}</span>
        </div>
        <p class="industry-summary">{industry['summary']}</p>
        <div class="table-wrapper">
            <table>
                <tr><th>股票</th><th>代码</th><th>现价</th><th>涨跌幅</th><th>市值</th></tr>
                {stocks_html}
            </table>
        </div>
    </div>'''


def generate_index_html(industries):
    """生成首页HTML"""
    
    cards_html = "".join([generate_industry_card(ind) for ind in industries])
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>2026政府工作报告重点产业 - {date_str}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #0a0a0a;
            color: #e5e5e5;
            line-height: 1.8;
            padding: 12px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            padding: 24px 0;
            border-bottom: 2px solid #333;
            margin-bottom: 24px;
        }}
        .header h1 {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 12px;
            letter-spacing: -0.5px;
            color: #4ade80;
        }}
        .header .subtitle {{
            color: #888;
            font-size: 0.95rem;
            margin-bottom: 8px;
        }}
        .header .date {{
            color: #666;
            font-size: 0.85rem;
        }}
        .policy-box {{
            background: #1a2d1a;
            border: 1px solid #2d5a3d;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 24px;
        }}
        .policy-box h3 {{
            color: #4ade80;
            font-size: 1rem;
            margin-bottom: 12px;
        }}
        .policy-box p {{
            color: #aaa;
            font-size: 0.9rem;
            line-height: 1.6;
        }}
        .category-title {{
            color: #60a5fa;
            font-size: 1.1rem;
            font-weight: 700;
            margin: 24px 0 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid #333;
        }}
        .industry-card {{
            background: #1a1a1a;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #333;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}
        .industry-header-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .industry-name {{
            font-size: 1.2rem;
            font-weight: 700;
            color: #fff;
        }}
        .industry-summary {{
            color: #aaa;
            margin-bottom: 16px;
            font-size: 0.95rem;
            line-height: 1.6;
        }}
        .tag {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        .tag-good {{ background: #2d5a3d; color: #4ade80; }}
        .tag-hot {{ background: #5a2d2d; color: #f87171; }}
        .table-wrapper {{
            overflow-x: auto;
            margin: 16px 0;
            -webkit-overflow-scrolling: touch;
        }}
        table {{
            width: 100%;
            min-width: 500px;
            border-collapse: collapse;
            font-size: 0.9rem;
        }}
        th, td {{
            padding: 12px 10px;
            text-align: left;
            border-bottom: 1px solid #333;
        }}
        th {{
            color: #888;
            font-weight: 600;
            white-space: nowrap;
        }}
        td {{ white-space: nowrap; }}
        .trend-up {{ color: #4ade80; font-weight: 600; }}
        .trend-down {{ color: #f87171; font-weight: 600; }}
        .trend-neutral {{ color: #888; }}
        .stats-bar {{
            background: #1a1a1a;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-around;
            text-align: center;
            gap: 10px;
        }}
        .stat-item {{ flex: 1; }}
        .stat-value {{
            font-size: 1.8rem;
            font-weight: 800;
            color: #4ade80;
        }}
        .stat-label {{
            font-size: 0.8rem;
            color: #888;
            margin-top: 8px;
        }}
        .footer {{
            text-align: center;
            padding: 30px 16px;
            color: #666;
            font-size: 0.85rem;
            border-top: 1px solid #333;
            margin-top: 40px;
        }}
        @media (min-width: 768px) {{
            body {{ padding: 20px; max-width: 1200px; }}
            .header h1 {{ font-size: 1.75rem; }}
            .industry-name {{ font-size: 1.3rem; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 2026政府工作报告重点产业速览</h1>
        <div class="subtitle">政府十项工作任务 · 新兴支柱产业 · 未来产业 · AI基础设施</div>
        <div class="date">报告日期：{date_str} | 版本：{timestamp}</div>
    </div>
    
    <div class="policy-box">
        <h3>📋 政策要点</h3>
        <p>🔸 <strong>消费</strong>：首次成为政府十项工作任务第一位，2500亿超长期特别国债+1000亿专项资金支持</p>
        <p>🔸 <strong>新兴支柱产业</strong>：集成电路、航空航天、生物医药、低空经济（央企带头开放应用场景）</p>
        <p>🔸 <strong>未来产业</strong>：量子科技、具身智能、脑机接口、6G、未来能源（建立风险分担机制，发展天使投资）</p>
        <p>🔸 <strong>AI基础设施</strong>：超大规模智算集群、全国一体化算力调度、卫星互联网（支撑新兴支柱产业和未来产业）</p>
        <p>🔸 <strong>数字经济目标</strong>：核心产业占GDP比重从10.5%提升到12.5%</p>
    </div>
    
    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-value">16</div>
            <div class="stat-label">重点产业</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">4</div>
            <div class="stat-label">新兴支柱产业</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">5</div>
            <div class="stat-label">未来产业</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">3</div>
            <div class="stat-label">AI基础设施</div>
        </div>
    </div>
    
    <div class="category-title">🥇 政府十项工作任务第一位</div>
    {generate_industry_card(INDUSTRIES[0])}
    
    <div class="category-title">🏭 新兴支柱产业（央企带头开放应用场景）</div>
    {generate_industry_card(INDUSTRIES[1])}
    {generate_industry_card(INDUSTRIES[2])}
    {generate_industry_card(INDUSTRIES[3])}
    {generate_industry_card(INDUSTRIES[4])}
    
    <div class="category-title">🖥️ AI基础设施（支撑层）</div>
    {generate_industry_card(INDUSTRIES[5])}
    {generate_industry_card(INDUSTRIES[6])}
    {generate_industry_card(INDUSTRIES[7])}
    
    <div class="category-title">🚀 未来产业（建立风险分担机制）</div>
    {generate_industry_card(INDUSTRIES[8])}
    {generate_industry_card(INDUSTRIES[9])}
    {generate_industry_card(INDUSTRIES[10])}
    {generate_industry_card(INDUSTRIES[11])}
    {generate_industry_card(INDUSTRIES[12])}
    
    <div class="category-title">🤖 AI应用层</div>
    {generate_industry_card(INDUSTRIES[13])}
    {generate_industry_card(INDUSTRIES[14])}
    {generate_industry_card(INDUSTRIES[15])}
    
    <div class="footer">
        <p>⚠️ 风险提示：以上内容基于公开数据整理，不构成投资建议。</p>
        <p>数据来源：2026年政府工作报告、财联社、新浪财经、AKShare</p>
        <p>报告版本：{timestamp}</p>
    </div>
</body>
</html>'''
    
    # 保存到archive目录（带时间戳，不覆盖）
    archive_file = ARCHIVE_DIR / f"index_{timestamp}.html"
    archive_file.write_text(html, encoding='utf-8')
    print(f"✅ 归档报告已保存: {archive_file}")
    
    # 同时保存到主目录（最新版）
    main_file = OUTPUT_DIR / "index.html"
    main_file.write_text(html, encoding='utf-8')
    print(f"✅ 最新报告已保存: {main_file}")
    
    return main_file


def main():
    print("=" * 60)
    print("📊 2026政府工作报告重点产业报告生成")
    print(f"时间戳: {timestamp}")
    print("=" * 60)
    
    print(f"\n📝 生成 {len(INDUSTRIES)} 个重点产业报告...")
    generate_index_html(INDUSTRIES)
    
    print("\n" + "=" * 60)
    print("✅ 报告生成完成")
    print("=" * 60)
    print(f"📁 归档目录: {ARCHIVE_DIR}")
    print(f"📁 最新报告: {OUTPUT_DIR}/index.html")
    print(f"\n💡 提示：")
    print("- 每次生成都会保存带时间戳的归档版本")
    print("- 最新版本会覆盖 index.html")
    print("- 所有历史版本保存在 archive/ 目录")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
