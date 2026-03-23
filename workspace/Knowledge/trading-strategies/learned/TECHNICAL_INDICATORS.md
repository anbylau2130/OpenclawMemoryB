# 技术指标学习指南

> 来源：OpenclawMemery 仓库
> 日期：2026-03-17

---

## 📊 一、基础指标（必学）

### 1. 趋势指标
```python
# 移动平均线
MA5 = df['close'].rolling(5).mean()
MA10 = df['close'].rolling(10).mean()
MA20 = df['close'].rolling(20).mean()

# 指数移动平均
EMA12 = df['close'].ewm(span=12).mean()
EMA26 = df['close'].ewm(span=26).mean()

# 信号：金叉（MA5上穿MA10）、死叉（MA5下穿MA10）
```

### 2. 动量指标
```python
# RSI（相对强弱指数）
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# 信号：RSI < 30 超卖，RSI > 70 超买
```

### 3. 波动率指标
```python
# 布林带
def calculate_bollinger_bands(prices, period=20):
    middle = prices.rolling(period).mean()
    std = prices.rolling(period).std()
    upper = middle + 2 * std
    lower = middle - 2 * std
    return upper, middle, lower

# 信号：价格触及下轨买入，触及上轨卖出
```

### 4. 成交量指标
```python
# OBV（能量潮）
def calculate_obv(df):
    obv = [0]
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['close'].iloc[i-1]:
            obv.append(obv[-1] + df['volume'].iloc[i])
        elif df['close'].iloc[i] < df['close'].iloc[i-1]:
            obv.append(obv[-1] - df['volume'].iloc[i])
        else:
            obv.append(obv[-1])
    return pd.Series(obv, index=df.index)

# 信号：OBV上升 + 价格上涨 = 强势
```

---

## 📈 二、进阶指标

### 1. MACD
```python
def calculate_macd(prices):
    ema12 = prices.ewm(span=12).mean()
    ema26 = prices.ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    histogram = macd - signal
    return macd, signal, histogram

# 信号：MACD上穿Signal买入，下穿卖出
```

### 2. KDJ
```python
def calculate_kdj(df, period=9):
    low_min = df['low'].rolling(period).min()
    high_max = df['high'].rolling(period).max()

    rsv = (df['close'] - low_min) / (high_max - low_min) * 100

    k = rsv.ewm(alpha=1/3).mean()
    d = k.ewm(alpha=1/3).mean()
    j = 3 * k - 2 * d

    return k, d, j

# 信号：K上穿D买入，K下穿D卖出
```

### 3. ATR（平均真实波幅）
```python
def calculate_atr(df, period=14):
    high = df['high']
    low = df['low']
    close = df['close'].shift(1)

    tr1 = high - low
    tr2 = abs(high - close)
    tr3 = abs(low - close)

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()

    return atr

# 用途：计算止损位、仓位大小
```

---

## 🎯 三、组合指标策略

### 1. 趋势确认
```python
def trend_confirmation(df):
    """趋势确认策略"""
    signals = []

    # 条件1：MA5 > MA10 > MA20（上升趋势）
    ma5 = df['close'].rolling(5).mean()
    ma10 = df['close'].rolling(10).mean()
    ma20 = df['close'].rolling(20).mean()

    # 条件2：RSI 30-70之间
    rsi = calculate_rsi(df['close'])

    # 条件3：MACD金叉
    macd, signal, _ = calculate_macd(df['close'])

    # 组合信号
    for i in range(len(df)):
        if (ma5.iloc[i] > ma10.iloc[i] > ma20.iloc[i] and
            30 < rsi.iloc[i] < 70 and
            macd.iloc[i] > signal.iloc[i]):
            signals.append('BUY')
        elif (ma5.iloc[i] < ma10.iloc[i] < ma20.iloc[i] and
              rsi.iloc[i] > 70):
            signals.append('SELL')
        else:
            signals.append('HOLD')

    return signals
```

### 2. 超买超卖
```python
def overbought_oversold(df):
    """超买超卖策略"""
    signals = []

    rsi = calculate_rsi(df['close'])
    upper, middle, lower = calculate_bollinger_bands(df['close'])

    for i in range(len(df)):
        # 超卖：RSI < 30 且 价格 < 下轨
        if rsi.iloc[i] < 30 and df['close'].iloc[i] < lower.iloc[i]:
            signals.append('STRONG_BUY')
        # 超买：RSI > 70 且 价格 > 上轨
        elif rsi.iloc[i] > 70 and df['close'].iloc[i] > upper.iloc[i]:
            signals.append('STRONG_SELL')
        else:
            signals.append('HOLD')

    return signals
```

---

## 💡 四、A股做T指标

### 1. 开盘价偏离
```python
def opening_price_deviation(df):
    """开盘价偏离策略"""
    open_price = df['open'].iloc[0]
    current_price = df['close'].iloc[-1]

    deviation = (current_price - open_price) / open_price * 100

    if deviation < -1.0:
        return 'BUY'  # 低于开盘价1%买入
    elif deviation > 1.5:
        return 'SELL'  # 高于开盘价1.5%卖出
    else:
        return 'HOLD'
```

### 2. 量价配合
```python
def volume_price_analysis(df):
    """量价配合分析"""
    price_change = df['close'].pct_change()
    volume_change = df['volume'].pct_change()

    # 价涨量增
    if price_change.iloc[-1] > 0 and volume_change.iloc[-1] > 0:
        return 'BULLISH'
    # 价涨量缩
    elif price_change.iloc[-1] > 0 and volume_change.iloc[-1] < 0:
        return 'WEAK_BULL'
    # 价跌量增
    elif price_change.iloc[-1] < 0 and volume_change.iloc[-1] > 0:
        return 'BEARISH'
    # 价跌量缩
    else:
        return 'WEAK_BEAR'
```

---

## 📚 五、学习路径

### 第1周：基础指标
- [x] 移动平均线（MA、EMA）
- [x] RSI
- [x] 布林带
- [x] 成交量指标

### 第2周：进阶指标
- [x] MACD
- [x] KDJ
- [x] ATR
- [ ] 威廉指标

### 第3周：组合策略
- [x] 趋势确认策略
- [x] 超买超卖策略
- [x] 量价配合策略

### 第4周：实战应用
- [x] 回测验证
- [ ] 参数优化
- [ ] 策略组合

---

## 🔧 六、V5系统已使用的指标

### 高胜率因子（已集成）

| 指标 | 胜率 | 权重 | 说明 |
|------|------|------|------|
| VWAP | 92% | +3 | 成交量加权平均价 |
| 布林带 | 71% | +2 | 下轨买入信号 |
| KDJ | 70% | +1.5 | 超买超卖 |
| RSI | 69% | +1.5 | 相对强弱 |

### 低效因子（已移除）

| 指标 | 胜率 | 说明 |
|------|------|------|
| 量价背离 | 28.7% | 严重亏损 |
| 双均线 | 36.3% | 胜率低 |
| MACD | 36.6% | 趋势跟踪在震荡市失效 |

---

_来源：OpenclawMemery 仓库 main 分支_
_提取时间：2026-03-17_
