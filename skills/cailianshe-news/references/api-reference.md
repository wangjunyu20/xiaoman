# Cailianshe News API 参考

> 财联社电报 API 文档

## API 端点

```
GET https://www.cls.cn/nodeapi/telegraphList
```

## 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| app | string | 是 | 固定值: `CailianpressWeb` |
| os | string | 是 | 固定值: `web` |
| sv | string | 是 | 版本号: `8.4.6` |
| rn | int | 否 | 返回数量，默认 50 |
| last_time | int | 否 | 时间戳，用于分页 |

## 响应格式

```json
{
  "code": 0,
  "data": {
    "roll_data": [
      {
        "id": "123456",
        "title": "新闻标题",
        "content": "新闻内容",
        "ctime": "2026-03-09 10:30:00",
        "subject_name": "相关板块",
        "subject_id": "8888"
      }
    ]
  }
}
```

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 新闻唯一ID |
| title | string | 新闻标题 |
| content | string | 完整内容 |
| ctime | string | 发布时间 |
| subject_name | string | 相关板块/概念 |
| subject_id | string | 板块ID |

## URL 格式

文章详情页:
```
https://www.cls.cn/telegraph/{id}
```

## 行业关键词映射

| 行业 | 关键词 |
|------|--------|
| 光模块 | 光模块、光通信、CPO |
| 人形机器人 | 人形机器人、具身智能、机器人 |
| 量子科技 | 量子、量子计算、量子通信 |
| AI应用 | AI应用、大模型、AIGC |
| 脑机接口 | 脑机接口、脑科学、神经 |
| 可控核聚变 | 核聚变、托卡马克、人造太阳 |
| AI+医疗 | AI医疗、智慧医疗、医疗AI |
| 消费 | 消费、零售、内需 |
| 集成电路 | 集成电路、芯片、半导体 |
| 低空经济 | 低空经济、飞行汽车、eVTOL |
| 算力 | 算力、数据中心、IDC |

## 注意事项

1. **免签名**: 该 API 无需签名即可访问
2. **限流**: 建议请求间隔 > 1秒
3. **缓存**: 建议缓存 30 分钟以上
4. **HTTPS**: 必须使用 HTTPS 访问

## 错误码

| 错误码 | 说明 | 处理 |
|--------|------|------|
| 0 | 成功 | - |
| 400 | 参数错误 | 检查请求参数 |
| 429 | 请求频繁 | 降低请求频率 |
| 500 | 服务器错误 | 稍后重试 |

## 示例代码

### Python

```python
import requests

url = "https://www.cls.cn/nodeapi/telegraphList"
params = {
    "app": "CailianpressWeb",
    "os": "web",
    "sv": "8.4.6",
    "rn": 50
}

response = requests.get(url, params=params, timeout=10)
data = response.json()

if data.get("code") == 0:
    for item in data["data"]["roll_data"]:
        print(f"[{item['ctime']}] {item['title']}")
```

### cURL

```bash
curl -s "https://www.cls.cn/nodeapi/telegraphList?app=CailianpressWeb&os=web&sv=8.4.6&rn=50" \
  -H "User-Agent: Mozilla/5.0" | jq .
```
