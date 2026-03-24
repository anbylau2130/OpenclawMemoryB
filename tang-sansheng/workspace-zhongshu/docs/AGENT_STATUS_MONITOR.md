# Agent状态监控系统

**创建时间**: 2026-03-24 09:55
**创建部门**: 中书省
**目的**: 让陛下能随时了解所有agent的当前工作状态

---

## 📊 当前活跃Sessions

### 最近30分钟内活跃的Agents

| Agent | 部门 | 最后活动 | 状态 |
|-------|------|---------|------|
| zhongshu | 中书省 | 09:55 | 🟢 活跃（当前对话） |
| main | 主Agent | 09:48 | 🟢 活跃（系统备份） |
| jessica | Jessica | 09:41 | 🟡 刚刚活跃 |

---

## 🔍 查看Agent状态的方法

### 方法1：查看Sessions列表（推荐）

```bash
# 查看最近30分钟活跃的agents
openclaw sessions list --active 30

# 或者在对话中问我
"查看所有agent状态"
```

### 方法2：查看各部门工作记录

```bash
# 查看中书省今日工作
cat /root/.openclaw/tang-sansheng/workspace-zhongshu/docs/Conversation/20260324.md

# 查看各部门报告
ls /root/.openclaw/tang-sansheng/workspace-*/docs/reports/
```

### 方法3：查看各部门状态文件

```bash
# 每个部门都有一个STATUS.md文件
cat /root/.openclaw/tang-sansheng/workspace-zhongshu/STATUS.md
cat /root/.openclaw/tang-sansheng/workspace-menxia/STATUS.md
cat /root/.openclaw/tang-sansheng/workspace-shangshu/STATUS.md
```

### 方法4：通过钉钉询问

```
在钉钉中直接对话某个部门：
"你现在在做什么？"
"你的工作进展如何？"
```

---

## 📋 建议的状态报告机制

### 标准化状态文件

每个部门应该维护一个 `STATUS.md` 文件：

```markdown
# [部门名称] - 当前状态

**最后更新**: YYYY-MM-DD HH:MM

## 当前任务
- 任务1：描述
- 任务2：描述

## 待处理
- [ ] 待办1
- [ ] 待办2

## 已完成（今日）
- [x] 完成1
- [x] 完成2

## 下一步计划
1. 计划1
2. 计划2
```

---

## 🔄 实时监控方案

### 方案1：定期状态更新

**建议**：每个部门每小时更新一次STATUS.md

### 方案2：任务开始/结束时通知

**建议**：开始或结束重要任务时，通过message通知陛下

### 方案3：每日工作报告

**建议**：每天结束时，各部门生成工作报告到 `docs/reports/`

---

## 📊 三省六部所有部门

| # | 部门 | 账号ID | 状态文件位置 |
|---|------|--------|-------------|
| 1 | 中书省 | zhongshu | workspace-zhongshu/STATUS.md |
| 2 | 门下省 | menxia | workspace-menxia/STATUS.md |
| 3 | 尚书省 | shangshu | workspace-shangshu/STATUS.md |
| 4 | 御史台 | yushitai | workspace-yushitai/STATUS.md |
| 5 | 兵部 | bingbu | workspace-bingbu/STATUS.md |
| 6 | 礼部 | libu | workspace-libu/STATUS.md |
| 7 | 户部 | hubu | workspace-hubu/STATUS.md |
| 8 | 工部 | gongbu | workspace-gongbu/STATUS.md |
| 9 | 吏部 | libu2 | workspace-libu2/STATUS.md |
| 10 | 刑部 | xingbu | workspace-xingbu/STATUS.md |

---

## 💡 陛下的使用建议

### 快速查看所有agent状态

**在钉钉中对中书省说**：
```
"查看所有agent状态"
"各部门现在在做什么"
"生成agent状态报告"
```

**我会立即**：
1. 查询sessions_list
2. 读取各部门STATUS.md
3. 生成统一的状态报告

---

## 🎯 立即可用的查询命令

### 陛下可以直接问我：

1. **"查看所有agent状态"**
   - 返回：所有活跃agents的列表

2. **"中书省现在在做什么"**
   - 返回：中书省的当前任务

3. **"兵部的工作进展"**
   - 返回：兵部的详细进展

4. **"生成状态报告"**
   - 返回：完整的HTML格式状态报告

5. **"各部门今日完成情况"**
   - 返回：所有部门今日工作汇总

---

## 📝 中书省当前状态（示例）

**最后更新**: 2026-03-24 09:55

### 当前任务
- ✅ 建立agent状态监控系统
- ✅ 通知所有部门对话记录规范
- ✅ 通知所有部门projects目录用途

### 今日完成
1. ✅ 通知所有部门CLAUDE.md更新（100%）
2. ✅ 通知所有部门projects目录用途（100%）
3. ✅ 通知所有部门对话记录规范（100%）
4. ✅ 建立对话记录系统
5. ✅ 更新三省六部文件存放规范
6. ✅ 记录到memory/2026-03-24.md
7. ✅ 建立agent状态监控系统

### 下一步计划
1. 等待陛下下一步指示
2. 协调各部门执行规范
3. 监控各部门对话记录实施情况

---

_创建时间: 2026-03-24 09:55_
_创建部门: 中书省_
