# 交易策略知识库

> 📊 255个交易策略 + 177条向量记忆
> 📅 更新: 2026-03-16
> 🎯 总文件: 135个

---

## 🚀 快速开始

**老板，你想查什么？**

| 需求 | 推荐文档 |
|------|---------|
| 查看所有策略 | [trading-strategies/STRATEGIES_COMPLETE_HANDBOOK.md](trading-strategies/STRATEGIES_COMPLETE_HANDBOOK.md) |
| **学习经典策略** | [trading-strategies/learned/](trading-strategies/learned/) ⭐ 新增 |
| 学习技术指标 | [trading-strategies/technical-indicators/](trading-strategies/technical-indicators/) |
| 查看实战经验 | [trading-strategies/TRADING_MEMORIES.md](trading-strategies/TRADING_MEMORIES.md) |
| 知识库导航 | [trading-strategies/KNOWLEDGE_INDEX.md](trading-strategies/KNOWLEDGE_INDEX.md) |

---

## 📊 策略统计

| 分类 | 数量 | 胜率范围 |
|------|------|---------|
| 日内做T | 12 | 60-82% |
| 卖出信号 | 5 | 65-100% |
| 经典策略 | 15 | 0-67% |
| A股专属 | 8 | 60-72% |
| 技术指标 | 4 | 63-68% |
| 高胜率组合 | 123 | 70-90% |
| **总计** | **255** | - |

---

## 📁 目录结构

```
Knowledge/
├── README.md                           # 本文件
├── trading-strategies/                 # 交易策略库
│   ├── STRATEGIES_COMPLETE_HANDBOOK.md # ⭐ 255策略完整手册
│   ├── KNOWLEDGE_INDEX.md              # 知识库导航
│   ├── TRADING_MEMORIES.md             # 交易记忆库
│   ├── STRATEGY-LIBRARY.md             # 策略索引
│   ├── technical-indicators/           # 技术指标
│   │   ├── MACD.md                     # MACD详解
│   │   ├── KDJ.md                      # KDJ详解
│   │   ├── RSI.md                      # RSI详解
│   │   ├── VWAP.md                     # VWAP详解
│   │   ├── BOLL.md                     # 布林带详解
│   │   └── Multi-Indicator-Strategy.md # 多指标组合
│   ├── code/                           # 策略代码 (28个)
│   ├── backtest/                       # 回测数据
│   └── *.json                          # 数据文件
└── english-words/                      # 英语学习
```

---

## 🎯 高胜率策略 TOP 10

| 排名 | 策略 | 胜率 | 类型 |
|------|------|------|------|
| 1 | 盈利>1.5%止盈 | 100% | 止盈 |
| 2 | KDJ超买超卖 | 98% | 形态 |
| 3 | RSI Pattern | 98% | 均值回归 |
| 4 | Pair Trading | 92% | 统计套利 |
| 5 | 多指标组合 | 85% | 组合 |
| 6 | MACD Oscillator | 85% | 趋势 |
| 7 | Dual Thrust | 80% | 突破 |
| 8 | 布林带 | 80% | 均值回归 |
| 9 | 大涨+高开 | 82% | 做T |
| 10 | 高开+量缩 | 74% | 做T |

---

## 📖 学习路径

### 新手入门

1. [STRATEGIES_COMPLETE_HANDBOOK.md](trading-strategies/STRATEGIES_COMPLETE_HANDBOOK.md) - 了解全部策略
2. [technical-indicators/MACD.md](trading-strategies/technical-indicators/MACD.md) - 学习基础指标
3. [TRADING_MEMORIES.md](trading-strategies/TRADING_MEMORIES.md) - 实战经验

### 进阶学习

1. [technical-indicators/Multi-Indicator-Strategy.md](trading-strategies/technical-indicators/Multi-Indicator-Strategy.md) - 多指标组合
2. [code/](trading-strategies/code/) - 策略代码实现
3. [backtest/](trading-strategies/backtest/) - 回测报告

### 实战应用

1. 选择2-3个高胜率策略
2. 设置止损止盈
3. 模拟验证后实盘

---

## 🔧 数据文件

| 文件 | 大小 | 说明 |
|------|------|------|
| STRATEGY_LIBRARY_COMPLETE.json | 87KB | 255个策略JSON |
| lancedb_all_memories.json | 81KB | 177条向量记忆 |
| lancedb_trading_memories.json | 23KB | 41条交易记忆 |

---

## ⚠️ 风险提示

- 历史胜率不代表未来收益
- 策略需结合市场环境调整
- 先模拟验证再实盘
- 严格止损止盈纪律

---

*维护者: 小秘*
*更新时间: 2026-03-16*
