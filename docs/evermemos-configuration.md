# EverMemOS 配置指南

> **来源：** EverMemOS 官方 GitHub 文档
> **文档时间：** 2026-03-16
> **仓库：** https://github.com/EverMind-AI/EverMemOS

---

## ⚠️ 重要原则

**配置前必须查阅官方文档！** 不要猜测配置选项。

**文档位置：**
- 官方 README：https://github.com/EverMind-AI/EverMemOS
- 配置指南：`docs/usage/CONFIGURATION_GUIDE.md`
- 检索策略：`docs/advanced/RETRIEVAL_STRATEGIES.md`

---

## 检索方法对比

| 方法 | 需要 Embedding | 需要 Rerank | 速度 | 准确度 | 推荐场景 |
|------|---------------|-------------|------|--------|---------|
| `keyword` | ❌ | ❌ | ⚡⚡⚡ 最快 | ⭐⭐ | 精确关键词匹配 |
| `vector` | ✅ | ❌ | ⚡⚡ 较快 | ⭐⭐⭐ | 语义理解 |
| `rrf` | ✅ | ❌ | ⚡⚡ 较快 | ⭐⭐⭐⭐ | **默认推荐** |
| `hybrid` | ✅ | ✅ 必须 | ⚡ 慢 | ⭐⭐⭐⭐⭐ | 高精度需求 |
| `agentic` | ✅ | ✅ 必须 | 🐢 最慢 | ⭐⭐⭐⭐⭐ | 复杂分析 |

---

## Rerank 配置

### 支持的 Rerank Provider

根据官方文档，`RERANK_PROVIDER` **只支持**：
- `deepinfra` - 付费服务
- `vllm` - 本地部署

### ❌ 不支持的值

以下值**不被支持**（会导致错误）：
- `none`
- `disabled`
- 空值
- 不设置

### ✅ 不需要 Rerank 的方案

使用 `vector` 或 `rrf` 检索方法，不需要配置 Rerank。

---

## OpenClaw 插件配置

**文件：** `/root/.openclaw/openclaw.json`

```json5
"plugins": {
  "entries": {
    "openclaw-evermemos": {
      "enabled": true,
      "config": {
        "baseUrl": "http://192.168.50.251:1995/api/v1",
        "userId": "main",
        "groupId": "openclaw-agents",
        "retrieveMethod": "rrf",  // 推荐：不需要 Rerank
        "topK": 10
      }
    }
  }
}
```

---

## EverMemOS 服务器配置

### Vectorize 配置（使用 Jina）

```bash
# .env 或 docker-compose.yml
VECTORIZE_PROVIDER=vllm
VECTORIZE_API_KEY=jina_xxxxx
VECTORIZE_BASE_URL=https://api.jina.ai/v1
VECTORIZE_MODEL=jina-embeddings-v3
VECTORIZE_DIMENSIONS=1024
```

### Rerank 配置

**如果不需要 Rerank：** 不配置 `RERANK_*` 变量，使用 `rrf` 检索方法。

**如果需要 Rerank：**

```bash
# 方案1：DeepInfra（付费）
RERANK_PROVIDER=deepinfra
RERANK_API_KEY=your_deepinfra_key
RERANK_BASE_URL=https://api.deepinfra.com/v1/inference
RERANK_MODEL=Qwen/Qwen3-Reranker-4B

# 方案2：本地 vLLM（免费，需部署）
# 先部署：vllm serve Qwen/Qwen3-Reranker-4B --task reward --port 12000
RERANK_PROVIDER=vllm
RERANK_API_KEY=none
RERANK_BASE_URL=http://localhost:12000/score
RERANK_MODEL=Qwen3-Reranker-4B
```

---

## 常见错误

### 错误1：`Unsupported provider: none`

**原因：** `RERANK_PROVIDER=none` 不被支持

**解决：** 删除 Rerank 配置，使用 `rrf` 检索方法

### 错误2：`Unsupported provider: disabled`

**原因：** `RERANK_PROVIDER=disabled` 不被支持

**解决：** 删除 Rerank 配置，使用 `rrf` 检索方法

### 错误3：`Unsupported provider: ollama`

**原因：** `VECTORIZE_PROVIDER=ollama` 不被支持

**解决：** 使用 `vllm`、`deepinfra`、`jina` 或 `openai`

---

## 验证配置

```bash
# 1. 健康检查
curl http://192.168.50.251:1995/health

# 2. 测试向量检索
curl -G "http://192.168.50.251:1995/api/v0/memories/search" \
  --data-urlencode "user_id=main" \
  --data-urlencode "query=test" \
  --data-urlencode "retrieve_method=rrf" \
  --data-urlencode "top_k=5"
```

---

## 参考资料

- [EverMemOS 官方仓库](https://github.com/EverMind-AI/EverMemOS)
- [配置指南](https://github.com/EverMind-AI/EverMemOS/blob/main/docs/usage/CONFIGURATION_GUIDE.md)
- [检索策略](https://github.com/EverMind-AI/EverMemOS/blob/main/docs/advanced/RETRIEVAL_STRATEGIES.md)
- [OpenClaw 插件](https://github.com/ZhenhangTung/openclaw-EverMemOS)
