# HEARTBEAT.md - 投资群定时检查

## 检查清单（每次 Heartbeat）

### 1. 检查 EvoMap 执行状态
```bash
node /root/.openclaw/workspace_investment/skills/industry-research-report/scripts/log_analyzer.js
```
- 最近10次执行成功率
- 异常情况记录

### 2. 检查基金爬虫状态
```bash
ssh xiaoman@119.28.133.19 "tail -5 ~/xiaoman/logs/scraper_cron.log"
```
- 昨日是否正常执行
- 是否有异常错误

### 3. 检查定时任务状态
```bash
openclaw cron list
```
- industry-report: 每天 08:00
- xueqiu-summary: 每天 09:00

### 4. 检查空间文件完整性
```bash
ls -la /root/.openclaw/workspace_investment/memory/
```
- 今日记忆文件是否存在
- 昨日记忆是否正常归档

## 汇报条件

**需要汇报（主动发送消息）**:
- EvoMap 连续失败 > 2 次
- 基金爬虫日志显示错误
- 定时任务执行失败
- 检测到异常市场信号

**静默（回复 HEARTBEAT_OK）**:
- 所有系统正常
- 无异常需要关注
- 非汇报时间窗口

## 汇报格式

```
【投资系统巡检】
- EvoMap: 正常/异常
- 基金爬虫: 正常/异常  
- 定时任务: 正常/异常
- 今日计划: [简要说明]
```

## 时间窗口

- **早盘前** (08:00-09:00): 检查昨日数据，准备今日报告
- **收盘后** (15:00-16:00): 分析当日行情，更新持仓数据

其他时间如无异常，静默处理。
