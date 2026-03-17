#!/usr/bin/env python3
"""
Backtrader回测系统 - 多因子策略V3
=====================================
使用Backtrader框架回测我们的优化策略
数据保存: /root/.openclaw/workspace/data/backtest/
"""

import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

# 回测数据保存路径
BACKTEST_DATA_DIR = "/root/.openclaw/workspace/data/backtest"


# ============================================================
# 一、策略定义
# ============================================================

class MultiFactorStrategyV3(bt.Strategy):
    """
    多因子策略V3 - Backtrader版本
    
    因子:
    - VWAP: +2分 (胜率92%)
    - 布林带下轨: +1分 (胜率71%)
    - 均线多头: +2分
    - 站上MA5: +1分
    - 放量: +1分
    - MACD: +0.5分 (降权)
    - RSI超卖: +1分
    """
    
    params = (
        ('min_score', 3.0),      # 买入阈值（降低以增加交易）
        ('stop_loss', 0.04),     # 止损4%
        ('take_profit', 0.10),   # 止盈10%
        ('hold_days', 5),        # 持有天数
    )
    
    def __init__(self):
        # 技术指标
        self.ma5 = bt.indicators.SMA(self.data.close, period=5)
        self.ma10 = bt.indicators.SMA(self.data.close, period=10)
        self.ma20 = bt.indicators.SMA(self.data.close, period=20)
        
        # VWAP
        self.vwap = bt.indicators.WeightedMovingAverage(
            self.data.close * self.data.volume, 
            period=20
        ) / bt.indicators.WeightedMovingAverage(self.data.volume, period=20)
        
        # 布林带
        self.bollinger = bt.indicators.BollingerBands(self.data.close, period=20)
        
        # RSI
        self.rsi = bt.indicators.RSI(self.data.close, period=14)
        
        # MACD
        self.macd = bt.indicators.MACD(self.data.close)
        
        # 成交量均线
        self.vol_ma20 = bt.indicators.SMA(self.data.volume, period=20)
        
        # 交易状态
        self.order = None
        self.buy_price = None
        self.buy_date = None
        self.score = 0
        
        # 记录交易
        self.trades = []
    
    def calculate_score(self):
        """计算多因子得分"""
        score = 0.0
        signals = []
        
        # 1. VWAP因子（胜率92%）
        if self.data.close[0] < self.vwap[0] * 0.98:
            score += 2
            signals.append("VWAP买入")
        
        # 2. 布林带下轨（胜率71%）
        if self.data.close[0] <= self.bollinger.lines.bot[0] * 1.01:
            score += 1
            signals.append("布林下轨")
        
        # 3. 均线多头
        if self.ma5[0] > self.ma10[0] > self.ma20[0]:
            score += 2
            signals.append("均线多头")
        
        # 4. 站上MA5
        if self.data.close[0] > self.ma5[0]:
            score += 1
            signals.append("站上MA5")
        
        # 5. 放量
        vol_ratio = self.data.volume[0] / self.vol_ma20[0] if self.vol_ma20[0] > 0 else 1
        if vol_ratio > 1.5:
            score += 1
            signals.append(f"放量({vol_ratio:.1f})")
        
        # 6. MACD金叉（降权）
        if self.macd.lines.macd[0] > self.macd.lines.signal[0]:
            score += 0.5
            signals.append("MACD金叉")
        
        # 7. RSI超卖
        if self.rsi[0] < 30:
            score += 1
            signals.append(f"RSI超卖({self.rsi[0]:.0f})")
        
        self.score = score
        return score, signals
    
    def next(self):
        # 有持仓时检查卖出
        if self.position and self.buy_date:
            hold_days = (self.data.datetime.date(0) - self.buy_date).days
            pnl_pct = (self.data.close[0] - self.buy_price) / self.buy_price
            
            # 卖出条件
            if hold_days >= self.p.hold_days:
                self.sell(reason="到期")
            elif pnl_pct <= -self.p.stop_loss:
                self.sell(reason="止损")
            elif pnl_pct >= self.p.take_profit:
                self.sell(reason="止盈")
            return
        
        # 无持仓时检查买入
        score, signals = self.calculate_score()
        
        if score >= self.p.min_score:
            # 计算仓位（得分越高仓位越大）
            if score >= 7:
                size = 0.4  # 40%仓位
            elif score >= 5:
                size = 0.3  # 30%仓位
            else:
                size = 0.2  # 20%仓位
            
            self.order = self.buy(size=size)
            self.signals = signals
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                self.buy_date = self.data.datetime.date(0)
                self.trades.append({
                    'type': 'BUY',
                    'date': str(self.buy_date),
                    'price': order.executed.price,
                    'size': order.executed.size,
                    'score': self.score,
                    'signals': self.signals
                })
            else:
                sell_date = self.data.datetime.date(0)
                pnl = (order.executed.price - self.buy_price) * order.executed.size
                pnl_pct = (order.executed.price - self.buy_price) / self.buy_price * 100
                
                self.trades[-1].update({
                    'sell_date': str(sell_date),
                    'sell_price': order.executed.price,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'hold_days': (sell_date - self.buy_date).days
                })
                
                self.buy_price = None
                self.buy_date = None


# ============================================================
# 二、数据加载
# ============================================================

class MockDataFeed(bt.feeds.PandasData):
    """模拟数据源"""
    pass


def generate_mock_data(days=365):
    """生成模拟股票数据"""
    np.random.seed(42)
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # 生成价格数据（随机游走）
    returns = np.random.randn(days) * 0.02  # 2%波动
    close = 100 * np.exp(np.cumsum(returns))
    
    # OHLCV数据
    high = close * (1 + np.abs(np.random.randn(days)) * 0.01)
    low = close * (1 - np.abs(np.random.randn(days)) * 0.01)
    open_price = close * (1 + np.random.randn(days) * 0.005)
    volume = np.random.randint(1000000, 10000000, days)
    
    df = pd.DataFrame({
        'datetime': dates,
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })
    df.set_index('datetime', inplace=True)
    
    return df


# ============================================================
# 三、回测引擎
# ============================================================

def run_backtest(strategy_class, data_df, cash=100000, commission=0.001):
    """运行回测"""
    cerebro = bt.Cerebro()
    
    # 添加策略
    cerebro.addstrategy(strategy_class)
    
    # 添加数据
    data = bt.feeds.PandasData(dataname=data_df)
    cerebro.adddata(data)
    
    # 设置初始资金
    cerebro.broker.setcash(cash)
    
    # 设置手续费
    cerebro.broker.setcommission(commission=commission)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # 运行回测
    initial_value = cerebro.broker.getvalue()
    results = cerebro.run()
    final_value = cerebro.broker.getvalue()
    
    # 提取结果
    strat = results[0]
    
    # 获取分析结果
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    returns = strat.analyzers.returns.get_analysis()
    trades = strat.analyzers.trades.get_analysis()
    
    return {
        'initial_value': initial_value,
        'final_value': final_value,
        'total_return': (final_value - initial_value) / initial_value * 100,
        'sharpe_ratio': sharpe.get('sharperatio', 0),
        'max_drawdown': drawdown.get('max', {}).get('drawdown', 0),
        'total_trades': trades.get('total', {}).get('total', 0),
        'won_trades': trades.get('won', {}).get('total', 0),
        'lost_trades': trades.get('lost', {}).get('total', 0),
        'trade_list': strat.trades if hasattr(strat, 'trades') else []
    }


# ============================================================
# 四、主程序
# ============================================================

def main():
    print("="*60)
    print("📊 Backtrader回测系统 - 多因子策略V3")
    print("="*60)
    print(f"数据保存路径: {BACKTEST_DATA_DIR}")
    print("="*60)
    
    # 生成模拟数据
    print("\n生成模拟数据...")
    data = generate_mock_data(days=365)
    print(f"  数据范围: {data.index[0].date()} ~ {data.index[-1].date()}")
    print(f"  数据条数: {len(data)}")
    
    # 运行回测
    print("\n运行回测...")
    results = run_backtest(MultiFactorStrategyV3, data)
    
    # 打印结果
    print("\n" + "="*60)
    print("📈 回测结果")
    print("="*60)
    print(f"初始资金: ¥{results['initial_value']:,.2f}")
    print(f"最终资金: ¥{results['final_value']:,.2f}")
    print(f"总收益率: {results['total_return']:.2f}%")
    print(f"夏普比率: {results['sharpe_ratio']:.2f}")
    print(f"最大回撤: {results['max_drawdown']:.2f}%")
    print(f"\n总交易数: {results['total_trades']}")
    print(f"盈利交易: {results['won_trades']}")
    print(f"亏损交易: {results['lost_trades']}")
    
    if results['total_trades'] > 0:
        win_rate = results['won_trades'] / results['total_trades'] * 100
        print(f"胜率: {win_rate:.1f}%")
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(BACKTEST_DATA_DIR, f"backtest_v3_{timestamp}.json")
    
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'strategy': 'MultiFactorStrategyV3',
        'data_range': {
            'start': str(data.index[0].date()),
            'end': str(data.index[-1].date()),
            'days': len(data)
        },
        'parameters': {
            'min_score': 3.0,
            'stop_loss': 0.04,
            'take_profit': 0.10,
            'hold_days': 5
        },
        'results': {
            'initial_value': results['initial_value'],
            'final_value': results['final_value'],
            'total_return': results['total_return'],
            'sharpe_ratio': results['sharpe_ratio'],
            'max_drawdown': results['max_drawdown'],
            'total_trades': results['total_trades'],
            'won_trades': results['won_trades'],
            'lost_trades': results['lost_trades'],
            'win_rate': win_rate if results['total_trades'] > 0 else 0
        },
        'trades': results['trade_list']
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 回测结果已保存: {output_file}")
    
    return results


if __name__ == '__main__':
    main()
