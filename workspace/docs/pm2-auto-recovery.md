# PM2 服务自动恢复方案

## 问题描述

容器重启后，PM2 管理的 Dashboard 服务（端口 18795）不会自动启动。

## 解决方案

已部署三层保护机制：

### 1. PM2 开机自启
```bash
pm2 save
pm2 startup
```

### 2. Watchdog 守护进程（推荐）
**位置：** `/root/.openclaw/workspace/scripts/pm2-watchdog.sh`

**功能：**
- 每 60 秒检查 Dashboard 可访问性
- 自动恢复停止的服务
- 记录恢复日志

**日志位置：**
- `/root/.openclaw/workspace/logs/pm2-watchdog.log`
- `/root/.openclaw/workspace/logs/pm2-watchdog.out`

**手动启动：**
```bash
nohup /root/.openclaw/workspace/scripts/pm2-watchdog.sh > /root/.openclaw/workspace/logs/pm2-watchdog.out 2>&1 &
```

**检查状态：**
```bash
ps aux | grep pm2-watchdog
tail -f /root/.openclaw/workspace/logs/pm2-watchdog.log
```

### 3. 手动恢复脚本
**位置：** `/root/.openclaw/workspace/scripts/pm2-auto-restart.sh`

**使用：**
```bash
/root/.openclaw/workspace/scripts/pm2-auto-restart.sh
```

## 验证

```bash
# 检查 PM2 服务
pm2 list

# 检查 Dashboard 可访问性
curl http://localhost:18795

# 检查 Watchdog 运行状态
ps aux | grep pm2-watchdog
```

## 常见问题

**Q: 容器重启后 Dashboard 仍然不可访问？**
A: 运行手动恢复脚本：
```bash
/root/.openclaw/workspace/scripts/pm2-auto-restart.sh
```

**Q: Watchdog 没有运行？**
A: 启动 Watchdog：
```bash
nohup /root/.openclaw/workspace/scripts/pm2-watchdog.sh > /root/.openclaw/workspace/logs/pm2-watchdog.out 2>&1 &
```

**Q: 如何停止 Watchdog？**
A: 查找并停止进程：
```bash
pkill -f pm2-watchdog.sh
```

## 配置文件

| 文件 | 说明 |
|------|------|
| pm2-watchdog.sh | 守护进程脚本 |
| pm2-auto-restart.sh | 手动恢复脚本 |
| ensure-pm2.sh | 检查脚本 |
| /root/.pm2/dump.pm2 | PM2 保存的进程列表 |

## 更新时间

2026-03-21 15:26
