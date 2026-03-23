# SearXNG 本地搜索技能

> 🔍 隐私优先的本地搜索引擎
> 📅 创建时间: 2026-03-16
> 🌐 服务地址: http://192.168.50.251:10011

---

## 📋 技能说明

使用本地部署的 SearXNG 实例进行网络搜索，无需外部 API Key，保护隐私。

---

## 🔧 配置信息

| 配置项 | 值 |
|--------|-----|
| **服务地址** | http://192.168.50.251:10011 |
| **默认引擎** | duckduckgo, bing |
| **返回格式** | JSON |
| **支持语言** | 中文、英文 |

---

## 💻 使用方法

### 方法1：直接调用 API

```bash
# 基本搜索
curl "http://192.168.50.251:10011/search?q=关键词&format=json&engines=duckduckgo,bing"

# 中文搜索
curl "http://192.168.50.251:10011/search?q=量化交易&format=json&engines=duckduckgo,bing&language=zh"

# 英文搜索
curl "http://192.168.50.251:10011/search?q=python+tutorial&format=json&engines=duckduckgo,bing&language=en"
```

### 方法2：Python 脚本

```python
import requests
import json

def search_searxng(query, engines="duckduckgo,bing", language="auto"):
    """
    使用本地 SearXNG 搜索

    Args:
        query: 搜索关键词
        engines: 搜索引擎（默认：duckduckgo,bing）
        language: 语言（auto/zh/en）

    Returns:
        搜索结果列表
    """
    base_url = "http://192.168.50.251:10011"

    params = {
        'q': query,
        'format': 'json',
        'engines': engines
    }

    if language != "auto":
        params['language'] = language

    try:
        response = requests.get(f"{base_url}/search", params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = []

        for r in data.get('results', []):
            results.append({
                'title': r.get('title', ''),
                'url': r.get('url', ''),
                'snippet': r.get('content', ''),
                'engine': r.get('engine', '')
            })

        return results

    except Exception as e:
        print(f"搜索失败: {e}")
        return []

# 使用示例
if __name__ == "__main__":
    # 中文搜索
    results = search_searxng("量化交易策略", language="zh")
    for i, r in enumerate(results[:5], 1):
        print(f"{i}. {r['title']}")
        print(f"   {r['url']}")
        print(f"   {r['snippet'][:100]}...")
        print()
```

### 方法3：在 OpenClaw 中使用

直接在对话中告诉我搜索内容，我会调用 SearXNG：

```
老板：帮我搜索一下最新的量化交易策略
我：[使用 SearXNG 搜索并返回结果]
```

---

## 🎯 最佳实践

### 推荐搜索引擎

| 用途 | 推荐引擎 | 说明 |
|------|---------|------|
| **通用搜索** | duckduckgo, bing | 平衡质量和速度 |
| **技术搜索** | duckduckgo, github | 代码和技术文档 |
| **中文搜索** | baidu, bing | 中文内容更准确 |
| **学术搜索** | google scholar, arxiv | 学术论文 |
| **新闻搜索** | bing news, google news | 新闻资讯 |

### 搜索技巧

1. **精确匹配**：使用引号 `"量化交易"`
2. **排除词**：使用减号 `量化交易 -基金`
3. **站内搜索**：`site:github.com python`
4. **文件类型**：`filetype:pdf 量化交易`

---

## ⚙️ 高级配置

### 自定义搜索函数

```python
def advanced_search(query, options=None):
    """高级搜索选项"""
    options = options or {}

    params = {
        'q': query,
        'format': 'json',
        'engines': options.get('engines', 'duckduckgo,bing'),
        'language': options.get('language', 'auto'),
        'pageno': options.get('page', 1),
        'time_range': options.get('time_range', ''),  # day/week/month/year
        'safesearch': options.get('safesearch', 0),   # 0/1/2
    }

    response = requests.get(
        "http://192.168.50.251:10011/search",
        params=params,
        timeout=10
    )

    return response.json()

# 使用
results = advanced_search(
    "量化交易",
    {
        'engines': 'duckduckgo,bing',
        'language': 'zh',
        'time_range': 'week',  # 只搜索最近一周
        'page': 1
    }
)
```

---

## 📊 可用搜索引擎

SearXNG 支持 247 个搜索引擎，常用包括：

### 通用搜索
- duckduckgo
- bing
- google（可能不稳定）
- baidu

### 技术搜索
- github
- stackoverflow
- devto

### 学术搜索
- google scholar
- arxiv
- pubmed

### 媒体搜索
- youtube
- vimeo
- flickr
- unsplash

---

## 🔧 故障排查

### 问题1：搜索结果为空

**原因**：搜索引擎可能被屏蔽

**解决**：更换搜索引擎
```python
# 避免使用 google
engines = "duckduckgo,bing"
```

### 问题2：响应超时

**原因**：网络或服务器问题

**解决**：增加超时时间或重试
```python
response = requests.get(url, params=params, timeout=30)
```

### 问题3：中文乱码

**原因**：编码问题

**解决**：指定 language 参数
```python
params['language'] = 'zh'
```

---

## 📚 参考资料

- [SearXNG 官方文档](https://docs.searxng.org/)
- [SearXNG API 文档](https://docs.searxng.org/dev/search_api.html)
- [配置文件](../../docs/searxng-setup.md)

---

## 🔄 更新记录

- **2026-03-16**: 创建技能文档
- **服务地址**: http://192.168.50.251:10011
- **状态**: ✅ 正常运行

---

*维护者: 小秘*
