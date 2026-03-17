# 交易策略学习总结 - 第一阶段

> 学习时间：2026-03-12 21:40 UTC
> 来源：GitHub - je-suis-tm/quant-trading
> 状态：已完成 4 个核心策略学习

---

## 🎯 学习成果

### 已学习策略

1. ✅ **Pair Trading（配对交易）**
   - 协整关系
   - 均值回归
   - 统计套利

2. ✅ **Bollinger Bands Pattern Recognition（布林带形态识别）**
   - W 底形态
   - 算术方法
   - 带宽收缩

3. ✅ **RSI Pattern Recognition（RSI形态识别）**
   - 超买/超卖
   - 头肩形态
   - 均值回归

4. ✅ **Heikin-Ashi（平均K线）**
   - 趋势过滤
   - K线形态
   - 动能确认

---

## 📊 策略对比

| 策略 | 核心原理 | 适用市场 | 信号类型 | 难度 |
|------|---------|---------|---------|------|
| Pair Trading | 协整关系 | 震荡市场 | 对冲 | ⭐⭐⭐ |
| Bollinger Bands | 形态识别 | 震荡市场 | 反转 | ⭐⭐⭐⭐ |
| RSI | 超买超卖 | 震荡市场 | 反转 | ⭐⭐ |
| Heikin-Ashi | 趋势过滤 | 趋势市场 | 趋势 | ⭐⭐ |

---

## 🔍 量价分析核心要点

### 1. 成交量确认

**所有策略都应结合成交量**：
```python
# 成交量放大 = 信号确认
if signal and (volume > avg_volume * 1.5):
    signal_strength *= 2
```

---

### 2. OBV 验证

**OBV 是量价分析的核心指标**：
```python
# OBV 背离 = 趋势反转
if (price makes lower low) and (OBV makes higher low):
    strong_reversal_signal()
```

---

### 3. 成交量萎缩

**成交量萎缩 = 动能减弱**：
```python
# 成交量萎缩 = 趋势结束
if trend and (volume < avg_volume * 0.5):
    prepare_exit()
```

---

## 💡 策略组合建议

### 组合 1：趋势 + 成交量

**Heikin-Ashi + OBV**：
```python
# Heikin-Ashi 识别趋势
# OBV 确认量价配合
if (ha_trend == 'up') and (obv > obv_ma):
    strong_buy()
```

---

### 组合 2：反转 + 成交量

**Bollinger Bands + 成交量**：
```python
# 布林带 W 底
# 成交量放大确认
if (w_bottom_detected) and (volume > avg_volume * 1.5):
    confirmed_buy()
```

---

### 组合 3：统计套利 + 趋势过滤

**Pair Trading + Heikin-Ashi**：
```python
# 配对交易信号
# Heikin-Ashi 过滤趋势
if (pair_signal) and (not ha_trending):
    execute_pair_trade()
```

---

## 📚 学习笔记清单

### 已创建文档

1. ✅ `pair-trading-learning-notes.md`（5.8KB）
2. ✅ `bollinger-bands-pattern-learning-notes.md`（5.8KB）
3. ✅ `rsi-pattern-learning-notes.md`（5.8KB）
4. ✅ `heikin-ashi-learning-notes.md`（6.1KB）

**总计**：23.5KB 学习笔记

---

## 🎯 下一步学习计划

### 阶段 2：实战应用（1-2周）

**1. 在三一重工上验证**
- [ ] 获取历史数据
- [ ] 实现各个策略
- [ ] 回测验证
- [ ] 参数优化

**2. 构建组合策略**
- [ ] 趋势 + 成交量组合
- [ ] 反转 + 成交量组合
- [ ] 多指标组合

**3. 实盘测试**
- [ ] 小仓位验证
- [ ] 记录交易结果
- [ ] 优化策略

---

### 阶段 3：深度学习（2-3周）

**1. 学习更多策略**
- [ ] MACD Oscillator
- [ ] Dual Thrust
- [ ] London Breakout
- [ ] Parabolic SAR

**2. 学习量化项目**
- [ ] Monte Carlo Project
- [ ] Oil Money Project
- [ ] Smart Farmers Project

---

## 📊 关键代码片段

### 1. 协整检验（Pair Trading）

```python
def EG_method(X, Y):
    # 第一步：长期均衡
    model1 = sm.OLS(Y, sm.add_constant(X)).fit()
    epsilon = model1.resid
    
    # ADF 检验
    if sm.tsa.stattools.adfuller(epsilon)[1] > 0.05:
        return False, model1
    
    # 第二步：误差修正
    X_dif = sm.add_constant(pd.concat([X.diff(), epsilon.shift(1)], axis=1))
    Y_dif = Y.diff()
    model2 = sm.OLS(Y_dif, X_dif).fit()
    
    if model2.params[-1] > 0:
        return False, model1
    else:
        return True, model1
```

---

### 2. 布林带计算

```python
def bollinger_bands(df):
    df['std'] = df['price'].rolling(20).std()
    df['mid'] = df['price'].rolling(20).mean()
    df['upper'] = df['mid'] + 2 * df['std']
    df['lower'] = df['mid'] - 2 * df['std']
    return df
```

---

### 3. RSI 计算

```python
def rsi(data, n=14):
    delta = data.diff().dropna()
    up = np.where(delta > 0, delta, 0)
    down = np.where(delta < 0, -delta, 0)
    rs = np.divide(smma(up, n), smma(down, n))
    return 100 - 100 / (1 + rs)
```

---

### 4. Heikin-Ashi 计算

```python
def heikin_ashi(data):
    df['HA close'] = (df['Open'] + df['Close'] + df['High'] + df['Low']) / 4
    df['HA open'][0] = df['Open'][0]
    for n in range(1, len(df)):
        df.at[n, 'HA open'] = (df['HA open'][n-1] + df['HA close'][n-1]) / 2
    temp = pd.concat([df['HA open'], df['HA close'], df['Low'], df['High']], axis=1)
    df['HA high'] = temp.apply(max, axis=1)
    df['HA low'] = temp.apply(min, axis=1)
    return df
```

---

## 💡 核心心得

### 1. 量价配合是关键

> "成交量是价格的验证者"

- 所有策略都应结合成交量
- OBV 是最好的量价指标
- 成交量背离是强烈的反转信号

---

### 2. 形态识别不一定需要机器学习

> "算术方法更快更简单"

- W 底、头肩形态可以用数学方法识别
- 逻辑清晰，可解释性强
- 计算速度快

---

### 3. 协整关系不是永久的

> "协整关系会破裂"

- NVIDIA 和 AMD 的案例
- 每次交易前重新检验
- 市场条件是动态的

---

### 4. 趋势和震荡要区分

> "不同策略适用于不同市场"

- 趋势市场：Heikin-Ashi, MACD
- 震荡市场：Pair Trading, Bollinger Bands, RSI
- 用 ADX 判断趋势强度

---

## 📚 延伸资源

### GitHub 仓库

**已克隆**：
- `/root/.openclaw/workspace/projects/quant-trading-repo/`

**包含**：
- 15+ 种策略
- 3 个量化项目
- 完整代码示例

---

### 文档清单

**学习笔记**：
- `memory/learning/pair-trading-learning-notes.md`
- `memory/learning/bollinger-bands-pattern-learning-notes.md`
- `memory/learning/rsi-pattern-learning-notes.md`
- `memory/learning/heikin-ashi-learning-notes.md`
- `memory/learning/github-trading-strategies-collection.md`
- `memory/learning/volume-price-trading-learning-guide.md`
- `memory/learning/volume-price-trading-resources.md`

---

## 🎯 最终目标

**4周后能够**：
1. ✅ 理解 4 个核心策略
2. ⏳ 掌握量价分析方法
3. ⏳ 在三一重工上验证
4. ⏳ 构建自己的策略组合
5. ⏳ 实盘小仓位测试

---

_学习总结创建时间：2026-03-12 21:40 UTC_
_已完成第一阶段学习_
