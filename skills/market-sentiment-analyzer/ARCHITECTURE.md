# 市场舆情分析系统 - 架构设计

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     市场舆情分析系统                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ 数据采集层  │  │  分析引擎   │  │    数据存储层       │ │
│  │             │  │             │  │                     │ │
│  │ - 腾讯行情  │→ │ - COT分析   │→ │ - SQLite数据库      │ │
│  │ - kimi搜索  │  │ - 因果推理  │  │ - 概述表            │ │
│  │ - 财联社    │  │ - 双向验证  │  │ - 详情表            │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                      API接口层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ /api/summary │  │ /api/detail  │  │ /api/batch   │      │
│  │ 获取概述     │  │ 获取详情     │  │ 批量获取     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     调用方 (投资分析skill)                    │
└─────────────────────────────────────────────────────────────┘
```

## 数据库设计

### 表结构

```sql
-- 行业舆情概述表 (用于报告首页)
CREATE TABLE industry_sentiment_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    industry_name VARCHAR(50) NOT NULL,      -- 行业名称
    analysis_date DATE NOT NULL,              -- 分析日期
    change_pct DECIMAL(5,2),                  -- 涨跌幅
    trend_summary VARCHAR(20),                -- 趋势概述 (上涨/下跌/震荡)
    sentiment_brief TEXT,                     -- 舆情概述 (3-5句话)
    key_factors TEXT,                         -- 核心驱动因素 (JSON数组)
    risk_level VARCHAR(10),                   -- 风险等级 (高/中/低)
    outlook_short VARCHAR(100),               -- 短期展望
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(industry_name, analysis_date)
);

-- 行业舆情详情表 (用于详情页)
CREATE TABLE industry_sentiment_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    industry_name VARCHAR(50) NOT NULL,      -- 行业名称
    analysis_date DATE NOT NULL,              -- 分析日期
    
    -- Layer 1: 表面现象
    market_data JSON,                         -- 行情数据
    volume_status VARCHAR(20),                -- 成交量状态
    fund_flow VARCHAR(50),                    -- 资金流向
    
    -- Layer 2: 直接驱动
    direct_factors TEXT,                      -- 直接驱动因素 (完整文字)
    key_events JSON,                          -- 关键事件列表
    
    -- Layer 3-4: 宏观与国际
    macro_environment TEXT,                   -- 宏观环境分析
    international_factors TEXT,               -- 国际形势分析
    
    -- Layer 5: 深度因果
    causal_chain_full TEXT,                   -- 完整因果链条 (大段文字)
    root_cause VARCHAR(200),                  -- 根本原因
    transmission_path TEXT,                   -- 传导路径
    
    -- 数据来源
    data_sources JSON,                        -- 数据来源列表
    
    -- 分析质量
    analysis_depth INTEGER,                   -- 分析深度 (1-4)
    verification_status VARCHAR(20),          -- 验证状态
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(industry_name, analysis_date)
);

-- 搜索日志表 (用于追踪分析过程)
CREATE TABLE search_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    industry_name VARCHAR(50),
    search_time TIMESTAMP,
    search_dimensions JSON,                   -- 搜索维度
    keywords_used JSON,                       -- 使用的关键词
    results_count INTEGER,                    -- 结果数量
    duration_seconds INTEGER,                 -- 耗时
    status VARCHAR(20)                        -- 状态
);
```

## API接口设计

### 1. 获取单个行业概述
```
GET /api/summary?industry={行业名}&date={日期}

Response:
{
    "industry": "光模块",
    "date": "2026-03-09",
    "change_pct": -4.36,
    "trend": "下跌",
    "sentiment_brief": "光模块板块今日下跌4.36%，主要受中东地缘政治危机影响。伊朗封锁霍尔木兹海峡导致油价暴涨54%，推高通胀预期，市场担忧美联储维持高利率将压缩科技股估值。资金从AI板块流出，中际旭创遭净卖出超17亿元。",
    "key_factors": ["地缘政治", "能源危机", "货币政策", "资金流出"],
    "risk_level": "高",
    "outlook_short": "短期关注中东局势演变和美联储政策动向"
}
```

### 2. 获取单个行业详情
```
GET /api/detail?industry={行业名}&date={日期}

Response:
{
    "industry": "光模块",
    "date": "2026-03-09",
    "layer1_surface": {
        "market_data": {...},
        "volume_status": "放量下跌",
        "fund_flow": "主力净流出17亿"
    },
    "layer2_direct": {
        "full_text": "完整的直接驱动因素分析...",
        "key_events": [...]
    },
    "layer3_macro": "完整的宏观环境分析...",
    "layer4_international": "完整的国际形势分析...",
    "layer5_causal": {
        "full_text": "完整的5层因果推导文字...",
        "root_cause": "伊朗封锁霍尔木兹海峡",
        "transmission_path": "油价→通胀→利率→估值→股价"
    },
    "data_sources": [...],
    "analysis_depth": 3,
    "verification_status": "已验证"
}
```

### 3. 批量获取多个行业
```
GET /api/batch?industries={行业1,行业2,行业3}&date={日期}&type={summary|detail|both}

Response:
{
    "date": "2026-03-09",
    "industries": [
        {"industry": "光模块", "summary": {...}, "detail": {...}},
        {"industry": "算力", "summary": {...}, "detail": {...}},
        {...}
    ],
    "total": 3,
    "generated_at": "2026-03-09T19:30:00"
}
```

### 4. 触发分析任务
```
POST /api/analyze

Body:
{
    "industries": ["光模块", "算力", "人形机器人"],
    "depth": 3,
    "force_update": false
}

Response:
{
    "task_id": "task_20260309_001",
    "status": "running",
    "estimated_completion": "2026-03-09T19:35:00",
    "industries_count": 3
}
```

## 实现计划

### Phase 1: 数据库和核心分析引擎
- [ ] 创建SQLite数据库和表结构
- [ ] 实现COT分析引擎
- [ ] 实现数据存储逻辑

### Phase 2: API接口
- [ ] 实现/summary接口
- [ ] 实现/detail接口
- [ ] 实现/batch接口
- [ ] 实现/analyze接口

### Phase 3: 自动化
- [ ] 定时任务自动分析
- [ ] 结果自动入库
- [ ] 对外暴露服务

### Phase 4: 集成测试
- [ ] 投资分析skill调用测试
- [ ] 性能优化
- [ ] 文档完善

## 文件结构

```
market-sentiment-analyzer/
├── database/
│   ├── schema.sql              # 数据库结构
│   └── sentiment.db            # SQLite数据库文件
├── api/
│   ├── server.py               # API服务
│   └── routes.py               # 路由定义
├── core/
│   ├── analyzer.py             # 核心分析引擎
│   ├── cot_engine.py           # COT思维链引擎
│   └── search_executor.py      # 搜索执行器
├── storage/
│   ├── db_manager.py           # 数据库管理
│   └── cache_manager.py        # 缓存管理
├── scheduler/
│   └── auto_analyze.py         # 自动分析任务
└── config/
    └── settings.py             # 配置
```
