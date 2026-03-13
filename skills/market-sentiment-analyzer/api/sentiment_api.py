#!/usr/bin/env python3
"""
API服务模块
对外暴露REST API接口
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.db_manager import get_db

class SentimentAPI:
    """舆情分析API服务"""
    
    def __init__(self):
        self.db = get_db()
    
    def get_summary(self, industry: str, date: str = None) -> Dict:
        """
        获取单个行业概述 (用于报告首页)
        
        Args:
            industry: 行业名称
            date: 日期 (默认今天)
        
        Returns:
            {
                "industry": "光模块",
                "date": "2026-03-09",
                "change_pct": -4.36,
                "trend": "下跌",
                "sentiment_brief": "3-5句话概述...",
                "key_factors": ["因素1", "因素2"],
                "risk_level": "高",
                "outlook_short": "短期展望..."
            }
        """
        result = self.db.get_summary(industry, date)
        
        if result:
            return {
                "status": "success",
                "data": result
            }
        else:
            return {
                "status": "not_found",
                "message": f"未找到 {industry} 的舆情数据",
                "data": None
            }
    
    def get_detail(self, industry: str, date: str = None) -> Dict:
        """
        获取单个行业详情 (用于详情页)
        
        Args:
            industry: 行业名称
            date: 日期 (默认今天)
        
        Returns:
            {
                "industry": "光模块",
                "date": "2026-03-09",
                "change_pct": -4.36,
                "volume_status": "放量下跌",
                "fund_flow": "主力净流出17亿",
                "leader_stocks": [...],
                "causal_analysis_full": "完整的5层因果分析文字...",
                "root_cause": "根本原因",
                "key_events": [...],
                "data_sources": [...],
                "analysis_depth": 3,
                "verification_status": "已验证"
            }
        """
        result = self.db.get_detail(industry, date)
        
        if result:
            return {
                "status": "success",
                "data": result
            }
        else:
            return {
                "status": "not_found",
                "message": f"未找到 {industry} 的详细分析",
                "data": None
            }
    
    def get_both(self, industry: str, date: str = None) -> Dict:
        """
        同时获取概述和详情
        
        Args:
            industry: 行业名称
            date: 日期 (默认今天)
        
        Returns:
            {
                "industry": "光模块",
                "date": "2026-03-09",
                "summary": {...},
                "detail": {...}
            }
        """
        result = self.db.get_both(industry, date)
        
        if result:
            return {
                "status": "success",
                "data": result
            }
        else:
            return {
                "status": "not_found",
                "message": f"未找到 {industry} 的数据",
                "data": None
            }
    
    def get_batch(self, industries: List[str], date: str = None, include_detail: bool = False) -> Dict:
        """
        批量获取多个行业数据 (用于生成完整报告)
        
        Args:
            industries: 行业名称列表
            date: 日期 (默认今天)
            include_detail: 是否包含详情
        
        Returns:
            {
                "date": "2026-03-09",
                "industries": [
                    {"industry": "光模块", "summary": {...}, "detail": {...}},
                    ...
                ],
                "total": 3,
                "generated_at": "..."
            }
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        results = []
        for industry in industries:
            if include_detail:
                data = self.db.get_both(industry, date)
            else:
                summary = self.db.get_summary(industry, date)
                if summary:
                    data = {
                        'industry': industry,
                        'date': date,
                        'summary': summary
                    }
                else:
                    data = None
            
            if data:
                results.append(data)
        
        return {
            "status": "success",
            "date": date,
            "industries": results,
            "total": len(results),
            "generated_at": datetime.now().isoformat()
        }
    
    def get_all_summaries(self, date: str = None) -> Dict:
        """
        获取所有行业概述 (用于首页汇总)
        
        Args:
            date: 日期 (默认今天)
        
        Returns:
            {
                "date": "2026-03-09",
                "industries": [
                    {"industry": "光模块", "change_pct": -4.36, ...},
                    ...
                ],
                "up_count": 2,
                "down_count": 3,
                "neutral_count": 1
            }
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        results = self.db.get_all_summaries(date)
        
        up_count = sum(1 for r in results if r.get('change_pct', 0) > 0)
        down_count = sum(1 for r in results if r.get('change_pct', 0) < 0)
        neutral_count = sum(1 for r in results if r.get('change_pct', 0) == 0)
        
        return {
            "status": "success",
            "date": date,
            "industries": results,
            "up_count": up_count,
            "down_count": down_count,
            "neutral_count": neutral_count,
            "generated_at": datetime.now().isoformat()
        }
    
    def trigger_analysis(self, industries: List[str], depth: int = 3) -> Dict:
        """
        触发分析任务 (异步)
        
        Args:
            industries: 行业名称列表
            depth: 分析深度 (1-4)
        
        Returns:
            {
                "task_id": "task_20260309_001",
                "status": "queued",
                "industries": [...],
                "depth": 3,
                "estimated_completion": "..."
            }
        """
        # 这里应该启动异步任务
        # 简化版直接返回任务ID
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "status": "queued",
            "task_id": task_id,
            "industries": industries,
            "depth": depth,
            "message": "分析任务已加入队列，请稍后查询结果",
            "estimated_completion": (datetime.now().isoformat())
        }


# 便捷函数
def get_sentiment_summary(industry: str, date: str = None) -> Dict:
    """获取行业概述 (供其他skill调用)"""
    api = SentimentAPI()
    return api.get_summary(industry, date)

def get_sentiment_detail(industry: str, date: str = None) -> Dict:
    """获取行业详情 (供其他skill调用)"""
    api = SentimentAPI()
    return api.get_detail(industry, date)

def get_sentiment_batch(industries: List[str], date: str = None, include_detail: bool = False) -> Dict:
    """批量获取行业舆情 (供其他skill调用)"""
    api = SentimentAPI()
    return api.get_batch(industries, date, include_detail)


if __name__ == "__main__":
    # 测试API
    api = SentimentAPI()
    
    print("="*60)
    print("测试1: 获取单个行业概述")
    print("="*60)
    result = api.get_summary('光模块')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n" + "="*60)
    print("测试2: 获取单个行业详情")
    print("="*60)
    result = api.get_detail('光模块')
    if result['data']:
        print(f"完整分析文字长度: {len(result['data']['causal_analysis_full'])} 字符")
        print(f"前200字符预览:\n{result['data']['causal_analysis_full'][:200]}...")
    
    print("\n" + "="*60)
    print("测试3: 批量获取多个行业")
    print("="*60)
    result = api.get_batch(['光模块', '算力', '人形机器人'], include_detail=False)
    print(f"获取到 {result['total']} 个行业数据")
    for item in result['industries']:
        print(f"  - {item['industry']}: {item['summary']['change_pct']:+.2f}%")
