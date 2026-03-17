# Dual Thrust（双重推力突破策略）学习笔记

> 学习时间：2026-03-12 21:50 UTC
> 来源：je-suis-tm/quant-trading
> 文件：Dual Thrust backtest.py

---

## 🎯 核心概念

### 什么是 Dual Thrust？

**Dual Thrust（双重推力）**：
- 开盘区间突破策略
- 类似于 London Breakout
- 日内交易策略
- 基于历史波动率设定阈值

### 策略特点

- ✅ 日内交易（收盘平仓）
- ✅ 基于历史波动率
- ✅ 双向突破（做多/做空）
- ✅ 无止损（收盘平仓）

---

## 📊 计算公式

### 区间计算

```python
# 基于 N 天历史数据
range1 = high_rolling(N).max() - close_rolling(N).min()
range2 = close_rolling(N).max() - low_rolling(N).min()

# 取最大值
range = max(range1, range2)
```

---

### 阈值设定

```python
# 开盘时设定
upper_threshold = current_price + param * range
lower_threshold = current_price - (1 - param) * range

# param 通常为 0.5（50/50 机会）
```

---

## 📊 信号生成规则

### 基本规则

```python
def signal_generation(df, intraday, param, column, rg):
    signals = df.copy()
    signals['signals'] = 0
    signals['cumsum'] = 0
    signals['upper'] = 0.0
    signals['lower'] = 0.0
    
    sigup = 0.0
    siglo = 0.0
    
    for i in signals.index:
        date = '%s-%s-%s' % (i.year, i.month, i.day)
        
        # 开盘时设定阈值（3:00 AM）
        if (i.hour == 3 and i.minute == 0):
            sigup = float(param * intraday['range'][date] + signals[column][i])
            siglo = float(-(1-param) * intraday['range'][date] + signals[column][i])
        
        # 突破上阈值，做多
        if (sigup != 0 and signals[column][i] > sigup):
            signals.at[i, 'signals'] = 1
        
        # 突破下阈值，做空
        if (siglo != 0 and signals[column][i] < siglo):
            signals.at[i, 'signals'] = -1
        
        # 收盘时平仓（12:00 PM）
        if i.hour == 12 and i.minute == 0:
            sigup, siglo = 0.0, 0.0
            signals['cumsum'] = signals['signals'].cumsum()
            signals.at[i, 'signals'] = -signals['cumsum'][i:i]
        
        # 记录阈值
        signals.at[i, 'upper'] = sigup
        signals.at[i, 'lower'] = siglo
    
    return signals
```

---

### 信号解读

**做多信号**：
```python
# 价格突破上阈值
if price > upper_threshold:
    buy_signal()
```

**做空信号**：
```python
# 价格突破下阈值
if price < lower_threshold:
    sell_signal()
```

**平仓信号**：
```python
# 收盘时（12:00 PM）
if market_close:
    close_all_positions()
```

---

## 💡 策略逻辑

### 为什么有效？

**1. 波动率突破**
- 历史波动率 = 未来波动率的预测
- 突破阈值 = 趋势确认

**2. 日内交易**
- 无隔夜风险
- 资金利用率高
- 适合高频交易

**3. 双向机会**
- param = 0.5：50/50 机会
- 可做多也可做空
- 适应不同市场

---

### 参数选择

**rg（回看天数）**：
- 默认：5 天
- 建议：3-10 天
- 太短：噪音多
- 太长：反应慢

**param（阈值参数）**：
- 默认：0.5（50/50）
- 保守：0.3-0.4（更多做空机会）
- 激进：0.6-0.7（更多做多机会）

---

## 🔍 量价分析应用

### 结合成交量

**1. 成交量确认**
```python
# 突破 + 成交量放大
if (price > upper_threshold) and (volume > avg_volume * 1.5):
    confirmed_breakout()
```

**2. 成交量萎缩**
```python
# 突破 + 成交量萎缩 = 假突破
if (price > upper_threshold) and (volume < avg_volume * 0.5):
    false_breakout()
```

**3. OBV 验证**
```python
# 突破 + OBV 上升 = 真突破
if (price > upper_threshold) and (obv > obv_ma):
    strong_breakout()
```

---

## ⚠️ 重要注意事项

### 1. 日内交易风险

**问题**：
- 需要实时监控
- 滑点成本高
- 需要高频数据

**应对**：
- 使用自动化交易
- 设置滑点容忍度
- 选择流动性好的品种

---

### 2. 假突破

**问题**：
- 价格可能短暂突破后回落
- 假信号多

**应对**：
- 结合成交量确认
- 等待回踩确认
- 使用多个时间框架

---

### 3. 参数敏感性

**问题**：
- 不同参数表现差异大
- 需要针对不同市场优化

**应对**：
- 回测验证
- 参数优化
- 使用自适应参数

---

## 📈 实战案例

### 三一重工 Dual Thrust 策略

**步骤**：
1. 获取分钟级数据
2. 计算 5 天历史区间
3. 开盘时设定阈值
4. 等待突破
5. 执行交易
6. 收盘前平仓

**代码示例**：
```python
# 获取数据（分钟级）
df = get_minute_data('sh600031.SS', period='1mo')

# 计算日内数据
intraday = min2day(df, 'price', year, month, rg=5)

# 生成信号
signals = signal_generation(df, intraday, param=0.5, column='price', rg=5)

# 检查最新信号
if signals['signals'].iloc[-1] == 1:
    print("Dual Thrust 做多信号")
elif signals['signals'].iloc[-1] == -1:
    print("Dual Thrust 做空信号")
```

---

## 💻 完整代码流程

```python
# 1. 分钟转日数据
def min2day(df, column, year, month, rg):
    memo = {'date':[], 'open':[], 'close':[], 'high':[], 'low':[]}
    
    for i in range(1, 32):
        try:
            temp = df['%s-%s-%s 3:00:00'%(year,month,i):'%s-%s-%s 12:00:00'%(year,month,i)][column]
            memo['open'].append(temp[0])
            memo['close'].append(temp[-1])
            memo['high'].append(max(temp))
            memo['low'].append(min(temp))
            memo['date'].append('%s-%s-%s'%(year,month,i))
        except:
            pass
    
    intraday = pd.DataFrame(memo)
    intraday['range1'] = intraday['high'].rolling(rg).max() - intraday['close'].rolling(rg).min()
    intraday['range2'] = intraday['close'].rolling(rg).max() - intraday['low'].rolling(rg).min()
    intraday['range'] = np.where(intraday['range1'] > intraday['range2'], intraday['range1'], intraday['range2'])
    
    return intraday

# 2. 生成信号
def signal_generation(df, intraday, param, column, rg):
    # ... 信号生成逻辑
    return signals

# 3. 执行交易
def execute_trade(signals):
    if signals['signals'].iloc[-1] == 1:
        print("买入")
    elif signals['signals'].iloc[-1] == -1:
        print("卖出")
```

---

## 🎯 学习总结

### 核心要点

1. **Dual Thrust 基础**
   - 开盘区间突破
   - 基于历史波动率
   - 日内交易

2. **参数选择**
   - rg: 5 天（回看天数）
   - param: 0.5（阈值参数）

3. **信号规则**
   - 突破上阈值：做多
   - 突破下阈值：做空
   - 收盘：平仓

4. **结合成交量**
   - 成交量确认
   - 假突破识别
   - OBV 验证

---

### 优缺点

**优点**：
- ✅ 逻辑简单
- ✅ 无隔夜风险
- ✅ 双向机会
- ✅ 适合高频

**缺点**：
- ❌ 需要高频数据
- ❌ 假突破多
- ❌ 参数敏感
- ❌ 需要实时监控

---

### 与其他策略对比

| 策略 | 时间框架 | 交易方向 | 持仓时间 |
|------|---------|---------|---------|
| Dual Thrust | 日内 | 双向 | 几小时 |
| London Breakout | 日内 | 双向 | 几小时 |
| MACD | 日线 | 趋势 | 几天-几周 |
| Pair Trading | 日线 | 对冲 | 几天-几周 |

---

## 📚 延伸阅读

### 经典资源

**1. QuantConnect**
- Dual Thrust Trading Algorithm
- 详细说明和代码

**2. Investopedia**
- Opening Range Breakout
- Trading Strategy

**3. 相关策略**
- London Breakout
- Donchian Channel

---

## 📝 下一步

1. ✅ 理解 Dual Thrust 基础
2. ⏳ 获取分钟级数据
3. ⏳ 回测验证
4. ⏳ 优化参数
5. ⏳ 实盘测试

---

_学习笔记创建时间：2026-03-12 21:50 UTC_
