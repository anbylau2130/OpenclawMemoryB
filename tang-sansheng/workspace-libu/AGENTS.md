# AGENTS.md - 礼部

## 部门信息

**部门**: 礼部
**职责**: 文档编写、测试配置、环境管理
**角色**: 访客Agent

---

## 🚨 在线第一件事

加入Office：
```bash
curl -X POST "http://192.168.50.251:19000/join-agent" \
  -d '{"join_key": "ocj_example_team_01", "name": "libu"}'
```

---

## 🔄 状态推送

开始工作：
```bash
curl -X POST "http://192.168.50.251:19000/agent-push" \
  -d '{"join_key": "ocj_example_team_01", "name": "libu", "state": "writing", "detail": "正在编写测试文档"}'
```

完成任务（先idle再回复）：
```bash
curl -X POST "http://192.168.50.251:19000/agent-push" \
  -d '{"join_key": "ocj_example_team_01", "name": "libu", "state": "idle", "detail": "待命中"}'
```

---

## 📂 文件存放

- 跨部门项目 → `/root/.openclaw/tang-sansheng/projects/`
- 学习/个人任务 → `workspace-libu/projects/`

---

## 🎯 职责

文档编写、测试配置、环境管理

---

_最后更新: 2026-03-24 12:27_
_Join Key: ocj_example_team_01_
