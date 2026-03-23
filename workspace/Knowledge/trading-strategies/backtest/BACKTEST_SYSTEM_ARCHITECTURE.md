# 回测系统完整架构

> 来源：OpenclawMemery 仓库
> 日期：2026-03-17

---

## 一、回测系统架构

### 1.1 系统组件

```
┌─────────────────────────────────────────┐
│         回测系统架构                      │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │  数据模块     │───▶│  策略模块     │  │
│  │  DataModule  │    │ StrategyMod  │  │
│  └──────────────┘    └──────────────┘  │
│         │                    │         │
│         ▼                    ▼         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │  信号模块     │───▶│  交易模块     │  │
│  │ SignalModule │    │ TradingMod   │  │
│  └──────────────┘    └──────────────┘  │
│         │                    │         │
│         ▼                    ▼         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │  风险模块     │───▶│  报告模块     │  │
│  │ RiskModule   │    │ ReportModule │  │
│  └──────────────┘    └──────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

### 1.2 各模块职责

| 模块 | 职责 | 输入 | 输出 |
|------|------|------|------|
| **数据模块** | 获取、清洗数据 | 原始数据 | 处理后数据 |
| **策略模块** | 生成交易信号 | 价格、指标 | 买入/卖出信号 |
| **信号模块** | 过滤、优化信号 | 原始信号 | 最终信号 |
| **交易模块** | 执行交易 | 信号、资金 | 交易记录 |
| **风险模块** | 风险控制 | 仓位、盈亏 | 风险报告 |
| **报告模块** | 生成报告 | 交易记录 | 回测报告 |

---

## 二、数据模块

### 2.1 数据获取

```python
import pandas as pd
import tushare as ts
import akshare as ak

class DataModule:
    def __init__(self, source='akshare'):
        self.source = source
        
        if source == 'tushare':
            ts.set_token('your_token')
            self.pro = ts.pro_api()
    
    def get_daily_data(self, symbol, start_date, end_date):
        """获取日线数据"""
        if self.source == 'tushare':
            df = self.pro.daily(
                ts_code=symbol,
                start_date=start_date,
                end_date=end_date
            )
        
        elif self.source == 'akshare':
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period='daily',
                start_date=start_date,
                end_date=end_date,
                adjust='qfq'  # 前复权
            )
        
        return df
    
    def get_realtime_data(self, symbol):
        """获取实时数据"""
        if self.source == 'akshare':
            df = ak.stock_zh_a_spot_em()
            df = df[df['代码'] == symbol]
            return df
```

### 2.2 数据清洗

```python
class DataCleaner:
    def clean_data(self, df):
        """数据清洗"""
        # 1. 检查缺失值
        print(f"缺失值统计：\n{df.isnull().sum()}")
        
        # 2. 填充缺失值
        df = df.fillna(method='ffill')  # 前向填充
        
        # 3. 检查异常值
        df = self.remove_outliers(df)
        
        # 4. 数据类型转换
        df['日期'] = pd.to_datetime(df['日期'])
        df['收盘'] = pd.to_numeric(df['收盘'], errors='coerce')
        
        return df
    
    def remove_outliers(self, df):
        """移除异常值"""
        # 使用IQR方法检测异常值
        Q1 = df['收盘'].quantile(0.25)
        Q3 = df['收盘'].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        df = df[(df['收盘'] >= lower_bound) & (df['收盘'] <= upper_bound)]
        
        return df
```

---

## 三、策略模块

### 3.1 策略基类

```python
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, params=None):
        self.params = params or {}
    
    @abstractmethod
    def generate_signals(self, data):
        """生成交易信号"""
        pass
    
    def calculate_indicators(self, data):
        """计算技术指标"""
        pass
```

### 3.2 多因子策略

```python
class MultiFactorStrategy(BaseStrategy):
    """多因子策略"""
    
    def generate_signals(self, data):
        signals = []
        
        # 1. VWAP因子
        if self.check_vwap(data):
            signals.append(('VWAP', 1, 3.0))  # (因子名, 方向, 权重)
        
        # 2. 布林带因子
        if self.check_bollinger(data):
            signals.append(('BOLL', 1, 2.0))
        
        # 3. RSI因子
        if self.check_rsi(data):
            signals.append(('RSI', 1, 1.5))
        
        # 4. KDJ因子
        if self.check_kdj(data):
            signals.append(('KDJ', 1, 1.5))
        
        # 计算总分
        total_score = sum([s[2] for s in signals])
        
        return {
            'signals': signals,
            'score': total_score,
            'action': 'BUY' if total_score >= 3 else 'HOLD'
        }
```

---

## 四、信号模块

### 4.1 信号过滤

```python
class SignalFilter:
    """信号过滤器"""
    
    def __init__(self, min_score=3.0):
        self.min_score = min_score
    
    def filter_signals(self, signals):
        """过滤低质量信号"""
        return [s for s in signals if s['score'] >= self.min_score]
    
    def combine_signals(self, signals):
        """组合多个信号"""
        if not signals:
            return None
        
        # 取最高分信号
        best_signal = max(signals, key=lambda x: x['score'])
        
        return best_signal
```

---

## 五、交易模块

### 5.1 交易执行

```python
class TradingModule:
    """交易模块"""
    
    def __init__(self, initial_capital=100000):
        self.capital = initial_capital
        self.positions = {}
        self.trades = []
    
    def execute_trade(self, signal, price):
        """执行交易"""
        if signal['action'] == 'BUY':
            shares = int(self.capital * 0.2 / price)  # 20%仓位
            if shares > 0:
                self.positions[signal['symbol']] = {
                    'shares': shares,
                    'buy_price': price,
                    'buy_time': signal['time']
                }
                self.capital -= shares * price
                self.trades.append({
                    'type': 'BUY',
                    'symbol': signal['symbol'],
                    'price': price,
                    'shares': shares,
                    'time': signal['time']
                })
        
        elif signal['action'] == 'SELL':
            if signal['symbol'] in self.positions:
                pos = self.positions[signal['symbol']]
                self.capital += pos['shares'] * price
                self.trades.append({
                    'type': 'SELL',
                    'symbol': signal['symbol'],
                    'price': price,
                    'shares': pos['shares'],
                    'time': signal['time'],
                    'pnl': (price - pos['buy_price']) / pos['buy_price']
                })
                del self.positions[signal['symbol']]
```

---

## 六、风险模块

### 6.1 风险控制

```python
class RiskModule:
    """风险模块"""
    
    def __init__(self, stop_loss=0.03, take_profit=0.10):
        self.stop_loss = stop_loss
        self.take_profit = take_profit
    
    def check_stop_loss(self, position, current_price):
        """检查止损"""
        pnl_pct = (current_price - position['buy_price']) / position['buy_price']
        return pnl_pct <= -self.stop_loss
    
    def check_take_profit(self, position, current_price):
        """检查止盈"""
        pnl_pct = (current_price - position['buy_price']) / position['buy_price']
        return pnl_pct >= self.take_profit
    
    def calculate_position_size(self, capital, risk_per_trade=0.02):
        """计算仓位大小"""
        return capital * risk_per_trade
```

---

## 七、报告模块

### 7.1 报告生成

```python
class ReportModule:
    """报告模块"""
    
    def generate_report(self, trades, initial_capital, final_capital):
        """生成回测报告"""
        total_trades = len([t for t in trades if t['type'] == 'SELL'])
        win_trades = len([t for t in trades if t['type'] == 'SELL' and t.get('pnl', 0) > 0])
        loss_trades = total_trades - win_trades
        
        total_return = (final_capital - initial_capital) / initial_capital * 100
        win_rate = win_trades / total_trades * 100 if total_trades > 0 else 0
        
        report = {
            'initial_capital': initial_capital,
            'final_capital': final_capital,
            'total_return': f"{total_return:.2f}%",
            'total_trades': total_trades,
            'win_trades': win_trades,
            'loss_trades': loss_trades,
            'win_rate': f"{win_rate:.1f}%",
            'risk_reward_ratio': f"{self.take_profit/self.stop_loss:.1f}"
        }
        
        return report
```

---

## 八、使用示例

```python
# 初始化各模块
data_module = DataModule(source='akshare')
strategy = MultiFactorStrategy()
signal_filter = SignalFilter(min_score=3.0)
trading_module = TradingModule(initial_capital=100000)
risk_module = RiskModule(stop_loss=0.03, take_profit=0.10)
report_module = ReportModule()

# 获取数据
data = data_module.get_daily_data('600031', '20250101', '20260317')

# 生成信号
signals = strategy.generate_signals(data)

# 过滤信号
filtered_signals = signal_filter.filter_signals(signals)

# 执行交易
for signal in filtered_signals:
    trading_module.execute_trade(signal, signal['price'])

# 生成报告
report = report_module.generate_report(
    trading_module.trades,
    100000,
    trading_module.capital
)

print(report)
```

---

_来源：OpenclawMemery 仓库 main 分支_
_提取时间：2026-03-17_
