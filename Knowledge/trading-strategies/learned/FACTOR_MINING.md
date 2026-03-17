# 因子挖掘方法指南

> 来源：OpenclawMemery 仓库
> 日期：2026-03-17

---

## 📊 一、因子分类

### 1. 动量因子
```python
# 价格动量
def price_momentum(df, period=20):
    """价格动量因子"""
    momentum = df['close'] / df['close'].shift(period) - 1
    return momentum

# 时间序列动量
def time_series_momentum(df, lookback=12, holding=1):
    """时间序列动量"""
    returns = df['close'].pct_change(lookback)
    signal = np.sign(returns)
    return signal.shift(holding)

# 横截面动量
def cross_sectional_momentum(df_all, period=20):
    """横截面动量（多股票）"""
    momentum = {}
    for symbol, df in df_all.items():
        momentum[symbol] = df['close'].iloc[-1] / df['close'].iloc[-period] - 1

    # 排名
    ranked = pd.Series(momentum).rank()
    return ranked
```

### 2. 价值因子
```python
# 市盈率因子
def pe_factor(pe_ratio):
    """市盈率因子"""
    return 1 / pe_ratio  # 低PE更优

# 市净率因子
def pb_factor(pb_ratio):
    """市净率因子"""
    return 1 / pb_ratio  # 低PB更优

# 股息率因子
def dividend_yield_factor(div_yield):
    """股息率因子"""
    return div_yield  # 高股息率更优
```

### 3. 质量因子
```python
# ROE因子
def roe_factor(roe):
    """ROE因子"""
    return roe  # 高ROE更优

# 资产负债率因子
def debt_ratio_factor(debt_ratio):
    """资产负债率因子"""
    return 1 / debt_ratio  # 低负债更优

# 毛利率因子
def gross_margin_factor(gross_margin):
    """毛利率因子"""
    return gross_margin  # 高毛利率更优
```

### 4. 波动率因子
```python
# 历史波动率
def volatility_factor(df, period=20):
    """历史波动率因子"""
    returns = df['close'].pct_change()
    volatility = returns.rolling(period).std() * np.sqrt(252)
    return -volatility  # 低波动更优

# ATR因子
def atr_factor(df, period=14):
    """ATR因子"""
    atr = calculate_atr(df, period)
    return -atr / df['close']  # 低ATR比例更优
```

### 5. 成交量因子
```python
# 成交量动量
def volume_momentum_factor(df, period=20):
    """成交量动量因子"""
    vol_ma = df['volume'].rolling(period).mean()
    vol_ratio = df['volume'] / vol_ma
    return vol_ratio

# 换手率因子
def turnover_rate_factor(turnover_rate):
    """换手率因子"""
    return -turnover_rate  # 低换手更优（长期持有）
```

---

## 🔍 二、因子挖掘方法

### 1. 基于遗传规划（GP）

```python
from gplearn.genetic import SymbolicTransformer

def genetic_programming_factor(df):
    """遗传规划挖掘因子"""

    # 准备数据
    X = df[['open', 'high', 'low', 'close', 'volume']].values
    y = df['close'].shift(-5) / df['close'] - 1  # 未来5日收益

    # 遗传规划
    gp = SymbolicTransformer(
        generations=20,
        population_size=1000,
        hall_of_fame=100,
        n_components=10,
        function_set=['add', 'sub', 'mul', 'div', 'sqrt', 'log'],
        parsimony_coefficient=0.0005,
        max_samples=0.9,
        verbose=1
    )

    gp.fit(X[:-5], y[:-5].dropna())

    # 输出最佳因子
    print("发现的因子：")
    for i, program in enumerate(gp):
        print(f"因子 {i+1}: {program}")

    return gp
```

### 2. 基于机器学习

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_classif

def ml_factor_selection(df, n_factors=20):
    """机器学习因子选择"""

    # 生成候选因子
    factors = pd.DataFrame()
    factors['momentum_5'] = price_momentum(df, 5)
    factors['momentum_10'] = price_momentum(df, 10)
    factors['momentum_20'] = price_momentum(df, 20)
    factors['volatility'] = volatility_factor(df, 20)
    factors['volume_ratio'] = volume_momentum_factor(df, 20)
    factors['rsi'] = calculate_rsi(df['close'])
    factors['macd'] = calculate_macd(df['close'])[0]
    # ... 添加更多因子

    # 目标：未来收益
    y = (df['close'].shift(-5) / df['close'] - 1 > 0).astype(int)

    # 特征选择
    selector = SelectKBest(f_classif, k=n_factors)
    X_selected = selector.fit_transform(factors.fillna(0), y)

    # 显示最佳因子
    selected_indices = selector.get_support(indices=True)
    print("最佳因子：")
    for idx in selected_indices:
        print(f"  {factors.columns[idx]}: {selector.scores_[idx]:.2f}")

    return factors.columns[selected_indices]
```

### 3. 基于统计检验

```python
from scipy import stats

def ic_test(factor_values, returns):
    """IC（信息系数）检验"""

    # Spearman相关系数
    ic, p_value = stats.spearmanr(factor_values, returns)

    return {
        'IC': ic,
        'p_value': p_value,
        'significant': p_value < 0.05
    }

def factor_effectiveness_test(df, factor_func):
    """因子有效性检验"""

    # 计算因子值
    factor = factor_func(df)

    # 计算未来收益
    forward_returns = df['close'].shift(-5) / df['close'] - 1

    # IC检验
    ic_results = []
    for i in range(len(df) - 5):
        ic = stats.spearmanr(factor.iloc[i:i+50], forward_returns.iloc[i:i+50])[0]
        ic_results.append(ic)

    # 统计
    mean_ic = np.mean(ic_results)
    icir = mean_ic / np.std(ic_results)

    print(f"平均IC: {mean_ic:.4f}")
    print(f"ICIR: {icir:.4f}")
    print(f"IC > 0比例: {sum(ic > 0 for ic in ic_results) / len(ic_results):.2%}")

    return {
        'mean_IC': mean_ic,
        'ICIR': icir,
        'positive_ratio': sum(ic > 0 for ic in ic_results) / len(ic_results)
    }
```

---

## 📈 三、因子组合

### 1. 等权组合

```python
def equal_weight_combination(factors_dict):
    """等权因子组合"""
    factor_df = pd.DataFrame(factors_dict)
    combined = factor_df.mean(axis=1)
    return combined
```

### 2. IC加权

```python
def ic_weighted_combination(factors_dict, ic_values):
    """IC加权因子组合"""
    
    # 归一化IC
    ic_weights = pd.Series(ic_values)
    ic_weights = ic_weights / ic_weights.sum()
    
    # 加权组合
    combined = pd.DataFrame(factors_dict).mul(ic_weights, axis=1).sum(axis=1)
    
    return combined
```

### 3. 最大化ICIR

```python
from scipy.optimize import minimize

def maximize_icir(factors_dict, returns):
    """最大化ICIR组合"""

    factor_df = pd.DataFrame(factors_dict)
    n_factors = len(factors_dict)

    # 目标函数：最小化 -ICIR
    def objective(weights):
        combined = factor_df.mul(weights, axis=1).sum(axis=1)
        ic = stats.spearmanr(combined, returns)[0]
        icir = ic / np.std(combined)
        return -icir

    # 约束：权重和=1
    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
    
    # 边界：权重>=0
    bounds = tuple((0, 1) for _ in range(n_factors))

    # 优化
    result = minimize(
        objective,
        x0=np.ones(n_factors) / n_factors,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )

    optimal_weights = result.x
    return optimal_weights
```

---

## 💡 四、实战经验

### 1. V5系统因子选择

基于上证50回测结果：

| 因子 | 胜率 | 平均收益 | 权重 | 说明 |
|------|------|----------|------|------|
| VWAP | 92% | 37.6% | 3.0 | 成交量加权价 |
| 布林带 | 71% | 30.4% | 2.0 | 下轨反弹 |
| KDJ | 70% | 23.0% | 1.5 | 超买超卖 |
| RSI | 69% | 25.8% | 1.5 | 相对强弱 |

### 2. 因子筛选标准

**保留因子：**
- 胜率 > 60%
- 平均收益 > 20%
- IC > 0.05
- ICIR > 0.5

**移除因子：**
- 胜率 < 40%
- 严重亏损
- IC < 0
- 高度相关（相关系数>0.7）

### 3. 因子衰减

因子效果会随时间衰减，需要：
- 定期回测验证
- 动态调整权重
- 持续挖掘新因子

---

## 🔧 五、因子库维护

### 1. 定期更新

```bash
# 每周更新因子表现
cd /root/.openclaw/workspace/Knowledge/trading-strategies/code
python3 factor_calculator.py --update

# 每月重新挖掘因子
python3 factor_mining.py --auto
```

### 2. 因子监控

```python
def monitor_factors():
    """监控因子表现"""
    
    # 读取因子库
    factors = load_factor_library()
    
    # 检查因子衰减
    for factor in factors:
        current_ic = calculate_ic(factor)
        if current_ic < factor['historical_ic'] * 0.5:
            send_alert(f"因子{factor['name']}衰减，IC从{factor['historical_ic']:.2f}降至{current_ic:.2f}")
```

---

_来源：OpenclawMemery 仓库 main 分支_
_提取时间：2026-03-17_
