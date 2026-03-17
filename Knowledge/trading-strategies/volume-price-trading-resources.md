# 量价交易策略 - 实战资源清单

> 创建时间：2026-03-12 21:10 UTC
> 状态：学习资源清单

---

## 🎯 核心学习目标

**量价交易策略的核心**：
1. 成交量确认价格趋势
2. 量价背离预警趋势反转
3. 成交量突破确认趋势强度

---

## 📚 必读论文（英文）

### 1. 经典论文

**"Volume and Price" 系列**
- Gervais, S., Kaniel, R., & Mingelgrin, D. H. (2001)
- "The High-Volume Return Premium"
- 关键发现：高成交量股票未来收益更高

**"Volume and Momentum" 系列**
- Lee, C. M., & Swaminathan, B. (2000)
- "Price Momentum and Trading Volume"
- 关键发现：成交量可以预测动量策略的持续性

**"Volume and Volatility" 系列**
- Gallant, A. R., Rossi, P. E., & Tauchen, G. (1992)
- "Stock Prices and Volume"
- 关键发现：成交量和价格波动的关系

---

## 📚 必读论文（中文）

### 1. 中国市场研究

**"A股量价关系研究"**
- 搜索：中国知网、万方数据
- 关键词：量价关系、成交量、价格动量
- 重点：A股市场的特殊性

**"中国股市成交量研究"**
- 期刊：《金融研究》、《经济研究》
- 重点：A股成交量的预测能力

---

## 💻 实战代码资源

### GitHub 项目

**1. TA-Lib（技术分析库）**
```bash
pip install TA-Lib
```
- 包含：OBV、VPT 等指标
- 文档：https://ta-lib.org

**2. Backtrader（回测框架）**
```bash
pip install backtrader
```
- 支持自定义量价策略
- 文档：https://www.backtrader.com

**3. QuantLib（量化库）**
```bash
pip install QuantLib
```
- 专业量化工具
- 文档：https://www.quantlib.org

---

## 🔍 论坛精华帖

### QuantConnect 论坛

**搜索关键词**：
- volume price strategy
- OBV trading
- volume breakout

**推荐帖子**：
- "Volume Price Analysis in Python"
- "Building a Volume-Based Strategy"
- "Volume Confirmation Strategy"

---

### 雪球精华

**搜索关键词**：
- 量价分析
- OBV 指标
- 成交量选股

**推荐关注**：
- 量化投资话题
- 技术分析话题
- A股实战话题

---

### 集思录精华

**搜索关键词**：
- 量价策略
- 成交量因子
- 量化选股

**推荐关注**：
- 量化投资板块
- 策略分享板块
- 回测报告板块

---

## 📖 经典书籍

### 英文

**1. "Volume Price Analysis" - Anna Coulling**
- Amazon: https://www.amazon.com/dp/B00DGT8M4E
- 重点：基础量价分析

**2. "A Complete Guide to Volume Price Analysis" - Anna Coulling**
- 进阶内容
- 实战案例

**3. "Trading in the Zone" - Mark Douglas**
- 交易心理
- 风险管理

**4. "Technical Analysis of the Financial Markets" - John Murphy**
- 技术分析经典
- 量价章节

---

### 中文

**1. 《量价分析》**
- 翻译版
- 适合入门

**2. 《威科夫操盘法》**
- 经典理论
- 实战应用

**3. 《成交量陷阱》**
- 风险识别
- 反向思维

---

## 🎓 在线课程

### Coursera

**"Financial Markets" - Yale University**
- 包含技术分析模块
- 免费

**"Trading Strategies" - Interactive Brokers**
- 实战策略
- 付费

---

### Udemy

**"Volume Price Analysis Trading"**
- 实战课程
- 付费

**"Technical Analysis Masterclass"**
- 包含量价分析
- 付费

---

## 📊 实战指标公式

### 1. OBV（On-Balance Volume）

```python
def calculate_obv(prices, volumes):
    obv = [0]
    for i in range(1, len(prices)):
        if prices[i] > prices[i-1]:
            obv.append(obv[-1] + volumes[i])
        elif prices[i] < prices[i-1]:
            obv.append(obv[-1] - volumes[i])
        else:
            obv.append(obv[-1])
    return obv
```

---

### 2. VPT（Volume Price Trend）

```python
def calculate_vpt(prices, volumes):
    vpt = [0]
    for i in range(1, len(prices)):
        price_change = (prices[i] - prices[i-1]) / prices[i-1]
        vpt.append(vpt[-1] + volumes[i] * price_change)
    return vpt
```

---

### 3. 成交量加权价格（VWAP）

```python
def calculate_vwap(high, low, close, volume):
    typical_price = (high + low + close) / 3
    vwap = (typical_price * volume).cumsum() / volume.cumsum()
    return vwap
```

---

## 🚀 学习建议

### 阶段 1（1-2周）
- 阅读基础书籍
- 理解 OBV、VPT 指标
- 在雪球、集思录浏览量价分析帖子

### 阶段 2（2-3周）
- 研读经典论文
- 在 QuantConnect 查看代码示例
- 用 Python 实现基础指标

### 阶段 3（3-4周）
- 在三一重工上回测量价策略
- 优化参数
- 实盘小仓位验证

---

## 📝 学习笔记模板

**每次学习后记录**：
```markdown
# 量价策略学习笔记 - [日期]

## 学习内容
- [论文/书籍/论坛帖子名称]

## 核心观点
1. ...
2. ...

## 实战应用
- 如何应用到三一重工交易

## 疑问
- ...

## 下一步
- ...
```

---

## 🎯 最终目标

**4周后能够**：
1. ✅ 理解量价关系的基本原理
2. ✅ 掌握 OBV、VPT 等核心指标
3. ✅ 识别量价背离和突破
4. ✅ 建立自己的量价交易策略
5. ✅ 在三一重工上验证策略

---

_资源清单创建时间：2026-03-12 21:10 UTC_
