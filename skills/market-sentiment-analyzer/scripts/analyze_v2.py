#!/usr/bin/env python3
"""
市场情感分析器 - 专业证券研究员级别
实现COT思维链：数据采集 → 多维度分析 → 关联分析 → 归因分析 → 结论生成
"""

import json
import pandas as pd
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class MarketSentimentAnalyzer:
    """行情与舆情分析器 - 专业证券研究员级别"""
    
    def __init__(self):
        self.cache_dir = Path(__file__).parent.parent / "output" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.data_sources = []  # 记录使用的数据源
        
    # ==================== 第一层：数据采集 ====================
    
    def collect_market_data(self, industry: str, days: int = 7) -> Dict:
        """
        采集行情数据（多源冗余策略）
        数据源优先级：腾讯财经 > 东方财富 > 同花顺
        """
        self.data_sources = []
        
        # 优先使用腾讯财经API（最稳定）
        try:
            from tencent_fetcher import TencentDataFetcher
            fetcher = TencentDataFetcher()
            result = fetcher.get_concept_market_data(industry)
            if "error" not in result:
                result["source"] = "腾讯财经"
                self.data_sources.append("腾讯财经")
                return result
        except Exception as e:
            pass
        
        # 备用：东方财富/同花顺
        result = {"error": None}
        try:
            import akshare as ak
            board_name = self._map_industry_to_board(industry)
            df = ak.stock_board_concept_hist_em(
                symbol=board_name, period="日k",
                start_date=(datetime.now() - timedelta(days=days+5)).strftime("%Y%m%d"),
                end_date=datetime.now().strftime("%Y%m%d"), adjust=""
            )
            if df is not None and not df.empty:
                result = self._process_board_df(df, days)
                result["source"] = "东方财富"
                self.data_sources.append("东方财富")
                return result
        except Exception as e:
            result["error"] = f"东方财富: {str(e)}"
        
        self.data_sources.append("无可用数据源")
        return {"error": result.get("error", "所有数据源均不可用")}
    
    def _map_industry_to_board(self, industry: str) -> str:
        """行业名称映射到板块名称"""
        mapping = {
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
            "生物医药": "创新药",
            "消费": "消费",
        }
        return mapping.get(industry, industry)
    
    def _process_board_df(self, df: pd.DataFrame, days: int) -> Dict:
        """处理板块行情DataFrame"""
        df = df.tail(days)
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        change_pct = float(latest['涨跌幅']) if '涨跌幅' in latest else 0
        close_prices = pd.to_numeric(df['收盘'], errors='coerce').dropna()
        rsi = self._calculate_rsi(close_prices) if len(close_prices) > 14 else 50
        
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
            "technical_signal": self._interpret_technical(rsi, change_pct),
            "amplitude": round(float(latest.get('振幅', 0)), 2),
            "highest": float(latest['最高']) if '最高' in latest else 0,
            "lowest": float(latest['最低']) if '最低' in latest else 0,
        }
    
    def _fetch_sina_finance(self, industry: str, days: int) -> Dict:
        """从新浪财经获取行情（备用数据源）"""
        # 新浪财经行业板块API
        url = f"https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
        # 这里简化处理，实际需根据行业映射到新浪板块代码
        return {"error": "新浪财经数据源待实现"}
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
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
        return 100 - (100 / (1 + rs))
    
    def _interpret_technical(self, rsi: float, change_pct: float) -> str:
        """技术指标解读"""
        if rsi > 70:
            return "超买（警惕回调）"
        elif rsi < 30:
            return "超卖（或有反弹）"
        elif change_pct > 3:
            return "强势上涨"
        elif change_pct < -3:
            return "弱势下跌"
        return "震荡整理"
    
    def collect_sentiment_data(self, industry: str) -> Dict:
        """
        采集舆情数据（三层架构）
        P0: 财联社 | P1: 股吧/雪球 | P2: 宏观政策
        """
        sentiment_result = {
            "layer_p0": [],  # 权威媒体
            "layer_p1": [],  # 社交平台
            "layer_p2": [],  # 宏观政策
            "combined": {}
        }
        
        # P0: 财联社新闻
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "cailianshe-news" / "scripts"))
            from fetch_cailianshe import fetch_cailianshe_news
            
            news = fetch_cailianshe_news(industry, limit=15)
            sentiment_result["layer_p0"] = news
            
            # 深度分析新闻
            sentiment_analysis = self._analyze_news_sentiment(news)
            sentiment_result["combined"] = sentiment_analysis
            
        except Exception as e:
            sentiment_result["error_p0"] = str(e)
        
        return sentiment_result
    
    def _analyze_news_sentiment(self, news_list: List[Dict]) -> Dict:
        """
        深度分析新闻情绪和内容
        使用情绪周期理论 + PESTEL模型
        """
        if not news_list:
            return {"sentiment_label": "中性", "sentiment_score": 0, "key_factors": []}
        
        # 情绪关键词库
        sentiment_keywords = {
            "positive": ["利好", "增长", "突破", "上涨", "超预期", "订单", "签约", "合作", "放量", "新高"],
            "negative": ["利空", "下跌", "下滑", "不及预期", "风险", "亏损", "减持", "制裁", "暴雷", "跌停"],
            "macro": {
                "中东": "地缘政治",
                "战争": "地缘政治", 
                "冲突": "地缘政治",
                "政策": "政策影响",
                "监管": "监管动态",
                "加息": "货币政策",
                "降息": "货币政策",
                "关税": "贸易摩擦",
                "制裁": "国际制裁"
            }
        }
        
        pos_count = 0
        neg_count = 0
        macro_factors = []
        capital_flow = ""  # 资金流向
        
        for news in news_list:
            title = news.get('title', '')
            
            # 情绪统计
            for kw in sentiment_keywords["positive"]:
                if kw in title:
                    pos_count += 1
                    break
            for kw in sentiment_keywords["negative"]:
                if kw in title:
                    neg_count += 1
                    break
            
            # 宏观因素提取（PESTEL）
            for keyword, factor_type in sentiment_keywords["macro"].items():
                if keyword in title and factor_type not in macro_factors:
                    macro_factors.append(factor_type)
            
            # 资金流向提取
            if '净卖出' in title or '净流出' in title:
                capital_flow = "主力资金净流出"
            elif '净买入' in title or '净流入' in title:
                capital_flow = "主力资金净流入"
        
        # 计算情绪得分（-100到+100）
        total = pos_count + neg_count
        if total > 0:
            sentiment_score = (pos_count - neg_count) / total * 100
        else:
            sentiment_score = 0
        
        # 情绪标签
        if sentiment_score > 30:
            sentiment_label = "偏多"
        elif sentiment_score < -30:
            sentiment_label = "偏空"
        elif sentiment_score > 10:
            sentiment_label = "略偏多"
        elif sentiment_score < -10:
            sentiment_label = "略偏空"
        else:
            sentiment_label = "中性"
        
        return {
            "news_count": len(news_list),
            "positive": pos_count,
            "negative": neg_count,
            "neutral": len(news_list) - pos_count - neg_count,
            "sentiment_score": round(sentiment_score, 2),
            "sentiment_label": sentiment_label,
            "key_factors": macro_factors,
            "capital_flow": capital_flow,
            "latest_news": news_list[:5]  # 最新5条
        }
    
    # ==================== 第二层：多维度分析 ====================
    
    def analyze_market_environment(self) -> Dict:
        """
        大盘环境判断
        分析维度：指数走势、成交量、资金流向、涨跌家数
        """
        try:
            import akshare as ak
            
            # 获取上证指数数据
            sh_index = ak.index_zh_a_hist(symbol="000001", period="daily", 
                start_date=(datetime.now() - timedelta(days=5)).strftime("%Y%m%d"),
                end_date=datetime.now().strftime("%Y%m%d"))
            
            if sh_index is not None and not sh_index.empty:
                latest = sh_index.iloc[-1]
                change_pct = float(latest['涨跌幅'])
                
                # 判断市场环境
                if change_pct > 1:
                    env = "强势上涨"
                elif change_pct > 0:
                    env = "温和上涨"
                elif change_pct > -1:
                    env = "震荡调整"
                else:
                    env = "明显下跌"
                
                return {
                    "sh_index_change": round(change_pct, 2),
                    "environment": env,
                    "trend": "上涨" if change_pct > 0 else "下跌"
                }
        except Exception as e:
            pass
        
        return {"environment": "未知", "sh_index_change": 0}
    
    def analyze_relative_strength(self, industry_change: float, market_change: float) -> Dict:
        """
        板块相对强度分析
        """
        relative = industry_change - market_change
        
        if relative > 2:
            strength = "显著强于大盘"
        elif relative > 0:
            strength = "强于大盘"
        elif relative > -2:
            strength = "与大盘持平"
        else:
            strength = "弱于大盘"
        
        return {
            "relative_change": round(relative, 2),
            "strength": strength,
            "outperform": relative > 0
        }
    
    # ==================== 第三层：关联分析 ====================
    
    def correlation_analysis(self, market_data: Dict, sentiment_data: Dict) -> Dict:
        """
        行情与舆情关联分析
        """
        change_pct = market_data.get('change_pct', 0)
        sentiment_label = sentiment_data.get('sentiment_label', '中性')
        sentiment_score = sentiment_data.get('sentiment_score', 0)
        
        # 验证一致性
        consistent = False
        if change_pct < -2 and sentiment_score < -20:
            consistent = True  # 下跌+偏空 = 一致
        elif change_pct > 2 and sentiment_score > 20:
            consistent = True  # 上涨+偏多 = 一致
        elif -2 <= change_pct <= 2 and -20 <= sentiment_score <= 20:
            consistent = True  # 震荡+中性 = 一致
        
        return {
            "price_sentiment_consistent": consistent,
            "correlation_strength": "强" if abs(sentiment_score) > 50 else "中" if abs(sentiment_score) > 20 else "弱"
        }
    
    # ==================== 第四层：归因分析 ====================
    
    def attribution_analysis(self, market_data: Dict, sentiment_data: Dict, 
                           market_env: Dict, relative_strength: Dict) -> List[Dict]:
        """
        走势归因分析（按权重排序）
        """
        factors = []
        
        change_pct = market_data.get('change_pct', 0)
        technical = market_data.get('technical_signal', '')
        sentiment_label = sentiment_data.get('sentiment_label', '中性')
        sentiment_score = sentiment_data.get('sentiment_score', 0)
        key_factors = sentiment_data.get('key_factors', [])
        capital_flow = sentiment_data.get('capital_flow', '')
        env = market_env.get('environment', '')
        
        # 因素1：宏观环境（权重最高）
        if key_factors:
            factors.append({
                "factor": "、".join(key_factors),
                "weight": 40,
                "description": f"受{'、'.join(key_factors)}影响，市场整体情绪{'偏空' if change_pct < 0 else '偏多'}"
            })
        elif "下跌" in env and change_pct < 0:
            factors.append({
                "factor": "大盘环境",
                "weight": 35,
                "description": f"大盘{env}，板块跟随调整"
            })
        
        # 因素2：资金流向
        if capital_flow:
            factors.append({
                "factor": "资金流向",
                "weight": 30,
                "description": capital_flow + "，市场抛压较大" if "流出" in capital_flow else capital_flow + "，市场信心充足"
            })
        
        # 因素3：技术面
        if "超卖" in technical or "超买" in technical:
            factors.append({
                "factor": "技术因素",
                "weight": 15,
                "description": f"技术指标显示{technical}"
            })
        
        # 因素4：情绪面
        if abs(sentiment_score) > 30:
            factors.append({
                "factor": "市场情绪",
                "weight": 15,
                "description": f"市场 sentiment {sentiment_label}，得分{sentiment_score}"
            })
        
        # 默认因素
        if not factors:
            factors.append({
                "factor": "市场波动",
                "weight": 100,
                "description": "市场正常波动，无明显驱动因素"
            })
        
        return sorted(factors, key=lambda x: x['weight'], reverse=True)
    
    # ==================== 第五层：结论生成 ====================
    
    def generate_conclusion(self, industry: str, market_data: Dict, 
                          sentiment_data: Dict, attribution: List[Dict],
                          correlation: Dict) -> Dict:
        """
        生成专业分析结论
        """
        change_pct = market_data.get('change_pct', 0) if 'error' not in market_data else 0
        trend = market_data.get('trend', '震荡') if 'error' not in market_data else '震荡'
        
        # 1. 走势定性
        if change_pct > 5:
            trend_qualitative = "强势上涨"
        elif change_pct > 2:
            trend_qualitative = "温和上涨"
        elif change_pct > -2:
            trend_qualitative = "震荡整理"
        elif change_pct > -5:
            trend_qualitative = "明显下跌"
        else:
            trend_qualitative = "大幅下跌"
        
        # 2. 核心原因（自然语言）
        reasons = []
        for factor in attribution[:3]:  # 前3大因素
            reasons.append(factor['description'])
        
        if change_pct < 0:
            core_reasoning = f"{trend}{abs(change_pct):.2f}%。主要因{'；'.join(reasons)}。市场情绪偏空，资金流出明显。"
        elif change_pct > 0:
            core_reasoning = f"{trend}{change_pct:.2f}%。主要因{'；'.join(reasons)}。市场情绪回暖，资金关注度提升。"
        else:
            core_reasoning = f"震荡整理。{'；'.join(reasons)}。市场等待方向选择。"
        
        # 3. 风险提示
        risks = self._identify_risks(market_data, sentiment_data, attribution)
        
        # 4. 后市展望
        outlook = self._generate_outlook(change_pct, sentiment_data, correlation)
        
        return {
            "trend_qualitative": trend_qualitative,
            "core_reasoning": core_reasoning,
            "risks": risks,
            "outlook": outlook
        }
    
    def _identify_risks(self, market_data: Dict, sentiment_data: Dict, 
                       attribution: List[Dict]) -> List[str]:
        """识别风险因素"""
        risks = []
        
        change_pct = market_data.get('change_pct', 0) if 'error' not in market_data else 0
        rsi = market_data.get('rsi', 50) if 'error' not in market_data else 50
        key_factors = sentiment_data.get('key_factors', [])
        
        # 短期跌幅风险
        if change_pct < -5:
            risks.append("短期跌幅较大，注意止损风险")
        
        # 技术风险
        if rsi > 75:
            risks.append("技术超买，警惕回调风险")
        elif rsi < 25:
            risks.append("技术超卖，或有反弹机会但需确认")
        
        # 宏观风险
        if any(f in key_factors for f in ["地缘政治", "贸易摩擦"]):
            risks.append("地缘政治不确定性")
        
        if "货币政策" in key_factors:
            risks.append("货币政策收紧风险")
        
        # 业绩风险
        if "业绩发布" in str(attribution):
            risks.append("业绩不及预期风险")
        
        return risks if risks else ["市场系统性风险"]
    
    def _generate_outlook(self, change_pct: float, sentiment_data: Dict, 
                         correlation: Dict) -> Dict:
        """生成后市展望"""
        sentiment_label = sentiment_data.get('sentiment_label', '中性')
        consistent = correlation.get('price_sentiment_consistent', False)
        
        # 短期展望（1-5个交易日）
        if change_pct < -3 and sentiment_label == "偏空":
            short_term = "短期或继续承压，关注情绪修复信号"
        elif change_pct > 3 and sentiment_label == "偏多":
            short_term = "短期强势有望延续，关注成交量配合"
        elif not consistent:
            short_term = "行情与情绪背离，短期或有修正"
        else:
            short_term = "短期震荡整理，等待方向明确"
        
        # 中期展望（1-3个月）
        if sentiment_label == "偏空":
            medium_term = "中期需观察基本面改善和政策支持力度"
        elif sentiment_label == "偏多":
            medium_term = "中期趋势向好，回调可考虑布局"
        else:
            medium_term = "中期维持震荡，精选个股为主"
        
        return {
            "short_term": short_term,
            "medium_term": medium_term
        }
    
    # ==================== 主入口 ====================
    
    def analyze(self, industry: str, days: int = 7) -> Dict:
        """
        完整分析流程 - 实现COT思维链
        """
        print(f"🔍 [{industry}] 启动专业行情分析...")
        print("=" * 60)
        
        # 步骤1：数据采集
        print("\n【步骤1】数据采集")
        print("  → 采集行情数据（多源冗余）...")
        market_data = self.collect_market_data(industry, days)
        if 'error' not in market_data:
            print(f"  ✅ 行情数据获取成功（来源: {market_data.get('source', '未知')}）")
        else:
            print(f"  ⚠️ 行情数据获取失败: {market_data.get('error', '未知错误')}")
        
        print("  → 采集舆情数据（三层架构）...")
        sentiment_data_full = self.collect_sentiment_data(industry)
        sentiment_data = sentiment_data_full.get('combined', {})
        print(f"  ✅ 舆情数据采集完成（{sentiment_data.get('news_count', 0)}条新闻）")
        
        # 步骤2：大盘环境分析
        print("\n【步骤2】大盘环境分析")
        market_env = self.analyze_market_environment()
        print(f"  → 大盘环境: {market_env.get('environment', '未知')}（沪指{market_env.get('sh_index_change', 0):+.2f}%）")
        
        # 步骤3：相对强度分析
        print("\n【步骤3】相对强度分析")
        industry_change = market_data.get('change_pct', 0) if 'error' not in market_data else 0
        market_change = market_env.get('sh_index_change', 0)
        relative = self.analyze_relative_strength(industry_change, market_change)
        print(f"  → 相对大盘: {relative.get('strength', '未知')}（相对{relative.get('relative_change', 0):+.2f}%）")
        
        # 步骤4：关联分析
        print("\n【步骤4】行情-舆情关联分析")
        correlation = self.correlation_analysis(market_data, sentiment_data)
        print(f"  → 一致性: {'一致' if correlation.get('price_sentiment_consistent') else '背离'}")
        print(f"  → 关联强度: {correlation.get('correlation_strength', '弱')}")
        
        # 步骤5：归因分析
        print("\n【步骤5】走势归因分析")
        attribution = self.attribution_analysis(market_data, sentiment_data, market_env, relative)
        print("  → 主要驱动因素（按权重排序）:")
        for i, factor in enumerate(attribution[:3], 1):
            print(f"     {i}. {factor['factor']}（权重{factor['weight']}%）")
        
        # 步骤6：结论生成
        print("\n【步骤6】生成分析结论")
        conclusion = self.generate_conclusion(industry, market_data, sentiment_data, attribution, correlation)
        print(f"  → 走势定性: {conclusion['trend_qualitative']}")
        print(f"  → 识别风险: {len(conclusion['risks'])}项")
        
        # 组装最终结果
        result = {
            "industry": industry,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "analysis_framework": "COT思维链（数据采集→多维分析→关联分析→归因分析→结论生成）",
            "market_data": market_data,
            "sentiment": sentiment_data,
            "market_environment": market_env,
            "relative_strength": relative,
            "correlation": correlation,
            "attribution": attribution,
            "conclusion": conclusion,
            "data_sources": self.data_sources
        }
        
        # 保存结果
        output_file = self.cache_dir / f"{industry}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print(f"✅ 分析完成！结果保存至: {output_file}")
        print("=" * 60)
        
        return result


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='专业行情与舆情分析器（证券研究员级别）')
    parser.add_argument('--industry', '-i', required=True, help='行业名称（如：光模块、CPO概念）')
    parser.add_argument('--days', '-d', type=int, default=7, help='分析天数（默认7天）')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='text', help='输出格式')
    
    args = parser.parse_args()
    
    analyzer = MarketSentimentAnalyzer()
    result = analyzer.analyze(args.industry, args.days)
    
    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 文本格式输出
        print(f"\n📊 {result['industry']} 专业分析报告")
        print("=" * 60)
        print(f"分析时间: {result['date']}")
        print(f"分析框架: {result['analysis_framework']}")
        print(f"数据来源: {', '.join(result['data_sources'])}")
        print("\n【行情概况】")
        if 'error' not in result['market_data']:
            md = result['market_data']
            print(f"  涨跌幅: {md.get('change_pct', 0):+.2f}%")
            print(f"  技术面: {md.get('technical_signal', '未知')}")
            print(f"  成交量: {md.get('volume_change', '持平')}")
        print("\n【舆情情绪】")
        st = result['sentiment']
        print(f"  情绪标签: {st.get('sentiment_label', '中性')}（得分{st.get('sentiment_score', 0)}）")
        print(f"  新闻统计: 利好{st.get('positive', 0)}/利空{st.get('negative', 0)}/中性{st.get('neutral', 0)}")
        print(f"  资金流向: {st.get('capital_flow', '未知')}")
        print("\n【核心结论】")
        cn = result['conclusion']
        print(f"  走势定性: {cn.get('trend_qualitative', '未知')}")
        print(f"  核心原因: {cn.get('core_reasoning', '未知')}")
        print("\n【风险提示】")
        for risk in cn.get('risks', []):
            print(f"  - {risk}")
        print("\n【后市展望】")
        outlook = cn.get('outlook', {})
        print(f"  短期: {outlook.get('short_term', '未知')}")
        print(f"  中期: {outlook.get('medium_term', '未知')}")
        print("\n" + "=" * 60)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 详细结果已保存: {args.output}")


if __name__ == "__main__":
    main()
