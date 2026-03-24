# FOLDERS.md - 目录结构规范（2026-03-24 15:35)

**维护部门**: 中书省

**版本**: v1.0

---

## 📁 目录结构总览

```
workspace-zhongshu/
├── 核心配置文件（7个）
│   ├── AGENTS.md          # 部门规范和职责
│   ├── SOUL.md            # 三省六部制度
│   ├── TOOLS.md           # 可用工具
│   ├── USER.md            # 关于陛下
│   ├── FOLDERS.md         # 目录结构规范（本文件)
│   ├── IDENTITY.md        # 身份标识
│   └── README.md          # 工作空间说明
│
├── docs/                  # 文档目录
│   ├── Conversation/      # 对话记录（只保存陛下 │   │   └── yyyymmdd.md    # 每天一个文件
│   ├── reports/           # 工作报告
│   ├── plans/             # 计划文档
│   └── guides/            # 指导文档
│
├── projects/              # 学习项目和个人任务
│   ├── learning/          # 学习项目
│   └── tasks/             # 个人任务
│
├── memory/                # 记忆文件
│   └── yyyy-mm-dd.md      # 每日记忆
│
├── knowledge/             # 知识库
│   ├── standards/         # 规范文档
│   └── references/        # 参考资料
│
├── .learnings/             # 学习记录
│   ├── learnings.md       # 学习总结
│   └── errors.md          # 错误记录
│
├── data/                  # 数据文件
├── scripts/               # 脚本工具
└── logs/                  # 日志文件
