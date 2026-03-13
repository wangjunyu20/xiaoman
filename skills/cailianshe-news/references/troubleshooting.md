# Cailianshe News 故障排查指南

## 常见问题速查

### 1. 网络连接问题

#### 现象
```
Error: HTTPSConnectionPool(host='www.cls.cn', port=443): Max retries exceeded
```

#### 排查步骤

1. **测试网络连通性**
   ```bash
   ping www.cls.cn
   curl -I https://www.cls.cn
   ```

2. **检查 DNS 解析**
   ```bash
   nslookup www.cls.cn
   ```

3. **检查代理设置**
   ```bash
   echo $HTTP_PROXY
   echo $HTTPS_PROXY
   # 如有代理，尝试取消
   unset HTTP_PROXY HTTPS_PROXY
   ```

#### 解决方案
- 等待网络恢复
- 切换网络环境
- 配置代理（如需要）

---

### 2. API 限流/封禁

#### 现象
```
Error: 429 Too Many Requests
```
或返回 HTML 页面而非 JSON

#### 排查步骤

1. **检查请求频率**
   ```bash
   # 查看脚本是否频繁运行
   ps aux | grep fetch_cailianshe
   ```

2. **检查缓存是否生效**
   ```bash
   ls -la ./news_cache/
   cat ./news_cache/*.json | head
   ```

#### 解决方案
- 增加请求间隔（默认已设置 1 秒）
- 延长缓存时间（修改 `cache_ttl` 参数）
- 等待 5-10 分钟后重试

---

### 3. 解析错误

#### 现象
```
Error: Expecting value: line 1 column 1 (char 0)
```
或
```
Error: KeyError: 'roll_data'
```

#### 排查步骤

1. **检查 API 返回格式**
   ```bash
   python scripts/fetch_cailianshe.py "光模块" 1 --debug
   ```

2. **手动测试 API**
   ```bash
   curl -s "https://www.cls.cn/nodeapi/telegraphList?app=CailianpressWeb&os=web&sv=8.4.6" | jq .
   ```

#### 解决方案
- API 可能已变更，更新解析代码
- 添加更多的错误处理
- 降级使用缓存数据

---

### 4. 关键词匹配失败

#### 现象
返回空列表 `[]`，但网站上有相关新闻

#### 排查步骤

1. **检查关键词映射**
   ```python
   # 在脚本中添加调试
   print(f"Searching for keywords: {keywords}")
   ```

2. **扩大搜索范围**
   ```bash
   # 使用更宽泛的关键词
   python scripts/fetch_cailianshe.py "机器人" 10
   ```

3. **检查返回原始数据**
   ```bash
   # 临时修改脚本打印原始数据
   python -c "
   import requests
   url = 'https://www.cls.cn/nodeapi/telegraphList'
   params = {'app': 'CailianpressWeb', 'os': 'web', 'sv': '8.4.6', 'rn': 50}
   r = requests.get(url, params=params, timeout=10)
   print(r.text[:2000])
   "
   ```

#### 解决方案
- 使用同义词/近义词
- 检查财联社是否真有相关新闻
- 扩大关键词映射表

---

### 5. 缓存相关问题

#### 现象
- 获取到过时的新闻
- 缓存文件损坏
- 磁盘空间不足

#### 排查步骤

1. **检查缓存文件**
   ```bash
   ls -lah ./news_cache/
   # 查看文件修改时间
   stat ./news_cache/cls_光模块.json
   ```

2. **验证缓存内容**
   ```bash
   cat ./news_cache/cls_光模块.json | jq .
   ```

3. **检查磁盘空间**
   ```bash
   df -h
   ```

#### 解决方案

```bash
# 清理缓存
rm -rf ./news_cache/*

# 或修改缓存时间
python scripts/fetch_cailianshe.py "光模块" 5 --cache-ttl=600  # 10分钟
```

---

### 6. 中文编码问题

#### 现象
```
UnicodeEncodeError: 'ascii' codec can't encode characters
```
或终端显示乱码

#### 排查步骤

```bash
# 检查环境编码
echo $LANG
echo $PYTHONIOENCODING
python -c "import sys; print(sys.stdout.encoding)"
```

#### 解决方案

```bash
# 设置 UTF-8 编码
export LANG=en_US.UTF-8
export PYTHONIOENCODING=utf-8

# 或在 Python 脚本中设置
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

---

## 调试模式

启用调试输出查看详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from scripts.fetch_cailianshe import CailiansheNewsFetcher
fetcher = CailiansheNewsFetcher(debug=True)
news = fetcher.fetch_telegraph("光模块", limit=3)
```

## 联系与支持

- **财联社官网**: https://www.cls.cn
- **投资研究群**: 请通过 Feishu 联系管理员
- **Issue 反馈**: 记录错误现象和排查步骤

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-03-09 | 1.0 | 初始版本 |
