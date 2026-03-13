# AKShare 技术指标计算指南

> RSI、MACD、均线等技术指标计算说明

## 技术指标列表

| 指标 | 周期 | 用途 | 信号 |
|------|------|------|------|
| RSI | 14日 | 判断超买超卖 | >70超买, <30超卖 |
| MACD | 12,26,9 | 趋势判断 | 金叉看涨, 死叉看跌 |
| MA | 5/10/20/60日 | 趋势支撑 | 多头排列看涨 |
| BOLL | 20日 | 波动区间 | 触及上轨可能回调 |
| KDJ | 9,3,3 | 短线买卖 | K>D超买, K<D超卖 |
| 成交量比 | 5日平均 | 量能判断 | >1.5放量, <0.5缩量 |

---

## 1. RSI 相对强弱指数

### 计算公式

```
RSI = 100 - (100 / (1 + RS))
RS = 平均上涨幅度 / 平均下跌幅度

周期：14日
```

### Python实现

```python
import pandas as pd
import numpy as np

def calculate_rsi(prices, period=14):
    """
    计算RSI指标
    
    Args:
        prices: 收盘价序列 (list或pandas.Series)
        period: 计算周期，默认14
    
    Returns:
        RSI值 (0-100)
    """
    deltas = pd.Series(prices).diff()
    gain = deltas.where(deltas > 0, 0)
    loss = -deltas.where(deltas < 0, 0)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50

# 使用示例
data = ak.stock_zh_a_hist(symbol="300308", period="daily", 
                         start_date="20250101", adjust="qfq")
rsi = calculate_rsi(data['收盘'])
print(f"RSI(14): {rsi:.2f}")
```

### 信号判断

| RSI值 | 状态 | 操作建议 |
|-------|------|----------|
| > 80 | 严重超买 | 警惕回调 |
| 70-80 | 超买 | 考虑减仓 |
| 50-70 | 强势 | 持有 |
| 30-50 | 弱势 | 观望 |
| 20-30 | 超卖 | 考虑建仓 |
| < 20 | 严重超卖 | 关注反弹 |

---

## 2. MACD 异同移动平均线

### 计算公式

```
EMA12 = 12日指数移动平均
EMA26 = 26日指数移动平均
DIF = EMA12 - EMA26
DEA = DIF的9日指数移动平均
MACD = (DIF - DEA) * 2
```

### Python实现

```python
def calculate_macd(prices, fast=12, slow=26, signal=9):
    """
    计算MACD指标
    
    Args:
        prices: 收盘价序列
        fast: 快线周期，默认12
        slow: 慢线周期，默认26
        signal: 信号线周期，默认9
    
    Returns:
        dict: {dif, dea, macd, signal}
    """
    exp1 = prices.ewm(span=fast, adjust=False).mean()
    exp2 = prices.ewm(span=slow, adjust=False).mean()
    dif = exp1 - exp2
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd = (dif - dea) * 2
    
    # 判断信号
    latest_dif = dif.iloc[-1]
    latest_dea = dea.iloc[-1]
    prev_dif = dif.iloc[-2] if len(dif) > 1 else latest_dif
    prev_dea = dea.iloc[-2] if len(dea) > 1 else latest_dea
    
    signal_type = "neutral"
    if latest_dif > latest_dea and prev_dif <= prev_dea:
        signal_type = "golden_cross"  # 金叉
    elif latest_dif < latest_dea and prev_dif >= prev_dea:
        signal_type = "death_cross"   # 死叉
    elif latest_dif > latest_dea:
        signal_type = "bullish"       # 多头
    else:
        signal_type = "bearish"       # 空头
    
    return {
        "dif": round(latest_dif, 4),
        "dea": round(latest_dea, 4),
        "macd": round(macd.iloc[-1], 4),
        "signal": signal_type
    }
```

### 信号判断

| 信号 | 条件 | 含义 |
|------|------|------|
| 金叉 | DIF上穿DEA | 买入信号 |
| 死叉 | DIF下穿DEA | 卖出信号 |
| 多头 | DIF > DEA且>0 | 强势上涨 |
| 空头 | DIF < DEA且<0 | 弱势下跌 |
| 背离 | 价格新高MACD未新高 | 可能反转 |

---

## 3. 移动平均线 MA

### 计算公式

```
MA(n) = (P1 + P2 + ... + Pn) / n
Pn: 第n日的收盘价
```

### Python实现

```python
def calculate_ma(prices, periods=[5, 10, 20, 60]):
    """
    计算多周期移动平均线
    
    Args:
        prices: 收盘价序列
        periods: 周期列表，默认[5,10,20,60]
    
    Returns:
        dict: {周期: MA值}
    """
    result = {}
    for period in periods:
        ma = prices.rolling(window=period).mean()
        result[f"ma{period}"] = round(ma.iloc[-1], 2)
    
    # 判断均线排列
    latest_price = prices.iloc[-1]
    ma5 = result.get("ma5", 0)
    ma10 = result.get("ma10", 0)
    ma20 = result.get("ma20", 0)
    
    arrangement = "neutral"
    if latest_price > ma5 > ma10 > ma20:
        arrangement = "bullish"  # 多头排列
    elif latest_price < ma5 < ma10 < ma20:
        arrangement = "bearish"  # 空头排列
    
    result["arrangement"] = arrangement
    return result
```

### 均线排列判断

| 排列 | 条件 | 趋势判断 |
|------|------|----------|
| 多头排列 | 股价>MA5>MA10>MA20 | 强势上涨 |
| 空头排列 | 股价<MA5<MA10<MA20 | 弱势下跌 |
| 整理 | 均线缠绕 | 震荡整理 |
| 金叉 | 短期均线上穿长期均线 | 趋势转强 |
| 死叉 | 短期均线下穿长期均线 | 趋势转弱 |

---

## 4. 布林带 BOLL

### 计算公式

```
中轨 = 20日简单移动平均
上轨 = 中轨 + 2 * 20日标准差
下轨 = 中轨 - 2 * 20日标准差
```

### Python实现

```python
def calculate_boll(prices, period=20, std_dev=2):
    """
    计算布林带指标
    
    Args:
        prices: 收盘价序列
        period: 计算周期，默认20
        std_dev: 标准差倍数，默认2
    
    Returns:
        dict: {upper, middle, lower, position}
    """
    middle = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    
    upper = middle + std_dev * std
    lower = middle - std_dev * std
    
    latest_price = prices.iloc[-1]
    latest_upper = upper.iloc[-1]
    latest_lower = lower.iloc[-1]
    
    # 判断位置
    if latest_price >= latest_upper:
        position = "upper"
    elif latest_price <= latest_lower:
        position = "lower"
    else:
        position = "middle"
    
    return {
        "upper": round(latest_upper, 2),
        "middle": round(middle.iloc[-1], 2),
        "lower": round(latest_lower, 2),
        "position": position,
        "width": round((latest_upper - latest_lower) / middle.iloc[-1] * 100, 2)
    }
```

---

## 5. KDJ 随机指标

### 计算公式

```
RSV = (当日收盘价 - N日内最低价) / (N日内最高价 - N日内最低价) * 100
K = 2/3 * 前日K + 1/3 * 当日RSV
D = 2/3 * 前日D + 1/3 * 当日K
J = 3 * K - 2 * D

默认参数: N=9, K=3, D=3
```

### Python实现

```python
def calculate_kdj(df, n=9, m1=3, m2=3):
    """
    计算KDJ指标
    
    Args:
        df: DataFrame，包含['high', 'low', 'close']
        n: RSV周期，默认9
        m1: K平滑系数，默认3
        m2: D平滑系数，默认3
    
    Returns:
        dict: {k, d, j, signal}
    """
    low_list = df['low'].rolling(window=n, min_periods=n).min()
    high_list = df['high'].rolling(window=n, min_periods=n).max()
    rsv = (df['close'] - low_list) / (high_list - low_list) * 100
    
    k = rsv.ewm(com=m1-1, adjust=False).mean()
    d = k.ewm(com=m2-1, adjust=False).mean()
    j = 3 * k - 2 * d
    
    latest_k = k.iloc[-1]
    latest_d = d.iloc[-1]
    latest_j = j.iloc[-1]
    
    # 信号判断
    signal = "neutral"
    if latest_k > 80 and latest_d > 80:
        signal = "overbought"
    elif latest_k < 20 and latest_d < 20:
        signal = "oversold"
    elif k.iloc[-1] > d.iloc[-1] and k.iloc[-2] <= d.iloc[-2]:
        signal = "golden_cross"
    elif k.iloc[-1] < d.iloc[-1] and k.iloc[-2] >= d.iloc[-2]:
        signal = "death_cross"
    
    return {
        "k": round(latest_k, 2),
        "d": round(latest_d, 2),
        "j": round(latest_j, 2),
        "signal": signal
    }
```

---

## 6. 成交量比

### 计算公式

```
成交量比 = 当日成交量 / 近5日平均成交量
```

### Python实现

```python
def calculate_volume_ratio(volumes):
    """
    计算成交量比
    
    Args:
        volumes: 成交量序列
    
    Returns:
        dict: {ratio, signal}
    """
    latest_volume = volumes.iloc[-1]
    avg_volume = volumes.tail(5).mean()
    
    ratio = latest_volume / avg_volume if avg_volume > 0 else 1
    
    if ratio > 2:
        signal = "extreme_high"  # 极度放量
    elif ratio > 1.5:
        signal = "high"          # 明显放量
    elif ratio > 1.2:
        signal = "mild_high"     # 温和放量
    elif ratio < 0.5:
        signal = "extreme_low"   # 极度缩量
    elif ratio < 0.8:
        signal = "low"           # 明显缩量
    else:
        signal = "normal"        # 正常
    
    return {
        "ratio": round(ratio, 2),
        "signal": signal
    }
```

---

## 综合技术指标分析

### 综合判断函数

```python
def analyze_technical_indicators(df):
    """
    综合分析所有技术指标
    
    Args:
        df: DataFrame，包含['open', 'high', 'low', 'close', 'volume']
    
    Returns:
        dict: 综合分析结果
    """
    rsi = calculate_rsi(df['close'])
    macd = calculate_macd(df['close'])
    ma = calculate_ma(df['close'])
    boll = calculate_boll(df['close'])
    volume = calculate_volume_ratio(df['volume'])
    
    # 综合评分 (0-100)
    score = 50
    
    # RSI评分
    if rsi > 70: score -= 10
    elif rsi < 30: score += 10
    
    # MACD评分
    if macd['signal'] == 'golden_cross': score += 15
    elif macd['signal'] == 'death_cross': score -= 15
    elif macd['signal'] == 'bullish': score += 5
    
    # 均线评分
    if ma['arrangement'] == 'bullish': score += 10
    elif ma['arrangement'] == 'bearish': score -= 10
    
    # 量能评分
    if volume['signal'] in ['high', 'extreme_high'] and df['close'].iloc[-1] > df['close'].iloc[-2]:
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
        "volume": volume,
        "score": score,
        "trend": trend
    }
```

---

## 注意事项

1. **数据完整性**: 技术指标需要足够的历史数据，建议至少60个交易日
2. **复权处理**: 计算前需进行前复权处理，避免除权除息影响
3. **滞后性**: 技术指标有滞后性，不能预测只能跟随
4. **组合使用**: 单一指标容易失效，建议多指标组合判断
5. **市场环境**: 不同市场环境（牛/熊/震荡）指标有效性不同
