# 量化项目学习笔记

> 学习时间：2026-03-12 22:00 UTC
> 来源：GitHub - je-suis-tm/quant-trading
> 项目：Monte Carlo, Oil Money, Smart Farmers

---

## 🎯 项目 1：Monte Carlo Simulation（蒙特卡洛模拟）

### 核心概念

**蒙特卡洛模拟**：
- 用随机数模拟股价未来走势
- 基于几何布朗运动（GBM）
- 预测股价分布

### 作者观点

> "行业内每个人都开玩笑说用蒙特卡洛，但没人真正用它"

**问题**：
- 基于历史数据预测未来
- 无法预测从未发生的事件（黑天鹅）
- 2008年金融危机、2018年VIX飙升都未预测到

---

### 核心算法

**几何布朗运动（GBM）**：
```python
# 股价预测
S[t+1] = S[t] * exp((μ - 0.5*σ²)*dt + σ*√dt*ε)

# μ: 平均收益率
# σ: 波动率
# ε: 标准正态随机数
```

---

### 实现步骤

1. **计算历史收益率**
```python
returns = df['Close'].pct_change()
mu = returns.mean()
sigma = returns.std()
```

2. **生成随机路径**
```python
def monte_carlo_simulation(S0, mu, sigma, T, N):
    dt = T/N
    prices = [S0]
    for _ in range(N):
        epsilon = np.random.normal(0, 1)
        S_next = prices[-1] * np.exp((mu - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*epsilon)
        prices.append(S_next)
    return prices
```

3. **多次模拟**
```python
# 运行 1000 次模拟
simulations = []
for _ in range(1000):
    path = monte_carlo_simulation(S0, mu, sigma, T, N)
    simulations.append(path)
```

---

### 应用场景

**1. 期权定价**
- Black-Scholes 模型
- 路径依赖期权

**2. 风险管理**
- VaR（Value at Risk）
- 压力测试

**3. 价格预测**
- 未来股价分布
- 置信区间

---

### 局限性

**1. 依赖历史数据**
- 无法预测黑天鹅
- 过去不代表未来

**2. 假设正态分布**
- 实际收益率有肥尾
- 极端事件概率被低估

**3. 参数敏感**
- μ 和 σ 估计误差
- 影响预测准确性

---

## 🎯 项目 2：Oil Money Project（石油货币项目）

### 核心概念

**石油货币套利**：
- 挪威克朗（NOK）与布伦特原油的关系
- 石油出口国货币与油价的相关性
- 统计套利机会

### 交易逻辑

**1. 回归模型**
```python
# NOK vs Brent Crude Oil
NOK = α + β*Brent + ε

# 如果 R² > 0.7，模型有效
if r_squared > 0.7:
    model_valid = True
```

**2. 信号生成**
```python
# 计算残差
residual = NOK - (α + β*Brent)

# 标准化残差
z_score = (residual - mean) / std

# 信号
if z_score > 2:  # +2σ
    # NOK 高估，做空 NOK
    signal = -1
elif z_score < -2:  # -2σ
    # NOK 低估，做多 NOK
    signal = 1
```

---

### 风险管理

**1. 持仓时间限制**
```python
# 最多持仓 10 天
if holding_days > 10:
    clear_positions()
```

**2. 止损/止盈**
```python
# 止损/止盈：0.5 点
stop_limit = 0.5

if abs(current_price - entry_price) > stop_limit:
    clear_positions()
```

**3. 模型有效性检验**
```python
# 每次交易前重新检验 R²
if r_squared < 0.7:
    # 模型失效，停止交易
    stop_trading()
```

---

### 石油货币清单

**主要石油出口国货币**：
1. **NOK（挪威克朗）** - 布伦特原油
2. **CAD（加拿大元）** - WTI 原油
3. **RUB（俄罗斯卢布）** - 乌拉尔原油
4. **COP（哥伦比亚比索）** - 原油出口

---

### 交易流程

```python
def oil_money_trading():
    # 1. 获取数据
    nok = get_data('NOK')
    brent = get_data('Brent')
    
    # 2. 回归分析
    model = OLS(nok, brent).fit()
    
    # 3. 检验有效性
    if model.rsquared > 0.7:
        # 4. 计算残差
        residual = nok - model.predict(brent)
        z_score = (residual - residual.mean()) / residual.std()
        
        # 5. 生成信号
        if z_score > 2:
            return 'short NOK'
        elif z_score < -2:
            return 'long NOK'
    
    return 'hold'
```

---

## 🎯 项目 3：Smart Farmers Project（智能农场项目）

### 核心概念

**农产品期货预测**：
- 天气数据分析
- 供需预测
- 季节性模式

### 数据来源

**1. 天气数据**
- 温度
- 降雨量
- 日照时长

**2. 农业数据**
- 种植面积
- 产量预测
- 库存数据

**3. 经济数据**
- 出口数据
- 价格指数
- 汇率

---

### 预测模型

**1. 需求预测**
```python
def estimate_demand():
    # 基于历史数据
    # 考虑季节性
    # 预测未来需求
```

**2. 供给预测**
```python
def estimate_supply():
    # 基于天气数据
    # 考虑种植面积
    # 预测产量
```

**3. 价格预测**
```python
def forecast_price():
    demand = estimate_demand()
    supply = estimate_supply()
    
    # 供需平衡
    balance = supply - demand
    
    # 价格预测
    price_forecast = current_price * (1 + balance_coefficient * balance)
    
    return price_forecast
```

---

## 💡 核心心得

### 1. 蒙特卡洛的局限性

> "用过去预测未来，就像麻瓜试图理解魔法世界"

**教训**：
- 无法预测黑天鹅
- 历史数据不足
- 需要结合其他方法

---

### 2. 统计套利的本质

**核心**：
- 相关性 ≠ 因果性
- 相关关系会破裂
- 需要持续检验

**案例**：
- NVIDIA 和 AMD 的协整关系破裂
- 石油和货币的相关性变化

---

### 3. 基本面分析的重要性

**Smart Farmers 项目启示**：
- 天气影响产量
- 供需决定价格
- 季节性模式可预测

---

## 📊 项目对比

| 项目 | 核心方法 | 数据需求 | 难度 | 实用性 |
|------|---------|---------|------|--------|
| Monte Carlo | 随机模拟 | 历史价格 | ⭐⭐ | ⭐⭐ |
| Oil Money | 统计套利 | 汇率+商品 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Smart Farmers | 基本面分析 | 多源数据 | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🎯 实战应用

### 1. Monte Carlo

**适用场景**：
- 期权定价
- 风险管理
- 压力测试

**不适用**：
- 股价预测（黑天鹅风险）
- 长期投资决策

---

### 2. Oil Money

**适用场景**：
- 外汇市场
- 商品货币
- 统计套利

**注意事项**：
- 持续检验相关性
- 设置止损
- 控制持仓时间

---

### 3. Smart Farmers

**适用场景**：
- 农产品期货
- 长线投资
- 季节性交易

**数据需求**：
- 天气数据
- 农业数据
- 经济数据

---

## 📚 延伸阅读

### Monte Carlo

**1. Wikipedia**
- Monte Carlo method
- Geometric Brownian Motion

**2. Books**
- "Options, Futures, and Other Derivatives" - John Hull

---

### Oil Money

**1. Research Papers**
- "Oil Prices and Exchange Rates"
- "Commodity Currencies"

**2. Data Sources**
- Bloomberg
- Quandl
- FRED

---

### Smart Farmers

**1. Data Sources**
- NOAA（天气数据）
- USDA（农业数据）
- FAO（粮食组织）

**2. Books**
- "Agricultural Finance"
- "Commodity Trading"

---

## 📝 下一步

1. ✅ 理解三个量化项目
2. ⏳ 选择一个项目深入研究
3. ⏳ 获取必要数据
4. ⏳ 实现并回测
5. ⏳ 实盘测试

---

_学习笔记创建时间：2026-03-12 22:00 UTC_
