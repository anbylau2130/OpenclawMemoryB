# Ralph Loop - OpenClaw 适配版

## 快速开始

### 1. 复制模板到项目

```bash
# 在项目根目录
mkdir -p specs stdlib

# 复制 PRD 模板
cp ~/.openclaw/workspace/skills/ralph-loop/templates/prd.json ./

# 复制进度文件
cp ~/.openclaw/workspace/skills/ralph-loop/templates/progress.txt ./

# 复制示例规格
cp -r ~/.openclaw/workspace/skills/ralph-loop/templates/specs/* ./specs/

# 复制标准库
cp -r ~/.openclaw/workspace/skills/ralph-loop/templates/stdlib/* ./stdlib/

# 复制脚本
mkdir -p scripts/ralph
cp ~/.openclaw/workspace/skills/ralph-loop/scripts/ralph-loop.sh scripts/ralph/
chmod +x scripts/ralph/ralph-loop.sh
```

---

### 2. 编辑 prd.json

```json
{
  "branchName": "feature/your-feature",
  "userStories": [
    {
      "id": "story-1",
      "title": "你的任务",
      "priority": 1,
      "passes": false,
      "acceptance": [
        "验收标准 1",
        "验收标准 2"
      ]
    }
  ]
}
```

---

### 3. 创建规格文档

在 `specs/` 目录创建详细的规格文档：

```bash
# 示例
specs/
├── feature-1-spec.md
├── feature-2-spec.md
└── api-spec.md
```

---

### 4. 运行 Ralph Loop

**手动执行（推荐学习）：**

在对话中说：
```
使用 Ralph Loop 方法完成任务。
请按照以下步骤：

1. 读取 prd.json（选择未完成任务）
2. 读取 progress.txt（了解之前的教训）
3. 读取 specs/ 和 stdlib/（理解规范）
4. 实现该任务（只做这一个）
5. 运行质量检查
6. 如果通过：
   - 提交代码
   - 更新 prd.json (passes: true)
   - 添加学习到 progress.txt
```

**自动化执行：**

```bash
./scripts/ralph/ralph-loop.sh [max_iterations]
```

---

## 目录结构

```
project/
├── prd.json              # 任务列表
├── progress.txt          # 学习笔记
├── specs/                # 规格文档
│   ├── auth-spec.md
│   └── api-spec.md
├── stdlib/               # 技术标准库
│   ├── patterns.md
│   └── conventions.md
└── scripts/ralph/        # Ralph 脚本
    └── ralph-loop.sh
```

---

## 核心原则

1. **单任务循环**：每次只做一个任务
2. **搜索优先**：不要假设代码不存在
3. **质量检查**：必须通过测试和类型检查
4. **记录学习**：每个循环都要记录发现

---

## 示例

### 第一次迭代

```
任务：Story-1 - 添加登录表单

1. 读取 prd.json ✅
2. 读取 progress.txt（空）✅
3. 搜索代码库：LoginForm 不存在 ✅
4. 创建 LoginForm.tsx ✅
5. 运行测试：通过 ✅
6. 提交代码 ✅
7. 更新 prd.json ✅
8. 添加学习到 progress.txt ✅

学习：
- React Hook Form 很好用
- Zod 验证效果很好
```

### 第二次迭代

```
任务：Story-2 - 添加注册表单

1. 读取 prd.json ✅
2. 读取 progress.txt（了解使用 React Hook Form）✅
3. 搜索代码库：发现可复用 LoginForm 模式 ✅
4. 创建 RegisterForm.tsx ✅
5. 运行测试：通过 ✅
6. 提交代码 ✅
7. 更新 prd.json ✅
8. 添加学习到 progress.txt ✅

学习：
- 复用了 LoginForm 的模式
- 注册需要额外的密码确认字段
```

---

## 参考资料

- **完整文档：** ~/.openclaw/workspace/skills/ralph-loop/SKILL.md
- **原始 Ralph：** https://ghuntley.com/ralph/
- **GitHub：** https://github.com/snarktank/ralph
