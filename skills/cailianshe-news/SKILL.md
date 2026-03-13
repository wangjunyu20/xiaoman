---
name: cailianshe-news
description: Fetch real-time financial news from Cailianshe (财联社), a mainstream Chinese financial news agency. Use this skill when users need to retrieve financial telegraph news, industry-specific news, or real-time market updates from Cailianshe.
---

# Cailianshe News Fetcher

This skill provides the ability to fetch real-time financial news from **Cailianshe (财联社)**, one of China's mainstream financial news agencies.

## When to Use

Use this skill when:
- Users need to fetch real-time financial news from Cailianshe
- Users need industry-specific news (e.g., AI, semiconductors, robotics)
- Users need financial telegraph updates for investment research

## How to Use

### Method 1: Use the Python Script Directly

Execute the script with keyword and optional limit:

```bash
python scripts/fetch_cailianshe.py <keyword> [limit]
```

Examples:
```bash
# Fetch 3 news items about "光模块" (optical modules)
python scripts/fetch_cailianshe.py "光模块" 3

# Fetch 5 news items about "人形机器人" (humanoid robots)
python scripts/fetch_cailianshe.py "人形机器人" 5
```

### Method 2: Import as Python Module

```python
from scripts.fetch_cailianshe import CailiansheNewsFetcher, fetch_cailianshe_news

# Method A: Use the convenience function
news = fetch_cailianshe_news("光模块", limit=5)

# Method B: Use the class for more control
fetcher = CailiansheNewsFetcher(cache_dir="./cache", cache_ttl=1800)
news = fetcher.fetch_telegraph("AI应用", limit=3)

# Process results
for item in news:
    print(f"Title: {item['title']}")
    print(f"URL: {item['url']}")
    print(f"Time: {item['publish_time']}")
    print(f"Impact: {item['impact']}")
    print(f"Summary: {item['summary']}")
```

## News Data Structure

Each news item returned is a dictionary with:

| Field | Type | Description |
|-------|------|-------------|
| `source` | str | News source (always "财联社") |
| `title` | str | News headline |
| `url` | str | Full URL to the original article |
| `publish_time` | str | Publication time (format: YYYY-MM-DD HH:MM) |
| `summary` | str | Brief summary of the content |
| `impact` | str | Sentiment analysis: "利好" (positive), "利空" (negative), or "中性" (neutral) |

## Technical Details

### API Endpoint
```
https://www.cls.cn/nodeapi/telegraphList
```

This is a **signature-free API** that returns JSON data directly.

### Request Parameters
- `app`: CailianpressWeb
- `os`: web
- `sv`: 8.4.6
- `rn`: 50 (number of results)
- `last_time`: 0 (timestamp for pagination)

### URL Format
Article URLs follow the pattern:
```
https://www.cls.cn/telegraph/{id}
```

### Caching
- Default cache directory: `./news_cache/`
- Default cache TTL: 30 minutes (1800 seconds)
- Cache files are stored as JSON

### Supported Industries
The following industries have pre-configured keyword mappings:

- 光模块 (Optical Modules)
- 人形机器人 (Humanoid Robots)
- 量子科技 (Quantum Technology)
- AI应用 (AI Applications)
- 脑机接口 (Brain-Computer Interface)
- 可控核聚变 (Nuclear Fusion)
- AI+医疗 (AI Healthcare)
- 消费 (Consumption)
- 集成电路 (Integrated Circuits)
- 低空经济 (Low-altitude Economy)
- 算力 (Computing Power)

## Examples

### Example 1: Fetch News for Semiconductor Industry
```python
from scripts.fetch_cailianshe import fetch_cailianshe_news

news = fetch_cailianshe_news("集成电路", limit=3)
for item in news:
    print(f"[{item['impact']}] {item['title']}")
    print(f"   → {item['url']}\n")
```

### Example 2: Command Line Usage
```bash
# Get latest AI industry news
python scripts/fetch_cailianshe.py "AI应用" 5
```

### Example 3: Batch Fetch Multiple Industries
```python
from scripts.fetch_cailianshe import CailiansheNewsFetcher

fetcher = CailiansheNewsFetcher()
industries = ["光模块", "人形机器人", "量子科技"]

for industry in industries:
    news = fetcher.fetch_telegraph(industry, limit=3)
    print(f"\n=== {industry} ({len(news)}条) ===")
    for item in news:
        print(f"• {item['title'][:40]}...")
```

## Notes

- The API returns the latest 50 telegraph messages, which are then filtered by keyword
- If no matching news is found for a keyword, an empty list is returned
- The API has rate limiting; use caching to avoid being blocked
- All URLs are complete and clickable (unlike some other news sources that return relative paths)

## Error Handling

The script handles common errors gracefully:
- Network timeouts (10-second timeout)
- Invalid JSON responses
- Missing fields in response data
- Cache read/write errors

If an error occurs, the function returns an empty list and prints an error message.

## Troubleshooting

### Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Network timeout | `Max retries exceeded` | Check connection, increase timeout |
| Rate limited | `429 Too Many Requests` | Wait 5-10 minutes, increase cache TTL |
| Empty results | `[]` returned | Try broader keywords, check mapping |
| Parse error | `KeyError: 'roll_data'` | API may have changed, check debug output |
| Encoding issue | `UnicodeEncodeError` | Set `export PYTHONIOENCODING=utf-8` |

### Debug Mode

Enable debug output for detailed logs:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from scripts.fetch_cailianshe import CailiansheNewsFetcher
fetcher = CailiansheNewsFetcher(debug=True)
```

### Clear Cache

If cache is corrupted or outdated:

```bash
rm -rf ./news_cache/*
```

See [troubleshooting.md](references/troubleshooting.md) for detailed troubleshooting guide.

## References

- [API Reference](references/api-reference.md) - API endpoint details and parameters
- [Troubleshooting Guide](references/troubleshooting.md) - Detailed error diagnosis and solutions

## Quick Check

Before using, verify setup:

```bash
# Test network
ping -c 3 www.cls.cn

# Test API
curl -s "https://www.cls.cn/nodeapi/telegraphList?app=CailianpressWeb&os=web&sv=8.4.6&rn=5" | head -c 200

# Run test
python scripts/fetch_cailianshe.py "光模块" 1
```

## 故障排查

### 问题1: 返回空列表

**现象**: 
```python
news = fetch_cailianshe_news("量子科技", limit=5)
print(news)  # 输出: []
```

**可能原因**:
1. 财联社近期没有该关键词的新闻
2. 关键词不匹配（尝试使用更通用的关键词）
3. API 限流或暂时不可用

**解决方案**:
```python
# 尝试使用更通用的关键词
news = fetch_cailianshe_news("量子", limit=5)  # 代替 "量子科技"

# 检查缓存是否过期
fetcher = CailiansheNewsFetcher(cache_ttl=0)  # 禁用缓存
news = fetcher.fetch_telegraph("量子科技", limit=5)
```

### 问题2: 网络超时

**现象**:
```
Request timeout after 10 seconds
```

**解决方案**:
```python
# 增加超时时间
fetcher = CailiansheNewsFetcher(timeout=30)
news = fetcher.fetch_telegraph("光模块", limit=3)
```

### 问题3: 缓存不更新

**现象**: 获取到的新闻是旧数据

**解决方案**:
```bash
# 清除缓存
rm -rf ./news_cache/*.json

# 或在代码中禁用缓存
fetcher = CailiansheNewsFetcher(cache_ttl=0)
```

### 问题4: API 返回错误

**现象**:
```
Error fetching data: HTTP 429
```

**原因**: 请求频率过高，触发限流

**解决方案**:
```python
import time

fetcher = CailiansheNewsFetcher()
for industry in industries:
    news = fetcher.fetch_telegraph(industry, limit=3)
    time.sleep(1)  # 请求间隔1秒
```

## 参考文档

### 内部文档
- [搜索规则](references/search-rules.md) - 关键词设计规范
- [数据格式](references/data-format.md) - 返回数据结构说明

### 外部资源
- [财联社官网](https://www.cls.cn)
- [电报列表 API](https://www.cls.cn/nodeapi/telegraphList)

## 更新记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-03-09 | v1.1 | 添加故障排查章节 |
| 2026-03-08 | v1.0 | 初始版本 |
