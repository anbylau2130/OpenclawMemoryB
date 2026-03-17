# 回测系统实战 - 从零搭建

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

**各模块职责：**

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

**数据源选择：**

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
        """
        获取日线数据
        """
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
        """
        获取实时数据
        """
        if self.source == 'akshare':
            df = ak.stock_zh_a_spot_em()
            df = df[df['代码'] == symbol]
            return df

# 使用示例
data_module = DataModule(source='akshare')
df = data_module.get_daily_data('600031', '20250101', '20260307')
print(df.head())
```

---

### 2.2 数据清洗

**清洗流程：**

```python
class DataCleaner:
    def clean_data(self, df):
        """
        数据清洗
        """
        # 1. 检查缺失值
        print(f"缺失值统计：\n{df.isnull().sum()}")
        
        # 2. 填充缺失值
        df = df.fillna(method='ffill')  # 前向填充
        
        # 3. 检查异常值
        df = self.remove_outliers(df)
        
        # 4. 数据类型转换
        df['日期'] = pd.to_datetime(df['日期'])
        df['收盘'] = pd.to_numeric(df['收盘'], errors='coerce')
        
        # 5. 排序
        df = df.sort_values('日期')
        
        # 6. 重置索引
        df = df.reset_index(drop=True)
        
        return df
    
    def remove_outliers(self, df, threshold=3):
        """
        移除异常值（3σ原则）
        """
        for col in ['收盘', '最高', '最低']:
            mean = df[col].mean()
            std = df[col].std()
            
            # 标记异常值
            df[f'{col}_outlier'] = (df[col] - mean).abs() > threshold * std
            
            # 替换异常值
            df.loc[df[f'{col}_outlier'], col] = mean
        
        return df

# 使用示例
cleaner = DataCleaner()
clean_df = cleaner.clean_data(df)
```

---

### 2.3 特征工程

**技术指标计算：**

```python
class FeatureEngineer:
    def calculate_all_indicators(self, df):
        """
        计算所有技术指标
        """
        # 移动平均
        df['MA5'] = df['收盘'].rolling(5).mean()
        df['MA10'] = df['收盘'].rolling(10).mean()
        df['MA20'] = df['收盘'].rolling(20).mean()
        
        # MACD
        df = self.calculate_macd(df)
        
        # KDJ
        df = self.calculate_kdj(df)
        
        # RSI
        df = self.calculate_rsi(df)
        
        # BOLL
        df = self.calculate_bollinger(df)
        
        # 成交量指标
        df['VOL_MA5'] = df['成交量'].rolling(5).mean()
        df['VOL_RATIO'] = df['成交量'] / df['VOL_MA5']
        
        return df
    
    def calculate_macd(self, df, fast=12, slow=26, signal=9):
        """计算MACD"""
        df['EMA12'] = df['收盘'].ewm(span=fast, adjust=False).mean()
        df['EMA26'] = df['收盘'].ewm(span=slow, adjust=False).mean()
        df['DIF'] = df['EMA12'] - df['EMA26']
        df['DEA'] = df['DIF'].ewm(span=signal, adjust=False).mean()
        df['MACD'] = (df['DIF'] - df['DEA']) * 2
        
        return df
    
    def calculate_kdj(self, df, n=9, m=3):
        """计算KDJ"""
        df['LOW_N'] = df['最低'].rolling(n).min()
        df['HIGH_N'] = df['最高'].rolling(n).max()
        
        df['RSV'] = (df['收盘'] - df['LOW_N']) / (df['HIGH_N'] - df['LOW_N']) * 100
        
        df['K'] = df['RSV'].ewm(alpha=1/m, adjust=False).mean()
        df['D'] = df['K'].ewm(alpha=1/m, adjust=False).mean()
        df['J'] = 3 * df['K'] - 2 * df['D']
        
        return df
    
    def calculate_rsi(self, df, period=14):
        """计算RSI"""
        delta = df['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df
    
    def calculate_bollinger(self, df, period=20, std_dev=2):
        """计算布林带"""
        df['BOLL_MID'] = df['收盘'].rolling(period).mean()
        df['BOLL_STD'] = df['收盘'].rolling(period).std()
        df['BOLL_UPPER'] = df['BOLL_MID'] + std_dev * df['BOLL_STD']
        df['BOLL_LOWER'] = df['BOLL_MID'] - std_dev * df['BOLL_STD']
        
        return df

# 使用示例
engineer = FeatureEngineer()
df = engineer.calculate_all_indicators(clean_df)
```

---

## 三、策略模块

### 3.1 策略基类

**定义策略接口：**

```python
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    策略基类
    """
    def __init__(self, params=None):
        self.params = params or {}
    
    @abstractmethod
    def generate_signals(self, df):
        """
        生成交易信号
        必须由子类实现
        
        返回：DataFrame，包含 'signal' 列
        - 1: 买入
        - -1: 卖出
        - 0: 无信号
        """
        pass
    
    def get_name(self):
        """获取策略名称"""
        return self.__class__.__name__
    
    def get_params(self):
        """获取策略参数"""
        return self.params
```

---

### 3.2 双均线策略

```python
class DualMAStrategy(BaseStrategy):
    """
    双均线策略
    """
    def __init__(self, fast_period=10, slow_period=30):
        super().__init__({
            'fast_period': fast_period,
            'slow_period': slow_period
        })
    
    def generate_signals(self, df):
        fast_period = self.params['fast_period']
        slow_period = self.params['slow_period']
        
        # 计算均线
        df['MA_FAST'] = df['收盘'].rolling(fast_period).mean()
        df['MA_SLOW'] = df['收盘'].rolling(slow_period).mean()
        
        # 生成信号
        df['signal'] = 0
        
        # 金叉
        df.loc[(df['MA_FAST'] > df['MA_SLOW']) & 
               (df['MA_FAST'].shift(1) <= df['MA_SLOW'].shift(1)), 'signal'] = 1
        
        # 死叉
        df.loc[(df['MA_FAST'] < df['MA_SLOW']) & 
               (df['MA_FAST'].shift(1) >= df['MA_SLOW'].shift(1)), 'signal'] = -1
        
        return df

# 使用示例
strategy = DualMAStrategy(fast_period=10, slow_period=30)
df = strategy.generate_signals(df)
print(df[df['signal'] != 0][['日期', '收盘', 'signal']].head())
```

---

### 3.3 多因子策略

```python
class MultiFactorStrategy(BaseStrategy):
    """
    多因子策略
    """
    def __init__(self, factors=None):
        super().__init__({'factors': factors})
        self.factors = factors or []
    
    def generate_signals(self, df):
        # 计算各因子得分
        df['score'] = 0
        
        for factor in self.factors:
            df = factor.calculate(df)
            df['score'] += df[factor.name]
        
        # 生成信号
        df['signal'] = 0
        
        # 买入：得分 >= 阈值
        df.loc[df['score'] >= 60, 'signal'] = 1
        
        # 卖出：得分 <= -60
        df.loc[df['score'] <= -60, 'signal'] = -1
        
        return df

class MACDFactor:
    """MACD因子"""
    def __init__(self):
        self.name = 'MACD_SCORE'
    
    def calculate(self, df):
        # 金叉
        df.loc[(df['DIF'] > df['DEA']) & 
               (df['DIF'].shift(1) <= df['DEA'].shift(1)), 'MACD_SCORE'] = 20
        
        # 死叉
        df.loc[(df['DIF'] < df['DEA']) & 
               (df['DIF'].shift(1) >= df['DEA'].shift(1)), 'MACD_SCORE'] = -20
        
        df['MACD_SCORE'] = df['MACD_SCORE'].fillna(0)
        
        return df

class RSIFactor:
    """RSI因子"""
    def __init__(self):
        self.name = 'RSI_SCORE'
    
    def calculate(self, df):
        # 超卖
        df.loc[df['RSI'] < 30, 'RSI_SCORE'] = 20
        
        # 超买
        df.loc[df['RSI'] > 70, 'RSI_SCORE'] = -20
        
        df['RSI_SCORE'] = df['RSI_SCORE'].fillna(0)
        
        return df

# 使用示例
factors = [MACDFactor(), RSIFactor()]
strategy = MultiFactorStrategy(factors=factors)
df = strategy.generate_signals(df)
```

---

## 四、交易模块

### 4.1 交易引擎

```python
class TradingEngine:
    """
    交易引擎
    """
    def __init__(self, initial_capital=100000, commission=0.0003):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.commission = commission  # 手续费率
        self.position = 0  # 持仓数量
        self.trades = []   # 交易记录
        self.portfolio_value = []  # 组合价值
    
    def execute_backtest(self, df):
        """
        执行回测
        """
        for i, row in df.iterrows():
            # 执行信号
            if row['signal'] == 1 and self.position == 0:
                # 买入
                self.buy(row['日期'], row['收盘'], i)
            
            elif row['signal'] == -1 and self.position > 0:
                # 卖出
                self.sell(row['日期'], row['收盘'], i)
            
            # 记录组合价值
            portfolio_value = self.capital + self.position * row['收盘']
            self.portfolio_value.append({
                'date': row['日期'],
                'value': portfolio_value,
                'capital': self.capital,
                'position': self.position,
                'price': row['收盘']
            })
        
        return self.generate_report()
    
    def buy(self, date, price, index):
        """买入"""
        # 计算可买数量
        shares = int(self.capital / price)
        
        # 计算成本
        cost = shares * price
        commission_fee = cost * self.commission
        
        # 执行买入
        self.capital -= (cost + commission_fee)
        self.position = shares
        
        # 记录交易
        self.trades.append({
            'date': date,
            'index': index,
            'action': 'buy',
            'price': price,
            'shares': shares,
            'cost': cost,
            'commission': commission_fee,
            'capital': self.capital
        })
    
    def sell(self, date, price, index):
        """卖出"""
        # 计算收入
        revenue = self.position * price
        commission_fee = revenue * self.commission
        
        # 执行卖出
        self.capital += (revenue - commission_fee)
        
        # 记录交易
        self.trades.append({
            'date': date,
            'index': index,
            'action': 'sell',
            'price': price,
            'shares': self.position,
            'revenue': revenue,
            'commission': commission_fee,
            'capital': self.capital
        })
        
        self.position = 0
    
    def generate_report(self):
        """生成报告"""
        portfolio_df = pd.DataFrame(self.portfolio_value)
        trades_df = pd.DataFrame(self.trades)
        
        # 计算指标
        metrics = self.calculate_metrics(portfolio_df, trades_df)
        
        return {
            'portfolio': portfolio_df,
            'trades': trades_df,
            'metrics': metrics
        }
    
    def calculate_metrics(self, portfolio_df, trades_df):
        """计算回测指标"""
        # 总收益率
        final_value = portfolio_df['value'].iloc[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # 年化收益率
        days = len(portfolio_df)
        annual_return = (1 + total_return) ** (252 / days) - 1
        
        # 最大回撤
        portfolio_df['cummax'] = portfolio_df['value'].cummax()
        portfolio_df['drawdown'] = (portfolio_df['cummax'] - portfolio_df['value']) / portfolio_df['cummax']
        max_drawdown = portfolio_df['drawdown'].max()
        
        # 胜率
        if len(trades_df) >= 2:
            buy_trades = trades_df[trades_df['action'] == 'buy']
            sell_trades = trades_df[trades_df['action'] == 'sell']
            
            profits = []
            for i in range(min(len(buy_trades), len(sell_trades))):
                profit = (sell_trades.iloc[i]['price'] - buy_trades.iloc[i]['price']) / buy_trades.iloc[i]['price']
                profits.append(profit)
            
            win_rate = len([p for p in profits if p > 0]) / len(profits) if profits else 0
        else:
            win_rate = 0
        
        # 夏普比率
        returns = portfolio_df['value'].pct_change().dropna()
        sharpe_ratio = (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'sharpe_ratio': sharpe_ratio,
            'num_trades': len(trades_df) // 2
        }

# 使用示例
engine = TradingEngine(initial_capital=100000, commission=0.0003)
report = engine.execute_backtest(df)

print(f"总收益率：{report['metrics']['total_return']:.2%}")
print(f"年化收益率：{report['metrics']['annual_return']:.2%}")
print(f"最大回撤：{report['metrics']['max_drawdown']:.2%}")
print(f"胜率：{report['metrics']['win_rate']:.2%}")
print(f"夏普比率：{report['metrics']['sharpe_ratio']:.2f}")
print(f"交易次数：{report['metrics']['num_trades']}")
```

---

## 五、完整回测流程

### 5.1 一键回测

```python
class BacktestSystem:
    """
    完整回测系统
    """
    def __init__(self, symbol, start_date, end_date, strategy, initial_capital=100000):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.strategy = strategy
        self.initial_capital = initial_capital
        
        # 初始化各模块
        self.data_module = DataModule(source='akshare')
        self.cleaner = DataCleaner()
        self.engineer = FeatureEngineer()
        self.trading_engine = TradingEngine(initial_capital=initial_capital)
    
    def run(self):
        """
        运行回测
        """
        print(f"开始回测：{self.symbol}")
        print(f"时间范围：{self.start_date} 至 {self.end_date}")
        print(f"策略：{self.strategy.get_name()}")
        print(f"参数：{self.strategy.get_params()}")
        print("-" * 50)
        
        # 1. 获取数据
        print("1. 获取数据...")
        df = self.data_module.get_daily_data(self.symbol, self.start_date, self.end_date)
        
        # 2. 清洗数据
        print("2. 清洗数据...")
        df = self.cleaner.clean_data(df)
        
        # 3. 特征工程
        print("3. 计算技术指标...")
        df = self.engineer.calculate_all_indicators(df)
        
        # 4. 生成信号
        print("4. 生成交易信号...")
        df = self.strategy.generate_signals(df)
        
        # 5. 执行回测
        print("5. 执行回测...")
        report = self.trading_engine.execute_backtest(df)
        
        # 6. 输出报告
        print("6. 生成报告...")
        self.print_report(report)
        
        return report
    
    def print_report(self, report):
        """打印报告"""
        metrics = report['metrics']
        
        print("\n" + "=" * 50)
        print("回测报告")
        print("=" * 50)
        
        print(f"\n【收益指标】")
        print(f"总收益率：{metrics['total_return']:.2%}")
        print(f"年化收益率：{metrics['annual_return']:.2%}")
        
        print(f"\n【风险指标】")
        print(f"最大回撤：{metrics['max_drawdown']:.2%}")
        
        print(f"\n【风险调整收益】")
        print(f"夏普比率：{metrics['sharpe_ratio']:.2f}")
        
        print(f"\n【交易统计】")
        print(f"交易次数：{metrics['num_trades']}")
        print(f"胜率：{metrics['win_rate']:.2%}")
        
        print("\n" + "=" * 50)

# 使用示例
system = BacktestSystem(
    symbol='600031',
    start_date='20250101',
    end_date='20260307',
    strategy=DualMAStrategy(fast_period=10, slow_period=30),
    initial_capital=100000
)

report = system.run()
```

---

## 📝 总结

**回测系统核心：**

| 模块 | 功能 | 关键点 |
|------|------|--------|
| **数据模块** | 获取、清洗数据 | 数据质量决定回测准确性 |
| **策略模块** | 生成交易信号 | 策略逻辑要清晰、可验证 |
| **交易模块** | 执行交易 | 模拟真实交易成本 |
| **报告模块** | 生成报告 | 多维度评估策略 |

**注意事项：**

```
1. 过拟合
   - 参数不要过度优化
   - 留出样本外数据验证

2. 未来函数
   - 不要使用未来数据
   - 确保信号在时间上合理

3. 交易成本
   - 考虑手续费、滑点
   - 影响策略收益

4. 流动性
   - 考虑成交量限制
   - 大单会冲击成本
```

---

_最后更新：2026-03-07 04:20 UTC_
