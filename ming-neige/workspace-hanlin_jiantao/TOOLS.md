# TOOLS.md - 可用技能工具箱

本 workspace 已安装 26 个技能，按类别分组如下。使用前请阅读对应技能的 SKILL.md 文件。

---

## 📦 项目管理类

### 1. TaskMaster - 项目管理和任务委派
**用途：** 复杂项目分解、任务分配、进度追踪
**触发词：** 项目管理、任务分解、委派、进度
**使用方法：**
```bash
# 查看技能文档
cat skills/TaskMaster/SKILL.md

# 适用场景
- 多步骤项目需要分解
- 需要分配任务给不同模型
- 需要追踪进度和预算
```

### 2. clawlist - 任务追踪和验证
**用途：** 任务清单管理、验证检查、进度跟踪
**触发词：** 任务清单、验证、检查清单
**使用方法：**
```bash
cat skills/clawlist/SKILL.md

# 适用场景
- 需要系统性执行任务
- 需要验证完成度
- 需要检查点管理
```

### 3. quadrants - 艾森豪威尔矩阵任务管理
**用途：** 任务优先级管理、重要紧急分类
**触发词：** 优先级、四象限、任务分类
**使用方法：**
```bash
cat skills/quadrants/SKILL.md
```

### 4. todoist - Todoist 任务管理
**用途：** Todoist 平台任务同步
**触发词：** todoist、任务同步
**使用方法：**
```bash
cat skills/todoist/SKILL.md
```

---

## 💻 开发工具类

### 5. github - GitHub 交互
**用途：** PR、Issue、CI/CD 操作
**触发词：** github、pr、issue、ci
**使用方法：**
```bash
cat skills/github/SKILL.md

# 常用命令
gh pr list
gh issue create
gh run watch
```

### 6. code-review - 代码审查
**用途：** 代码质量检查、安全审查、性能分析
**触发词：** 代码审查、code review
**使用方法：**
```bash
cat skills/code-review/SKILL.md
```

### 7. ralph-loop - 自主编程循环
**用途：** 自动化编程循环、PRD 驱动开发
**触发词：** ralph、循环编程、prd
**使用方法：**
```bash
cat skills/ralph-loop/SKILL.md

# 核心流程
Generate → Backpressure → Commit
```

### 8. shell-script - Shell 脚本
**用途：** Shell 脚本编写、自动化
**触发词：** shell、脚本、自动化
**使用方法：**
```bash
cat skills/shell-script/SKILL.md
```

---

## 🌐 浏览器与网络类

### 9. browser-use - 浏览器自动化
**用途：** 网页操作、数据抓取、社交媒体管理
**触发词：** 浏览器、自动化、抓取
**使用方法：**
```bash
cat skills/browser-use/SKILL.md

# 支持平台
- Instagram
- LinkedIn
- X (Twitter)
```

### 10. openviking - Viking 记忆增强
**用途：** 记忆系统、上下文管理
**触发词：** 记忆、viking、上下文
**使用方法：**
```bash
cat skills/openviking/SKILL.md
```

---

## 📚 小说创作类

### 11. novel-worldbuilding - 架构设计
**用途：** 大纲设计、世界观构建、人物设定
**触发词：** 大纲、世界观、架构、设定
**使用方法：**
```bash
cat skills/novel-worldbuilding/SKILL.md
```

### 12. novel-prose - 小说写作技法
**用途：** 章节执笔、正文创作
**触发词：** 写作、执笔、章节、正文
**使用方法：**
```bash
cat skills/novel-prose/SKILL.md
```

### 13. novel-research - 深度调研
**用途：** 素材检索、背景调研
**触发词：** 调研、检索、素材
**使用方法：**
```bash
cat skills/novel-research/SKILL.md
```

### 14. novel-memory - 小说记忆系统
**用途：** 角色记忆、情节追踪
**触发词：** 记忆、存储、查询
**使用方法：**
```bash
cat skills/novel-memory/SKILL.md
```

### 15. novel-review - 章节审核
**用途：** 质量校对、内容审核
**触发词：** 审核、校对、检查
**使用方法：**
```bash
cat skills/novel-review/SKILL.md
```

### 16. novel-archiving - 章节归档
**用途：** 章节完成后的持久化、摘要生成
**触发词：** 归档、摘要、持久化
**使用方法：**
```bash
cat skills/novel-archiving/SKILL.md
```

---

## 🔍 信息获取类

### 17. context7 - 技术文档搜索
**用途：** 技术文档查询、API 参考
**触发词：** 文档、api、技术搜索
**使用方法：**
```bash
cat skills/context7/SKILL.md

# 需要配置 API Key
export CONTEXT7_API_KEY=your_key
```

### 18. searxng - 本地搜索
**用途：** SearXNG 本地搜索引擎
**触发词：** 搜索、searxng
**使用方法：**
```bash
cat skills/searxng/SKILL.md

# 搜索地址
http://192.168.50.251:10011
```

### 19. hacker-news - Hacker News
**用途：** 技术资讯、热门讨论
**触发词：** hacker news、资讯、hn
**使用方法：**
```bash
cat skills/hacker-news/SKILL.md
```

### 20. weather - 天气查询
**用途：** 天气预报、气象信息
**触发词：** 天气、预报
**使用方法：**
```bash
cat skills/weather/SKILL.md
```

---

## 🗄️ 知识管理类

### 21. ontology - 知识图谱
**用途：** 结构化知识存储、实体关系管理
**触发词：** 知识图谱、实体、关系
**使用方法：**
```bash
cat skills/ontology/SKILL.md
```

### 22. notion - Notion API
**用途：** Notion 页面和数据库管理
**触发词：** notion、数据库
**使用方法：**
```bash
cat skills/notion/SKILL.md
```

---

## 🔧 系统工具类

### 23. system-info - 系统诊断
**用途：** CPU、内存、磁盘、运行时间
**触发词：** 系统信息、诊断
**使用方法：**
```bash
cat skills/system-info/SKILL.md
```

### 24. system-resource-monitor - 资源监控
**用途：** 实时资源监控、负载分析
**触发词：** 资源监控、负载
**使用方法：**
```bash
cat skills/system-resource-monitor/SKILL.md
```

### 25. self-improving-agent - 自我改进
**用途：** 错误学习、持续改进
**触发词：** 改进、学习、错误
**使用方法：**
```bash
cat skills/self-improving-agent/SKILL.md
```

---

## 🛡️ 社区管理类

### 26. discord-message-guard - Discord 消息防护
**用途：** Discord 消息过滤、安全防护
**触发词：** discord、防护、过滤
**使用方法：**
```bash
cat skills/discord-message-guard/SKILL.md
```

---

## 📖 使用建议

### 1. 技能选择原则
- **先读 SKILL.md** - 每个技能都有详细文档
- **匹配触发词** - 使用正确的关键词触发
- **按需使用** - 不是所有任务都需要技能

### 2. 技能组合使用
```
小说创作流程：
novel-worldbuilding → novel-research → novel-prose 
→ novel-review → novel-archiving → novel-memory

项目开发流程：
TaskMaster → ralph-loop → code-review → github
```

### 3. 技能文件位置
```
skills/
├── TaskMaster/
│   └── SKILL.md
├── browser-use/
│   └── SKILL.md
├── ...
└── weather/
    └── SKILL.md
```

### 4. 查看技能详情
```bash
# 查看单个技能
cat skills/TaskMaster/SKILL.md

# 列出所有技能
ls -1 skills/

# 搜索技能关键词
grep -r "关键词" skills/*/SKILL.md
```

---

## 🎯 快速查找

| 需求 | 推荐技能 |
|------|---------|
| 项目管理 | TaskMaster, clawlist |
| 代码开发 | github, ralph-loop, code-review |
| 小说创作 | novel-* 系列 (6个) |
| 浏览器操作 | browser-use |
| 文档查询 | context7, searxng |
| 系统监控 | system-info, system-resource-monitor |
| 任务管理 | quadrants, todoist |
| 知识管理 | ontology, notion |

---

## 📝 技能状态

- ✅ 已安装：26 个
- 📂 分类：7 大类
- 📄 文档：每个技能都有 SKILL.md

---

## 🔗 相关链接

- **ClawHub:** https://clawhub.com
- **技能市场:** https://clawhub.com/skills
- **OpenClaw 文档:** https://docs.openclaw.ai

---

_更新时间: 2026-03-23_
_技能数量: 26 个_
