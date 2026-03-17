# RSI Pattern Recognition（RSI形态识别）学习笔记

> 学习时间：2026-03-12 21:30 UTC
> 来源：je-suis-tm/quant-trading
> 文件：RSI Pattern Recognition backtest.py

---

## 🎯 核心概念

### 什么是 RSI？

**相对强弱指数（Relative Strength Index）**：
- 衡量价格变动的速度和幅度
- 范围：0-100
- 超买：RSI > 70
- 超卖：RSI < 30

### RSI 计算公式

```python
def rsi(data, n=14):
    # 价格变化
    delta = data.diff().dropna()
    
    # 上涨和下跌
    up = np.where(delta > 0, delta, 0)
    down = np.where(delta < 0, -delta, 0)
    
    # 平滑移动平均
    rs = np.divide(smma(up, n), smma(down, n))
    
    # RSI
    output = 100 - 100 / (1 + rs)
    
    return output[n-1:]
```

---

## 📊 策略一：超买/超卖

### 基本逻辑

```python
# RSI > 70：超买，做空
# RSI < 30：超卖，做多

def signal_generation(df, method, n=14):
    df['rsi'] = method(df['Close'], n=14)
    
    # 信号生成
    df['positions'] = np.select(
        [df['rsi'] < 30, df['rsi'] > 70],
        [1, -1],  # 做多，做空
        default=0
    )
    
    df['signals'] = df['positions'].diff()
    return df
```

---

### 策略逻辑

**超买（RSI > 70）**：
- 价格上涨过快
- 可能回调
- 做空信号

**超卖（RSI < 30）**：
- 价格下跌过快
- 可能反弹
- 做多信号

---

## 📊 策略二：头肩形态识别

### 头肩形态

**头肩顶（Head and Shoulders Top）**：
```
  l (左肩)   i (右肩)
      \     /
       \   /
        \ /
         j (头部)
```

**节点**：
- m：左起点
- l：左肩
- j：头部（最高点）
- k：颈部
- i：右肩

---

### 识别算法

```python
def pattern_recognition(df, method, lag=14):
    # 参数
    period = 25  # 形态识别窗口
    delta = 0.2  # 价格差异阈值
    head = 1.1   # 头部显著性
    shoulder = 1.1  # 肩部显著性
    
    for i in range(period, len(df)):
        # 从右肩 i 开始
        # 找到头部 j（最大值）
        j = df['rsi'][i-period:i].idxmax()
        
        # 找到右肩 k（接近右肩 i）
        for k in range(i, j, -1):
            if abs(df['rsi'][k] - df['rsi'][i]) < delta:
                break
        
        # 找到左肩 l（接近右肩 i）
        for l in range(j, i-period, -1):
            if abs(df['rsi'][l] - df['rsi'][i]) < delta * shoulder:
                break
        
        # 找到左起点 m（接近右肩 i）
        for m in range(l, i-period, -1):
            if abs(df['rsi'][m] - df['rsi'][i]) < delta * shoulder:
                # 确认头部显著高于肩部
                if (df['rsi'][j] - df['rsi'][i]) > delta * head:
                    # 头肩顶确认，做空
                    df.at[i, 'signals'] = -1
                    break
```

---

### 退出策略

```python
# 两种退出条件
entry_rsi = df['rsi'][i]  # 入场 RSI
counter = 0
exit_rsi = 4  # RSI 上升阈值
exit_days = 5  # 持仓天数

# 条件 1：持仓超过 5 天
if counter > exit_days:
    df.at[i, 'signals'] = 1  # 平仓

# 条件 2：RSI 上升超过 4
if df['rsi'][i] - entry_rsi > exit_rsi:
    df.at[i, 'signals'] = 1  # 平仓

counter += 1
```

---

## 💡 策略逻辑

### 为什么 RSI 有效？

**均值回归**：
- RSI 极端值（> 70 或 < 30）不会持续
- 会回归到中性区域（40-60）

**市场心理**：
- RSI > 70：过度乐观，可能回调
- RSI < 30：过度悲观，可能反弹

---

### 头肩形态的意义

**头肩顶**：
- 左肩：第一次上涨，动能强劲
- 头部：第二次上涨，创新高但动能减弱
- 右肩：第三次上涨，无法创新高
- 趋势反转信号

---

## 🔍 量价分析应用

### 结合成交量

**1. 成交量确认**
```python
# RSI 超卖 + 成交量放大
if (rsi < 30) and (volume > avg_volume * 1.5):
    # 成交量放大，确认反弹
    signal_strength = 2
```

**2. OBV 背离**
```python
# RSI 底背离 + OBV 上升
if (price makes lower low) and (RSI makes higher low) and (OBV rising):
    # 强烈买入信号
    signal_strength = 3
```

**3. 成交量萎缩**
```python
# RSI 超买 + 成交量萎缩
if (rsi > 70) and (volume < avg_volume * 0.5):
    # 动能减弱，确认回调
    signal_strength = 2
```

---

## ⚠️ 重要注意事项

### 1. RSI 的局限性

**作者观点**：
> "实际上我觉得 RSI 有点扯淡"

**问题**：
- 趋势市场中，RSI 可能长期超买/超卖
- 假信号多
- 需要结合其他指标

---

### 2. 背离策略的争议

**Wilder（发明者）**：
- 看跌背离 → 卖出机会

**Cardwell（门徒）**：
- 看跌背离只在牛市中出现
- 与发明者观点矛盾

**结论**：
> "我会放弃这个扯淡的背离策略"

---

### 3. 参数调优

**RSI 周期**：
- 默认：14 天
- 短期：7-10 天（更敏感）
- 长期：21-28 天（更平滑）

**超买/超卖阈值**：
- 默认：70/30
- 保守：80/20
- 激进：60/40

---

## 📈 实战案例

### 三一重工 RSI 策略

**步骤**：
1. 计算 RSI（14天）
2. 等待 RSI < 30（超卖）
3. 检查成交量（放大）
4. 检查 OBV（背离）
5. 执行交易

**代码示例**：
```python
# 获取数据
df = yf.download('sh600031.SS', period='6mo')

# 计算 RSI
df['rsi'] = rsi(df['Close'], 14)

# 生成信号
if df['rsi'].iloc[-1] < 30:
    if df['Volume'].iloc[-1] > df['Volume'].rolling(20).mean().iloc[-1] * 1.5:
        print("RSI 超卖 + 成交量放大，买入信号")
```

---

## 💻 完整代码流程

```python
# 1. 平滑移动平均
def smma(series, n):
    output = [series[0]]
    for i in range(1, len(series)):
        temp = output[-1] * (n-1) + series[i]
        output.append(temp / n)
    return output

# 2. RSI 计算
def rsi(data, n=14):
    delta = data.diff().dropna()
    up = np.where(delta > 0, delta, 0)
    down = np.where(delta < 0, -delta, 0)
    rs = np.divide(smma(up, n), smma(down, n))
    return 100 - 100 / (1 + rs)

# 3. 信号生成（超买/超卖）
def generate_signals(df):
    df['rsi'] = rsi(df['Close'], 14)
    df['signals'] = np.select(
        [df['rsi'] < 30, df['rsi'] > 70],
        [1, -1],
        default=0
    )
    return df

# 4. 头肩形态识别
def detect_head_shoulders(df, period=25, delta=0.2):
    for i in range(period, len(df)):
        j = df['rsi'][i-period:i].idxmax()
        # ... 形态识别逻辑
    return df
```

---

## 🎯 学习总结

### 核心要点

1. **RSI 基础**
   - 范围：0-100
   - 超买：> 70
   - 超卖：< 30

2. **超买/超卖策略**
   - 简单直接
   - 均值回归
   - 假信号多

3. **头肩形态**
   - 5个节点
   - 形态识别复杂
   - 趋势反转信号

4. **结合成交量**
   - 确认信号
   - 减少假信号
   - 提高胜率

---

### 优缺点

**优点**：
- ✅ 逻辑简单
- ✅ 广泛使用
- ✅ 可视化清晰
- ✅ 适合震荡市场

**缺点**：
- ❌ 趋势市场失效
- ❌ 假信号多
- ❌ 背离策略有争议
- ❌ 需要结合其他指标

---

### 与其他指标结合

**1. 布林带**
```python
# RSI 超卖 + 触及布林带下轨
if (rsi < 30) and (price < lower_band):
    strong_buy_signal()
```

**2. MACD**
```python
# RSI 超卖 + MACD 金叉
if (rsi < 30) and (MACD_golden_cross):
    execute_trade()
```

**3. 成交量**
```python
# RSI 超卖 + 成交量放大
if (rsi < 30) and (volume > avg_volume * 1.5):
    confirmed_signal()
```

---

## 📚 延伸阅读

### 经典资源

**1. TradingView Wiki**
- RSI 详细说明
- 策略应用
- 实战案例

**2. Investopedia**
- Head and Shoulders Pattern
- RSI Strategy

**3. 书籍**
- "New Concepts in Technical Trading Systems" - J. Welles Wilder（RSI 发明者）

---

## 📝 下一步

1. ✅ 理解 RSI 基础
2. ⏳ 在三一重工上应用 RSI
3. ⏳ 结合成交量验证
4. ⏳ 回测验证
5. ⏳ 实盘测试

---

_学习笔记创建时间：2026-03-12 21:30 UTC_
