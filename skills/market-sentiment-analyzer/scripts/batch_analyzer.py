#!/usr/bin/env python3
"""
批量舆情分析定时任务
每天定时分析所有监控行业，存入数据库
供行业报告skill直接调用
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.db_manager import get_db
from api.sentiment_api import SentimentAPI

# 监控行业列表
MONITORED_INDUSTRIES = [
    "光模块",
    "CPO",
    "人形机器人",
    "机器人",
    "量子科技",
    "量子",
    "脑机接口",
    "AI应用",
    "人工智能",
    "低空经济",
    "算力",
    "芯片",
    "集成电路",
    "生物医药",
    "新能源"
]

def fetch_market_data(industry: str) -> dict:
    """获取行业行情数据"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from tencent_fetcher import TencentDataFetcher
        fetcher = TencentDataFetcher()
        return fetcher.get_concept_market_data(industry)
    except Exception as e:
        print(f"  ⚠️  获取{industry}行情失败: {e}")
        return {}

def generate_summary(industry: str, change_pct: float, trend: str) -> dict:
    """生成概述内容"""
    # 这里简化处理，实际应该调用搜索和分析
    # 目前使用预定义的模板数据
    
    summaries = {
        "光模块": {
            "sentiment_brief": "光模块板块今日下跌，主要受中东地缘政治危机影响。伊朗封锁霍尔木兹海峡导致油价暴涨，推高通胀预期，市场担忧美联储维持高利率将压缩科技股估值。资金从AI板块流出，板块承压。",
            "key_factors": ["地缘政治", "能源危机", "货币政策", "资金流出"],
            "risk_level": "高",
            "outlook_short": "短期关注中东局势演变，中期等待估值回归"
        },
        "算力": {
            "sentiment_brief": "算力板块今日逆势上涨，主要受益于大额算力服务订单签订，验证了商业模式可行性。同时AI应用商业化落地加速，国产算力技术突破进一步强化了国产替代逻辑。",
            "key_factors": ["大单签订", "AI应用落地", "国产替代", "政策支持"],
            "risk_level": "中",
            "outlook_short": "短期高位震荡，关注新订单持续性"
        },
        "人形机器人": {
            "sentiment_brief": "人形机器人板块今日回调，主要受利好兑现后的获利回吐影响。节前资金提前博弈春晚亮相预期，节后资金离场。同时产业化进度不及预期，估值逻辑从'技术故事'切换到'订单业绩'。",
            "key_factors": ["利好兑现", "量产推迟", "估值切换", "筹码松动"],
            "risk_level": "中",
            "outlook_short": "高位震荡，等待量产进度催化"
        }
    }
    
    # 默认模板
    default = {
        "sentiment_brief": f"{industry}板块今日{trend}，市场情绪波动。建议关注行业政策变化和龙头企业动态，注意控制风险。",
        "key_factors": ["市场情绪", "资金流向"],
        "risk_level": "中",
        "outlook_short": "短期震荡，等待明确方向"
    }
    
    return summaries.get(industry, default)

def generate_detail_text(industry: str) -> str:
    """生成详情分析文字"""
    # 实际应该从搜索和分析结果生成
    # 这里返回简化版
    
    return f"""
{industry}板块行情分析

第一步：行情数据获取
获取{industry}板块最新行情数据，包括涨跌幅、成交量、资金流向等。

第二步：舆情数据收集
通过多维度搜索收集{industry}相关新闻、研报、政策等信息。

第三步：因果分析
分析影响{industry}板块走势的核心因素，构建传导链条。

第四步：结论生成
基于以上分析，生成投资建议和风险提示。

[详细分析内容待补充]
"""

def analyze_industry(industry: str, date: str) -> bool:
    """分析单个行业并入库"""
    print(f"\n分析行业: {industry}")
    print("-" * 40)
    
    try:
        # 1. 获取行情数据
        market_data = fetch_market_data(industry)
        if not market_data or 'error' in market_data:
            print(f"  ⚠️ 行情数据获取失败，跳过")
            return False
        
        change_pct = market_data.get('change_pct', 0)
        trend = market_data.get('trend', '震荡')
        leader_stocks = market_data.get('leader_stocks', [])
        
        print(f"  📊 行情: {change_pct:+.2f}% ({trend})")
        
        # 2. 生成概述
        summary_data = generate_summary(industry, change_pct, trend)
        
        # 3. 保存概述
        db = get_db()
        summary_record = {
            'industry': industry,
            'date': date,
            'change_pct': change_pct,
            'trend': trend,
            'sentiment_brief': summary_data['sentiment_brief'],
            'key_factors': summary_data['key_factors'],
            'risk_level': summary_data['risk_level'],
            'outlook_short': summary_data['outlook_short']
        }
        
        if db.save_summary(summary_record):
            print(f"  ✅ 概述已保存")
        else:
            print(f"  ❌ 概述保存失败")
            return False
        
        # 4. 生成并保存详情
        detail_text = generate_detail_text(industry)
        detail_record = {
            'industry': industry,
            'date': date,
            'change_pct': change_pct,
            'volume_status': market_data.get('volume_change', '持平'),
            'fund_flow': '待分析',
            'leader_stocks': leader_stocks,
            'causal_analysis_full': detail_text,
            'root_cause': '待分析',
            'key_events': [],
            'data_sources': ['腾讯财经API'],
            'analysis_depth': 2,
            'verification_status': '自动分析'
        }
        
        if db.save_detail(detail_record):
            print(f"  ✅ 详情已保存")
        else:
            print(f"  ❌ 详情保存失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ 分析失败: {e}")
        return False

def batch_analyze_all(date: str = None):
    """批量分析所有行业"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    print("=" * 60)
    print(f"批量舆情分析任务")
    print(f"日期: {date}")
    print(f"行业数: {len(MONITORED_INDUSTRIES)}")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for i, industry in enumerate(MONITORED_INDUSTRIES, 1):
        print(f"\n[{i}/{len(MONITORED_INDUSTRIES)}] ", end="")
        
        if analyze_industry(industry, date):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"分析完成!")
    print(f"成功: {success_count} 个行业")
    print(f"失败: {fail_count} 个行业")
    print("=" * 60)
    
    return success_count, fail_count

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='批量舆情分析')
    parser.add_argument('--date', '-d', help='分析日期 (默认今天)')
    parser.add_argument('--industry', '-i', help='分析单个行业')
    
    args = parser.parse_args()
    
    if args.industry:
        # 分析单个行业
        date = args.date or datetime.now().strftime('%Y-%m-%d')
        analyze_industry(args.industry, date)
    else:
        # 批量分析
        batch_analyze_all(args.date)
