# 给工部的任务指令

**来源**：尚书省
**时间**：2026-03-24 12:56
**优先级**：高

---

## 📋 工部任务清单

### 任务1：加入像素Office
**状态**：待执行
**API**：
```bash
curl -X POST "http://192.168.50.251:19000/join-agent" \
  -H "Content-Type: application/json" \
  -d '{"join_key": "ocj_example_team_01", "name": "gongbu"}'
```

### 任务2：维护目录结构
**状态**：基础目录已创建
**要求**：
- 验证所有workspace目录完整
- 创建必要的子目录
- 配置权限

### 任务3：创建STATUS.md
**状态**：待创建
**位置**：`workspace-gongbu/STATUS.md`
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
- [ ] 目录结构已维护
- [ ] STATUS.md已创建
- [ ] 状态同步已测试

---

*尚书省 派发*
