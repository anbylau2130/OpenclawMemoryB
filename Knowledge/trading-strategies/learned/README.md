# 策略学习笔记 - 总索引

> 📚 已学习的策略索引
> 📅 最后更新: 2026-03-16 09:10
> 🎯 已学习: 10 个策略/主题
> ⚠️ 规则：每个策略只保存一份文档，避免重复

---

## 📋 已学习策略（按类型分类）

### 趋势跟踪（1个）

| 策略 | 文档位置 | 大小 |
|------|---------|------|
| **MACD振荡器** | [macd-oscillator-learning-notes.md](../macd-oscillator-learning-notes.md) | 6.7KB |

### 均值回归（2个）

| 策略 | 文档位置 | 大小 |
|------|---------|------|
| **RSI形态识别** | [rsi-pattern-learning-notes.md](../rsi-pattern-learning-notes.md) | 7.8KB |
| **布林带形态** | [bollinger-bands-pattern-learning-notes.md](../bollinger-bands-pattern-learning-notes.md) | 7.9KB |

### 日内/突破（1个）

| 策略 | 文档位置 | 大小 |
|------|---------|------|
| **Dual Thrust** | [dual-thrust-learning-notes.md](../dual-thrust-learning-notes.md) | 7.5KB |

### 技术指标（1个）

| 策略 | 文档位置 | 大小 |
|------|---------|------|
| **Heikin-Ashi** | [heikin-ashi-learning-notes.md](../heikin-ashi-learning-notes.md) | 8.4KB |

### 统计套利（1个）

| 策略 | 文档位置 | 大小 |
|------|---------|------|
| **配对交易** | [pair-trading-learning-notes.md](../pair-trading-learning-notes.md) | 8.2KB |

### 其他主题（4个）

| 主题 | 文档位置 | 大小 |
|------|---------|------|
| **因子投资** | [factor-investing-learning-notes.md](../factor-investing-learning-notes.md) | 9.7KB |
| **量化项目** | [quantitative-projects-learning-notes.md](../quantitative-projects-learning-notes.md) | 7.0KB |
| **量价分析** | [volume-price-trading-learning-guide.md](../volume-price-trading-learning-guide.md) | 7.0KB |
| **学习总结** | [trading-strategies-learning-summary-phase1.md](../trading-strategies-learning-summary-phase1.md) | 6.5KB |

---

## 📊 学习状态统计

| 状态 | 数量 | 说明 |
|------|------|------|
| **已学习** | 10 | 包含策略和主题 |
| **待学习** | 6 | quant-trading 剩余策略 |
| **总计** | 16 | - |

---

## 🎯 待学习策略（6个）

### 高优先级

1. **Awesome Oscillator** - 动量指标（MACD变体）
2. **Parabolic SAR** - 趋势跟踪（止损利器）

### 中优先级

3. **London Breakout** - 伦敦突破（类似Dual Thrust）

### 低优先级

4. **Shooting Star** - 形态识别
5. **Options Straddle** - 期权策略
6. **VIX Calculator** - 波动率计算

---

## ⚠️ 学习规则（重要！）

### 避免重复学习

1. **学习前检查**：查看 `LEARNING_INDEX.json`
2. **每个策略一份文档**：不要创建重复文件
3. **完善已有文档**：如果存在，就增强它
4. **统一命名**：使用 `{strategy}-learning-notes.md`

### 学习流程

```
1. 检查 LEARNING_INDEX.json → 是否已学习？
   ├─ 是 → 完善已有文档
   └─ 否 → 创建新文档

2. 学习策略代码
   - 核心逻辑（一句话概括）
   - 计算公式
   - 交易规则
   - Python 实现

3. 创建学习文档（2-4KB）
   - 通俗易懂的解释
   - 实战技巧
   - 代码示例

4. 更新 LEARNING_INDEX.json
```

---

## 💻 快速使用

### 查看已学习策略

```bash
# 查看索引
cat LEARNING_INDEX.json

# 查看某个策略
cat macd-oscillator-learning-notes.md
```

### 学习新策略

```bash
# 1. 检查是否已学习
grep "策略名" LEARNING_INDEX.json

# 2. 如果未学习，查看原始代码
cat projects/quant-trading/策略名.py

# 3. 创建学习文档（2-4KB）
# 4. 更新索引
```

---

## 📁 文件组织

```
Knowledge/trading-strategies/
├── LEARNING_INDEX.json              # 学习索引（必查！）
├── LEARNING_WORKFLOW.md             # 学习流程指南
│
├── learned/                          # 学习报告目录
│   ├── README.md                     # 本文件
│   └── LEARNING_REPORT.md            # 学习报告
│
├── macd-oscillator-learning-notes.md
├── rsi-pattern-learning-notes.md
├── dual-thrust-learning-notes.md
├── bollinger-bands-pattern-learning-notes.md
├── heikin-ashi-learning-notes.md
├── pair-trading-learning-notes.md
├── factor-investing-learning-notes.md
├── quantitative-projects-learning-notes.md
├── volume-price-trading-learning-guide.md
└── trading-strategies-learning-summary-phase1.md
```

---

## 🔗 相关链接

- [学习索引 JSON](../LEARNING_INDEX.json)
- [学习流程指南](../LEARNING_WORKFLOW.md)
- [策略总库](../STRATEGY-LIBRARY.md)
- [原始代码](../../../projects/quant-trading/)

---

*维护者: 小秘*
*更新时间: 2026-03-16 09:10*
*总策略数: 10 个已学习*
