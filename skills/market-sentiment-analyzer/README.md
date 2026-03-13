# 市场舆情分析系统 - 使用文档

## 系统概述

市场舆情分析系统实现了：
1. **概述版**: 3-5句话总结行业舆情（用于报告首页）
2. **详情版**: 完整的5层因果分析文字（用于详情页顶部）
3. **数据存储**: SQLite数据库存储分析结果
4. **API接口**: 对外暴露REST API供其他skill调用

## 快速开始

### 1. 获取单个行业概述（用于首页）

```python
from skills.market-sentiment-analyzer.api.sentiment_api import get_sentiment_summary

result = get_sentiment_summary('光模块', date='2026-03-09')

# 返回结果
{
    "status": "success",
    "data": {
        "industry": "光模块",
        "date": "2026-03-09",
        "change_pct": -4.36,
        "trend": "下跌",
        "sentiment_brief": "光模块板块今日下跌4.36%，主要受中东地缘政治危机影响...",
        "key_factors": ["地缘政治", "能源危机", "货币政策", "资金流出"],
        "risk_level": "高",
        "outlook_short": "短期关注中东局势演变..."
    }
}
```

### 2. 获取单个行业详情（用于详情页）

```python
from skills.market-sentiment-analyzer.api.sentiment_api import get_sentiment_detail

result = get_sentiment_detail('光模块', date='2026-03-09')

# 返回结果
{
    "status": "success",
    "data": {
        "industry": "光模块",
        "date": "2026-03-09",
        "change_pct": -4.36,
        "causal_analysis_full": "完整的5层因果分析文字...",
        "root_cause": "伊朗封锁霍尔木兹海峡",
        "key_events": [...],
        "data_sources": [...]
    }
}
```

### 3. 批量获取多个行业（用于生成完整报告）

```python
from skills.market-sentiment-analyzer.api.sentiment_api import get_sentiment_batch

industries = ['光模块', '算力', '人形机器人', '量子科技']
result = get_sentiment_batch(industries, date='2026-03-09', include_detail=True)

# 返回结果
{
    "status": "success",
    "date": "2026-03-09",
    "industries": [
        {
            "industry": "光模块",
            "summary": {...},  # 概述
            "detail": {...}    # 详情
        },
        ...
    ],
    "total": 4
}
```

## 数据结构设计

### 概述版数据结构（3-5句话）

```json
{
    "industry": "光模块",
    "date": "2026-03-09",
    "change_pct": -4.36,
    "trend": "下跌",
    "sentiment_brief": "光模块板块今日下跌4.36%，主要受中东地缘政治危机影响。伊朗封锁霍尔木兹海峡导致油价暴涨54%，推高通胀预期，市场担忧美联储维持高利率将压缩科技股估值。资金从AI板块流出，中际旭创遭净卖出超17亿元。",
    "key_factors": ["地缘政治", "能源危机", "货币政策", "资金流出"],
    "risk_level": "高",
    "outlook_short": "短期关注中东局势演变，中期等待估值回归合理区间"
}
```

### 详情版数据结构（完整文字）

```json
{
    "industry": "光模块",
    "date": "2026-03-09",
    "change_pct": -4.36,
    "volume_status": "放量下跌",
    "fund_flow": "主力净流出超17亿元",
    "leader_stocks": ["中际旭创", "天孚通信", "新易盛"],
    "causal_analysis_full": "第一步：地缘政治冲突爆发。2026年3月2日，伊朗宣布全面封锁霍尔木兹海峡...",
    "root_cause": "伊朗封锁霍尔木兹海峡",
    "key_events": [
        {"event": "伊朗封锁霍尔木兹海峡", "date": "2026-03-02", "source": "财新周刊"},
        {"event": "油价暴涨至108美元", "date": "2026-03-09", "source": "财新"}
    ],
    "data_sources": ["腾讯财经API", "财新周刊", "财联社"],
    "analysis_depth": 3,
    "verification_status": "已验证"
}
```

## 集成到投资分析skill

### 示例代码

```python
# 在投资分析skill中调用舆情分析API
from skills.market-sentiment-analyzer.api.sentiment_api import (
    get_sentiment_summary,
    get_sentiment_detail,
    get_sentiment_batch
)

def generate_industry_report(industry_name):
    """生成行业报告"""
    
    # 1. 获取概述（放在首页）
    summary = get_sentiment_summary(industry_name)
    if summary['status'] == 'success':
        report_summary = summary['data']['sentiment_brief']
        
    # 2. 获取详情（放在详情页顶部）
    detail = get_sentiment_detail(industry_name)
    if detail['status'] == 'success':
        report_detail = detail['data']['causal_analysis_full']
        
    # 3. 整合到报告
    report = {
        'industry': industry_name,
        'summary': report_summary,  # 首页显示
        'detail': report_detail,    # 详情页显示
        'data_sources': detail['data']['data_sources']
    }
    
    return report

# 批量生成报告
def generate_all_reports(industry_list):
    """批量生成所有行业报告"""
    batch_result = get_sentiment_batch(industry_list, include_detail=True)
    
    reports = []
    for item in batch_result['industries']:
        reports.append({
            'industry': item['industry'],
            'summary': item['summary']['sentiment_brief'],
            'detail': item['detail']['causal_analysis_full'],
            'change_pct': item['summary']['change_pct']
        })
    
    return reports
```

## 文件结构

```
market-sentiment-analyzer/
├── database/
│   ├── schema.sql              # 数据库结构
│   └── sentiment.db            # SQLite数据库
├── storage/
│   └── db_manager.py           # 数据库管理
├── api/
│   └── sentiment_api.py        # API接口
├── output/deep_analysis/       # 分析报告
│   ├── 光模块_深度分析示例.md
│   ├── 算力_深度分析_完整版.md
│   └── 人形机器人_深度分析_完整版.md
└── 设计文档/
    ├── ARCHITECTURE.md         # 架构设计
    ├── COT_DESIGN_V2.md        # COT框架
    └── CAUSALITY_PRINCIPLES.md # 因果原理
```

## 已完成的分析行业

| 行业 | 涨跌 | 概述版 | 详情版 |
|-----|------|-------|-------|
| 光模块/CPO | -4.36% | ✅ | ✅ |
| 算力 | +2.45% | ✅ | ✅ |
| 人形机器人 | -1.20% | ✅ | ✅ |

## 后续扩展计划

1. **自动分析**: 定时任务自动分析所有监控行业
2. **更多行业**: 量子科技、脑机接口、低空经济等
3. **实时更新**: 盘中重大事件触发重新分析
4. **历史对比**: 保存历史分析，支持趋势对比

## 测试命令

```bash
# 测试API
cd /root/.openclaw/workspace_investment/skills/market-sentiment-analyzer
python3 api/sentiment_api.py
```

## 数据查看

```bash
# 查看数据库
sqlite3 database/sentiment.db "SELECT industry_name, change_pct, trend_summary FROM industry_sentiment_summary;"
```
