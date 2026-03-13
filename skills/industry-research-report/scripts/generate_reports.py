#!/usr/bin/env python3
"""
行业研究报告生成脚本（含多源新闻数据）

功能：
1. 抓取多源财经新闻（财联社、新浪财经、东财股吧、新华网、中国基金报）
2. 生成多行业速览首页（HTML）
3. 生成7个行业详情页（HTML）
4. 合并生成完整PDF报告

使用方法：
    python scripts/generate_reports.py
    python scripts/generate_reports.py --skip-news  # 跳过新闻抓取（使用缓存）

输出：
    /workspace_investment/output/research_reports/
    ├── index.html                          # 首页
    ├── full_report.html                    # 完整报告（合并版）
    ├── 行业研究报告_最终版_YYYYMMDD.pdf     # PDF报告
    └── reports/                            # 行业详情页目录
"""

import os
import sys
import subprocess
import json
import argparse
from datetime import datetime
from pathlib import Path

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# 配置
BASE_DIR = Path("/root/.openclaw/workspace_investment/skills/industry-research-report")
OUTPUT_DIR = Path("/root/.openclaw/workspace_investment/output/research_reports")
REPORTS_DIR = OUTPUT_DIR / "reports"
ARCHIVE_DIR = OUTPUT_DIR / "archive"  # 新增归档目录
ASSETS_DIR = BASE_DIR / "assets"
REFERENCES_DIR = BASE_DIR / "references"

# 时间戳
def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M")

def ensure_directories():
    """确保输出目录存在"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)  # 创建归档目录
    print(f"✅ 输出目录已准备: {OUTPUT_DIR}")
    print(f"✅ 归档目录已准备: {ARCHIVE_DIR}")

def load_industry_list():
    """加载行业清单（2026政府工作报告版 - 16个行业）"""
    industries = [
        # 政府十项任务第一 - 消费
        {
            "name": "消费",
            "icon": "🛒",
            "file": "consumption",
            "stocks": [
                {"name": "中国中免", "code": "601888", "price": 68.50, "change": 1.23, "market_cap": "1400亿"},
                {"name": "贵州茅台", "code": "600519", "price": 1588.00, "change": 0.56, "market_cap": "2万亿"},
                {"name": "伊利股份", "code": "600887", "price": 28.35, "change": -0.42, "market_cap": "1800亿"},
            ],
            "tag": "政策首位",
            "summary": "政府十项任务第一位，2500亿特别国债+1000亿专项资金支持",
            "heat": "🔥🔥🔥🔥🔥 极高",
            "category": "政府十项任务首位"
        },
        # 新兴支柱产业
        {
            "name": "集成电路",
            "icon": "🧩",
            "file": "semiconductor",
            "stocks": [
                {"name": "中芯国际", "code": "688981", "price": 82.35, "change": 2.15, "market_cap": "6500亿"},
                {"name": "北方华创", "code": "002371", "price": 445.20, "change": 3.68, "market_cap": "2300亿"},
                {"name": "韦尔股份", "code": "603501", "price": 128.60, "change": 1.92, "market_cap": "1500亿"},
            ],
            "tag": "国产替代",
            "summary": "新兴支柱产业，央企带头开放应用场景",
            "heat": "🔥🔥🔥🔥🔥 极高",
            "category": "新兴支柱产业"
        },
        {
            "name": "航空航天",
            "icon": "✈️",
            "file": "aerospace",
            "stocks": [
                {"name": "中航沈飞", "code": "600760", "price": 58.25, "change": 1.85, "market_cap": "800亿"},
                {"name": "航发动力", "code": "600893", "price": 42.18, "change": 0.95, "market_cap": "1100亿"},
                {"name": "航天彩虹", "code": "002389", "price": 22.45, "change": 2.31, "market_cap": "220亿"},
            ],
            "tag": "军工融合",
            "summary": "新兴支柱产业，央企带头开放应用场景",
            "heat": "🔥🔥🔥🔥 高",
            "category": "新兴支柱产业"
        },
        {
            "name": "生物医药",
            "icon": "💊",
            "file": "biotech",
            "stocks": [
                {"name": "恒瑞医药", "code": "600276", "price": 48.92, "change": 1.25, "market_cap": "3100亿"},
                {"name": "药明康德", "code": "603259", "price": 52.18, "change": -0.85, "market_cap": "1500亿"},
                {"name": "智飞生物", "code": "300122", "price": 28.65, "change": 2.15, "market_cap": "680亿"},
            ],
            "tag": "创新药",
            "summary": "新兴支柱产业，关键核心技术企业享上市融资绿色通道",
            "heat": "🔥🔥🔥🔥 高",
            "category": "新兴支柱产业"
        },
        {
            "name": "低空经济",
            "icon": "🚁",
            "file": "low_altitude",
            "stocks": [
                {"name": "万丰奥威", "code": "002085", "price": 18.25, "change": 5.68, "market_cap": "380亿"},
                {"name": "中信海直", "code": "000099", "price": 28.45, "change": 3.21, "market_cap": "220亿"},
                {"name": "纵横股份", "code": "688070", "price": 42.18, "change": 4.15, "market_cap": "36亿"},
            ],
            "tag": "新基建",
            "summary": "新兴支柱产业，2026年低空经济商业化元年",
            "heat": "🔥🔥🔥🔥🔥 极高",
            "category": "新兴支柱产业"
        },
        # AI基础设施
        {
            "name": "算力基础设施",
            "icon": "🖥️",
            "file": "computing_infra",
            "stocks": [
                {"name": "中科曙光", "code": "603019", "price": 72.45, "change": 3.25, "market_cap": "1050亿"},
                {"name": "浪潮信息", "code": "000977", "price": 48.92, "change": 2.85, "market_cap": "720亿"},
                {"name": "紫光股份", "code": "000938", "price": 32.15, "change": 1.95, "market_cap": "920亿"},
            ],
            "tag": "智算集群",
            "summary": "AI基础设施，超大规模智算集群+全国一体化算力调度",
            "heat": "🔥🔥🔥🔥🔥 极高",
            "category": "AI基础设施"
        },
        {
            "name": "光模块",
            "icon": "🔌",
            "file": "optical_module",
            "stocks": [
                {"name": "中际旭创", "code": "300308", "price": 557.00, "change": 2.09, "market_cap": "6000亿"},
                {"name": "天孚通信", "code": "300394", "price": 334.80, "change": 3.69, "market_cap": "1800亿"},
                {"name": "新易盛", "code": "300502", "price": 401.24, "change": -0.19, "market_cap": "2800亿"},
            ],
            "tag": "业绩爆发",
            "summary": "AI基础设施，1.6T商用启幕，中际旭创2025年净利润同比增长108.81%",
            "heat": "🔥🔥🔥🔥🔥 极高",
            "category": "AI基础设施"
        },
        {
            "name": "卫星互联网",
            "icon": "🛰️",
            "file": "satellite",
            "stocks": [
                {"name": "中国卫通", "code": "601698", "price": 25.85, "change": 2.65, "market_cap": "1100亿"},
                {"name": "北斗星通", "code": "002151", "price": 32.45, "change": 1.85, "market_cap": "175亿"},
                {"name": "华力创通", "code": "300045", "price": 28.92, "change": 3.15, "market_cap": "190亿"},
            ],
            "tag": "天地一体",
            "summary": "AI基础设施，卫星互联网支撑数字经济发展",
            "heat": "🔥🔥🔥🔥 高",
            "category": "AI基础设施"
        },
        # 未来产业
        {
            "name": "具身智能/人形机器人",
            "icon": "🦾",
            "file": "embodied_ai",
            "stocks": [
                {"name": "埃斯顿", "code": "002747", "price": 21.99, "change": -1.12, "market_cap": "190亿"},
                {"name": "汇川技术", "code": "300124", "price": 68.25, "change": 2.35, "market_cap": "1800亿"},
                {"name": "拓斯达", "code": "300607", "price": 18.45, "change": 1.85, "market_cap": "78亿"},
                {"name": "中大力德", "code": "002896", "price": 77.55, "change": -0.18, "market_cap": "120亿"},
                {"name": "青岛双星", "code": "000599", "price": 6.79, "change": -2.86, "market_cap": "55亿"},
            ],
            "tag": "人机融合",
            "summary": "未来产业，国标落地，2026成量产元年，建立风险分担机制",
            "heat": "🔥🔥🔥🔥🔥 极高",
            "category": "未来产业"
        },
        {
            "name": "6G",
            "icon": "📡",
            "file": "6g",
            "stocks": [
                {"name": "中兴通讯", "code": "000063", "price": 38.25, "change": 1.65, "market_cap": "1800亿"},
                {"name": "烽火通信", "code": "600498", "price": 22.18, "change": 0.95, "market_cap": "260亿"},
                {"name": "信维通信", "code": "300136", "price": 28.45, "change": 2.15, "market_cap": "275亿"},
            ],
            "tag": "下一代通信",
            "summary": "未来产业，6G技术研发加速",
            "heat": "🔥🔥🔥🔥 高",
            "category": "未来产业"
        },
        {
            "name": "量子科技",
            "icon": "⚛️",
            "file": "quantum",
            "stocks": [
                {"name": "国盾量子", "code": "688027", "price": 712.05, "change": 1.74, "market_cap": "570亿"},
                {"name": "四创电子", "code": "600990", "price": 25.98, "change": -1.07, "market_cap": "72亿"},
                {"name": "三维通信", "code": "002115", "price": 13.86, "change": 1.91, "market_cap": "110亿"},
            ],
            "tag": "技术突破",
            "summary": "未来产业，十五五首位+北大量子网络突破",
            "heat": "🔥🔥🔥🔥 高",
            "category": "未来产业"
        },
        {
            "name": "脑机接口",
            "icon": "🧬",
            "file": "brain_machine",
            "stocks": [
                {"name": "三博脑科", "code": "301293", "price": 74.02, "change": -4.16, "market_cap": "120亿"},
                {"name": "国际医学", "code": "000516", "price": 4.55, "change": 0.00, "market_cap": "103亿"},
            ],
            "tag": "前沿探索",
            "summary": "未来产业，Neuralink 2026大规模生产",
            "heat": "🔥🔥 中低",
            "category": "未来产业"
        },
        {
            "name": "可控核聚变",
            "icon": "⚡",
            "file": "nuclear_fusion",
            "stocks": [
                {"name": "东方电气", "code": "600875", "price": 42.21, "change": -4.55, "market_cap": "1300亿"},
                {"name": "中国核建", "code": "601611", "price": 16.79, "change": 1.39, "market_cap": "500亿"},
            ],
            "tag": "未来能源",
            "summary": "未来产业，十五五未来产业，技术突破尚需时日",
            "heat": "🔥🔥 中低",
            "category": "未来产业"
        },
        # AI应用层
        {
            "name": "AI应用",
            "icon": "🤖",
            "file": "ai_app",
            "stocks": [
                {"name": "科大讯飞", "code": "002230", "price": 52.19, "change": -0.67, "market_cap": "1200亿"},
                {"name": "广联达", "code": "002410", "price": 12.59, "change": -1.18, "market_cap": "210亿"},
            ],
            "tag": "产业加速",
            "summary": "AI应用层，MWC中国军团引爆AI革命",
            "heat": "🔥🔥🔥🔥🔥 极高",
            "category": "AI应用层"
        },
        {
            "name": "AI+医疗",
            "icon": "🏥",
            "file": "ai_healthcare",
            "stocks": [
                {"name": "卫宁健康", "code": "300253", "price": 9.52, "change": -1.65, "market_cap": "205亿"},
                {"name": "爱尔眼科", "code": "300015", "price": 10.18, "change": -1.36, "market_cap": "900亿"},
            ],
            "tag": "智慧医疗",
            "summary": "AI应用层，AI应用场景落地，龙头稳健发展",
            "heat": "🔥🔥🔥 中等",
            "category": "AI应用层"
        },
    ]
    return industries

def fetch_all_news(industries, skip_fetch=False):
    """
    获取所有行业的新闻数据

    Args:
        industries: 行业列表
        skip_fetch: 是否跳过抓取（使用缓存）

    Returns:
        Dict: {industry_name: {source: [news_list]}}
    """
    import json
    from pathlib import Path
    
    CACHE_DIR = Path("/root/.openclaw/workspace_investment/output/news_cache")
    
    if skip_fetch:
        print("⏩ 跳过新闻抓取，从缓存加载数据...")
        all_news = {}
        
        # 从缓存文件加载新闻数据
        for cache_file in CACHE_DIR.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    news_list = data.get('news', [])
                    if not news_list:
                        continue
                    
                    # 从文件名提取行业名和来源
                    # 文件名格式: source_行业名.json 或 source_search_行业名.json
                    file_stem = cache_file.stem
                    
                    # 移除常见的source前缀
                    source = None
                    industry = None
                    
                    if '_search_' in file_stem:
                        parts = file_stem.split('_search_')
                        source = parts[0]
                        industry = parts[1]
                    elif '_em_' in file_stem:
                        parts = file_stem.split('_em_')
                        source = parts[0]
                        industry = parts[1]
                    elif '_telegraph_' in file_stem:
                        # 财联社电报: cailianshe_telegraph_行业名.json
                        parts = file_stem.split('_telegraph_')
                        source = parts[0]
                        industry = parts[1]
                    elif '_' in file_stem:
                        parts = file_stem.split('_', 1)
                        source = parts[0]
                        industry = parts[1]
                    else:
                        continue
                    
                    # 只加载当前行业列表中的行业
                    industry_names = [ind['name'] for ind in industries]
                    
                    # 行业名称映射（处理变体）
                    industry_mapping = {
                        '具身智能': '具身智能/人形机器人',
                        '人形机器人': '具身智能/人形机器人',
                        '核聚变': '可控核聚变',
                        'AI医疗': 'AI+医疗',
                    }
                    
                    # 尝试直接匹配或映射匹配
                    matched_industry = None
                    if industry in industry_names:
                        matched_industry = industry
                    elif industry in industry_mapping:
                        mapped = industry_mapping[industry]
                        if mapped in industry_names:
                            matched_industry = mapped
                    
                    if matched_industry:
                        # 过滤无效URL的新闻（百度新闻URL是相对路径，会404）
                        valid_news = []
                        for news in news_list:
                            url = news.get('url', '')
                            # 只保留有效的完整URL（以http开头）
                            if url and (url.startswith('http://') or url.startswith('https://')):
                                valid_news.append(news)
                        
                        if valid_news:
                            if matched_industry not in all_news:
                                all_news[matched_industry] = {}
                            if source not in all_news[matched_industry]:
                                all_news[matched_industry][source] = []
                            all_news[matched_industry][source].extend(valid_news)
                        
            except Exception as e:
                continue
        
        # 统计新闻数量
        total_news = sum(
            sum(len(news) for news in sources.values())
            for sources in all_news.values()
        )
        print(f"✅ 从缓存加载完成，共 {total_news} 条新闻")
        return all_news

    try:
        from news_fetcher import NewsFetcher

        print("=" * 60)
        print("📰 开始抓取多源财经新闻...")
        print("=" * 60)

        fetcher = NewsFetcher()
        industry_names = [ind['name'] for ind in industries]

        all_news = fetcher.fetch_all_industries(industry_names)

        # 统计新闻数量
        total_news = sum(
            sum(len(news) for news in sources.values())
            for sources in all_news.values()
        )

        print(f"\n✅ 新闻抓取完成，共 {total_news} 条新闻")
        return all_news

    except Exception as e:
        print(f"⚠️ 新闻抓取失败: {e}")
        return {}

def generate_news_section(news_by_source, is_detail_page=False):
    """
    生成新闻栏目HTML
    
    命名规范（v2026-03-12）：统一使用"行业资讯"，区分展示层级
    - 首页：📰 行业资讯（Top 5）
    - 详情页：📰 行业资讯（完整列表）

    Args:
        news_by_source: {source: [news_list]}
        is_detail_page: 是否是详情页（展示数量不同）

    Returns:
        HTML字符串
    """
    if not news_by_source:
        return ""

    # 合并所有新闻并按影响排序
    all_news = []
    for source, items in news_by_source.items():
        for item in items:
            item['source_display'] = source
            all_news.append(item)

    # 按影响排序（利好 > 中性 > 利空）
    impact_order = {'利好': 0, '中性': 1, '利空': 2}
    all_news.sort(key=lambda x: impact_order.get(x.get('impact', '中性'), 1))

    # 统一命名规范：根据页面类型确定标题和展示数量
    if is_detail_page:
        header = "📰 行业资讯（完整列表）"
        max_items = 10  # 详情页展示10条
    else:
        header = "📰 行业资讯（Top 5）"
        max_items = 5   # 首页展示5条
    
    # 取前N条
    top_news = all_news[:max_items]

    if not top_news:
        return ""

    news_items_html = ""
    for news in top_news:
        impact = news.get('impact', '中性')
        impact_class = {
            '利好': 'impact-positive',
            '利空': 'impact-negative',
            '中性': 'impact-neutral'
        }.get(impact, 'impact-neutral')

        title = news.get('title', '')[:35] + '...' if len(news.get('title', '')) > 35 else news.get('title', '')
        source = news.get('source_display', '未知来源')
        url = news.get('url', '')

        news_items_html += f"""
            <div class="news-item">
                <span class="news-source">{source}</span>
                <a href="{url}" target="_blank" class="news-title-link" title="{news.get('title', '')}">{title}</a>
                <span class="news-impact {impact_class}">{impact}</span>
            </div>
        """

    return f"""
        <div class="news-section">
            <div class="news-header">{header}</div>
            {news_items_html}
        </div>
    """

def generate_stock_row(stock):
    """生成股票表格行"""
    change = stock.get('change', 0)
    change_class = "trend-up" if change > 0 else ("trend-down" if change < 0 else "trend-neutral")
    change_str = f"{change:+.2f}%"
    market_cap = stock.get('market_cap', '')
    market_cap_str = f"{market_cap}" if market_cap else ""

    return f"""
        <tr>
            <td>{stock['name']}</td>
            <td>{stock['code']}</td>
            <td>¥{stock['price']:.2f}</td>
            <td class="{change_class}">{change_str}</td>
            <td>{market_cap_str}</td>
        </tr>"""

def generate_industry_card(industry, news_by_source=None):
    """
    生成行业卡片HTML

    Args:
        industry: 行业数据
        news_by_source: 新闻数据 {source: [news_list]}
    """
    stocks_html = "".join([generate_stock_row(s) for s in industry['stocks']])

    # 生成新闻栏目（首页使用Top 5）
    news_html = generate_news_section(news_by_source, is_detail_page=False) if news_by_source else ""

    return f"""
    <div class="industry-card">
        <div class="industry-header-row">
            <a href="reports/{industry['file']}.html" class="industry-name-link">
                <span class="industry-name">{industry['icon']} {industry['name']}</span>
            </a>
            <span class="tag tag-good">{industry['tag']}</span>
        </div>
        <p class="industry-summary">{industry['summary']}</p>
        {news_html}
        <div class="table-wrapper">
            <table>
                <tr><th>股票</th><th>代码</th><th>现价</th><th>涨跌幅</th><th>市值</th></tr>
                {stocks_html}
            </table>
        </div>
        <div class="detail-link-row">
            <a href="reports/{industry['file']}.html" class="detail-link">查看详情 →</a>
        </div>
    </div>"""

def generate_index_html(industries, all_news=None):
    """
    生成首页HTML（按两会政府工作报告分类展示）

    Args:
        industries: 行业列表
        all_news: 新闻数据 {industry: {source: [news_list]}}
    """
    today = datetime.now().strftime("%Y年%m月%d日")

    # 定义分类和描述（按指定顺序）
    CATEGORIES = [
        ("政府十项任务首位", "提振消费，2500亿特别国债+1000亿专项资金支持"),
        ("新兴支柱产业", "央企带头开放应用场景，关键核心技术企业享上市融资绿色通道"),
        ("AI基础设施", "超大规模智算集群+全国一体化算力调度"),
        ("未来产业", "建立风险分担机制，发展天使投资"),
        ("AI应用层", "AI应用场景加速落地")
    ]

    # 按分类生成行业卡片
    cards_html = ""
    for category, desc in CATEGORIES:
        # 生成分类标题HTML（标题和描述在一个div中）
        cards_html += f'''
        <div class="category-header">
            <h2>{category}</h2>
            <p>{desc}</p>
        </div>
'''
        # 找到该分类的所有行业
        category_industries = [ind for ind in industries if ind.get('category') == category]
        # 生成这些行业的卡片
        for ind in category_industries:
            cards_html += generate_industry_card(ind, all_news.get(ind['name'], {}))

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>热点行业投资速览 - {today}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        /* 基础样式 - 移动端优先 */
        html {{ font-size: 16px; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #0a0a0a;
            color: #e5e5e5;
            line-height: 1.8;
            padding: 12px;
            margin: 0 auto;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}

        .header {{
            text-align: center;
            padding: 24px 0;
            border-bottom: 2px solid #333;
            margin-bottom: 24px;
        }}
        .header h1 {{
            font-size: 1.75rem;
            font-weight: 700;
            margin-bottom: 12px;
            letter-spacing: -0.5px;
        }}
        .header .date {{
            color: #888;
            font-size: 0.95rem;
            margin-bottom: 8px;
        }}
        .header .sources {{
            color: #666;
            font-size: 0.8rem;
            margin-top: 8px;
            line-height: 1.5;
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
            font-size: 1.3rem;
            font-weight: 700;
            color: #fff;
        }}
        .industry-name-link {{
            text-decoration: none;
            color: inherit;
        }}
        .industry-name-link:hover .industry-name {{
            color: #4ade80;
        }}
        .detail-link-row {{
            text-align: right;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #333;
        }}
        .detail-link {{
            color: #60a5fa;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
        }}
        .detail-link:hover {{
            color: #4ade80;
            text-decoration: underline;
        }}
        .industry-summary {{
            color: #aaa;
            margin-bottom: 16px;
            font-size: 1rem;
            line-height: 1.6;
        }}

        .tag {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-right: 5px;
        }}
        .tag-good {{ background: #2d5a3d; color: #4ade80; }}

        /* 分类标题样式 */
        .category-header {{
            background: linear-gradient(90deg, #2d5a3d 0%, #1a3a2a 100%);
            padding: 16px 20px;
            border-radius: 12px;
            margin: 30px 0 20px 0;
            border-left: 4px solid #4ade80;
        }}
        .category-header h2 {{
            color: #4ade80;
            font-size: 1.2rem;
            margin: 0 0 8px 0;
        }}
        .category-header p {{
            color: #aaa;
            font-size: 0.9rem;
            margin: 0;
        }}

        /* 新闻栏目样式 - 移动端优化 */
        .news-section {{
            background: #252525;
            border-radius: 12px;
            padding: 16px;
            margin: 16px 0;
            border-left: 4px solid #4ade80;
        }}
        .news-header {{
            font-size: 1rem;
            font-weight: 700;
            color: #4ade80;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .news-item {{
            display: flex;
            align-items: flex-start;
            padding: 12px 0;
            font-size: 0.95rem;
            border-bottom: 1px solid #333;
            gap: 10px;
            line-height: 1.5;
        }}
        .news-item:last-child {{ border-bottom: none; }}
        .news-source {{
            color: #888;
            min-width: 70px;
            font-size: 0.8rem;
            flex-shrink: 0;
            margin-top: 2px;
        }}
        .news-title {{
            flex: 1;
            color: #ddd;
            line-height: 1.5;
            word-break: break-all;
        }}
        .news-title-link {{
            flex: 1;
            color: #60a5fa;
            line-height: 1.5;
            word-break: break-all;
            text-decoration: underline;
            cursor: pointer;
        }}
        .news-title-link:hover {{
            color: #4ade80;
            text-decoration: underline;
        }}
        .news-impact {{
            font-size: 0.75rem;
            padding: 4px 10px;
            border-radius: 12px;
            flex-shrink: 0;
            font-weight: 600;
        }}
        .impact-positive {{ background: #1a472a; color: #4ade80; }}
        .impact-negative {{ background: #5a1f1f; color: #f87171; }}
        .impact-neutral {{ background: #3a3a3a; color: #bbb; }}

        /* 表格样式 - 移动端横向滚动 */
        .table-wrapper {{
            overflow-x: auto;
            margin: 16px 0;
            -webkit-overflow-scrolling: touch;
        }}
        table {{
            width: 100%;
            min-width: 500px;
            border-collapse: collapse;
            font-size: 0.95rem;
        }}
        th, td {{
            padding: 14px 12px;
            text-align: left;
            border-bottom: 1px solid #333;
        }}
        th {{
            color: #888;
            font-weight: 600;
            font-size: 0.9rem;
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
            font-size: 2rem;
            font-weight: 800;
            color: #4ade80;
        }}
        .stat-label {{
            font-size: 0.85rem;
            color: #888;
            margin-top: 8px;
            font-weight: 500;
        }}

        .footer {{
            text-align: center;
            padding: 30px 16px;
            color: #666;
            font-size: 0.85rem;
            border-top: 1px solid #333;
            margin-top: 40px;
            line-height: 1.8;
        }}
        .footer .data-sources {{
            margin-top: 12px;
            color: #555;
            font-size: 0.8rem;
        }}

        /* 平板和桌面端 */
        @media (min-width: 768px) {{
            body {{ padding: 20px; max-width: 1200px; }}
            html {{ font-size: 15px; }}
            .header h1 {{ font-size: 2rem; }}
            .industry-name {{ font-size: 1.4rem; }}
        }}

        /* 大屏优化 */
        @media (min-width: 1024px) {{
            html {{ font-size: 16px; }}
            .header h1 {{ font-size: 2.25rem; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 热点行业投资速览</h1>
        <div class="date">报告日期：{today}</div>
        <div class="sources">数据来源：财联社 | 新浪财经 | 东方财富 | 新华网 | 中国基金报 | AKShare</div>
    </div>

    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-value">{len(industries)}</div>
            <div class="stat-label">关注行业</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">15+</div>
            <div class="stat-label">龙头标的</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">5</div>
            <div class="stat-label">新闻来源</div>
        </div>
    </div>

    {cards_html}

    <div class="footer">
        <p>⚠️ 风险提示：以上内容基于公开数据整理，不构成投资建议。</p>
        <p class="data-sources">数据来源：财联社、新浪财经、东方财富股吧、新华网财经、中国基金报、AKShare</p>
        <p>数据更新时间：{today}</p>
    </div>
</body>
</html>"""

    output_file = OUTPUT_DIR / "index.html"
    output_file.write_text(html, encoding='utf-8')
    print(f"✅ 首页已生成: {output_file}")
    return output_file

def generate_pdf():
    """生成PDF报告"""
    print("🔄 正在生成PDF...")

    html_file = OUTPUT_DIR / "full_report_white.html"
    pdf_file = OUTPUT_DIR / f"行业研究报告_{datetime.now().strftime('%Y%m%d')}.pdf"

    cmd = [
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        f"--print-to-pdf={pdf_file}",
        "--print-to-pdf-no-header",
        "--run-all-compositor-stages-before-draw",
        f"file://{html_file}"
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=30)
        print(f"✅ PDF已生成: {pdf_file}")
        return pdf_file
    except subprocess.TimeoutExpired:
        print("⚠️ PDF生成超时，请稍后查看")
        return None
    except Exception as e:
        print(f"❌ PDF生成失败: {e}")
        return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='行业研究报告生成工具')
    parser.add_argument('--skip-news', action='store_true', help='跳过新闻抓取，使用缓存')
    parser.add_argument('--pdf', action='store_true', help='同时生成PDF')
    args = parser.parse_args()

    print("=" * 60)
    print("📊 行业研究报告生成工具")
    print("=" * 60)

    # 1. 准备目录
    ensure_directories()

    # 2. 加载行业数据
    industries = load_industry_list()
    print(f"✅ 已加载 {len(industries)} 个行业数据")

    # 3. 抓取新闻数据
    all_news = fetch_all_news(industries, skip_fetch=args.skip_news)

    # 4. 生成首页（包含新闻）
    generate_index_html(industries, all_news)

    # 5. 生成PDF（可选）
    if args.pdf:
        generate_pdf()

    print("\n" + "=" * 60)
    print("✅ 报告生成完成")
    print("=" * 60)
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print(f"🌐 首页: {OUTPUT_DIR / 'index.html'}")
    print("\n💡 提示：")
    if not args.skip_news:
        print("- 新闻数据已缓存1小时，可通过 --skip-news 跳过重复抓取")
    print("- 使用 --pdf 参数可同时生成PDF版本")

    return 0

if __name__ == "__main__":
    sys.exit(main())
