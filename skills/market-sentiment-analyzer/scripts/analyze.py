#!/usr/bin/env python3
"""
行业行情与舆情分析器
采集行情走势，分析舆情，推导走势原因
"""

import json
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# 行业代码映射（同花顺板块）
INDUSTRY_CODES = {
    "光模块": "bk1166",
    "人形机器人": "bk1158",
    "量子科技": "bk1150",
    "AI应用": "bk1172",
    "脑机接口": "bk1154",
    "低空经济": "bk1168",
    "集成电路": "bk1152",
    "算力": "bk1160",
    "消费": "bk1162",
    "生物医药": "bk1156",
}

class MarketSentimentAnalyzer:
    """行业行情与舆情分析器"""
    
    def __init__(self):
        self.cache_dir = Path(__file__).parent.parent / "output" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_market_data(self, industry: str, days: int = 7) -> Dict:
        """获取行业行情数据（使用东方财富概念板块）"""
        try:
            import akshare as ak
            import time
            
            # 行业名称映射到同花顺概念板块
            concept_map = {
                "光模块": "CPO概念",
                "CPO": "CPO概念",
                "人形机器人": "人形机器人",
                "机器人": "人形机器人",
                "量子科技": "量子计算",
                "量子": "量子计算",
                "脑机接口": "脑机接口",
                "AI应用": "多模态AI",
                "人工智能": "多模态AI",
                "低空经济": "低空经济",
                "算力": "算力概念",
                "集成电路": "芯片概念",
                "芯片": "芯片概念",
            }
            
            concept_name = concept_map.get(industry, industry)
            
            # 获取概念板块行情（使用stock_board_concept_name_em获取列表）
            try:
                concept_list = ak.stock_board_concept_name_em()
                # 查找匹配的概念
                matched_concept = None
                for _, row in concept_list.iterrows():
                    if concept_name in row['板块名称'] or row['板块名称'] in concept_name:
                        matched_concept = row['板块名称']
                        break
                
                if not matched_concept:
                    matched_concept = concept_name
                
                # 获取历史行情
                board_df = ak.stock_board_concept_hist_em(
                    symbol=matched_concept,
                    period="日k",
                    start_date=(datetime.now() - timedelta(days=days+5)).strftime("%Y%m%d"),
                    end_date=datetime.now().strftime("%Y%m%d"),
                    adjust=""
                )
            except Exception as e:
                # 如果获取失败，尝试直接获取
                time.sleep(1)
                board_df = ak.stock_board_concept_hist_em(
                    symbol=concept_name,
                    period="日k",
                    start_date=(datetime.now() - timedelta(days=days+5)).strftime("%Y%m%d"),
                    end_date=datetime.now().strftime("%Y%m%d"),
                    adjust=""
                )
            
            if board_df is None or board_df.empty:
                return {"error": "无行情数据"}
            
            # 只取最近days天
            board_df = board_df.tail(days)
            
            # 计算涨跌幅
            latest = board_df.iloc[-1]
            prev = board_df.iloc[-2] if len(board_df) > 1 else latest
            
            change_pct = float(latest['涨跌幅']) if '涨跌幅' in latest else 0
            
            # 计算技术指标
            close_prices = pd.to_numeric(board_df['收盘'], errors='coerce').dropna()
            rsi = self._calculate_rsi(close_prices) if len(close_prices) > 14 else 50
            
            # 成交量变化
            volume = int(latest['成交量']) if '成交量' in latest else 0
            prev_volume = int(prev['成交量']) if '成交量' in prev else volume
            volume_change = "放大" if volume > prev_volume * 1.2 else "萎缩" if volume < prev_volume * 0.8 else "持平"
            
            return {
                "latest_close": float(latest['收盘']) if '收盘' in latest else 0,
                "change_pct": round(change_pct, 2),
                "volume": volume,
                "volume_change": volume_change,
                "rsi": round(rsi, 2),
                "trend": "上涨" if change_pct > 0 else "下跌" if change_pct < 0 else "持平",
                "technical_signal": self._technical_interpretation(rsi, change_pct),
                "amplitude": round(float(latest['振幅']), 2) if '振幅' in latest else 0,
                "highest": float(latest['最高']) if '最高' in latest else 0,
                "lowest": float(latest['最低']) if '最低' in latest else 0
            }
        except Exception as e:
            return {"error": f"行情获取失败: {str(e)}"}
    
    def _calculate_rsi(self, prices, period=14) -> float:
        """计算RSI指标"""
        if len(prices) < period:
            return 50.0
        
        deltas = prices.diff().dropna()
        gains = deltas.where(deltas > 0, 0)
        losses = -deltas.where(deltas < 0, 0)
        
        avg_gain = gains.tail(period).mean()
        avg_loss = losses.tail(period).mean()
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _technical_interpretation(self, rsi: float, change_pct: float) -> str:
        """技术指标解读"""
        if rsi > 70:
            return "超买"
        elif rsi < 30:
            return "超卖"
        elif change_pct > 3:
            return "强势"
        elif change_pct < -3:
            return "弱势"
        return "震荡"
    
    def get_sentiment_data(self, industry: str) -> Dict:
        """获取舆情数据 - 使用多源聚合器"""
        # 导入多源新闻聚合器
        try:
            from multi_source_news import MultiSourceNewsAggregator
            aggregator = MultiSourceNewsAggregator()
            
            # 聚合多源新闻
            news = aggregator.aggregate_news(industry, limit_per_source=10)
            
            # 情绪分析
            positive = sum(1 for n in news if n.get('impact') == '利好')
            negative = sum(1 for n in news if n.get('impact') == '利空')
            neutral = len(news) - positive - negative
            
            sentiment_score = (positive - negative) / len(news) * 100 if news else 0
            
            # 提取关键事件
            key_events = self._extract_key_events(news)
            
            return {
                "news_count": len(news),
                "positive": positive,
                "negative": negative,
                "neutral": neutral,
                "sentiment_score": round(sentiment_score, 2),
                "sentiment_label": self._sentiment_label(sentiment_score),
                "key_events": key_events[:5],
                "latest_news": news[:3] if news else []
            }
        except Exception as e:
            return {"error": f"舆情获取失败: {str(e)}"}
    
    def _extract_key_events(self, news_list: List[Dict]) -> List[str]:
        """提取关键事件"""
        events = []
        keywords_map = {
            "中东": "中东局势",
            "战争": "地缘政治",
            "冲突": "地缘政治",
            "财报": "业绩发布",
            "业绩": "业绩发布",
            "政策": "政策影响",
            "监管": "监管动态",
            "加息": "货币政策",
            "降息": "货币政策",
            "净流出": "资金流出",
            "净卖出": "主力出货",
            "跌幅": "板块下跌",
            "CPO": "CPO概念",
            "光模块": "光模块",
        }
        
        for news in news_list:
            title = news.get('title', '')
            for keyword, event_type in keywords_map.items():
                if keyword in title and event_type not in events:
                    events.append(event_type)
        
        return events
    
    def _sentiment_label(self, score: float) -> str:
        """情绪标签"""
        if score > 30:
            return "偏多"
        elif score < -30:
            return "偏空"
        elif score > 10:
            return "略偏多"
        elif score < -10:
            return "略偏空"
        return "中性"
    
    def generate_reasoning(self, market_data: Dict, sentiment_data: Dict, industry: str = "") -> str:
        """生成走势原因分析 - 改进版：基于新闻内容生成个性化分析"""
        
        news_list = sentiment_data.get('latest_news', [])
        sentiment_label = sentiment_data.get('sentiment_label', '中性')
        key_events = sentiment_data.get('key_events', [])
        
        # 行业特定关键词映射
        industry_factors = {
            "芯片": ["国产替代", "制裁", "制程", "产能", "订单"],
            "算力": ["智算中心", "大模型", "算力租赁", "订单", "招标"],
            "AI应用": ["大模型", "Agent", "落地", "商业化", "用户增长"],
            "人形机器人": ["特斯拉", "Optimus", "量产", "零部件", "执行器"],
            "量子科技": ["量子计算", "量子通信", "技术突破", "论文", "专利"],
            "脑机接口": ["Neuralink", "临床试验", "植入", "医疗应用"],
            "低空经济": ["适航证", "eVTOL", "订单", "试飞", "政策"],
            "光模块": ["CPO", "1.6T", "英伟达", "订单", "出货", "业绩"],
            "生物医药": ["创新药", "临床", "FDA", "批准", "管线"],
            "6G": ["标准", "频谱", "太赫兹", "研发", "试验"],
            "卫星互联网": ["星链", "低轨", "组网", "发射", "频谱"],
            "可控核聚变": ["托卡马克", "点火", "能量增益", "实验", "装置"],
            "消费": ["复苏", "促销", "政策", "节假日", "数据"],
            "航空航天": ["订单", "交付", "型号", "列装", "军贸"],
        }
        
        # 从新闻提取具体信息
        factors_found = []
        specific_events = []
        
        for news in news_list:
            title = news.get('title', '')
            # 提取行业特定因素
            for factor in industry_factors.get(industry, []):
                if factor in title and factor not in factors_found:
                    factors_found.append(factor)
            
            # 提取具体事件
            if '涨停' in title:
                specific_events.append("个股涨停带动情绪")
            if '利好' in title or '支持' in title:
                specific_events.append("政策利好")
            if '订单' in title or '中标' in title:
                specific_events.append("大额订单")
            if '突破' in title or '进展' in title:
                specific_events.append("技术突破")
            if '业绩' in title or '预增' in title:
                specific_events.append("业绩预期向好")
        
        # 构建个性化分析
        parts = []
        
        # 1. 整体趋势判断
        if sentiment_label in ['偏多', '略偏多']:
            parts.append("板块受利好消息提振")
        elif sentiment_label in ['偏空', '略偏空']:
            parts.append("板块承压，市场情绪偏谨慎")
        else:
            parts.append("板块走势震荡，多空因素交织")
        
        # 2. 具体因素
        if factors_found:
            parts.append(f"主要关注{'、'.join(factors_found[:3])}等因素")
        
        # 3. 具体事件
        if specific_events:
            unique_events = list(dict.fromkeys(specific_events))[:2]  # 去重，最多2个
            parts.append(f"近期{'，'.join(unique_events)}")
        
        # 4. 建议
        parts.append("建议关注后续政策面和资金面变化，把握结构性机会")
        
        # 组合成完整分析
        reasoning = "。".join(parts)
        if not reasoning.endswith("。"):
            reasoning += "。"
        
        return reasoning
    
    def analyze(self, industry: str, days: int = 7) -> Dict:
        """完整分析流程"""
        print(f"🔍 正在分析 {industry} 行情与舆情...")
        
        # 1. 获取行情数据
        print("  → 获取行情数据...")
        market_data = self.get_market_data(industry, days)
        
        # 2. 获取舆情数据
        print("  → 获取舆情数据...")
        sentiment_data = self.get_sentiment_data(industry)
        
        # 3. 生成原因分析
        print("  → 生成走势分析...")
        reasoning = self.generate_reasoning(market_data, sentiment_data, industry)
        
        # 4. 识别风险
        risks = self._identify_risks(market_data, sentiment_data)
        
        result = {
            "industry": industry,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "market_data": market_data,
            "sentiment": sentiment_data,
            "reasoning": reasoning,
            "risks": risks
        }
        
        # 保存结果
        output_file = self.cache_dir / f"{industry}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 分析完成，结果保存至: {output_file}")
        return result
    
    def _identify_risks(self, market_data: Dict, sentiment_data: Dict) -> List[str]:
        """识别风险因素"""
        risks = []
        
        change_pct = market_data.get('change_pct', 0)
        rsi = market_data.get('rsi', 50)
        events = sentiment_data.get('key_events', [])
        
        if change_pct < -5:
            risks.append("短期跌幅较大，注意止损")
        
        if rsi > 80:
            risks.append("技术超买，警惕回调")
        elif rsi < 20:
            risks.append("技术超卖，或有反弹")
        
        if "中东局势" in events or "地缘政治" in events:
            risks.append("地缘政治风险")
        
        if "业绩发布" in events:
            risks.append("业绩不确定性")
        
        if "监管动态" in events:
            risks.append("政策监管风险")
        
        return risks if risks else ["市场风险"]
    
    def search_macro_factors(self, industry: str) -> List[str]:
        """互联网搜索宏观影响因素"""
        try:
            # 搜索行业相关的宏观新闻
            # 这里使用预定义的影响因素映射
            macro_factors = {
                "光模块": ["中东局势", "AI算力需求", "1.6T光模块出货"],
                "CPO": ["中东局势", "英伟达财报", "AI算力需求"],
                "人形机器人": ["特斯拉Optimus进展", "量产进度", "政策扶持"],
                "量子科技": ["技术突破", "政策利好", "量子计算商业化"],
                "脑机接口": ["Neuralink进展", "临床试验", "政策支持"],
                "AI应用": ["大模型迭代", "应用场景落地", "算力成本"],
                "低空经济": ["适航认证", "订单交付", "空域政策"],
            }
            
            return macro_factors.get(industry, [])
        except Exception as e:
            return []


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='行业行情与舆情分析')
    parser.add_argument('--industry', '-i', required=True, help='行业名称')
    parser.add_argument('--days', '-d', type=int, default=7, help='分析天数')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    args = parser.parse_args()
    
    analyzer = MarketSentimentAnalyzer()
    result = analyzer.analyze(args.industry, args.days)
    
    # 输出结果
    print("\n" + "="*60)
    print(f"📊 {args.industry} 行情分析报告")
    print("="*60)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存: {args.output}")


if __name__ == "__main__":
    main()
