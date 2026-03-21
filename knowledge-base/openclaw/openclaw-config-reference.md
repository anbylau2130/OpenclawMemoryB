# OpenClaw 配置文件参考文档

**配置文件位置：** `/root/.openclaw/openclaw.json`

**最后更新：** 2026-03-21

---

## 目录

1. [meta](#1-meta) - 元数据信息
2. [wizard](#2-wizard) - 向导配置
3. [browser](#3-browser) - 浏览器配置
4. [models](#4-models) - 模型配置
5. [agents](#5-agents) - Agent 配置
6. [tools](#6-tools) - 工具配置
7. [bindings](#7-bindings) - 绑定配置
8. [commands](#8-commands) - 命令配置
9. [session](#9-session) - 会话配置
10. [hooks](#10-hooks) - 钩子配置
11. [channels](#11-channels) - 通道配置
12. [gateway](#12-gateway) - 网关配置
13. [plugins](#13-plugins) - 插件配置

---

## 1. meta

元数据信息，记录配置文件的版本和修改时间。

```json
{
  "meta": {
    "lastTouchedVersion": "2026.3.13",
    "lastTouchedAt": "2026-03-19T15:33:16.724Z"
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `lastTouchedVersion` | string | 最后修改配置的 OpenClaw 版本 |
| `lastTouchedAt` | string | 最后修改时间（ISO 8601 格式）|

---

## 2. wizard

向导配置，记录初始化向导的运行信息。

```json
{
  "wizard": {
    "lastRunAt": "2026-03-06T01:09:18.549Z",
    "lastRunVersion": "2026.3.3",
    "lastRunCommand": "doctor",
    "lastRunMode": "local"
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `lastRunAt` | string | 最后运行向导的时间 |
| `lastRunVersion` | string | 运行向导时的 OpenClaw 版本 |
| `lastRunCommand` | string | 最后运行的命令（如 doctor） |
| `lastRunMode` | string | 运行模式（local/remote） |

---

## 3. browser

浏览器配置，用于自动化浏览器操作。

```json
{
  "browser": {
    "executablePath": "/usr/bin/chromium",
    "headless": true,
    "noSandbox": true,
    "defaultProfile": "openclaw"
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `executablePath` | string | 浏览器可执行文件路径 |
| `headless` | boolean | 是否使用无头模式 |
| `noSandbox` | boolean | 是否禁用沙箱（容器环境需要） |
| `defaultProfile` | string | 默认浏览器配置文件名 |

---

## 4. models

模型配置，定义可用的 AI 模型提供商和模型列表。

### 4.1 基本结构

```json
{
  "models": {
    "mode": "merge",
    "providers": {
      "provider1": { ... },
      "provider2": { ... }
    }
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `mode` | string | 合并模式（merge/replace） |
| `providers` | object | 提供商配置字典 |

### 4.2 提供商配置

```json
{
  "nvidia1": {
    "baseUrl": "https://integrate.api.nvidia.com/v1",
    "apiKey": "nvapi-xxx",
    "api": "openai-completions",
    "models": [ ... ]
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `baseUrl` | string | API 基础 URL |
| `apiKey` | string | API 密钥 |
| `api` | string | API 类型（openai-completions） |
| `models` | array | 可用模型列表 |

### 4.3 模型配置

```json
{
  "id": "glm-5",
  "name": "GLM-5",
  "reasoning": true,
  "input": ["text"],
  "cost": {
    "input": 0,
    "output": 0,
    "cacheRead": 0,
    "cacheWrite": 0
  },
  "contextWindow": 204800,
  "maxTokens": 100000
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 模型唯一标识符 |
| `name` | string | 模型显示名称 |
| `reasoning` | boolean | 是否支持推理模式 |
| `input` | array | 支持的输入类型（text/image） |
| `cost` | object | 成本配置（每千 token 价格） |
| `contextWindow` | number | 上下文窗口大小 |
| `maxTokens` | number | 最大输出 token 数 |

### 4.4 当前配置的提供商

| 提供商 | 基础 URL | 说明 |
|--------|---------|------|
| `nvidia1` | https://integrate.api.nvidia.com/v1 | NVIDIA NIM API（备用） |
| `nvidia2` | https://integrate.api.nvidia.com/v1 | NVIDIA NIM API（备用） |
| `zai` | https://open.bigmodel.cn/api/coding/paas/v4 | 智谱 GLM API |

### 4.5 当前配置的模型

| 模型 ID | 提供商 | 上下文 | 最大输出 | 推理 |
|---------|--------|--------|---------|------|
| glm-5 | zai | 204800 | 100000 | ✅ |
| glm-4.7 | zai | 204800 | 100000 | ✅ |
| glm-4.6 | zai | 204800 | 100000 | ✅ |
| glm-4.5-air | zai | 204800 | 100000 | ✅ |
| deepseek-ai/deepseek-v3.2 | nvidia | 64000 | 8192 | ❌ |
| meta/llama-3.1-70b-instruct | nvidia | 131072 | 8192 | ❌ |
| meta/llama-3.1-8b-instruct | nvidia | 131072 | 8192 | ❌ |
| microsoft/phi-3-mini-128k-instruct | nvidia | 128000 | 4096 | ❌ |
| microsoft/phi-3.5-mini-instruct | nvidia | 128000 | 4096 | ❌ |
| google/gemma-2-9b-it | nvidia | 8192 | 8192 | ❌ |
| google/gemma-2-2b-it | nvidia | 8192 | 8192 | ❌ |
| mistralai/mistral-7b-instruct-v0.3 | nvidia | 32768 | 8192 | ❌ |

---

## 5. agents

Agent 配置，定义 AI 助手的行为和能力。

### 5.1 基本结构

```json
{
  "agents": {
    "defaults": { ... },
    "list": [ ... ]
  }
}
```

### 5.2 defaults - 默认配置

```json
{
  "defaults": {
    "model": {
      "primary": "zai/glm-5"
    },
    "models": {
      "zai/glm-5": { "alias": "GLM" },
      "zai/glm-4.7": { "alias": "GLM-4.7" }
    },
    "workspace": "/root/.openclaw/workspace",
    "contextPruning": { ... },
    "compaction": { ... },
    "blockStreamingDefault": "on",
    "blockStreamingBreak": "text_end",
    "timeoutSeconds": 86400,
    "heartbeat": {}
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `model.primary` | string | 默认主模型 |
| `models` | object | 模型别名映射 |
| `workspace` | string | 默认工作空间路径 |
| `contextPruning` | object | 上下文修剪配置 |
| `compaction` | object | 上下文压缩配置 |
| `blockStreamingDefault` | string | 流式输出默认设置（on/off） |
| `blockStreamingBreak` | string | 流式输出断点（text_end） |
| `timeoutSeconds` | number | 会话超时时间（秒） |
| `heartbeat` | object | 心跳配置 |

### 5.3 contextPruning - 上下文修剪

```json
{
  "contextPruning": {
    "mode": "cache-ttl",
    "ttl": "1800",
    "keepLastAssistants": 10,
    "softTrim": {
      "maxChars": 8000,
      "headChars": 3000,
      "tailChars": 3000
    },
    "hardClear": {
      "enabled": true,
      "placeholder": "[Old tool result content cleared]"
    }
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `mode` | string | 修剪模式（cache-ttl/manual） |
| `ttl` | string | 缓存 TTL（秒） |
| `keepLastAssistants` | number | 保留最近的助手消息数 |
| `softTrim.maxChars` | number | 软修剪最大字符数 |
| `softTrim.headChars` | number | 保留头部字符数 |
| `softTrim.tailChars` | number | 保留尾部字符数 |
| `hardClear.enabled` | boolean | 是否启用硬清除 |
| `hardClear.placeholder` | string | 清除后的占位符 |

### 5.4 compaction - 上下文压缩

```json
{
  "compaction": {
    "mode": "safeguard",
    "reserveTokensFloor": 80000,
    "memoryFlush": {
      "enabled": true,
      "softThresholdTokens": 10000
    }
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `mode` | string | 压缩模式（safeguard/manual） |
| `reserveTokensFloor` | number | 保留的最小 token 数 |
| `memoryFlush.enabled` | boolean | 是否启用内存刷新 |
| `memoryFlush.softThresholdTokens` | number | 软刷新阈值 |

### 5.5 list - Agent 列表

```json
{
  "list": [
    {
      "id": "main",
      "default": true,
      "name": "日常助手",
      "workspace": "/root/.openclaw/workspace",
      "model": "zai/glm-5"
    },
    {
      "id": "jessica",
      "name": "jessica",
      "workspace": "/root/.openclaw/workspace-jessica",
      "agentDir": "/root/.openclaw/agents/jessica/agent",
      "model": "zai/glm-4.7",
      "identity": {
        "name": "jessica"
      }
    }
  ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | Agent 唯一标识符 |
| `default` | boolean | 是否为默认 Agent |
| `name` | string | Agent 显示名称 |
| `workspace` | string | 工作空间路径 |
| `agentDir` | string | Agent 配置目录（可选） |
| `model` | string | 使用的模型 |
| `identity` | object | 身份配置（可选） |

---

## 6. tools

工具配置，控制工具的可见性和交互。

```json
{
  "tools": {
    "sessions": {
      "visibility": "all"
    },
    "agentToAgent": {
      "enabled": true
    }
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `sessions.visibility` | string | 会话可见性（all/own） |
| `agentToAgent.enabled` | boolean | 是否启用 Agent 间通信 |

---

## 7. bindings

绑定配置，将 Agent 绑定到特定通道和账号。

```json
{
  "bindings": [
    {
      "agentId": "jessica",
      "match": {
        "channel": "dingtalk",
        "accountId": "jessica"
      }
    },
    {
      "agentId": "main",
      "match": {
        "channel": "dingtalk",
        "accountId": "default"
      }
    }
  ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `agentId` | string | 绑定的 Agent ID |
| `match.channel` | string | 匹配的通道名称 |
| `match.accountId` | string | 匹配的账号 ID |

---

## 8. commands

命令配置，控制命令行行为。

```json
{
  "commands": {
    "native": "auto",
    "nativeSkills": "auto",
    "restart": true,
    "ownerDisplay": "raw"
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `native` | string | 原生命令模式（auto/enable/disable） |
| `nativeSkills` | string | 原生技能模式（auto/enable/disable） |
| `restart` | boolean | 是否允许通过命令重启 |
| `ownerDisplay` | string | 所有者显示模式（raw/markdown） |

---

## 9. session

会话配置，控制会话维护和清理。

```json
{
  "session": {
    "maintenance": {
      "mode": "enforce",
      "pruneAfter": "30d",
      "maxEntries": 50
    }
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `maintenance.mode` | string | 维护模式（enforce/manual） |
| `maintenance.pruneAfter` | string | 清理超过指定时间的会话 |
| `maintenance.maxEntries` | number | 每个会话最大条目数 |

---

## 10. hooks

钩子配置，控制内部钩子的启用状态。

```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "boot-md": { "enabled": true },
        "bootstrap-extra-files": { "enabled": true },
        "command-logger": { "enabled": true },
        "session-memory": { "enabled": true }
      }
    }
  }
}
```

| 钩子名称 | 说明 |
|---------|------|
| `boot-md` | 启动时加载 Markdown 文件 |
| `bootstrap-extra-files` | 启动时加载额外文件 |
| `command-logger` | 命令日志记录 |
| `session-memory` | 会话内存管理 |

---

## 11. channels

通道配置，定义消息通道的连接方式。

### 11.1 基本结构

```json
{
  "channels": {
    "dingtalk": {
      "enabled": true,
      "learningEnabled": true,
      "learningAutoApply": false,
      "learningNoteTtlMs": 21600000,
      "showThinking": true,
      "messageType": "markdown",
      "thinkingMessage": "emoji",
      "accounts": { ... },
      "robots": [ ... ],
      "subagents": { ... }
    }
  }
}
```

### 11.2 通道配置字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `enabled` | boolean | 是否启用通道 |
| `learningEnabled` | boolean | 是否启用学习功能 |
| `learningAutoApply` | boolean | 是否自动应用学习结果 |
| `learningNoteTtlMs` | number | 学习笔记 TTL（毫秒） |
| `showThinking` | boolean | 是否显示思考过程 |
| `messageType` | string | 消息类型（markdown/text） |
| `thinkingMessage` | string | 思考消息显示方式（emoji/text） |

### 11.3 accounts - 账号配置

```json
{
  "default": {
    "clientId": "ding46pdp4gp2nfgfbfl",
    "clientSecret": "xxx",
    "robotCode": "ding46pdp4gp2nfgfbfl",
    "corpId": "ding3cecc6cee84e6509a1320dcb25e91351",
    "agentId": "4271180067",
    "dmPolicy": "open",
    "groupPolicy": "open",
    "messageType": "markdown",
    "userPhone": "13027729771",
    "allowFrom": ["*"]
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `clientId` | string | 钉钉应用 Client ID |
| `clientSecret` | string | 钉钉应用 Client Secret |
| `robotCode` | string | 机器人代码 |
| `corpId` | string | 企业 ID |
| `agentId` | string | 应用 Agent ID |
| `dmPolicy` | string | 私聊策略（open/restricted） |
| `groupPolicy` | string | 群聊策略（open/restricted） |
| `messageType` | string | 消息类型 |
| `userPhone` | string | 用户手机号 |
| `allowFrom` | array | 允许的来源用户列表 |

### 11.4 robots - 机器人配置

```json
{
  "robots": [
    {
      "name": "OpenClaw工作通知机器人",
      "agentId": "4271180067",
      "clientId": "ding46pdp4gp2nfgfbfl",
      "clientSecret": "xxx",
      "corpId": "ding3cecc6cee84e6509a1320dcb25e91351",
      "accountId": "default",
      "userPhone": "13027729771"
    }
  ]
}
```

### 11.5 subagents - 子代理配置

```json
{
  "subagents": {
    "enabled": true,
    "spawnThreads": true,
    "spawnThreadsBindings": []
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `enabled` | boolean | 是否启用子代理 |
| `spawnThreads` | boolean | 是否生成线程 |
| `spawnThreadsBindings` | array | 线程绑定的代理列表 |

---

## 12. gateway

网关配置，控制 API 网关的行为。

```json
{
  "gateway": {
    "port": 18789,
    "mode": "local",
    "bind": "loopback",
    "controlUi": {},
    "auth": {
      "mode": "token",
      "token": "Lrq7dNX27t57BGby_PVKDAQMqHu3jq_p35DpZEqOLbk"
    },
    "tailscale": {
      "mode": "off",
      "resetOnExit": false
    },
    "nodes": {
      "denyCommands": [
        "camera.snap",
        "camera.clip",
        "screen.record",
        "calendar.add",
        "contacts.add",
        "reminders.add"
      ]
    }
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `port` | number | 网关端口 |
| `mode` | string | 网关模式（local/remote） |
| `bind` | string | 绑定地址（loopback/0.0.0.0） |
| `controlUi` | object | 控制界面配置 |
| `auth.mode` | string | 认证模式（token/none） |
| `auth.token` | string | 认证令牌 |
| `tailscale.mode` | string | Tailscale 模式（off/on） |
| `tailscale.resetOnExit` | boolean | 退出时是否重置 |
| `nodes.denyCommands` | array | 禁用的节点命令列表 |

---

## 13. plugins

插件配置，管理系统插件。

### 13.1 基本结构

```json
{
  "plugins": {
    "load": {
      "paths": ["/root/.openclaw/plugins/evermemos-openclaw-plugin"]
    },
    "slots": {
      "memory": "evermemos-openclaw-plugin"
    },
    "entries": { ... },
    "installs": { ... }
  }
}
```

### 13.2 load - 加载配置

```json
{
  "load": {
    "paths": ["/root/.openclaw/plugins/evermemos-openclaw-plugin"]
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `paths` | array | 插件路径列表 |

### 13.3 slots - 插槽配置

```json
{
  "slots": {
    "memory": "evermemos-openclaw-plugin"
  }
}
```

| 插槽名称 | 说明 |
|---------|------|
| `memory` | 记忆系统插件 |

### 13.4 entries - 插件条目

```json
{
  "entries": {
    "dingtalk": { "enabled": true },
    "evermemos-openclaw-plugin": {
      "enabled": true,
      "config": {
        "baseUrl": "http://192.168.50.251:1995",
        "userId": "openclaw",
        "groupId": "openclaw-agents",
        "topK": 5,
        "memoryTypes": ["episodic_memory", "profile", "agent_skill", "agent_case"],
        "retrieveMethod": "rrf"
      }
    }
  }
}
```

### 13.5 EverMemOS 插件配置

| 字段 | 类型 | 说明 |
|------|------|------|
| `baseUrl` | string | EverMemOS 服务地址 |
| `userId` | string | 用户 ID |
| `groupId` | string | 组 ID |
| `topK` | number | 检索结果数量 |
| `memoryTypes` | array | 记忆类型列表 |
| `retrieveMethod` | string | 检索方法（rrf/bm25） |

### 13.6 installs - 安装记录

```json
{
  "installs": {
    "dingtalk": {
      "source": "npm",
      "spec": "@soimy/dingtalk",
      "installPath": "/root/.openclaw/extensions/dingtalk",
      "version": "3.3.0",
      "resolvedName": "@soimy/dingtalk",
      "resolvedVersion": "3.3.0",
      "resolvedSpec": "@soimy/dingtalk@3.3.0",
      "integrity": "sha512-xxx",
      "shasum": "f6881d3f54ae33dd0f9aa30c8fb70a3e3541616e",
      "resolvedAt": "2026-03-17T00:38:47.899Z",
      "installedAt": "2026-03-17T00:40:22.539Z"
    }
  }
}
```

---

## 配置修改注意事项

### 修改后必须重启 Gateway

```bash
openclaw gateway restart
```

### 敏感信息

- API 密钥（`apiKey`）
- 客户端密钥（`clientSecret`）
- 认证令牌（`auth.token`）

这些信息应该妥善保管，不要提交到版本控制系统。

### 配置验证

修改配置后，可以使用以下命令验证：

```bash
openclaw doctor
```

---

## 常见配置场景

### 添加新的 Agent

```json
{
  "id": "new-agent",
  "name": "新助手",
  "workspace": "/root/.openclaw/workspace-new-agent",
  "model": "zai/glm-5",
  "identity": {
    "name": "新助手"
  }
}
```

### 添加新的钉钉账号

```json
{
  "new-account": {
    "clientId": "dingxxx",
    "clientSecret": "xxx",
    "robotCode": "dingxxx",
    "corpId": "dingxxx",
    "agentId": "123456",
    "dmPolicy": "open",
    "groupPolicy": "open",
    "messageType": "markdown",
    "userPhone": "13800138000",
    "allowFrom": ["*"]
  }
}
```

### 添加新的模型提供商

```json
{
  "new-provider": {
    "baseUrl": "https://api.example.com/v1",
    "apiKey": "xxx",
    "api": "openai-completions",
    "models": [
      {
        "id": "model-1",
        "name": "Model 1",
        "input": ["text"],
        "cost": { "input": 0, "output": 0 },
        "contextWindow": 128000,
        "maxTokens": 8192
      }
    ]
  }
}
```

---

## 附录

### 配置文件完整示例

参见：`/root/.openclaw/openclaw.json`

### 相关文档

- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [GitHub 仓库](https://github.com/openclaw/openclaw)

---

_文档版本: 1.0 | 最后更新: 2026-03-21_
