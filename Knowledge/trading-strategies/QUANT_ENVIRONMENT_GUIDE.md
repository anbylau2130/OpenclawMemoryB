# 量化交易环境使用指南

> 📅 安装时间: 2026-03-16
> 🎯 已安装: Backtesting.py + Backtrader + Quant-trading

---

## ✅ 已安装项目

| 项目 | 类型 | 位置 | 状态 |
|------|------|------|------|
| **Backtesting.py** | pip 包 | 系统 | ✅ 已安装 |
| **Backtrader** | pip 包 | 系统 | ✅ 已安装 |
| **Quant-trading** | GitHub 仓库 | `projects/quant-trading/` | ✅ 已下载 |

---

## 🚀 快速使用

### 1. Backtesting.py（最简单）

```python
from backtesting import Backtest, Strategy
from backtesting.test import GOOG

class SmaCross(Strategy):
    def init(self):
        self.ma = self.I(lambda x: x.rolling(20).mean(), self.data.Close)
    
    def next(self):
        if self.data.Close > self.ma[-1]:
            self.buy()
        elif self.data.Close < self.ma[-1]:
            self.sell()

bt = Backtest(GOOG, SmaCross, cash=10000)
stats = bt.run()
print(stats)
bt.plot()  # 生成HTML报告
```

**特点：**
- ⭐ 最简单的回测框架
- ⭐ 5分钟上手
- ⭐ 内置示例数据（GOOG）

---

### 2. Backtrader（最专业）

```python
import backtrader as bt

class SmaStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=20)
    
    def next(self):
        if self.data.close > self.sma[0]:
            self.buy()
        elif self.data.close < self.sma[0]:
            self.sell()

cerebro = bt.Cerebro()
cerebro.addstrategy(SmaStrategy)

# 添加数据
data = bt.feeds.YahooFinanceData(dataname='AAPL', fromdate=datetime(2020,1,1))
cerebro.adddata(data)

# 运行回测
cerebro.run()
cerebro.plot()
```

**特点：**
- ⭐ 最专业的回测框架
- ⭐ 丰富的技术指标
- ⭐ 参数优化功能
- ⭐ 多策略组合

---

### 3. Quant-trading（策略最丰富）

**位置：** `/root/.openclaw/workspace/projects/quant-trading/`

**包含策略（15+）：**

| 策略文件 | 策略名称 | 类型 |
|---------|---------|------|
| MACD Oscillator backtest.py | MACD | 趋势跟踪 |
| RSI Pattern Recognition backtest.py | RSI | 均值回归 |
| Bollinger Bands Pattern Recognition backtest.py | 布林带 | 均值回归 |
| Pair trading backtest.py | 配对交易 | 统计套利 |
| Dual Thrust backtest.py | 双重推力 | 日内突破 |
| Heikin-Ashi backtest.py | 平均K线 | 趋势跟踪 |
| London Breakout backtest.py | 伦敦突破 | 日内突破 |
| Awesome Oscillator backtest.py | 动量指标 | 趋势跟踪 |
| Parabolic SAR backtest.py | 抛物线转向 | 趋势跟踪 |
| Shooting Star backtest.py | 射击之星 | 形态识别 |
| Options Straddle backtest.py | 期权跨式 | 期权策略 |

**使用方式：**

```bash
cd /root/.openclaw/workspace/projects/quant-trading
python3 "MACD Oscillator backtest.py"
```

---

## 📊 对比选择

| 需求 | 推荐 | 原因 |
|------|------|------|
| 快速验证策略 | Backtesting.py | 最简单 |
| 学习策略代码 | Quant-trading | 策略丰富 |
| 专业回测优化 | Backtrader | 功能强大 |
| 多策略组合 | Backtrader | 支持好 |

---

## 🎯 使用示例

### 在 OpenClaw 中使用

**方式1：直接运行 Python 代码**

```python
# 在对话中直接让 OpenClaw 执行
from backtesting import Backtest, Strategy
from backtesting.test import GOOG

class MyStrategy(Strategy):
    def init(self):
        pass
    def next(self):
        pass

bt = Backtest(GOOG, MyStrategy, cash=10000)
print(bt.run())
```

**方式2：运行 Quant-trading 策略**

```bash
# OpenClaw 执行 shell 命令
cd /root/.openclaw/workspace/projects/quant-trading
python3 "MACD Oscillator backtest.py"
```

**方式3：让 OpenClaw 帮你回测**

```
用户: 用 Backtesting.py 帮我回测三一重工的MACD策略
OpenClaw: [自动获取数据，编写代码，运行回测，输出结果]
```

---

## 📁 文件位置

```
/root/.openclaw/workspace/
├── projects/
│   └── quant-trading/          # GitHub 策略库（26个文件）
│       ├── MACD Oscillator backtest.py
│       ├── RSI Pattern Recognition backtest.py
│       ├── Pair trading backtest.py
│       └── ...
└── Knowledge/
    └── trading-strategies/
        ├── OPENCLAW_COMPATIBLE_PROJECTS.md  # 项目说明
        └── code/                            # 本地策略代码（28个）
```

---

## 🔧 依赖说明

**已安装的 Python 包：**

| 包名 | 版本 | 用途 |
|------|------|------|
| backtesting | latest | 回测框架 |
| backtrader | latest | 回测框架 |
| pandas | latest | 数据处理 |
| numpy | latest | 数值计算 |
| matplotlib | latest | 可视化 |
| yfinance | latest | Yahoo 数据 |

---

## 💡 常见问题

### Q1: 如何获取A股数据？

```python
import yfinance as yf

# 三一重工
stock = yf.Ticker("600031.SS")
data = stock.history(period="1y")
```

### Q2: 如何保存回测结果？

```python
# Backtesting.py
stats = bt.run()
stats.to_csv('backtest_results.csv')

# 生成HTML报告
bt.plot(filename='report.html')
```

### Q3: 如何添加自定义指标？

```python
# Backtesting.py
def my_indicator(close):
    return close.rolling(20).mean()

class MyStrategy(Strategy):
    def init(self):
        self.my_ma = self.I(my_indicator, self.data.Close)
```

---

## 🎓 学习路径

### 第1周：Backtesting.py
- ✅ 运行内置示例
- ✅ 修改参数
- ✅ 添加自定义指标

### 第2周：Quant-trading
- ✅ 阅读 MACD 策略代码
- ✅ 理解策略逻辑
- ✅ 修改并运行

### 第3周：Backtrader
- ✅ 学习 Cerebro 架构
- ✅ 添加多个指标
- ✅ 参数优化

---

*安装时间: 2026-03-16*
*维护者: 小秘*
