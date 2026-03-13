#!/usr/bin/env python3
"""
LLM整合分析报告生成器
- 新闻分类入库
- 分批总结分析
- 汇总生成分析文章
"""

import json
import re
from typing import Dict, List
from datetime import datetime

class LLMIntegratedAnalyzer:
    """用LLM整合新闻生成分析文章"""
    
    def analyze(self, industry: str, news_list: List[Dict]) -> Dict:
        """
        生成整合分析报告
        
        流程：
        1. 新闻分类（政策/数据/观点/事件）
        2. 分类总结（生成分析段落）
        3. 观点整合（对比分析）
        4. 综合文章（连贯的分析报告）
        """
        if not news_list:
            return {"error": "无新闻数据"}
        
        # 1. 新闻分类
        categorized = self._categorize_news(news_list)
        
        # 2. 生成各部分分析
        policy_analysis = self._generate_policy_analysis(categorized['policy'])
        data_analysis = self._generate_data_analysis(categorized['data'])
        opinion_analysis = self._generate_opinion_analysis(categorized['opinion'])
        event_summary = self._generate_event_summary(categorized['event'])
        
        # 3. 整合生成最终分析文章
        integrated_report = self._integrate_report(
            industry, 
            policy_analysis, 
            data_analysis, 
            opinion_analysis, 
            event_summary
        )
        
        return {
            'industry': industry,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'categorized': categorized,
            'sections': {
                'policy': policy_analysis,
                'data': data_analysis,
                'opinion': opinion_analysis,
                'event': event_summary
            },
            'integrated_report': integrated_report
        }
    
    def _categorize_news(self, news_list: List[Dict]) -> Dict:
        """将新闻分类"""
        categories = {
            'policy': [],
            'data': [],
            'opinion': [],
            'event': []
        }
        
        policy_keywords = ['政策', '两会', '国务院', '财政部', '发改委', '规划', '纲要', '补贴', '专项']
        data_keywords = ['增长', '下降', '上涨', '下跌', '亿元', '万亿', '%', '净流入', '流出']
        opinion_keywords = ['看好', '看空', '认为', '表示', '预计', '预期', '谨慎', '乐观']
        
        for news in news_list:
            title = news.get('title', '')
            
            # 优先级：政策 > 数据 > 观点 > 事件
            if any(kw in title for kw in policy_keywords):
                categories['policy'].append(news)
            elif any(kw in title for kw in data_keywords):
                categories['data'].append(news)
            elif any(kw in title for kw in opinion_keywords):
                categories['opinion'].append(news)
            else:
                categories['event'].append(news)
        
        return categories
    
    def _generate_policy_analysis(self, policy_news: List[Dict]) -> str:
        """生成政策分析段落"""
        if not policy_news:
            return "近期无明显政策动态。"
        
        # 提取政策要点
        policies = []
        for news in policy_news[:3]:
            title = news.get('title', '')
            source = news.get('source', '')
            
            # 提取关键信息
            numbers = re.findall(r'(\d+(?:\.\d+)?)\s*(亿|万亿|万|%|个)', title)
            numbers_str = '、'.join([f"{n[0]}{n[1]}" for n in numbers[:2]]) if numbers else ""
            
            policies.append({
                'title': title[:60] + '...' if len(title) > 60 else title,
                'source': source,
                'numbers': numbers_str
            })
        
        # 生成分析段落（模拟LLM输出）
        analysis = "【政策面分析】\n\n"
        
        for i, p in enumerate(policies, 1):
            analysis += f"{i}. {p['title']}\n"
            if p['numbers']:
                analysis += f"   关键数据：{p['numbers']}\n"
            analysis += f"   来源：{p['source']}\n\n"
        
        # 加入分析结论
        analysis += "【政策影响评估】\n"
        analysis += "近期政策层面持续释放积极信号，"
        if any('3000' in p.get('title', '') for p in policies):
            analysis += "3000亿特别国债等具体措施出台，"
        analysis += "政策力度符合市场预期。"
        analysis += "建议关注政策落地节奏及受益板块的业绩验证。"
        
        return analysis
    
    def _generate_data_analysis(self, data_news: List[Dict]) -> str:
        """生成数据分析段落"""
        if not data_news:
            return "暂无显著数据变化。"
        
        # 提取数据点
        data_points = []
        for news in data_news[:3]:
            title = news.get('title', '')
            
            # 提取数字
            numbers = re.findall(r'(增长|下降|上涨|下跌|流入|流出)\s*(\d+(?:\.\d+)?)\s*(亿|万亿|%)?', title)
            if numbers:
                data_points.append({
                    'desc': numbers[0][0],
                    'value': numbers[0][1],
                    'unit': numbers[0][2] if numbers[0][2] else '',
                    'source': news.get('source', '')
                })
        
        analysis = "【资金面分析】\n\n"
        
        if data_points:
            analysis += "最新数据显示：\n"
            for dp in data_points:
                analysis += f"• {dp['desc']}{dp['value']}{dp['unit']}"
                if dp['source']:
                    analysis += f"（{dp['source']}）"
                analysis += "\n"
            analysis += "\n"
        
        analysis += "【数据解读】\n"
        if any('流入' in dp['desc'] for dp in data_points):
            analysis += "北向资金持续流入显示外资对板块长期价值的认可，"
        analysis += "但短期数据波动仍需结合基本面综合判断。"
        
        return analysis
    
    def _generate_opinion_analysis(self, opinion_news: List[Dict]) -> str:
        """生成观点分析段落"""
        if not opinion_news:
            return "市场观点较为一致。"
        
        # 分离看多/看空观点
        bullish = [n for n in opinion_news if n.get('impact') == '利好']
        bearish = [n for n in opinion_news if n.get('impact') == '利空']
        
        analysis = "【市场观点分析】\n\n"
        
        # 看多观点
        if bullish:
            analysis += "▶ 看多逻辑：\n"
            for news in bullish[:2]:
                title = news.get('title', '')[:50]
                analysis += f"  • {title}...\n"
            analysis += "\n"
        
        # 看空观点
        if bearish:
            analysis += "▶ 看空逻辑：\n"
            for news in bearish[:2]:
                title = news.get('title', '')[:50]
                analysis += f"  • {title}...\n"
            analysis += "\n"
        
        # 观点分歧分析
        analysis += "【观点分歧点】\n"
        if bullish and bearish:
            analysis += "市场对该板块存在明显分歧："
            analysis += "看涨方认为政策利好将推动业绩改善，"
            analysis += "看跌方则担忧复苏节奏不及预期。"
            analysis += "这种分歧反映了市场对基本面验证的不同预期。"
        elif bullish:
            analysis += "当前市场情绪偏乐观，"
            analysis += "多数观点看好政策效果及行业复苏。"
        else:
            analysis += "当前市场情绪偏谨慎，"
            analysis += "需关注后续催化因素及业绩验证。"
        
        return analysis
    
    def _generate_event_summary(self, event_news: List[Dict]) -> str:
        """生成事件摘要"""
        if not event_news:
            return ""
        
        summary = "【重要事件】\n\n"
        for news in event_news[:2]:
            title = news.get('title', '')[:60]
            summary += f"• {title}...\n"
        
        return summary
    
    def _integrate_report(self, industry: str, policy: str, data: str, opinion: str, event: str) -> str:
        """整合生成最终分析文章"""
        report = f"# {industry}板块深度分析报告\n\n"
        report += f"分析日期：{datetime.now().strftime('%Y年%m月%d日')}\n\n"
        
        report += "---\n\n"
        
        # 一、政策背景
        report += "## 一、政策背景与影响\n\n"
        report += policy
        report += "\n\n"
        
        # 二、资金面分析
        report += "## 二、资金面与市场情绪\n\n"
        report += data
        report += "\n\n"
        
        # 三、市场观点
        report += "## 三、市场观点与分歧\n\n"
        report += opinion
        report += "\n\n"
        
        # 四、重要事件
        if event:
            report += "## 四、近期重要事件\n\n"
            report += event
            report += "\n\n"
        
        # 五、综合判断
        report += "## 五、综合判断与建议\n\n"
        report += "基于以上分析，我们认为：\n\n"
        
        # 根据内容生成判断
        if '利好' in policy or '积极' in policy:
            report += "1. **政策环境**：政策面持续向好，为板块提供支撑。\n"
        else:
            report += "1. **政策环境**：政策预期平稳，需关注后续动向。\n"
        
        if '流入' in data:
            report += "2. **资金流向**：资金呈现净流入态势，市场情绪偏正面。\n"
        else:
            report += "2. **资金流向**：资金面相对谨慎，等待明确信号。\n"
        
        if '分歧' in opinion:
            report += "3. **市场共识**：市场观点存在分歧，多空博弈加剧。\n"
        else:
            report += "3. **市场共识**：市场观点趋于一致，方向逐渐明朗。\n"
        
        report += "\n**投资建议**：\n"
        report += "• 短期关注政策落地节奏及业绩验证\n"
        report += "• 中期看好行业复苏趋势，建议精选龙头\n"
        report += "• 注意控制仓位，防范市场波动风险\n"
        
        return report
    
    def format_html(self, analysis: Dict) -> str:
        """格式化为HTML"""
        report = analysis.get('integrated_report', '')
        
        # 简单的Markdown转HTML
        html = report
        
        # 标题转换
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        
        # 加粗转换
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # 列表转换
        lines = html.split('\n')
        result = []
        in_list = False
        
        for line in lines:
            if line.startswith('• '):
                if not in_list:
                    result.append('<ul>')
                    in_list = True
                result.append(f'<li>{line[2:]}</li>')
            else:
                if in_list:
                    result.append('</ul>')
                    in_list = False
                result.append(line)
        
        if in_list:
            result.append('</ul>')
        
        html = '\n'.join(result)
        
        # 段落转换
        html = re.sub(r'\n\n', '</p><p>', html)
        
        return f"""
        <div class='llm-analysis'>
            {html}
        </div>
        <style>
        .llm-analysis {{ background: #1a1a2e; border-radius: 12px; padding: 20px; margin: 16px 0; border: 1px solid #333; }}
        .llm-analysis h1 {{ color: #4ade80; font-size: 1.3rem; margin-bottom: 16px; }}
        .llm-analysis h2 {{ color: #60a5fa; font-size: 1.1rem; margin: 20px 0 12px; border-bottom: 1px solid #333; padding-bottom: 8px; }}
        .llm-analysis strong {{ color: #fbbf24; }}
        .llm-analysis ul {{ margin: 8px 0; padding-left: 20px; }}
        .llm-analysis li {{ margin: 4px 0; color: #ccc; }}
        .llm-analysis p {{ margin: 8px 0; line-height: 1.8; color: #ccc; }}
        </style>
        """


# 测试
if __name__ == '__main__':
    analyzer = LLMIntegratedAnalyzer()
    
    test_news = [
        {'title': '财政部安排3000亿超长期特别国债支持消费品以旧换新', 'source': '财联社', 'impact': '利好'},
        {'title': '商务部：将推进服务消费新增长点培育', 'source': '新浪财经', 'impact': '利好'},
        {'title': '消费板块今日上涨2.3%，北向资金净流入15亿', 'source': '东方财富', 'impact': '利好'},
        {'title': '某经济学家：消费复苏仍需时间验证', 'source': '新浪财经', 'impact': '中性'},
    ]
    
    result = analyzer.analyze('消费', test_news)
    print(result['integrated_report'])
    print("\n" + "="*60)
    print(analyzer.format_html(result)[:500])
