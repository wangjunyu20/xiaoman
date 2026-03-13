#!/usr/bin/env python3
"""
详细分析报告生成器
在综述基础上，展开政策和观点的详细分析
"""

import re
from typing import Dict, List
from datetime import datetime

class DetailedAnalysisGenerator:
    """生成有理有据的详细分析报告"""
    
    def generate(self, industry: str, news_list: List[Dict], pestm_result: Dict, causal_analysis: str) -> str:
        """
        生成详细分析报告
        
        结构：
        一、政策背景详析（展开政策细节）
        二、市场观点详析（对比不同机构观点）
        三、数据验证（支撑观点的数据）
        四、综合分析与结论
        """
        sections = []
        
        # 一、政策背景详析
        policy_section = self._generate_policy_section(news_list)
        if policy_section:
            sections.append(policy_section)
        
        # 二、市场观点详析
        opinion_section = self._generate_opinion_section(news_list)
        if opinion_section:
            sections.append(opinion_section)
        
        # 三、数据验证
        data_section = self._generate_data_section(news_list, pestm_result)
        if data_section:
            sections.append(data_section)
        
        # 四、综合分析
        conclusion_section = self._generate_conclusion_section(pestm_result, causal_analysis)
        sections.append(conclusion_section)
        
        return '\n\n'.join(sections)
    
    def _generate_policy_section(self, news_list: List[Dict]) -> str:
        """生成政策背景详析"""
        policy_news = []
        
        for news in news_list:
            title = news.get('title', '')
            if any(kw in title for kw in ['政策', '两会', '国务院', '财政部', '发改委', '工信部', '补贴', '规划']):
                policy_news.append(news)
        
        if not policy_news:
            return ""
        
        lines = ["【一、政策背景详析】"]
        lines.append("")
        
        for i, news in enumerate(policy_news[:3], 1):
            title = news.get('title', '')
            source = news.get('source', '')
            
            # 提取政策要点
            lines.append(f"{i}. {title}")
            lines.append(f"   来源：{source}")
            
            # 提取具体数字（金额、比例等）
            numbers = re.findall(r'(\d+(?:\.\d+)?)\s*(亿|万亿|万|%|个)', title)
            if numbers:
                lines.append(f"   关键数据：{', '.join([f'{n[0]}{n[1]}' for n in numbers[:2]])}")
            
            lines.append("")
        
        # 政策影响总结
        lines.append("【政策影响评估】")
        lines.append("• 政策力度：根据具体金额和覆盖面评估")
        lines.append("• 落地进度：关注后续配套措施出台时间")
        lines.append("• 受益程度：直接受益板块与间接受益板块区分")
        lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_opinion_section(self, news_list: List[Dict]) -> str:
        """生成市场观点详析"""
        # 分离看涨和看跌观点
        bullish = []
        bearish = []
        neutral = []
        
        for news in news_list:
            impact = news.get('impact', '中性')
            if impact == '利好':
                bullish.append(news)
            elif impact == '利空':
                bearish.append(news)
            else:
                neutral.append(news)
        
        lines = ["【二、市场观点详析】"]
        lines.append("")
        
        # 看涨观点
        if bullish:
            lines.append("▶ 看涨方观点：")
            for i, news in enumerate(bullish[:2], 1):
                title = news.get('title', '')[:60]
                source = news.get('source', '')
                lines.append(f"  {i}. {title}...")
                lines.append(f"     来源：{source}")
                lines.append("")
        
        # 看跌观点
        if bearish:
            lines.append("▶ 看跌方观点：")
            for i, news in enumerate(bearish[:2], 1):
                title = news.get('title', '')[:60]
                source = news.get('source', '')
                lines.append(f"  {i}. {title}...")
                lines.append(f"     来源：{source}")
                lines.append("")
        
        # 观点分歧分析
        lines.append("【观点分歧点】")
        if bullish and bearish:
            lines.append("• 核心分歧：政策效果预期 vs 实际复苏节奏")
            lines.append("• 时间维度：短期谨慎 vs 中期乐观")
        else:
            lines.append("• 当前市场观点较为一致，需关注后续变化")
        lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_data_section(self, news_list: List[Dict], pestm_result: Dict) -> str:
        """生成数据验证部分"""
        lines = ["【三、数据验证】"]
        lines.append("")
        
        # 从PEST-M结果提取数据
        dimensions = pestm_result.get('dimensions', {})
        
        # 情绪维度数据
        sentiment_dim = dimensions.get('sentiment', {})
        if sentiment_dim.get('facts'):
            lines.append("▶ 市场情绪数据：")
            for fact in sentiment_dim['facts'][:2]:
                content = fact.get('content', '')
                source = fact.get('source', '')
                lines.append(f"  • {content}")
                if source:
                    lines.append(f"    来源：{source}")
            lines.append("")
        
        # 经济维度数据
        economy_dim = dimensions.get('economy', {})
        if economy_dim.get('facts'):
            lines.append("▶ 行情数据：")
            for fact in economy_dim['facts'][:2]:
                content = fact.get('content', '')
                lines.append(f"  • {content}")
            lines.append("")
        
        # 从新闻提取数据
        data_points = []
        for news in news_list:
            title = news.get('title', '')
            # 提取金额数据
            money_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(亿|万亿|万元)', title)
            for m in money_matches:
                data_points.append(f"{m[0]}{m[1]}")
        
        if data_points:
            lines.append("▶ 关键数据点：")
            for dp in data_points[:3]:
                lines.append(f"  • {dp}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_conclusion_section(self, pestm_result: Dict, causal_analysis: str) -> str:
        """生成综合分析与结论"""
        lines = ["【四、综合分析与结论】"]
        lines.append("")
        
        # PEST-M评分总结
        overall_score = pestm_result.get('overall_score', 0)
        overall_rating = pestm_result.get('overall_rating', '')
        
        lines.append(f"综合评分：{overall_score}/5（{overall_rating}）")
        lines.append("")
        
        # 各维度简评
        dimensions = pestm_result.get('dimensions', {})
        dim_names = {
            'policy': '政策',
            'economy': '经济',
            'sentiment': '情绪',
            'technology': '技术',
            'market': '市场'
        }
        
        lines.append("各维度评估：")
        for key, name in dim_names.items():
            dim = dimensions.get(key, {})
            score = dim.get('score', 3)
            stars = '⭐' * score
            lines.append(f"  • {name}：{stars} ({score}/5)")
        lines.append("")
        
        # 因果推导总结
        lines.append("【逻辑推导总结】")
        lines.append(causal_analysis.split('【多步因果推导】')[-1].strip() if '【多步因果推导】' in causal_analysis else causal_analysis[:500])
        lines.append("")
        
        # 投资建议
        lines.append("【投资建议】")
        if overall_score >= 4:
            lines.append("• 建议：积极关注，把握配置机会")
            lines.append("• 关注：政策落地节奏、龙头业绩")
        elif overall_score >= 3:
            lines.append("• 建议：谨慎乐观，精选个股")
            lines.append("• 关注：估值合理性、业绩验证")
        else:
            lines.append("• 建议：保持观望，控制风险")
            lines.append("• 关注：基本面改善信号")
        lines.append("")
        
        # 风险提示
        lines.append("【风险提示】")
        lines.append("• 政策落地不及预期风险")
        lines.append("• 市场系统性风险")
        lines.append("• 行业竞争加剧风险")
        
        return '\n'.join(lines)


# 测试
if __name__ == '__main__':
    generator = DetailedAnalysisGenerator()
    
    # 模拟数据
    test_news = [
        {'title': '财政部安排3000亿超长期特别国债支持消费品以旧换新', 'source': '财联社', 'impact': '利好'},
        {'title': '商务部：将推进服务消费新增长点培育', 'source': '新浪财经', 'impact': '利好'},
        {'title': '消费板块今日上涨2.3%，北向资金净流入15亿', 'source': '东方财富', 'impact': '利好'},
    ]
    test_pestm = {
        'overall_score': 4.2,
        'overall_rating': '谨慎乐观',
        'dimensions': {
            'policy': {'score': 5, 'facts': [{'content': '3000亿国债政策出台', 'source': '财联社'}]},
            'economy': {'score': 4, 'facts': [{'content': '板块上涨2.3%'}]},
            'sentiment': {'score': 4, 'facts': [{'content': '资金净流入15亿'}]},
            'technology': {'score': 3, 'facts': []},
            'market': {'score': 4, 'facts': []}
        }
    }
    test_causal = "【多步因果推导】\n第一步：政策出台\n第二步：机构解读\n第三步：资金流入\n第四步：股价上涨"
    
    result = generator.generate('消费', test_news, test_pestm, test_causal)
    print(result)
