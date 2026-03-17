# Bollinger Bands Pattern Recognition（布林带形态识别）学习笔记

> 学习时间：2026-03-12 21:25 UTC
> 来源：je-suis-tm/quant-trading
> 文件：Bollinger Bands Pattern Recognition backtest.py

---

## 🎯 核心概念

### 什么是布林带？

布林带（Bollinger Bands）是一个简单但强大的技术指标：
- **中轨**：20日移动平均线
- **上轨**：中轨 + 2个标准差
- **下轨**：中轨 - 2个标准差

### 什么是形态识别？

**W 底（Double Bottom）**：
- 两个底部（k, m）+ 一个顶部（j）+ 两个肩部（l, i）
- 形状像字母 "W"
- 预示趋势反转（下跌 → 上涨）

---

## 📊 策略原理

### 1. 布林带计算

```python
def bollinger_bands(df):
    # 标准差（20日）
    data['std'] = data['price'].rolling(window=20).std()
    
    # 中轨（20日均线）
    data['mid band'] = data['price'].rolling(window=20).mean()
    
    # 上轨（+2σ）
    data['upper band'] = data['mid band'] + 2 * data['std']
    
    # 下轨（-2σ）
    data['lower band'] = data['mid band'] - 2 * data['std']
    
    return data
```

---

### 2. W 底形态识别

**五个节点**：
```
l (左肩)     i (右肩)
  \         /
   k (左底) - j (顶部) - m (右底)
```

**四个条件**：
1. **条件 1**：左底（k）触及下轨
2. **条件 2**：顶部（j）接近中轨
3. **条件 3**：右底（m）触及下轨且高于左底（k）
4. **条件 4**：右肩（i）突破上轨

---

### 3. 信号生成算法

```python
def signal_generation(data, method):
    # 参数
    period = 75  # 3个月窗口
    alpha = 0.0001  # 价格与布林带的容差
    beta = 0.0001  # 带宽阈值
    
    for i in range(period, len(df)):
        # 条件 4：右肩突破上轨
        if (df['price'][i] > df['upper band'][i]) and (df['cumsum'][i] == 0):
            
            # 条件 2：找到顶部 j（接近中轨）
            for j in range(i, i-period, -1):
                if (abs(df['mid band'][j] - df['price'][j]) < alpha) and \
                   (abs(df['mid band'][j] - df['upper band'][i]) < alpha):
                    break
            
            # 条件 1：找到左底 k（触及下轨）
            for k in range(j, i-period, -1):
                if abs(df['lower band'][k] - df['price'][k]) < alpha:
                    threshold = df['price'][k]  # 记录左底价格
                    break
            
            # 找到左肩 l（用于画图）
            for l in range(k, i-period, -1):
                if df['mid band'][l] < df['price'][l]:
                    break
            
            # 条件 3：找到右底 m（触及下轨且高于左底）
            for m in range(i, j, -1):
                if (df['price'][m] - df['lower band'][m] < alpha) and \
                   (df['price'][m] > df['lower band'][m]) and \
                   (df['price'][m] < threshold):  # 高于左底
                    df.at[i, 'signals'] = 1  # 做多信号
                    break
        
        # 清仓条件：布林带收缩（带宽 < beta）
        if (df['cumsum'][i] != 0) and (df['std'][i] < beta):
            df.at[i, 'signals'] = -1  # 清仓信号
```

---

## 💡 策略逻辑

### 为什么 W 底有效？

**市场心理学**：
1. **左底（k）**：第一次探底，恐慌抛售
2. **顶部（j）**：反弹，但动能不足
3. **右底（m）**：第二次探底，但买盘更强（高于左底）
4. **右肩（i）**：突破确认，趋势反转

**关键点**：
- 右底高于左底 → 买盘力量增强
- 突破上轨 → 趋势确认

---

### 为什么用算术方法？

**作者观点**：
> "为什么要用机器学习？算术方法更快更简单！"

**优势**：
- ✅ 计算速度快
- ✅ 逻辑清晰
- ✅ 不需要训练数据
- ✅ 可解释性强

---

## 🔍 量价分析应用

### 结合成交量

**1. 成交量确认**
```python
# 在右底（m）时，检查成交量
if (price[m] touches lower band) and \
   (volume[m] > avg_volume * 1.5):
    # 成交量放大，确认底部
    signal_strength = 2
```

**2. OBV 验证**
```python
# 检查 OBV 是否与价格背离
if (price makes lower low) and (OBV makes higher low):
    # 底背离，强烈买入信号
    signal_strength = 3
```

**3. 带宽收缩**
```python
# 布林带收缩 → 波动率降低 → 大行情前兆
if bandwidth < beta:
    # 准备突破
    watch_for_breakout()
```

---

## ⚠️ 重要注意事项

### 1. 参数调优

**alpha（容差）**：
- 太小 → 信号太少
- 太大 → 假信号多

**beta（带宽）**：
- 太小 → 无法识别收缩
- 太大 → 过早清仓

**period（窗口）**：
- 75天（3个月）是经验值
- 可根据市场调整

---

### 2. 假突破

**风险**：
- 右肩（i）可能假突破
- 随后回落

**应对**：
- 设置止损
- 等待确认（连续2天突破）
- 结合成交量验证

---

### 3. 市场环境

**适合**：
- 震荡市场
- 明显支撑位

**不适合**：
- 单边趋势
- 高波动市场

---

## 📈 实战案例

### 三一重工 W 底识别

**步骤**：
1. 获取历史数据（75天）
2. 计算布林带
3. 识别 W 底形态
4. 等待突破上轨
5. 成交量确认
6. 执行交易

**代码示例**：
```python
# 获取数据
df = yf.download('sh600031.SS', period='6mo')

# 计算布林带
df = bollinger_bands(df)

# 识别 W 底
signals = signal_generation(df, bollinger_bands)

# 执行交易
if signals['signals'].iloc[-1] == 1:
    print("W 底确认，买入信号")
```

---

## 💻 完整代码流程

```python
# 1. 计算布林带
def bollinger_bands(df):
    df['std'] = df['price'].rolling(20).std()
    df['mid'] = df['price'].rolling(20).mean()
    df['upper'] = df['mid'] + 2 * df['std']
    df['lower'] = df['mid'] - 2 * df['std']
    return df

# 2. 识别 W 底
def detect_w_bottom(df, period=75, alpha=0.0001, beta=0.0001):
    for i in range(period, len(df)):
        # 条件 4：突破上轨
        if df['price'][i] > df['upper'][i]:
            # 条件 2：找到顶部
            j = find_top(df, i, period, alpha)
            # 条件 1：找到左底
            k = find_left_bottom(df, j, period, alpha)
            # 条件 3：找到右底
            m = find_right_bottom(df, i, j, alpha, df['price'][k])
            if m:
                return 'W bottom detected at', i
    return 'No W bottom'

# 3. 生成信号
def generate_signals(df):
    signals = signal_generation(df, bollinger_bands)
    return signals
```

---

## 🎯 学习总结

### 核心要点

1. **布林带基础**
   - 中轨 = 20日均线
   - 上下轨 = ±2σ

2. **W 底识别**
   - 5个节点（l, k, j, m, i）
   - 4个条件
   - 右底高于左底

3. **算术方法**
   - 不用机器学习
   - 逻辑清晰
   - 计算快速

4. **成交量确认**
   - 结合 OBV
   - 成交量放大
   - 趋势确认

---

### 优缺点

**优点**：
- ✅ 形态识别准确
- ✅ 算术方法快速
- ✅ 可视化清晰
- ✅ 适合震荡市场

**缺点**：
- ❌ 参数敏感
- ❌ 假突破风险
- ❌ 不适合单边趋势
- ❌ 需要人工调参

---

### 与其他指标结合

**1. RSI**
```python
# W 底 + RSI 超卖
if (w_bottom_detected) and (RSI < 30):
    signal_strength *= 2
```

**2. MACD**
```python
# W 底 + MACD 金叉
if (w_bottom_detected) and (MACD_golden_cross):
    execute_trade()
```

**3. 成交量**
```python
# W 底 + 成交量放大
if (w_bottom_detected) and (volume > avg_volume * 1.5):
    strong_buy_signal()
```

---

## 📚 延伸阅读

### 经典资源

**1. TradingView Wiki**
- Bollinger Bands 详细说明
- W 底形态规则
- 实战案例

**2. Investopedia**
- Double Bottom Pattern
- Bollinger Bands Strategy

**3. 书籍**
- "Bollinger on Bollinger Bands" - John Bollinger
- 《布林带交易策略》

---

## 📝 下一步

1. ✅ 理解 W 底形态
2. ⏳ 在三一重工上识别 W 底
3. ⏳ 结合成交量验证
4. ⏳ 回测验证
5. ⏳ 实盘测试

---

_学习笔记创建时间：2026-03-12 21:25 UTC_
