#!/usr/bin/env python3
"""
PEST-M 行业分析方法论框架
- Policy（政策）
- Economy（经济）
- Sentiment（情绪）
- Technology（技术）
- Market（市场）

输出有理有据的行业分析
"""

import json
import re
from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path

class PESTMFramework:
    """PEST-M 五维分析框架"""
    
    # 关键词词典
    POLICY_KEYWORDS = ['政策', '政府', '两会', '国务院', '工信部', '发改委', '补贴', '专项', '规划', '纲要']
    ECONOMY_KEYWORDS = ['经济', 'GDP', '增长', '复苏', '景气', '需求', '供给', '通胀', '利率']
    SENTIMENT_KEYWORDS = ['情绪', '资金', '流入', '流出', '看好', '看空', '增持', '减持', '热度']
    TECH_KEYWORDS = ['技术', '突破', '创新', '专利', '研发', '产品', '迭代', '升级', '国产']
    MARKET_KEYWORDS = ['市场', '竞争', '格局', '龙头', '份额', '订单', '价格', '供需', '产能']
    
    def __init__(self):
        self.evidence_log = []  # 证据日志
    
    def analyze(self, industry: str, news_list: List[Dict], market_data: Dict) -> Dict:
        """
        执行PEST-M五维分析
        
        Returns:
            {
                'dimensions': {
                    'policy': {'score': 4, 'facts': [...], 'sources': [...]},
                    'economy': {...},
                    'sentiment': {...},
                    'technology': {...},
                    'market': {...}
                },
                'overall_score': 4.2,
                'overall_rating': '谨慎乐观',
                'conflicts': [...],  # 观点分歧
                'conclusion': '综合分析结论'
            }
        """
        result = {
            'industry': industry,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'dimensions': {}
        }
        
        # 五个维度分析
        result['dimensions']['policy'] = self._analyze_policy(news_list)
        result['dimensions']['economy'] = self._analyze_economy(news_list, market_data)
        result['dimensions']['sentiment'] = self._analyze_sentiment(news_list, market_data)
        result['dimensions']['technology'] = self._analyze_technology(news_list)
        result['dimensions']['market'] = self._analyze_market(news_list, market_data)
        
        # 计算综合评分
        scores = [d['score'] for d in result['dimensions'].values()]
        result['overall_score'] = round(sum(scores) / len(scores), 1)
        result['overall_rating'] = self._get_rating(result['overall_score'])
        
        # 识别观点分歧
        result['conflicts'] = self._identify_conflicts(news_list)
        
        # 生成综合结论
        result['conclusion'] = self._generate_conclusion(result)
        
        return result
    
    def _analyze_policy(self, news_list: List[Dict]) -> Dict:
        """P-政策维度分析"""
        facts = []
        sources = []
        score = 3  # 基础分
        
        for news in news_list:
            title = news.get('title', '')
            
            # 提取政策事实
            if any(kw in title for kw in self.POLICY_KEYWORDS):
                # 提取具体政策内容
                policy_match = re.search(r'([^。]*?(?:出台|发布|实施|推进|加强)[^。]{10,60})', title)
                if policy_match:
                    facts.append({
                        'content': policy_match.group(1),
                        'source': news.get('source', '未知'),
                        'impact': news.get('impact', '中性')
                    })
                    sources.append(news.get('source'))
                    
                    # 评分调整
                    if '利好' in title or '支持' in title:
                        score += 0.5
                    elif '监管' in title or '限制' in title:
                        score -= 0.5
        
        # 去重
        facts = self._dedup_facts(facts)
        
        return {
            'score': min(5, max(1, round(score))),
            'facts': facts[:3],  # 最多3条
            'sources': list(set(sources))[:2]
        }
    
    def _analyze_economy(self, news_list: List[Dict], market_data: Dict) -> Dict:
        """E-经济维度分析"""
        facts = []
        sources = []
        score = 3
        
        # 从行情数据提取
        change_pct = market_data.get('change_pct', 0)
        if change_pct > 3:
            facts.append({
                'content': f'板块今日上涨{change_pct:.2f}%，表现强势',
                'source': '行情数据',
                'impact': '利好'
            })
            score += 1
        elif change_pct < -3:
            facts.append({
                'content': f'板块今日下跌{abs(change_pct):.2f}%，承压明显',
                'source': '行情数据',
                'impact': '利空'
            })
            score -= 1
        
        # 从新闻提取经济数据
        for news in news_list:
            title = news.get('title', '')
            # 提取经济数据
            numbers = re.findall(r'(增长|下降|上涨|下跌)\s*(\d+(?:\.\d+)?)\s*%', title)
            if numbers:
                facts.append({
                    'content': f"{numbers[0][0]}{numbers[0][1]}%",
                    'source': news.get('source'),
                    'impact': '利好' if numbers[0][0] in ['增长', '上涨'] else '利空'
                })
        
        return {
            'score': min(5, max(1, round(score))),
            'facts': facts[:3],
            'sources': list(set(sources))[:2]
        }
    
    def _analyze_sentiment(self, news_list: List[Dict], market_data: Dict) -> Dict:
        """S-情绪维度分析"""
        facts = []
        sources = []
        score = 3
        
        # 统计舆情
        positive = sum(1 for n in news_list if n.get('impact') == '利好')
        negative = sum(1 for n in news_list if n.get('impact') == '利空')
        total = len(news_list)
        
        if total > 0:
            sentiment_ratio = positive / total
            if sentiment_ratio > 0.6:
                facts.append({
                    'content': f'舆情偏正面，利好新闻占比{sentiment_ratio*100:.0f}%',
                    'source': '舆情统计',
                    'impact': '利好'
                })
                score += 1
            elif sentiment_ratio < 0.4:
                facts.append({
                    'content': f'舆情偏负面，利空新闻占比{(1-sentiment_ratio)*100:.0f}%',
                    'source': '舆情统计',
                    'impact': '利空'
                })
                score -= 1
        
        # 提取资金相关
        for news in news_list:
            title = news.get('title', '')
            if '资金' in title or '流入' in title or '流出' in title:
                facts.append({
                    'content': title[:50] + '...',
                    'source': news.get('source'),
                    'impact': news.get('impact', '中性')
                })
        
        return {
            'score': min(5, max(1, round(score))),
            'facts': facts[:3],
            'sources': list(set(sources))[:2]
        }
    
    def _analyze_technology(self, news_list: List[Dict]) -> Dict:
        """T-技术维度分析"""
        facts = []
        sources = []
        score = 3
        
        for news in news_list:
            title = news.get('title', '')
            if any(kw in title for kw in self.TECH_KEYWORDS):
                # 提取技术突破信息
                tech_match = re.search(r'([^。]*?(?:突破|发布|推出|研发)[^。]{10,50})', title)
                if tech_match:
                    facts.append({
                        'content': tech_match.group(1),
                        'source': news.get('source'),
                        'impact': news.get('impact', '中性')
                    })
                    sources.append(news.get('source'))
                    if news.get('impact') == '利好':
                        score += 0.5
        
        return {
            'score': min(5, max(1, round(score))),
            'facts': facts[:3],
            'sources': list(set(sources))[:2]
        }
    
    def _analyze_market(self, news_list: List[Dict], market_data: Dict) -> Dict:
        """M-市场维度分析"""
        facts = []
        sources = []
        score = 3
        
        # 提取市场相关新闻
        for news in news_list:
            title = news.get('title', '')
            if any(kw in title for kw in self.MARKET_KEYWORDS):
                facts.append({
                    'content': title[:60] + '...',
                    'source': news.get('source'),
                    'impact': news.get('impact', '中性')
                })
                sources.append(news.get('source'))
        
        return {
            'score': min(5, max(1, round(score))),
            'facts': facts[:3],
            'sources': list(set(sources))[:2]
        }
    
    def _identify_conflicts(self, news_list: List[Dict]) -> List[Dict]:
        """识别观点分歧"""
        conflicts = []
        
        # 按主题分组
        bullish = [n for n in news_list if n.get('impact') == '利好']
        bearish = [n for n in news_list if n.get('impact') == '利空']
        
        if bullish and bearish:
            conflicts.append({
                'type': '多空分歧',
                'bullish_view': bullish[0].get('title', '看好')[:50] if bullish else '',
                'bearish_view': bearish[0].get('title', '看空')[:50] if bearish else '',
                'bullish_source': bullish[0].get('source') if bullish else '',
                'bearish_source': bearish[0].get('source') if bearish else ''
            })
        
        return conflicts
    
    def _generate_conclusion(self, result: Dict) -> str:
        """生成综合结论"""
        score = result['overall_score']
        dimensions = result['dimensions']
        
        # 找出最强和最弱维度
        scores = {k: v['score'] for k, v in dimensions.items()}
        strongest = max(scores, key=scores.get)
        weakest = min(scores, key=scores.get)
        
        if score >= 4:
            return f"综合评分{score}/5，行业整体向好。{strongest}维度表现最佳，{weakest}维度需关注。"
        elif score >= 3:
            return f"综合评分{score}/5，行业中性偏谨慎。{strongest}有支撑，{weakest}存压力。"
        else:
            return f"综合评分{score}/5，行业面临挑战。{weakest}维度风险较大，需警惕。"
    
    def _get_rating(self, score: float) -> str:
        """获取评级描述"""
        if score >= 4.5:
            return '非常乐观'
        elif score >= 4:
            return '谨慎乐观'
        elif score >= 3.5:
            return '中性偏乐观'
        elif score >= 3:
            return '中性偏谨慎'
        elif score >= 2.5:
            return '谨慎'
        else:
            return '悲观'
    
    def _dedup_facts(self, facts: List[Dict]) -> List[Dict]:
        """事实去重"""
        seen = set()
        result = []
        for fact in facts:
            key = fact['content'][:30]
            if key not in seen:
                seen.add(key)
                result.append(fact)
        return result
    
    def format_report(self, analysis: Dict) -> str:
        """格式化输出报告"""
        lines = []
        lines.append(f"📊 {analysis['industry']}板块 PEST-M 综合分析")
        lines.append(f"分析日期：{analysis['date']}")
        lines.append("")
        
        # 五维分析
        dim_names = {
            'policy': 'P-政策',
            'economy': 'E-经济', 
            'sentiment': 'S-情绪',
            'technology': 'T-技术',
            'market': 'M-市场'
        }
        
        for key, name in dim_names.items():
            dim = analysis['dimensions'][key]
            stars = '⭐' * dim['score']
            lines.append(f"{name}：{stars} ({dim['score']}/5)")
            for fact in dim['facts']:
                impact_emoji = {'利好': '🟢', '利空': '🔴', '中性': '⚪'}.get(fact['impact'], '⚪')
                lines.append(f"  {impact_emoji} {fact['content']}")
                lines.append(f"     来源：{fact['source']}")
            lines.append("")
        
        # 观点分歧
        if analysis['conflicts']:
            lines.append("【观点分歧】")
            for conflict in analysis['conflicts']:
                lines.append(f"  {conflict['type']}：")
                lines.append(f"    看涨方：{conflict['bullish_view']}...")
                lines.append(f"    看跌方：{conflict['bearish_view']}...")
            lines.append("")
        
        # 综合结论
        lines.append("【综合结论】")
        lines.append(f"  综合评分：{analysis['overall_score']}/5 ({analysis['overall_rating']})")
        lines.append(f"  {analysis['conclusion']}")
        
        return '\n'.join(lines)


# 测试
if __name__ == '__main__':
    framework = PESTMFramework()
    
    # 模拟数据
    test_news = [
        {'title': '财政部安排3000亿超长期特别国债支持消费品以旧换新', 'source': '财联社', 'impact': '利好'},
        {'title': '商务部：将推进服务消费新增长点培育', 'source': '新浪财经', 'impact': '利好'},
        {'title': '消费板块今日上涨2.3%，北向资金净流入15亿', 'source': '东方财富', 'impact': '利好'},
        {'title': '某经济学家：消费复苏仍需时间验证', 'source': '新浪财经', 'impact': '中性'},
    ]
    test_market = {'change_pct': 2.3}
    
    result = framework.analyze('消费', test_news, test_market)
    print(framework.format_report(result))
