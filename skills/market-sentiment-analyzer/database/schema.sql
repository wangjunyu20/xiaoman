-- 市场舆情分析系统数据库结构
-- 创建时间: 2026-03-09

-- 行业舆情概述表 (用于报告首页，3-5句话概述)
CREATE TABLE IF NOT EXISTS industry_sentiment_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    industry_name VARCHAR(50) NOT NULL,
    analysis_date DATE NOT NULL,
    change_pct DECIMAL(5,2),
    trend_summary VARCHAR(20),
    sentiment_brief TEXT,           -- 舆情概述 (3-5句话)
    key_factors TEXT,               -- 核心驱动因素 (JSON)
    risk_level VARCHAR(10),         -- 风险等级
    outlook_short VARCHAR(200),     -- 短期展望
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(industry_name, analysis_date)
);

-- 行业舆情详情表 (用于详情页，完整大段文字)
CREATE TABLE IF NOT EXISTS industry_sentiment_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    industry_name VARCHAR(50) NOT NULL,
    analysis_date DATE NOT NULL,
    
    -- Layer 1: 表面现象
    latest_price DECIMAL(10,2),
    change_pct DECIMAL(5,2),
    volume_status VARCHAR(20),
    fund_flow VARCHAR(100),
    leader_stocks TEXT,             -- 龙头股表现 (JSON)
    
    -- Layer 2-5: 完整分析文字
    causal_analysis_full TEXT,      -- 完整因果分析 (大段文字)
    root_cause VARCHAR(200),        -- 根本原因
    key_events TEXT,                -- 关键事件 (JSON)
    
    -- 数据来源和质量
    data_sources TEXT,              -- 数据来源 (JSON)
    analysis_depth INTEGER DEFAULT 3,
    verification_status VARCHAR(20) DEFAULT '待验证',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(industry_name, analysis_date)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_summary_industry_date 
    ON industry_sentiment_summary(industry_name, analysis_date);
CREATE INDEX IF NOT EXISTS idx_detail_industry_date 
    ON industry_sentiment_detail(industry_name, analysis_date);

-- 插入示例数据 (光模块)
INSERT OR REPLACE INTO industry_sentiment_summary (
    industry_name, analysis_date, change_pct, trend_summary, 
    sentiment_brief, key_factors, risk_level, outlook_short
) VALUES (
    '光模块',
    '2026-03-09',
    -4.36,
    '下跌',
    '光模块板块今日下跌4.36%，主要受中东地缘政治危机影响。伊朗封锁霍尔木兹海峡导致油价暴涨54%，推高通胀预期，市场担忧美联储维持高利率将压缩科技股估值。资金从AI板块流出，中际旭创遭净卖出超17亿元。',
    '["地缘政治", "能源危机", "货币政策", "资金流出"]',
    '高',
    '短期关注中东局势演变，中期等待估值回归合理区间'
);

INSERT OR REPLACE INTO industry_sentiment_detail (
    industry_name, analysis_date, change_pct, volume_status, fund_flow,
    causal_analysis_full, root_cause, key_events, data_sources
) VALUES (
    '光模块',
    '2026-03-09',
    -4.36,
    '放量下跌',
    '主力净流出超17亿元',
    '第一步：地缘政治冲突爆发。2026年3月2日，伊朗宣布全面封锁霍尔木兹海峡，这是该海峡历史上首次正式封闭。背景是美国与以色列在2月28日对伊朗发动了代号为"史诗怒火"的联合军事行动，伊朗最高领袖哈梅内伊在袭击中遇害。作为报复，伊朗革命卫队宣布将向任何试图穿越霍尔木兹海峡的船只开火。这一地缘政治事件的严重性在于，霍尔木兹海峡是全球石油运输的咽喉要道，承担着全球约20%的海运石油贸易量和近30%的液化天然气运输量。

第二步：能源市场剧烈动荡。霍尔木兹海峡被封的消息传出后，国际原油市场立即做出剧烈反应。布伦特原油期货价格从危机前的每桶70美元左右飙升至108美元以上，涨幅超过54%。

第三步：通胀预期迫使美联储维持高利率。油价暴涨通过成本推动机制推高了通胀预期。能源成本占美国CPI权重的约7%，油价上涨直接推高了运输成本和商品价格。市场预期美联储将被迫维持4.5-5.0%的高利率水平。

第四步：高利率环境压制科技股估值。根据贴现现金流(DCF)模型，当贴现率上升时，远期现金流的现值会大幅下降。科技股的特点是大部分现金流在未来，因此对利率变化特别敏感。

第五步：机构减仓导致股价下跌。在上述多重因素叠加下，机构开始减仓AI板块。中际旭创单日遭主力净卖出超过17亿元，最终板块下跌4.36%。',
    '伊朗封锁霍尔木兹海峡',
    '[{"event": "伊朗封锁霍尔木兹海峡", "date": "2026-03-02", "source": "财新周刊"}, {"event": "油价暴涨至108美元", "date": "2026-03-09", "source": "财新"}, {"event": "中际旭创遭净卖出17亿", "date": "2026-03-09", "source": "财联社"}]',
    '["腾讯财经API", "财新周刊", "财联社", "九方智投"]'
);

-- 插入示例数据 (算力)
INSERT OR REPLACE INTO industry_sentiment_summary (
    industry_name, analysis_date, change_pct, trend_summary, 
    sentiment_brief, key_factors, risk_level, outlook_short
) VALUES (
    '算力',
    '2026-03-09',
    2.45,
    '上涨',
    '算力板块今日逆势上涨2.45%，主要受益于海南华铁36.9亿元算力服务大单签订，验证了算力租赁商业模式的可行性。同时腾讯AI智能体WorkBuddy上线，标志着AI应用商业化落地加速。国产算力技术突破和两会政策支持进一步强化了国产替代逻辑。',
    '["大单签订", "AI应用落地", "国产替代", "政策支持"]',
    '中',
    '短期高位震荡，关注新订单持续性'
);

INSERT OR REPLACE INTO industry_sentiment_detail (
    industry_name, analysis_date, change_pct, volume_status, fund_flow,
    causal_analysis_full, root_cause, key_events, data_sources
) VALUES (
    '算力',
    '2026-03-09',
    2.45,
    '放量上涨',
    '主力资金净流入',
    '第一步：大额订单签订验证商业模式。2026年3月4日晚间，海南华铁发布公告，其全资子公司签署了一份价值36.9亿元的算力服务协议，服务期限为五年。这一订单的规模相当于海南华铁过去几年的总收入，直接证明了算力租赁这一商业模式的可行性。

第二步：AI应用落地强化需求预期。2026年3月9日，腾讯正式推出全场景AI智能体WorkBuddy。这款产品不同于此前的大模型聊天工具，它是一个真正能"干活"的办公助手，标志着AI大模型从"技术展示"阶段正式进入了"实际应用"阶段。

第三步：国产技术突破降低供应链风险。海光信息与上海人工智能实验室合作，推出了DeepLink多元算力混合推理加速方案。在国际局势紧张的背景下，国产算力技术的突破降低了对海外供应链的依赖。

第四步：两会政策提供长期支撑。2026年3月召开的全国两会上，"具身智能"连续两年被写入政府工作报告，算力作为AI基础设施获得了国家战略层面的支持。

第五步：估值逻辑从概念转向业绩。随着36.9亿大单的签订和AI应用的落地，算力板块的估值基础转变为"已经有确定订单和收入"，进入了业绩驱动阶段。

第六步：资金流入推动股价上涨。与CPO板块不同，算力板块主要面向国内市场，受益于国产替代政策，受海外AI投资预期下调的影响较小，最终上涨2.45%。',
    '海南华铁36.9亿大单+腾讯AI应用落地',
    '[{"event": "海南华铁36.9亿大单", "date": "2026-03-04", "source": "九方智投"}, {"event": "腾讯WorkBuddy上线", "date": "2026-03-09", "source": "腾讯云"}, {"event": "海光信息技术突破", "date": "2026-03-09", "source": "海光信息"}]',
    '["腾讯财经API", "九方智投", "腾讯云", "海光信息", "财新周刊"]'
);

-- 插入示例数据 (人形机器人)
INSERT OR REPLACE INTO industry_sentiment_summary (
    industry_name, analysis_date, change_pct, trend_summary, 
    sentiment_brief, key_factors, risk_level, outlook_short
) VALUES (
    '人形机器人',
    '2026-03-09',
    -1.20,
    '下跌',
    '人形机器人板块今日下跌1.20%，主要受春晚利好兑现后的获利回吐影响。节前资金提前博弈春晚亮相预期导致板块大涨，节后利好兑现资金离场。同时特斯拉Optimus V3发布推迟至2026年Q1，产业化进度不及预期。市场估值逻辑从"技术故事"切换到"订单业绩"，但订单未能如期落地。',
    '["利好兑现", "量产推迟", "估值切换", "筹码松动"]',
    '中',
    '高位震荡，等待特斯拉V3发布催化'
);

INSERT OR REPLACE INTO industry_sentiment_detail (
    industry_name, analysis_date, change_pct, volume_status, fund_flow,
    causal_analysis_full, root_cause, key_events, data_sources
) VALUES (
    '人形机器人',
    '2026-03-09',
    -1.20,
    '缩量下跌',
    '节前埋伏资金获利了结',
    '第一步：春晚亮相预期被提前炒作。2026年1月底的春节联欢晚会上，宇树科技、松延动力等人形机器人企业登上舞台，表演了空翻、集群协同等高难度动作。资金在节前就已经提前博弈这一预期，春节前机器人概念已经历过一轮大幅上涨。

第二步：特斯拉Optimus发布推迟打击预期。市场原本普遍预期特斯拉会在2025年底发布第三代Optimus人形机器人，但摩根士丹利的报告显示，特斯拉实际上将发布时间推迟到了2026年第一季度。这一推迟意味着产业化进度不及市场预期。

第三步：估值逻辑从技术切换到订单。2025年被称为人形机器人技术突破年，市场炒作的核心逻辑是"技术有多先进"。但进入2026年，市场的关注点发生了根本性转变，市场逻辑已经从"看技术"切换到"看业绩、寻订单"的阶段。

第四步：量产瓶颈和商业化困难暴露。瑞银证券估计2026年全球人形机器人出货量仅约3万台，这一数字相比市场预期偏保守。技术层面仍存在瓶颈，商业化路径也不明朗。

第五步：筹码结构恶化加剧调整。节前埋伏的资金获利了结后，机构调仓至业绩确定性更高的板块，而散户成为接盘方，导致筹码松动。

第六步：多重因素叠加导致下跌。春晚利好兑现后的获利回吐、特斯拉发布推迟、估值逻辑切换、量产瓶颈暴露、筹码结构恶化等多重因素叠加，导致人形机器人板块下跌1.20%。',
    '春晚利好兑现+量产不及预期',
    '[{"event": "春晚机器人亮相", "date": "2026-01-28", "source": "央视"}, {"event": "Optimus V3推迟发布", "date": "2026-02-24", "source": "摩根士丹利"}, {"event": "高盛看空报告", "date": "2026-02-27", "source": "高盛"}]',
    '["腾讯财经API", "新浪财经", "第一财经", "摩根士丹利", "高盛"]'
);
