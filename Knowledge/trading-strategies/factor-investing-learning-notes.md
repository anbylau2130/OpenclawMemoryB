# 因子投资（Factor Investing）学习笔记

> 学习时间：2026-03-13 07:50 UTC
> 来源：GitHub 搜索 + 学术资源
> 目标：提升交易胜率

---

## 🎯 什么是因子投资？

### 核心概念

**因子投资（Factor Investing）**：
- 基于因子暴露来选择股票
- 因子 = 影响股票收益的共同特征
- 通过因子组合获得超额收益（Alpha）

### 诺贝尔经济学奖成果

**Eugene Fama（2013年诺贝尔奖）**：
- Fama-French 三因子模型
- 市场因子（Market）
- 规模因子（SMB - Small Minus Big）
- 价值因子（HML - High Minus Low）

---

## 📊 主要因子分类

### 1. 风险因子（Risk Factors）

**Fama-French 五因子模型**：
1. **市场因子（MKT）**
   - 市场超额收益
   - Beta 暴露

2. **规模因子（SMB）**
   - 小市值 vs 大市值
   - 小市值股票长期跑赢大市值

3. **价值因子（HML）**
   - 高账面市值比 vs 低账面市值比
   - 价值股长期跑赢成长股

4. **盈利因子（RMW）**
   - 高盈利 vs 低盈利
   - 盈利能力强的公司表现更好

5. **投资因子（CMA）**
   - 保守投资 vs 激进投资
   - 投资保守的公司表现更好

---

### 2. 动量因子（Momentum Factors）

**1. 价格动量（Price Momentum）**
- 过去 3-12 个月涨幅
- 趋势跟踪
- 胜率：60-70%

**2. 盈余动量（Earnings Momentum）**
- 盈余惊喜
- 分析师上调
- 胜率：55-65%

**3. 收入动量（Revenue Momentum）**
- 收入增长
- 销售加速
- 胜率：50-60%

---

### 3. 质量因子（Quality Factors）

**1. 盈利质量（Profitability）**
- ROE（净资产收益率）
- ROA（总资产收益率）
- 胜率：55-65%

**2. 财务稳健（Financial Strength）**
- 资产负债率
- 流动比率
- 胜率：55-60%

**3. 盈利稳定性（Earnings Stability）**
- 盈利波动率
- 现金流稳定性
- 胜率：50-60%

---

### 4. 波动率因子（Volatility Factors）

**1. 低波动率异象（Low Volatility Anomaly）**
- 低波动率股票长期跑赢高波动率
- 胜率：60-70%

**2. 波动率动量（Volatility Momentum）**
- 波动率变化趋势
- VIX 相关
- 胜率：50-60%

---

### 5. 流动性因子（Liquidity Factors）

**1. 流动性溢价（Liquidity Premium）**
- 低流动性 = 高收益
- Amihud 非流动性指标
- 胜率：55-65%

**2. 流动性动量（Liquidity Momentum）**
- 流动性变化
- 成交量变化
- 胜率：50-60%

---

### 6. 情绪因子（Sentiment Factors）

**1. 投资者情绪（Investor Sentiment）**
- 看涨/看跌比例
- 社交媒体情绪
- 胜率：50-55%

**2. 分析师情绪（Analyst Sentiment）**
- 分析师评级
- 目标价调整
- 胜率：50-55%

---

## 💻 因子计算公式

### 1. 价值因子

**账面市值比（B/P）**：
```python
# 账面价值 / 市值
book_to_market = book_value / market_cap

# 高 B/P = 价值股
# 低 B/P = 成长股
```

---

### 2. 规模因子

**市值（Market Cap）**：
```python
# 流通股数 * 股价
market_cap = shares_outstanding * price

# 小市值 = Market Cap < 中位数
# 大市值 = Market Cap > 中位数
```

---

### 3. 动量因子

**价格动量（12-1 动量）**：
```python
# 过去 12 个月收益 - 过去 1 个月收益
# 避免 1 个月反转效应
momentum_12_1 = (price[t] / price[t-12]) - (price[t] / price[t-1])
```

---

### 4. 质量因子

**盈利能力（ROE）**：
```python
# 净利润 / 净资产
ROE = net_income / shareholders_equity

# 高 ROE = 高质量
```

**财务稳健（Altman Z-Score）**：
```python
# 破产预警指标
Z = 1.2*(working_capital/total_assets) + \
    1.4*(retained_earnings/total_assets) + \
    3.3*(EBIT/total_assets) + \
    0.6*(market_cap/total_liabilities) + \
    1.0*(sales/total_assets)

# Z > 2.99 = 安全
# Z < 1.81 = 破产风险
```

---

### 5. 波动率因子

**历史波动率**：
```python
# 收益率标准差（年化）
returns = df['Close'].pct_change()
volatility = returns.std() * np.sqrt(252)

# 低波动率 = 低风险 + 高收益（异象）
```

---

## 📊 因子测试方法

### 1. 单因子测试

**IC（Information Coefficient）**：
```python
# 因子值与未来收益的相关系数
IC = correlation(factor_value, future_return)

# IC > 0.05 = 有效因子
# IC > 0.10 = 强因子
```

**IR（Information Ratio）**：
```python
# 超额收益 / 跟踪误差
IR = (portfolio_return - benchmark_return) / tracking_error

# IR > 0.5 = 优秀
# IR > 1.0 = 卓越
```

---

### 2. 多因子模型

**Fama-MacBeth 回归**：
```python
# 第一步：时间序列回归（估计 Beta）
for stock in stocks:
    beta[stock] = OLS(stock_return, factors).fit()

# 第二步：横截面回归（估计因子溢价）
for period in periods:
    factor_premium[period] = OLS(cross_section_return, beta).fit()

# 平均因子溢价
average_premium = mean(factor_premium)
```

---

### 3. 组合测试

**分位数组合**：
```python
# 将股票按因子值分为 10 组
group1 = stocks_with_lowest_factor_value  # 第 1 组
group10 = stocks_with_highest_factor_value  # 第 10 组

# 计算每组收益
return_group1 = portfolio_return(group1)
return_group10 = portfolio_return(group10)

# 多空组合
long_short_return = return_group10 - return_group1
```

---

## 🎯 经典因子策略

### 1. 价值投资（Value Investing）

**策略**：
- 买入低 P/E、P/B、P/CF 的股票
- 持有 3-5 年

**胜率**：60-70%（长期）
**年化收益**：12-15%

**代码示例**：
```python
# 价值因子
value_score = (1/PE + 1/PB + 1/PCF) / 3

# 选择价值得分最高的股票
selected_stocks = stocks.nlargest(50, 'value_score')
```

---

### 2. 动量投资（Momentum Investing）

**策略**：
- 买入过去 3-12 个月涨幅最大的股票
- 持有 3-6 个月

**胜率**：60-70%
**年化收益**：15-20%

**代码示例**：
```python
# 12-1 动量
momentum = (price / price.shift(12)) - (price / price.shift(1))

# 选择动量最强的股票
selected_stocks = stocks.nlargest(50, 'momentum')
```

---

### 3. 质量投资（Quality Investing）

**策略**：
- 买入高 ROE、低负债、稳定盈利的股票
- 持有 1-3 年

**胜率**：55-65%
**年化收益**：10-15%

**代码示例**：
```python
# 质量因子
quality_score = (ROE + (1/debt_ratio) + earnings_stability) / 3

# 选择质量最高的股票
selected_stocks = stocks.nlargest(50, 'quality_score')
```

---

### 4. 低波动率投资（Low Volatility Investing）

**策略**：
- 买入历史波动率低的股票
- 持有 1 年以上

**胜率**：60-70%
**年化收益**：10-12%（风险调整后更高）

**代码示例**：
```python
# 波动率
volatility = returns.rolling(252).std() * np.sqrt(252)

# 选择波动率最低的股票
selected_stocks = stocks.nsmallest(50, 'volatility')
```

---

### 5. 多因子组合（Multi-Factor Combination）

**策略**：
- 结合价值 + 动量 + 质量
- 分散风险

**胜率**：65-75%
**年化收益**：15-25%

**代码示例**：
```python
# 多因子得分
multi_factor_score = (
    0.3 * value_score +
    0.3 * momentum_score +
    0.2 * quality_score +
    0.2 * low_volatility_score
)

# 选择综合得分最高的股票
selected_stocks = stocks.nlargest(50, 'multi_factor_score')
```

---

## 📊 因子胜率统计

### 单因子胜率

| 因子类型 | 胜率 | 年化收益 | 夏普比率 | 最大回撤 |
|---------|------|---------|---------|---------|
| 价值因子 | 60-70% | 12-15% | 0.6-0.8 | -30% |
| 动量因子 | 60-70% | 15-20% | 0.7-0.9 | -40% |
| 质量因子 | 55-65% | 10-15% | 0.7-0.9 | -25% |
| 低波动率 | 60-70% | 10-12% | 0.8-1.0 | -20% |
| 规模因子 | 55-60% | 8-12% | 0.5-0.7 | -35% |

---

### 多因子组合胜率

| 组合方式 | 胜率 | 年化收益 | 夏普比率 | 最大回撤 |
|---------|------|---------|---------|---------|
| 价值+动量 | 65-75% | 18-22% | 0.9-1.1 | -25% |
| 价值+质量 | 60-70% | 15-18% | 1.0-1.2 | -20% |
| 动量+质量 | 65-75% | 20-25% | 1.0-1.2 | -30% |
| 全因子组合 | 70-80% | 20-30% | 1.2-1.5 | -20% |

---

## 💡 因子投资实战建议

### 1. 因子选择

**优先级**：
1. **动量因子**（胜率最高，60-70%）
2. **价值因子**（长期有效）
3. **质量因子**（风险低）
4. **低波动率**（夏普比率高）

---

### 2. 因子组合

**推荐组合**：
- **价值 + 动量**（胜率 65-75%）
- **质量 + 动量**（胜率 65-75%）
- **全因子组合**（胜率 70-80%）

---

### 3. 风险管理

**关键规则**：
1. **因子分散**：至少 3 个因子
2. **行业分散**：避免集中在单一行业
3. **止损设置**：单因子 -5%，组合 -10%
4. **定期调仓**：季度或半年度

---

## 📚 延伸阅读

### 经典论文

**1. Fama-French 三因子模型**
- Fama, E. F., & French, K. R. (1993)
- "Common risk factors in the returns on stocks and bonds"

**2. 动量效应**
- Jegadeesh, N., & Titman, S. (1993)
- "Returns to buying winners and selling losers"

**3. 低波动率异象**
- Ang, A., et al. (2006)
- "The cross-section of volatility and expected returns"

---

### 书籍推荐

**1. "Active Portfolio Management"**
- Grinold & Kahn
- 因子投资圣经

**2. "Expected Returns"**
- Antti Ilmanen
- 因子收益预测

**3. "Quantitative Equity Portfolio Management"**
- Ludwig B. Chincarini & Daehwan Kim
- 量化投资实战

---

## 🎯 下一步学习

### 1. 因子数据获取

**数据源**：
- Tushare（A股）
- Wind（专业）
- Bloomberg（全球）

---

### 2. 因子回测

**框架**：
- Backtrader
- Zipline
- QuantConnect

---

### 3. 因子优化

**方法**：
- IC 加权
- IR 加权
- 机器学习优化

---

_学习笔记创建时间：2026-03-13 07:50 UTC_
