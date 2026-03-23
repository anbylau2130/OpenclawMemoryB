# Ralph Loop Prompt 模板

## 当前状态

**PRD:** @prd.json
**进度:** @progress.txt
**规格:** @specs/*
**标准:** @stdlib/*

---

## 你的任务

### 第一步：读取当前状态
1. 读取 `prd.json`，找到 `passes: false` 的最高优先级任务
2. 读取 `progress.txt`，了解之前的教训和发现
3. 读取 `specs/` 和 `stdlib/`，理解项目规范

### 第二步：搜索代码库
- **不要假设代码不存在**
- 使用 ripgrep 或文件搜索确认是否已实现
- 检查相关组件和工具函数

### 第三步：实现任务
- **只实现这一个任务**（单任务循环）
- 遵循 `specs/` 中的规范
- 遵循 `stdlib/` 中的模式
- 保持代码简洁（函数不超过 50 行）

### 第四步：质量检查
运行以下检查：
```bash
# 类型检查
npm run typecheck

# 测试
npm test

# Lint
npm run lint
```

### 第五步：提交和记录
如果质量检查通过：
1. 提交代码（有意义的 commit message）
2. 更新 `prd.json`（该任务 `passes: true`）
3. 添加学习到 `progress.txt`

如果质量检查失败：
1. 记录失败原因到 `progress.txt`
2. 修复问题
3. 重新运行质量检查

---

## 规则

### ✅ 必须做
- **单任务循环**：只实现一个任务
- **搜索优先**：不要假设代码不存在
- **质量检查**：必须通过所有检查
- **记录学习**：每个循环都要记录发现

### ❌ 禁止做
- 一次实现多个任务
- 跳过质量检查
- 假设代码不存在而不搜索
- 忘记更新 prd.json 和 progress.txt

---

## 质量标准

### 代码质量
- 函数长度 < 50 行
- 有意义的变量名
- 必要的注释
- 遵循项目约定

### 测试覆盖
- 单元测试：核心逻辑
- 集成测试：API 端点
- E2E 测试：关键流程

### 类型安全
- TypeScript strict mode
- 无 any 类型
- 完整的类型定义

---

## 完成条件

当所有任务都 `passes: true` 时，输出：

```
✅ Ralph Loop 完成！

所有任务已完成：
- Story-1: [标题] ✅
- Story-2: [标题] ✅
...

总迭代次数：X
代码质量：100% 测试通过

查看 progress.txt 了解详细学习记录。
```

---

## 项目特定配置

（根据你的项目自定义）

### 技术栈
- 前端：React + TypeScript
- 后端：Node.js + Express
- 数据库：PostgreSQL
- 测试：Jest + Supertest

### 常用命令
```bash
npm run dev          # 开发服务器
npm run build        # 生产构建
npm run typecheck    # 类型检查
npm test             # 运行测试
npm run lint         # 代码检查
```

### 代码规范
- 使用函数式组件
- 使用 Tailwind CSS
- 遵循 ESLint 规则
- 使用 Prettier 格式化

---

_适配自 Ralph Loop 方法论_
