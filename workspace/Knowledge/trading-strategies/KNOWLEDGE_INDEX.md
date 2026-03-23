# 交易策略知识库总索引

> 📊 完整知识库导航
> 📅 更新: 2026-03-16
> 🎯 总文件: 133个

---

## 📚 快速导航

### 核心文档

| 文档 | 说明 | 推荐度 |
|------|------|-------|
| [STRATEGIES_HANDBOOK.md](STRATEGIES_HANDBOOK.md) | **策略总手册** - 255个策略详解 | ⭐⭐⭐⭐⭐ |
| [TRADING_MEMORIES.md](TRADING_MEMORIES.md) | 交易记忆库 - 41条实战经验 | ⭐⭐⭐⭐ |
| [STRATEGY-LIBRARY.md](STRATEGY-LIBRARY.md) | 策略索引 - 16核心+3组合 | ⭐⭐⭐⭐ |

### 技术指标

| 指标 | 文档 | 胜率 |
|------|------|------|
| MACD | [technical-indicators/MACD.md](technical-indicators/MACD.md) | 65-70% |
| KDJ | [technical-indicators/KDJ.md](technical-indicators/KDJ.md) | 98% |
| RSI | [technical-indicators/RSI.md](technical-indicators/RSI.md) | 98% |
| VWAP | [technical-indicators/VWAP.md](technical-indicators/VWAP.md) | 88% |
| BOLL | [technical-indicators/BOLL.md](technical-indicators/BOLL.md) | 80% |
| 多指标组合 | [technical-indicators/Multi-Indicator-Strategy.md](technical-indicators/Multi-Indicator-Strategy.md) | 85% |

### 数据文件

| 文件 | 格式 | 说明 |
|------|------|------|
| STRATEGY_LIBRARY_COMPLETE.json | JSON | 255个策略完整数据 |
| lancedb_all_memories.json | JSON | 177条向量记忆 |
| lancedb_trading_memories.json | JSON | 41条交易相关记忆 |

---

## 📁 目录结构

```
Knowledge/
├── README.md                           # 知识库说明
├── KNOWLEDGE_INDEX.md                  # 本文件 - 总索引
├── trading-strategies/                 # 交易策略
│   ├── STRATEGIES_HANDBOOK.md          # ⭐ 策略总手册
│   ├── TRADING_MEMORIES.md             # 交易记忆库
│   ├── STRATEGY-LIBRARY.md             # 策略索引
│   ├── STRATEGY_LIBRARY.json           # 策略数据
│   ├── STRATEGY_LIBRARY_COMPLETE.json  # 完整策略数据
│   ├── technical-indicators/           # 技术指标
│   │   ├── MACD.md                     # MACD详解
│   │   ├── KDJ.md                      # KDJ详解
│   │   ├── RSI.md                      # RSI详解
│   │   ├── VWAP.md                     # VWAP详解
│   │   ├── BOLL.md                     # 布林带详解
│   │   └── Multi-Indicator-Strategy.md # 多指标组合
│   ├── quantitative-trading/           # 量化交易
│   ├── code/                           # 策略代码 (28个)
│   ├── backtest/                       # 回测数据
│   └── *.md                            # 学习笔记
└── ...
```

---

## 🎯 按胜率排序的策略

### 顶级策略 (>90% 胜率)

| 策略 | 胜率 | 类型 | 来源 |
|------|------|------|------|
| 盈利>1.5%止盈 | 100% | 卖出信号 | 回测验证 |
| KDJ超买超卖 | 98% | 形态识别 | 回测验证 |
| RSI Pattern | 98% | 均值回归 | 回测验证 |
| Pair Trading | 92% | 均值回归 | 回测验证 |

### 高胜率策略 (70-90%)

| 策略 | 胜率 | 类型 | 来源 |
|------|------|------|------|
| 大涨+高开 | 82% | 日内做T | 回测验证 |
| 高开+量缩 | 74% | 日内做T | 回测验证 |
| MACD Oscillator | 85% | 趋势跟踪 | 回测验证 |
| Dual Thrust | 80% | 日内突破 | 回测验证 |
| 多指标组合 | 85% | 组合策略 | 回测验证 |

### 中等胜率策略 (60-70%)

| 策略 | 胜率 | 类型 | 来源 |
|------|------|------|------|
| 冲高回落 | 65% | 日内做T | 回测验证 |
| RSI均值回归 | 66.7% | 经典策略 | 回测验证 |
| 低于开盘价 | 60% | 日内做T | 回测验证 |

---

## 📖 学习路径

### 新手入门

1. 阅读 [STRATEGIES_HANDBOOK.md](STRATEGIES_HANDBOOK.md) 了解全部策略
2. 学习 [technical-indicators/MACD.md](technical-indicators/MACD.md) 掌握基础指标
3. 查看 [TRADING_MEMORIES.md](TRADING_MEMORIES.md) 学习实战经验

### 进阶学习

1. 研究 [technical-indicators/Multi-Indicator-Strategy.md](technical-indicators/Multi-Indicator-Strategy.md) 多指标组合
2. 阅读 code/ 目录下的策略代码
3. 查看 backtest/ 目录的回测报告

### 实战应用

1. 选择2-3个高胜率策略组合
2. 设置止损止盈规则
3. 模拟盘验证后实盘操作

---

## ⚠️ 风险提示

- 历史胜率不代表未来收益
- 策略需要结合市场环境调整
- 建议先模拟盘验证再实盘
- 严格执行止损止盈纪律

---

*生成时间: 2026-03-16*
*维护者: 小秘*
