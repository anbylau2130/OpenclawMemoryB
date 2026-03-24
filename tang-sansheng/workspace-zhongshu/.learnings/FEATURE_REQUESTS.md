# 💡 功能请求

本文件记录用户请求的新功能、改进建议和能力扩展。

---

## [FEAT-20260324-001] self-improving-agent技能

**Logged**: 2026-03-24T13:02:00Z
**Priority**: high
**Status**: pending
**Area**: config

### Requested Capability
启用self-improving-agent和29个其他skills，让所有agents具备自我改进能力。

### User Context
陛下要求充分利用配置的技能，提升三省六部系统的智能化水平。

### Complexity Estimate
medium

### Suggested Implementation
1. 创建.learnings目录结构
2. 为每个agent配置skills访问权限
3. 建立学习日志记录机制
4. 定期review和promote学习内容

### Metadata
- Frequency: first_time
- Related Features: 状态管理, 文件规范

---

## [FEAT-20260324-002] 自动对话记录

**Logged**: 2026-03-24T13:02:00Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Requested Capability
自动记录陛下对话到docs/Conversation/YYYYMMDD.md

### User Context
需要保存陛下的所有对话，便于后续查阅和历史追溯。

### Complexity Estimate
simple

### Suggested Implementation
建立自动记录机制，每次对话后追加到对应日期文件。

### Metadata
- Frequency: recurring
- Related Features: 史官职责

---
