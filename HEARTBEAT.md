# HEARTBEAT.md

## 心跳检查（轮流，每天2-4次）

### 交易系统
- [ ] 检查定时任务（8:00选股、16:00复盘）
- [ ] 交易时段（9:30-15:00）监控 **→ 推送到钉钉工作通知（dingtalk_work_notice.py）**
- [ ] 验证选股策略效果（每日）
- [ ] **推送告警队列**（如果有待推送告警）**→ 使用工作通知API**

### 执行方式

**定时任务检查：**
```bash
cd /root/.openclaw/workspace/Knowledge/trading-strategies/code
python3 scheduled_tasks.py
```

**交易时段监控（9:30-15:00）：**
```bash
cd /root/.openclaw/workspace/Knowledge/trading-strategies/code
python3 trading_hours_monitor.py
```
- ✅ 自动识别交易时段（9:30-11:30, 13:00-15:00）
- ✅ 60秒扫描间隔，毫秒级信号生成
- ✅ 告警写入推送队列（data/alert_queue.json）
- ✅ 心跳时自动推送到钉钉
- ✅ 监控V5高胜率因子（VWAP、布林带、RSI、KDJ）

**告警推送检查（心跳时执行）：**
```bash
cd /root/.openclaw/workspace/Knowledge/trading-strategies/code
python3 check_alert_queue.py
```
- 检查 `data/alert_queue.json`
- 使用 `dingtalk_work_notice.py` 发送到**工作通知**（不是私聊）
- 发送后自动清空队列

### 系统状态
- [ ] Gateway 运行中？（避免消息丢失）
- [ ] EverMemOS 向量正常？

### 记忆维护
- [ ] 更新每日笔记（memory/YYYY-MM-DD.md）
- [ ] 回顾并提炼 MEMORY.md（每隔几天）

---

## 定时任务（Cron）

### 每日 8:00 - 策略选股（V5真实数据版）
```bash
cd /root/.openclaw/workspace/Knowledge/trading-strategies/code
python3 stock_selector_v5_real.py
```
- 真实数据源（新浪/东财/腾讯三重备份）
- 高胜率因子：VWAP(92%) + 布林带(71%) + RSI(69%) + KDJ(70%)
- 盈亏比：3.3（止盈10%/止损3%）
- 输出：买入价、卖出价、止盈、止损

### 每日 16:00 - 复盘验证
```bash
cd /root/.openclaw/workspace/Knowledge/trading-strategies/code
python3 stock_review_v2.py
```
- 验证当日选股效果
- 计算准确率和收益
- 检查止损止盈触发情况

### 每周五 16:00 - 周趋势验证
- 验证本周周趋势判断
- 统计中线策略效果
- 调整周线因子权重

---

## 交易告警规则

### 买入信号
- 🟢 多因子得分 > 4（日线+周线）
- 🟢 放量突破 MA5
- 🟢 周线多头排列

### 卖出信号
- 🔴 触发止损（短线-5%，中线-8%）
- 🔴 周线趋势改变
- 🔴 多因子得分 < 2

---

## 仓位管理

| 信号强度 | 仓位 | 持有周期 |
|---------|------|---------|
| ⭐⭐⭐ 强 | 30-40% | 中线（1-4周）|
| ⭐⭐ 中 | 20-30% | 短线（3-10天）|
| ⭐ 弱 | 10-20% | 观察仓 |

---

## 止盈止损纪律（V5优化版）

### 统一规则（盈亏比3.3）
- 止损：-3%
- 止盈：+10%
- 分批止盈：+6%卖30%，+10%卖40%，+15%清仓

### 风控原则
1. 单只股票仓位不超过20%
2. 总仓位不超过80%
3. 连续2次止损后暂停交易1天

---

## 状态跟踪

记录在 `memory/heartbeat-state.json`

---

## 主动联系时机

- Gateway 未运行 → 提醒启动
- 股票触发告警 → 立即通知
- 选股完成 → 发送选股报告
- 复盘完成 → 发送验证结果
- 策略需要调整 → 提醒改进

---

**注意：无任务时回复 HEARTBEAT_OK**
