# SearXNG 本地搜索配置

> 📊 配置本地 SearXNG 搜索引擎
> 📅 创建时间: 2026-03-16
> ✅ 状态: 已配置并测试通过

---

## 🎯 配置完成

### 服务信息

| 配置项 | 值 |
|--------|-----|
| **服务地址** | http://192.168.50.251:10011 |
| **状态** | ✅ 运行正常 |
| **可用引擎** | 247 个 |
| **推荐引擎** | duckduckgo, bing |
| **支持中文** | ✅ 是 |

### 测试结果

```
✅ 主页访问: HTTP 200
✅ 英文搜索: 10 条结果
✅ 中文搜索: 10 条结果
✅ 技术搜索: 正常
```

---

## 💻 使用方法

### 方法1：命令行搜索

```bash
# 基本搜索
curl "http://192.168.50.251:10011/search?q=关键词&format=json&engines=duckduckgo,bing"

# 中文搜索
curl "http://192.168.50.251:10011/search?q=量化交易&format=json&engines=duckduckgo,bing&language=zh"

# 最近一周的结果
curl "http://192.168.50.251:10011/search?q=bitcoin&format=json&engines=duckduckgo,bing&time_range=week"
```

### 方法2：Python 调用

```python
import requests

def search(query, engines="duckduckgo,bing", language="auto"):
    """使用本地 SearXNG 搜索"""
    params = {
        'q': query,
        'format': 'json',
        'engines': engines
    }
    
    if language != "auto":
        params['language'] = language
    
    response = requests.get(
        "http://192.168.50.251:10011/search",
        params=params,
        timeout=10
    )
    
    data = response.json()
    return data.get('results', [])

# 使用
results = search("量化交易", language="zh")
for r in results[:5]:
    print(f"{r['title']}: {r['url']}")
```

### 方法3：在对话中使用

直接告诉我要搜索的内容：
```
老板：帮我搜索一下最新的量化交易策略
我：[使用 SearXNG 搜索并返回结果]
```

---

## 🎯 推荐配置

### 默认搜索引擎

| 场景 | 推荐引擎 | 原因 |
|------|---------|------|
| **通用搜索** | duckduckgo, bing | 稳定且结果质量好 |
| **中文搜索** | baidu, bing | 中文内容更准确 |
| **技术搜索** | duckduckgo, github | 技术文档和代码 |
| **新闻搜索** | bing news, google news | 新闻资讯 |

### 搜索参数

```bash
# 完整参数示例
curl "http://192.168.50.251:10011/search" \
  -d "q=搜索关键词" \
  -d "format=json" \
  -d "engines=duckduckgo,bing" \
  -d "language=zh" \
  -d "time_range=week" \      # day/week/month/year
  -d "pageno=1" \              # 分页
  -d "safesearch=0"            # 0=关闭, 1=中等, 2=严格
```

---

## 🚀 快速启动 SearXNG

### 使用 Docker（推荐）

```bash
# 拉取镜像
docker pull searxng/searxng:latest

# 运行容器
docker run -d \
  --name searxng \
  -p 8888:8080 \
  -e BASE_URL=http://localhost:8888 \
  -e INSTANCE_NAME=my-searxng \
  searxng/searxng:latest

# 验证
curl http://localhost:8888
```

### 使用 Docker Compose

```yaml
# docker-compose.yml
version: '3'

services:
  searxng:
    image: searxng/searxng:latest
    container_name: searxng
    ports:
      - "8888:8080"
    environment:
      - BASE_URL=http://localhost:8888
      - INSTANCE_NAME=my-searxng
    volumes:
      - ./searxng:/etc/searxng
    restart: unless-stopped
```

```bash
# 启动
docker-compose up -d
```

---

## ⚙️ 高级配置

### 自定义设置

创建 `settings.yml`：

```yaml
# settings.yml
general:
  instance_name: "My SearXNG"
  debug: false

search:
  safe_search: 0
  autocomplete: "google"
  default_lang: "zh"

server:
  port: 8080
  bind_address: "0.0.0.0"

engines:
  - name: google
    engine: google
    shortcut: g
    
  - name: bing
    engine: bing
    shortcut: b
    
  - name: duckduckgo
    engine: duckduckgo
    shortcut: ddg
```

---

## 🔍 验证配置

### 测试脚本

```python
#!/usr/bin/env python3
"""测试 SearXNG 配置"""

import requests
import json

def test_searxng(base_url="http://localhost:8888"):
    print("=" * 50)
    print("SearXNG 配置测试")
    print("=" * 50)
    
    # 测试1：主页访问
    try:
        r = requests.get(base_url, timeout=5)
        print(f"✅ 主页访问: {r.status_code}")
    except Exception as e:
        print(f"❌ 主页访问失败: {e}")
        return False
    
    # 测试2：搜索API
    try:
        params = {'q': 'test', 'format': 'json'}
        r = requests.get(f"{base_url}/search", params=params, timeout=10)
        data = r.json()
        print(f"✅ 搜索API: {r.status_code}")
        print(f"   结果数: {len(data.get('results', []))}")
    except Exception as e:
        print(f"❌ 搜索API失败: {e}")
        return False
    
    # 测试3：中文搜索
    try:
        params = {'q': '量化交易', 'format': 'json', 'language': 'zh'}
        r = requests.get(f"{base_url}/search", params=params, timeout=10)
        data = r.json()
        print(f"✅ 中文搜索: {r.status_code}")
        if data.get('results'):
            print(f"   第一条: {data['results'][0].get('title', 'N/A')}")
    except Exception as e:
        print(f"❌ 中文搜索失败: {e}")
    
    print("=" * 50)
    return True

if __name__ == "__main__":
    test_searxng()
```

---

## 📊 OpenClaw 集成

### 当前状态

- ❌ Brave Search API：未配置
- ⏳ SearXNG：待配置

### 配置后效果

配置完成后，OpenClaw 可以：

1. ✅ 使用本地 SearXNG 搜索
2. ✅ 无需外部 API Key
3. ✅ 隐私保护
4. ✅ 支持多个搜索引擎

---

## 🛠️ 故障排查

### 问题1：无法访问

```bash
# 检查端口
netstat -tlnp | grep 8888

# 检查 Docker
docker ps -a | grep searxng

# 检查日志
docker logs searxng
```

### 问题2：搜索无结果

```bash
# 检查引擎配置
curl http://localhost:8888/config

# 查看日志
docker logs searxng | grep -i error
```

### 问题3：响应慢

```bash
# 减少引擎数量
# 在 settings.yml 中只保留需要的引擎

# 增加超时时间
# 在 OpenClaw 配置中设置更长的超时
```

---

## 📚 参考资料

- [SearXNG 官方文档](https://docs.searxng.org/)
- [SearXNG GitHub](https://github.com/searxng/searxng)
- [Docker Hub](https://hub.docker.com/r/searxng/searxng)

---

*创建时间: 2026-03-16*
*维护者: 小秘*
