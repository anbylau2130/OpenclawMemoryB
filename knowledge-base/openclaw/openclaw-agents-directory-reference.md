# OpenClaw Agents 目录参考文档

**目录位置：** `/root/.openclaw/agents/`

**最后更新：** 2026-03-21

---

## 目录

1. [目录结构概览](#1-目录结构概览)
2. [Agent 目录结构](#2-agent-目录结构)
3. [SOUL.md - 身份配置](#3-soulmd---身份配置)
4. [agent 目录 - 核心配置](#4-agent-目录---核心配置)
5. [sessions 目录 - 会话数据](#5-sessions-目录---会话数据)
6. [当前配置的 Agents](#6-当前配置的-agents)
7. [配置最佳实践](#7-配置最佳实践)

---

## 1. 目录结构概览

```
.openclaw/agents/
├── main/                    # 主 Agent（日常助手）
│   ├── SOUL.md             # 身份配置
│   ├── agent/              # 核心配置
│   │   ├── auth-profiles.json
│   │   ├── config.yaml
│   │   └── models.json
│   └── sessions/           # 会话数据
│       ├── sessions.json
│       └── *.jsonl
├── jessica/                # Jessica Agent
│   ├── agent/
│   │   ├── auth-profiles.json
│   │   └── models.json
│   └── sessions/
│       ├── sessions.json
│       └── *.jsonl
├── blackwidow/             # 其他 Agents...
├── captain/
├── hulk/
├── ironman/
├── thor/
└── default/                # 默认配置模板
    └── sessions/
```

---

## 2. Agent 目录结构

每个 Agent 目录包含以下子目录：

| 目录/文件 | 说明 |
|----------|------|
| `SOUL.md` | Agent 身份和职责定义（可选） |
| `agent/` | 核心配置目录 |
| `agent/config.yaml` | Agent 行为配置 |
| `agent/models.json` | 可用模型配置 |
| `agent/auth-profiles.json` | 认证配置 |
| `agent/auth.json` | 简单认证配置（旧版） |
| `agent/auth-profiles-*.json` | 按提供商的认证配置 |
| `sessions/` | 会话数据目录 |
| `sessions/sessions.json` | 会话索引 |
| `sessions/*.jsonl` | 会话历史记录 |
| `sessions/dingtalk-state/` | 钉钉状态数据 |

---

## 3. SOUL.md - 身份配置

SOUL.md 定义 Agent 的身份、职责和行为规则。

### 3.1 示例结构（太子 Agent）

```markdown
# 太子 · 皇上代理

你是太子，皇上在飞书上所有消息的第一接收人和分拣者。

## 核心职责
1. 接收皇上通过飞书发来的**所有消息**
2. **判断消息类型**：闲聊/问答 vs 正式旨意/复杂任务
3. 简单消息 → **自己直接回复皇上**（不创建任务）
4. 旨意/复杂任务 → **自己用人话重新概括**后转交中书省
5. 收到尚书省的最终回奏 → **在飞书原对话中回复皇上**

## 消息分拣规则（最高优先级）

### 自己直接回复（不建任务）：
- 简短回复：「好」「否」「?」「了解」「收到」
- 闲聊/问答：「token消耗多少？」「这个怎么样？」
- 内容不足10个字的消息

### 整理需求给中书省（创建 JJC 任务）：
- 明确的工作指令：「帮我做XX」「调研XX」
- 包含具体目标或交付物
- 有实质内容（≥10字），含动作词 + 具体目标
```

### 3.2 SOUL.md 配置要点

| 要素 | 说明 |
|------|------|
| **身份定义** | 明确 Agent 是谁 |
| **核心职责** | 列出主要职责清单 |
| **工作流程** | 定义处理流程和规则 |
| **边界条件** | 明确什么不该做 |
| **命令参考** | 提供常用命令示例 |

---

## 4. agent 目录 - 核心配置

### 4.1 config.yaml - Agent 行为配置

```yaml
# Main Agent Configuration
# 自动压缩策略配置

agent:
  id: main
  name: 骡子（日常助手）
  
# Compaction 配置 - 自动压缩对话历史
compaction:
  enabled: true
  triggerTokens: 60000        # 触发压缩的token阈值
  reserveTokensFloor: 10000   # 保留的最小token数
  strategy: "sliding_window"  # 压缩策略
  keepRecentMessages: 15      # 保留最近的N条消息
  keepSystemMessages: true    # 保留系统消息
  
# 模型配置
model:
  provider: zai
  model: glm-5
  contextWindow: 204800
  maxTokens: 131072
  
# 会话配置
session:
  maxHistorySize: 2000
  autoCompact: true
  compactInterval: 100
  
# 上下文硬限制 - 防止超出模型窗口
context:
  maxTokens: 60000
  truncationStrategy: "sliding_window"
  preserveSystemMessages: true
  preserveRecentMessages: 15
```

### 4.2 config.yaml 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `agent.id` | string | Agent 唯一标识符 |
| `agent.name` | string | Agent 显示名称 |
| `compaction.enabled` | boolean | 是否启用自动压缩 |
| `compaction.triggerTokens` | number | 触发压缩的 token 阈值 |
| `compaction.reserveTokensFloor` | number | 保留的最小 token 数 |
| `compaction.strategy` | string | 压缩策略（sliding_window/summary） |
| `compaction.keepRecentMessages` | number | 保留最近的消息数 |
| `model.provider` | string | 模型提供商 |
| `model.model` | string | 模型名称 |
| `model.contextWindow` | number | 上下文窗口大小 |
| `model.maxTokens` | number | 最大输出 token 数 |
| `session.maxHistorySize` | number | 最大历史记录数 |
| `context.maxTokens` | number | 上下文硬限制 |

### 4.3 models.json - 可用模型配置

```json
{
  "providers": {
    "nvidia1": {
      "baseUrl": "https://integrate.api.nvidia.com/v1",
      "apiKey": "nvapi-xxx",
      "api": "openai-completions",
      "models": [
        {
          "id": "deepseek-ai/deepseek-v3.2",
          "name": "DeepSeek V3.2",
          "input": ["text"],
          "cost": { "input": 0, "output": 0 },
          "contextWindow": 64000,
          "maxTokens": 8192,
          "reasoning": false
        }
      ]
    },
    "zai": {
      "baseUrl": "https://open.bigmodel.cn/api/coding/paas/v4",
      "api": "openai-completions",
      "models": [
        {
          "id": "glm-5",
          "name": "GLM-5",
          "reasoning": true,
          "input": ["text"],
          "cost": { "input": 0, "output": 0 },
          "contextWindow": 204800,
          "maxTokens": 100000
        }
      ],
      "apiKey": "xxx"
    }
  }
}
```

### 4.4 models.json 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `providers` | object | 提供商配置字典 |
| `providers.*.baseUrl` | string | API 基础 URL |
| `providers.*.apiKey` | string | API 密钥（可覆盖） |
| `providers.*.api` | string | API 类型 |
| `providers.*.models` | array | 可用模型列表 |
| `models[].id` | string | 模型唯一标识符 |
| `models[].name` | string | 模型显示名称 |
| `models[].reasoning` | boolean | 是否支持推理 |
| `models[].input` | array | 支持的输入类型 |
| `models[].cost` | object | 成本配置 |
| `models[].contextWindow` | number | 上下文窗口大小 |
| `models[].maxTokens` | number | 最大输出 token 数 |

### 4.5 auth-profiles.json - 认证配置

```json
{
  "version": 1,
  "profiles": {
    "zai:default": {
      "type": "api_key",
      "provider": "zai",
      "key": "xxx"
    },
    "anthropic:default": {
      "type": "api_key",
      "provider": "anthropic",
      "key": "xxx"
    },
    "zai:edict": {
      "type": "api_key",
      "provider": "zai",
      "key": "xxx",
      "baseUrl": "https://open.bigmodel.cn/api/coding/paas/v4"
    }
  },
  "lastGood": {
    "zai": "zai:default",
    "anthropic": "anthropic:default"
  },
  "usageStats": {
    "zai:default": {
      "lastUsed": 1773727635970,
      "errorCount": 0,
      "lastFailureAt": 1773215880792
    }
  }
}
```

### 4.6 auth-profiles.json 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `version` | number | 配置版本 |
| `profiles` | object | 认证配置文件字典 |
| `profiles.*.type` | string | 认证类型（api_key） |
| `profiles.*.provider` | string | 提供商名称 |
| `profiles.*.key` | string | API 密钥 |
| `profiles.*.baseUrl` | string | 可选的自定义 URL |
| `lastGood` | object | 每个提供商最后成功的配置 |
| `usageStats` | object | 使用统计信息 |
| `usageStats.*.lastUsed` | number | 最后使用时间戳 |
| `usageStats.*.errorCount` | number | 错误计数 |
| `usageStats.*.lastFailureAt` | number | 最后失败时间戳 |

---

## 5. sessions 目录 - 会话数据

### 5.1 sessions.json - 会话索引

```json
{
  "agent:jessica:main": {
    "origin": {
      "label": "崔晓洋 (096028035723738668)",
      "provider": "dingtalk",
      "surface": "dingtalk",
      "chatType": "direct",
      "from": "096028035723738668",
      "to": "096028035723738668",
      "accountId": "jessica"
    },
    "sessionId": "ee357db7-8445-46d2-92a5-7089e3694f30",
    "updatedAt": 1773727635983,
    "deliveryContext": {
      "channel": "dingtalk",
      "to": "096028035723738668",
      "accountId": "jessica"
    },
    "lastChannel": "dingtalk",
    "chatType": "direct",
    "sessionFile": "/root/.openclaw/agents/jessica/sessions/ee357db7-8445-46d2-92a5-7089e3694f30.jsonl",
    "authProfileOverride": "zai:default",
    "modelProvider": "zai",
    "model": "glm-4.7",
    "contextTokens": 204800,
    "inputTokens": 118080,
    "outputTokens": 159,
    "totalTokens": 121494
  }
}
```

### 5.2 sessions.json 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `origin` | object | 会话来源信息 |
| `origin.label` | string | 显示标签 |
| `origin.provider` | string | 提供商（dingtalk） |
| `origin.surface` | string | 界面类型 |
| `origin.chatType` | string | 聊天类型（direct/group） |
| `origin.from` | string | 发送者 ID |
| `origin.accountId` | string | 账号 ID |
| `sessionId` | string | 会话唯一 ID（UUID） |
| `updatedAt` | number | 最后更新时间戳 |
| `deliveryContext` | object | 投递上下文 |
| `lastChannel` | string | 最后使用的通道 |
| `chatType` | string | 聊天类型 |
| `sessionFile` | string | 会话文件路径 |
| `authProfileOverride` | string | 认证配置覆盖 |
| `modelProvider` | string | 模型提供商 |
| `model` | string | 使用的模型 |
| `contextTokens` | number | 上下文 token 数 |
| `inputTokens` | number | 输入 token 数 |
| `outputTokens` | number | 输出 token 数 |
| `totalTokens` | number | 总 token 数 |

### 5.3 会话历史文件（*.jsonl）

会话历史以 JSONL 格式存储，每行一条消息记录：

```
/root/.openclaw/agents/jessica/sessions/ee357db7-8445-46d2-92a5-7089e3694f30.jsonl
```

### 5.4 dingtalk-state 目录

存储钉钉特定的状态数据：

```
sessions/dingtalk-state/
├── quoted.msg-journal.account-xxx.json  # 引用消息日志
└── ...
```

---

## 6. 当前配置的 Agents

### 6.1 Agents 列表

| Agent ID | 目录 | 说明 | 状态 |
|----------|------|------|------|
| `main` | main/ | 日常助手（骡子） | ✅ 活跃 |
| `jessica` | jessica/ | Jessica 助手 | ✅ 活跃 |
| `blackwidow` | blackwidow/ | 备用 | 💤 休眠 |
| `captain` | captain/ | 备用 | 💤 休眠 |
| `hulk` | hulk/ | 备用 | 💤 休眠 |
| `ironman` | ironman/ | 备用 | 💤 休眠 |
| `thor` | thor/ | 备用 | 💤 休眠 |
| `default` | default/ | 默认模板 | - |

### 6.2 已清理的 Agents（三省六部）

以下 Agents 已于 2026-03-21 清理：

| Agent ID | 名称 | 原职责 |
|----------|------|--------|
| `taizi` | 太子 | 消息分拣 |
| `zhongshu` | 中书省 | 规划 |
| `menxia` | 门下省 | 审核 |
| `shangshu` | 尚书省 | 派发 |
| `hubu` | 户部 | 数据 |
| `libu` | 礼部 | 文档 |
| `bingbu` | 兵部 | 工程 |
| `xingbu` | 刑部 | 合规 |
| `gongbu` | 工部 | 基建 |
| `libu_hr` | 吏部 | 人事 |
| `zaochao` | 早朝官 | 情报 |

---

## 7. 配置最佳实践

### 7.1 创建新 Agent

1. **创建目录结构**
```bash
mkdir -p /root/.openclaw/agents/new-agent/{agent,sessions}
```

2. **创建 SOUL.md**（可选）
```markdown
# 新助手

你是新助手，负责...

## 核心职责
1. ...
2. ...
```

3. **创建 models.json**
```json
{
  "providers": {
    "zai": {
      "baseUrl": "https://open.bigmodel.cn/api/coding/paas/v4",
      "api": "openai-completions",
      "models": [...]
    }
  }
}
```

4. **创建 auth-profiles.json**
```json
{
  "version": 1,
  "profiles": {
    "zai:default": {
      "type": "api_key",
      "provider": "zai",
      "key": "your-api-key"
    }
  }
}
```

5. **在 openclaw.json 中注册**
```json
{
  "agents": {
    "list": [
      {
        "id": "new-agent",
        "name": "新助手",
        "workspace": "/root/.openclaw/workspace-new-agent",
        "model": "zai/glm-5"
      }
    ]
  }
}
```

### 7.2 配置优化建议

| 场景 | 建议 |
|------|------|
| **长对话** | 启用 compaction，设置合理的 triggerTokens |
| **多模型** | 在 models.json 中配置多个提供商 |
| **认证切换** | 配置多个 auth-profiles，使用 lastGood 管理 |
| **会话管理** | 定期清理旧的 jsonl 文件 |

### 7.3 常见问题

| 问题 | 解决方案 |
|------|---------|
| Agent 不响应 | 检查 auth-profiles.json 中的 API Key |
| 上下文超限 | 调整 compaction.triggerTokens |
| 会话丢失 | 检查 sessions/sessions.json |
| 模型切换失败 | 检查 models.json 配置 |

---

## 附录

### 相关文档

- [OpenClaw 主配置参考](/root/.openclaw/knowledge-base/openclaw-config-reference.md)
- [OpenClaw 官方文档](https://docs.openclaw.ai)

### 目录清理命令

```bash
# 清理已删除 Agent 的目录
rm -rf /root/.openclaw/agents/taizi
rm -rf /root/.openclaw/agents/zhongshu
# ... 其他已删除的 agents

# 清理会话缓存
rm -rf /root/.openclaw/agents/*/sessions/*.jsonl
```

---

_文档版本: 1.0 | 最后更新: 2026-03-21_
