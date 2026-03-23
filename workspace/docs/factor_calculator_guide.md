# 量化因子计算器使用指南

> **文件位置：** `Knowledge/trading-strategies/code/factor_calculator.py`
> **版本：** v1.0
> **依赖：** 纯Python，无需外部库

---

## 一、快速开始

```python
# 导入因子计算器
from factor_calculator import *

# 准备股票数据（字典格式）
data = {
    'price': [10.5, 10.8, 11.2, ...],           # 股价
    'book_value_per_share': [8.5, ...],         # 每股净资产
    'eps': [0.8, ...],                          # 每股收益
    'dividend_per_share': [0.3, ...],           # 每股股息
    'total_shares': [1000000000, ...],          # 总股本
    'net_income': [500000000, ...],             # 净利润
    'total_equity': [3000000000, ...],          # 总权益
    'total_assets': [5000000000, ...],          # 总资产
    'total_debt': [2000000000, ...],            # 总负债
    'revenue': [2000000000, ...],               # 营收
    'cost_of_revenue': [1200000000, ...]        # 营业成本
}
```

---

## 二、单因子计算

### 2.1 价值因子

```python
value_scores = calc_value_factor(data)
# 返回：价值因子得分列表（负值=被低估）
```

**判断标准：**
- 得分 < 0：被低估（买入信号）
- 得分 > 0：被高估（卖出信号）

---

### 2.2 动量因子

```python
momentum_scores = calc_momentum_factor(data, lookback=252, exclude_recent=21)
# lookback=252：回看1年
# exclude_recent=21：排除最近1个月（避免短期反转）
```

**判断标准：**
- 得分 > 0：上涨趋势强
- 得分 < 0：下跌趋势强

---

### 2.3 质量因子

```python
quality_scores = calc_quality_factor(data)
# 基于：ROE、ROA、毛利率、负债率
```

**判断标准：**
- 得分 > 0：财务质量好
- 得分 < 0：财务质量差

---

### 2.4 规模因子

```python
size_scores = calc_size_factor(data)
# 基于市值（对数）
```

**判断标准：**
- 得分 > 0：小盘股
- 得分 < 0：大盘股

---

### 2.5 低波动因子

```python
low_vol_scores = calc_low_vol_factor(data, lookback=252)
# 基于历史波动率
```

**判断标准：**
- 得分 > 0：低波动
- 得分 < 0：高波动

---

### 2.6 成长因子

```python
growth_scores = calc_growth_factor(data, period=252)
# 基于营收增长率和EPS增长率
```

**判断标准：**
- 得分 > 0：高增长
- 得分 < 0：低增长

---

## 三、多因子组合

### 3.1 预设因子组合

```python
# 稳健型（低风险）
CONSERVATIVE_WEIGHTS = {
    'value': 0.30,
    'quality': 0.30,
    'low_vol': 0.40
}

# 成长型（高收益）
GROWTH_WEIGHTS = {
    'momentum': 0.35,
    'growth': 0.35,
    'quality': 0.30
}

# 均衡型（推荐）
BALANCED_WEIGHTS = {
    'value': 0.20,
    'momentum': 0.20,
    'quality': 0.25,
    'size': 0.15,
    'low_vol': 0.20
}

# A股优化型
A_STOCK_WEIGHTS = {
    'value': 0.15,
    'momentum': 0.20,
    'quality': 0.30,
    'size': 0.20,
    'low_vol': 0.15
}
```

### 3.2 计算综合得分

```python
# 使用均衡型权重
composite_scores = calc_multifactor_score(data, BALANCED_WEIGHTS)

# 自定义权重
my_weights = {
    'value': 0.25,
    'momentum': 0.25,
    'quality': 0.50
}
composite_scores = calc_multifactor_score(data, my_weights)
```

---

## 四、回测功能

### 4.1 单因子回测

```python
# 计算未来收益（21天后）
forward_returns = []
for i in range(len(prices)):
    if i + 21 < len(prices):
        ret = (prices[i + 21] / prices[i]) - 1
        forward_returns.append(ret)

# 回测
result = backtest_single_factor(value_scores, forward_returns, n_groups=5)

# 结果
print(f"IC值: {result['ic']:.4f} ({result['ic_quality']})")
print(f"多空收益: {result['long_short_return']:.2%}")

for stat in result['group_stats']:
    print(f"第{stat['group']}组: 收益={stat['avg_return']:.2%}, 胜率={stat['win_rate']:.1%}")
```

---

### 4.2 完整回测报告

```python
# 生成完整报告
report = generate_backtest_report(data, BALANCED_WEIGHTS, forward_periods=21)
print(report)
```

**输出示例：**
```
============================================================
量化因子回测报告
============================================================

【因子权重】
  value: 20.0%
  momentum: 20.0%
  quality: 25.0%
  size: 15.0%
  low_vol: 20.0%

【回测结果】
  样本数量: 500
  预测周期: 21天
  IC值: 0.0689 (优秀)
  多空收益: 512.77%

【分组收益】
  第1组: 收益=-610.39%, 胜率=27.1%
  第2组: 收益=70.57%, 胜率=46.9%
  第3组: 收益=23.11%, 胜率=38.5%
  第4组: 收益=17.93%, 胜率=52.1%
  第5组: 收益=-97.62%, 胜率=41.1%

【胜率统计】
  最高组胜率: 52.1%
  最低组胜率: 27.1%
  平均胜率: 41.1%

============================================================
```

---

## 五、胜率计算

### 5.1 基本胜率

```python
returns = [0.05, -0.02, 0.03, 0.01, -0.01, 0.04, ...]
win_rate = calc_win_rate(returns)
print(f"胜率: {win_rate:.1%}")
```

### 5.2 夏普比率

```python
sharpe = calc_sharpe_ratio(returns, risk_free_rate=0.03, periods_per_year=252)
print(f"夏普比率: {sharpe:.3f}")
```

**判断标准：**
- Sharpe > 1.0：优秀
- Sharpe 0.5-1.0：良好
- Sharpe 0-0.5：一般
- Sharpe < 0：差

### 5.3 最大回撤

```python
prices = [10, 11, 10.5, 12, 11, 10, 9, 10, 11, 12]
max_dd = calc_max_drawdown(prices)
print(f"最大回撤: {max_dd:.2%}")
```

---

## 六、实战应用

### 6.1 选股流程

```python
# 1. 准备数据
stocks_data = {
    '600031': {...},  # 三一重工
    '600028': {...},  # 中国石化
    ...
}

# 2. 计算各股票综合得分
scores = {}
for stock_code, data in stocks_data.items():
    score = calc_multifactor_score(data, A_STOCK_WEIGHTS)
    scores[stock_code] = score[-1]  # 取最新得分

# 3. 排序选股
sorted_stocks = sorted(scores.items(), key=lambda x: x[1], reverse=True)

# 4. 选取前10名
selected = sorted_stocks[:10]
for code, score in selected:
    print(f"{code}: 得分={score:.3f}")
```

---

### 6.2 IC监控

```python
# 每日计算IC，监控因子有效性
ic_history = []

for date in trading_dates:
    factor_values = calc_value_factor(data[date])
    forward_returns = get_forward_returns(date, periods=21)
    ic, quality = calc_ic(factor_values, forward_returns)
    ic_history.append(ic)
    
    print(f"{date}: IC={ic:.4f} ({quality})")

# 计算IC均值和ICIR
ic_mean = sum(ic_history) / len(ic_history)
ic_std = (sum((ic - ic_mean)**2 for ic in ic_history) / len(ic_history)) ** 0.5
icir = ic_mean / ic_std if ic_std > 0 else 0

print(f"IC均值: {ic_mean:.4f}")
print(f"ICIR: {icir:.4f}")
```

---

## 七、IC判断标准

### 7.1 IC值

| IC范围 | 因子质量 |
|--------|---------|
| > 0.05 | 优秀 |
| 0.03-0.05 | 良好 |
| 0.01-0.03 | 一般 |
| < 0.01 | 较差 |

### 7.2 ICIR

| ICIR范围 | 因子稳定性 |
|----------|-----------|
| > 0.5 | 优秀 |
| 0.3-0.5 | 良好 |
| 0.1-0.3 | 一般 |
| < 0.1 | 较差 |

---

## 八、注意事项

1. **数据质量**：确保财务数据准确，价格数据完整
2. **样本量**：至少需要100个以上样本才能进行有效回测
3. **过拟合**：避免过度优化因子权重
4. **市场环境**：不同市场环境下因子有效性可能变化
5. **交易成本**：实际交易需要考虑滑点和手续费

---

**文档更新：** 2026-03-16
