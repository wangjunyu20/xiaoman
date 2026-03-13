#!/usr/bin/env python3
"""
集成示例：在generate_all_details.py中添加行情分析
复制此代码到 industry-research-report/scripts/generate_all_details.py
"""

# 在文件顶部添加导入
import sys
sys.path.insert(0, '/root/.openclaw/workspace_investment/skills/market-sentiment-analyzer/scripts')
try:
    from analyze import MarketSentimentAnalyzer
    analyzer = MarketSentimentAnalyzer()
    ANALYZER_AVAILABLE = True
except Exception as e:
    print(f"⚠️ 行情分析器加载失败: {e}")
    ANALYZER_AVAILABLE = False


def generate_market_analysis_section(industry_name: str) -> str:
    """生成行情分析HTML"""
    if not ANALYZER_AVAILABLE:
        return ""
    
    try:
        # 调用行情分析
        analysis = analyzer.analyze(industry_name, days=7)
        
        market_data = analysis.get('market_data', {})
        sentiment = analysis.get('sentiment', {})
        reasoning = analysis.get('reasoning', '')
        risks = analysis.get('risks', [])
        
        # 构建HTML
        html_parts = ['    <section>', '        <h2>三、行情与舆情分析</h2>']
        
        # 行情概况（如果有数据）
        if 'error' not in market_data:
            change_pct = market_data.get('change_pct', 0)
            trend_color = "#4ade80" if change_pct > 0 else "#f87171"
            trend_arrow = "📈" if change_pct > 0 else "📉"
            
            html_parts.append(f'''
        <div class="summary-box" style="border-left-color: {trend_color};">
            <h3>{trend_arrow} 行情概况</h3>
            <table>
                <tr><th>指标</th><th>数值</th><th>说明</th></tr>
                <tr><td>涨跌幅</td><td style="color: {trend_color}; font-weight: bold;">{change_pct:+.2f}%</td><td>{market_data.get('trend', '震荡')}</td></tr>
                <tr><td>成交量</td><td>{market_data.get('volume_change', '持平')}</td><td>相对前日</td></tr>
                <tr><td>RSI</td><td>{market_data.get('rsi', 50)}</td><td>{market_data.get('technical_signal', '震荡')}</td></tr>
            </table>
        </div>''')
        
        # 舆情情绪
        sentiment_label = sentiment.get('sentiment_label', '中性')
        sentiment_score = sentiment.get('sentiment_score', 0)
        tag_class = "tag-good" if sentiment_score > 10 else "tag-bad" if sentiment_score < -10 else "tag-neutral"
        
        html_parts.append(f'''
        <div class="summary-box">
            <h3>📰 舆情情绪</h3>
            <p>情绪标签：<span class="tag {tag_class}">{sentiment_label}</span></p>
            <p>新闻统计：利好 {sentiment.get('positive', 0)} / 利空 {sentiment.get('negative', 0)} / 中性 {sentiment.get('neutral', 0)}</p>
        </div>''')
        
        # 走势解读
        html_parts.append(f'''
        <div class="summary-box" style="border-left-color: #60a5fa;">
            <h3>💡 走势解读</h3>
            <p>{reasoning}</p>
        </div>''')
        
        # 风险提示
        if risks:
            risk_items = ''.join([f"                <li>{r}</li>\n" for r in risks])
            html_parts.append(f'''
        <div class="summary-box" style="border-left-color: #f87171;">
            <h3>⚠️ 风险提示</h3>
            <ul>
{risk_items}            </ul>
        </div>''')
        
        html_parts.append('    </section>')
        return '\n'.join(html_parts)
        
    except Exception as e:
        print(f"  ⚠️ 行情分析生成失败: {e}")
        return ""


# 使用示例：在generate_detail_page函数中添加
# 
# def generate_detail_page(industry):
#     # ... 原有代码 ...
#     
#     # 新增：行情分析
#     market_section = generate_market_analysis_section(industry['name'])
#     
#     html = f'''...{market_section}...'''
#     return html
