# 给中书省的任务指令

**来源**：尚书省
**时间**：2026-03-24 12:56
**优先级**：高

---

## 📋 中书省任务清单

### 任务1：加入像素Office
**状态**：待执行
**API**：
```bash
curl -X POST "http://192.168.50.251:19000/join-agent" \
  -H "Content-Type: application/json" \
  -d '{"join_key": "ocj_example_team_01", "name": "zhongshu"}'
```

### 任务2：起草工作分配诏令
**状态**：待起草
**要求**：
- 明确各部门职责
- 设定完成时间
- 参考六大核心任务

### 任务3：创建STATUS.md
**状态**：待创建
**位置**：`workspace-zhongshu/STATUS.md`
**要求**：记录当前任务、今日完成、下一步计划

### 任务4：配置状态同步
**状态**：待执行
**要求**：
- 工作开始前推送状态
- 工作完成后推送idle状态
- API参考：OPENCLAW_AGENT_CONFIG.md

---

## ✅ 完成标志

- [ ] 已成功加入Office
- [ ] 工作分配诏令已起草
- [ ] STATUS.md已创建
- [ ] 状态同步已测试

---

*尚书省 派发*
