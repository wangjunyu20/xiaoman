# 集成指南：行情分析器 → 行业报告

## 集成步骤

### 步骤1: 修改详情页生成脚本

编辑 `/root/.openclaw/workspace_investment/skills/industry-research-report/scripts/generate_all_details.py`

在文件顶部添加导入：
```python
import sys
sys.path.insert(0, '/root/.openclaw/workspace_investment/skills/market-sentiment-analyzer/scripts')
from analyze import MarketSentimentAnalyzer

# 初始化分析器
analyzer = MarketSentimentAnalyzer()
```

### 步骤2: 在generate_detail_page函数中添加行情分析

```python
def generate_detail_page(industry):
    """生成详情页HTML"""
    
    # 原有代码：获取新闻等
    news_list = load_news(industry['name'], industry['file'])
    
    # 新增：获取行情分析
    try:
        market_analysis = analyzer.analyze(industry['name'], days=7)
        market_html = generate_market_section(market_analysis)
    except Exception as e:
        market_html = ""
        print(f"  ⚠️ 行情分析失败: {e}")
    
    # 原有代码：生成其他部分...
    
    # 在HTML中插入行情分析（放在新闻之后，股票之前）
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>...</head>
<body>
    ...
    
    <section>
        <h2>二、本周重大资讯</h2>
        ...
    </section>
    
    {market_html}  <!-- 新增：行情分析 -->
    
    <section>
        <h2>四、龙头股跟踪</h2>
        ...
    </section>
    ...
</body>
</html>'''
    
    return html
```

### 步骤3: 添加行情分析HTML生成函数

```python
def generate_market_section(analysis):
    """生成行情分析HTML"""
    
    market_data = analysis.get('market_data', {})
    sentiment = analysis.get('sentiment', {})
    reasoning = analysis.get('reasoning', '')
    risks = analysis.get('risks', [])
    
    # 如果行情数据失败，只显示舆情
    if 'error' in market_data:
        return f'''
    <section>
        <h2>三、舆情分析</h2>
        <div class="summary-box" style="border-left-color: #fbbf24;">
            <h3>📰 市场情绪</h3>
            <p>情绪标签：<span class="tag tag-neutral">{sentiment.get('sentiment_label', '中性')}</span></p>
            <p>新闻统计：利好 {sentiment.get('positive', 0)} / 利空 {sentiment.get('negative', 0)} / 中性 {sentiment.get('neutral', 0)}</p>
            <p>影响因素：{', '.join(sentiment.get('key_events', [])) if sentiment.get('key_events') else '暂无'}</p>
        </div>
    </section>'''
    
    # 正常显示完整分析
    change_pct = market_data.get('change_pct', 0)
    trend_color = "#4ade80" if change_pct > 0 else "#f87171" if change_pct < 0 else "#fbbf24"
    trend_arrow = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➡️"
    
    return f'''
    <section>
        <h2>三、行情与舆情分析</h2>
        
        <div class="summary-box" style="border-left-color: {trend_color};">
            <h3>{trend_arrow} 行情概况</h3>
            <table>
                <tr><th>指标</th><th>数值</th><th>说明</th></tr>
                <tr><td>涨跌幅</td><td style="color: {trend_color}; font-weight: bold;">{change_pct:+.2f}%</td><td>{market_data.get('trend', '震荡')}</td></tr>
                <tr><td>成交量</td><td>{market_data.get('volume_change', '持平')}</td><td>相对前日</td></tr>
                <tr><td>RSI指标</td><td>{market_data.get('rsi', 50)}</td><td>{market_data.get('technical_signal', '震荡')}</td></tr>
            </table>
        </div>
        
        <div class="summary-box">
            <h3>📰 舆情情绪</h3>
            <p>情绪标签：<span class="tag {'tag-good' if sentiment.get('sentiment_score', 0) > 10 else 'tag-bad' if sentiment.get('sentiment_score', 0) < -10 else 'tag-neutral'}">{sentiment.get('sentiment_label', '中性')}</span></p>
            <p>新闻统计：利好 {sentiment.get('positive', 0)} / 利空 {sentiment.get('negative', 0)} / 中性 {sentiment.get('neutral', 0)}</p>
            <p>影响因素：{', '.join(sentiment.get('key_events', [])) if sentiment.get('key_events') else '暂无显著影响因素'}</p>
        </div>
        
        <div class="summary-box" style="border-left-color: #60a5fa;">
            <h3>💡 走势解读</h3>
            <p>{reasoning}</p>
        </div>
        
        {f'''<div class="summary-box" style="border-left-color: #f87171;">
            <h3>⚠️ 风险提示</h3>
            <ul>
                {''.join([f"<li>{r}</li>" for r in risks])}
            </ul>
        </div>''' if risks else ''}
        
    </section>'''
```

### 步骤4: 测试集成

```bash
# 1. 测试单个行业
cd /root/.openclaw/workspace_investment/skills/industry-research-report
python3 scripts/generate_all_details.py

# 2. 检查输出
cat output/research_reports/reports/光模块.html | grep -A20 "行情与舆情分析"

# 3. 完整部署
./scripts/deploy_full.sh
```

## 预期效果

详情页新增"行情与舆情分析"章节，包含：
1. **行情概况** - 涨跌幅、成交量、技术指标
2. **舆情情绪** - 利好/利空统计、影响因素
3. **走势解读** - 自然语言分析涨跌原因
4. **风险提示** - 识别的主要风险因素

## 注意事项

1. **性能影响** - 每个行业增加1-2秒分析时间，15个行业约增加20-30秒
2. **容错处理** - 行情分析失败时不中断整个报告生成
3. **缓存策略** - 分析结果可缓存1小时，避免重复调用

## 示例输出

```html
<section>
    <h2>三、行情与舆情分析</h2>
    
    <div class="summary-box" style="border-left-color: #f87171;">
        <h3>📉 行情概况</h3>
        <table>
            <tr><th>指标</th><th>数值</th><th>说明</th></tr>
            <tr><td>涨跌幅</td><td style="color: #f87171; font-weight: bold;">-3.25%</td><td>下跌</td></tr>
            <tr><td>成交量</td><td>放大</td><td>相对前日</td></tr>
            <tr><td>RSI指标</td><td>35.5</td><td>超卖</td></tr>
        </table>
    </div>
    
    <div class="summary-box">
        <h3>📰 舆情情绪</h3>
        <p>情绪标签：<span class="tag tag-bad">偏空</span></p>
        <p>新闻统计：利好 2 / 利空 6 / 中性 2</p>
        <p>影响因素：中东局势、业绩发布</p>
    </div>
    
    <div class="summary-box" style="border-left-color: #60a5fa;">
        <h3>💡 走势解读</h3>
        <p>下跌3.25%。主要受中东局势等因素影响；市场情绪偏空，资金流出明显。中际旭创遭主力净卖出超17亿元，板块整体承压。</p>
    </div>
    
    <div class="summary-box" style="border-left-color: #f87171;">
        <h3>⚠️ 风险提示</h3>
        <ul>
            <li>地缘政治风险</li>
            <li>业绩不确定性</li>
        </ul>
    </div>
</section>
```
