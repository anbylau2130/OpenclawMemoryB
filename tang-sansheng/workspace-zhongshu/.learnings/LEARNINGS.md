# LEARNINGS.md - 学习日志

_记录开发过程中的学习经验和最佳实践_

---

## Message 工具批量通知最佳实践（2026-03-24 08:45）

### Category: `best_practice`

### 学习内容

**成功使用 message 工具批量通知三省六部所有部门**

### 执行过程

1. **识别协作需求**：
   - 陛下要求通知所有三省六部 agent 充分利用配置的 skills
   - 这是一个跨部门协调任务

2. **选择正确的工具**：
   - ✅ 使用 message 工具（正确）
   - ❌ 不使用 spawn（无权限且不需要）

3. **批量通知实施**：

**已通知部门（9个）**：

| 部门 | 账号ID | 状态 | 消息ID | 推荐技能 |
|------|--------|------|--------|----------|
| 门下省 | menxia | ✅ 成功 | FllU5JSRZ0JbHbe5N4Z5VNkXv61fgjKdoQmGNgRzBtc= | code-review, TaskMaster, clawlist |
| 尚书省 | shangshu | ✅ 成功 | DIcK5eFBsJ9TyH2p2yech82bjCDhgX7urHV+gQwV7yM= | TaskMaster, quadrants, clawlist |
| 御史台 | yushitai | ✅ 成功 | z3KybZKwLDjbSXGvyrtXuWGt7ogqg8rg43DdaiwEaZo= | code-review, github, discord-message-guard |
| 兵部 | bingbu | ✅ 成功 | mKTyNtowI5tuzEL1afTVmdgiuHAyF9sDJlRCz9iMQK8= | github, code-review, ralph-loop, shell-script, context7 |
| 礼部 | libu | ✅ 成功 | eIbrcbelYpfLzCWBYwJA9AAIDXjruvweBFdRcyz0iho= | brains, frontend-design, novel-prose, novel-worldbuilding, browser-use |
| 户部 | hubu | ✅ 成功 | Qb3WnISf3xIQx98ynUMoy673fQwAN9XuNibA/cSb144= | ontology, notion, TaskMaster, quadrants |
| 工部 | gongbu | ✅ 成功 | UySN7p7oC61/gIms9XowyO7KjQL2Ilk0dQWIz/lm3lk= | system-info, system-resource-monitor, shell-script, github, healthcheck |
| 吏部 | libu2 | ✅ 成功 | UiXrq6GlZHesfOB4k1ZUIkWh1rCuiyneKSfwNyxyEGI= | TaskMaster, quadrants, clawlist, notion |
| 刑部 | xingbu | ✅ 成功 | jGXSya98CklV3jLUfclixYFQNiAnmqF/Oe+5c/5zbBk= | code-review, github, discord-message-guard, self-improving-agent, TaskMaster |

4. **定制化内容**：
   - 根据各部门职责推荐相关技能
   - 提供具体的技能使用方法
   - 说明技能的触发词和用途

### 关键成功因素

1. **定制化推荐**：
   - 每个部门收到与其职责相关的技能推荐
   - 不是通用的消息，而是针对性的指导

2. **清晰的指引**：
   ```bash
   # 如何查看技能文档
   cat skills/{技能名}/SKILL.md
   
   # 如何查看完整技能列表
   cat TOOLS.md
   ```

3. **统一的格式**：
   - 标题：【技能使用通知】
   - 结构：重点推荐 → 使用方法 → 完整列表
   - 落款：中书省 + 日期

### 统计数据

- **总通知数**: 9
- **成功数**: 9
- **失败数**: 0
- **成功率**: 100%
- **定制化程度**: 100%（每个部门都收到定制内容）
- **推荐技能总数**: 30+ 个（覆盖所有部门核心职能）

### 最佳实践模板

```javascript
// 批量通知模板
const departments = ['menxia', 'shangshu', 'yushitai', 'bingbu', 'hubu', 'libu', 'gongbu', 'libu2', 'xingbu'];

departments.forEach(dept => {
  const recommendedSkills = getSkillsForDepartment(dept);
  
  message({
    accountId: dept,
    channel: "dingtalk",
    message: `
【技能使用通知】请充分利用配置的技能！

${dept}请注意：

## 🎯 重点推荐技能

${recommendedSkills.map(skill => `
### ${skill.name}
- **触发词**：${skill.triggers}
- **用途**：${skill.usage}
- **查看**：\`cat skills/${skill.name}/SKILL.md\`
`).join('\n')}

## 📖 完整技能列表（29个）
查看：\`cat TOOLS.md\`

中书省
2026-03-24
    `
  });
});
```

### 应用场景
- 批量部署新政策
- 批量通知新工具
- 批量更新工作流程
- 批量培训新技能

### 相关文件
- `TOOLS.md` - 完整技能列表
- `skills/*/SKILL.md` - 各技能文档

---

## Self-Improving-Agent 技能部署（2026-03-24 08:42）

### Category: `best_practice`

### 学习内容

**成功使用 message 工具协调三省六部**

### 执行过程

1. **识别协作需求**：
   - 陛下要求通知所有三省六部 agent 使用 self-improving-agent
   - 这是一个跨部门协调任务

2. **选择正确的工具**：
   - ❌ 不能使用 sessions_spawn（中书省无权限）
   - ✅ 使用 message 工具（正确的协作方式）

3. **实施通知**：
   - 门下省（menxia）✅
   - 尚书省（shangshu）✅
   - 御史台（yushitai）✅
   - 兵部（bingbu）✅
   - 户部（hubu）✅
   - 礼部（libu）✅
   - 工部（gongbu）✅
   - 吏部（libu2）✅
   - 刑部（xingbu）✅

4. **统一消息格式**：
   ```
   【技能启用通知】
   请XX立即启用 self-improving-agent 技能！
   
   ## 📋 要求
   1. 创建 .learnings 目录
   2. 创建 ERRORS.md, LEARNINGS.md, FEATURE_REQUESTS.md
   3. 记录部门特定内容
   ```

### 关键认知

1. **Message 工具的正确使用**：
   - 必须指定 accountId（目标部门ID）
   - 必须指定 channel（dingtalk）
   - 消息内容要清晰明确

2. **三省协作的正确流程**：
   ```
   中书省（我）→ message → 其他部门
   ```

3. **跨部门通知的成功要素**：
   - 统一的消息格式
   - 明确的要求
   - 部门特定的内容指导

### 成功指标

- ✅ 9个部门全部通知成功
- ✅ 返回 messageId 确认送达
- ✅ 消息格式规范统一
- ✅ 内容针对各部门职责定制

### 应用场景
- 任何需要跨部门协调的任务
- 任何需要通知多个部门的场景
- 任何需要统一部署政策的任务

### 最佳实践

```javascript
// 跨部门通知模板
message({
  accountId: "目标部门ID",
  channel: "dingtalk",
  message: `
【通知标题】

请XX立即执行某项任务！

## 📋 要求
1. 具体要求1
2. 具体要求2

## 🎯 目的
说明目的和意义

发送部门
日期
  `
})
```

### 相关文件
- `TOOLS.md` - message 工具说明
- `SOUL.md` - 三省六部制度

---

## 三省制分权制衡原理（2026-03-24 08:36）

### Category: `best_practice`

### 学习内容

**三省制的分权制衡设计**：

```
皇帝（陛下）
   ↓
中书省 → 门下省 → 尚书省 → 六部
(起草)   (审核)   (派发)   (执行)
   ↓         ↓         ↓        ↓
无 spawn  无 spawn  有 spawn  无 spawn
```

### 关键认知

1. **中书省无 spawn 权限是正确设计**
   - 目的：防止中书省绕过审核直接派发
   - 体现三省制的分权制衡原则

2. **尚书省是唯一有 spawn 权限的部门**
   - 目的：统一调度，避免多头指挥
   - 六部只对尚书省负责

3. **配置与 danghuangshang 完全一致**
   - 不是配置错误
   - 是三省制的正确实现

### 最佳实践

```javascript
// 正确的三省流程：

// 1. 中书省起草
起草诏令草案.md

// 2. 提交门下省审核
message({
  accountId: "menxia",
  channel: "dingtalk",
  message: "【诏令草案】请审核..."
})

// 3. 门下省审核后，通知尚书省
message({
  accountId: "shangshu",
  message: "【审核通过】请派发..."
})

// 4. 尚书省 spawn 六部
sessions_spawn({
  agentId: "bingbu",
  task: "开发后端..."
})
```

### 相关文件
- `SOUL.md` - 三省六部制度
- `AGENTS.md` - 各部门职责

---

_最后更新: 2026-03-24 08:50_
_维护者: 中书省（zhongshu）_

---

## 批量通知启用所有 Skill（2026-03-24 08:50）

### Category: `best_practice`

### 学习内容

**成功通知所有三省六部启用所有 29 个 skill**

### 背景
陛下要求："让他们启用所有的skill，skill是工具，帮助你们提升效率的"

### 执行过程

1. **理解核心要求**：
   - 不仅仅是推荐相关skill
   - 要让所有部门启用**所有29个skill**
   - 强调skill是工具，能提升效率

2. **定制化通知**：
   每个部门都收到：
   - 完整的29个skill列表
   - 与职责相关的重点skill说明
   - 如何使用skill的具体流程
   - 鼓励主动探索所有skill

3. **通知统计**：
   | 部门 | 账号ID | 状态 | 消息ID |
   |------|--------|------|--------|
   | 门下省 | menxia | ✅ | ZccurDtnvnzcGpV0usMlKOXtltNqH9gjOVhioj5WLlA= |
   | 尚书省 | shangshu | ✅ | xzWZ4zaDzyPEsUI4zCmdOIoR/gLHmGkoreJ5Wuk9OKk= |
   | 御史台 | yushitai | ✅ | y3Ia+wZ4XPLoNynu75U6VquD5RUqAQAU/mlryoHmJ1c= |
   | 兵部 | bingbu | ✅ | l1jqPPXtmh2oRow4p7htNuerX4xp/Teq+pH3SyR0aCE= |
   | 礼部 | libu | ✅ | 7Wh/ONOMePPtGFjM0FHyW08zowdtyA8GJ/bF4Fla68c= |
   | 户部 | hubu | ✅ | GXUMDNTaUzRT6Dt1q+bt7ntuCSbNT1E0l7quOlgmdV4= |
   | 工部 | gongbu | ✅ | 6AiXGJplCkEzZThf95VQYwfvKY7mDz/A3Mgs8nMHfXU= |
   | 吏部 | libu2 | ✅ | lJijIJD0j7u5T0SDPv0pnIqQIsAtF6/Ri0Zuu0SKfgE= |
   | 刑部 | xingbu | ✅ | Xwg6L24Gllgbfm5qz9YfokVYnV/KSrgXCIOe/+UnDqg= |

### 关键成功因素

1. **强调核心理念**：
   - "Skill 是工具，是帮助你们提升效率的"
   - "不要只用推荐的几个，要主动探索所有 29 个 skill"

2. **完整列表展示**：
   - 提供所有29个skill的完整列表
   - 分类展示（创意、项目、开发、网络等）
   - 说明每个skill的用途

3. **使用场景指导**：
   - 提供具体的使用流程
   - 组合使用示例
   - 鼓励主动探索

4. **定制化内容**：
   - 根据部门职责强调相关skill
   - 但同时强调要使用所有skill
   - 提供部门特定的使用建议

### 统计数据

- **总通知数**: 9
- **成功数**: 9
- **失败数**: 0
- **成功率**: 100%
- **Skill覆盖**: 29个（100%）
- **定制化程度**: 100%

### 最佳实践

```javascript
// 批量通知启用skill模板
message({
  accountId: "部门ID",
  channel: "dingtalk",
  message: `
【重要通知】请立即启用所有 29 个 skill！

XX部请注意：

## 🎯 核心理念
**Skill 是工具，是帮助你们提升效率的！**
**不要只用推荐的几个，要主动探索所有 29 个 skill！**

## 📚 完整的 29 个 Skill 列表
[提供完整列表]

## 🚀 XX部使用建议
[提供定制化建议]

**XX部，请充分利用所有 29 个 skill！**
**让 skill 成为你XX工作的得力助手！**
  `
})
```

### 应用场景
- 批量部署新工具
- 批量通知新功能
- 批量培训新技能
- 统一提升团队能力

### 相关文件
- `TOOLS.md` - 完整skill列表
- `skills/*/SKILL.md` - 各skill文档
