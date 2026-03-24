# 📚 学习记录

本文件记录三省六部系统的学习、改进和最佳实践。

---

## [LRN-20260324-001] 状态同步机制

**Logged**: 2026-03-24T13:02:00Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
建立三省六部agents的Office状态同步机制，确保工作状态实时准确。

### Details
- 所有agents必须先加入Office再开始工作
- 工作时同时更改state.json和推送状态
- 禁止推送用户信息、密钥等敏感信息
- 每15秒自动推送一次状态

### Suggested Action
为每个agent配置office-push脚本，建立state.json更新机制。

### Metadata
- Source: user_feedback
- Related Files: tang-sansheng/docs/OPENCLAW_AGENT_CONFIG.md
- Tags: office, 状态同步, 多agent

---

## [LRN-20260324-002] 文件存放规范

**Logged**: 2026-03-24T13:02:00Z
**Priority**: medium
**Status**: promoted
**Area**: config

### Summary
建立统一的文件存放规范，避免文件混乱。

### Details
- 项目分个人项目和跨部门项目
- 对话记录按日期存放
- 状态报告定期更新
- 遵守CLAUDE.md和OPENCLAW_AGENT_CONFIG.md

### Suggested Action
所有agents严格遵守文件存放规范。

### Metadata
- Source: user_feedback
- Related Files: Knowledge/standards/三省六部文件存放规范_v1.0.md
- Tags: 文件管理, 规范
- Promoted: Knowledge/standards/三省六部文件存放规范_v1.0.md

---
