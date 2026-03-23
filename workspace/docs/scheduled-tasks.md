# 定时任务配置

## 说明

由于容器环境不支持crontab，定时任务通过心跳系统触发。

---

## 触发机制

### 方式1：心跳轮询
- HEARTBEAT.md中配置任务
- 每次心跳检查时间，到点执行

### 方式2：手动执行
```bash
# 8:00选股
cd /root/.openclaw/workspace/Knowledge/trading-strategies/code
python3 stock_selector_v5_real.py

# 16:00复盘
python3 stock_review_v2.py
```

---

## 心跳触发逻辑

在心跳检查时：
1. 检查当前时间
2. 如果是8:00±30分钟，执行选股
3. 如果是16:00±30分钟，执行复盘
4. 记录执行状态到heartbeat-state.json

---

## 状态跟踪

heartbeat-state.json结构：
```json
{
  "lastChecks": {
    "gateway": timestamp,
    "selection": timestamp,
    "review": timestamp
  },
  "trading": {
    "last_selection": "2026-03-17 08:00",
    "last_review": "2026-03-17 16:00"
  }
}
```
