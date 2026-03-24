# FOLDERS.md - 门下省目录结构规范

**创建时间**: 2026-03-24 15:35
**维护部门**: 门下省
**版本**: v1.0

---

## 📁 目录结构总览

```
workspace-menxia/
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
│   ├── Conversation/      # 对话记录（只保存陛下私聊）
│   │   └── YYYYMMDD.md    # 每天一个文件
│   ├── reports/           # 工作报告
│   ├── plans/             # 计划文档
│   └── guides/            # 指导文档
│
├── projects/              # 学习项目和个人任务
│   ├── learning/          # 学习项目
│   └── tasks/             # 个人任务
│
├── memory/                # 记忆文件
│   └── YYYY-MM-DD.md      # 每日记忆
│
├── Knowledge/             # 知识库
│   ├── standards/         # 规范文档
│   └── references/        # 参考资料
│
├── .learnings/             # 学习记录
│   ├── LEARNINGS.md       # 学习总结
│   └── ERRORS.md          # 错误记录
│
├── data/                  # 数据文件
├── scripts/               # 脚本工具
└── logs/                  # 日志文件
```

---

## 🎯 核心配置文件（7个)

### 必须存在，不可删除
1. **AGENTS.md** - 部门规范和职责
2. **SOUL.md** - 三省六部制度
3. **TOOLS.md** - 可用工具
4. **USER.md** - 关于陛下
5. **FOLDERS.md** - 目录结构规范（本文件)
6. **IDENTITY.md** - 身份标识
7. **README.md** - 工作空间说明
### 其他文件必须存放到对应目录
- ❌ 不要在根目录创建其他文件
- ✅ 按照目录结构规范存放
---
## 📂 docs/ 目录规范
### docs/Conversation/ - 对话记录
**⚠️ 重要： 只保存陛下的私聊对话
**位置**: `workspace-menxia/docs/Conversation/`
**文件名**: `YYYYMMDD.md`
**示例**:
```
docs/Conversation/
├── 20260324.md    # 2026年3月24日的对话
├── 20260325.md    # 2026年3月25日的对话
└── ...
```
**格式**:
```markdown
# YYYY-MM-DD 陛下对话记录
**记录部门**: 门下省
**开始时间**: YYYY-MM-DD HH:MM
---
## HH:MM
陛下： [陛下说的内容]
---
_最后更新: YYYY-MM-DD HH:MM_
_记录部门: 门下省_
```
**判断逻辑**:
```javascript
// 步骤1：检查是否是私聊
if (inbound_meta.chat_type !== "direct") {
  return; // 群聊，不记录
}
// 步骤2：检查是否是陛下
if (sender_id !== "096028035723738668") {
  return; // 不是陛下,不记录
}
// 步骤3：保存对话
saveConversation(user_message, timestamp);
```
---
## 📂 projects/ 目录规范
### 两个projects目录，用途不同
#### 🎯 统一协作项目
**位置**: `/root/.openclaw/tang-sansheng/projects/`
**用途**:
- ✅ 跨部门协作项目
- ✅ 组织级大型项目
**示例**:
```
tang-sansheng/projects/
├── yuntianyou-project/        # 云天佑平台（跨部门)
├── trading-system/            # 交易系统（多部门协作)
└── official-documents/        # 公文系统（组织级)
```
#### 📚 部门个人项目
**位置**: `workspace-menxia/projects/`
**用途**:
- ✅ **需要学习的项目**
- ✅ **单独的个人任务**
- ✅ 部门内部项目
**示例**:
```
workspace-menxia/projects/
├── learning-spring-boot/      # 学习Spring Boot
├── personal-scripts/          # 个人脚本工具
├── demo-project/              # 演示项目
└── task-20260324/             # 个人任务
```
---
## ⚠️ 重要规则
### ✅ 必须遵守
1. **根目录只保留7个核心配置文件**
2. **对话记录保存到自己的工作空间** `workspace-部门名/docs/Conversation/`
3. **按照目录结构规范存放文件**
4. **学习/个人任务放到自己的projects目录**
5. **跨部门项目放到统一projects目录**
### ❌ 禁止行为
1. ❌ 在根目录创建其他文件
2. ❌ 对话记录保存到统一位置（会造成冲突）
3. ❌ 不按目录结构规范存放文件
4. ❌ 个人任务放到统一projects目录
5. ❌ 跨部门项目放到个人projects目录
---
_最后更新: 2026-03-24 15:35_
_维护部门: 门下省_
_版本: v1.0_
