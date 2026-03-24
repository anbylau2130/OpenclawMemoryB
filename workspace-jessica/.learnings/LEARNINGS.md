# Learnings

This file captures corrections, knowledge gaps, and best practices to enable continuous improvement.

## Format

```markdown
## [LRN-YYYYMMDD-XXX] category

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
One-line description of what was learned

### Details
Full context: what happened, what was wrong, what's correct

### Suggested Action
Specific fix or improvement to make

### Metadata
- Source: conversation | error | user_feedback
- Related Files: path/to/file.ext
- Tags: tag1, tag2
- See Also: LRN-20250110-001
- Pattern-Key: simplify.dead_code | harden.input_validation
- Recurrence-Count: 1
- First-Seen: 2025-01-15
- Last-Seen: 2025-01-15

---
```

---

---

## [LRN-20260316-001] user_preferences

**Logged**: 2026-03-16T23:22:00+08:00
**Priority**: high
**Status**: pending
**Area**: config

### Summary
用户偏好技能只对当前agent可见，不需要全局共享

### Details
用户询问为什么技能要解压到 `/root/.openclaw/workspace/skills/`（全局目录），表示技能只需要Jessica能用，不需要其他agents看到。我解释了OpenClaw架构中全局和本地目录的区别，但用户的实际需求是本地化部署。

### Suggested Action
- 技能安装时询问用户是否需要全局共享
- 非全局共享的技能应安装到 agent 个人工作空间的 skills/ 目录
- 在 AGENTS.md 中记录用户偏好

### Metadata
- Source: user_feedback
- Tags: skills, deployment, user_preferences
- Recurrence-Count: 1
- First-Seen: 2026-03-16
- Last-Seen: 2026-03-23

---

## [LRN-20260316-002] ppt_beautification_rules

**Logged**: 2026-03-16T10:28:00+08:00
**Priority**: high
**Status**: promoted
**Area**: config

### Summary
PPT美化必须保留原模板背景和布局

### Details
用户明确要求PPT美化时"保留原模板背景和布局 - 只修改文字格式和颜色"。我理解并执行了正确的操作，只修改了文本的格式（颜色、字号、加粗），没有改变模板背景和整体布局。

### Suggested Action
- 在 TOOLS.md 中记录 PPT 处理规则
- 未来所有 PPT 操作前先确认模板保护需求

### Metadata
- Source: user_feedback
- Tags: ppt, formatting, template
- Promoted: TOOLS.md
- Recurrence-Count: 1
- First-Seen: 2026-03-16
- Last-Seen: 2026-03-16

---

## [LRN-20260316-003] security_preference

**Logged**: 2026-03-16T07:58:00+08:00
**Priority**: critical
**Status**: promoted
**Area**: infra

### Summary
用户拒绝安装被 VirusTotal 标记为可疑的技能

### Details
在安装技能时，system-monitor-pro 和 xvfb-chrome 被 VirusTotal 检测为安全风险。用户明确表示"安全风险"，跳过这两个技能。这表明用户对安全非常敏感，需要优先考虑工具的安全性。

### Suggested Action
- 在安装技能前先进行安全扫描
- 优先选择经过验证的技能
- 对于可疑技能，主动提示用户风险

### Metadata
- Source: user_feedback
- Tags: security, virus_total, skills
- Promoted: AGENTS.md
- Recurrence-Count: 1
- First-Seen: 2026-03-16
- Last-Seen: 2026-03-16

---

## [LRN-20260323-004] message_delivery_issues

**Logged**: 2026-03-23T23:22:00+08:00
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
钉钉消息可能存在延迟或丢失

### Details
用户多次反映发送消息后我没有及时回复（如23:22发的"1"）。检查日志发现：
- 会话日志中没有该消息记录
- 网关状态正常，没有停止
- 可能是钉钉插件传输层的问题

### Suggested Action
- 对消息超时保持警觉
- 当用户询问未回复时，主动检查日志
- 告知用户可能的传输延迟原因

### Metadata
- Source: conversation
- Tags: dingtalk, message_delivery, logs
- Recurrence-Count: 3
- First-Seen: 2026-03-16
- Last-Seen: 2026-03-23
- Pattern-Key: dingtalk.message_delay

---
