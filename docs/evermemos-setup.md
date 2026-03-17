# EverMemOS 记忆配置说明

## 概述

OpenClaw 已配置使用 EverMemOS 作为长期记忆存储。

## 服务器信息

- **地址：** http://192.168.50.251:1995
- **状态：** 运行中

## 配置详情

### 插件位置
`/root/.openclaw/plugins/evermemos-openclaw-plugin/`

### 配置参数
| 参数 | 值 | 说明 |
|------|-----|------|
| baseUrl | http://192.168.50.251:1995 | EverMemOS 服务器地址 |
| userId | openclaw | 默认用户ID（实际使用 agentId） |
| groupId | openclaw-agents | 组标识 |
| topK | 5 | 检索记忆数量 |
| memoryTypes | episodic_memory, profile, agent_skill, agent_case | 记忆类型 |
| retrieveMethod | hybrid | 检索方式 |

## Agent 记忆隔离

插件已修改，会自动从 sessionKey 提取 agentId 作为 userId：

- `main` → userId: main
- `jessica` → userId: jessica
- `blackwidow` → userId: blackwidow
- `captain` → userId: captain
- `thor` → userId: thor
- `ironman` → userId: ironman
- `hulk` → userId: hulk

每个 Agent 拥有独立的记忆空间。

## 配置日期

2026-03-15

## 参考

- EverMemOS: https://github.com/EverMind-AI/EverMemOS
- 插件文档: https://github.com/EverMind-AI/EverMemOS/tree/agent_memory/evermemos-openclaw-plugin
