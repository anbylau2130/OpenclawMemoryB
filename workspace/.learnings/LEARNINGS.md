# LEARNINGS - 学习与改进记录

记录重要的学习、纠正和最佳实践,用于持续改进。

---

## [LRN-20260326-004] correction

**Logged**: 2026-03-26T16:00:00+08:00
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
创建文件时使用错误路径,没有先验证实际目录结构

### Details
**错误发生：**
- 用户要求："让所有的agent都记住这个skill的使用,修改所有agent的agents.md文件"
- 我直接在`/root/.openclaw/agents/*/workspace/`创建AGENTS.md
- 没有先检查agents的实际工作空间位置

**错误分析：**
```
错误路径：/root/.openclaw/agents/*/workspace/AGENTS.md（12个文件）
正确路径：/root/.openclaw/tang-sansheng/workspace-*/AGENTS.md（10个文件）

错误原因：
1. 没有用ls命令检查目录结构
2. 想当然地认为agents/*/workspace/是工作空间
3. 没有询问用户确认路径
```

**错误影响：**
- ❌ 创建了12个错误位置的文件
- ❌ 需要删除并重新创建
- ❌ 浪费了2次git提交

**用户纠正：**
- 用户指出："删除你创建的文件,我的agents的工作空间在tang-sansheng目录下"
- 立即删除错误位置的文件
- 在正确的tang-sansheng/workspace-*/目录创建AGENTS.md

**根本原因：**
1. 没有验证目录结构就创建文件
2. 想当然地假设路径
3. 没有先询问用户

**正确流程：**
```bash
# 1. 先检查目录结构
ls -la /root/.openclaw/tang-sansheng/ | grep "workspace-"

# 2. 确认实际位置
find /root/.openclaw/tang-sansheng -type d -name "workspace-*"

# 3. 在正确位置创建文件
for workspace_dir in /root/.openclaw/tang-sansheng/workspace-*; do
  create_file "$workspace_dir/AGENTS.md"
done
```

### Suggested Action
1. **立即修正**：删除错误位置文件,在正确位置创建
2. **添加验证**：创建文件前先用`ls`或`find`验证目录结构
3. **更新文档**：在`AGENTS.md`中添加"路径验证"规则
4. **代码审查**：检查其他地方是否有类似的路径假设错误

### Metadata
- Source: user_feedback
- Related Files: `/root/.openclaw/tang-sansheng/workspace-*/AGENTS.md`
- Tags: 路径错误, 目录验证, 文件创建
- See Also: ERR-20260326-002
- Pattern-Key: path_verification
- Recurrence-Count: 1
- First-Seen: 2026-03-26
- Last-Seen: 2026-03-26

### Resolution
- **Resolved**: 2026-03-26T16:00:00+08:00
- **Commit**: 42a833a
- **Notes**: 删除错误位置文件,在正确的tang-sansheng目录创建AGENTS.md

---

## [LRN-20260326-003] best_practice
**Logged**: 2026-03-26T15:51:00+08:00
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
为所有agent添加Self-Improvement强制要求,确保每个agent都持续使用self-improving-agent技能

### Details
**背景：**
- 用户强调："让所有的agent都记住这个skill的使用,修改所有agent的agents.md文件"
- 这是2026-03-26成交量单位错误的后续改进措施
- 目的：防止类似错误再次发生

**执行过程（修正后）：**
1. 检查agents的实际工作空间位置（tang-sansheng目录）
2. 创建统一的AGENTS.md模板（包含Self-Improvement强制要求）
3. 为10个workspace目录创建AGENTS.md文件
4. 提交所有修改到版本控制系统（commit: 42a833a）
5. 推送到远程仓库

**核心内容：**
```markdown
## ⚠️ 强制要求：持续学习与自我改进
**所有agent必须持续使用self-improving-agent技能！**

### 📋 强制执行规则
1. 每次错误必须记录
2. 每次用户纠正必须记录
3. 数据验证是生命线
4. 每周审查待处理

### 📚 永久记住的教训
**2026-03-26 成交量单位错误（LRN-20260326-001）**
- Pattern-Key: data_unit_validation
- 这个错误让我明白数据单位验证是生命线
```

**影响范围:**
- ✅ 10个workspace目录添加强制要求
- ✅ 所有AGENTS.md已创建在正确位置
- ✅ 已提交到版本控制系统
- ✅ 已推送到远程仓库

### Suggested Action
1. ✅ 已完成：删除错误位置的文件
2. ✅ 已完成：在正确位置创建AGENTS.md
3. ✅ 已完成：提交到版本控制系统
4. ✅ 已完成:推送到远程仓库
5. ⏳ 待观察：验证所有agent是否遵循新要求

### Metadata
- Source: user_feedback
- Related Files: `/root/.openclaw/tang-sansheng/workspace-*/AGENTS.md`
- Tags: self-improvement, agent, 强制要求, 版本控制, 路径修正
- See Also: LRN-20260326-001, ERR-20260326-001, ERR-20260326-002
- Pattern-Key: agent_self_improvement_mandate
- Recurrence-Count: 2
- First-Seen: 2026-03-26
- Last-Seen: 2026-03-26

### Resolution
- **Resolved**: 2026-03-26T16:00:00+08:00
- **Commit**: 42a833a
- **Notes**: 修正路径错误,在正确的tang-sansheng目录为10个workspace创建AGENTS.md

---

## [LRN-20260326-001] correction
**Logged**: 2026-03-26T15:35:00+08:00
**Priority**: high
**Status**: promoted
**Area**: backend

### Summary
股票成交量数据单位错误导致严重的量价分析误判

### Details
**错误发生：**
- 分析三一重工（600031）成交量时,错误地将新浪财经API返回的数据单位理解为"手"
- 实际数据单位是"股",需要除以100才能转换为"手"

**错误分析:**
```
错误计算：
原始数据：41454369（股）
错误理解：4145.43万手
错误结论:放量6.45倍（与5日均量407万手对比）

正确计算：
原始数据:41454369（股）
正确转换:41454369 / 100 / 10000 = 41.45万手
正确结论:缩量下跌（三一重工正常日成交量30-50万手）
```

**错误影响:**
- ❌ 误判为"放量下跌"（恐慌抛售）
- ❌ 错误预测惯性下跌概率60%
- ❌ 给出过于悲观的操作建议
- ❌ 影响用户投资决策判断

**用户纠正:**
- 用户指出："今天明明是缩量呀"
- 立即承认错误并重新计算
- 修正为"缩量下跌"（抛压减轻）
- 修正预测:企稳反弹概率70%

**根本原因:**
1. 新浪财经API返回的`data[8]`字段单位是"股",不是"手"
2. 没有验证数据单位就进行计算
3. 没有与正常成交量范围对比验证

**正确流程:**
```python
# 获取原始数据
volume_shares = int(data[8])  # 单位：股

# 正确转换为万手
volume_wan_shou = volume_shares / 100 / 10000

# 验证合理性
# 三一重工正常日成交量：30-50万手
# 活跃日：50-80万手
# 清淡日：20-30万手
```

### Suggested Action
1. **立即修复**：在所有股票数据获取代码中添加单位转换注释
2. **添加验证**：成交量计算后验证是否在合理范围（1-200万手）
3. **更新文档**：在`TOOLS.md`中记录新浪财经API数据单位
4. **代码审查**：检查其他地方是否有类似的单位错误
5. **推广要求**：为所有agent添加Self-Improvement强制要求

### Metadata
- Source: user_feedback
- Related Files: `Knowledge/trading-strategies/code/` 下的所有股票数据获取代码
- Tags: 数据单位, 成交量, API, 量价分析, 新浪财经
- See Also: ERR-20260326-001
- Pattern-Key: data_unit_validation
- Recurrence-Count: 1
- First-Seen: 2026-03-26
- Last-Seen: 2026-03-26

### Resolution
- **Promoted**: AGENTS.md, SOUL.md, TOOLS.md
- **Date**: 2026-03-26T15:41:00+08:00
- **Notes**: 已推广到所有agent的AGENTS.md文件

---

## 使用说明

此文件记录重要的学习和改进,包括：
- 用户纠正（category: correction）
- 知识空白（category: knowledge_gap）
- 最佳实践（category: best_practice）

### 记录格式
```markdown
## [LRN-YYYYMMDD-XXX] category

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending | in_progress | resolved | promoted
**Area**: frontend | backend | infra | tests | docs | config

### Summary
一句话描述学到了什么

### Details
详细说明：发生了什么、错在哪、正确的是什么

### Suggested Action
具体的修复或改进建议

### Metadata
- Source: conversation | error | user_feedback
- Related Files: 相关文件路径
- Tags: 标签1, 标签2
- See Also: LRN-20250110-001（关联的学习条目）
- Pattern-Key: simplify.xxx | harden.xxx（可选）
- Recurrence-Count: 1（可选）
- First-Seen: 2025-01-15（可选）
- Last-Seen: 2025-01-15（可选）
```

### 定期审查
- 每周审查pending条目
- 解决已修复的问题
- 推广高价值学习到`AGENTS.md`或`TOOLS.md`
