# OpenClaw 配置备份

这个仓库用于备份 OpenClaw 的配置文件。

## 结构

```
.openclaw/
├── agents/          # Agent 配置
├── workspace*/      # 各 Agent 的工作空间
├── plugins/         # 插件配置
├── memory/          # 记忆文件
└── openclaw.template.json  # 配置模板
```

## 使用

1. 复制 `openclaw.template.json` 为 `openclaw.json`
2. 填入你的 API Key 和其他敏感信息
3. 放到 `~/.openclaw/` 目录

## 注意

- `openclaw.json` 包含敏感信息，已排除在版本控制之外
- `sessions/` 目录包含对话历史，已排除
