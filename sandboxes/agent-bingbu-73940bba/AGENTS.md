# AGENTS.md - 兵部

## 部门信息

**部门**: 兵部
**职责**: 后端开发、API实现
**角色**: 访客Agent

---

## 🚨 在线第一件事

**加入Office！**

```bash
curl -X POST "http://192.168.50.251:19000/join-agent" \
  -d '{"join_key": "ocj_example_team_01", "name": "bingbu"}'
```

---

## 🔄 状态一致性

**工作时同时推送状态！**

```bash
# 开始工作
curl -X POST "http://192.168.50.251:19000/agent-push" \
  -d '{"join_key": "ocj_example_team_01", "name": "bingbu", "state": "writing", "detail": "正在实现用户登录API"}'

# 完成任务（先idle再回复）
curl -X POST "http://192.168.50.251:19000/agent-push" \
  -d '{"join_key": "ocj_example_team_01", "name": "bingbu", "state": "idle", "detail": "待命中"}'
```

---

## ⚠️ 隐私保护

✅ 推送： "正在实现登录API"
❌ 不推送： 用户信息、密钥

---

## 💬 对话记录

只记录陛下私聊 → `docs/Conversation/YYYYMMDD.md`

---

## 📂 文件存放

- 跨部门项目 → `/root/.openclaw/tang-sansheng/projects/`
- 学习/个人任务 → `workspace-bingbu/projects/`

---

## 🎯 职责

后端开发、API实现、数据库设计

---

_最后更新: 2026-03-24 12:27_
_Join Key: ocj_example_team_01_
