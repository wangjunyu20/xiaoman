---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
description: |-
    生成热点行业研究报告和速览页面。
    用于：(1)用户要求生成行业报告时 (2)每日定时生成行业速览时 (3)需要获取行业资讯时。
name: industry-research-report
---

# 行业研究报告生成

## 核心功能

1. **多源新闻聚合** - 互联网搜索 + 自动抓取5大权威财经媒体
2. **行业数据整合** - A股行情 + 新闻舆情
3. **报告自动生成** - HTML速览页 + PDF完整报告

## 快速开始（3分钟上手）

### 一键部署（唯一正确方式）

```bash
# ✅ 正确：使用一键部署脚本（包含生成→检验→推送全流程）
./scripts/deploy_full.sh

# ❌ 禁止：分步手动执行（容易遗漏环节）
# python scripts/generate_reports.py  ← 禁止单独执行
```

### 验证部署结果

```bash
# 1. 查看检验报告
cat /workspace_investment/output/research_reports/verification_report.txt

# 2. 访问线上版本
open https://wangjunyu20.github.io/xiaoman/

# 3. 验证内容
# - 点击3个以上详情页链接
# - 下载PDF验证目录
# - 检查新闻可点击跳转
```

---

## 文档体系（渐进披露）

### Level 1: 快速参考（本文档）
- 部署命令、检验清单、故障排查

### Level 2: 详细规范（references/）
| 文档 | 内容 |
|------|------|
| [行业清单](references/行业清单.md) | 15个行业定义、龙头股代码 |
| [详情页模板](references/行业研究报告模板_v1.0.md) | 7个栏目规范 |
| [首页模板](references/多行业速览模板_v1.0.md) | 首页卡片规范 |
| [命名规范](references/命名规范_v1.0.md) ⭐新增 | 栏目命名统一规则 |
| [数据血缘](references/数据血缘规范_v1.0.md) ⭐新增 | 勾稽关系与数据追踪 |
| [测试体系](references/测试体系_v1.0.md) ⭐新增 | 自动化测试场景 |

### Level 3: 数据源配置（references/）
| 文档 | 内容 |
|------|------|
| [互联网搜索指南](references/互联网搜索指南.md) | 前沿资讯搜索规则 |
| [akshare数据获取](references/akshare数据获取指南.md) | A股行情获取 |
| [舆情数据获取](references/舆情数据获取指南.md) | 股吧舆情获取 |

---

## 重要更新（2026-03-12）

### 命名统一规范（方案A）

**统一为"行业资讯"，区分展示层级：**

| 位置 | 原命名 | 新命名 | 说明 |
|------|--------|--------|------|
| 首页行业卡片 | 📰 最新资讯 | 📰 行业资讯（Top 5） | 仅展示前5条 |
| 详情页 | 📰 相关资讯 | 📰 行业资讯（完整列表） | 展示全部 |

**为什么统一？**
- 消除用户困惑（两者数据来源相同）
- 明确展示差异（数量不同，内容一致）
- 便于建立勾稽关系

### 数据血缘追踪（新增）

**目标**：建立"输入=输出"的数据守恒验证

**数据流向**：
```
采集 → 清洗 → 标注 → 展示
 40     32      32      15(首页5+详情10)
```

**勾稽检查点**：
- 原始数据量 = 各来源之和
- 有效数据量 = 原始 - 过滤
- 展示数据量 = 首页 + 详情 + 归档

详见 [数据血缘规范](references/数据血缘规范_v1.0.md)

### 测试体系（新增）

**三层检验**：
1. **格式检验**（verify_reports.py）- 文件存在、链接有效
2. **逻辑检验**（test_consistency.py）- 数据一致性、勾稽关系
3. **业务检验**（test_scenarios.py）- 利空消息存在、情感一致性

详见 [测试体系](references/测试体系_v1.0.md)

---

## 部署规范

### 输出要求

每次部署必须生成：

| 格式 | 文件 | 内容 |
|------|------|------|
| **网页版** | `index.html` + `reports/*.html` | 首页+15个行业详情页 |
| **PDF版** | `行业研究报告_YYYYMMDD.pdf` | 带目录书签 |
| **检验报告** | `verification_report.txt` | 格式+逻辑检验结果 |
| **血缘报告** | `data_lineage_report.json` | 数据采集追踪 |

### 新闻展示规范

**所有新闻标题必须链接到原文**

```html
<!-- 正确 -->
<a href="https://finance.sina.com.cn/..." target="_blank">
    中际旭创发布1.6T光模块新品...
</a>

<!-- 错误 -->
<span>中际旭创发布1.6T光模块新品...</span>
```

**数据源优先级**：
1. **财联社** - 实时快讯/电报
2. **新浪财经** - 综合财经新闻
3. **东方财富** - 个股/板块资讯
4. **东财股吧** - 板块舆情

**禁止使用**：百度新闻（URL会404）

---

## 行业清单（15个）

| 分类 | 行业 | 文件名 |
|------|------|--------|
| 政府首位 | 消费 | consumption |
| 新兴支柱 | 集成电路 | semiconductor |
| 新兴支柱 | 航空航天 | aerospace |
| 新兴支柱 | 生物医药 | biotech |
| 新兴支柱 | 低空经济 | low_altitude |
| AI基础设施 | 算力基础设施 | computing_infra |
| AI基础设施 | 光模块 | optical_module |
| AI基础设施 | 卫星互联网 | satellite |
| 未来产业 | 具身智能/人形机器人 | embodied_ai |
| 未来产业 | 6G | 6g |
| 未来产业 | 量子科技 | quantum |
| 未来产业 | 脑机接口 | brain_machine |
| 未来产业 | 可控核聚变 | nuclear_fusion |
| AI应用层 | AI应用 | ai_app |
| AI应用层 | AI+医疗 | ai_healthcare |

---

## 数据一致性说明

### 舆情分析与资讯列表的关系

| 模块 | 数据来源 | 特点 |
|------|----------|------|
| **舆情分析** | 东财股吧/社媒 | 散户情绪，偏情绪化，可能负面 |
| **行业资讯** | 财联社/新浪 | 官方媒体，偏理性，可能偏正面 |

**常见差异场景**：
- 板块下跌时：股吧骂声一片（负面），媒体还在报道技术突破（利好）
- 这种差异是**正常现象**，不是BUG

**如何在报告中体现**：
```
📊 市场情绪分析
├── 社媒情绪（股吧）：偏谨慎/负面 ← 短期情绪
└── 官方资讯：以利好为主 ← 长期趋势
```

详见 [舆情数据获取指南](references/舆情数据获取指南.md)

---

## 故障排查

### 检验失败

```bash
# 查看失败原因
cat /workspace_investment/output/research_reports/verification_report.txt

# 常见原因：
# - 新闻标题无链接 → 检查news_fetcher情感标注
# - 详情页内容过少 → 检查新闻抓取是否成功
# - 勾稽关系错误 → 检查数据血缘日志
```

### 新闻抓取失败

```bash
# 使用缓存跳过抓取
python scripts/generate_reports.py --skip-news

# 测试单个抓取模块
python scripts/news_fetcher.py --test "光模块"
```

### PDF生成失败

```bash
# 检查Chrome
which google-chrome
google-chrome --version

# 手动生成（调试用）
python scripts/generate_reports.py --pdf-only
```

---

## 更新记录

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.2.0 | 2026-03-12 | 新增命名规范、数据血缘、测试体系 |
| 1.1.0 | 2026-03-09 | 新增互联网搜索数据源 |
| 1.0.0 | 2026-03-07 | 初始版本，支持多源新闻+PDF生成 |

---

**文档原则**：
- **完整性**：快速开始 → 详细规范 → 数据源 → 故障排查
- **渐进披露**：本文档只放最常用信息，细节引用references/
- **不重复**：命名规范只在[命名规范_v1.0.md]详细说明，本文档仅引用
