# 三省六部 Agent 目录结构规范

**制定时间**: 2026-03-24 09:01
**制定部门**: 中书省
**参考标准**: /root/.openclaw/workspace

---

## 📂 标准目录结构

每个 agent 的工作目录必须遵循以下结构：

```
/root/.openclaw/tang-sansheng/workspace-{部门}/
├── 📋 核心配置文件
│   ├── AGENTS.md              # Agent 配置和职责说明
│   ├── SOUL.md                # 行为准则和制度
│   ├── TOOLS.md               # 可用工具和技能列表
│   ├── USER.md                # 用户信息
│   ├── IDENTITY.md            # Agent 身份标识
│   └── HEARTBEAT.md           # 心跳检测配置
│
├── 📁 系统目录
│   ├── .openclaw/             # OpenClaw 系统配置
│   ├── .clawhub/              # ClawHub 技能市场
│   └── .gitignore             # Git 忽略规则
│
├── 📊 数据目录
│   ├── data/                  # 业务数据存储
│   │   ├── input/            # 输入数据
│   │   ├── output/           # 输出数据
│   │   └── cache/            # 缓存数据
│   │
│   ├── docs/                  # 文档存储
│   │   ├── reports/          # 工作报告
│   │   ├── guides/           # 操作指南
│   │   ├── drafts/           # 草稿文件
│   │   └── archives/         # 归档文件
│   │
│   └── projects/              # 项目文件
│       ├── active/           # 进行中的项目
│       ├── completed/        # 已完成的项目
│       └── pending/          # 待处理的项目
│
├── 🧠 知识管理
│   ├── memory/                # 记忆存储
│   │   ├── daily/            # 每日记忆
│   │   ├── projects/         # 项目记忆
│   │   └── lessons/          # 经验教训
│   │
│   ├── Knowledge/             # 知识库
│   │   ├── references/       # 参考资料
│   │   ├── standards/        # 标准规范
│   │   └── best-practices/   # 最佳实践
│   │
│   └── .learnings/            # 学习记录（self-improving-agent）
│       ├── ERRORS.md         # 错误日志
│       ├── LEARNINGS.md      # 学习日志
│       ├── FEATURE_REQUESTS.md # 功能请求
│       └── README.md         # 说明文档
│
├── 🛠️ 工具目录
│   ├── skills/                # 技能文件
│   │   ├── installed/        # 已安装技能
│   │   ├── custom/           # 自定义技能
│   │   └── templates/        # 技能模板
│   │
│   ├── scripts/               # 脚本文件
│   │   ├── automation/       # 自动化脚本
│   │   ├── deployment/       # 部署脚本
│   │   └── utilities/        # 工具脚本
│   │
│   └── tools/                 # 开发工具
│       ├── generators/       # 代码生成器
│       ├── validators/       # 验证工具
│       └── analyzers/        # 分析工具
│
├── 📝 临时文件
│   ├── temp/                  # 临时文件（定期清理）
│   ├── logs/                  # 日志文件
│   │   ├── system/           # 系统日志
│   │   ├── errors/           # 错误日志
│   │   └── debug/            # 调试日志
│   │
│   └── cache/                 # 缓存文件
│
└── 📦 部门特定目录
    ├── {部门专属}/            # 根据部门职责定制
    │   ├── ...               # 部门特定文件
    │   └── ...
    └── README.md              # 部门说明文档
```

---

## 🎯 各部门专属目录

### 中书省（zhongshu）- 决策起草
```
├── drafts/                    # 诏令草案
│   ├── pending/              # 待审核草案
│   ├── approved/             # 已通过草案
│   └── rejected/             # 已驳回草案
├── policies/                  # 政策文件
└── coordination/              # 协调记录
```

### 门下省（menxia）- 审核追问
```
├── reviews/                   # 审核记录
│   ├── pending/              # 待审核
│   ├── approved/             # 已通过
│   └── rejected/             # 已驳回
├── questions/                 # 追问记录
└── feedback/                  # 反馈文件
```

### 尚书省（shangshu）- 执行派发
```
├── dispatches/                # 派发记录
│   ├── active/               # 进行中任务
│   ├── completed/            # 已完成任务
│   └── overdue/              # 超期任务
├── schedules/                 # 调度计划
└── progress/                  # 进度跟踪
```

### 御史台（yushitai）- 独立监察
```
├── audits/                    # 审查报告
│   ├── code/                 # 代码审查
│   ├── security/             # 安全审查
│   └── quality/              # 质量审查
├── violations/                # 违规记录
└── recommendations/           # 改进建议
```

### 兵部（bingbu）- 软件工程
```
├── code/                      # 代码文件
│   ├── backend/              # 后端代码
│   ├── frontend/             # 前端代码
│   └── tests/                # 测试代码
├── architecture/              # 架构设计
└── deployments/               # 部署文件
```

### 礼部（libu）- 品牌营销
```
├── marketing/                 # 营销材料
│   ├── campaigns/            # 营销活动
│   ├── content/              # 内容创作
│   └── social/               # 社交媒体
├── branding/                  # 品牌设计
└── communications/            # 对外沟通
```

### 户部（hubu）- 财务分析
```
├── finance/                   # 财务文件
│   ├── budgets/              # 预算文件
│   ├── reports/              # 财务报告
│   └── analysis/             # 分析数据
├── resources/                 # 资源管理
└── planning/                  # 财务规划
```

### 工部（gongbu）- 运维部署
```
├── infrastructure/            # 基础设施
│   ├── servers/              # 服务器配置
│   ├── networks/             # 网络配置
│   └── security/             # 安全配置
├── deployment/                # 部署文件
└── monitoring/                # 监控配置
```

### 吏部（libu2）- 人事管理
```
├── hr/                        # 人事文件
│   ├── evaluations/          # 绩效评估
│   ├── assignments/          # 任务分配
│   └── records/              # 人事记录
├── training/                  # 培训材料
└── organization/              # 组织架构
```

### 刑部（xingbu）- 法务合规
```
├── legal/                     # 法务文件
│   ├── contracts/            # 合同文件
│   ├── compliance/           # 合规检查
│   └── policies/             # 法律政策
├── risk/                      # 风险评估
└── review/                    # 法务审查
```

---

## 📋 文件命名规范

### 通用规则
1. **使用中文或英文**：优先使用中文，技术文件可用英文
2. **使用日期前缀**：重要文件使用 `YYYYMMDD_` 前缀
3. **使用版本号**：需要版本管理的文件使用 `_v1.0` 后缀
4. **避免空格**：使用下划线 `_` 或连字符 `-` 代替空格

### 示例
```
✅ 好的命名：
- 20260324_云天佑项目报告.md
- 工作汇报_20260324_v1.0.md
- code_review_checklist.md

❌ 不好的命名：
- 新建文档 1.md
- final final final.md
- 2026-3-24 report.md
```

---

## 🧹 定期清理规则

### 每日清理
- `temp/` - 临时文件
- `cache/` - 缓存文件
- `logs/debug/` - 调试日志

### 每周清理
- `logs/` - 超过7天的日志
- `temp/` - 所有临时文件

### 每月归档
- `docs/drafts/` - 超过30天的草稿
- `projects/completed/` - 已完成项目归档
- `memory/daily/` - 合并到月度记忆

---

## 🚀 初始化脚本

### 自动创建目录结构

```bash
#!/bin/bash
# 初始化三省六部agent目录结构

WORKSPACE_BASE="/root/.openclaw/tang-sansheng"
DEPARTMENTS=("zhongshu" "menxia" "shangshu" "yushitai" "bingbu" "libu" "hubu" "gongbu" "libu2" "xingbu")

for dept in "${DEPARTMENTS[@]}"; do
    workspace="${WORKSPACE_BASE}/workspace-${dept}"
    
    echo "初始化 ${dept} 工作目录..."
    
    # 创建核心配置文件
    touch "${workspace}/AGENTS.md"
    touch "${workspace}/SOUL.md"
    touch "${workspace}/TOOLS.md"
    touch "${workspace}/USER.md"
    touch "${workspace}/IDENTITY.md"
    touch "${workspace}/HEARTBEAT.md"
    touch "${workspace}/.gitignore"
    
    # 创建系统目录
    mkdir -p "${workspace}/.openclaw"
    mkdir -p "${workspace}/.clawhub"
    
    # 创建数据目录
    mkdir -p "${workspace}/data/input"
    mkdir -p "${workspace}/data/output"
    mkdir -p "${workspace}/data/cache"
    
    mkdir -p "${workspace}/docs/reports"
    mkdir -p "${workspace}/docs/guides"
    mkdir -p "${workspace}/docs/drafts"
    mkdir -p "${workspace}/docs/archives"
    
    mkdir -p "${workspace}/projects/active"
    mkdir -p "${workspace}/projects/completed"
    mkdir -p "${workspace}/projects/pending"
    
    # 创建知识管理目录
    mkdir -p "${workspace}/memory/daily"
    mkdir -p "${workspace}/memory/projects"
    mkdir -p "${workspace}/memory/lessons"
    
    mkdir -p "${workspace}/Knowledge/references"
    mkdir -p "${workspace}/Knowledge/standards"
    mkdir -p "${workspace}/Knowledge/best-practices"
    
    mkdir -p "${workspace}/.learnings"
    touch "${workspace}/.learnings/ERRORS.md"
    touch "${workspace}/.learnings/LEARNINGS.md"
    touch "${workspace}/.learnings/FEATURE_REQUESTS.md"
    touch "${workspace}/.learnings/README.md"
    
    # 创建工具目录
    mkdir -p "${workspace}/skills/installed"
    mkdir -p "${workspace}/skills/custom"
    mkdir -p "${workspace}/skills/templates"
    
    mkdir -p "${workspace}/scripts/automation"
    mkdir -p "${workspace}/scripts/deployment"
    mkdir -p "${workspace}/scripts/utilities"
    
    mkdir -p "${workspace}/tools/generators"
    mkdir -p "${workspace}/tools/validators"
    mkdir -p "${workspace}/tools/analyzers"
    
    # 创建临时文件目录
    mkdir -p "${workspace}/temp"
    mkdir -p "${workspace}/logs/system"
    mkdir -p "${workspace}/logs/errors"
    mkdir -p "${workspace}/logs/debug"
    mkdir -p "${workspace}/cache"
    
    echo "✅ ${dept} 初始化完成"
done

echo ""
echo "🎉 所有部门目录结构初始化完成！"
```

---

## 📊 目录使用统计

### 必须使用的目录
- ✅ `docs/` - 所有文档
- ✅ `projects/` - 所有项目
- ✅ `memory/` - 所有记忆
- ✅ `.learnings/` - 所有学习记录
- ✅ `logs/` - 所有日志

### 推荐使用的目录
- 📁 `data/` - 业务数据
- 📁 `Knowledge/` - 知识库
- 📁 `skills/` - 技能文件
- 📁 `scripts/` - 脚本文件

### 临时使用的目录
- ⏳ `temp/` - 临时文件
- ⏳ `cache/` - 缓存文件

---

## ✅ 检查清单

### 每日检查
- [ ] 是否有文件放在根目录？
- [ ] 是否有临时文件未清理？
- [ ] 是否有日志文件过大？

### 每周检查
- [ ] 目录结构是否完整？
- [ ] 是否有废弃文件？
- [ ] 是否有重复文件？

### 每月检查
- [ ] 是否需要归档？
- [ ] 是否需要清理？
- [ ] 是否需要重组？

---

## 📝 注意事项

1. **不要在根目录放文件** - 所有文件必须分类存储
2. **不要创建深层嵌套** - 最多3层子目录
3. **不要使用临时目录存储重要文件** - temp/ 会定期清理
4. **不要重复创建目录** - 使用标准目录结构

---

**制定部门**: 中书省
**制定时间**: 2026-03-24 09:01
**版本**: v1.0
**适用范围**: 三省六部所有部门

---

_本规范基于 /root/.openclaw/workspace 标准结构制定_
_所有部门必须严格遵守此规范_
