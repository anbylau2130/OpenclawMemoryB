# 量化交易策略入门

## 一、量化交易概述

### 1.1 什么是量化交易

**定义：**
- 用数学模型和计算机程序进行交易决策
- 基于历史数据统计分析
- 系统化、纪律化执行

**与传统交易对比：**

| 特性 | 量化交易 | 传统交易 |
|------|---------|---------|
| **决策依据** | 数据和模型 | 经验和直觉 |
| **执行方式** | 程序自动化 | 人工下单 |
| **情绪影响** | 无 | 大 |
| **回测验证** | 可回测 | 无法回测 |
| **纪律性** | 强 | 弱 |
| **适应性** | 需要优化 | 灵活 |

---

### 1.2 量化交易优势

**优势：**

```
1. 纪律性
   - 严格执行策略
   - 不受情绪影响
   - 不追涨杀跌

2. 可回测
   - 历史数据验证
   - 统计胜率和盈亏比
   - 优化参数

3. 系统化
   - 完整的交易规则
   - 可重复执行
   - 持续优化

4. 效率高
   - 自动化执行
   - 快速响应
   - 多标的监控

5. 风险可控
   - 量化止损
   - 仓位管理
   - 风险监控
```

---

### 1.3 量化交易流程

**完整流程：**

```
1. 策略构思
   - 观察市场规律
   - 提出假设
   - 设计策略框架

2. 数据准备
   - 获取历史数据
   - 数据清洗
   - 特征工程

3. 策略开发
   - 编写策略代码
   - 设置参数
   - 定义规则

4. 回测验证
   - 历史数据回测
   - 统计指标
   - 优化参数

5. 模拟盘
   - 实时数据测试
   - 验证执行
   - 调整优化

6. 实盘交易
   - 小资金验证
   - 逐步放大
   - 持续监控

7. 风险管理
   - 止损止盈
   - 仓位控制
   - 异常处理

8. 持续优化
   - 定期复盘
   - 策略迭代
   - 适应市场
```

---

## 二、策略类型

### 2.1 趋势跟踪策略

**策略1：双均线策略**

```python
# Python 伪代码
def dual_ma_strategy(prices, fast_period=10, slow_period=30):
    """
    双均线策略
    买入：快线上穿慢线
    卖出：快线下穿慢线
    """
    # 计算均线
    fast_ma = calculate_ma(prices, fast_period)
    slow_ma = calculate_ma(prices, slow_period)
    
    signals = []
    for i in range(1, len(prices)):
        # 金叉：快线上穿慢线
        if fast_ma[i] > slow_ma[i] and fast_ma[i-1] <= slow_ma[i-1]:
            signals.append(('buy', i, prices[i]))
        
        # 死叉：快线下穿慢线
        elif fast_ma[i] < slow_ma[i] and fast_ma[i-1] >= slow_ma[i-1]:
            signals.append(('sell', i, prices[i]))
    
    return signals

# 回测
prices = get_historical_prices('600031', '2025-01-01', '2026-03-07')
signals = dual_ma_strategy(prices, fast_period=10, slow_period=30)
returns = calculate_returns(prices, signals)

print(f"总收益率：{returns['total_return']:.2%}")
print(f"胜率：{returns['win_rate']:.2%}")
print(f"最大回撤：{returns['max_drawdown']:.2%}")
```

**策略2：MACD策略**

```python
def macd_strategy(prices, fast=12, slow=26, signal=9):
    """
    MACD策略
    买入：DIF上穿DEA（金叉）
    卖出：DIF下穿DEA（死叉）
    """
    # 计算MACD
    macd_data = calculate_macd(prices, fast, slow, signal)
    
    signals = []
    for i in range(1, len(prices)):
        # 金叉
        if macd_data['DIF'][i] > macd_data['DEA'][i] and \
           macd_data['DIF'][i-1] <= macd_data['DEA'][i-1]:
            signals.append(('buy', i, prices[i]))
        
        # 死叉
        elif macd_data['DIF'][i] < macd_data['DEA'][i] and \
             macd_data['DIF'][i-1] >= macd_data['DEA'][i-1]:
            signals.append(('sell', i, prices[i]))
    
    return signals
```

---

### 2.2 均值回归策略

**策略1：布林带策略**

```python
def bollinger_strategy(prices, period=20, std_dev=2):
    """
    布林带策略
    买入：价格触及下轨
    卖出：价格触及上轨
    """
    # 计算布林带
    boll = calculate_bollinger(prices, period, std_dev)
    
    signals = []
    for i in range(period, len(prices)):
        # 触及下轨，买入
        if prices[i] <= boll['lower'][i]:
            signals.append(('buy', i, prices[i]))
        
        # 触及上轨，卖出
        elif prices[i] >= boll['upper'][i]:
            signals.append(('sell', i, prices[i]))
    
    return signals
```

**策略2：RSI策略**

```python
def rsi_strategy(prices, period=14, oversold=30, overbought=70):
    """
    RSI策略
    买入：RSI < 30（超卖）
    卖出：RSI > 70（超买）
    """
    # 计算RSI
    rsi = calculate_rsi(prices, period)
    
    signals = []
    for i in range(period, len(prices)):
        # 超卖，买入
        if rsi[i] < oversold and rsi[i-1] >= oversold:
            signals.append(('buy', i, prices[i]))
        
        # 超买，卖出
        elif rsi[i] > overbought and rsi[i-1] <= overbought:
            signals.append(('sell', i, prices[i]))
    
    return signals
```

---

### 2.3 多因子策略

**策略1：量价因子策略**

```python
def volume_price_strategy(prices, volumes):
    """
    量价因子策略
    买入：缩量 + 支撑有效
    卖出：放量 + 阻力遇阻
    """
    signals = []
    
    for i in range(20, len(prices)):
        # 计算量价因子
        volume_ratio = volumes[i] / calculate_ma(volumes, 5)[i]
        price_change = (prices[i] - prices[i-1]) / prices[i-1]
        
        # 缩量十字星
        if volume_ratio < 0.7 and abs(price_change) < 0.01:
            # 检查支撑位
            support = find_support(prices[:i])
            if prices[i] >= support * 0.98:  # 支撑有效
                signals.append(('buy', i, prices[i]))
        
        # 放量滞涨
        elif volume_ratio > 1.5 and price_change > 0.02:
            # 检查阻力位
            resistance = find_resistance(prices[:i])
            if prices[i] >= resistance * 0.98:  # 遇阻
                signals.append(('sell', i, prices[i]))
    
    return signals
```

**策略2：多因子组合策略**

```python
def multi_factor_strategy(prices, volumes):
    """
    多因子组合策略
    因子1：MACD 金叉
    因子2：RSI 超卖
    因子3：缩量
    因子4：支撑有效
    """
    # 计算各因子
    macd = calculate_macd(prices)
    rsi = calculate_rsi(prices)
    volume_ma = calculate_ma(volumes, 5)
    
    signals = []
    
    for i in range(30, len(prices)):
        score = 0
        
        # 因子1：MACD 金叉
        if macd['DIF'][i] > macd['DEA'][i] and macd['DIF'][i-1] <= macd['DEA'][i-1]:
            score += 25
        
        # 因子2：RSI 超卖
        if rsi[i] < 30:
            score += 25
        
        # 因子3：缩量
        if volumes[i] < volume_ma[i] * 0.7:
            score += 25
        
        # 因子4：支撑有效
        support = find_support(prices[:i])
        if prices[i] >= support * 0.98:
            score += 25
        
        # 信号判断
        if score >= 75:  # 3个以上因子
            signals.append(('buy', i, prices[i], score))
    
    return signals
```

---

## 三、回测系统

### 3.1 回测框架

**完整回测代码：**

```python
import pandas as pd
import numpy as np

class BacktestEngine:
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0  # 持仓数量
        self.trades = []   # 交易记录
        self.equity_curve = []  # 权益曲线
    
    def run_backtest(self, prices, signals):
        """
        运行回测
        prices: 价格序列
        signals: 信号列表 [('buy', index, price), ('sell', index, price)]
        """
        for signal in signals:
            action, index, price = signal[0], signal[1], signal[2]
            
            if action == 'buy' and self.position == 0:
                # 买入
                shares = int(self.capital / price)
                cost = shares * price
                self.capital -= cost
                self.position = shares
                
                self.trades.append({
                    'date': index,
                    'action': 'buy',
                    'price': price,
                    'shares': shares,
                    'capital': self.capital
                })
            
            elif action == 'sell' and self.position > 0:
                # 卖出
                revenue = self.position * price
                self.capital += revenue
                
                self.trades.append({
                    'date': index,
                    'action': 'sell',
                    'price': price,
                    'shares': self.position,
                    'capital': self.capital
                })
                
                self.position = 0
            
            # 记录权益
            equity = self.capital + self.position * price
            self.equity_curve.append({
                'date': index,
                'equity': equity
            })
        
        return self.calculate_metrics()
    
    def calculate_metrics(self):
        """计算回测指标"""
        equity_df = pd.DataFrame(self.equity_curve)
        
        # 总收益率
        total_return = (equity_df['equity'].iloc[-1] - self.initial_capital) / self.initial_capital
        
        # 年化收益率（假设数据为日线）
        days = len(equity_df)
        annual_return = (1 + total_return) ** (252 / days) - 1
        
        # 最大回撤
        equity_df['cummax'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['cummax'] - equity_df['equity']) / equity_df['cummax']
        max_drawdown = equity_df['drawdown'].max()
        
        # 胜率
        trades_df = pd.DataFrame(self.trades)
        buy_trades = trades_df[trades_df['action'] == 'buy']
        sell_trades = trades_df[trades_df['action'] == 'sell']
        
        profits = []
        for i in range(min(len(buy_trades), len(sell_trades))):
            profit = (sell_trades.iloc[i]['price'] - buy_trades.iloc[i]['price']) / buy_trades.iloc[i]['price']
            profits.append(profit)
        
        win_rate = len([p for p in profits if p > 0]) / len(profits) if profits else 0
        
        # 夏普比率
        returns = equity_df['equity'].pct_change().dropna()
        sharpe_ratio = (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'sharpe_ratio': sharpe_ratio,
            'num_trades': len(profits)
        }

# 使用示例
prices = get_historical_prices('600031', '2025-01-01', '2026-03-07')
signals = dual_ma_strategy(prices, fast_period=10, slow_period=30)

engine = BacktestEngine(initial_capital=100000)
metrics = engine.run_backtest(prices, signals)

print(f"总收益率：{metrics['total_return']:.2%}")
print(f"年化收益率：{metrics['annual_return']:.2%}")
print(f"最大回撤：{metrics['max_drawdown']:.2%}")
print(f"胜率：{metrics['win_rate']:.2%}")
print(f"夏普比率：{metrics['sharpe_ratio']:.2f}")
print(f"交易次数：{metrics['num_trades']}")
```

---

### 3.2 参数优化

**网格搜索优化：**

```python
def optimize_parameters(prices, strategy_func, param_grid):
    """
    参数优化
    prices: 价格序列
    strategy_func: 策略函数
    param_grid: 参数网格 {'fast_period': [5,10,15], 'slow_period': [20,30,40]}
    """
    best_params = None
    best_sharpe = -np.inf
    results = []
    
    # 遍历所有参数组合
    for fast in param_grid['fast_period']:
        for slow in param_grid['slow_period']:
            # 运行策略
            signals = strategy_func(prices, fast_period=fast, slow_period=slow)
            
            # 回测
            engine = BacktestEngine()
            metrics = engine.run_backtest(prices, signals)
            
            # 记录结果
            results.append({
                'fast_period': fast,
                'slow_period': slow,
                'sharpe_ratio': metrics['sharpe_ratio'],
                'total_return': metrics['total_return'],
                'max_drawdown': metrics['max_drawdown']
            })
            
            # 更新最佳参数
            if metrics['sharpe_ratio'] > best_sharpe:
                best_sharpe = metrics['sharpe_ratio']
                best_params = {'fast_period': fast, 'slow_period': slow}
    
    return best_params, pd.DataFrame(results)

# 使用示例
param_grid = {
    'fast_period': [5, 10, 15, 20],
    'slow_period': [20, 30, 40, 50]
}

best_params, results = optimize_parameters(prices, dual_ma_strategy, param_grid)

print(f"最佳参数：{best_params}")
print(results.sort_values('sharpe_ratio', ascending=False).head())
```

---

### 3.3 风险控制

**仓位管理：**

```python
class RiskManager:
    def __init__(self, max_position=0.8, max_single_loss=0.07, max_total_loss=0.2):
        self.max_position = max_position      # 最大仓位
        self.max_single_loss = max_single_loss  # 单笔最大亏损
        self.max_total_loss = max_total_loss    # 总最大亏损
    
    def calculate_position_size(self, capital, price, stop_loss_price):
        """
        计算仓位大小
        基于止损位计算
        """
        # 单笔最大亏损金额
        max_loss_amount = capital * self.max_single_loss
        
        # 每股最大亏损
        loss_per_share = price - stop_loss_price
        
        # 计算股数
        shares = int(max_loss_amount / loss_per_share)
        
        # 检查仓位限制
        max_shares = int(capital * self.max_position / price)
        shares = min(shares, max_shares)
        
        return shares
    
    def check_risk(self, portfolio_value, initial_capital):
        """
        检查风险
        """
        total_loss = (initial_capital - portfolio_value) / initial_capital
        
        if total_loss > self.max_total_loss:
            return {
                'status': 'stop_trading',
                'message': f'总亏损{total_loss:.2%}超过限制{self.max_total_loss:.2%}'
            }
        
        return {
            'status': 'ok',
            'message': '风险可控'
        }

# 使用示例
risk_manager = RiskManager()
shares = risk_manager.calculate_position_size(
    capital=100000,
    price=22.00,
    stop_loss_price=21.77
)
print(f"建议买入：{shares}股")
```

---

## 四、实战案例

### 4.1 三一重工量化策略

**完整策略：**

```python
def sany_quant_strategy(prices, volumes):
    """
    三一重工量化策略
    多因子组合
    """
    # 计算各指标
    macd = calculate_macd(prices)
    rsi = calculate_rsi(prices)
    kdj = calculate_kdj(prices)
    boll = calculate_bollinger(prices)
    volume_ma = calculate_ma(volumes, 5)
    
    signals = []
    
    for i in range(30, len(prices)):
        buy_score = 0
        sell_score = 0
        
        # 买入因子
        # 因子1：MACD 金叉
        if macd['DIF'][i] > macd['DEA'][i] and macd['DIF'][i-1] <= macd['DEA'][i-1]:
            buy_score += 20
        
        # 因子2：RSI 超卖
        if rsi[i] < 30:
            buy_score += 20
        
        # 因子3：KDJ 金叉
        if kdj['K'][i] > kdj['D'][i] and kdj['K'][i-1] <= kdj['D'][i-1]:
            buy_score += 20
        
        # 因子4：布林带下轨
        if prices[i] <= boll['lower'][i]:
            buy_score += 20
        
        # 因子5：缩量
        if volumes[i] < volume_ma[i] * 0.7:
            buy_score += 20
        
        # 卖出因子
        # 因子1：MACD 死叉
        if macd['DIF'][i] < macd['DEA'][i] and macd['DIF'][i-1] >= macd['DEA'][i-1]:
            sell_score += 20
        
        # 因子2：RSI 超买
        if rsi[i] > 70:
            sell_score += 20
        
        # 因子3：KDJ 死叉
        if kdj['K'][i] < kdj['D'][i] and kdj['K'][i-1] >= kdj['D'][i-1]:
            sell_score += 20
        
        # 因子4：布林带上轨
        if prices[i] >= boll['upper'][i]:
            sell_score += 20
        
        # 因子5：放量
        if volumes[i] > volume_ma[i] * 1.5:
            sell_score += 20
        
        # 生成信号
        if buy_score >= 60:  # 3个以上因子
            signals.append(('buy', i, prices[i], buy_score))
        elif sell_score >= 60:
            signals.append(('sell', i, prices[i], sell_score))
    
    return signals

# 回测
prices, volumes = get_historical_data('600031', '2025-01-01', '2026-03-07')
signals = sany_quant_strategy(prices, volumes)

engine = BacktestEngine(initial_capital=100000)
metrics = engine.run_backtest(prices, signals)

print(f"总收益率：{metrics['total_return']:.2%}")
print(f"年化收益率：{metrics['annual_return']:.2%}")
print(f"最大回撤：{metrics['max_drawdown']:.2%}")
print(f"胜率：{metrics['win_rate']:.2%}")
print(f"夏普比率：{metrics['sharpe_ratio']:.2f}")
print(f"交易次数：{metrics['num_trades']}")
```

---

## 📝 总结

**量化交易核心：**

| 模块 | 说明 |
|------|------|
| **策略开发** | 基于数据和模型设计策略 |
| **回测验证** | 历史数据验证策略有效性 |
| **参数优化** | 网格搜索找最佳参数 |
| **风险控制** | 仓位管理、止损止盈 |
| **持续优化** | 定期复盘、策略迭代 |

**学习路径：**

```
1. 基础知识
   - Python 编程
   - 数据分析（Pandas、NumPy）
   - 统计学基础

2. 策略开发
   - 技术指标计算
   - 信号生成规则
   - 多因子模型

3. 回测系统
   - 回测框架搭建
   - 指标计算
   - 参数优化

4. 实盘交易
   - 模拟盘测试
   - 小资金验证
   - 风险控制

5. 持续优化
   - 策略迭代
   - 适应市场
   - 提高收益
```

---

_最后更新：2026-03-07 04:15 UTC_
