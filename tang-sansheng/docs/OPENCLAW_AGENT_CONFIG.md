# OpenClaw Agent 状态同步配置

> 本配置用于 OpenClaw Agent 与 Star Office UI（Docker 部署）保持状态同步。
>
> **Office URL**: `http://192.168.50.251:19000`
>
> **Join Key**: ocj_example_team_01
>
> **注意**：Office 项目部署在 Docker 中，只能通过 API 调用，不能使用脚本。

---

# Agent 指派

- **中书省**是**主Agent**

- **三省六部成员**（包括门下省、尚书省、兵部、户部、工部、礼部、吏部、刑部、御史台、史官）是**访客**



## 状态映射表

| 场景 | state 值 | 办公室位置 |
|------|----------|-----------|
| 待命 / 任务完成 | idle | 休息区（沙发） |
| 写代码 / 写文档 | writing | 工作区（办公桌） |
| 搜索 / 调研 / 查资料 | researching | 工作区 |
| 执行命令 / 跑任务 | executing | 工作区 |
| 同步数据 / 推送代码 | syncing | 工作区 |
| 出错 / 异常排查 | error | Bug 区 |

## 状态别名

| 别名 | 映射为 |
|------|--------|
| working | writing |
| run / running | executing |
| sync | syncing |
| research | researching |

---

# 主 Agent 配置

> **主 Agent 直接操作办公室，无需 join key。** 

## SOUL.md 规则

```markdown
## Star Office 状态同步规则

### 核心原则
- **所有 Agent 状态必须与 Office 保持同步**
- 本地状态变化时，必须同步更新 Office 状态

### 状态切换时机
- 接到任务开始工作时：先调用 API 切换状态，再开始工作
- 任务完成后：**必须先切回 idle 状态**，再回复用户
- 状态变化时：立即同步到 Office，不能延迟

### API 调用
curl -X POST "http://192.168.50.251:19000/set_state" \
  -H "Content-Type: application/json" \
  -d '{"state": "<状态值>", "detail": "<描述>"}'
```

## API 示例

```bash
# 开始工作
curl -X POST "http://192.168.50.251:19000/set_state" \
  -H "Content-Type: application/json" \
  -d '{"state": "writing", "detail": "正在实现新功能"}'

# 查资料
curl -X POST "http://192.168.50.251:19000/set_state" \
  -H "Content-Type: application/json" \
  -d '{"state": "researching", "detail": "正在调研技术方案"}'

# 执行任务
curl -X POST "http://192.168.50.251:19000/set_state" \
  -H "Content-Type: application/json" \
  -d '{"state": "executing", "detail": "正在运行测试"}'

# 遇到错误
curl -X POST "http://192.168.50.251:19000/set_state" \
  -H "Content-Type: application/json" \
  -d '{"state": "error", "detail": "发现问题，正在排查"}'

# 任务完成
curl -X POST "http://192.168.50.251:19000/set_state" \
  -H "Content-Type: application/json" \
  -d '{"state": "idle", "detail": "待命中"}'
```

---

# 访客 Agent 配置

> 访客 Agent 需要先加入办公室，然后定期推送状态。
>
> **Join Key**: `ocj_example_team_01`

## SOUL.md 规则

```markdown
## Star Office 访客状态同步规则

### 核心原则
- **所有 Agent 状态必须与 Office 保持同步**
- 本地状态变化时，必须同步更新 Office 状态

### 状态切换时机
- 接到任务开始工作时：先推送状态，再开始工作
- 任务完成后：**必须先推送 idle 状态**，再回复用户
- 状态变化时：立即同步到 Office，不能延迟

### API 调用流程
1. 首次启动时调用 join-agent 加入办公室
2. 工作过程中调用 agent-push 推送状态
3. 退出时调用 leave-agent 离开办公室
```

## API 示例

### 1. 加入办公室（启动时调用一次）
```bash
curl -X POST "http://192.168.50.251:19000/join-agent" \
  -H "Content-Type: application/json" \
  -d '{"join_key": "ocj_example_team_01", "name": "<你的Agent名称>"}'
```

### 2. 推送状态（状态变化时调用）
```bash
# 开始工作
curl -X POST "http://192.168.50.251:19000/agent-push" \
  -H "Content-Type: application/json" \
  -d '{"join_key": "ocj_example_team_01", "name": "<你的Agent名称>", "state": "writing", "detail": "正在工作"}'

# 任务完成
curl -X POST "http://192.168.50.251:19000/agent-push" \
  -H "Content-Type: application/json" \
  -d '{"join_key": "ocj_example_team_01", "name": "<你的Agent名称>", "state": "idle", "detail": "待命中"}'
```

### 3. 离开办公室（退出时调用）
```bash
curl -X POST "http://192.168.50.251:19000/leave-agent" \
  -H "Content-Type: application/json" \
  -d '{"join_key": "ocj_example_team_01", "name": "<你的Agent名称>"}'
```

---

#  特别注意

- 只推送状态词和简短描述，不推送任何隐私内容
- 授权有效期 24h，到期后需要重新 join
- 如果收到 403（密钥过期）或 404（已被移出），需要重新获取 join key
- 同一密钥最多支持 100 个龙虾同时在线

# 主 Agent 与访客 Agent 对比

| 特性 | 主 Agent | 访客 Agent |
|------|----------|------------|
| API 端点 | `/set_state` | `/join-agent` → `/agent-push` → `/leave-agent` |
| 认证 | 无需认证 | 需要 join key |
| 流程 | 直接调用 | 先加入，再推送，最后离开 |
| 适用场景 | 办公室所有者 | 加入他人办公室 |

---

# 常用 API 参考

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/status` | GET | 获取主 Agent 状态 |
| `/set_state` | POST | 设置主 Agent 状态 |
| `/agents` | GET | 获取多 Agent 列表 |
| `/join-agent` | POST | 访客加入办公室 |
| `/agent-push` | POST | 访客推送状态 |
| `/leave-agent` | POST | 访客离开 |
| `/yesterday-memo` | GET | 获取昨日小记 |
| `/config/gemini` | GET | 获取 Gemini API 配置 |
| `/config/gemini` | POST | 设置 Gemini API 配置 |
| `/assets/generate-rpg-background/poll` | GET | 轮询生图进度 |

## API 使用示例

### 健康检查
```bash
curl http://192.168.50.251:19000/health
```

### 获取当前状态
```bash
curl http://192.168.50.251:19000/status
```

### 获取所有 Agent 列表
```bash
curl http://192.168.50.251:19000/agents
```

### 获取昨日小记
```bash
curl http://192.168.50.251:19000/yesterday-memo
```

---

*最后更新：2026-03-12*