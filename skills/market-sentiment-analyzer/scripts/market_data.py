#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行情数据采集模块
使用AKShare获取行业板块和龙头股行情数据
"""

import sys
import json
import time
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

import pandas as pd

# 添加indicators模块路径
sys.path.insert(0, str(Path(__file__).parent))
from indicators import calculate_all_indicators, analyze_stock_indicators


class MarketDataCollector:
    """行情数据采集器"""
    
    def __init__(self):
        self.ak = None
        self._init_akshare()
    
    def _init_akshare(self):
        """初始化AKShare"""
        try:
            import akshare as ak
            self.ak = ak
        except ImportError:
            print("错误: 未安装AKShare，请先运行: pip install akshare")
            raise
    
    def get_sector_spot(self) -> pd.DataFrame:
        """获取行业板块实时行情"""
        try:
            df = self.ak.stock_sector_spot_em()
            return df
        except Exception as e:
            print(f"获取板块行情失败: {e}")
            return pd.DataFrame()
    
    def get_sector_by_name(self, sector_name: str) -> Optional[Dict]:
        """
        根据名称获取板块行情
        
        Args:
            sector_name: 板块名称（如"光模块"、"半导体"）
        
        Returns:
            dict: 板块行情数据
        """
        df = self.get_sector_spot()
        if df.empty:
            return None
        
        # 尝试精确匹配
        match = df[df['名称'].str.contains(sector_name, na=False, case=False)]
        
        if match.empty:
            return None
        
        row = match.iloc[0]
        return {
            "name": row.get('名称', ''),
            "code": row.get('代码', ''),
            "price": float(row.get('最新价', 0)),
            "change_pct": float(row.get('涨跌幅', 0)),
            "change_amount": float(row.get('涨跌额', 0)),
            "volume": int(row.get('成交量', 0)),
            "turnover": float(row.get('成交额', 0)),
            "open": float(row.get('开盘价', 0)),
            "high": float(row.get('最高价', 0)),
            "low": float(row.get('最低价', 0)),
            "pre_close": float(row.get('昨收', 0)),
            "volume_ratio": float(row.get('量比', 1)),
            "turnover_rate": float(row.get('换手率', 0))
        }
    
    def get_stock_spot(self, symbol: str) -> Optional[Dict]:
        """
        获取个股实时行情
        
        Args:
            symbol: 股票代码（如"300308"）
        
        Returns:
            dict: 个股行情数据
        """
        try:
            df = self.ak.stock_zh_a_spot_em()
            stock = df[df['代码'] == symbol]
            
            if stock.empty:
                return None
            
            row = stock.iloc[0]
            return {
                "code": symbol,
                "name": row.get('名称', ''),
                "price": float(row.get('最新价', 0)),
                "change_pct": float(row.get('涨跌幅', 0)),
                "change_amount": float(row.get('涨跌额', 0)),
                "volume": int(row.get('成交量', 0)),
                "turnover": float(row.get('成交额', 0)),
                "high": float(row.get('最高', 0)),
                "low": float(row.get('最低', 0)),
                "open": float(row.get('今开', 0)),
                "pre_close": float(row.get('昨收', 0)),
                "volume_ratio": float(row.get('量比', 1)),
                "turnover_rate": float(row.get('换手率', 0)),
                "pe": float(row.get('市盈率-动态', 0)),
                "pb": float(row.get('市净率', 0)),
                "market_cap": float(row.get('总市值', 0)),
                "circulating_cap": float(row.get('流通市值', 0))
            }
        except Exception as e:
            print(f"获取股票 {symbol} 行情失败: {e}")
            return None
    
    def get_stock_fund_flow(self, symbol: str) -> Optional[Dict]:
        """
        获取个股资金流向
        
        Args:
            symbol: 股票代码
        
        Returns:
            dict: 资金流向数据
        """
        try:
            df = self.ak.stock_individual_fund_flow(stock=symbol)
            if df.empty:
                return None
            
            # 取最新数据
            latest = df.iloc[0]
            return {
                "main_force_inflow": float(latest.get('主力净流入', 0)),
                "main_force_ratio": float(latest.get('主力净流入占比', 0)),
                "retail_inflow": float(latest.get('散户净流入', 0)),
                "retail_ratio": float(latest.get('散户净流入占比', 0)),
                "super_large_inflow": float(latest.get('超大单净流入', 0)),
                "large_inflow": float(latest.get('大单净流入', 0)),
                "medium_inflow": float(latest.get('中单净流入', 0)),
                "small_inflow": float(latest.get('小单净流入', 0))
            }
        except Exception as e:
            print(f"获取股票 {symbol} 资金流向失败: {e}")
            return None
    
    def get_stock_history(self, symbol: str, days: int = 60) -> pd.DataFrame:
        """
        获取个股历史行情
        
        Args:
            symbol: 股票代码
            days: 历史天数
        
        Returns:
            DataFrame: 历史数据
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days + 20)  # 多取一些数据用于计算
            
            df = self.ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
                adjust="qfq"
            )
            
            return df
        except Exception as e:
            print(f"获取股票 {symbol} 历史数据失败: {e}")
            return pd.DataFrame()
    
    def get_leader_stocks_data(self, symbols: List[str]) -> List[Dict]:
        """
        获取多只股票的综合数据
        
        Args:
            symbols: 股票代码列表
        
        Returns:
            list: 各股票综合数据
        """
        results = []
        
        for symbol in symbols:
            print(f"  获取 {symbol} 数据...")
            
            # 实时行情
            spot = self.get_stock_spot(symbol)
            if not spot:
                continue
            
            # 历史数据及技术指标
            history = self.get_stock_history(symbol, days=60)
            indicators = calculate_all_indicators(history) if not history.empty else {}
            
            # 资金流向
            fund_flow = self.get_stock_fund_flow(symbol)
            
            stock_data = {
                "code": symbol,
                "name": spot.get("name", ""),
                "price": spot.get("price", 0),
                "change_pct": spot.get("change_pct", 0),
                "volume": spot.get("volume", 0),
                "turnover": spot.get("turnover", 0),
                "volume_ratio": spot.get("volume_ratio", 1),
                "turnover_rate": spot.get("turnover_rate", 0),
                "market_cap": spot.get("market_cap", 0),
                "indicators": indicators,
                "fund_flow": fund_flow or {}
            }
            
            results.append(stock_data)
            time.sleep(0.5)  # 避免请求过快
        
        return results
    
    def get_industry_full_data(self, industry_name: str, leader_codes: List[str]) -> Dict:
        """
        获取行业完整数据（板块行情+龙头股数据）
        
        Args:
            industry_name: 行业名称
            leader_codes: 龙头股代码列表
        
        Returns:
            dict: 行业完整数据
        """
        print(f"正在采集 {industry_name} 行业数据...")
        
        # 1. 获取板块行情
        sector_data = self.get_sector_by_name(industry_name)
        
        # 2. 获取龙头股数据
        print(f"获取 {len(leader_codes)} 只龙头股数据...")
        leaders_data = self.get_leader_stocks_data(leader_codes)
        
        # 3. 计算板块整体指标
        avg_change = sum(l.get("change_pct", 0) for l in leaders_data) / len(leaders_data) if leaders_data else 0
        total_volume = sum(l.get("volume", 0) for l in leaders_data)
        total_turnover = sum(l.get("turnover", 0) for l in leaders_data)
        
        # 4. 统计涨跌分布
        rise_count = sum(1 for l in leaders_data if l.get("change_pct", 0) > 0)
        fall_count = sum(1 for l in leaders_data if l.get("change_pct", 0) < 0)
        
        return {
            "industry_name": industry_name,
            "collect_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sector_data": sector_data or {},
            "leaders": leaders_data,
            "summary": {
                "avg_change_pct": round(avg_change, 2),
                "total_volume": total_volume,
                "total_turnover": round(total_turnover, 2),
                "rise_count": rise_count,
                "fall_count": fall_count,
                "flat_count": len(leaders_data) - rise_count - fall_count
            }
        }


def test_collector():
    """测试数据采集"""
    collector = MarketDataCollector()
    
    print("=" * 60)
    print("行情数据采集测试")
    print("=" * 60)
    
    # 测试1: 获取板块行情
    print("\n【测试1】获取板块行情")
    sectors = ["半导体", "电力", "银行", "医药"]
    for sector in sectors:
        data = collector.get_sector_by_name(sector)
        if data:
            print(f"  {data['name']}: 涨跌幅 {data['change_pct']:.2f}%, 成交额 {data['turnover']/1e8:.2f}亿")
        else:
            print(f"  {sector}: 未找到数据")
    
    # 测试2: 获取个股行情
    print("\n【测试2】获取个股行情")
    stocks = ["300308", "600519", "000858"]
    for symbol in stocks:
        data = collector.get_stock_spot(symbol)
        if data:
            print(f"  {data['name']}({symbol}): 价格 {data['price']:.2f}, 涨跌幅 {data['change_pct']:.2f}%")
        else:
            print(f"  {symbol}: 未找到数据")
    
    # 测试3: 获取龙头股完整数据
    print("\n【测试3】获取行业完整数据")
    industry_data = collector.get_industry_full_data("光模块", ["300308", "300394", "300502"])
    
    print(f"\n行业: {industry_data['industry_name']}")
    print(f"采集时间: {industry_data['collect_time']}")
    
    if industry_data['sector_data']:
        s = industry_data['sector_data']
        print(f"\n板块行情:")
        print(f"  名称: {s['name']}")
        print(f"  涨跌幅: {s['change_pct']:.2f}%")
        print(f"  成交额: {s['turnover']/1e8:.2f}亿")
    
    print(f"\n龙头股数据 ({len(industry_data['leaders'])} 只):")
    for leader in industry_data['leaders']:
        print(f"  {leader['name']}({leader['code']}): "
              f"价格 {leader['price']:.2f}, "
              f"涨跌幅 {leader['change_pct']:.2f}%, "
              f"量比 {leader['volume_ratio']:.2f}")
        if 'indicators' in leader and 'trend' in leader['indicators']:
            print(f"    趋势: {leader['indicators']['trend']}, RSI: {leader['indicators'].get('rsi', 'N/A')}")
    
    print(f"\n汇总:")
    summary = industry_data['summary']
    print(f"  平均涨跌幅: {summary['avg_change_pct']:.2f}%")
    print(f"  上涨/下跌: {summary['rise_count']}/{summary['fall_count']}")
    print(f"  总成交额: {summary['total_turnover']/1e8:.2f}亿")
    
    print("\n" + "=" * 60)
    print("测试完成")
    
    return industry_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="行情数据采集工具")
    parser.add_argument("--test", action="store_true", help="运行测试")
    parser.add_argument("--industry", type=str, help="行业名称")
    parser.add_argument("--leaders", type=str, help="龙头股代码，逗号分隔")
    parser.add_argument("--output", type=str, help="输出文件路径")
    
    args = parser.parse_args()
    
    if args.test:
        test_collector()
    elif args.industry:
        collector = MarketDataCollector()
        leaders = args.leaders.split(",") if args.leaders else []
        data = collector.get_industry_full_data(args.industry, leaders)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存至: {args.output}")
        else:
            print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print("行情数据采集模块")
        print("使用 --test 运行测试")
        print("使用 --industry 行业名 --leaders 代码1,代码2 采集特定行业数据")
