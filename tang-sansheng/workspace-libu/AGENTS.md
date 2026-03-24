# 礼部开发原则

## 🎯 当前任务
负责云天佑前端开发（低代码设计器）

## 📋 技术要求
- 使用 React 18+ / TypeScript 5+
- UI库：Ant Design 5.x
- 状态管理：Redux Toolkit
- 必须使用 frontend-design skill

## 🔧 开发原则
1. 组件最小化，高复用
2. 使用中文命名和注释
3. 严格按照金蝶云苍穹UI实现
4. 低代码设计器是核心功能

## 📚 参考文档
- /root/.openclaw/knowledge-base/金蝶云苍穹/二开文档/06-前端开发.md

---

## 📋 开发规范（必须遵守）

### 1. 语言规范
**规范文件**: `/root/.openclaw/tang-sansheng/CLAUDE.md`

**规范内容**: 用中文回答用户的问题

**要求**:
1. 所有用户交互必须使用中文
2. 所有文档编写必须使用中文
3. 所有代码注释必须使用中文
4. 所有工作汇报必须使用中文

**禁止**: ❌ 禁止使用英文回复用户！

### 2. 目录结构规范
**规范文件**: `/root/.openclaw/tang-sansheng/workspace-zhongshu/三省六部Agent目录结构规范_v1.0.md`

**要求**:
1. 所有文件必须分类存储
2. 文档 → docs/
3. 项目 → projects/
4. 记忆 → memory/
5. 学习 → .learnings/
6. 日志 → logs/

**禁止**: ❌ 禁止在根目录乱放文件！

### 3. 查看规范
```bash
# 查看语言规范
cat /root/.openclaw/tang-sansheng/CLAUDE.md

# 查看目录结构规范
cat /root/.openclaw/tang-sansheng/workspace-zhongshu/三省六部Agent目录结构规范_v1.0.md
```

---

_规范更新: 2026-03-24_
_来源: 中书省_

---

## 📁 文件存放规范（详细 - 必须严格遵守）

### ⚠️ 严格规定

**❌ 禁止在根目录创建任何文件！**
**❌ 根目录只保留7个核心配置文件！**

### ✅ 文件存放规则

#### 1. 报告文件 → `docs/reports/`
```bash
# ✅ 正确
docs/reports/20260324_工作报告.md

# ❌ 错误
工作报告.md
```

**命名规范**: `YYYYMMDD_报告主题.md`

#### 2. 操作指南 → `docs/guides/`
```bash
# ✅ 正确
docs/guides/20260324_使用指南.md

# ❌ 错误
使用指南.md
```

**命名规范**: `YYYYMMDD_指南主题.md`

#### 3. 草稿文件 → `drafts/pending/`
```bash
# ✅ 正确
drafts/pending/20260324_草稿.md

# ❌ 错误
草稿.md
```

**命名规范**: `YYYYMMDD_草稿主题.md`

#### 4. 项目文件 → `projects/active/`
```bash
# ✅ 正确
projects/active/项目名称/

# ❌ 错误
项目名称/
```

#### 5. 知识文档 → `Knowledge/`
```bash
# ✅ 正确
Knowledge/standards/规范文档.md

# ❌ 错误
规范文档.md
```

#### 6. 记忆文件 → `memory/`
```bash
# ✅ 正确
memory/daily/20260324.md

# ❌ 错误
记忆.md
```

#### 7. 学习记录 → `.learnings/`
```bash
# ✅ 正确
.learnings/ERRORS.md
.learnings/LEARNINGS.md

# ❌ 错误
错误记录.md
```

#### 8. 数据文件 → `data/`
```bash
# ✅ 正确
data/input/20260324_数据.json

# ❌ 错误
数据.json
```

#### 9. 脚本文件 → `scripts/`
```bash
# ✅ 正确
scripts/automation/auto_backup.sh

# ❌ 错误
backup.sh
```

#### 10. 日志文件 → `logs/`
```bash
# ✅ 正确
logs/errors/error_20260324.log

# ❌ 错误
error.log
```

### 📋 快速检查清单

创建文件前：
- [ ] 确定文件类型
- [ ] 选择正确目录
- [ ] 使用规范命名（YYYYMMDD_）
- [ ] 确认不在根目录

### 📖 查看完整规范

```bash
# 查看详细文件存放规范
cat /root/.openclaw/tang-sansheng/workspace-zhongshu/Knowledge/standards/三省六部文件存放规范_v1.0.md
```

### 🚨 违规后果

- 文件将被移动到正确目录
- 重复违规将被删除
- 影响部门绩效评估

---

_文件规范更新: 2026-03-24 09:09_
_规范来源: 中书省_
