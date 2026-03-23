# 交易系统定时任务配置指南

> **位置：** `projects/stock-tracking/`
> **创建时间：** 2026-03-17

---

## 📋 定时任务说明

| 时间 | 任务 | 脚本 | 说明 |
|------|------|------|------|
| **08:00** | 策略选股 | `stock_selector.py` | 从上证100中选出可能突破的股票 |
| **16:00** | 复盘验证 | `stock_review.py` | 验证选股准确性，计算收益 |

---

## 🔧 配置 Cron 定时任务

### 方法1：编辑 crontab

```bash
crontab -e
```

添加以下内容：

```cron
# 每天早上8点选股
0 8 * * 1-5 cd /root/.openclaw/workspace/projects/stock-tracking && /usr/bin/python3 stock_selector.py >> /var/log/stock_selector.log 2>&1

# 每天下午4点复盘
0 16 * * 1-5 cd /root/.openclaw/workspace/projects/stock-tracking && /usr/bin/python3 stock_review.py >> /var/log/stock_review.log 2>&1
```

**说明：**
- `1-5` 表示周一到周五（交易日）
- 输出重定向到日志文件

---

### 方法2：使用 OpenClaw Cron

在 OpenClaw 配置中添加：

```json
{
  "cron": {
    "entries": [
      {
        "schedule": "0 8 * * 1-5",
        "command": "cd /root/.openclaw/workspace/projects/stock-tracking && python3 stock_selector.py"
      },
      {
        "schedule": "0 16 * * 1-5",
        "command": "cd /root/.openclaw/workspace/projects/stock-tracking && python3 stock_review.py"
      }
    ]
  }
}
```

---

## 📂 文件结构

```
projects/stock-tracking/
├── stock_selector.py      # 选股脚本
├── stock_review.py        # 复盘脚本
├── selections/            # 选股结果
│   └── selection_YYYY-MM-DD.json
├── reviews/               # 复盘结果
│   └── review_YYYY-MM-DD.json
└── README.md              # 本文档
```

---

## 📊 选股策略

**多因子模型权重：**
| 因子 | 权重 | 说明 |
|------|------|------|
| 价值 | 20% | P/B、P/E、股息率 |
| 动量 | 25% | 过去12个月收益 |
| 质量 | 25% | ROE、ROA、毛利率 |
| 规模 | 10% | 市值（小盘股溢价）|
| 低波动 | 20% | 历史波动率 |

---

## 🎯 告警规则

### 买入信号
- 🟢 多因子得分 > 0.5
- 🟢 放量突破 MA5
- 🟢 量比 > 1.5

### 卖出信号
- 🔴 多因子得分 < -0.5
- 🔴 跌破关键支撑
- 🔴 MACD 死叉

---

## ⚠️ 注意事项

1. **数据源**：当前使用模拟数据，实际需要接入真实行情
2. **交易时间**：只在工作日运行
3. **风险控制**：建议止损 -5%，止盈 +10%
4. **策略优化**：根据复盘结果调整因子权重

---

## 📈 下一步

- [ ] 接入真实行情数据源（Tushare、AKShare）
- [ ] 添加更多因子（北向资金、分析师预期）
- [ ] 实现自动通知（选股和复盘结果推送）
- [ ] 策略参数优化

---

**更新时间：** 2026-03-17
