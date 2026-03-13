#!/usr/bin/env python3
"""
专业分析报告生成器
生成完整的分析文章（不是罗列）
"""

import re
from typing import Dict, List
from datetime import datetime

class ProfessionalReportGenerator:
    """生成专业分析文章"""
    
    def generate(self, industry: str, news_list: List[Dict]) -> Dict:
        """生成完整分析报告"""
        if not news_list:
            return {"error": "无新闻数据"}
        
        # 分析新闻
        policy_news = [n for n in news_list if self._is_policy(n)]
        data_news = [n for n in news_list if self._is_data(n)]
        opinion_news = [n for n in news_list if self._is_opinion(n)]
        
        # 生成各部分
        introduction = self._generate_introduction(industry, news_list)
        policy_section = self._generate_policy_section(policy_news)
        data_section = self._generate_data_section(data_news)
        opinion_section = self._generate_opinion_section(opinion_news)
        conclusion = self._generate_conclusion(industry, policy_news, data_news, opinion_news)
        
        # 生成参考文献
        references = self._generate_references(news_list)
        
        # 组装完整文章
        full_report = f"""# {industry}板块投资分析报告

**分析日期：{datetime.now().strftime('%Y年%m月%d日')}**

---

{introduction}

## 一、政策环境分析

{policy_section}

## 二、资金面与情绪

{data_section}

## 三、市场观点综述

{opinion_section}

## 四、综合判断

{conclusion}

---

## 参考资料

{references}
"""
        
        return {
            'industry': industry,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'full_report': full_report,
            'sections': {
                'introduction': introduction,
                'policy': policy_section,
                'data': data_section,
                'opinion': opinion_section,
                'conclusion': conclusion,
                'references': references
            }
        }
    
    def _is_policy(self, news: Dict) -> bool:
        """判断是否为政策新闻"""
        title = news.get('title', '')
        keywords = ['政策', '两会', '国务院', '财政部', '发改委', '规划', '补贴', '专项']
        return any(kw in title for kw in keywords)
    
    def _is_data(self, news: Dict) -> bool:
        """判断是否为数据新闻"""
        title = news.get('title', '')
        keywords = ['亿元', '万亿', '增长', '下降', '上涨', '下跌', '流入', '流出', '%']
        return any(kw in title for kw in keywords)
    
    def _is_opinion(self, news: Dict) -> bool:
        """判断是否为观点新闻"""
        title = news.get('title', '')
        keywords = ['看好', '看空', '认为', '表示', '预计', '观点', '研报']
        return any(kw in title for kw in keywords)
    
    def _generate_introduction(self, industry: str, news_list: List[Dict]) -> str:
        """生成引言"""
        # 统计
        policy_count = sum(1 for n in news_list if self._is_policy(n))
        data_count = sum(1 for n in news_list if self._is_data(n))
        
        intro = f"近期{industry}板块受到市场关注。"
        
        if policy_count > 0:
            intro += f"政策层面，{'、'.join([n.get('title', '')[:15] for n in news_list if self._is_policy(n)][:2])}等政策措施陆续出台，"
        
        if data_count > 0:
            intro += "资金面和情绪面呈现分化态势。"
        
        intro += f"本报告从政策环境、资金面、市场情绪等维度进行综合分析，为投资者提供参考。"
        
        return intro
    
    def _generate_policy_section(self, policy_news: List[Dict]) -> str:
        """生成政策分析段落"""
        if not policy_news:
            return "近期政策面相对平稳，无明显重大政策出台。"
        
        section = ""
        
        # 第一段：概述政策动态（使用自然引用，而非编号）
        section += "近期政策层面持续释放积极信号。"
        
        # 提取政策要点，自然融入正文
        policy_highlights = []
        for news in policy_news[:2]:
            title = news.get('title', '')
            source = news.get('source', '')
            # 提取核心内容
            core = title.split('丨')[0] if '丨' in title else title[:30]
            if source:
                policy_highlights.append(f"据{source}报道，{core}")
            else:
                policy_highlights.append(core)
        
        if policy_highlights:
            section += f"{'；'.join(policy_highlights)}。"
        
        section += "\n\n"
        
        # 第二段：政策影响分析
        section += "从政策影响来看："
        section += "一是政策导向明确，体现了对行业发展的支持态度；"
        section += "二是具体措施具有可操作性，有助于改善行业基本面；"
        section += "三是政策效果有待观察，建议关注后续落地进展。"
        
        section += "\n\n"
        
        # 第三段：政策建议
        section += "总体而言，政策环境对板块形成支撑，但投资者需关注政策落地的时滞效应，以及实际执行中可能面临的挑战。"
        
        return section
    
    def _generate_data_section(self, data_news: List[Dict]) -> str:
        """生成数据分析段落"""
        if not data_news:
            return "近期资金面数据相对平稳，无显著异常波动。"
        
        section = ""
        
        # 提取关键数据并自然引用
        data_mentions = []
        for news in data_news[:2]:
            title = news.get('title', '')
            source = news.get('source', '')
            # 提取数字
            nums = re.findall(r'(\d+(?:\.\d+)?)\s*(亿|万亿|%?)', title)
            if nums and source:
                data_mentions.append(f"{source}数据显示{nums[0][0]}{nums[0][1]}")
            elif nums:
                data_mentions.append(f"数据显示{nums[0][0]}{nums[0][1]}")
        
        # 第一段：数据概述
        section += "从资金面数据来看："
        if data_mentions:
            section += f"{'；'.join(data_mentions)}。"
        section += "\n\n"
        
        # 第二段：资金流向分析
        bullish = sum(1 for n in data_news if '流入' in n.get('title', '') or '增长' in n.get('title', ''))
        bearish = sum(1 for n in data_news if '流出' in n.get('title', '') or '下降' in n.get('title', ''))
        
        if bullish > bearish:
            section += "资金流向整体呈现净流入态势，显示市场对该板块的关注度有所提升。"
        elif bearish > bullish:
            section += "资金流向呈现净流出态势，反映市场短期情绪偏谨慎。"
        else:
            section += "资金流向相对均衡，多空双方博弈加剧。"
        
        section += "\n\n"
        
        # 第三段：情绪判断
        section += "市场情绪方面，投资者对该板块的预期出现分化。"
        section += "部分投资者看好政策利好带来的业绩改善，也有投资者担忧复苏节奏不及预期。"
        section += "建议关注后续资金动向和成交量变化。"
        
        return section
    
    def _generate_opinion_section(self, opinion_news: List[Dict]) -> str:
        """生成观点分析段落"""
        if not opinion_news:
            return "近期市场观点较为一致，无显著分歧。"
        
        section = ""
        
        # 分离观点
        bullish = [n for n in opinion_news if n.get('impact') == '利好']
        bearish = [n for n in opinion_news if n.get('impact') == '利空']
        
        # 第一段：观点概述
        section += "从市场各方观点来看："
        
        if bullish:
            # 获取来源和核心观点
            b_news = bullish[0]
            source = b_news.get('source', '市场')
            title = b_news.get('title', '')[:25]
            section += f"{source}等机构持乐观态度，认为{title}..."
            section += "主要逻辑是政策利好将推动行业景气度回升。"
        
        section += "\n\n"
        
        if bearish:
            s_news = bearish[0]
            source = s_news.get('source', '部分分析师')
            title = s_news.get('title', '')[:25]
            section += f"而{source}则相对谨慎，指出{title}..."
            section += "担忧经济复苏节奏和实际需求释放。"
        
        section += "\n\n"
        
        # 第二段：分歧分析
        if bullish and bearish:
            section += "当前市场观点存在明显分歧，这种分歧反映了投资者对基本面判断的差异。"
            section += "建议投资者在关注政策利好的同时，也要警惕业绩不及预期的风险。"
        elif bullish:
            section += "当前市场观点偏向乐观，多数机构看好板块中长期发展。"
        else:
            section += "当前市场观点偏向谨慎，建议等待更明确的催化剂。"
        
        return section
    
    def _generate_conclusion(self, industry: str, policy_news: List[Dict], 
                            data_news: List[Dict], opinion_news: List[Dict]) -> str:
        """生成结论"""
        conclusion = ""
        
        # 综合判断
        policy_score = min(5, len(policy_news)) if policy_news else 2
        
        conclusion += f"综合来看，{industry}板块当前处于"
        
        if policy_score >= 3:
            conclusion += "政策利好与业绩验证的博弈阶段。"
        else:
            conclusion += "等待催化剂的震荡整理阶段。"
        
        conclusion += "\n\n"
        
        conclusion += "**投资建议**：\n\n"
        
        if policy_score >= 3:
            conclusion += "1. 短期：关注政策落地节奏，精选直接受益标的\n"
            conclusion += "2. 中期：看好行业复苏趋势，建议逢低布局龙头\n"
            conclusion += "3. 风险：防范业绩不及预期和市场情绪波动\n"
        else:
            conclusion += "1. 短期：保持观望，等待明确信号\n"
            conclusion += "2. 中期：关注基本面改善信号，精选优质标的\n"
            conclusion += "3. 风险：控制仓位，防范系统性风险\n"
        
        conclusion += "\n"
        conclusion += "**风险提示**：政策落地不及预期、宏观经济下行、行业竞争加剧等。"
        
        return conclusion
    
    def _generate_references(self, news_list: List[Dict]) -> str:
        """生成参考文献"""
        refs = []
        for i, news in enumerate(news_list[:8], 1):
            title = news.get('title', '')[:60] + '...' if len(news.get('title', '')) > 60 else news.get('title', '')
            source = news.get('source', '未知')
            refs.append(f"[{i}] {title} 来源：{source}")
        
        return '\n'.join(refs)
    
    def format_html(self, report: Dict) -> str:
        """格式化为HTML"""
        full_report = report.get('full_report', '')
        
        # Markdown转HTML
        html = full_report
        
        # 标题
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        
        # 加粗
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # 列表
        lines = html.split('\n')
        result = []
        in_list = False
        
        for line in lines:
            if line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. '):
                if not in_list:
                    result.append('<ol>')
                    in_list = True
                result.append(f'<li>{line[3:]}</li>')
            else:
                if in_list:
                    result.append('</ol>')
                    in_list = False
                result.append(line)
        
        if in_list:
            result.append('</ol>')
        
        html = '\n'.join(result)
        
        # 参考文献
        html = html.replace('## 参考资料', '<h2>参考资料</h2>')
        
        # 段落
        html = re.sub(r'\n\n', '</p><p>', html)
        
        css = '.professional-report { background: #1a1a2e; border-radius: 12px; padding: 24px; margin: 16px 0; border: 1px solid #333; } .professional-report h1 { color: #4ade80; font-size: 1.4rem; margin-bottom: 16px; text-align: center; } .professional-report h2 { color: #60a5fa; font-size: 1.1rem; margin: 20px 0 12px; border-bottom: 1px solid #333; padding-bottom: 8px; } .professional-report strong { color: #fbbf24; } .professional-report ol { margin: 12px 0; padding-left: 24px; color: #ccc; } .professional-report li { margin: 8px 0; line-height: 1.6; } .professional-report p { margin: 12px 0; line-height: 1.8; color: #ccc; text-indent: 2em; }'
        
        return f"""
        <div class='professional-report'>
            {html}
        </div>
        <style>{css}</style>
        """


if __name__ == '__main__':
    generator = ProfessionalReportGenerator()
    
    test_news = [
        {'title': '财政部安排3000亿超长期特别国债支持消费品以旧换新', 'source': '财联社', 'impact': '利好'},
        {'title': '商务部：将推进服务消费新增长点培育', 'source': '新浪财经', 'impact': '利好'},
        {'title': '消费板块今日上涨2.3%，北向资金净流入15亿', 'source': '东方财富', 'impact': '利好'},
        {'title': '某经济学家：消费复苏仍需时间验证', 'source': '新浪财经', 'impact': '中性'},
    ]
    
    result = generator.generate('消费', test_news)
    print(result['full_report'])
