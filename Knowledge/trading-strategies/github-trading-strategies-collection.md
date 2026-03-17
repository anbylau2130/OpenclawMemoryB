# GitHub 交易策略学习资源汇总

> 创建时间：2026-03-12 21:15 UTC
> 来源：GitHub 热门仓库
> 目标：自主学习并整理到知识库

---

## 🎯 精选仓库（按推荐度排序）

### ⭐⭐⭐⭐⭐ 强烈推荐

#### 1. je-suis-tm/quant-trading（9385 stars）
**语言**：Python
**URL**：https://github.com/je-suis-tm/quant-trading

**包含策略**：
- VIX Calculator（波动率指数）
- Pattern Recognition（形态识别）
- Commodity Trading Advisor（商品交易顾问）
- Monte Carlo（蒙特卡洛模拟）
- Options Straddle（期权跨式）
- Shooting Star（射击之星）
- London Breakout（伦敦突破）
- Heikin-Ashi（平均K线）
- Pair Trading（配对交易）
- RSI（相对强弱指标）
- Bollinger Bands（布林带）
- Parabolic SAR（抛物线转向）
- Dual Thrust（双重推力）
- Awesome（动量指标）
- MACD（指数平滑异同移动平均线）

**推荐理由**：
- ✅ 策略丰富（15+种）
- ✅ Python 实现
- ✅ 代码质量高
- ✅ 有详细文档

**学习重点**：
1. **量价相关策略**：
   - Pattern Recognition（形态识别）
   - Pair Trading（配对交易）
   - Heikin-Ashi（平均K线）

2. **趋势跟踪策略**：
   - MACD
   - Bollinger Bands
   - Parabolic SAR

---

#### 2. mementum/backtrader（20707 stars）
**语言**：Python
**URL**：https://github.com/mementum/backtrader

**功能**：
- Python 回测库
- 支持多种数据源
- 内置技术指标
- 策略优化工具
- 可视化分析

**推荐理由**：
- ✅ 最流行的回测框架
- ✅ 功能完整
- ✅ 社区活跃
- ✅ 文档详细

**学习重点**：
1. 回测量价策略
2. 自定义指标
3. 参数优化
4. 风险管理

---

#### 3. kernc/backtesting.py（8035 stars）
**语言**：Python
**URL**：https://github.com/kernc/backtesting.py

**功能**：
- 轻量级回测框架
- 快速回测
- 内置指标
- 可视化报告

**推荐理由**：
- ✅ 简单易用
- ✅ 适合初学者
- ✅ 快速验证策略

**学习重点**：
1. 快速原型验证
2. 策略回测
3. 性能分析

---

### ⭐⭐⭐⭐ 推荐

#### 4. StockSharp/StockSharp（9253 stars）
**语言**：C#
**URL**：https://github.com/StockSharp/StockSharp

**功能**：
- 算法交易平台
- 支持多市场（股票、外汇、加密货币）
- 实时交易
- 策略开发

**推荐理由**：
- ✅ 完整的交易平台
- ✅ 实时交易支持
- ✅ 多市场支持

**学习重点**：
1. 交易系统架构
2. 实时数据处理
3. 订单管理

---

#### 5. TradeMaster-NTU/TradeMaster（2523 stars）
**语言**：Jupyter Notebook
**URL**：https://github.com/TradeMaster-NTU/TradeMaster

**功能**：
- 强化学习交易平台
- AI 驱动的交易
- 策略研究

**推荐理由**：
- ✅ AI/ML 集成
- ✅ 学术研究
- ✅ 前沿技术

**学习重点**：
1. 强化学习在交易中的应用
2. AI 策略开发
3. 策略评估

---

### ⭐⭐⭐ 值得关注

#### 6. fmzquant/strategies（5100 stars）
**语言**：多语言
**URL**：https://github.com/fmzquant/strategies

**功能**：
- 多语言策略（JavaScript, Python, C++）
- 量化交易策略集合
- 社区贡献

**推荐理由**：
- ✅ 策略多样
- ✅ 多语言支持
- ✅ 社区活跃

---

#### 7. cuemacro/finmarketpy（3717 stars）
**语言**：Python
**URL**：https://github.com/cuemacro/finmarketpy

**功能**：
- 回测交易策略
- 金融市场分析
- 数据可视化

**推荐理由**：
- ✅ 专业工具
- ✅ 金融分析
- ✅ 可视化强

---

## 📚 学习路径

### 阶段 1：基础（1-2周）

**学习内容**：
1. **Backtrader 入门**
   - 安装和配置
   - 基本回测
   - 内置指标

2. **Backtesting.py 入门**
   - 快速回测
   - 策略验证

**实践**：
```python
# 安装
pip install backtrader
pip install backtesting

# 简单回测
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

class SmaCross(Strategy):
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 10)
        self.ma2 = self.I(SMA, price, 20)
    
    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()
```

---

### 阶段 2：策略学习（2-3周）

**学习内容**：
1. **je-suis-tm/quant-trading**
   - 阅读代码
   - 理解策略逻辑
   - 运行示例

2. **重点策略**：
   - Pattern Recognition（形态识别）
   - Pair Trading（配对交易）
   - RSI 策略
   - Bollinger Bands 策略

**实践**：
```bash
# 克隆仓库
git clone https://github.com/je-suis-tm/quant-trading.git
cd quant-trading

# 安装依赖
pip install -r requirements.txt

# 运行示例
python pattern_recognition.py
```

---

### 阶段 3：实战应用（3-4周）

**学习内容**：
1. **在三一重工上验证**
   - 获取历史数据
   - 回测量价策略
   - 优化参数

2. **构建自己的策略**
   - 组合多个指标
   - 添加风控规则
   - 回测验证

**实践**：
```python
# 量价策略示例
class VolumePriceStrategy(Strategy):
    def init(self):
        self.obv = self.I(OBV, self.data.Close, self.data.Volume)
        self.sma_volume = self.I(SMA, self.data.Volume, 20)
    
    def next(self):
        # 量价配合
        if (self.data.Close > self.data.Close[-1] and 
            self.data.Volume > self.sma_volume):
            self.buy()
        # 量价背离
        elif (self.data.Close > self.data.Close[-1] and 
              self.data.Volume < self.sma_volume):
            if self.position:
                self.sell()
```

---

## 🔍 重点关注：量价相关策略

### 1. Pattern Recognition（形态识别）
**仓库**：je-suis-tm/quant-trading
**文件**：pattern_recognition.py
**重点**：
- K线形态识别
- 成交量确认
- 趋势判断

---

### 2. Pair Trading（配对交易）
**仓库**：je-suis-tm/quant-trading
**文件**：pair_trading.py
**重点**：
- 相关性分析
- 价差交易
- 均值回归

---

### 3. OBV 指标
**实现**：
```python
def OBV(close, volume):
    obv = [0]
    for i in range(1, len(close)):
        if close[i] > close[i-1]:
            obv.append(obv[-1] + volume[i])
        elif close[i] < close[i-1]:
            obv.append(obv[-1] - volume[i])
        else:
            obv.append(obv[-1])
    return obv
```

---

### 4. Volume Profile（成交量分布）
**实现**：
```python
def volume_profile(price, volume, bins=50):
    """
    计算成交量分布
    """
    price_range = np.linspace(min(price), max(price), bins)
    volume_dist = np.zeros(bins)
    
    for p, v in zip(price, volume):
        idx = np.searchsorted(price_range, p)
        volume_dist[idx] += v
    
    return price_range, volume_dist
```

---

## 💡 实战建议

### 1. 从简单开始
- ✅ 先学习 Backtesting.py（简单）
- ✅ 再学习 Backtrader（功能强）
- ✅ 最后研究 quant-trading（策略丰富）

---

### 2. 重点关注量价策略
**推荐仓库**：
- je-suis-tm/quant-trading
  - Pattern Recognition
  - Pair Trading
  - Heikin-Ashi

---

### 3. 在三一重工上验证
**步骤**：
1. 获取历史数据（Tushare/Yahoo Finance）
2. 实现量价策略
3. 回测验证
4. 优化参数
5. 小仓位实盘

---

## 📊 学习进度追踪

### 第 1 周
- [ ] 安装 Backtrader 和 Backtesting.py
- [ ] 运行简单回测示例
- [ ] 理解回测框架基础

### 第 2 周
- [ ] 克隆 je-suis-tm/quant-trading
- [ ] 阅读 Pattern Recognition 代码
- [ ] 理解量价形态识别

### 第 3 周
- [ ] 在三一重工上回测量价策略
- [ ] 优化参数
- [ ] 分析回测结果

### 第 4 周
- [ ] 构建自己的量价策略
- [ ] 组合多个指标
- [ ] 添加风险管理规则

---

## 🔗 快速链接

### GitHub 仓库
1. quant-trading: https://github.com/je-suis-tm/quant-trading
2. backtrader: https://github.com/mementum/backtrader
3. backtesting.py: https://github.com/kernc/backtesting.py
4. StockSharp: https://github.com/StockSharp/StockSharp
5. TradeMaster: https://github.com/TradeMaster-NTU/TradeMaster

### 文档
- Backtrader 文档: https://www.backtrader.com
- Backtesting.py 文档: https://kernc.github.io/backtesting.py

---

## 📝 学习笔记模板

```markdown
# GitHub 策略学习笔记 - [仓库名称]

## 学习时间
- 日期：YYYY-MM-DD
- 时长：X 小时

## 学习内容
- 文件：xxx.py
- 策略：XXX

## 核心代码
```python
# 关键代码片段
```

## 理解要点
1. ...
2. ...

## 实战应用
- 如何应用到三一重工

## 疑问
- ...

## 下一步
- ...
```

---

## 🎯 总结

### 最值得学习的仓库
1. **je-suis-tm/quant-trading**（策略丰富）
2. **mementum/backtrader**（回测框架）
3. **kernc/backtesting.py**（快速验证）

### 学习重点
1. 量价策略（Pattern Recognition, Pair Trading）
2. 回测框架（Backtrader）
3. 实战应用（三一重工）

### 4周目标
1. ✅ 掌握回测框架
2. ✅ 理解量价策略
3. ✅ 在三一重工上验证
4. ✅ 构建自己的策略

---

_资源汇总创建时间：2026-03-12 21:15 UTC_
_学习资源已整理到知识库_
