#!/usr/bin/env python3
"""
为所有16个行业生成详情页（集成舆情分析）
- 从market-sentiment-analyzer API获取舆情数据
- 首页显示概述，详情页显示完整因果分析
"""
import json
import sys
import re
from datetime import datetime
from pathlib import Path

# 添加market-sentiment-analyzer路径
sys.path.insert(0, str(Path("/root/.openclaw/workspace_investment/skills/market-sentiment-analyzer")))

# 导入PEST-M分析框架
try:
    from scripts.pestm_framework import PESTMFramework
    HAS_PESTM = True
except ImportError:
    HAS_PESTM = False

# 导入专业报告生成器
try:
    from scripts.professional_report_generator import ProfessionalReportGenerator
    HAS_PRO_REPORT = True
except ImportError:
    HAS_PRO_REPORT = False
    print("  ⚠️  专业报告生成器未找到")


def format_pestm_html(pestm_result: dict) -> str:
    """格式化PEST-M分析结果为HTML"""
    if not pestm_result:
        return ""
    
    dimensions = pestm_result.get('dimensions', {})
    overall_score = pestm_result.get('overall_score', 0)
    overall_rating = pestm_result.get('overall_rating', '')
    conflicts = pestm_result.get('conflicts', [])
    
    # 五维度名称映射
    dim_names = {
        'policy': 'P-政策',
        'economy': 'E-经济',
        'sentiment': 'S-情绪',
        'technology': 'T-技术',
        'market': 'M-市场'
    }
    
    # 构建五维分析HTML
    dims_html = ""
    for key, name in dim_names.items():
        dim = dimensions.get(key, {})
        score = dim.get('score', 3)
        stars = '⭐' * score
        facts = dim.get('facts', [])
        
        facts_html = ""
        for fact in facts[:2]:
            impact_emoji = {'利好': '🟢', '利空': '🔴', '中性': '⚪'}.get(fact.get('impact'), '⚪')
            facts_html += f"<div class='pestm-fact'>{impact_emoji} {fact.get('content', '')[:40]}</div>"
        
        dims_html += f"""
        <div class='pestm-dimension'>
            <div class='pestm-dim-header'>
                <span class='pestm-dim-name'>{name}</span>
                <span class='pestm-dim-score'>{stars} ({score}/5)</span>
            </div>
            <div class='pestm-dim-facts'>{facts_html}</div>
        </div>
        """
    
    # 观点分歧HTML
    conflicts_html = ""
    if conflicts:
        conflicts_html = "<div class='pestm-conflicts'><h5>⚖️ 观点分歧</h5>"
        for conf in conflicts:
            conflicts_html += f"""
            <div class='conflict-item'>
                <div>🟢 {conf.get('bullish_view', '看涨')[:30]}...</div>
                <div>🔴 {conf.get('bearish_view', '看空')[:30]}...</div>
            </div>
            """
        conflicts_html += "</div>"
    
    # 综合结论
    conclusion = pestm_result.get('conclusion', '')
    
    return f"""
    <div class='pestm-analysis'>
        <h4>📊 PEST-M 五维分析</h4>
        <div class='pestm-score'>综合评分: {overall_score}/5 ({overall_rating})</div>
        <div class='pestm-dimensions'>{dims_html}</div>
        {conflicts_html}
        <div class='pestm-conclusion'>💡 {conclusion}</div>
    </div>
    <style>
    .pestm-analysis {{ background: #252525; border-radius: 8px; padding: 16px; margin: 16px 0; }}
    .pestm-analysis h4 {{ color: #4ade80; margin-bottom: 12px; }}
    .pestm-score {{ font-size: 1.1rem; font-weight: 600; color: #fff; margin-bottom: 12px; }}
    .pestm-dimensions {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .pestm-dimension {{ background: #1a1a1a; padding: 12px; border-radius: 6px; }}
    .pestm-dim-header {{ display: flex; justify-content: space-between; margin-bottom: 8px; }}
    .pestm-dim-name {{ color: #ccc; font-weight: 500; }}
    .pestm-dim-score {{ color: #fbbf24; font-size: 0.9rem; }}
    .pestm-fact {{ font-size: 0.85rem; color: #aaa; margin: 4px 0; }}
    .pestm-conflicts {{ margin-top: 12px; padding-top: 12px; border-top: 1px solid #444; }}
    .pestm-conflicts h5 {{ color: #60a5fa; margin-bottom: 8px; }}
    .conflict-item {{ font-size: 0.85rem; margin: 8px 0; padding: 8px; background: #1a1a1a; border-radius: 4px; }}
    .pestm-conclusion {{ margin-top: 12px; padding: 12px; background: #1a472a; border-radius: 6px; color: #4ade80; font-size: 0.9rem; }}
    @media (max-width: 768px) {{ .pestm-dimensions {{ grid-template-columns: 1fr; }} }}
    </style>
    """


def format_detailed_html(detailed_text: str) -> str:
    """格式化详细分析文本为HTML"""
    if not detailed_text:
        return ""
    
    # 将文本转换为HTML
    lines = detailed_text.split('\n')
    html_lines = []
    in_list = False
    
    for line in lines:
        line = line.strip()
        if not line:
            if in_list:
                html_lines.append('</div>')
                in_list = False
            html_lines.append('<br>')
            continue
        
        # 标题行
        if line.startswith('【') and line.endswith('】'):
            if in_list:
                html_lines.append('</div>')
                in_list = False
            html_lines.append(f'<h5 class="detailed-section-title">{line}</h5>')
        
        # 列表项
        elif line.startswith(('•', '▶')):
            if not in_list:
                html_lines.append('<div class="detailed-list">')
                in_list = True
            content = line[1:].strip()
            html_lines.append(f'<div class="detailed-item">{content}</div>')
        
        # 数字列表项
        elif re.match(r'^\d+\.', line):
            if not in_list:
                html_lines.append('<div class="detailed-list">')
                in_list = True
            html_lines.append(f'<div class="detailed-item">{line}</div>')
        
        # 普通文本
        else:
            if in_list:
                html_lines.append('</div>')
                in_list = False
            html_lines.append(f'<p class="detailed-text">{line}</p>')
    
    if in_list:
        html_lines.append('</div>')
    
    content_html = '\n'.join(html_lines)
    
    return f"""
    <div class='detailed-analysis'>
        <h4>📑 详细分析</h4>
        <div class='detailed-content'>
            {content_html}
        </div>
    </div>
    <style>
    .detailed-analysis {{ background: #1e1e2e; border-radius: 8px; padding: 16px; margin: 16px 0; border-left: 4px solid #60a5fa; }}
    .detailed-analysis h4 {{ color: #60a5fa; margin-bottom: 12px; }}
    .detailed-content {{ font-size: 0.9rem; line-height: 1.8; color: #ccc; }}
    .detailed-section-title {{ color: #fbbf24; font-weight: 600; margin: 12px 0 8px; font-size: 0.95rem; }}
    .detailed-list {{ margin: 8px 0; padding-left: 12px; }}
    .detailed-item {{ margin: 4px 0; padding: 4px 0; border-bottom: 1px solid #333; }}
    .detailed-item:last-child {{ border-bottom: none; }}
    .detailed-text {{ margin: 4px 0; }}
    </style>
    """



# 直接从cache读取舆情数据
SENTIMENT_CACHE_DIR = Path("/root/.openclaw/workspace_investment/skills/market-sentiment-analyzer/output/cache")

# 行业名称映射（从报告系统名称映射到舆情系统cache文件名）
INDUSTRY_NAME_MAP = {
    "光模块": "光模块",
    "算力基础设施": "算力",
    "具身智能/人形机器人": "人形机器人",
    "量子科技": "量子科技",
    "脑机接口": "脑机接口",
    "AI应用": "AI应用",
    "低空经济": "低空经济",
    "集成电路": "芯片",
    "生物医药": "生物医药",
    "航空航天": "航空航天",
    "消费": "消费",
    "6G": "6G",
    "卫星互联网": "卫星互联网",
    "可控核聚变": "可控核聚变",
    "AI+医疗": "AI医疗",
    "人形机器人": "人形机器人",
    "半导体": "芯片",
    "卫星": "卫星互联网",
}

def get_sentiment_from_cache(industry_name):
    """从cache文件读取舆情分析数据 - 查找最近一天"""
    
    # 使用映射表转换行业名称
    mapped_name = INDUSTRY_NAME_MAP.get(industry_name, industry_name)
    
    # 查找所有匹配的缓存文件（不按日期限制）
    possible_prefixes = [
        mapped_name,
        mapped_name.replace('/', '_'),
        industry_name,
    ]
    
    matched_files = []
    for prefix in possible_prefixes:
        for cache_file in SENTIMENT_CACHE_DIR.glob(f"{prefix}_*.json"):
            if cache_file.exists():
                # 提取日期部分
                try:
                    date_str = cache_file.stem.split('_')[-1]
                    if date_str.isdigit() and len(date_str) == 8:
                        matched_files.append((cache_file, int(date_str)))
                except:
                    pass
    
    # 按日期排序，取最新的
    if matched_files:
        matched_files.sort(key=lambda x: x[1], reverse=True)
        cache_file = matched_files[0][0]
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"  ⚠️ 读取cache失败: {e}")
    
    return None

OUTPUT_DIR = Path("/root/.openclaw/workspace_investment/output/research_reports")
REPORTS_DIR = OUTPUT_DIR / "reports"
NEWS_CACHE = Path("/root/.openclaw/workspace_investment/output/news_cache")

today = datetime.now().strftime("%Y年%m月%d日")
now = datetime.now().strftime("%Y-%m-%d %H:%M")

# 16个行业数据
INDUSTRIES = [
    {"name": "消费", "icon": "🛒", "file": "consumption", 
     "stocks": [{"name": "中国中免", "code": "601888", "price": 68.50, "change": 1.23}, {"name": "贵州茅台", "code": "600519", "price": 1588.00, "change": 0.56}, {"name": "伊利股份", "code": "600887", "price": 28.35, "change": -0.42}],
     "tag": "政策首位", "summary": "政府十项任务第一位，2500亿特别国债+1000亿专项资金支持", "heat": "🔥🔥🔥🔥🔥 极高"},
    {"name": "集成电路", "icon": "🧩", "file": "semiconductor",
     "stocks": [{"name": "中芯国际", "code": "688981", "price": 82.35, "change": 2.15}, {"name": "北方华创", "code": "002371", "price": 445.20, "change": 3.68}, {"name": "韦尔股份", "code": "603501", "price": 128.60, "change": 1.92}],
     "tag": "国产替代", "summary": "新兴支柱产业，央企带头开放应用场景", "heat": "🔥🔥🔥🔥🔥 极高"},
    {"name": "光模块", "icon": "🔌", "file": "optical_module",
     "stocks": [{"name": "中际旭创", "code": "300308", "price": 557.00, "change": -4.36}, {"name": "天孚通信", "code": "300394", "price": 334.80, "change": -4.15}, {"name": "新易盛", "code": "300502", "price": 401.24, "change": -4.50}],
     "tag": "业绩爆发", "summary": "AI基础设施，受中东局势影响今日回调", "heat": "🔥🔥🔥🔥🔥 极高"},
    {"name": "算力基础设施", "icon": "🖥️", "file": "computing_infra",
     "stocks": [{"name": "中科曙光", "code": "603019", "price": 72.45, "change": 2.45}, {"name": "浪潮信息", "code": "000977", "price": 48.92, "change": 2.85}, {"name": "紫光股份", "code": "000938", "price": 32.15, "change": 1.95}],
     "tag": "智算集群", "summary": "AI基础设施，大单签订推动板块上涨", "heat": "🔥🔥🔥🔥🔥 极高"},
    {"name": "具身智能/人形机器人", "icon": "🦾", "file": "embodied_ai",
     "stocks": [{"name": "埃斯顿", "code": "002747", "price": 21.99, "change": -1.20}, {"name": "汇川技术", "code": "300124", "price": 68.25, "change": -1.80}, {"name": "拓斯达", "code": "300607", "price": 18.45, "change": -3.20}],
     "tag": "人机融合", "summary": "未来产业，利好兑现后回调", "heat": "🔥🔥🔥🔥🔥 极高"},
    {"name": "量子科技", "icon": "⚛️", "file": "quantum",
     "stocks": [{"name": "国盾量子", "code": "688027", "price": 712.05, "change": -0.88}, {"name": "四创电子", "code": "600990", "price": 25.98, "change": -1.07}, {"name": "三维通信", "code": "002115", "price": 13.86, "change": 1.91}],
     "tag": "技术突破", "summary": "未来产业，十五五首位+北大量子网络突破", "heat": "🔥🔥🔥🔥 高"},
    {"name": "脑机接口", "icon": "🧬", "file": "brain_machine",
     "stocks": [{"name": "三博脑科", "code": "301293", "price": 74.02, "change": 1.84}, {"name": "国际医学", "code": "000516", "price": 4.55, "change": 0.50}],
     "tag": "前沿探索", "summary": "未来产业，Neuralink 2026大规模生产", "heat": "🔥🔥 中低"},
    {"name": "低空经济", "icon": "🚁", "file": "low_altitude",
     "stocks": [{"name": "万丰奥威", "code": "002085", "price": 18.25, "change": -0.25}, {"name": "中信海直", "code": "000099", "price": 28.45, "change": 0.50}, {"name": "纵横股份", "code": "688070", "price": 42.18, "change": 1.20}],
     "tag": "新基建", "summary": "新兴支柱产业，2026年低空经济商业化元年", "heat": "🔥🔥🔥🔥🔥 极高"},
    {"name": "AI应用", "icon": "🤖", "file": "ai_app",
     "stocks": [{"name": "科大讯飞", "code": "002230", "price": 52.19, "change": 1.04}, {"name": "广联达", "code": "002410", "price": 12.59, "change": 0.80}],
     "tag": "产业加速", "summary": "AI应用层，腾讯AI应用落地推动板块", "heat": "🔥🔥🔥🔥🔥 极高"},
    {"name": "生物医药", "icon": "💊", "file": "biotech",
     "stocks": [{"name": "药明康德", "code": "603259", "price": 58.20, "change": 0.50}, {"name": "恒瑞医药", "code": "600276", "price": 48.50, "change": 1.20}],
     "tag": "创新药", "summary": "AI+医疗应用场景加速落地", "heat": "🔥🔥🔥 中等"},
    {"name": "航空航天", "icon": "🚀", "file": "aerospace",
     "stocks": [{"name": "中航沈飞", "code": "600760", "price": 58.25, "change": 1.50}, {"name": "航发动力", "code": "600893", "price": 42.80, "change": 0.80}],
     "tag": "军工", "summary": "新兴支柱产业，央企带头开放应用场景", "heat": "🔥🔥🔥🔥 高"},
    {"name": "6G", "icon": "📡", "file": "6g",
     "stocks": [{"name": "中兴通讯", "code": "000063", "price": 38.50, "change": 1.20}, {"name": "信维通信", "code": "300136", "price": 24.80, "change": 0.50}],
     "tag": "通信", "summary": "未来产业，6G技术研发加速", "heat": "🔥🔥🔥🔥 高"},
    {"name": "卫星互联网", "icon": "🛰️", "file": "satellite",
     "stocks": [{"name": "中国卫星", "code": "600118", "price": 28.50, "change": 0.80}, {"name": "北斗星通", "code": "002151", "price": 32.20, "change": 1.20}],
     "tag": "航天", "summary": "未来产业，低轨卫星组网加速", "heat": "🔥🔥🔥🔥 高"},
    {"name": "可控核聚变", "icon": "⚡", "file": "nuclear_fusion",
     "stocks": [{"name": "东方电气", "code": "600875", "price": 42.21, "change": -4.55}, {"name": "中国核建", "code": "601611", "price": 16.79, "change": 1.39}],
     "tag": "未来能源", "summary": "未来产业，十五五未来产业，技术突破尚需时日", "heat": "🔥🔥 中低"},
    {"name": "AI+医疗", "icon": "🏥", "file": "ai_healthcare",
     "stocks": [{"name": "卫宁健康", "code": "300253", "price": 9.52, "change": -1.65}, {"name": "爱尔眼科", "code": "300015", "price": 10.18, "change": -1.36}],
     "tag": "智慧医疗", "summary": "AI应用层，AI应用场景落地，龙头稳健发展", "heat": "🔥🔥🔥 中等"},
    {"name": "人形机器人", "icon": "🤖", "file": "robot",
     "stocks": [{"name": "埃斯顿", "code": "002747", "price": 21.99, "change": -1.20}, {"name": "汇川技术", "code": "300124", "price": 68.25, "change": -1.80}],
     "tag": "机器人", "summary": "人形机器人产业链", "heat": "🔥🔥🔥🔥🔥 极高"},
]

def get_sentiment_for_industry(industry_name):
    """获取行业舆情分析数据"""
    # 直接从cache读取
    return get_sentiment_from_cache(industry_name)


def format_pestm_html(pestm_result: dict) -> str:
    """格式化PEST-M分析结果为HTML"""
    if not pestm_result:
        return ""
    
    dimensions = pestm_result.get('dimensions', {})
    overall_score = pestm_result.get('overall_score', 0)
    overall_rating = pestm_result.get('overall_rating', '')
    conflicts = pestm_result.get('conflicts', [])
    
    # 五维度名称映射
    dim_names = {
        'policy': 'P-政策',
        'economy': 'E-经济',
        'sentiment': 'S-情绪',
        'technology': 'T-技术',
        'market': 'M-市场'
    }
    
    # 构建五维分析HTML
    dims_html = ""
    for key, name in dim_names.items():
        dim = dimensions.get(key, {})
        score = dim.get('score', 3)
        stars = '⭐' * score
        facts = dim.get('facts', [])
        
        facts_html = ""
        for fact in facts[:2]:
            impact_emoji = {'利好': '🟢', '利空': '🔴', '中性': '⚪'}.get(fact.get('impact'), '⚪')
            facts_html += f"<div class='pestm-fact'>{impact_emoji} {fact.get('content', '')[:40]}</div>"
        
        dims_html += f"""
        <div class='pestm-dimension'>
            <div class='pestm-dim-header'>
                <span class='pestm-dim-name'>{name}</span>
                <span class='pestm-dim-score'>{stars} ({score}/5)</span>
            </div>
            <div class='pestm-dim-facts'>{facts_html}</div>
        </div>
        """
    
    # 观点分歧HTML
    conflicts_html = ""
    if conflicts:
        conflicts_html = "<div class='pestm-conflicts'><h5>⚖️ 观点分歧</h5>"
        for conf in conflicts:
            conflicts_html += f"""
            <div class='conflict-item'>
                <div>🟢 {conf.get('bullish_view', '看涨')[:30]}...</div>
                <div>🔴 {conf.get('bearish_view', '看空')[:30]}...</div>
            </div>
            """
        conflicts_html += "</div>"
    
    # 综合结论
    conclusion = pestm_result.get('conclusion', '')
    
    return f"""
    <div class='pestm-analysis'>
        <h4>📊 PEST-M 五维分析</h4>
        <div class='pestm-score'>综合评分: {overall_score}/5 ({overall_rating})</div>
        <div class='pestm-dimensions'>{dims_html}</div>
        {conflicts_html}
        <div class='pestm-conclusion'>💡 {conclusion}</div>
    </div>
    <style>
    .pestm-analysis {{ background: #252525; border-radius: 8px; padding: 16px; margin: 16px 0; }}
    .pestm-analysis h4 {{ color: #4ade80; margin-bottom: 12px; }}
    .pestm-score {{ font-size: 1.1rem; font-weight: 600; color: #fff; margin-bottom: 12px; }}
    .pestm-dimensions {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .pestm-dimension {{ background: #1a1a1a; padding: 12px; border-radius: 6px; }}
    .pestm-dim-header {{ display: flex; justify-content: space-between; margin-bottom: 8px; }}
    .pestm-dim-name {{ color: #ccc; font-weight: 500; }}
    .pestm-dim-score {{ color: #fbbf24; font-size: 0.9rem; }}
    .pestm-fact {{ font-size: 0.85rem; color: #aaa; margin: 4px 0; }}
    .pestm-conflicts {{ margin-top: 12px; padding-top: 12px; border-top: 1px solid #444; }}
    .pestm-conflicts h5 {{ color: #60a5fa; margin-bottom: 8px; }}
    .conflict-item {{ font-size: 0.85rem; margin: 8px 0; padding: 8px; background: #1a1a1a; border-radius: 4px; }}
    .pestm-conclusion {{ margin-top: 12px; padding: 12px; background: #1a472a; border-radius: 6px; color: #4ade80; font-size: 0.9rem; }}
    @media (max-width: 768px) {{ .pestm-dimensions {{ grid-template-columns: 1fr; }} }}
    </style>
    """


def generate_sentiment_section(data, industry_name=""):
    """生成舆情分析栏目HTML（含PEST-M分析）"""
    if not data:
        return ""
    
    # 从cache数据结构中提取
    market_data = data.get('market_data', {})
    sentiment = data.get('sentiment', {})
    
    # 涨跌样式 - 从market_data或sentiment获取
    change_pct = market_data.get('change_pct', 0) if isinstance(market_data, dict) else 0
    change_class = "trend-up" if change_pct > 0 else ("trend-down" if change_pct < 0 else "trend-neutral")
    change_str = f"{change_pct:+.2f}%"
    
    # 情绪标签
    sentiment_label = sentiment.get('sentiment_label', '中性') if isinstance(sentiment, dict) else '中性'
    
    # 关键因素标签
    key_factors_html = ""
    key_events = sentiment.get('key_events', []) if isinstance(sentiment, dict) else []
    for factor in key_events[:5]:
        key_factors_html += f'<span class="factor-tag">{factor}</span>'
    
    # PEST-M分析（如果框架可用）
    pestm_html = ""
    llm_analysis_html = ""
    pestm_result = None
    
    if HAS_PESTM and industry_name:
        try:
            framework = PESTMFramework()
            news_list = sentiment.get('latest_news', [])
            pestm_result = framework.analyze(industry_name, news_list, market_data)
            pestm_html = format_pestm_html(pestm_result)
        except Exception as e:
            print(f"  ⚠️  PEST-M分析失败: {e}")
    
    # 专业分析报告（如果可用）
    pro_report_html = ""
    if HAS_PRO_REPORT and industry_name:
        try:
            generator = ProfessionalReportGenerator()
            news_list = sentiment.get('latest_news', [])
            report_result = generator.generate(industry_name, news_list)
            pro_report_html = generator.format_html(report_result)
        except Exception as e:
            print(f"  ⚠️  专业报告生成失败: {e}")
    
    # 分析文本 - 使用多步因果推导
    causal_analysis = data.get('causal_analysis', data.get('reasoning', '暂无分析数据'))
    # 将换行符转换为HTML换行
    causal_html = causal_analysis.replace('\n\n', '</p><p>').replace('\n', '<br>')
    
    # 最新新闻
    latest_news = sentiment.get('latest_news', []) if isinstance(sentiment, dict) else []
    news_html = ""
    for news in latest_news[:3]:
        title = news.get('title', '')[:40] + '...' if len(news.get('title', '')) > 40 else news.get('title', '')
        impact = news.get('impact', '中性')
        impact_class = {'利好': 'impact-positive', '利空': 'impact-negative'}.get(impact, 'impact-neutral')
        news_html += f'<div class="news-item-small"><span class="news-source-small">{news.get("source", "")}</span><span class="news-title-small">{title}</span><span class="news-impact {impact_class}">{impact}</span></div>'
    
    return f'''
    <section class="sentiment-section">
        <h2>📊 行情与舆情分析</h2>
        <div class="sentiment-overview">
            <div class="change-box {change_class}">
                <span class="change-label">涨跌幅度</span>
                <span class="change-value">{change_str}</span>
            </div>
            <div class="sentiment-box">
                <span class="sentiment-label">市场情绪</span>
                <span class="sentiment-value">{sentiment_label}</span>
            </div>
            <div class="factors-box">
                <span class="factors-label">核心因素</span>
                <div class="factors-list">{key_factors_html}</div>
            </div>
        </div>
        {pestm_html}
        {pro_report_html}
        <div class="reasoning-box">
            <h4>📋 多步因果推导（综述）</h4>
            <p>{causal_html}</p>
        </div>
        <div class="latest-news">
            <!-- 命名规范v2026-03-12: 统一为"行业资讯"，详情页展示完整列表 -->
            <h4>📰 行业资讯（完整列表）</h4>
            {news_html}
        </div>
    </section>
    <style>
    .sentiment-section {{
        background: #1a1a1a;
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
        border: 1px solid #333;
    }}
    .sentiment-section h2 {{
        color: #fff;
        font-size: 1.3rem;
        margin-bottom: 16px;
        border-bottom: 2px solid #4ade80;
        padding-bottom: 8px;
    }}
    .sentiment-overview {{
        display: flex;
        gap: 16px;
        margin-bottom: 16px;
        flex-wrap: wrap;
    }}
    .change-box, .sentiment-box, .factors-box {{
        background: #252525;
        border-radius: 8px;
        padding: 12px 16px;
        flex: 1;
        min-width: 120px;
    }}
    .change-label, .sentiment-label, .factors-label {{
        display: block;
        color: #888;
        font-size: 0.85rem;
        margin-bottom: 4px;
    }}
    .change-value {{
        font-size: 1.5rem;
        font-weight: 700;
    }}
    .sentiment-value {{
        font-size: 1.2rem;
        color: #60a5fa;
    }}
    .trend-up {{ color: #f87171; }}
    .trend-down {{ color: #4ade80; }}
    .trend-neutral {{ color: #fbbf24; }}
    .factor-tag {{
        display: inline-block;
        background: #333;
        color: #aaa;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        margin: 2px;
    }}
    .reasoning-box {{
        background: #252525;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
    }}
    .reasoning-box h4 {{
        color: #4ade80;
        margin-bottom: 8px;
    }}
    .reasoning-box p {{
        color: #ccc;
        line-height: 1.8;
        margin: 0;
    }}
    .latest-news {{
        background: #1f1f1f;
        border-radius: 8px;
        padding: 16px;
        border-left: 3px solid #60a5fa;
    }}
    .latest-news h4 {{
        color: #60a5fa;
        margin-bottom: 12px;
    }}
    .news-item-small {{
        display: flex;
        gap: 10px;
        padding: 8px 0;
        border-bottom: 1px solid #333;
        font-size: 0.9rem;
    }}
    .news-item-small:last-child {{ border-bottom: none; }}
    .news-source-small {{
        color: #888;
        min-width: 60px;
        font-size: 0.8rem;
    }}
    .news-title-small {{
        flex: 1;
        color: #bbb;
    }}
    .news-impact {{
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 10px;
    }}
    .impact-positive {{ background: #1a472a; color: #4ade80; }}
    .impact-negative {{ background: #5a1f1f; color: #f87171; }}
    .impact-neutral {{ background: #3a3a3a; color: #bbb; }}
    </style>
    '''

def generate_detail_page(ind):
    """生成行业详情页HTML"""
    
    # 获取舆情分析数据
    print(f"  🔍 获取舆情分析: {ind['name']}")
    sentiment_data = get_sentiment_for_industry(ind['name'])
    
    # 生成舆情栏目（传递行业名称以启用PEST-M分析）
    sentiment_html = generate_sentiment_section(sentiment_data, ind['name']) if sentiment_data else ""
    
    # 生成新闻列表HTML（从舆情数据）
    news_html = ""
    if sentiment_data:
        news_list = sentiment_data.get('sentiment', {}).get('latest_news', [])
        for news in news_list[:5]:  # 最多显示5条
            source = news.get('source', '')
            title = news.get('title', '')[:50] + '...' if len(news.get('title', '')) > 50 else news.get('title', '')
            impact = news.get('impact', '中性')
            impact_class = {'利好': 'impact-positive', '利空': 'impact-negative'}.get(impact, 'impact-neutral')
            news_html += f'<div class="news-item-small"><span class="news-source-small">{source}</span><span class="news-title-small">{title}</span><span class="news-impact {impact_class}">{impact}</span></div>'
    
    if not news_html:
        news_html = '<p style="color: #888;">暂无可展示的行业资讯</p>'
    
    stocks_html = "".join([f"""
        <tr>
            <td>{s['name']}</td>
            <td>{s['code']}</td>
            <td>¥{s['price']:.2f}</td>
            <td class='{"up" if s["change"] > 0 else "down"}'>{s['change']:+.2f}%</td>
        </tr>""" for s in ind['stocks']])
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{ind['name']} - 行业投资分析</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #e5e5e5;
            line-height: 1.8;
            padding: 16px;
        }}
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            border: 1px solid #333;
        }}
        .header h1 {{ font-size: 1.5rem; margin-bottom: 8px; }}
        .tag {{ display: inline-block; background: #4ade80; color: #000; padding: 4px 12px; border-radius: 12px; font-size: 0.85rem; font-weight: 600; margin-right: 8px; }}
        .heat {{ color: #f87171; }}
        
        section {{
            background: #1a1a1a;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #333;
        }}
        section h2 {{
            color: #fff;
            font-size: 1.2rem;
            margin-bottom: 16px;
            border-bottom: 2px solid #4ade80;
            padding-bottom: 8px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #333;
        }}
        th {{ color: #888; font-weight: 600; }}
        .up {{ color: #f87171; }}
        .down {{ color: #4ade80; }}
        
        .back-link {{
            display: inline-block;
            color: #60a5fa;
            text-decoration: none;
            margin-bottom: 20px;
        }}
        
        .footer {{
            text-align: center;
            color: #666;
            font-size: 0.85rem;
            margin-top: 40px;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <a href="../index.html" class="back-link">← 返回首页</a>
    
    <div class="header">
        <h1>{ind['icon']} {ind['name']}</h1>
        <span class="tag">{ind['tag']}</span>
        <span class="heat">{ind['heat']}</span>
        <p style="margin-top: 12px; color: #aaa;">{ind['summary']}</p>
    </div>
    
    {sentiment_html}
    
    <section>
        <h2>📈 成分股行情</h2>
        <table>
            <tr><th>名称</th><th>代码</th><th>价格</th><th>涨跌</th></tr>
            {stocks_html}
        </table>
    </section>
    
    <section>
        <!-- 命名规范v2026-03-12: 统一为"行业资讯" -->
        <h2>📰 行业资讯（完整列表）</h2>
        {news_html}
    </section>
    
    <section>
        <h2>⚠️ 风险提示</h2>
        <ul style="color: #aaa; padding-left: 20px;">
            <li>市场波动风险</li>
            <li>政策变化风险</li>
            <li>技术迭代风险</li>
        </ul>
    </section>
    
    <div class="footer">
        <p>⚠️ 风险提示：以上内容基于公开数据整理，不构成投资建议。</p>
        <p>数据更新时间：{now}</p>
    </div>
</body>
</html>'''
    
    return html

# 主程序
if __name__ == "__main__":
    print("=" * 60)
    print("生成行业详情页（集成舆情分析）")
    print("=" * 60)
    
    # 确保目录存在
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 生成所有行业详情页
    success_count = 0
    for ind in INDUSTRIES:
        try:
            html = generate_detail_page(ind)
            (REPORTS_DIR / f"{ind['file']}.html").write_text(html, encoding='utf-8')
            print(f"✅ {ind['name']}")
            success_count += 1
        except Exception as e:
            print(f"❌ {ind['name']}: {e}")
    
    print(f"\n✅ 共生成 {success_count}/{len(INDUSTRIES)} 个行业详情页")
    print(f"📁 输出目录: {REPORTS_DIR}")


def format_pestm_html(pestm_result: dict) -> str:
    """格式化PEST-M分析结果为HTML"""
    if not pestm_result:
        return ""
    
    dimensions = pestm_result.get('dimensions', {})
    overall_score = pestm_result.get('overall_score', 0)
    overall_rating = pestm_result.get('overall_rating', '')
    conflicts = pestm_result.get('conflicts', [])
    
    # 五维度名称映射
    dim_names = {
        'policy': 'P-政策',
        'economy': 'E-经济',
        'sentiment': 'S-情绪',
        'technology': 'T-技术',
        'market': 'M-市场'
    }
    
    # 构建五维分析HTML
    dims_html = ""
    for key, name in dim_names.items():
        dim = dimensions.get(key, {})
        score = dim.get('score', 3)
        stars = '⭐' * score
        facts = dim.get('facts', [])
        
        facts_html = ""
        for fact in facts[:2]:
            impact_emoji = {'利好': '🟢', '利空': '🔴', '中性': '⚪'}.get(fact.get('impact'), '⚪')
            facts_html += f"<div class='pestm-fact'>{impact_emoji} {fact.get('content', '')[:40]}</div>"
        
        dims_html += f"""
        <div class='pestm-dimension'>
            <div class='pestm-dim-header'>
                <span class='pestm-dim-name'>{name}</span>
                <span class='pestm-dim-score'>{stars} ({score}/5)</span>
            </div>
            <div class='pestm-dim-facts'>{facts_html}</div>
        </div>
        """
    
    # 观点分歧HTML
    conflicts_html = ""
    if conflicts:
        conflicts_html = "<div class='pestm-conflicts'><h5>⚖️ 观点分歧</h5>"
        for conf in conflicts:
            conflicts_html += f"""
            <div class='conflict-item'>
                <div>🟢 {conf.get('bullish_view', '看涨')[:30]}...</div>
                <div>🔴 {conf.get('bearish_view', '看空')[:30]}...</div>
            </div>
            """
        conflicts_html += "</div>"
    
    # 综合结论
    conclusion = pestm_result.get('conclusion', '')
    
    return f"""
    <div class='pestm-analysis'>
        <h4>📊 PEST-M 五维分析</h4>
        <div class='pestm-score'>综合评分: {overall_score}/5 ({overall_rating})</div>
        <div class='pestm-dimensions'>{dims_html}</div>
        {conflicts_html}
        <div class='pestm-conclusion'>💡 {conclusion}</div>
    </div>
    <style>
    .pestm-analysis {{ background: #252525; border-radius: 8px; padding: 16px; margin: 16px 0; }}
    .pestm-analysis h4 {{ color: #4ade80; margin-bottom: 12px; }}
    .pestm-score {{ font-size: 1.1rem; font-weight: 600; color: #fff; margin-bottom: 12px; }}
    .pestm-dimensions {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .pestm-dimension {{ background: #1a1a1a; padding: 12px; border-radius: 6px; }}
    .pestm-dim-header {{ display: flex; justify-content: space-between; margin-bottom: 8px; }}
    .pestm-dim-name {{ color: #ccc; font-weight: 500; }}
    .pestm-dim-score {{ color: #fbbf24; font-size: 0.9rem; }}
    .pestm-fact {{ font-size: 0.85rem; color: #aaa; margin: 4px 0; }}
    .pestm-conflicts {{ margin-top: 12px; padding-top: 12px; border-top: 1px solid #444; }}
    .pestm-conflicts h5 {{ color: #60a5fa; margin-bottom: 8px; }}
    .conflict-item {{ font-size: 0.85rem; margin: 8px 0; padding: 8px; background: #1a1a1a; border-radius: 4px; }}
    .pestm-conclusion {{ margin-top: 12px; padding: 12px; background: #1a472a; border-radius: 6px; color: #4ade80; font-size: 0.9rem; }}
    @media (max-width: 768px) {{ .pestm-dimensions {{ grid-template-columns: 1fr; }} }}
    </style>
    """


def format_detailed_html(detailed_text: str) -> str:
    """格式化详细分析文本为HTML"""
    if not detailed_text:
        return ""
    
    # 将文本转换为HTML
    lines = detailed_text.split('\n')
    html_lines = []
    in_list = False
    
    for line in lines:
        line = line.strip()
        if not line:
            if in_list:
                html_lines.append('</div>')
                in_list = False
            html_lines.append('<br>')
            continue
        
        # 标题行
        if line.startswith('【') and line.endswith('】'):
            if in_list:
                html_lines.append('</div>')
                in_list = False
            html_lines.append(f'<h5 class="detailed-section-title">{line}</h5>')
        
        # 列表项
        elif line.startswith(('•', '▶')):
            if not in_list:
                html_lines.append('<div class="detailed-list">')
                in_list = True
            content = line[1:].strip()
            html_lines.append(f'<div class="detailed-item">{content}</div>')
        
        # 数字列表项
        elif re.match(r'^\d+\.', line):
            if not in_list:
                html_lines.append('<div class="detailed-list">')
                in_list = True
            html_lines.append(f'<div class="detailed-item">{line}</div>')
        
        # 普通文本
        else:
            if in_list:
                html_lines.append('</div>')
                in_list = False
            html_lines.append(f'<p class="detailed-text">{line}</p>')
    
    if in_list:
        html_lines.append('</div>')
    
    content_html = '\n'.join(html_lines)
    
    return f"""
    <div class='detailed-analysis'>
        <h4>📑 详细分析</h4>
        <div class='detailed-content'>
            {content_html}
        </div>
    </div>
    <style>
    .detailed-analysis {{ background: #1e1e2e; border-radius: 8px; padding: 16px; margin: 16px 0; border-left: 4px solid #60a5fa; }}
    .detailed-analysis h4 {{ color: #60a5fa; margin-bottom: 12px; }}
    .detailed-content {{ font-size: 0.9rem; line-height: 1.8; color: #ccc; }}
    .detailed-section-title {{ color: #fbbf24; font-weight: 600; margin: 12px 0 8px; font-size: 0.95rem; }}
    .detailed-list {{ margin: 8px 0; padding-left: 12px; }}
    .detailed-item {{ margin: 4px 0; padding: 4px 0; border-bottom: 1px solid #333; }}
    .detailed-item:last-child {{ border-bottom: none; }}
    .detailed-text {{ margin: 4px 0; }}
    </style>
    """
