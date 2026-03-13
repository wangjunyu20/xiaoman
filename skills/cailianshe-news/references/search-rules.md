# 财联社新闻 Skill - 搜索规则

## 关键词设计原则

### 1. 长度适中
- 推荐: 2-4个字
- 太短: "AI" 会匹配太多无关新闻
- 太长: "人工智能芯片设计" 可能无匹配

### 2. 使用行业通用术语

| 不推荐 | 推荐 |
|--------|------|
| 光通信模块 | 光模块 |
| 人形智能机器 | 人形机器人 |
| 大脑计算机接口 | 脑机接口 |

### 3. 多关键词策略

```python
# 单一关键词可能不够
keywords = ["量子科技", "量子计算", "国盾量子", "本源量子"]

# 合并搜索
all_news = []
for kw in keywords:
    news = fetcher.fetch_telegraph(kw, limit=3)
    all_news.extend(news)

# 去重
unique_news = {n['title']: n for n in all_news}.values()
```

## 行业关键词库

### AI相关
- AI应用
- 大模型
- ChatGPT
- 文心一言

### 量子科技
- 量子科技
- 量子计算
- 国盾量子
- 本源量子

### 脑机接口
- 脑机接口
- Neuralink
- 三博脑科

### 机器人
- 人形机器人
- 具身智能
- 优必选

### 光模块
- 光模块
- CPO
- 中际旭创
- 天孚通信

## 返回数据处理

### 数据去重
```python
def deduplicate_news(news_list):
    """根据标题去重"""
    seen = set()
    result = []
    for news in news_list:
        title = news['title']
        if title not in seen:
            seen.add(title)
            result.append(news)
    return result
```

### 时效性筛选
```python
def filter_by_date(news_list, days=7):
    """筛选最近N天的新闻"""
    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(days=days)
    return [
        n for n in news_list
        if datetime.strptime(n['publish_time'], '%Y-%m-%d %H:%M') > cutoff
    ]
```
