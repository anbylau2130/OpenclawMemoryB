# LEARNINGS.md - 学习日志

_记录开发过程中的学习经验和最佳实践_

---

## projects目录用途澄清（2026-03-24 09:30）

### Category: `best_practice`

### 学习内容

**两个projects目录的正确用途**

### 错误理解（09:25）

**我的错误**:
- ❌ 以为所有项目都要存到 tang-sansheng/projects/
- ❌ 以为 workspace-部门/projects/ 不再使用
- ❌ 通知了所有部门错误的信息

**陛下纠正**（09:30）:
- ✅ tang-sansheng/projects/ = 跨部门协作项目
- ✅ workspace-部门/projects/ = 学习项目 + 个人任务

### 正确理解

#### 🎯 目录1：统一协作项目

**位置**: `/root/.openclaw/tang-sansheng/projects/`

**用途**:
- ✅ 跨部门协作项目
- ✅ 组织级大型项目
- ✅ 多人协作项目
- ✅ 生产环境项目

**示例**:
```
tang-sansheng/projects/
├── yuntianyou-project/        # 云天佑平台（跨部门）
├── trading-system/            # 交易系统（多部门协作）
└── official-documents/        # 公文系统（组织级）
```

#### 📚 目录2：部门个人项目

**位置**: `workspace-[部门]/projects/`

**用途**:
- ✅ **需要学习的项目**
- ✅ **单独的个人任务**
- ✅ 部门内部项目
- ✅ 学习练习项目
- ✅ 个人探索项目

**示例**:
```
workspace-zhongshu/projects/
├── learning-spring-boot/      # 学习Spring Boot
├── personal-scripts/          # 个人脚本工具
├── demo-project/              # 演示项目
└── task-20260324/             # 个人任务
```

### 对比总结

| 目录 | 位置 | 用途 | 适用场景 |
|------|------|------|---------|
| **统一项目** | tang-sansheng/projects/ | 跨部门协作 | 组织级项目 |
| **部门项目** | workspace-部门/projects/ | 学习+个人任务 | 个人学习、单独任务 |

### 判断标准

**问题1**: 这个项目是否需要跨部门协作？
- ✅ 是 → tang-sansheng/projects/
- ❌ 否 → 继续判断

**问题2**: 这个项目是学习用的吗？
- ✅ 是 → workspace-部门/projects/
- ❌ 否 → 继续判断

**问题3**: 这个项目是个人任务吗？
- ✅ 是 → workspace-部门/projects/
- ❌ 否 → tang-sansheng/projects/

### 应用场景

**场景1：云天佑低代码平台**
```
✅ 跨部门协作
✅ 组织级项目
✅ 多人协作

→ 使用：tang-sansheng/projects/yuntianyou-project/
```

**场景2：学习Spring Boot**
```
✅ 学习项目
✅ 个人练习
✅ 单独任务

→ 使用：workspace-zhongshu/projects/learning-spring-boot/
```

**场景3：个人自动化脚本**
```
✅ 个人任务
✅ 单独工作
✅ 部门内部

→ 使用：workspace-zhongshu/projects/personal-scripts/
```

### 经验教训

1. **充分询问澄清** - 不确定时立即询问陛下
2. **提供示例确认** - 给出具体场景请陛下确认
3. **理解实际需求** - 考虑实际工作场景
4. **不要过度推断** - 不要假设理解正确

### 相关文件
- `Knowledge/standards/三省六部文件存放规范_v1.0.md`
- `docs/reports/projects目录用途澄清报告_20260324.md`
- `.learnings/ERRORS.md` - 错误记录

---

## Message工具单向通知特性（2026-03-24 09:06）

### Category: `best_practice`

### 学习内容

**Message工具是单向通知，不会触发Agent自动回复**

### 工具机制

**Message工具特性**:
```
中书省 → message → 其他部门
  ↓
✅ 消息已送达（有messageId）
❌ 但不会触发自动回复
```

**类比**:
```
Message = 发送邮件（单向）
对话 = 打电话（双向）
```

### 如何获得回复

**方法1：陛下主动对话**
```
1. 打开钉钉
2. 找到对应部门机器人
3. 发送消息
4. 部门会回复
```

**方法2：通过尚书省spawn**
```javascript
sessions_spawn({
  agentId: "部门ID",
  task: "任务内容"
})
```

**方法3：等待下次对话**
```
下次对话时：
- Agent启动 → 读取AGENTS.md
- 看到规范 → 自动遵守
```

### 适用场景

**Message工具**:
- ✅ 单向通知
- ✅ 广播消息
- ✅ 规范传达
- ❌ 不适合获取回复

**对话/spawn**:
- ✅ 获取回复
- ✅ 任务执行
- ✅ 交互式对话

### 相关文件
- `.learnings/ERRORS.md` - Message工具误解记录

---

## 三省制分权制衡原理（2026-03-24 08:36）

### Category: `best_practice`

### 学习内容

**三省制的分权制衡设计**

```
皇帝（陛下）
   ↓
中书省 → 门下省 → 尚书省 → 六部
(起草)   (审核)   (派发)   (执行)
   ↓         ↓         ↓        ↓
无 spawn  无 spawn  有 spawn  无 spawn
```

### 关键认知

1. **中书省无 spawn 权限是正确设计**
   - 目的：防止中书省绕过审核直接派发
   - 体现三省制的分权制衡原则

2. **尚书省是唯一有 spawn 权限的部门**
   - 目的：统一调度，避免多头指挥
   - 六部只对尚书省负责

3. **配置与 danghuangshang 完全一致**
   - 不是配置错误
   - 是三省制的正确实现

### 最佳实践

```javascript
// 正确的三省流程：

// 1. 中书省起草
起草诏令草案.md

// 2. 提交门下省审核
message({
  accountId: "menxia",
  channel: "dingtalk",
  message: "【诏令草案】请审核..."
})

// 3. 门下省审核后，通知尚书省
message({
  accountId: "shangshu",
  message: "【审核通过】请派发..."
})

// 4. 尚书省 spawn 六部
sessions_spawn({
  agentId: "bingbu",
  task: "开发后端..."
})
```

### 相关文件
- `SOUL.md` - 三省六部制度
- `AGENTS.md` - 各部门职责

---

_最后更新: 2026-03-24 09:30_
_维护者: 中书省（zhongshu）_
