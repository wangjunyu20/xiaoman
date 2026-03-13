# TOOLS.md - 投资工具配置

## 数据源配置

### 1. AKShare - A股实时行情
- **用途**: 获取A股行情、财务数据
- **文档**: `/root/.openclaw/workspace_investment/skills/industry-research-report/references/akshare数据获取指南.md`
- **脚本**: `scripts/akshare_data.py`

### 2. Tushare - 财经数据API
- **用途**: 股票、基金、宏观经济数据
- **Skill**: `tushare-finance`
- **文档**: `/root/.openclaw/workspace_investment/skills/tushare-finance/SKILL.md`

### 3. 雪球 (Xueqiu) - 大V动态
- **用途**: 抓取大V发帖、自选股行情
- **Skill**: `snowtrace`
- **Token**: `e577278ba14a6ac22826026e270f697d33bf973f`
- **文档**: `/root/.openclaw/workspace_investment/skills/snowtrace/SKILL.md`

### 4. 东方财富 - 基金数据
- **用途**: 基金净值、持仓分析
- **远程服务器**: 119.28.133.19

## 远程服务器配置

### 基金爬虫服务器
- **Host**: 119.28.133.19
- **User**: xiaoman
- **Password**: 666888@Aa
- **用途**: 基金净值数据爬取

**关键路径**:
- 日志: `~/xiaoman/logs/scraper_cron.log`
- 代码: `~/xiaoman/fund_scraper/`
- 数据库: `/home/xiaoman/xiaoman/fund_scraper/fund_robot.db`

**SSH连接**:
```bash
ssh xiaoman@119.28.133.19
```

## 定时任务配置

| 任务 | 时间 | 功能 | 脚本 |
|-----|------|------|------|
| industry-report | 08:00 | 生成行业研究报告 | `skills/industry-research-report/scripts/generate_reports.py` |
| xueqiu-summary | 09:00 | 汇总雪球大V观点 | `skills/snowtrace/fetch_timeline.js` |
| fund-check | 08:00 | 检查基金净值更新 | 远程服务器定时任务 |
| portfolio-analysis | 18:00 | 投资组合分析 | 待开发 |

## 输出目录

```
/workspace_investment/output/
├── reports/                    # 研究报告
│   ├── industry/              # 行业报告
│   └── daily/                 # 日报
├── data/                      # 数据文件
│   ├── stock_quotes/          # 行情数据
│   ├── fund_nav/              # 基金净值
│   └── sentiment/             # 舆情数据
└── analysis/                  # 分析结果
    ├── portfolio/             # 组合分析
    └── backtest/              # 回测结果
```

## 快捷命令

```bash
# 生成行业报告
cd /root/.openclaw/workspace_investment && python skills/industry-research-report/scripts/generate_reports.py

# 获取雪球大V动态
node /root/.openclaw/workspace_investment/skills/snowtrace/fetch_timeline.js timeline "user_id1,user_id2" 5

# 查看基金日志
ssh xiaoman@119.28.133.19 "tail -20 ~/xiaoman/logs/scraper_cron.log"

# 分析日志
cd /root/.openclaw/workspace_investment && node scripts/log_analyzer.js
```
