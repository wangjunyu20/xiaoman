---
name: skill-template
description: Skill 描述模板 - 一句话说明用途，100字以内
metadata:
  version: "1.0.0"
  updated: "2026-03-09"
  author: "投资研究群"
  category: "数据/分析/报告/工具"
allowed-tools:
  - Bash(python:*)
  - Bash(node:*)
  - Bash(curl:*)
  - Read
  - Write
  - Edit
  - kimi_search
  - kimi_fetch
  - web_search
user-invocable: true
---

# Skill 名称

> 一句话概述：这个 Skill 是做什么的，解决什么问题。

## 元数据

| 属性 | 值 |
|------|-----|
| 名称 | skill-template |
| 分类 | 数据/分析/报告/工具 |
| 版本 | 1.0.0 |
| 更新日期 | 2026-03-09 |
| 依赖 | Python 3.8+, Node.js 16+ |
| 环境变量 | `API_TOKEN`, `CACHE_DIR` |

## 快速开始

### 1. 环境检查

```bash
# 检查依赖
python -c "import requests, pandas; print('OK')"
node -v

# 检查环境变量
echo $API_TOKEN
```

### 2. 运行示例

```bash
# 方式1: 命令行
python scripts/example_script.py "参数1" "参数2"

# 方式2: Python 导入
from scripts.example_script import ExampleClass
result = ExampleClass.run("参数")
```

### 3. 预期输出

```json
{
  "status": "success",
  "data": {
    "key": "value"
  }
}
```

## 执行流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  1. 输入验证  │ --> │  2. 数据获取  │ --> │  3. 数据处理  │
└─────────────┘     └─────────────┘     └─────────────┘
                                               |
                                               v
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  6. 结果输出  | <-- │  5. 质量检查  | <-- │  4. 内容生成  │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 详细步骤

#### 步骤 1: 输入验证
- 验证必需参数
- 检查环境变量
- 验证文件路径

#### 步骤 2: 数据获取
- 调用 API / 爬取数据
- 错误重试机制
- 缓存策略

#### 步骤 3: 数据处理
- 数据清洗
- 格式转换
- 去重筛选

#### 步骤 4: 内容生成
- 生成报告/分析
- 格式化输出
- 添加元数据

#### 步骤 5: 质量检查
- 数据完整性检查
- 格式校验
- 链接有效性

#### 步骤 6: 结果输出
- 保存到文件
- 返回结构化数据
- 生成摘要

## 功能详情

### 功能 1: 功能名称

**用途**: 说明用途

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| param1 | str | 是 | 参数说明 |
| param2 | int | 否 | 默认值: 10 |

**示例**:
```python
result = func(param1="value", param2=20)
```

**输出**:
```json
{
  "code": 0,
  "message": "success",
  "data": []
}
```

## 配置文件

### config.json

```json
{
  "api_endpoint": "https://api.example.com",
  "timeout": 30,
  "retry_times": 3,
  "cache_ttl": 3600
}
```

### 环境变量

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `API_TOKEN` | 是 | API 访问令牌 |
| `CACHE_DIR` | 否 | 缓存目录，默认 `./cache` |

## 故障排查

### 问题 1: 错误描述

**现象**: 
```
Error: Connection timeout
```

**原因**: 网络连接超时

**解决方案**:
1. 检查网络连接
2. 增加超时时间: `export TIMEOUT=60`
3. 使用代理: `export HTTPS_PROXY=http://proxy:8080`

### 问题 2: 认证失败

**现象**:
```
Error: Authentication failed (401)
```

**原因**: Token 无效或过期

**解决方案**:
1. 检查环境变量: `echo $API_TOKEN`
2. 重新获取 Token
3. 更新环境变量

### 问题 3: 依赖缺失

**现象**:
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案**:
```bash
pip install -r requirements.txt
# 或
npm install
```

## 性能优化

### 缓存策略
- 默认缓存 TTL: 30分钟
- 缓存位置: `./cache/`
- 清理命令: `python scripts/clear_cache.py`

### 并发控制
- 默认并发: 5
- 请求间隔: 1秒
- 重试次数: 3

## 安全注意事项

1. **Token 安全**: 不要将 Token 硬编码在代码中
2. **数据隐私**: 敏感数据不要记录在日志中
3. **请求限流**: 遵守 API 的限流规则
4. **错误处理**: 不要暴露内部错误详情

## 参考资源

### 内部文档
- [API 参考](references/api-reference.md)
- [数据字典](references/data-dictionary.md)
- [变更日志](CHANGELOG.md)

### 外部链接
- [官方文档](https://docs.example.com)
- [API 测试](https://api.example.com/test)

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-03-09 | 初始版本 |

---

> 本 Skill 遵循投资研究群空间标准化规范  
> 质量检查清单: `/root/.openclaw/workspace_investment/SKILL_QUALITY_CHECKLIST.md`
