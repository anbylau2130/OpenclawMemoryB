# 量化因子策略完整指南

> **学习时间：** 2026-03-16
> **状态：** 学习中
> **来源：** 综合资料整理

---

## 一、什么是因子投资（Factor Investing）

### 1.1 核心概念

**因子（Factor）**：能够解释股票收益差异的共同特征或驱动因素。

**因子投资**：通过识别和系统性地暴露于这些因子，获得长期超额收益。

**核心理念**：
- 股票收益不是随机的
- 某些特征（因子）能够持续预测未来收益
- 通过多因子组合，可以分散风险、提高收益

---

### 1.2 发展历史

| 年份 | 里程碑 | 贡献者 |
|------|--------|--------|
| 1964 | CAPM 单因子模型 | Sharpe, Lintner |
| 1992 | Fama-French 三因子模型 | Eugene Fama, Kenneth French |
| 2015 | Fama-French 五因子模型 | Fama, French |
| 1990s | Barra 风险模型 | MSCI Barra |
| 2000s | AQR 因子研究 | Cliff Asness |
| 2010s | 智能贝塔（Smart Beta）ETF 兴起 | 各大资管公司 |

---

## 二、六大核心因子

### 2.1 价值因子（Value）

**定义**：买入便宜股票，卖出昂贵股票。

**衡量指标**：
- **P/B（市净率）**：股价 / 每股净资产
- **P/E（市盈率）**：股价 / 每股收益
- **P/CF（市现率）**：股价 / 每股现金流
- **EV/EBITDA**：企业价值 / 息税折旧摊销前利润
- **股息率**：每股股息 / 股价

**计算示例**：
```python
def value_factor_score(stock):
    """价值因子评分（越低越好）"""
    pb = stock.price / stock.book_value_per_share
    pe = stock.price / stock.eps
    dividend_yield = stock.dividend_per_share / stock.price
    
    # 综合评分（PB和PE越低越好，股息率越高越好）
    score = (zscore(pb) + zscore(pe) - zscore(dividend_yield)) / 3
    return score
```

**历史收益**：年化 3-5% 超额收益（长期）

**适用市场**：
- ✅ 成熟市场（美国、欧洲）
- ✅ 新兴市场（中国、印度）
- ⚠️ 短期可能失效（2010-2020 价值股表现不佳）

---

### 2.2 动量因子（Momentum）

**定义**：买入过去表现好的股票，卖出过去表现差的股票。

**衡量指标**：
- **12-1 动量**：过去12个月收益（排除最近1个月）
- **相对强度**：相对于基准的超额收益
- **价格动量**：价格趋势强度

**计算示例**：
```python
def momentum_factor_score(stock, lookback=12, exclude_recent=1):
    """动量因子评分（越高越好）"""
    # 过去12个月收益（排除最近1个月，避免短期反转）
    returns = stock.returns[-lookback:-exclude_recent]
    cumulative_return = (1 + returns).prod() - 1
    return cumulative_return
```

**历史收益**：年化 4-8% 超额收益

**风险**：
- ⚠️ 动量崩溃（Momentum Crashes）：市场反转时大幅回撤
- ⚠️ 交易成本高（需要频繁调仓）

---

### 2.3 质量因子（Quality）

**定义**：买入财务稳健、盈利能力强的公司。

**衡量指标**：
- **ROE（净资产收益率）**：净利润 / 净资产
- **ROA（总资产收益率）**：净利润 / 总资产
- **毛利率**：（收入 - 成本）/ 收入
- **资产负债率**：总负债 / 总资产（越低越好）
- **盈利稳定性**：利润波动程度
- **现金流质量**：经营现金流 / 净利润

**计算示例**：
```python
def quality_factor_score(stock):
    """质量因子评分（越高越好）"""
    roe = stock.net_income / stock.equity
    roa = stock.net_income / stock.total_assets
    debt_ratio = stock.total_debt / stock.total_assets
    earnings_stability = 1 / stock.earnings_volatility
    
    # 综合评分
    score = (zscore(roe) + zscore(roa) + 
             zscore(1-debt_ratio) + zscore(earnings_stability)) / 4
    return score
```

**历史收益**：年化 2-4% 超额收益

**优势**：
- ✅ 低波动
- ✅ 下行保护（熊市表现更好）

---

### 2.4 规模因子（Size）

**定义**：小市值股票长期跑赢大市值股票。

**衡量指标**：
- **市值**：股价 × 总股本
- **流通市值**：股价 × 流通股本

**计算示例**：
```python
def size_factor_score(stock):
    """规模因子评分（越小越好）"""
    market_cap = stock.price * stock.shares_outstanding
    # 小市值得分高
    return -zscore(market_cap)
```

**历史收益**：年化 2-3% 超额收益

**争议**：
- ⚠️ 近年来效应减弱（美国市场）
- ⚠️ 可能是流动性溢价或风险溢价
- ✅ 新兴市场（中国）仍然有效

---

### 2.5 低波动因子（Low Volatility）

**定义**：低波动股票风险调整后收益更高（低波动异象）。

**衡量指标**：
- **历史波动率**：过去N天收益率标准差
- **Beta**：相对于市场的系统性风险
- **下行波动率**：负收益的标准差

**计算示例**：
```python
def low_vol_factor_score(stock, lookback=252):
    """低波动因子评分（越低越好）"""
    returns = stock.returns[-lookback:]
    volatility = returns.std() * np.sqrt(252)  # 年化波动率
    beta = stock.beta_to_market
    
    # 低波动得分高
    score = -(zscore(volatility) + zscore(beta)) / 2
    return score
```

**历史收益**：年化 2-4% 超额收益

**悖论**：
- 🤔 理论上高风险应该有高收益
- 💡 实际：杠杆限制导致低波动股票被低估

---

### 2.6 成长因子（Growth）

**定义**：买入增长速度快的企业。

**衡量指标**：
- **营收增长率**：同比营收增长
- **盈利增长率**：同比EPS增长
- **PEG**：市盈率 / 盈利增长率
- **投资率**：资本支出 / 资产

**计算示例**：
```python
def growth_factor_score(stock):
    """成长因子评分（越高越好）"""
    revenue_growth = (stock.revenue - stock.revenue_last_year) / stock.revenue_last_year
    eps_growth = (stock.eps - stock.eps_last_year) / stock.eps_last_year
    
    score = (zscore(revenue_growth) + zscore(eps_growth)) / 2
    return score
```

**历史收益**：波动较大，牛市表现优异

---

## 三、多因子模型

### 3.1 Fama-French 三因子模型

**公式**：
```
Ri - Rf = α + βm(Rm - Rf) + βs*SMB + βv*HML + ε
```

**三个因子**：
| 因子 | 含义 | 计算方法 |
|------|------|---------|
| **市场因子（Rm - Rf）** | 市场风险溢价 | 市场收益 - 无风险利率 |
| **规模因子（SMB）** | Small Minus Big | 小盘股收益 - 大盘股收益 |
| **价值因子（HML）** | High Minus Low | 价值股收益 - 成长股收益 |

**应用**：
```python
def fama_french_3factor_regression(stock_returns, market_returns, smb, hml, rf):
    """Fama-French 三因子回归"""
    import statsmodels.api as sm
    
    excess_returns = stock_returns - rf
    X = sm.add_constant(np.column_stack([market_returns - rf, smb, hml]))
    model = sm.OLS(excess_returns, X).fit()
    
    return {
        'alpha': model.params[0],      # 超额收益
        'beta_market': model.params[1], # 市场暴露
        'beta_size': model.params[2],   # 规模暴露
        'beta_value': model.params[3],  # 价值暴露
        'r_squared': model.rsquared
    }
```

---

### 3.2 Fama-French 五因子模型

**在三因子基础上增加**：
| 因子 | 含义 | 计算方法 |
|------|------|---------|
| **盈利因子（RMW）** | Robust Minus Weak | 高盈利 - 低盈利 |
| **投资因子（CMA）** | Conservative Minus Aggressive | 低投资 - 高投资 |

**公式**：
```
Ri - Rf = α + βm(Rm-Rf) + βs*SMB + βv*HML + βr*RMW + βc*CMA + ε
```

---

### 3.3 Barra 风险模型

**MSCI Barra 模型**：业界标准的多因子风险模型

**10 大类因子**：
1. **波动率（Volatility）**
2. **动量（Momentum）**
3. **规模（Size）**
4. **规模非线性（Size Non-Linearity）**
5. **交易活动（Trading Activity）**
6. **账面市值比（Book-to-Price）**
7. **盈利收益率（Earnings Yield）**
8. **盈利变动（Earnings Variability）**
9. **杠杆（Leverage）**
10. **货币敏感度（Currency Sensitivity）**

**应用**：
```python
def barra_factor_exposure(stock):
    """计算 Barra 因子暴露"""
    factors = {
        'volatility': calculate_volatility_factor(stock),
        'momentum': calculate_momentum_factor(stock),
        'size': calculate_size_factor(stock),
        'book_to_price': calculate_btp_factor(stock),
        'earnings_yield': calculate_ep_factor(stock),
        'leverage': calculate_leverage_factor(stock)
    }
    return factors
```

---

## 四、因子组合构建

### 4.1 因子打分法

**步骤**：
1. 计算每个股票的各因子得分
2. 标准化处理（Z-Score）
3. 加权合成综合得分
4. 按综合得分排序选股

**示例代码**：
```python
def build_multifactor_portfolio(stocks, factor_weights):
    """多因子组合构建"""
    
    # 1. 计算各因子得分
    factor_scores = {}
    for factor_name in factor_weights.keys():
        factor_scores[factor_name] = [
            calculate_factor_score(stock, factor_name) 
            for stock in stocks
        ]
    
    # 2. 标准化
    for factor_name in factor_scores:
        scores = factor_scores[factor_name]
        mean, std = np.mean(scores), np.std(scores)
        factor_scores[factor_name] = [(s - mean) / std for s in scores]
    
    # 3. 加权合成
    composite_scores = []
    for i, stock in enumerate(stocks):
        score = sum(
            factor_scores[factor_name][i] * weight
            for factor_name, weight in factor_weights.items()
        )
        composite_scores.append((stock, score))
    
    # 4. 排序选股
    composite_scores.sort(key=lambda x: x[1], reverse=True)
    selected_stocks = [s for s, score in composite_scores[:50]]  # 选前50只
    
    return selected_stocks

# 因子权重配置
factor_weights = {
    'value': 0.25,
    'momentum': 0.20,
    'quality': 0.25,
    'size': 0.15,
    'low_volatility': 0.15
}
```

---

### 4.2 因子权重确定

**方法**：

| 方法 | 优点 | 缺点 |
|------|------|------|
| **等权** | 简单 | 忽略因子质量差异 |
| **历史IC加权** | 基于预测能力 | 过拟合风险 |
| **最大化夏普比率** | 理论最优 | 对参数敏感 |
| **风险平价** | 风险均衡 | 不考虑收益 |
| **ICIR加权** | 考虑稳定性 | 需要足够历史数据 |

**IC（Information Coefficient）**：
```python
def calculate_ic(factor_scores, forward_returns):
    """计算因子IC值"""
    from scipy.stats import spearmanr
    ic, p_value = spearmanr(factor_scores, forward_returns)
    return ic

def calculate_icir(ic_series):
    """计算ICIR（IC的夏普比率）"""
    return ic_series.mean() / ic_series.std()
```

---

### 4.3 因子中性化

**目的**：消除行业、市值等风格暴露

**方法**：
```python
def neutralize_factor(factor_values, industry_dummies, market_caps):
    """因子中性化"""
    import statsmodels.api as sm
    
    # 回归残差即为中性化后的因子
    X = np.column_stack([industry_dummies, np.log(market_caps)])
    X = sm.add_constant(X)
    model = sm.OLS(factor_values, X).fit()
    neutralized_factor = model.resid
    
    return neutralized_factor
```

---

## 五、因子有效性检验

### 5.1 IC 分析

**IC（Information Coefficient）**：因子值与未来收益的相关系数

**判断标准**：
| IC 均值 | 因子质量 |
|---------|---------|
| > 0.05 | 优秀 |
| 0.03 - 0.05 | 良好 |
| 0.01 - 0.03 | 一般 |
| < 0.01 | 较差 |

**代码**：
```python
def analyze_factor_ic(factor_values, forward_returns, periods=252):
    """分析因子IC"""
    ic_series = []
    for i in range(periods):
        ic = spearmanr(factor_values[i], forward_returns[i])[0]
        ic_series.append(ic)
    
    return {
        'ic_mean': np.mean(ic_series),
        'ic_std': np.std(ic_series),
        'icir': np.mean(ic_series) / np.std(ic_series),
        'ic_positive_ratio': sum(ic > 0 for ic in ic_series) / len(ic_series)
    }
```

---

### 5.2 分组回测

**方法**：按因子值分10组，比较各组收益

```python
def quintile_backtest(factor_values, returns, n_groups=5):
    """分组回测"""
    # 按因子值分组
    quantiles = pd.qcut(factor_values, n_groups, labels=False)
    
    group_returns = []
    for q in range(n_groups):
        group_mask = (quantiles == q)
        group_return = returns[group_mask].mean()
        group_returns.append(group_return)
    
    # 多空组合收益（做多最好组，做空最差组）
    long_short_return = group_returns[-1] - group_returns[0]
    
    return {
        'group_returns': group_returns,
        'spread': long_short_return,
        'monotonicity': check_monotonicity(group_returns)
    }
```

---

### 5.3 因子衰减分析

**检验因子预测能力的持续性**

```python
def factor_decay_analysis(factor_values, returns, max_lag=20):
    """因子衰减分析"""
    ics = []
    for lag in range(1, max_lag + 1):
        # 计算lag期后的IC
        ic = spearmanr(factor_values[:-lag], returns[lag:])[0]
        ics.append(ic)
    
    return ics  # IC随时间衰减曲线
```

---

## 六、因子组合优化

### 6.1 均值方差优化

**目标**：最大化夏普比率

```python
def mean_variance_optimize(expected_returns, covariance_matrix, 
                          risk_free_rate=0.03):
    """均值方差优化"""
    from scipy.optimize import minimize
    
    n_assets = len(expected_returns)
    
    def neg_sharpe(weights):
        port_return = np.dot(weights, expected_returns)
        port_vol = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
        return -(port_return - risk_free_rate) / port_vol
    
    # 约束条件
    constraints = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # 权重和为1
    ]
    bounds = tuple((0, 0.1) for _ in range(n_assets))  # 单只股票不超过10%
    
    result = minimize(neg_sharpe, 
                     x0=np.ones(n_assets) / n_assets,
                     bounds=bounds,
                     constraints=constraints)
    
    return result.x
```

---

### 6.2 风险预算（Risk Budgeting）

**目标**：控制各因子风险贡献

```python
def risk_budget_optimize(factor_exposures, factor_cov_matrix, 
                        risk_budgets):
    """风险预算优化"""
    # 每个因子的边际风险贡献
    def risk_contribution(weights):
        port_vol = np.sqrt(weights.T @ factor_cov_matrix @ weights)
        mrc = factor_cov_matrix @ weights / port_vol
        rc = weights * mrc / port_vol
        return rc
    
    # 优化使风险贡献接近预算
    def objective(weights):
        rc = risk_contribution(weights)
        return np.sum((rc - risk_budgets) ** 2)
    
    # 优化求解...
    return optimal_weights
```

---

## 七、实战配置建议

### 7.1 推荐因子组合

**稳健型（低风险）**：
- 价值 30% + 质量 30% + 低波动 40%

**成长型（高收益）**：
- 动量 35% + 成长 35% + 质量 30%

**均衡型（推荐）**：
- 价值 20% + 动量 20% + 质量 25% + 规模 15% + 低波动 20%

---

### 7.2 调仓频率

| 因子类型 | 建议调仓频率 |
|---------|-------------|
| 价值 | 月度/季度 |
| 动量 | 月度 |
| 质量 | 季度 |
| 规模 | 月度 |
| 低波动 | 月度/季度 |

---

### 7.3 风险控制

**关键指标**：
- **单因子暴露上限**：±2 标准差
- **行业偏离上限**：±10%
- **跟踪误差**：< 5%
- **最大回撤**：< 15%

---

## 八、A 股市场因子有效性

### 8.1 A 股因子表现（历史数据）

| 因子 | 年化超额收益 | IC 均值 | 近期趋势 |
|------|-------------|---------|---------|
| 价值 | 4-6% | 0.03-0.05 | ⚠️ 2020后弱化 |
| 动量 | 3-5% | 0.02-0.04 | ✅ 短周期有效 |
| 质量 | 3-5% | 0.03-0.04 | ✅ 持续有效 |
| 规模 | 5-8% | 0.04-0.06 | ✅ 小盘股溢价 |
| 低波动 | 2-4% | 0.02-0.03 | ✅ 有效 |
| 成长 | 波动大 | 0.01-0.03 | ⚠️ 牛市有效 |

---

### 8.2 A 股特色因子

**反转因子**：A股短期（1个月）反转效应显著

**北向资金因子**：跟踪外资流向

**分析师预期因子**：盈利预期修正

**技术因子**：成交量、换手率

---

## 九、学习资源

### 9.1 经典论文

1. Fama & French (1992) - "The Cross-Section of Expected Stock Returns"
2. Fama & French (2015) - "A Five-Factor Asset Pricing Model"
3. Asness et al. (2013) - "Value and Momentum Everywhere"
4. Novy-Marx (2013) - "The Other Side of Value"

### 9.2 书籍推荐

1. 《量化投资：以Python为工具》 - 蔡立耑
2. 《主动投资组合管理》 - Grinold & Kahn
3. 《Expected Returns》 - Antti Ilmanen
4. 《因子投资：方法与应用》 - 石川

### 9.3 数据源

- **因子数据**：Wind、东方财富、Tushare
- **财务数据**：财报、年报
- **行情数据**：日线、分钟线

---

## 十、下一步计划

- [ ] 实现 A 股因子计算模块
- [ ] 回测各因子在 A 股的有效性
- [ ] 构建多因子组合
- [ ] 对接 OpenClaw 自动化交易

---

**学习状态：** 📚 已完成理论学习，准备实战验证

**下次更新：** 实现因子计算代码后补充
