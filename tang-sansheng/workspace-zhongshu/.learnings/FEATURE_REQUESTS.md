# FEATURE_REQUESTS.md - 功能请求

_记录用户提出的功能需求和改进建议_

---

## 三省流程自动化协调（2026-03-24）

### 请求来源
- **用户**: 陛下（崔晓洋）
- **时间**: 2026-03-24
- **场景**: 云天佑项目开发

### 问题描述
中书省（我）没有自动使用三省流程协调各部门，导致一个人完成所有工作，违反了三省六部制度。

### 期望行为
1. 中书省起草方案后，**自动提交门下省审核**
2. 门下省审核通过后，**自动通知尚书省派发**
3. 尚书省**自动 spawn 六部**执行
4. 御史台**自动审查**代码质量

### 建议实现

#### 方案1：自动化流程脚本
```javascript
// 在 SOUL.md 中添加流程自动化提示
当完成任务起草后：
1. 自动使用 message 提交门下省
2. 等待门下省审核
3. 根据审核结果执行下一步
```

#### 方案2：流程检查清单
```markdown
## 三省流程检查清单

- [ ] 中书省起草方案
- [ ] 提交门下省审核
- [ ] 等待门下省回复
- [ ] 门下省通知尚书省
- [ ] 尚书省派发六部
- [ ] 六部执行任务
- [ ] 御史台审查结果
```

#### 方案3：工作流自动化
- 在 agents 配置中添加自动触发规则
- 中书省完成后自动调用门下省
- 门下省完成后自动调用尚书省

### 优先级
**高** - 这是三省制的核心流程

### 相关文件
- `SOUL.md` - 三省六部制度
- `AGENTS.md` - 各部门职责

---

## Self-Improving-Agent 自动记录（2026-03-24）

### 请求来源
- **用户**: 陛下（崔晓洋）
- **时间**: 2026-03-24

### 问题描述
没有自动使用 self-improving-agent 技能记录错误和学习。

### 期望行为
1. **遇到错误时**：自动记录到 `.learnings/ERRORS.md`
2. **学习新知识时**：自动记录到 `.learnings/LEARNINGS.md`
3. **发现最佳实践时**：自动记录并更新
4. **定期回顾**：检查是否有改进机会

### 建议实现

#### 方案1：错误自动捕获
```javascript
// 在执行命令时自动捕获错误
try {
  await execute(task);
} catch (error) {
  // 自动记录到 ERRORS.md
  logError({
    date: new Date(),
    error: error.message,
    context: task,
    fix: proposedFix
  });
}
```

#### 方案2：学习触发器
```markdown
## 学习触发器

当以下情况发生时，自动记录到 LEARNINGS.md：
1. 用户纠正我（"不对..."、"其实..."）
2. 发现更好的方法
3. API 调用失败
4. 知识过时
```

#### 方案3：定期回顾
```markdown
## 每周回顾

每周检查：
- [ ] ERRORS.md - 是否有重复错误？
- [ ] LEARNINGS.md - 是否有新的最佳实践？
- [ ] FEATURE_REQUESTS.md - 是否有可实现的功能？
```

### 优先级
**高** - 这是持续改进的基础

### 相关文件
- `skills/self-improving-agent/SKILL.md`

---

## Message 工具协作增强（2026-03-24）

### 请求来源
- **用户**: 陛下（崔晓洋）
- **时间**: 2026-03-24

### 问题描述
没有主动使用 message 工具协调各部门，导致协作失败。

### 期望行为
1. **自动识别协作需求**：当任务需要多部门时，主动使用 message
2. **消息格式标准化**：统一的消息格式和标签
3. **等待响应机制**：发送消息后等待回复，不急于自己执行

### 建议实现

#### 方案1：协作需求识别
```javascript
// 自动识别需要协作的任务
function identifyCollaboration(task) {
  if (task.needReview) {
    return { target: "menxia", action: "submit_for_review" };
  }
  if (task.needDispatch) {
    return { target: "shangshu", action: "request_dispatch" };
  }
  if (task.needAudit) {
    return { target: "yushitai", action: "request_audit" };
  }
}
```

#### 方案2：消息模板
```javascript
const messageTemplates = {
  submitForReview: (draft) => `
【诏令草案】
任务：${draft.title}
描述：${draft.description}
请门下省审核。
  `,
  
  requestDispatch: (approved) => `
【审核通过】
任务：${approved.title}
请尚书省派发六部执行。
  `,
  
  requestAudit: (code) => `
【审查请求】
代码：${code.location}
请御史台审查代码质量。
  `
};
```

### 优先级
**高** - 这是三省协作的关键

### 相关文件
- `TOOLS.md` - message 工具说明

---

## 配置验证工具（2026-03-24）

### 请求来源
- **用户**: 陛下（崔晓洋）
- **时间**: 2026-03-24

### 问题描述
误以为配置与 danghuangshang 不一致，浪费时间去验证。

### 期望行为
1. **配置自动验证**：启动时自动验证配置是否符合预期
2. **配置文档化**：清晰记录配置的设计原理
3. **配置错误提示**：配置错误时给出明确提示

### 建议实现

#### 方案1：配置验证脚本
```javascript
// 验证三省制配置
function validateSanshengConfig(config) {
  const zhongshu = config.agents.find(a => a.id === 'zhongshu');
  const shangshu = config.agents.find(a => a.id === 'shangshu');
  
  // 中书省不应该有 spawn 权限
  if (zhongshu.subagents) {
    warn('中书省不应该有 subagents 配置');
  }
  
  // 尚书省应该有 spawn 权限
  if (!shangshu.subagents || !shangshu.subagents.allowAgents) {
    error('尚书省必须有 subagents.allowAgents 配置');
  }
}
```

#### 方案2：配置文档
```markdown
## 三省制配置说明

### 中书省
- **权限**: 无 spawn 权限
- **原因**: 分权制衡，防止绕过审核

### 尚书省
- **权限**: 有 spawn 权限
- **原因**: 统一调度，六部只对尚书省负责
```

### 优先级
**中** - 提高配置理解

### 相关文件
- `openclaw.json` - 系统配置

---

_最后更新: 2026-03-24 08:38_
_维护者: 中书省（zhongshu）_
