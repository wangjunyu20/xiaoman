#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术指标计算工具
提供RSI、MACD、均线、布林带等技术指标计算
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Union, Optional


def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    """
    计算RSI相对强弱指数
    
    Args:
        prices: 收盘价序列
        period: 计算周期，默认14
    
    Returns:
        RSI值 (0-100)
    """
    deltas = prices.diff()
    gain = deltas.where(deltas > 0, 0)
    loss = -deltas.where(deltas < 0, 0)
    
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    
    last_rsi = rsi.iloc[-1]
    return round(last_rsi, 2) if not pd.isna(last_rsi) else 50.0


def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
    """
    计算MACD指标
    
    Args:
        prices: 收盘价序列
        fast: 快线周期
        slow: 慢线周期
        signal: 信号线周期
    
    Returns:
        dict: {dif, dea, macd, signal}
    """
    exp1 = prices.ewm(span=fast, adjust=False).mean()
    exp2 = prices.ewm(span=slow, adjust=False).mean()
    dif = exp1 - exp2
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd_line = (dif - dea) * 2
    
    # 判断信号
    latest_dif = dif.iloc[-1]
    latest_dea = dea.iloc[-1]
    
    if len(dif) > 1 and len(dea) > 1:
        prev_dif = dif.iloc[-2]
        prev_dea = dea.iloc[-2]
        
        if latest_dif > latest_dea and prev_dif <= prev_dea:
            signal_type = "golden_cross"  # 金叉
        elif latest_dif < latest_dea and prev_dif >= prev_dea:
            signal_type = "death_cross"   # 死叉
        elif latest_dif > latest_dea:
            signal_type = "bullish"       # 多头
        else:
            signal_type = "bearish"       # 空头
    else:
        signal_type = "neutral"
    
    return {
        "dif": round(float(latest_dif), 4),
        "dea": round(float(latest_dea), 4),
        "macd": round(float(macd_line.iloc[-1]), 4),
        "signal": signal_type
    }


def calculate_ma(prices: pd.Series, periods: List[int] = None) -> Dict:
    """
    计算移动平均线
    
    Args:
        prices: 收盘价序列
        periods: 周期列表，默认[5,10,20,60]
    
    Returns:
        dict: 各周期MA值及排列状态
    """
    if periods is None:
        periods = [5, 10, 20, 60]
    
    result = {}
    for period in periods:
        if len(prices) >= period:
            ma = prices.rolling(window=period).mean().iloc[-1]
            result[f"ma{period}"] = round(float(ma), 2)
        else:
            result[f"ma{period}"] = None
    
    # 判断均线排列
    latest_price = prices.iloc[-1]
    ma5 = result.get("ma5")
    ma10 = result.get("ma10")
    ma20 = result.get("ma20")
    
    if ma5 and ma10 and ma20:
        if latest_price > ma5 > ma10 > ma20:
            arrangement = "bullish"  # 多头排列
        elif latest_price < ma5 < ma10 < ma20:
            arrangement = "bearish"  # 空头排列
        else:
            arrangement = "neutral"
    else:
        arrangement = "insufficient_data"
    
    result["arrangement"] = arrangement
    return result


def calculate_boll(prices: pd.Series, period: int = 20, std_dev: float = 2.0) -> Dict:
    """
    计算布林带
    
    Args:
        prices: 收盘价序列
        period: 计算周期
        std_dev: 标准差倍数
    
    Returns:
        dict: 布林带数据
    """
    if len(prices) < period:
        return {"upper": None, "middle": None, "lower": None, "position": "unknown", "width": 0}
    
    middle = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    
    upper = middle + std_dev * std
    lower = middle - std_dev * std
    
    latest_price = float(prices.iloc[-1])
    latest_upper = float(upper.iloc[-1])
    latest_lower = float(lower.iloc[-1])
    latest_middle = float(middle.iloc[-1])
    
    # 判断位置
    if latest_price >= latest_upper:
        position = "upper"
    elif latest_price <= latest_lower:
        position = "lower"
    else:
        position = "middle"
    
    width = (latest_upper - latest_lower) / latest_middle * 100 if latest_middle > 0 else 0
    
    return {
        "upper": round(latest_upper, 2),
        "middle": round(latest_middle, 2),
        "lower": round(latest_lower, 2),
        "position": position,
        "width": round(width, 2)
    }


def calculate_volume_ratio(volumes: pd.Series, period: int = 5) -> Dict:
    """
    计算成交量比
    
    Args:
        volumes: 成交量序列
        period: 平均周期
    
    Returns:
        dict: 量比及信号
    """
    if len(volumes) < period:
        return {"ratio": 1.0, "signal": "normal"}
    
    latest_volume = float(volumes.iloc[-1])
    avg_volume = float(volumes.tail(period).mean())
    
    ratio = latest_volume / avg_volume if avg_volume > 0 else 1.0
    
    if ratio > 2.5:
        signal = "extreme_high"
    elif ratio > 1.5:
        signal = "high"
    elif ratio > 1.2:
        signal = "mild_high"
    elif ratio < 0.4:
        signal = "extreme_low"
    elif ratio < 0.7:
        signal = "low"
    else:
        signal = "normal"
    
    return {
        "ratio": round(ratio, 2),
        "signal": signal
    }


def calculate_all_indicators(df: pd.DataFrame) -> Dict:
    """
    计算所有技术指标
    
    Args:
        df: DataFrame，包含['open', 'high', 'low', 'close', 'volume']
    
    Returns:
        dict: 所有指标结果
    """
    if df.empty or len(df) < 20:
        return {
            "error": "数据不足，需要至少20个交易日数据",
            "rsi": 50,
            "macd": {"signal": "neutral"},
            "ma": {"arrangement": "insufficient_data"},
            "boll": {},
            "volume": {}
        }
    
    # 标准化列名
    df = df.copy()
    column_map = {
        '收盘': 'close', 'close': 'close',
        '开盘': 'open', 'open': 'open',
        '最高': 'high', 'high': 'high',
        '最低': 'low', 'low': 'low',
        '成交量': 'volume', 'volume': 'volume'
    }
    df.columns = [column_map.get(str(c).lower(), c) for c in df.columns]
    
    close_prices = df['close']
    volumes = df['volume']
    
    # 计算各指标
    rsi = calculate_rsi(close_prices)
    macd = calculate_macd(close_prices)
    ma = calculate_ma(close_prices)
    boll = calculate_boll(close_prices)
    vol_ratio = calculate_volume_ratio(volumes)
    
    # 综合评分
    score = 50
    
    # RSI评分
    if rsi > 70:
        score -= 10
    elif rsi < 30:
        score += 10
    
    # MACD评分
    if macd['signal'] == 'golden_cross':
        score += 15
    elif macd['signal'] == 'death_cross':
        score -= 15
    elif macd['signal'] == 'bullish':
        score += 5
    
    # 均线评分
    if ma['arrangement'] == 'bullish':
        score += 10
    elif ma['arrangement'] == 'bearish':
        score -= 10
    
    # 量能评分
    if vol_ratio['signal'] in ['high', 'extreme_high'] and len(close_prices) > 1:
        if close_prices.iloc[-1] > close_prices.iloc[-2]:
            score += 10  # 放量上涨
    
    score = max(0, min(100, score))
    
    # 趋势判断
    if score >= 70:
        trend = "strong_bullish"
    elif score >= 55:
        trend = "bullish"
    elif score >= 45:
        trend = "neutral"
    elif score >= 30:
        trend = "bearish"
    else:
        trend = "strong_bearish"
    
    return {
        "rsi": rsi,
        "macd": macd,
        "ma": ma,
        "boll": boll,
        "volume": vol_ratio,
        "score": score,
        "trend": trend
    }


def analyze_stock_indicators(symbol: str, days: int = 60) -> Dict:
    """
    分析单个股票的技术指标
    
    Args:
        symbol: 股票代码
        days: 获取历史数据天数
    
    Returns:
        dict: 指标分析结果
    """
    try:
        import akshare as ak
        
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.Timedelta(days=days)
        
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
            adjust="qfq"
        )
        
        if df.empty:
            return {"error": f"无法获取股票 {symbol} 的数据"}
        
        indicators = calculate_all_indicators(df)
        
        # 添加最新价格信息
        latest = df.iloc[-1]
        indicators['latest_price'] = float(latest['收盘'])
        indicators['change_pct'] = float(latest['涨跌幅'])
        
        return indicators
        
    except Exception as e:
        return {"error": f"分析失败: {str(e)}"}


# 测试代码
if __name__ == "__main__":
    print("技术指标计算工具测试")
    print("=" * 50)
    
    # 测试数据
    test_prices = pd.Series([10, 11, 12, 11.5, 13, 14, 13.5, 15, 14.5, 16] * 3)
    test_volumes = pd.Series([1000, 1200, 1100, 1300, 1500, 1400, 1600, 1800, 1700, 1900] * 3)
    
    print(f"\n测试价格序列: {len(test_prices)} 个数据点")
    
    # 测试RSI
    rsi = calculate_rsi(test_prices)
    print(f"\nRSI(14): {rsi}")
    
    # 测试MACD
    macd = calculate_macd(test_prices)
    print(f"\nMACD:")
    print(f"  DIF: {macd['dif']}")
    print(f"  DEA: {macd['dea']}")
    print(f"  MACD: {macd['macd']}")
    print(f"  Signal: {macd['signal']}")
    
    # 测试MA
    ma = calculate_ma(test_prices)
    print(f"\n移动平均线:")
    for k, v in ma.items():
        print(f"  {k}: {v}")
    
    # 测试布林带
    boll = calculate_boll(test_prices)
    print(f"\n布林带:")
    print(f"  上轨: {boll['upper']}")
    print(f"  中轨: {boll['middle']}")
    print(f"  下轨: {boll['lower']}")
    print(f"  位置: {boll['position']}")
    
    # 测试成交量比
    vol = calculate_volume_ratio(test_volumes)
    print(f"\n成交量比: {vol['ratio']} ({vol['signal']})")
    
    print("\n" + "=" * 50)
    print("测试完成")
