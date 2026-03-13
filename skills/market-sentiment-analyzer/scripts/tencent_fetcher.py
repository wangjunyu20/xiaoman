#!/usr/bin/env python3
"""
行情数据获取模块 - 使用腾讯财经API（绕过东方财富限制）
"""

import requests
import json
import pandas as pd
from typing import Dict, List
from datetime import datetime

class TencentDataFetcher:
    """腾讯财经数据获取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_index_quote(self, code: str) -> Dict:
        """
        获取指数行情
        code: sh000001(上证), sz399001(深成指), sz399006(创业板)
        """
        url = f"https://qt.gtimg.cn/q={code}"
        try:
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                # 解析腾讯数据格式
                data_str = resp.text
                # 格式: v_sh000001="1~上证指数~000001~4102.68~..."
                if '~' in data_str:
                    parts = data_str.split('"')[1].split('~')
                    return {
                        "name": parts[1],
                        "code": parts[2],
                        "current": float(parts[3]),
                        "last_close": float(parts[4]),
                        "change_pct": round((float(parts[3]) - float(parts[4])) / float(parts[4]) * 100, 2),
                        "volume": int(parts[6]) if parts[6].isdigit() else 0
                    }
        except Exception as e:
            return {"error": str(e)}
        return {"error": "获取失败"}
    
    def get_stock_quote(self, code: str) -> Dict:
        """
        获取个股行情
        code: 300308(中际旭创), 600519(茅台)等
        """
        # 自动判断交易所
        if code.startswith('6'):
            full_code = f"sh{code}"
        else:
            full_code = f"sz{code}"
        
        url = f"https://qt.gtimg.cn/q={full_code}"
        try:
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                data_str = resp.text
                if '~' in data_str:
                    parts = data_str.split('"')[1].split('~')
                    return {
                        "name": parts[1],
                        "code": parts[2],
                        "current": float(parts[3]),
                        "last_close": float(parts[4]),
                        "open": float(parts[5]),
                        "high": float(parts[6]),
                        "low": float(parts[7]),
                        "change_pct": float(parts[32]) if len(parts) > 32 else 0,
                        "volume": int(parts[8]) if parts[8].isdigit() else 0,
                        "amount": float(parts[9]) if len(parts) > 9 else 0,
                        "pe": float(parts[39]) if len(parts) > 39 else 0,
                        "pb": float(parts[46]) if len(parts) > 46 else 0,
                        "market_cap": float(parts[44]) if len(parts) > 44 else 0,
                    }
        except Exception as e:
            return {"error": str(e)}
        return {"error": "获取失败"}
    
    def get_concept_stocks(self, concept_name: str) -> List[str]:
        """
        获取概念板块成分股（使用同花顺或东方财富）
        这里使用预定义的龙头股映射
        """
        concept_leaders = {
            "光模块": ["300308", "300394", "300502"],  # 中际旭创、天孚通信、新易盛
            "CPO": ["300308", "300394", "300502"],
            "人形机器人": ["002747", "300124", "300607"],  # 埃斯顿、汇川技术、拓斯达
            "量子科技": ["688027", "600990", "002115"],  # 国盾量子、四创电子、三维通信
            "脑机接口": ["301293", "000516"],  # 三博脑科、国际医学
            "AI应用": ["002230", "002410"],  # 科大讯飞、广联达
            "低空经济": ["002085", "000099", "688070"],  # 万丰奥威、中信海直、纵横股份
            "算力": ["603019", "000977", "000938"],  # 中科曙光、浪潮信息、紫光股份
            "集成电路": ["688981", "002371", "603501"],  # 中芯国际、北方华创、韦尔股份
        }
        return concept_leaders.get(concept_name, [])
    
    def get_concept_market_data(self, concept_name: str) -> Dict:
        """
        获取概念板块行情（通过龙头股平均涨跌幅）
        """
        stocks = self.get_concept_stocks(concept_name)
        if not stocks:
            return {"error": f"未找到{concept_name}的龙头股映射"}
        
        quotes = []
        for code in stocks[:3]:  # 取前3只
            quote = self.get_stock_quote(code)
            if "error" not in quote:
                quotes.append(quote)
        
        if not quotes:
            return {"error": "无法获取龙头股行情"}
        
        # 计算板块平均涨跌幅
        avg_change = sum(q.get('change_pct', 0) for q in quotes) / len(quotes)
        total_volume = sum(q.get('volume', 0) for q in quotes)
        total_amount = sum(q.get('amount', 0) for q in quotes)
        
        # 判断趋势
        trend = "上涨" if avg_change > 0 else "下跌" if avg_change < 0 else "持平"
        
        # 计算RSI（简化版，基于今日涨跌）
        rsi = 50 + avg_change * 2  # 粗略估计
        rsi = max(0, min(100, rsi))
        
        return {
            "concept": concept_name,
            "leader_stocks": [q['name'] for q in quotes],
            "change_pct": round(avg_change, 2),
            "trend": trend,
            "volume": total_volume,
            "amount": round(total_amount, 2),
            "rsi": round(rsi, 2),
            "technical_signal": "超买" if rsi > 70 else "超卖" if rsi < 30 else "震荡",
            "stocks_detail": quotes
        }


# 测试
if __name__ == "__main__":
    fetcher = TencentDataFetcher()
    
    print("=" * 60)
    print("腾讯财经数据获取测试")
    print("=" * 60)
    
    # 测试1：获取大盘指数
    print("\n【上证指数】")
    index = fetcher.get_index_quote("sh000001")
    if "error" not in index:
        print(f"  名称: {index['name']}")
        print(f"  当前: {index['current']}")
        print(f"  涨跌: {index['change_pct']:.2f}%")
    else:
        print(f"  错误: {index['error']}")
    
    # 测试2：获取个股
    print("\n【中际旭创】")
    stock = fetcher.get_stock_quote("300308")
    if "error" not in stock:
        print(f"  名称: {stock['name']}")
        print(f"  当前: {stock['current']}")
        print(f"  涨跌: {stock['change_pct']:.2f}%")
        print(f"  市值: {stock['market_cap']/1e8:.0f}亿")
    else:
        print(f"  错误: {stock['error']}")
    
    # 测试3：获取概念板块
    print("\n【光模块概念】")
    concept = fetcher.get_concept_market_data("光模块")
    if "error" not in concept:
        print(f"  龙头股: {', '.join(concept['leader_stocks'])}")
        print(f"  平均涨跌: {concept['change_pct']:.2f}%")
        print(f"  趋势: {concept['trend']}")
        print(f"  RSI: {concept['rsi']}")
    else:
        print(f"  错误: {concept['error']}")
    
    print("\n" + "=" * 60)
