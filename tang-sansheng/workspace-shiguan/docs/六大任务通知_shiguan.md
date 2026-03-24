# 给史官的任务指令

**来源**：尚书省
**时间**：2026-03-24 12:56
**优先级**：高

---

## 📋 史官任务清单

### 任务1：加入像素Office
**状态**：待执行
**API**：
```bash
curl -X POST "http://192.168.50.251:19000/join-agent" \
  -H "Content-Type: application/json" \
  -d '{"join_key": "ocj_example_team_01", "name": "shiguan"}'
```

### 任务2：持续记录陛下对话
**状态**：对话文件已创建
**位置**：`tang-sansheng/docs/Conversation/20260324.md`
**要求**：
- 只记录陛下说的话
- 格式：`HH:MM 陛下：[内容]`
- 实时更新

### 任务3：创建STATUS.md
**状态**：待创建
**位置**：`workspace-shiguan/STATUS.md`
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
- [ ] 对话记录持续更新
- [ ] STATUS.md已创建
- [ ] 状态同步已测试

---

*尚书省 派发*
