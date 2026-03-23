# 容器重启自动恢复配置

## ✅ 自动启动流程

```
容器启动
  ↓
init.d 调用 /etc/init.d/pm2-undefined
  ↓
PM2 resurrect (恢复 Dashboard)
  ↓
启动 pm2-watchdog.sh (监控进程)
  ↓
Dashboard (18795) 可访问 ✅
```

## 📋 配置详情

| 组件 | 自动启动 | 位置 |
|------|---------|------|
| PM2 | ✅ | /etc/init.d/pm2-undefined |
| Dashboard | ✅ | PM2 管理 |
| Watchdog | ✅ | PM2 init 脚本中 |

## 🔍 验证方法

**重启容器后检查：**
```bash
# 1. 检查 PM2
pm2 list

# 2. 检查 Dashboard
curl http://localhost:18795

# 3. 检查 Watchdog
ps aux | grep pm2-watchdog

# 4. 查看 Watchdog 日志
tail -f /root/.openclaw/workspace/logs/pm2-watchdog.log
```

## 📝 修改记录

**2026-03-21 15:28**
- ✅ 修改 `/etc/init.d/pm2-undefined`
- ✅ 添加 watchdog 自动启动
- ✅ 备份原文件到 `/etc/init.d/pm2-undefined.backup_20260321_152830`

## 🚨 故障排查

**Dashboard 不可访问？**
```bash
# 手动恢复
/root/.openclaw/workspace/scripts/pm2-auto-restart.sh
```

**Watchdog 没有运行？**
```bash
# 手动启动
nohup /root/.openclaw/workspace/scripts/pm2-watchdog.sh > /root/.openclaw/workspace/logs/pm2-watchdog.out 2>&1 &
```

**PM2 没有自动启动？**
```bash
# 检查 init.d 脚本
ls -la /etc/init.d/pm2-*
/etc/init.d/pm2-undefined start
```

## 🔄 重置配置

如果需要重置 PM2 init 脚本：
```bash
# 恢复备份
cp /etc/init.d/pm2-undefined.backup_20260321_152830 /etc/init.d/pm2-undefined

# 重新配置
pm2 unstartup
pm2 startup
```

---

**更新时间：** 2026-03-21 15:28
