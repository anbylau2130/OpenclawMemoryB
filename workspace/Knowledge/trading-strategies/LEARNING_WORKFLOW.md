# 策略学习流程 - 高效指南

> 📚 如何高效学习策略，避免重复
> 📅 创建时间: 2026-03-16
> ⚡ 目标：快速、高效、无重复

---

## 🎯 核心原则

1. **一个策略一份文档** - 绝不重复
2. **先查后学** - 学习前必须检查索引
3. **完善优先** - 已存在就增强，不创建新的
4. **快速高效** - 5分钟内完成一个策略学习

---

## 📋 学习流程（3步）

### 第1步：检查索引（10秒）

```bash
# 查看学习索引
cat Knowledge/trading-strategies/LEARNING_INDEX.json | grep "策略名"

# 或者直接查看
cat Knowledge/trading-strategies/learned/README.md
```

**判断：**
- ✅ **已学习** → 跳到第3步（完善文档）
- ❌ **未学习** → 继续第2步（创建文档）

---

### 第2步：创建学习文档（3分钟）

#### 快速模板

```markdown
# {策略名称} 学习笔记

> 📊 策略类型：{类型}
> 🎯 核心逻辑：{一句话概括}
> 📅 学习时间：{日期}

## 🎯 一句话概括
{核心交易逻辑}

## 📊 计算公式
\`\`\`python
# 核心指标计算
{主要公式}
\`\`\`

## 💻 交易规则
- **买入信号**：{条件}
- **卖出信号**：{条件}
- **止损规则**：{规则}

## 📝 Python 实现
\`\`\`python
def strategy(data):
    # 策略实现（10-20行）
    return signals
\`\`\`

## ⚠️ 注意事项
- 适用场景：{场景}
- 避免陷阱：{陷阱}

---
*学习时间: {日期}*
```

#### 填写要点

1. **一句话概括** - 最重要的交易逻辑
2. **计算公式** - 只写核心公式，不要长篇大论
3. **交易规则** - 明确的买卖条件
4. **Python实现** - 简洁的代码（<30行）
5. **注意事项** - 实战要点

---

### 第3步：更新索引（10秒）

```bash
# 在 LEARNING_INDEX.json 中添加
"{STRATEGY_NAME}": {
  "learned": true,
  "file": "learned/{STRATEGY_NAME}_LEARNED.md",
  "source": "quant-trading/{原始文件}.py",
  "date": "2026-03-16",
  "type": "{类型}",
  "win_rate": "{胜率}"
}
```

---

## 🚀 快速学习示例

### 示例1：MACD（3分钟完成）

```markdown
# MACD 振荡器学习笔记

> 📊 趋势跟踪
> 🎯 核心逻辑：金叉买入，死叉卖出

## 计算公式
\`\`\`python
MACD = EMA(12) - EMA(26)
Signal = EMA(MACD, 9)
\`\`\`

## 交易规则
- 买入：MACD 上穿 Signal
- 卖出：MACD 下穿 Signal

## Python 实现
\`\`\`python
def macd(data):
    ema12 = data['Close'].ewm(12).mean()
    ema26 = data['Close'].ewm(26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(9).mean()

    data['buy'] = (macd > signal) & (macd.shift(1) <= signal.shift(1))
    return data
\`\`\`

## 注意事项
- ✅ 趋势市场效果好
- ❌ 震荡市假信号多
```

### 示例2：RSI（3分钟完成）

```markdown
# RSI 超买超卖学习笔记

> 📊 均值回归
> 🎯 核心逻辑：RSI<30买入，RSI>70卖出

## 计算公式
\`\`\`python
RS = 平均涨幅 / 平均跌幅
RSI = 100 - 100/(1+RS)
\`\`\`

## 交易规则
- 买入：RSI < 30（超卖）
- 卖出：RSI > 70（超买）

## Python 实现
\`\`\`python
def rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    data['rsi'] = 100 - 100 / (1 + gain/loss)
    data['signal'] = np.select([data['rsi']<30, data['rsi']>70], [1,-1], 0)
    return data
\`\`\`
```

---

## ⚡ 效率对比

| 方式 | 耗时 | 文档长度 | 重复率 |
|------|------|---------|--------|
| **旧方式** | 10-15分钟 | 8-12KB | 高（重复创建） |
| **新方式** | 3-5分钟 | 2-4KB | 0（无重复） |
| **效率提升** | **3倍** | **简洁50%** | **无重复** |

---

## 📊 学习优先级

### 高优先级（先学这些）

1. **Pair Trading** - 配对交易（统计套利，胜率高）
2. **Awesome Oscillator** - 动量指标（MACD变体）
3. **Parabolic SAR** - 趋势跟踪（止损利器）

### 中优先级

4. **London Breakout** - 伦敦突破（类似Dual Thrust）
5. **Heikin-Ashi** - 平均K线（过滤噪音）

### 低优先级

6. **Shooting Star** - 形态识别（使用较少）
7. **Options Straddle** - 期权策略（非股票）
8. **VIX Calculator** - 波动率（辅助工具）

---

## ✅ 学习检查清单

学习新策略前，确认：

- [ ] 已查看 `LEARNING_INDEX.json`
- [ ] 确认该策略未学习过
- [ ] 如已存在，选择完善而非新建
- [ ] 使用简洁模板（<4KB）
- [ ] 更新索引文件

---

## 🔧 工具辅助

### 快速查询脚本

```bash
#!/bin/bash
# 查询策略是否已学习

STRATEGY=$1
if grep -q "\"$STRATEGY\"" Knowledge/trading-strategies/LEARNING_INDEX.json; then
    echo "✅ 已学习"
    grep -A 5 "\"$STRATEGY\"" Knowledge/trading-strategies/LEARNING_INDEX.json
else
    echo "❌ 未学习"
    echo "原始代码："
    ls projects/quant-trading/*$STRATEGY*.py 2>/dev/null
fi
```

---

## 📁 文件组织

```
Knowledge/trading-strategies/
├── LEARNING_INDEX.json              # 学习索引（必查）
├── learned/                          # 学习文档目录
│   ├── README.md                     # 总索引
│   ├── MACD_OSCILLATOR_LEARNED.md    # MACD
│   └── RSI_PATTERN_RECOGNITION_LEARNED.md  # RSI
├── bollinger-bands-pattern-learning-notes.md  # 布林带
└── dual-thrust-learning-notes.md    # Dual Thrust
```

---

## 🎯 总结

**高效学习 = 查索引 + 简洁模板 + 更新索引**

1. **10秒** - 查看索引
2. **3分钟** - 创建/完善文档
3. **10秒** - 更新索引

**总计：3-5分钟/策略，无重复！**

---

*创建时间: 2026-03-16*
*维护者: 小秘*
