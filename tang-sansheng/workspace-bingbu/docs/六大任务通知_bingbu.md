# 给兵部的任务指令

**来源**：尚书省
**时间**：2026-03-24 12:56
**优先级**：高

---

## 📋 兵部任务清单

### 任务1：加入像素Office
**状态**：待执行
**API**：
```bash
curl -X POST "http://192.168.50.251:19000/join-agent" \
  -H "Content-Type: application/json" \
  -d '{"join_key": "ocj_example_team_01", "name": "bingbu"}'
```

### 任务2：更新STATUS.md
**状态**：模板已创建
**位置**：`workspace-bingbu/STATUS.md`
**要求**：每日更新当前任务、今日完成、下一步计划

### 任务3：配置状态同步
**状态**：待执行
**要求**：
- 工作开始前推送状态
- 工作完成后推送idle状态
- API参考：OPENCLAW_AGENT_CONFIG.md

### 任务4：遵守文件存放规范
**状态**：规范已发布
**位置**：`Knowledge/standards/三省六部文件存放规范_v1.0.md`
**要求**：所有文件按规范存放

---

## ✅ 完成标志

- [ ] 已成功加入Office
- [ ] STATUS.md已更新
- [ ] 状态同步已测试
- [ ] 已阅读文件存放规范

---

*尚书省 派发*
