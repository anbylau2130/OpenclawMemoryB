# 量化交易工具使用指南

> 📅 创建时间: 2026-03-16
> 🎯 快速上手 Backtesting.py + Backtrader + Quant-trading

---

## 🎯 快速选择

| 你想做什么 | 用哪个 | 看哪节 |
|-----------|--------|--------|
| 5分钟验证策略 | Backtesting.py | 第1节 |
| 学习经典策略 | Quant-trading | 第2节 |
| 专业回测优化 | Backtrader | 第3节 |

---

## 1️⃣ Backtesting.py（最简单）

### 基础用法

```python
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG, SMA

class SmaCross(Strategy):
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 10)  # 快线
        self.ma2 = self.I(SMA, price, 20)  # 慢线
    
    def next(self):
        # 金叉买入
        if crossover(self.ma1, self.ma2):
            if not self.position:
                self.buy()
        # 死叉卖出
        elif crossover(self.ma2, self.ma1):
            if self.position:
                self.sell()

# 运行回测
bt = Backtest(GOOG, SmaCross, cash=10000, commission=.002)
stats = bt.run()
print(stats)

# 生成HTML报告
bt.plot(filename='report.html')
```

### 使用A股数据

```python
import yfinance as yf
from backtesting import Backtest

# 获取三一重工数据
stock = yf.Ticker("600031.SS")
data = stock.history(period="2y")

# 转换为 Backtesting 格式
data = data[['Open', 'High', 'Low', 'Close', 'Volume']]

# 运行回测
bt = Backtest(data, SmaCross, cash=100000)
stats = bt.run()
```

### 常用指标

```python
from backtesting.lib import SMA, EMA, RSI, MACD, BollingerBands

class MyStrategy(Strategy):
    def init(self):
        # 移动平均
        self.sma = self.I(SMA, self.data.Close, 20)
        self.ema = self.I(EMA, self.data.Close, 20)
        
        # RSI
        self.rsi = self.I(RSI, self.data.Close, 14)
        
        # MACD
        self.macd = self.I(MACD, self.data.Close)
        
        # 布林带
        self.bb = self.I(BollingerBands, self.data.Close, 20)
    
    def next(self):
        # RSI 超卖买入
        if self.rsi[-1] < 30:
            self.buy()
        # RSI 超买卖出
        elif self.rsi[-1] > 70:
            self.sell()
```

---

## 2️⃣ Quant-trading（策略库）

### 位置
```
/root/.openclaw/workspace/projects/quant-trading/
```

### 可用策略

| 文件名 | 策略 | 说明 |
|--------|------|------|
| `MACD Oscillator backtest.py` | MACD | 趋势跟踪 |
| `RSI Pattern Recognition backtest.py` | RSI | 均值回归 |
| `Bollinger Bands Pattern Recognition backtest.py` | 布林带 | 波动率 |
| `Pair trading backtest.py` | 配对交易 | 统计套利 |
| `Dual Thrust backtest.py` | 双重推力 | 日内突破 |
| `Heikin-Ashi backtest.py` | 平均K线 | 趋势过滤 |
| `London Breakout backtest.py` | 伦敦突破 | 时段突破 |
| `Options Straddle backtest.py` | 期权跨式 | 波动率交易 |

### 运行方式

**方法1：直接运行**
```bash
cd /root/.openclaw/workspace/projects/quant-trading
python3 "MACD Oscillator backtest.py"
```

**方法2：在代码中引用**
```python
import sys
sys.path.append('/root/.openclaw/workspace/projects/quant-trading')

# 导入策略模块
from macd_oscillator import MACDStrategy
```

### 学习策略代码

```bash
# 查看策略代码
cat "MACD Oscillator backtest.py"

# 或在 OpenClaw 中
read: projects/quant-trading/MACD Oscillator backtest.py
```

---

## 3️⃣ Backtrader（专业框架）

### 基础用法

```python
import backtrader as bt
from datetime import datetime

# 1. 创建策略
class SmaStrategy(bt.Strategy):
    params = (('period', 20),)
    
    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.period)
    
    def next(self):
        if not self.position:
            if self.data.close > self.sma[0]:
                self.buy()
        else:
            if self.data.close < self.sma[0]:
                self.sell()

# 2. 创建引擎
cerebro = bt.Cerebro()
cerebro.addstrategy(SmaStrategy)

# 3. 添加数据
data = bt.feeds.YahooFinanceData(
    dataname='AAPL',
    fromdate=datetime(2020, 1, 1),
    todate=datetime(2020, 12, 31)
)
cerebro.adddata(data)

# 4. 设置资金
cerebro.broker.setcash(100000)

# 5. 运行回测
cerebro.run()

# 6. 查看结果
print(f'最终资金: {cerebro.broker.getvalue():.2f}')

# 7. 绘图
cerebro.plot()
```

### 参数优化

```python
# 添加多个参数组合
cerebro.optstrategy(
    SmaStrategy,
    period=[10, 20, 30, 40]
)

# 运行优化
results = cerebro.run()

# 查看最佳参数
for result in results:
    print(f"Period: {result[0].params.period}, "
          f"Value: {result[0].broker.getvalue()}")
```

### 多策略组合

```python
# 添加多个策略
cerebro.addstrategy(SmaStrategy, period=20)
cerebro.addstrategy(RsiStrategy, period=14)

# 运行
cerebro.run()
```

### 内置指标

```python
class MyStrategy(bt.Strategy):
    def __init__(self):
        # 移动平均
        self.sma = bt.indicators.SMA(self.data.close, period=20)
        self.ema = bt.indicators.EMA(self.data.close, period=20)
        
        # MACD
        self.macd = bt.indicators.MACD(self.data.close)
        
        # RSI
        self.rsi = bt.indicators.RSI(self.data.close, period=14)
        
        # 布林带
        self.bb = bt.indicators.BollingerBands(self.data.close)
        
        # ATR
        self.atr = bt.indicators.ATR(self.data, period=14)
```

---

## 📊 实战示例

### 示例1：回测三一重工MACD策略

```python
# 在 OpenClaw 中直接运行
import yfinance as yf
from backtesting import Backtest, Strategy
from backtesting.lib import MACD, crossover

class MACDStrategy(Strategy):
    def init(self):
        self.macd, self.signal = self.I(MACD, self.data.Close)
    
    def next(self):
        if crossover(self.macd, self.signal):
            if not self.position:
                self.buy()
        elif crossover(self.signal, self.macd):
            if self.position:
                self.sell()

# 获取数据
stock = yf.Ticker("600031.SS")
data = stock.history(period="2y")

# 运行回测
bt = Backtest(data, MACDStrategy, cash=100000, commission=.001)
stats = bt.run()
print(stats)
```

### 示例2：多策略组合

```python
from backtesting import Backtest, Strategy
from backtesting.lib import SMA, RSI, BollingerBands

class MultiIndicatorStrategy(Strategy):
    def init(self):
        # 趋势指标
        self.sma = self.I(SMA, self.data.Close, 20)
        # 震荡指标
        self.rsi = self.I(RSI, self.data.Close, 14)
        # 波动率指标
        self.bb = self.I(BollingerBands, self.data.Close, 20)
    
    def next(self):
        # 多重确认
        if (self.data.Close > self.sma[-1] and      # 趋势向上
            self.rsi[-1] < 70 and                    # RSI不超买
            self.data.Close < self.bb[-1].mid):      # 价格在中轨下方
            if not self.position:
                self.buy()
        
        # 卖出条件
        elif (self.rsi[-1] > 70 or                   # RSI超买
              self.data.Close > self.bb[-1].upper):  # 突破上轨
            if self.position:
                self.sell()
```

---

## 🔧 常见问题

### Q1: 如何获取A股数据？

```python
import yfinance as yf

# A股代码格式：代码.SS（上交所）或 代码.SZ（深交所）
# 三一重工：600031.SS
# 平安银行：000001.SZ

stock = yf.Ticker("600031.SS")
data = stock.history(period="2y")
```

### Q2: 如何保存回测结果？

```python
# Backtesting.py
stats = bt.run()

# 保存为CSV
stats.to_csv('backtest_results.csv')

# 生成HTML报告
bt.plot(filename='report.html')
```

### Q3: 如何添加止损止盈？

```python
class StrategyWithStop(Strategy):
    def next(self):
        if not self.position:
            self.buy()
            # 设置止损止盈
            self.sl = self.sell(
                stop=self.data.Close * 0.97,  # -3%止损
                limit=self.data.Close * 1.05  # +5%止盈
            )
```

### Q4: 如何查看策略参数？

```python
# Backtesting.py
stats = bt.run()
print(stats['_strategy'])  # 查看策略参数

# Backtrader
cerebro.addstrategy(MyStrategy, period=20)
# 通过 params 设置
```

---

## 📁 相关文件

| 文件 | 位置 | 说明 |
|------|------|------|
| 策略库 | `projects/quant-trading/` | 26个策略文件 |
| 本地策略 | `Knowledge/trading-strategies/code/` | 28个策略代码 |
| 使用指南 | `Knowledge/trading-strategies/QUANT_ENVIRONMENT_GUIDE.md` | 环境说明 |
| 项目对比 | `Knowledge/trading-strategies/OPENCLAW_COMPATIBLE_PROJECTS.md` | 项目对比 |

---

## 💡 学习建议

### 第1周：Backtesting.py
- ✅ 运行上面的示例代码
- ✅ 修改参数观察结果
- ✅ 添加自己的指标

### 第2周：Quant-trading
- ✅ 阅读 MACD 策略代码
- ✅ 理解策略逻辑
- ✅ 修改并运行

### 第3周：Backtrader
- ✅ 学习基础用法
- ✅ 尝试参数优化
- ✅ 组合多个策略

---

## 🎯 快速命令

```bash
# 在 OpenClaw 中执行

# 查看策略列表
ls projects/quant-trading/*.py

# 运行回测
python3 -c "from backtesting import Backtest; ..."

# 查看策略代码
cat projects/quant-trading/MACD*.py
```

---

*创建时间: 2026-03-16*
*维护者: 小秘*
