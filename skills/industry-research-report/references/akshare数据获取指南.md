---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022100ce73d10008e6a35bfc07cb035cc5811e179b4c2f60f283599ee4589edfd89bc802207ed849448ac5e64658491a2190e15707941f61fa1304bde814acdc52dadc19b2
    ReservedCode2: 3044022044d3ab8def9d6fb84fd6d55f74df7bce0ced19c385e5943db959f7276cb0a38202204db1dc35a13435c31ecfc3cc0f94df92a6a8a22857b7215fdf12978081c220ca
---

# AKShare 数据获取指南

> A股/基金/指数数据获取手册

## 安装

```bash
pip install akshare pandas
```

## 常用数据接口

### 1. 行业板块行情

```python
import akshare as ak

# 行业板块涨跌榜
df = ak.stock_sector_spot_em()
print(df.head(10))
```

返回字段：代码、名称、涨跌幅、涨跌额、成交量、成交额

---

### 2. 个股实时行情

```python
# A股实时行情
df = ak.stock_zh_a_spot_em()

# 筛选个股
stock = df[df['代码'] == '600519']  # 贵州茅台
print(stock)
```

返回字段：代码、名称、实时价格、涨跌幅、涨跌额、成交量、成交额、买卖盘等

---

### 3. 指数行情

```python
# 大盘指数行情
df = ak.index_zh_a_spot_em()

# 上证指数
sh = df[df['代码'] == '000001']
print(sh)
```

---

### 4. 基金净值

```python
# 场外基金历史净值
df = ak.fund_zh_a_hist(
    symbol="161039",  # 基金代码
    period="daily",   # 日线
    start_date="20250101",
    end_date="20251231"
)

print(df.tail())  # 最新净值
```

---

### 5. 融资融券

```python
# 融资融券数据
df = ak.stock_margin_detail(symbol="600519")
print(df)
```

---

### 6. 龙虎榜

```python
# 每日龙虎榜
df = ak.stock_lhb_detail_em()
print(df.head())
```

---

### 7. 资金流向

```python
# 单日资金流向
df = ak.stock_individual_fund_flow(stock="600519")
print(df)
```

---

## 快速命令

```bash
# 获取行业板块行情
python scripts/akshare_data.py stock_industry

# 获取指数行情
python scripts/akshare_data.py index_spot

# 获取基金净值
python scripts/akshare_data.py fund_nav
```

---

## 注意事项

1. **数据延迟**：akshare 数据可能有几分钟延迟，不适合高频交易
2. **频率限制**：请求过快可能被限制，适当添加延时
3. **数据格式**：返回多为 Pandas DataFrame，需要转换为 JSON
4. **网络问题**：数据源可能不稳定，需要添加异常处理

---

## 错误处理

```python
import akshare as ak
import time

def get_with_retry(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            print(f"第{i+1}次失败: {e}")
            time.sleep(2)
    return None
```

---

*AKShare 是开源项目，数据仅供研究参考，不构成投资建议*
