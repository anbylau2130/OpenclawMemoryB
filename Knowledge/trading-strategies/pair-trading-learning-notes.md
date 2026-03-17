# Pair Trading（配对交易）学习笔记

> 学习时间：2026-03-12 21:20 UTC
> 来源：je-suis-tm/quant-trading
> 文件：Pair trading backtest.py

---

## 🎯 核心概念

### 什么是配对交易？

配对交易（Pair Trading）是一种**统计套利**策略，基于以下假设：
- 两个**协整**的资产不会偏离太远
- 当一个资产过度上涨（或下跌）时，会回归到均值
- 通过做多低估资产、做空高估资产获利

### 形象比喻

> "就像一个醉汉牵着一只狗，看不见的狗绳会把两者保持在一定范围内"

---

## 📊 策略原理

### 1. 协整关系（Cointegration）

**定义**：
- 两个时间序列的线性组合是平稳的
- 即使单个序列不平稳，它们的组合可以平稳

**检验方法**：
- **Engle-Granger 两步法**（本代码使用）
- Johansen 检验（更常用）

---

### 2. Engle-Granger 两步法

**第一步**：估计长期均衡
```python
# Y = α + βX + ε
model1 = sm.OLS(Y, sm.add_constant(X)).fit()
epsilon = model1.resid  # 残差
```

**检验平稳性**：
```python
# ADF 检验（Augmented Dickey-Fuller）
# 如果 p-value <= 0.05，通过平稳性检验
if sm.tsa.stattools.adfuller(epsilon)[1] > 0.05:
    return False  # 不协整
```

**第二步**：误差修正模型
```python
# ΔY = α + βΔX + γ*ε_{t-1}
X_dif = pd.concat([X.diff(), epsilon.shift(1)], axis=1)
Y_dif = Y.diff()
model2 = sm.OLS(Y_dif, X_dif).fit()

# 调整系数必须为负
if model2.params[-1] > 0:
    return False  # 不协整
else:
    return True  # 协整
```

---

### 3. 信号生成

**标准化残差（Z-score）**：
```python
# 计算残差
fitted = model.predict(X)
residual = Y - fitted

# 标准化（白噪声 N(0,1)）
z = (residual - mean(residual)) / std(residual)
```

**交易信号**：
```python
# 阈值：1个标准差
z_upper = z + std(residual)
z_lower = z - std(residual)

# 信号生成
if z > z_upper:
    # Y 高估，X 低估
    signal_Y = -1  # 做空 Y
    signal_X = 1   # 做多 X
    
if z < z_lower:
    # Y 低估，X 高估
    signal_Y = 1   # 做多 Y
    signal_X = -1  # 做空 X
```

---

## 💻 完整策略流程

```python
def signal_generation(asset1, asset2, bandwidth=250):
    """
    asset1, asset2: 两个资产的历史数据
    bandwidth: 协整检验窗口（默认250天，约1年）
    """
    
    # 1. 滚动窗口检验协整关系
    for i in range(bandwidth, len(data)):
        
        # 检验协整
        coint_status, model = EG_method(
            asset1[i-bandwidth:i],
            asset2[i-bandwidth:i]
        )
        
        # 2. 如果协整关系破裂，清仓
        if prev_status and not coint_status:
            signals['asset1'] = 0
            signals['asset2'] = 0
            
        # 3. 如果协整关系成立，设置阈值
        if not prev_status and coint_status:
            # 预测价格
            fitted = model.predict(asset1[i:])
            residual = asset2[i:] - fitted
            
            # 标准化
            z = (residual - mean(residual)) / std(residual)
            
            # 阈值（1个标准差）
            z_upper = z + std(residual)
            z_lower = z - std(residual)
        
        # 4. 生成交易信号
        if coint_status and z > z_upper:
            signals['asset1'] = 1   # 做多 asset1
            signals['asset2'] = -1  # 做空 asset2
            
        if coint_status and z < z_lower:
            signals['asset1'] = -1  # 做空 asset1
            signals['asset2'] = 1   # 做多 asset2
```

---

## ⚠️ 重要注意事项

### 1. 协整关系可能破裂

**案例**：NVIDIA 和 AMD
- 两个 GPU 公司，历史上协整
- 比特币挖矿和 AI 热潮后
- NVIDIA 股价暴涨，AMD 变化不大
- 协整关系完全破裂

**教训**：
> "协整关系不是永久的，市场条件是动态的"

---

### 2. 持续检验

**最佳实践**：
- 每次交易前重新检验协整关系
- 设置窗口大小（默认250天）
- 如果协整关系破裂，立即清仓

---

### 3. 风险管理

**风险点**：
- 协整关系突然破裂
- 两个资产同时下跌
- 流动性风险（做空可能受限）

**建议**：
- 设置止损
- 分散投资多对资产
- 定期重新检验协整关系

---

## 🔍 量价分析应用

### 如何结合量价分析？

**1. 成交量确认**
```python
# 当 z > z_upper 时（做空信号）
# 确认成交量是否放大
if z > z_upper and volume > avg_volume * 1.5:
    # 成交量放大，确认信号
    execute_trade()
```

**2. OBV 验证**
```python
# 检查 OBV 是否与价格背离
if z > z_upper and obv < obv_ma:
    # 价格高估 + OBV 下降 = 强烈做空信号
    signal_strength = 2
```

**3. 趋势过滤**
```python
# 只在趋势不明确时使用配对交易
if not is_trending_market():
    apply_pair_trading()
```

---

## 📈 实战案例

### 三一重工配对交易

**潜在配对**：
- 三一重工 + 徐工机械（同行业）
- 三一重工 + 工程机械ETF
- 三一重工 + 中联重科

**步骤**：
1. 获取历史数据（250天）
2. 检验协整关系
3. 如果协整，设置阈值
4. 等待信号触发
5. 执行交易（对冲）

---

## 💡 关键代码片段

### 协整检验

```python
import statsmodels.api as sm

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
    
    # 调整系数必须为负
    if model2.params[-1] > 0:
        return False, model1
    else:
        return True, model1
```

---

### 信号生成

```python
def generate_signals(asset1, asset2, bandwidth=250):
    for i in range(bandwidth, len(data)):
        # 检验协整
        coint_status, model = EG_method(
            asset1[i-bandwidth:i],
            asset2[i-bandwidth:i]
        )
        
        if coint_status:
            # 计算残差
            fitted = model.predict(asset1[i:])
            residual = asset2[i:] - fitted
            
            # 标准化
            z = (residual - residual.mean()) / residual.std()
            
            # 信号
            if z > 1:
                return ('long asset1', 'short asset2')
            elif z < -1:
                return ('short asset1', 'long asset2')
    
    return ('hold', 'hold')
```

---

## 📚 延伸阅读

### 学术资源

**1. Engle-Granger 两步法**
- Engle, R. F., & Granger, C. W. (1987)
- "Co-integration and error correction"
- 诺贝尔经济学奖成果

**2. Johansen 检验**
- Johansen, S. (1988)
- "Statistical analysis of cointegration vectors"
- 更常用的方法

---

### 实战资源

**1. Python 库**
```bash
pip install statsmodels
pip install yfinance
```

**2. 数据源**
- Yahoo Finance（免费）
- Bloomberg（付费）
- Wind（中国A股）

---

## 🎯 学习总结

### 核心要点

1. **协整关系是核心**
   - 不是相关性，是长期均衡关系
   - 可以用 Engle-Granger 或 Johansen 检验

2. **均值回归是原理**
   - 当偏离太远时，会回归
   - Z-score > 1 是标准阈值

3. **动态检验是关键**
   - 协整关系会破裂
   - 每次交易前重新检验

4. **对冲是手段**
   - 做多一个，做空另一个
   - 市场中性策略

---

### 优缺点

**优点**：
- ✅ 市场中性（不依赖大盘方向）
- ✅ 统计基础扎实
- ✅ 风险可控（对冲）

**缺点**：
- ❌ 协整关系可能破裂
- ❌ 做空可能受限（A股）
- ❌ 需要持续监控

---

### 适用场景

**适合**：
- 两个高度相关的股票（同行业）
- 股票和ETF
- 期货套利

**不适合**：
- 单边趋势市场
- 协整关系已破裂
- 流动性差的资产

---

## 📝 下一步

1. ✅ 理解协整关系
2. ⏳ 在三一重工上寻找配对
3. ⏳ 回测验证
4. ⏳ 实盘小仓位测试

---

_学习笔记创建时间：2026-03-12 21:20 UTC_
