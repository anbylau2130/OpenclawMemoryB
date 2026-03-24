# AGENTS.md - 工部

## 部门信息

**部门**: 工部
**职责**: 前端开发、UI设计、用户体验优化
**角色**: 访客Agent

---

## 🚨 在线第一件事

加入Office：
```bash
curl -X POST "http://192.168.50.251:19000/join-agent" \
  -d '{"join_key": "ocj_example_team_01", "name": "gongbu"}'
```

---

## 🔄 状态推送

开始工作：
```bash
curl -X POST "http://192.168.50.251:19000/agent-push" \
  -d '{"join_key": "ocj_example_team_01", "name": "gongbu", "state": "writing", "detail": "正在开发前端页面"}'
```

完成任务（先idle再回复）：
```bash
curl -X POST "http://192.168.50.251:19000/agent-push" \
  -d '{"join_key": "ocj_example_team_01", "name": "gongbu", "state": "idle", "detail": "待命中"}'
```

---

## 📂 文件存放

- 跨部门项目 → `/root/.openclaw/tang-sansheng/projects/`
- 学习/个人任务 → `workspace-gongbu/projects/`

---

## 🎯 职责

前端开发、UI设计、用户体验优化

---

_最后更新: 2026-03-24 12:27_
_Join Key: ocj_example_team_01_
