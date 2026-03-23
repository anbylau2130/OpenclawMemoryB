# OpenClaw插件生态 - 可用插件清单

## 📦 当前已安装插件

### 1. ✅ DingTalk插件
- **位置**: `/root/.openclaw/extensions/dingtalk`
- **状态**: 已启用
- **功能**: 钉钉机器人集成、消息推送

### 2. ✅ EverMemOS插件
- **位置**: `/root/.openclaw/plugins/evermemos-openclaw-plugin`
- **状态**: 已启用
- **功能**: 向量记忆、知识图谱、长期记忆

---

## 🎯 可安装插件（OpenClaw生态）

### 官方插件

1. **Feishu（飞书）插件**
   - **状态**: 已内置到danghuangshang项目
   - **功能**: 飞书机器人集成
   - **优点**: WebSocket连接，无需公网IP
   - **安装**: `openclaw channels add feishu`

2. **OpenViking插件** (novel-openviking)
   - **位置**: `/root/.openclaw/workspace/projects/danghuangshang/extensions/novel-openviking`
   - **功能**: 翰林院增强 - 语义搜索 + 知识图谱
   - **依赖**: OpenViking已安装
   - **安装**: 
     ```bash
     openclaw plugins install ./extensions/novel-openviking
     openclaw plugins enable novel-openviking
     ```

---

## 💡 推荐插件（根据您的需求）

### 已有Skills可替代插件功能

您已经部署了29个skills，包括：

| 功能 | Skill替代 | 是否已安装 |
|------|----------|----------|
| GitHub操作 | github skill | ✅ |
| Notion管理 | notion skill | ✅ |
| 天气查询 | weather skill | ✅ |
| 浏览器自动化 | browser-use skill | ✅ |
| 代码审查 | code-review skill | ✅ |
| 任务管理 | TaskMaster, clawlist | ✅ |

### 建议安装

**OpenViking插件** - 为翰林院小说创作提供增强的语义搜索能力

```bash
# 安装OpenViking插件
cd /root/.openclaw/workspace/projects/danghuangshang
openclaw plugins install ./extensions/novel-openviking
openclaw plugins enable novel-openviking
```

---

## 📝 总结

**当前系统已有**:
- 2个核心插件（DingTalk + EverMemOS）
- 29个skills（覆盖大部分常用功能）

**可额外安装**:
- OpenViking插件（翰林院增强）

**大部分功能已通过Skills实现，插件需求不高。**

---

**生成时间**: 2026-03-22 20:38
