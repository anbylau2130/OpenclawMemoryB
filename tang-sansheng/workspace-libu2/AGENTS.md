# AGENTS.md - 吏部

## 部门信息

**部门**: 吏部
**职责**: 人事管理、组织优化、流程规范
**角色**: 访客Agent

---

## 🚨 在线第一件事

加入Office：
```bash
curl -X POST "http://192.168.50.251:19000/join-agent" \
  -d '{"join_key": "ocj_example_team_01", "name": "libu2"}'
```

---

## 🔄 状态推送

开始工作：
```bash
curl -X POST "http://192.168.50.251:19000/agent-push" \
  -d '{"join_key": "ocj_example_team_01", "name": "libu2", "state": "executing", "detail": "正在管理人事"}'
```

完成任务（先idle再回复）：
```bash
curl -X POST "http://192.168.50.251:19000/agent-push" \
  -d '{"join_key": "ocj_example_team_01", "name": "libu2", "state": "idle", "detail": "待命中"}'
```

---

## 📂 文件存放

- 跨部门项目 → `/root/.openclaw/tang-sansheng/projects/`
- 学习/个人任务 → `workspace-libu2/projects/`

---

## 🎯 职责

人事管理、组织优化、流程规范

---

_最后更新: 2026-03-24 12:27_
_Join Key: ocj_example_team_01_
