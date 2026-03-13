---
name: market-sentiment-analyzer
description: |
  行业行情与舆情分析器 — 采集行业行情走势，分析舆情情绪，推导走势背后的原因。
  用于：(1)分析行业涨跌原因 (2)识别影响行业的宏观/政策因素 (3)生成行情走势解读。
  被industry-research-report调用以丰富报告的行情分析维度。
allowed-tools:
  - Bash(python:*)
  - kimi_search
  - kimi_fetch
user-invocable: true
---

# 行业行情与舆情分析器

## 核心功能

1. **行情数据采集** - 获取行业板块和龙头股行情
2. **舆情情绪分析** - 采集新闻和社媒情绪
3. **走势原因推导** - 关联行情与舆情，生成原因分析

## 快速开始

### 独立分析

```bash
cd /root/.openclaw/workspace_investment/skills/market-sentiment-analyzer

# 分析光模块行情
python3 scripts/analyze.py --industry "光模块" --days 7
```

### 被行业报告调用

```python
import sys
sys.path.insert(0, '/root/.openclaw/workspace_investment/skills/market-sentiment-analyzer/scripts')

from analyze import MarketSentimentAnalyzer

analyzer = MarketSentimentAnalyzer()
result = analyzer.analyze(industry="光模块", days=7)
```

---

## 数据源说明（重要）

### 与"行业资讯"模块的区别

| 维度 | 本模块（舆情分析） | 行业资讯模块 |
|------|-------------------|-------------|
| **数据来源** | 东方财富股吧、社媒 | 财联社、新浪财经 |
| **内容特点** | 散户讨论、情绪化 | 官方报道、理性 |
| **情感倾向** | 可能偏负面（下跌时骂声多） | 可能偏正面（报道技术突破） |
| **用途** | 反映短期市场情绪 | 反映长期行业趋势 |

### 为什么两者可能不一致？

**典型场景**：光模块板块今日下跌3%
- **股吧舆情**："垃圾板块，又跌了！""主力出货了！" → **负面**
- **官方资讯**："1.6T光模块商用启动""中际旭创业绩翻倍" → **利好**

**这不是BUG，是正常现象**：
- 短期情绪（股吧）与长期价值（资讯）本就不同
- 两者结合才能全面判断市场

### 在报告中的呈现方式

```
📊 市场情绪分析（本模块数据）
├── 社媒情绪指数：35/100（偏谨慎）
├── 关键词：回调、出货、观望
└── 来源：东方财富股吧

📰 行业资讯（行业资讯模块数据）
├── 利好：2条（技术突破、业绩预增）
├── 中性：1条（行业动态）
└── 来源：财联社、新浪财经
```

---

## 输出字段说明

```json
{
  "industry": "光模块",
  "date": "2026-03-12",
  "market_data": {
    "latest_close": 557.00,
    "change_pct": -2.5,
    "rsi": 45,
    "trend": "震荡"
  },
  "sentiment": {
    "source": "东方财富股吧",
    "posts_count": 156,
    "negative_ratio": 0.65,
    "sentiment_label": "偏负面",
    "keywords": ["回调", "出货", "观望"]
  },
  "reasoning": "板块今日下跌2.5%，RSI回落至45。股吧情绪偏负面，多讨论短期回调风险。但基本面未变，1.6T光模块商用稳步推进。",
  "risks": ["短期回调风险", "市场情绪波动"]
}
```

| 字段 | 说明 |
|------|------|
| `market_data` | 行情数据：收盘价、涨跌幅、RSI、趋势 |
| `sentiment.source` | 数据来源（东方财富股吧） |
| `sentiment.posts_count` | 采集的帖子数量 |
| `sentiment.negative_ratio` | 负面帖子占比 |
| `reasoning` | 走势原因分析 |
| `risks` | 识别的风险因素 |

---

## 支持的行业

- 光模块 / CPO
- 人形机器人 / 机器人
- 量子科技 / 量子计算
- AI应用 / 人工智能
- 脑机接口
- 低空经济
- 集成电路 / 芯片
- 算力

---

## 工作原理

### 行情数据采集
- 使用AKShare获取东方财富概念板块行情
- 计算涨跌幅、成交量变化、RSI技术指标

### 舆情数据采集
- 爬取东方财富股吧帖子
- 统计情绪倾向（正面/负面/中性）
- 提取高频关键词

**注意**：本模块**不采集**财联社/新浪等官方新闻，那些由`industry-research-report`的`news_fetcher`处理。

### 走势原因推导
- 关联技术指标与情绪数据
- 识别主力资金流向
- 生成自然语言分析

---

## 集成到行业报告

### 自动集成（推荐）

`industry-research-report`的`generate_reports.py`已自动调用本模块：

```python
# 在详情页生成过程中自动执行
from market-sentiment-analyzer.scripts.analyze import MarketSentimentAnalyzer

analyzer = MarketSentimentAnalyzer()
sentiment_result = analyzer.analyze(industry_name)

# 结果写入详情页HTML
```

### 手动集成

详见 [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)

---

## 故障排查

### 行情获取失败
**现象**: `行情获取失败: Connection aborted`

**原因**: 东方财富接口限流、网络不稳定

**解决**: 
- 自动降级到仅使用舆情分析
- 5分钟后重试

### 舆情数据为空
**现象**: `posts_count: 0`

**原因**: 该行业股吧讨论度低、网络问题

**解决**:
```python
# 使用更通用的关键词
result = analyzer.analyze("CPO")  # 代替 "光模块"
result = analyzer.analyze("机器人")  # 代替 "人形机器人"
```

---

## 参考文档

| 文档 | 说明 |
|------|------|
| [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) | 集成到行业报告的详细指南 |
| [行业研究报告SKILL](../industry-research-report/SKILL.md) | 主报告生成模块 |
| [AKShare文档](https://www.akshare.xyz/) | 行情数据源文档 |

---

## 更新记录

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.1.0 | 2026-03-12 | 新增数据源说明，明确与行业资讯的区别 |
| 1.0.0 | 2026-03-09 | 初始版本，支持行情+舆情+原因推导 |

---

**重要提示**：
本模块的舆情数据（股吧）与`industry-research-report`的行业资讯（官方媒体）是**互补关系**，不是重复关系。两者差异反映的是**短期情绪vs长期价值**的不同视角。
