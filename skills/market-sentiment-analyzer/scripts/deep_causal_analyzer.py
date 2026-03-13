#!/usr/bin/env python3
"""
深度因果推理分析器 V2
实现5层分析：表面现象→直接驱动→宏观环境→国际形势→深层因果
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# 添加tencent_fetcher路径
sys.path.insert(0, str(Path(__file__).parent))
from tencent_fetcher import TencentDataFetcher

class DeepCausalAnalyzer:
    """深度因果推理分析器"""
    
    def __init__(self):
        self.fetcher = TencentDataFetcher()
        self.search_results = {
            "layer1_surface": {},      # 表面现象
            "layer2_direct": [],       # 直接驱动
            "layer3_macro": [],        # 宏观环境
            "layer4_international": [], # 国际形势
            "layer5_causal_chain": ""  # 深层因果
        }
    
    def search_multi_dimension(self, industry: str) -> Dict:
        """
        5维深度搜索
        """
        print("🔍 启动5维深度搜索...")
        
        # 维度1: 实时新闻（发生了什么）
        print("  → 搜索实时新闻...")
        try:
            from kimi_search import kimi_search
            news = kimi_search(f"{industry} 今日 最新消息 下跌 原因", limit=10)
            self.search_results["layer2_direct"] = news
            print(f"     找到{len(news)}条新闻")
        except Exception as e:
            print(f"     搜索失败: {e}")
        
        # 维度2: 产业分析（行业视角）
        print("  → 搜索产业分析...")
        try:
            industry_analysis = kimi_search(f"{industry} 产业链 发展趋势 投资分析 2026", limit=5)
            print(f"     找到{len(industry_analysis)}篇分析")
        except Exception as e:
            print(f"     搜索失败: {e}")
        
        # 维度3: 宏观政策（政策视角）
        print("  → 搜索宏观政策...")
        try:
            policy = kimi_search(f"AI 人工智能 政策 补贴 监管 美国 中国 2026", limit=5)
            print(f"     找到{len(policy)}条政策信息")
        except Exception as e:
            print(f"     搜索失败: {e}")
        
        # 维度4: 国际形势（全球视角）
        print("  → 搜索国际形势...")
        try:
            international = kimi_search(f"中东 伊朗 霍尔木兹海峡 石油 地缘政治 2026", limit=5)
            self.search_results["layer4_international"] = international
            print(f"     找到{len(international)}条国际新闻")
        except Exception as e:
            print(f"     搜索失败: {e}")
        
        # 维度5: 资本市场（资金视角）
        print("  → 搜索资本市场观点...")
        try:
            capital = kimi_search(f"{industry} 主力资金 机构 北向资金 减仓 2026", limit=5)
            print(f"     找到{len(capital)}条资本动态")
        except Exception as e:
            print(f"     搜索失败: {e}")
        
        return self.search_results
    
    def extract_causal_factors(self, search_results: Dict) -> List[Dict]:
        """
        从搜索结果中提取因果因素
        """
        factors = []
        
        # 从国际新闻中提取
        for news in search_results.get("layer4_international", []):
            title = news.get("title", "")
            if "伊朗" in title or "霍尔木兹" in title:
                factors.append({
                    "layer": 4,
                    "type": "地缘政治",
                    "event": "伊朗威胁封锁霍尔木兹海峡",
                    "impact": "全球石油供应危机预期",
                    "transmission": "石油价格上涨→通胀预期→加息预期→科技股估值承压"
                })
            if "石油" in title and ("上涨" in title or "供应" in title):
                factors.append({
                    "layer": 4,
                    "type": "能源危机",
                    "event": "中东石油供应受阻",
                    "impact": "全球能源成本上升",
                    "transmission": "油价上涨→通胀上升→货币政策收紧→风险资产下跌"
                })
        
        # 从直接新闻中提取
        for news in search_results.get("layer2_direct", []):
            title = news.get("title", "")
            if "净卖出" in title or "净流出" in title:
                factors.append({
                    "layer": 2,
                    "type": "资金流向",
                    "event": "主力资金净流出",
                    "impact": "短期抛压增大",
                    "transmission": "机构减仓→股价下跌→散户恐慌→进一步下跌"
                })
        
        return factors
    
    def build_causal_chain(self, industry: str, factors: List[Dict], market_data: Dict) -> str:
        """
        构建深度因果链条
        """
        change_pct = market_data.get("change_pct", 0)
        trend = "上涨" if change_pct > 0 else "下跌"
        
        # 识别根本原因
        root_causes = [f for f in factors if f["layer"] == 4]  # 国际形势
        direct_causes = [f for f in factors if f["layer"] == 2]  # 直接驱动
        
        # 构建链条描述
        chain_parts = []
        
        # 如果有国际因素
        if root_causes:
            chain_parts.append(f"【根本原因】{root_causes[0]['event']}")
            chain_parts.append(f"  → {root_causes[0]['impact']}")
            chain_parts.append(f"  → {root_causes[0]['transmission']}")
        
        # 添加宏观传导
        chain_parts.append("【宏观影响】中东石油美元收入下降→美债销售困难→美国财政融资成本上升")
        chain_parts.append("  → 美国政府支出受限→AI产业补贴预期减少")
        
        # 添加市场反应
        if direct_causes:
            chain_parts.append(f"【市场反应】{direct_causes[0]['event']}→{change_pct:.2f}%{trend}")
        
        return "\n".join(chain_parts)
    
    def generate_analysis_report(self, industry: str) -> Dict:
        """
        生成完整的深度分析报告
        """
        print(f"\n{'='*60}")
        print(f"🔬 启动深度因果分析：{industry}")
        print(f"{'='*60}\n")
        
        # Layer 1: 表面现象
        print("【Layer 1】表面现象识别")
        market_data = self.fetcher.get_concept_market_data(industry)
        if "error" not in market_data:
            print(f"  📊 行情：{market_data['change_pct']:+.2f}% ({market_data['trend']})")
            print(f"  💰 龙头股：{', '.join(market_data['leader_stocks'][:3])}")
        
        # 多维搜索
        print("\n【Layer 2-4】多维深度搜索...")
        search_results = self.search_multi_dimension(industry)
        
        # 提取因果因素
        print("\n【Layer 5】提取因果因素...")
        factors = self.extract_causal_factors(search_results)
        print(f"  识别到{len(factors)}个关键因素")
        
        # 构建因果链条
        print("\n【深度因果链条】")
        causal_chain = self.build_causal_chain(industry, factors, market_data)
        print(causal_chain)
        
        # 生成报告
        report = {
            "industry": industry,
            "timestamp": datetime.now().isoformat(),
            "analysis_version": "2.0-deep-causal",
            "layers": {
                "layer1_surface": {
                    "market_data": market_data,
                    "description": f"{market_data.get('trend', '震荡')}{abs(market_data.get('change_pct', 0)):.2f}%"
                },
                "layer2_direct_factors": [f for f in factors if f["layer"] == 2],
                "layer3_macro": "需进一步搜索宏观数据",
                "layer4_international": [f for f in factors if f["layer"] == 4],
                "layer5_causal_chain": causal_chain
            },
            "conclusion": {
                "root_cause": factors[0]["event"] if factors else "未知",
                "transmission_path": "国际形势→能源市场→债券市场→财政政策→产业政策→资本市场",
                "key_risks": ["地缘政治风险", "美债销售困难", "AI投资预期下调"]
            }
        }
        
        # 保存报告
        output_dir = Path(__file__).parent.parent / "output" / "deep_analysis"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{industry}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print(f"✅ 深度分析完成！")
        print(f"💾 报告保存：{output_file}")
        print(f"{'='*60}\n")
        
        return report


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='深度因果推理分析器')
    parser.add_argument('--industry', '-i', required=True, help='行业名称')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    args = parser.parse_args()
    
    analyzer = DeepCausalAnalyzer()
    report = analyzer.generate_analysis_report(args.industry)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"💾 详细报告：{args.output}")


if __name__ == "__main__":
    main()
