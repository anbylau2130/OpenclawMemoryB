# MACD Oscillator（指数平滑异同移动平均线）学习笔记

> 学习时间：2026-03-12 21:45 UTC
> 来源：je-suis-tm/quant-trading
> 文件：MACD Oscillator backtest.py

---

## 🎯 核心概念

### 什么是 MACD？

**MACD（Moving Average Convergence/Divergence）**：
- 动量指标
- 趋势跟踪
- 最常用的技术指标之一

### 历史背景

> "很久以前，一周有6个交易日"
> "所以是2周均线 vs 1月均线"
> "现在理想选择是 10 和 21"

---

## 📊 计算公式

### 移动平均计算

```python
def macd(signals):
    # 短期移动平均（默认12，建议10）
    signals['ma1'] = signals['Close'].rolling(window=ma1, min_periods=1).mean()
    
    # 长期移动平均（默认26，建议21）
    signals['ma2'] = signals['Close'].rolling(window=ma2, min_periods=1).mean()
    
    return signals
```

### MACD 线

```python
# MACD = 短期均线 - 长期均线
signals['oscillator'] = signals['ma1'] - signals['ma2']
```

---

## 📊 信号生成规则

### 基本规则

```python
def signal_generation(df, method):
    signals = method(df)
    signals['positions'] = 0
    
    # 当短期均线 >= 长期均线，做多
    signals['positions'][ma1:] = np.where(
        signals['ma1'][ma1:] >= signals['ma2'][ma1:],
        1,  # 做多
        0   # 空仓
    )
    
    # 生成交易信号（差分）
    signals['signals'] = signals['positions'].diff()
    
    # MACD 振荡器
    signals['oscillator'] = signals['ma1'] - signals['ma2']
    
    return signals
```

---

### 信号解读

**金叉（Golden Cross）**：
```python
# 短期均线上穿长期均线
if (signals['ma1'][i] > signals['ma2'][i]) and \
   (signals['ma1'][i-1] <= signals['ma2'][i-1]):
    # 做多信号
    buy_signal()
```

**死叉（Death Cross）**：
```python
# 短期均线下穿长期均线
if (signals['ma1'][i] < signals['ma2'][i]) and \
   (signals['ma1'][i-1] >= signals['ma2'][i-1]):
    # 做空/平仓信号
    sell_signal()
```

---

## 💡 策略逻辑

### 为什么有效？

**1. 动量原理**
> "动量对短期移动平均的影响更大"

- 短期均线反应快
- 长期均线反应慢
- 差值 = 动量方向

---

**2. 趋势跟踪**
- MACD > 0：上升趋势
- MACD < 0：下降趋势
- MACD = 0：无趋势

---

### MACD 与 EMA 螺旋

**作者警告**：
> "注意向下EMA螺旋！"

**问题**：
- 入场信号总是滞后
- 在快速下跌市场中，MACD 可能一直为负
- 无法及时退出

**应对**：
- 结合止损
- 使用多个时间框架
- 结合其他指标

---

## 🔍 量价分析应用

### 结合成交量

**1. 成交量确认**
```python
# MACD 金叉 + 成交量放大
if (macd_golden_cross) and (volume > avg_volume * 1.5):
    # 成交量确认，增强信号
    signal_strength = 2
```

**2. OBV 验证**
```python
# MACD 上升趋势 + OBV 上升
if (macd > 0) and (obv > obv_ma):
    # 量价配合，强趋势
    strong_trend()
```

**3. 成交量背离**
```python
# MACD 上升 + 成交量下降 = 动能减弱
if (macd > 0) and (volume < avg_volume * 0.5):
    # 动能减弱，准备退出
    prepare_exit()
```

---

## ⚠️ 重要注意事项

### 1. 滞后性

**问题**：
- 移动平均是滞后指标
- 信号滞后于价格
- 可能错过最佳入场点

**应对**：
- 使用更短的周期（10/21）
- 结合领先指标（RSI, 成交量）
- 分批建仓

---

### 2. 震荡市场失效

**问题**：
- 横盘震荡时，频繁交叉
- 假信号多

**应对**：
- 使用 ADX 过滤趋势
- 避免震荡市场
- 增加确认条件

---

### 3. 参数选择

**经典参数**：
- 12/26（旧标准，一周6天）

**现代参数**：
- 10/21（一周5天）
- 更快反应

**其他选择**：
- 5/13（超短线）
- 20/50（长线）

---

## 📈 实战案例

### 三一重工 MACD 策略

**步骤**：
1. 获取历史数据
2. 计算 MACD（10/21）
3. 等待金叉信号
4. 检查成交量（放大）
5. 执行交易
6. 等待死叉平仓

**代码示例**：
```python
# 获取数据
df = yf.download('sh600031.SS', period='6mo')

# 计算 MACD
df['ma1'] = df['Close'].rolling(10).mean()
df['ma2'] = df['Close'].rolling(21).mean()
df['macd'] = df['ma1'] - df['ma2']

# 生成信号
df['signal'] = np.where(df['ma1'] >= df['ma2'], 1, 0)
df['positions'] = df['signal'].diff()

# 检查最新信号
if df['positions'].iloc[-1] == 1:
    print("MACD 金叉，买入信号")
elif df['positions'].iloc[-1] == -1:
    print("MACD 死叉，卖出信号")
```

---

## 💻 完整代码流程

```python
# 1. 计算移动平均
def macd(signals):
    signals['ma1'] = signals['Close'].rolling(window=ma1).mean()
    signals['ma2'] = signals['Close'].rolling(window=ma2).mean()
    return signals

# 2. 生成信号
def signal_generation(df, method):
    signals = method(df)
    signals['positions'] = 0
    signals['positions'][ma1:] = np.where(
        signals['ma1'][ma1:] >= signals['ma2'][ma1:],
        1, 0
    )
    signals['signals'] = signals['positions'].diff()
    signals['oscillator'] = signals['ma1'] - signals['ma2']
    return signals

# 3. 执行交易
def execute_trade(df):
    signals = signal_generation(df, macd)
    if signals['signals'].iloc[-1] == 1:
        print("买入")
    elif signals['signals'].iloc[-1] == -1:
        print("卖出")
```

---

## 🎯 学习总结

### 核心要点

1. **MACD 基础**
   - 短期均线 vs 长期均线
   - 金叉/死叉
   - 动量方向

2. **参数选择**
   - 经典：12/26
   - 现代：10/21
   - 根据交易风格调整

3. **趋势跟踪**
   - MACD > 0：上升
   - MACD < 0：下降
   - 趋势确认

4. **结合成交量**
   - 成交量确认
   - OBV 验证
   - 动能判断

---

### 优缺点

**优点**：
- ✅ 简单易懂
- ✅ 广泛使用
- ✅ 趋势跟踪效果好
- ✅ 可视化清晰

**缺点**：
- ❌ 滞后性
- ❌ 震荡市场失效
- ❌ 向下EMA螺旋风险
- ❌ 需要结合其他指标

---

### 与其他指标结合

**1. RSI**
```python
# MACD 金叉 + RSI 超卖
if (macd_golden_cross) and (RSI < 30):
    strong_buy()
```

**2. Bollinger Bands**
```python
# MACD 上升 + 触及布林带下轨
if (macd > 0) and (price < lower_band):
    reversal_buy()
```

**3. 成交量**
```python
# MACD 金叉 + 成交量放大
if (macd_golden_cross) and (volume > avg_volume * 1.5):
    confirmed_buy()
```

---

## 📚 延伸阅读

### 经典资源

**1. TradingView Wiki**
- MACD 详细说明
- 策略应用
- 实战案例

**2. Investopedia**
- MACD Definition
- Trading Strategy

**3. 书籍**
- "Technical Analysis of the Financial Markets" - John Murphy

---

## 📝 下一步

1. ✅ 理解 MACD 基础
2. ⏳ 在三一重工上应用
3. ⏳ 结合成交量验证
4. ⏳ 回测验证
5. ⏳ 实盘测试

---

_学习笔记创建时间：2026-03-12 21:45 UTC_
