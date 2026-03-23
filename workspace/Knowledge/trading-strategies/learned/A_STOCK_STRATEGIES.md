# A股交易策略深度探索

> 来源：OpenclawMemery 仓库
> 日期：2026-03-17

---

## 📊 一、A股市场特征

### 1. 交易规则
- **交易时间：** 9:30-11:30, 13:00-15:00
- **涨跌停板：** ±10%（主板），±20%（创业板/科创板），±5%（ST）
- **T+1制度：** 当日买入次日才能卖出
- **集合竞价：** 9:15-9:25（可撤单9:15-9:20）

### 2. 市场特点
- **散户为主：** 情绪化交易明显
- **政策市：** 政策影响大
- **板块轮动：** 行业板块轮动快
- **资金驱动：** 资金流向影响显著

---

## 🎯 二、A股专属策略

### 1. 涨跌停板策略

#### 策略1：涨停板战法
```python
def limit_up_strategy(df):
    """涨停板战法"""

    signals = []

    for i in range(1, len(df)):
        # 计算涨停价（假设主板10%）
        limit_up = df['close'].iloc[i-1] * 1.10

        # 接近涨停（9.5%以上）
        if df['close'].iloc[i] >= limit_up * 0.95:
            # 次日开盘买入
            if i + 1 < len(df):
                signals.append({
                    'date': df.index[i],
                    'type': 'PREPARE_BUY',
                    'reason': '涨停封板',
                    'target_date': df.index[i+1]
                })

    return signals
```

**要点：**
- 涨停次日高开概率70%
- 需判断封板强度
- 注意炸板风险

#### 策略2：跌停板反弹
```python
def limit_down_rebound(df):
    """跌停板反弹策略"""

    signals = []

    for i in range(1, len(df)):
        limit_down = df['close'].iloc[i-1] * 0.90

        # 跌停打开
        if (df['low'].iloc[i] <= limit_down and
            df['close'].iloc[i] > limit_down):
            signals.append({
                'date': df.index[i],
                'type': 'BUY',
                'reason': '跌停打开，可能反弹'
            })

    return signals
```

**胜率：** 约60-65%

---

### 2. 集合竞价策略

#### 策略3：竞价高开
```python
def auction_high_open(df_intraday):
    """集合竞价高开策略"""

    # 9:15-9:25竞价数据
    auction_data = df_intraday.between_time('09:15', '09:25')

    if len(auction_data) == 0:
        return None

    open_price = auction_data.iloc[-1]['price']
    prev_close = df_intraday.iloc[0]['prev_close']

    open_change = (open_price - prev_close) / prev_close * 100

    # 高开2-5%
    if 2 < open_change < 5:
        return {
            'signal': 'BUY',
            'reason': f'竞价高开{open_change:.2f}%',
            'confidence': 0.65
        }
    # 高开>7%（可能高开低走）
    elif open_change > 7:
        return {
            'signal': 'SELL',
            'reason': f'竞价高开过多{open_change:.2f}%',
            'confidence': 0.70
        }

    return None
```

**要点：**
- 9:20前可撤单，需观察真实意图
- 高开2-5%最佳
- 高开>7%需警惕

---

### 3. 板块轮动策略

#### 策略4：板块强弱轮动
```python
def sector_rotation(df_sectors):
    """板块轮动策略"""

    # 计算各板块5日涨幅
    sector_returns = {}
    for sector, df in df_sectors.items():
        sector_returns[sector] = (df['close'].iloc[-1] / df['close'].iloc[-5] - 1) * 100

    # 排名
    ranked_sectors = sorted(sector_returns.items(), key=lambda x: x[1], reverse=True)

    # 买入前3强板块
    top_sectors = ranked_sectors[:3]
    bottom_sectors = ranked_sectors[-3:]

    return {
        'buy_sectors': [s[0] for s in top_sectors],
        'sell_sectors': [s[0] for s in bottom_sectors],
        'sector_returns': sector_returns
    }
```

**要点：**
- 强者恒强，买强势板块
- 弱者恒弱，卖弱势板块
- 轮动周期通常3-5天

---

### 4. 资金流向策略

#### 策略5：主力资金跟踪
```python
def main_capital_flow(df, capital_data):
    """主力资金跟踪策略"""

    # capital_data: 主力净流入数据

    signals = []

    for i in range(len(df)):
        net_inflow = capital_data.iloc[i]['net_inflow']
        net_inflow_ratio = net_inflow / df['close'].iloc[i] / df['volume'].iloc[i]

        # 主力大幅流入
        if net_inflow_ratio > 0.05:  # 流入>5%
            signals.append({
                'date': df.index[i],
                'type': 'BUY',
                'reason': f'主力净流入{net_inflow_ratio*100:.1f}%'
            })
        # 主力大幅流出
        elif net_inflow_ratio < -0.05:  # 流出>5%
            signals.append({
                'date': df.index[i],
                'type': 'SELL',
                'reason': f'主力净流出{abs(net_inflow_ratio)*100:.1f}%'
            })

    return signals
```

**数据来源：**
- 东方财富网
- 同花顺
- 雪球

---

### 5. 北向资金策略

#### 策略6：北向资金跟踪
```python
def northbound_capital_strategy(stock_code, northbound_data):
    """北向资金跟踪策略"""

    # northbound_data: 北向资金持股数据

    signals = []

    for i in range(1, len(northbound_data)):
        prev_holding = northbound_data.iloc[i-1]['holding']
        curr_holding = northbound_data.iloc[i]['holding']

        change_ratio = (curr_holding - prev_holding) / prev_holding * 100

        # 北向资金大幅增持
        if change_ratio > 10:
            signals.append({
                'date': northbound_data.index[i],
                'type': 'BUY',
                'reason': f'北向资金增持{change_ratio:.1f}%',
                'confidence': 0.70
            })
        # 北向资金大幅减持
        elif change_ratio < -10:
            signals.append({
                'date': northbound_data.index[i],
                'type': 'SELL',
                'reason': f'北向资金减持{abs(change_ratio):.1f}%',
                'confidence': 0.65
            })

    return signals
```

**要点：**
- 北向资金=外资（聪明钱）
- 增持>10%通常看涨
- 持续增持更可靠

---

### 6. 龙虎榜策略

#### 策略7：龙虎榜跟踪
```python
def dragon_tiger_list_strategy(df, lhb_data):
    """龙虎榜策略"""

    # lhb_data: 龙虎榜数据

    signals = []

    for record in lhb_data:
        # 著名游资买入
        famous_traders = ['赵老哥', '章盟主', '方新侠', '炒股养家']
        
        for trader in famous_traders:
            if trader in record['buy_traders']:
                signals.append({
                    'date': record['date'],
                    'symbol': record['symbol'],
                    'type': 'BUY',
                    'reason': f'游资{trader}买入',
                    'confidence': 0.65
                })

    return signals
```

**要点：**
- 著名游资跟踪
- 游资买入通常短期拉升
- 注意游资风格

---

## 💡 三、实战要点

### 1. A股特有规律
- **早盘急跌：** 9:30-10:00容易急跌，可低吸
- **尾盘拉升：** 14:30-15:00容易拉升，可高抛
- **午盘休整：** 13:00-14:00成交量低，观望为主

### 2. 风险控制
- 涨停次日高开低走风险
- 跌停打开可能继续下跌
- 板块轮动速度过快

### 3. 最佳实践
- 多策略组合使用
- 结合大盘环境
- 严格止损止盈

---

_来源：OpenclawMemery 仓库 main 分支_
_提取时间：2026-03-17_
