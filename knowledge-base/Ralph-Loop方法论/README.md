# Ralph Loop 方法论 - 完整知识库

> **学习时间**: 2026-03-23
> **来源**: https://github.com/snarktank/ralph | https://ghuntley.com/ralph/
> **整理者**: 司礼监

---

## 📖 概述

### 什么是 Ralph？

**Ralph** 是一个**自主 AI 代理循环**系统，它重复运行 AI 编码工具（如 Amp 或 Claude Code）直到所有 PRD（产品需求文档）项目完成。

**核心理念**：
```
while :; do cat PROMPT.md | claude-code; done
```

本质上，Ralph 就是一个 **Bash 循环**，但它的方法论远比这个简单的命令深刻得多。

### 核心特点

1. **每次迭代 = 全新上下文**
   - 每次循环启动一个新的 AI 实例
   - 上下文干净，没有历史包袱
   - 记忆通过文件持久化

2. **单体架构**
   - 单一操作系统进程
   - 垂直扩展
   - 每次循环执行一个任务

3. **最终一致性**
   - 需要信念和信任
   - 通过持续调优改进
   - 错误是可识别和可解决的

---

## 🎯 核心方法论

### 1. One Item Per Loop（每次循环一件事）

**关键原则**：
```
❌ 不要: 每次循环做多件事
✅ 应该: 每次循环只做一件事
```

**原因**：
- 上下文窗口有限（约170k tokens）
- 上下文使用越少，结果越好
- 单一任务更容易保证质量

**示例**：
```bash
✅ 正确的任务大小:
- 添加数据库列和迁移
- 向现有页面添加 UI 组件
- 更新服务器操作的逻辑
- 向列表添加筛选下拉框

❌ 过大的任务（需要拆分）:
- "构建整个仪表板"
- "添加认证系统"
- "重构整个 API"
```

### 2. Trust Ralph to Prioritize（信任 Ralph 优先级）

**核心理念**：
- 让 Ralph 决定什么是最重要的任务
- LLM 擅长推理实现优先级
- 完全放手（hands-off vibe coding）

**挑战**：
```
这会挑战你对"负责任工程"的认知边界
```

### 3. Deterministic Stack Allocation（确定性堆栈分配）

**每次循环必须分配的内容**：
```
1. 计划文档 (@fix_plan.md)
2. 规范文档 (specifications/)
3. 进度文件 (progress.txt)
4. PRD 状态 (prd.json)
```

**为什么重要**：
- 每次循环都是全新上下文
- 需要重新加载所有必要信息
- 确定性 = 可预测性

---

## 🔄 工作流程

### 完整流程

```
┌─────────────────────────────────────────┐
│  1. 创建 PRD（产品需求文档）              │
│     - 使用 PRD skill 生成                │
│     - 保存到 tasks/prd-[feature].md     │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  2. 转换为 Ralph 格式                    │
│     - 使用 Ralph skill 转换             │
│     - 生成 prd.json                     │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  3. 运行 Ralph 循环                      │
│     ./scripts/ralph/ralph.sh            │
└──────────────┬──────────────────────────┘
               ↓
         ┌─────────┐
         │  Loop   │ ←─────────┐
         └────┬────┘            │
              ↓                 │
    ┌─────────────────────┐     │
    │ 选择最高优先级任务   │     │
    │ (passes: false)     │     │
    └──────────┬──────────┘     │
               ↓                │
    ┌─────────────────────┐     │
    │ 实现单个故事        │     │
    └──────────┬──────────┘     │
               ↓                │
    ┌─────────────────────┐     │
    │ 运行质量检查        │     │
    │ - 类型检查          │     │
    │ - 测试              │     │
    └──────────┬──────────┘     │
               ↓                │
    ┌─────────────────────┐     │
    │ 通过?               │     │
    └──┬─────────────┬────┘     │
       │ Yes         │ No       │
       ↓             ↓          │
  ┌─────────┐   ┌─────────┐    │
  │ Commit  │   │  Fix    │────┘
  └────┬────┘   └─────────┘
       ↓
  ┌─────────────────────┐
  │ 更新 prd.json       │
  │ passes: true        │
  └──────────┬──────────┘
             ↓
  ┌─────────────────────┐
  │ 追加学习到          │
  │ progress.txt        │
  └──────────┬──────────┘
             ↓
  ┌─────────────────────┐
  │ 所有任务完成?       │
  └──┬──────────────┬───┘
     │ Yes          │ No
     ↓              ↓
┌─────────┐    ┌──────────┐
│ COMPLETE│    │ Continue │
└─────────┘    └──────────┘
```

### 关键步骤详解

#### 1. 创建 PRD

```bash
# 使用 PRD skill
Load the prd skill and create a PRD for [功能描述]

# 输出位置
tasks/prd-[feature-name].md
```

**PRD 应包含**：
- 功能描述
- 用户故事
- 验收标准
- 技术要求

#### 2. 转换为 prd.json

```bash
# 使用 Ralph skill
Load the ralph skill and convert tasks/prd-[feature].md to prd.json
```

**prd.json 格式**：
```json
{
  "branchName": "feature/add-auth",
  "userStories": [
    {
      "id": "story-001",
      "title": "添加登录页面",
      "priority": 1,
      "passes": false,
      "acceptanceCriteria": [
        "用户可以输入用户名和密码",
        "显示错误消息",
        "成功登录后跳转"
      ]
    }
  ]
}
```

#### 3. 运行 Ralph

```bash
# 使用 Amp（默认）
./scripts/ralph/ralph.sh [max_iterations]

# 使用 Claude Code
./scripts/ralph/ralph.sh --tool claude [max_iterations]
```

**Ralph 会自动**：
1. 创建功能分支
2. 选择最高优先级任务（`passes: false`）
3. 实现该任务
4. 运行质量检查
5. 提交代码（如果检查通过）
6. 更新 `prd.json`（标记 `passes: true`）
7. 追加学习到 `progress.txt`
8. 重复直到完成或达到最大迭代次数

---

## 📁 关键文件

### 文件结构

```
project/
├── scripts/ralph/
│   ├── ralph.sh           # Bash 循环脚本
│   ├── prompt.md          # Amp 提示模板
│   └── CLAUDE.md          # Claude Code 提示模板
├── tasks/
│   └── prd-[feature].md   # PRD 文档
├── prd.json               # 任务列表（包含 passes 状态）
├── progress.txt           # 学习记录（append-only）
├── AGENTS.md              # 模式和约定（关键！）
└── specifications/        # 规范文档
    ├── spec-001.md
    ├── spec-002.md
    └── ...
```

### 文件用途

| 文件 | 用途 | 重要性 |
|-----|------|--------|
| **ralph.sh** | Bash 循环脚本，启动新 AI 实例 | ⭐⭐⭐⭐⭐ |
| **prd.json** | 任务列表，跟踪完成状态 | ⭐⭐⭐⭐⭐ |
| **progress.txt** | 学习记录，append-only | ⭐⭐⭐⭐⭐ |
| **AGENTS.md** | 模式、约定、陷阱 | ⭐⭐⭐⭐⭐ |
| **specifications/** | 详细规范文档 | ⭐⭐⭐⭐ |
| **prompt.md** | AI 提示模板 | ⭐⭐⭐⭐ |

---

## 🎓 核心概念

### 1. Fresh Context Every Iteration（每次迭代全新上下文）

**记忆持久化方式**：
```
Git History → 之前的提交记录
progress.txt → 学习和经验
prd.json → 哪些任务已完成
AGENTS.md → 模式和约定
```

**为什么重要**：
- 避免上下文污染
- 每次都是"干净"的开始
- 依赖文件而不是内存

### 2. AGENTS.md Updates Are Critical（AGENTS.md 更新至关重要）

**为什么关键**：
- AI 编码工具自动读取这些文件
- 未来迭代受益于发现的模式
- 人类开发者也能受益

**应该记录什么**：
```markdown
## 模式发现
- 这个代码库使用 X 来实现 Y
- 数据库迁移位于 migrations/
- API 路由遵循 RESTful 规范

## 陷阱和注意事项
- 不要忘记修改 Z 时更新 W
- 组件 X 和 Y 有循环依赖
- 配置文件需要在部署前更新

## 有用的上下文
- 设置面板在 component X 中
- 测试数据库使用 SQLite
- CI/CD 流程在 .github/workflows/
```

### 3. Feedback Loops（反馈循环）

**Ralph 只在有反馈循环时有效**：
```
✅ 必须有:
- TypeScript 类型检查（捕获类型错误）
- 单元测试（验证行为）
- 集成测试（验证集成）
- CI 必须保持绿色
```

**为什么重要**：
```
错误的代码会在迭代中复合
→ 破坏的代码导致更多破坏
→ 反馈循环及时发现问题
```

### 4. Browser Verification for UI Stories（UI 故事的浏览器验证）

**前端任务必须包含**：
```json
{
  "acceptanceCriteria": [
    "Verify in browser using dev-browser skill"
  ]
}
```

**Ralph 会**：
1. 使用 dev-browser skill
2. 导航到页面
3. 与 UI 交互
4. 确认更改正常工作

### 5. Stop Condition（停止条件）

**循环退出条件**：
```
当所有故事都有 passes: true 时
→ 输出 <promise>COMPLETE</promise>
→ 循环退出
```

---

## 🛠️ 实践指南

### 安装和设置

#### 方法1: 复制到项目

```bash
# 从项目根目录
mkdir -p scripts/ralph
cp /path/to/ralph/ralph.sh scripts/ralph/
cp /path/to/ralph/prompt.md scripts/ralph/prompt.md
chmod +x scripts/ralph/ralph.sh
```

#### 方法2: 安装全局 Skills（Amp）

```bash
cp -r skills/prd ~/.config/amp/skills/
cp -r skills/ralph ~/.config/amp/skills/
```

#### 方法3: Claude Code Marketplace

```bash
/plugin marketplace add snarktank/ralph
/plugin install ralph-skills@ralph-marketplace
```

### 配置 Amp Auto-Handoff

**添加到 ~/.config/amp/settings.json**：
```json
{
  "amp.experimental.autoHandoff": { "context": 90 }
}
```

**作用**：
- 上下文满时自动切换
- 允许处理大故事

### 自定义 Prompt

**复制 prompt.md 后，为你的项目自定义**：
```markdown
# 项目特定的质量检查命令
- npm run typecheck
- npm run test
- npm run lint

# 代码库约定
- 使用 TypeScript strict 模式
- 组件使用 PascalCase 命名
- 测试文件放在 __tests__/ 目录

# 常见陷阱
- 不要直接修改 dist/ 目录
- 环境变量在 .env.local 中配置
- API 路由需要认证中间件
```

### 调试和监控

**检查当前状态**：
```bash
# 查看哪些故事已完成
cat prd.json | jq '.userStories[] | {id, title, passes}'

# 查看之前迭代的学习
cat progress.txt

# 检查 git 历史
git log --oneline -10
```

---

## 💡 最佳实践

### 1. Specifications-First（规范优先）

**流程**：
```
1. 与 LLM 进行长时间对话
2. 讨论需求和实现细节
3. 生成规范文档（每个文件一个规范）
4. 保存到 specifications/ 目录
```

**为什么重要**：
- 明确需求
- 减少歧义
- 每次循环确定性加载

### 2. Continuous Tuning（持续调优）

**方法**：
```
观察 Ralph 的行为
→ 发现不良模式
→ 更新 prompt.md
→ 添加"标志"到 AGENTS.md
→ Ralph 变得越来越好
```

**比喻**：
```
Ralph 像一个孩子
→ 在操场上玩耍
→ 摔倒了（犯错）
→ 你添加标志（"不要跳，滑下去"）
→ Ralph 学会了正确的方式
```

### 3. Eventual Consistency（最终一致性）

**心态**：
```
需要信念和耐心
→ Ralph 会测试你
→ 错误时不要责怪工具
→ 反思和调优
→ 最终会达到目标
```

### 4. Context Window Management（上下文窗口管理）

**策略**：
```
✅ 使用最少上下文
✅ 只加载必要信息
✅ 规范文档简洁明了
✅ 任务拆分合理

❌ 避免上下文浪费
❌ 不要加载不必要的大文件
❌ 不要让任务过大
```

---

## 🚫 常见陷阱

### 1. 任务过大

**问题**：
```
"构建整个仪表板"
→ 上下文不够
→ 代码质量差
→ 迭代失败
```

**解决**：
```
拆分为小任务:
1. 添加仪表板布局组件
2. 添加图表组件
3. 添加数据获取逻辑
4. 添加筛选功能
```

### 2. 缺乏反馈循环

**问题**：
```
没有测试
→ 错误累积
→ 代码越来越糟
→ 最终失败
```

**解决**：
```
必须有:
- 类型检查
- 单元测试
- 集成测试
- CI/CD
```

### 3. 不更新 AGENTS.md

**问题**：
```
不记录学习
→ 每次迭代重复犯错
→ 效率低下
```

**解决**：
```
每次迭代后:
- 记录发现的模式
- 记录遇到的陷阱
- 更新有用上下文
```

### 4. 过度干预

**问题**：
```
不信任 Ralph
→ 频繁干预
→ 破坏自主性
→ 失去 Ralph 的优势
```

**解决**：
```
放手让 Ralph 决定
→ 相信 LLM 的推理能力
→ 只在必要时干预
→ 通过调优而不是干预
```

---

## 📊 适用场景

### ✅ 适合 Ralph 的场景

```
✅ Greenfield 项目
✅ 新功能开发
✅ 重构任务
✅ API 开发
✅ UI 组件开发
✅ 测试编写
✅ 文档生成
```

### ❌ 不适合 Ralph 的场景

```
❌ 需要创造性设计
❌ 需要人类判断
❌ 需要快速原型
❌ 需要频繁变更
❌ 缺乏清晰规范
❌ 没有测试的项目
```

---

## 🔬 深度分析

### 为什么 Ralph 有效？

#### 1. 确定性优于非确定性

```
在不确定的世界中
→ Ralph 的"确定性缺陷"是优势
→ 错误可识别
→ 错误可解决
→ 通过调优改进
```

#### 2. 单一责任

```
每次循环只做一件事
→ 专注
→ 质量高
→ 上下文充足
→ 成功率高
```

#### 3. 持续学习

```
通过文件持久化记忆
→ 每次迭代都进步
→ 不重复犯错
→ 效率提升
```

#### 4. 自动化优先级

```
LLM 擅长推理优先级
→ 信任 AI
→ 减少人类决策
→ 加速开发
```

### Ralph vs. 其他方法

| 特性 | Ralph | 多代理系统 | 传统开发 |
|-----|-------|-----------|---------|
| **架构** | 单体 | 微服务 | - |
| **上下文** | 每次干净 | 共享 | - |
| **任务** | 每次一个 | 并行 | 手动 |
| **记忆** | 文件 | 内存 | 大脑 |
| **自动化** | 高 | 中 | 低 |

---

## 🎯 成功案例

### 案例1: 构建新编程语言

**项目**: CURSED esoteric programming language

**成果**:
```
✅ Ralph 从零开始构建
✅ 语言不在 LLM 训练数据中
✅ Ralph 学会了编程这个语言
✅ 生产级质量
```

### 案例2: 企业级低代码平台

**项目**: 云天佑（Tianyou）

**适用性**:
```
✅ 适合:
- 微服务架构
- 前端 UI 开发
- 测试编写
- 文档生成

📝 需要调整:
- 任务拆分更细
- 反馈循环更完善
- AGENTS.md 更新及时
```

---

## 📚 参考资料

### 官方资源

- **GitHub**: https://github.com/snarktank/ralph
- **Geoffrey Huntley's Blog**: https://ghuntley.com/ralph/
- **Amp Documentation**: https://ampcode.com/manual
- **Claude Code Documentation**: https://docs.anthropic.com/en/docs/claude-code

### 相关文章

- "deliberate intentional practice" - Geoffrey Huntley
- "LLMs are mirrors of operator skill" - Geoffrey Huntley
- "From Design doc to code: the Groundhog AI coding assistant" - Geoffrey Huntley

---

## 🚀 在三省六部中的应用

### 适合部门的 Ralph 应用

#### 兵部（技术架构）
```
✅ API 开发
✅ 数据库设计
✅ 微服务实现
✅ 代码重构
```

#### 礼部（前端 UI）
```
✅ 组件开发
✅ 页面实现
✅ UI 优化
✅ 浏览器验证
```

#### 工部（文档测试）
```
✅ 测试编写
✅ 文档生成
✅ 规范编写
✅ 质量检查
```

#### 刑部（安全权限）
```
✅ 权限实现
✅ 安全审计
✅ 日志系统
✅ 合规检查
```

### 三省六部 Ralph 配置

```bash
# 每个部门配置
scripts/ralph/
├── ralph.sh           # 循环脚本
├── prompt-bing.md     # 兵部提示模板
├── prompt-li.md       # 礼部提示模板
├── prompt-gong.md     # 工部提示模板
└── prompt-xing.md     # 刑部提示模板

# 共享文件
prd.json               # 统一任务列表
progress.txt           # 共享学习记录
AGENTS.md              # 共享模式和约定
```

---

## 📝 总结

### Ralph Loop 方法论核心要点

1. **简单即强大** - 本质是 Bash 循环
2. **每次一个任务** - 专注和质量
3. **全新上下文** - 通过文件持久化
4. **信任 AI** - 让 Ralph 决定优先级
5. **持续调优** - 观察和改进
6. **反馈循环** - 测试和验证
7. **记录学习** - AGENTS.md 是关键
8. **规范优先** - 明确需求
9. **最终一致性** - 需要信念和耐心
10. **上下文管理** - 珍惜每一个 token

### 实施建议

1. **从小项目开始** - 积累经验
2. **建立反馈循环** - 测试和 CI
3. **持续更新 AGENTS.md** - 记录学习
4. **合理拆分任务** - 不要过大
5. **相信过程** - 最终会成功

---

**创建时间**: 2026-03-23
**创建者**: 司礼监
**版本**: v1.0
**状态**: ✅ 完成
