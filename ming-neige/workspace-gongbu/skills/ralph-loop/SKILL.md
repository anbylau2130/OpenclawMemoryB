---
name: ralph-loop
description: Ralph Loop 自主 AI 编程循环方法论。通过不断启动新的 AI 实例完成任务，直到所有 PRD 项完成。适用于大型项目、自动化编程、持续集成。关键词：Ralph、循环、自主、PRD、规格文档。
---

# Ralph Loop - 自主 AI 编程循环

Ralph Loop 是一个革命性的 AI 编程方法论，通过不断启动新的 AI 实例来完成任务，直到所有 PRD（产品需求文档）项完成。

## 核心原则

### 1. 单任务循环（One Item Per Loop）
- ✅ **每次循环只做一个任务**
- ✅ 每次循环都是**全新的上下文**（fresh instance）
- ❌ 不要试图在一个循环中完成多个任务

**正确示例：**
- "添加一个数据库列和迁移"
- "在现有页面添加一个 UI 组件"
- "更新一个 server action 的逻辑"

**错误示例（太大）：**
- "构建整个仪表板"
- "添加认证系统"

---

## 三阶段流程

```
┌─────────────┐
│   Generate  │  生成代码
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Backpressure│  质量检查
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Commit    │  提交和记录
└─────────────┘
```

---

## 记忆持久化

每个循环通过三个文件持久化记忆：

| 文件 | 用途 | 说明 |
|------|------|------|
| **prd.json** | 任务列表 | 用户故事和完成状态 |
| **progress.txt** | 学习笔记 | 每次迭代的发现和教训 |
| **specs/** | 规格文档 | 项目需求和设计规范 |

---

## 使用方法

### 1. 创建 PRD（产品需求文档）

```bash
# 在项目根目录创建 PRD
mkdir -p specs
touch prd.json progress.txt
```

**prd.json 格式：**
```json
{
  "branchName": "feature/auth",
  "userStories": [
    {
      "id": "story-1",
      "title": "Add login form",
      "priority": 1,
      "passes": false,
      "acceptance": [
        "Form validates email",
        "Shows error on invalid input",
        "Submits to /api/login"
      ]
    }
  ]
}
```

---

### 2. 创建规格文档

```bash
mkdir -p specs
```

**specs/auth-spec.md 示例：**
```markdown
# 认证系统规格

## 登录表单

### 要求
- 邮箱验证（正则表达式）
- 密码最小长度 8 位
- 错误提示友好

### 技术栈
- 表单：React Hook Form
- 验证：Zod
- API：fetch

### 文件位置
- 组件：src/components/LoginForm.tsx
- API：src/api/auth.ts
```

---

### 3. 创建技术标准库

```bash
mkdir -p stdlib
```

**stdlib/patterns.md 示例：**
```markdown
# 代码模式

## 错误处理
```typescript
try {
  const result = await api.call();
  return { success: true, data: result };
} catch (error) {
  console.error('API Error:', error);
  return { success: false, error: error.message };
}
```

## 日志
```typescript
logger.info('Operation completed', { userId, action });
```
```

---

### 4. 执行 Ralph Loop

**手动执行（推荐学习）：**
```
我需要使用 Ralph Loop 方法完成 prd.json 中的任务。
请按照以下步骤：

1. 读取 prd.json，选择最高优先级未完成任务
2. 读取 progress.txt，了解之前的教训
3. 读取 specs/ 和 stdlib/，理解项目规范
4. 实现该任务（只做这一个）
5. 运行质量检查（类型检查、测试）
6. 如果通过，提交代码并更新 prd.json
7. 记录学习到 progress.txt
```

**自动化执行：**
```bash
# 运行 Ralph Loop（最多 10 次迭代）
./scripts/ralph/ralph-loop.sh 10
```

---

## Prompt 模板

**通用 Ralph Loop Prompt：**

```markdown
# Ralph Loop 任务

## 当前状态
- PRD: @prd.json
- 进度: @progress.txt
- 规格: @specs/*
- 标准: @stdlib/*

## 你的任务
1. 读取 prd.json，找到 passes: false 的最高优先级任务
2. 读取 progress.txt，了解之前的学习
3. 搜索代码库（不要假设未实现）
4. 实现该任务（只做这一个）
5. 运行质量检查
6. 如果通过：
   - 提交代码
   - 更新 prd.json (passes: true)
   - 添加学习到 progress.txt

## 规则
- **单任务循环**：只实现一个任务
- **搜索优先**：不要假设代码不存在
- **质量检查**：必须通过测试和类型检查
- **记录学习**：每个循环都要记录发现

## 质量检查命令
- 类型检查：npm run typecheck
- 测试：npm test
- Lint：npm run lint
```

---

## 质量检查（Backpressure）

### 推荐的反向压力机制

| 语言 | 类型检查 | 测试 | Lint |
|------|---------|------|------|
| **TypeScript** | tsc --noEmit | Jest | ESLint |
| **Python** | pyrefly | pytest | pylint |
| **Rust** | cargo check | cargo test | clippy |
| **Go** | go vet | go test | golangci-lint |
| **C#** | dotnet build | dotnet test | StyleCop |

**Prompt 示例：**
```
After implementing functionality, run quality checks:
- Type check: npm run typecheck
- Tests: npm test
- Lint: npm run lint

If any check fails, fix the issues before committing.
```

---

## 迭代示例

### 第 1 次迭代

**输入：**
- prd.json（story-1: passes: false）
- progress.txt（空）

**执行：**
1. 读取 story-1：添加登录表单
2. 搜索代码库：发现没有 LoginForm.tsx
3. 创建 LoginForm.tsx
4. 运行测试：通过 ✅
5. 提交代码
6. 更新 prd.json（story-1: passes: true）
7. 添加到 progress.txt：
   ```
   [2026-03-23 21:47] Story-1 完成
   - 使用 React Hook Form 处理表单
   - Zod 验证效果很好
   - 注意：email 验证规则在 specs/auth-spec.md
   ```

---

### 第 2 次迭代

**输入：**
- prd.json（story-1: passes: true, story-2: passes: false）
- progress.txt（上次的学习）

**执行：**
1. 读取 story-2：添加注册表单
2. 读取 progress.txt：了解使用 React Hook Form
3. 搜索代码库：发现可以复用 LoginForm 的模式
4. 创建 RegisterForm.tsx
5. 运行测试：通过 ✅
6. 提交代码
7. 更新 prd.json（story-2: passes: true）
8. 添加到 progress.txt：
   ```
   [2026-03-23 22:15] Story-2 完成
   - 复用了 LoginForm 的模式
   - 注册需要额外的密码确认字段
   ```

---

## 完成条件

当所有任务都标记为 `passes: true` 时，Ralph Loop 输出：

```
✅ Ralph Loop 完成！

所有任务已完成：
- Story-1: Add login form ✅
- Story-2: Add register form ✅
- Story-3: Add logout button ✅

总迭代次数：3
总耗时：2.5 小时
代码质量：100% 测试通过

查看 progress.txt 了解详细学习记录。
```

---

## 常见陷阱

### ❌ 任务太大
```
错误："构建整个仪表板"
正确："添加销售图表组件到仪表板"
```

### ❌ 缺少质量检查
```
错误：没有测试和类型检查
正确：必须有 CI/CD 保持绿色
```

### ❌ 假设未实现
```
错误：AI 搜索后认为代码不存在（实际存在）
正确：明确要求"搜索代码库，不要假设未实现"
```

### ❌ 上下文溢出
```
错误：在主上下文中执行所有操作
正确：使用 subagents 分配工作
```

---

## 高级技巧

### 1. 使用 Subagents

**问题：** 主上下文窗口有限（约 170k）

**解决方案：**
```
使用 parallel subagents 搜索代码库。
主代理只作为调度器，不执行昂贵操作。
```

### 2. 规格文档驱动

**最佳实践：**
1. 项目开始时，与 AI 长期对话
2. 形成详细的规格文档
3. 每个循环都加载规格文档
4. 避免重复解释

### 3. 技术标准库

**创建可重用的代码模式：**
- 错误处理模式
- 日志记录模式
- 测试模式
- API 调用模式

### 4. 持续调优

**Ralph 会犯错，这是正常的：**
- 观察失败模式
- 添加"标志"到 prompt
- 像调吉他一样持续调整

---

## 项目结构

```
project/
├── prd.json              # 任务列表
├── progress.txt          # 学习笔记
├── specs/                # 规格文档
│   ├── auth-spec.md
│   ├── api-spec.md
│   └── ui-spec.md
├── stdlib/               # 技术标准库
│   ├── patterns.md
│   ├── conventions.md
│   └── testing.md
├── scripts/ralph/        # Ralph 脚本
│   ├── ralph-loop.sh
│   └── prompt.md
└── AGENTS.md             # 项目知识库
```

---

## 适用场景

### ✅ 适合
- Greenfield 项目
- 有明确规格的任务
- 有完善的测试体系
- 单一仓库

### ❌ 不适合
- 没有测试的项目
- 需要多代理协调的复杂系统
- 没有明确规格的探索性项目

---

## 核心哲学

### 1. 信任但验证
- 信任 AI 选择最重要的任务
- 但必须有反向压力机制验证

### 2. 持续调优
- Ralph 会犯错，这是正常的
- 通过添加"标志"到 prompt 来调优
- 像调吉他一样持续调整

### 3. 最终一致性
- 相信最终会完成
- 即使中间过程看起来混乱
- 通过反馈循环保证质量

### 4. 单体架构
- Ralph 是单体应用，不是微服务
- 避免多代理通信的复杂性
- 单一进程，单一仓库

---

## 参考资料

- **Geoffrey Huntley 博客：** https://ghuntley.com/ralph/
- **Ralph GitHub：** https://github.com/snarktank/ralph
- **交互式流程图：** https://snarktank.github.io/ralph/

---

_基于 Geoffrey Huntley 的 Ralph Pattern 改编，适配 OpenClaw 框架_
