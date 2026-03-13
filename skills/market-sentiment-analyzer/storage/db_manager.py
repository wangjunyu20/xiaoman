#!/usr/bin/env python3
"""
数据库管理模块
管理SQLite数据库连接和操作
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class SentimentDatabase:
    """舆情数据库管理类"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 使用database目录下的sentiment.db
            db_path = Path(__file__).parent.parent / "database" / "sentiment.db"
        self.db_path = str(db_path)
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        # schema.sql在database目录下
        schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()
            
            conn = sqlite3.connect(self.db_path)
            conn.executescript(schema)
            conn.commit()
            conn.close()
    
    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ==================== 概述表操作 ====================
    
    def save_summary(self, data: Dict) -> bool:
        """保存行业概述"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO industry_sentiment_summary (
                    industry_name, analysis_date, change_pct, trend_summary,
                    sentiment_brief, key_factors, risk_level, outlook_short
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['industry'],
                data['date'],
                data.get('change_pct'),
                data.get('trend'),
                data.get('sentiment_brief'),
                json.dumps(data.get('key_factors', []), ensure_ascii=False),
                data.get('risk_level'),
                data.get('outlook_short')
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"保存概述失败: {e}")
            return False
        finally:
            conn.close()
    
    def get_summary(self, industry: str, date: str = None) -> Optional[Dict]:
        """获取单个行业概述"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM industry_sentiment_summary
                WHERE industry_name = ? AND analysis_date = ?
            ''', (industry, date))
            
            row = cursor.fetchone()
            if row:
                return {
                    'industry': row['industry_name'],
                    'date': row['analysis_date'],
                    'change_pct': row['change_pct'],
                    'trend': row['trend_summary'],
                    'sentiment_brief': row['sentiment_brief'],
                    'key_factors': json.loads(row['key_factors']) if row['key_factors'] else [],
                    'risk_level': row['risk_level'],
                    'outlook_short': row['outlook_short']
                }
            return None
        finally:
            conn.close()
    
    def get_all_summaries(self, date: str = None) -> List[Dict]:
        """获取所有行业概述"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM industry_sentiment_summary
                WHERE analysis_date = ?
                ORDER BY change_pct DESC
            ''', (date,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'industry': row['industry_name'],
                    'date': row['analysis_date'],
                    'change_pct': row['change_pct'],
                    'trend': row['trend_summary'],
                    'sentiment_brief': row['sentiment_brief'],
                    'key_factors': json.loads(row['key_factors']) if row['key_factors'] else [],
                    'risk_level': row['risk_level'],
                    'outlook_short': row['outlook_short']
                })
            return results
        finally:
            conn.close()
    
    # ==================== 详情表操作 ====================
    
    def save_detail(self, data: Dict) -> bool:
        """保存行业详情"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO industry_sentiment_detail (
                    industry_name, analysis_date, change_pct, volume_status,
                    fund_flow, leader_stocks, causal_analysis_full, root_cause,
                    key_events, data_sources, analysis_depth, verification_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['industry'],
                data['date'],
                data.get('change_pct'),
                data.get('volume_status'),
                data.get('fund_flow'),
                json.dumps(data.get('leader_stocks', []), ensure_ascii=False),
                data.get('causal_analysis_full'),
                data.get('root_cause'),
                json.dumps(data.get('key_events', []), ensure_ascii=False),
                json.dumps(data.get('data_sources', []), ensure_ascii=False),
                data.get('analysis_depth', 3),
                data.get('verification_status', '待验证')
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"保存详情失败: {e}")
            return False
        finally:
            conn.close()
    
    def get_detail(self, industry: str, date: str = None) -> Optional[Dict]:
        """获取单个行业详情"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM industry_sentiment_detail
                WHERE industry_name = ? AND analysis_date = ?
            ''', (industry, date))
            
            row = cursor.fetchone()
            if row:
                return {
                    'industry': row['industry_name'],
                    'date': row['analysis_date'],
                    'change_pct': row['change_pct'],
                    'volume_status': row['volume_status'],
                    'fund_flow': row['fund_flow'],
                    'leader_stocks': json.loads(row['leader_stocks']) if row['leader_stocks'] else [],
                    'causal_analysis_full': row['causal_analysis_full'],
                    'root_cause': row['root_cause'],
                    'key_events': json.loads(row['key_events']) if row['key_events'] else [],
                    'data_sources': json.loads(row['data_sources']) if row['data_sources'] else [],
                    'analysis_depth': row['analysis_depth'],
                    'verification_status': row['verification_status']
                }
            return None
        finally:
            conn.close()
    
    def get_both(self, industry: str, date: str = None) -> Optional[Dict]:
        """同时获取概述和详情"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        summary = self.get_summary(industry, date)
        detail = self.get_detail(industry, date)
        
        if summary and detail:
            return {
                'industry': industry,
                'date': date,
                'summary': summary,
                'detail': detail
            }
        return None
    
    def get_batch(self, industries: List[str], date: str = None) -> List[Dict]:
        """批量获取多个行业数据"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        results = []
        for industry in industries:
            data = self.get_both(industry, date)
            if data:
                results.append(data)
        return results


# 单例模式
db_instance = None

def get_db() -> SentimentDatabase:
    """获取数据库实例"""
    global db_instance
    if db_instance is None:
        db_instance = SentimentDatabase()
    return db_instance


if __name__ == "__main__":
    # 测试
    db = get_db()
    
    # 测试获取概述
    summary = db.get_summary('光模块')
    print("光模块概述:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    
    print("\n" + "="*60 + "\n")
    
    # 测试获取详情
    detail = db.get_detail('光模块')
    print("光模块详情:")
    print(f"完整分析文字长度: {len(detail['causal_analysis_full']) if detail else 0} 字符")
