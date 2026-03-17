# Heikin-Ashi（平均K线）学习笔记

> 学习时间：2026-03-12 21:35 UTC
> 来源：je-suis-tm/quant-trading
> 文件：Heikin-Ashi backtest.py

---

## 🎯 核心概念

### 什么是 Heikin-Ashi？

**Heikin-Ashi（平均K线）**：
- 日本技术分析方法
- 过滤市场噪音
- 识别趋势方向
- "Heikin" = 平均，"Ashi" = K线

### 与普通K线的区别

**普通K线**：
- Open, High, Low, Close = 实际价格

**Heikin-Ashi K线**：
- HA Open, HA High, HA Low, HA Close = 计算值
- 平滑处理，减少噪音

---

## 📊 计算公式

### Heikin-Ashi 计算

```python
def heikin_ashi(data):
    df = data.copy()
    
    # HA Close = (Open + High + Low + Close) / 4
    df['HA close'] = (df['Open'] + df['Close'] + df['High'] + df['Low']) / 4
    
    # HA Open = (前一日 HA Open + 前一日 HA Close) / 2
    df['HA open'] = float(0)
    df['HA open'][0] = df['Open'][0]  # 初始值
    
    for n in range(1, len(df)):
        df.at[n, 'HA open'] = (df['HA open'][n-1] + df['HA close'][n-1]) / 2
    
    # HA High = max(High, HA Open, HA Close)
    # HA Low = min(Low, HA Open, HA Close)
    temp = pd.concat([df['HA open'], df['HA close'], df['Low'], df['High']], axis=1)
    df['HA high'] = temp.apply(max, axis=1)
    df['HA low'] = temp.apply(min, axis=1)
    
    return df
```

---

### 公式详解

**1. HA Close**
```python
HA_Close = (Open + High + Low + Close) / 4
```
- 平均价格
- 平滑收盘价

**2. HA Open**
```python
HA_Open[t] = (HA_Open[t-1] + HA_Close[t-1]) / 2
```
- 递归计算
- 平滑开盘价

**3. HA High**
```python
HA_High = max(High, HA_Open, HA_Close)
```
- 取最大值
- 包含计算值

**4. HA Low**
```python
HA_Low = min(Low, HA_Open, HA_Close)
```
- 取最小值
- 包含计算值

---

## 📊 信号生成规则

### 做多信号（4个条件）

```python
# 条件 1：HA Open > HA Close（红色K线，下跌）
data['HA open'][n] > data['HA close'][n]

# 条件 2：HA Open = HA High（无上影线）
data['HA open'][n] == data['HA high'][n]

# 条件 3：实体大于前一日实体
abs(data['HA open'][n] - data['HA close'][n]) > abs(data['HA open'][n-1] - data['HA close'][n-1])

# 条件 4：前一日也是红色K线
data['HA open'][n-1] > data['HA close'][n-1]
```

**解释**：
- 条件 1-2：强下跌K线（光头阴线）
- 条件 3：动能增强
- 条件 4：趋势确认

---

### 平仓信号（3个条件）

```python
# 条件 1：HA Open < HA Close（绿色K线，上涨）
data['HA open'][n] < data['HA close'][n]

# 条件 2：HA Open = HA Low（无下影线）
data['HA open'][n] == data['HA low'][n]

# 条件 3：前一日也是绿色K线
data['HA open'][n-1] < data['HA close'][n-1]
```

**解释**：
- 条件 1-2：强上涨K线（光头阳线）
- 条件 3：趋势反转确认

---

## 💻 完整策略代码

```python
def signal_generation(df, method, stls):
    """
    df: 历史数据
    method: heikin_ashi 函数
    stls: 止损限制（最多持仓数）
    """
    data = method(df)
    data['signals'] = 0
    data['cumsum'] = 0  # 累计持仓
    
    for n in range(1, len(data)):
        # 做多信号（4个条件）
        if (data['HA open'][n] > data['HA close'][n] and 
            data['HA open'][n] == data['HA high'][n] and
            abs(data['HA open'][n] - data['HA close'][n]) > abs(data['HA open'][n-1] - data['HA close'][n-1]) and
            data['HA open'][n-1] > data['HA close'][n-1]):
            
            data.at[n, 'signals'] = 1
            data['cumsum'] = data['signals'].cumsum()
            
            # 检查止损
            if data['cumsum'][n] > stls:
                data.at[n, 'signals'] = 0
        
        # 平仓信号（3个条件）
        elif (data['HA open'][n] < data['HA close'][n] and 
              data['HA open'][n] == data['HA low'][n] and 
              data['HA open'][n-1] < data['HA close'][n-1]):
            
            data.at[n, 'signals'] = -1
            data['cumsum'] = data['signals'].cumsum()
            
            # 清空所有持仓
            if data['cumsum'][n] > 0:
                data.at[n, 'signals'] = -1 * (data['cumsum'][n-1])
            
            if data['cumsum'][n] < 0:
                data.at[n, 'signals'] = 0
    
    return data
```

---

## 💡 策略逻辑

### 为什么有效？

**1. 过滤噪音**
- 平滑处理减少假信号
- 更清晰的趋势识别

**2. 趋势识别**
- 连续红色K线 = 下跌趋势
- 连续绿色K线 = 上涨趋势
- 十字星 = 趋势反转

**3. 动能确认**
- 实体大小 = 动能强度
- 无影线 = 强趋势

---

### K线形态解读

**强上涨（绿色）**：
- HA Open = HA Low（无下影线）
- 实体大
- 连续出现

**强下跌（红色）**：
- HA Open = HA High（无上影线）
- 实体大
- 连续出现

**趋势反转**：
- 十字星（实体小）
- 颜色变化
- 影线出现

---

## 🔍 量价分析应用

### 结合成交量

**1. 成交量确认**
```python
# Heikin-Ashi 做多信号 + 成交量放大
if (ha_signal == 1) and (volume > avg_volume * 1.5):
    # 成交量确认，增强信号
    signal_strength = 2
```

**2. OBV 验证**
```python
# Heikin-Ashi 下跌 + OBV 上升 = 底背离
if (ha_trend == 'down') and (obv > obv_ma):
    # 底背离，准备反转
    watch_for_reversal()
```

**3. 成交量萎缩**
```python
# Heikin-Ashi 趋势 + 成交量萎缩 = 趋势减弱
if (ha_trend == 'up') and (volume < avg_volume * 0.5):
    # 动能减弱，准备平仓
    prepare_exit()
```

---

## ⚠️ 重要注意事项

### 1. 滞后性

**问题**：
- Heikin-Ashi 是平滑处理
- 信号滞后于实际价格
- 可能错过最佳入场点

**应对**：
- 结合其他领先指标
- 设置止损
- 分批建仓

---

### 2. 震荡市场失效

**问题**：
- 横盘震荡时，信号频繁
- 假信号多

**应对**：
- 结合趋势过滤器
- 避免震荡市场
- 使用 ADX 判断趋势强度

---

### 3. 止损设置

**代码中的止损**：
```python
# stls: stop loss limit
# 最多持仓数限制
if data['cumsum'][n] > stls:
    data.at[n, 'signals'] = 0
```

**建议**：
- 设置止损位（如 -3%）
- 分批建仓
- 控制总仓位

---

## 📈 实战案例

### 三一重工 Heikin-Ashi 策略

**步骤**：
1. 获取历史数据
2. 计算 Heikin-Ashi K线
3. 等待做多信号（4个条件）
4. 检查成交量（放大）
5. 执行交易
6. 等待平仓信号（3个条件）

**代码示例**：
```python
# 获取数据
df = yf.download('sh600031.SS', period='6mo')

# 计算 Heikin-Ashi
ha_df = heikin_ashi(df)

# 生成信号
signals = signal_generation(df, heikin_ashi, stls=3)

# 检查最新信号
if signals['signals'].iloc[-1] == 1:
    print("Heikin-Ashi 做多信号")
elif signals['signals'].iloc[-1] < 0:
    print("Heikin-Ashi 平仓信号")
```

---

## 🎯 学习总结

### 核心要点

1. **Heikin-Ashi 计算**
   - HA Close = (O+H+L+C)/4
   - HA Open = (前日HAO+前日HAC)/2
   - HA High/Low = max/min

2. **信号规则**
   - 做多：4个条件（光头阴线 + 动能增强）
   - 平仓：3个条件（光头阳线）

3. **趋势识别**
   - 连续红色 = 下跌
   - 连续绿色 = 上涨
   - 十字星 = 反转

4. **结合成交量**
   - 成交量确认
   - OBV 验证
   - 动能判断

---

### 优缺点

**优点**：
- ✅ 过滤噪音
- ✅ 趋势清晰
- ✅ 可视化好
- ✅ 规则明确

**缺点**：
- ❌ 信号滞后
- ❌ 震荡市场失效
- ❌ 需要结合其他指标
- ❌ 参数需要调优

---

### 与其他指标结合

**1. ADX（趋势强度）**
```python
# Heikin-Ashi + ADX
if (ha_signal == 1) and (ADX > 25):
    # 强趋势，执行交易
    execute_trade()
```

**2. MACD**
```python
# Heikin-Ashi + MACD
if (ha_trend == 'up') and (MACD_golden_cross):
    confirmed_buy()
```

**3. 成交量**
```python
# Heikin-Ashi + 成交量
if (ha_signal == 1) and (volume > avg_volume * 1.5):
    strong_signal()
```

---

## 📚 延伸阅读

### 经典资源

**1. Quantiacs**
- Intro to Algorithmic Trading with Heikin-Ashi
- 详细规则说明

**2. Investopedia**
- Heikin-Ashi Definition
- Trading Strategy

**3. 书籍**
- "Japanese Candlestick Charting Techniques" - Steve Nison

---

## 📝 下一步

1. ✅ 理解 Heikin-Ashi 计算
2. ⏳ 在三一重工上应用
3. ⏳ 结合成交量验证
4. ⏳ 回测验证
5. ⏳ 实盘测试

---

_学习笔记创建时间：2026-03-12 21:35 UTC_
