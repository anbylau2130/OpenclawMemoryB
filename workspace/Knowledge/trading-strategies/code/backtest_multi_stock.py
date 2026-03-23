#!/usr/bin/env python3
"""
多股票回测系统 - Backtrader
=====================================
同时回测多支股票，生成更可靠的统计数据
数据保存: /root/.openclaw/workspace/data/backtest/
"""

import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

BACKTEST_DATA_DIR = "/root/.openclaw/workspace/data/backtest"


class MultiFactorStrategy(bt.Strategy):
    """多因子策略"""
    
    params = (
        ('min_score', 3.0),
        ('stop_loss', 0.04),
        ('take_profit', 0.10),
    )
    
    def __init__(self):
        self.trades = []
        self.orders = {}
        
        for i, data in enumerate(self.datas):
            self.orders[data._name] = None
            
            # 为每个股票添加指标
            setattr(self, f'ma5_{i}', bt.indicators.SMA(data.close, period=5))
            setattr(self, f'ma10_{i}', bt.indicators.SMA(data.close, period=10))
            setattr(self, f'ma20_{i}', bt.indicators.SMA(data.close, period=20))
            setattr(self, f'rsi_{i}', bt.indicators.RSI(data.close, period=14))
            setattr(self, f'macd_{i}', bt.indicators.MACD(data.close))
    
    def get_score(self, data, i):
        """计算多因子得分"""
        score = 0.0
        
        ma5 = getattr(self, f'ma5_{i}')[0]
        ma10 = getattr(self, f'ma10_{i}')[0]
        ma20 = getattr(self, f'ma20_{i}')[0]
        rsi = getattr(self, f'rsi_{i}')[0]
        macd = getattr(self, f'macd_{i}')
        
        # 均线多头
        if ma5 > ma10 > ma20:
            score += 2
        
        # 站上MA5
        if data.close[0] > ma5:
            score += 1
        
        # RSI超卖
        if rsi < 30:
            score += 1
        
        # MACD金叉
        if macd.lines.macd[0] > macd.lines.signal[0]:
            score += 0.5
        
        return score
    
    def next(self):
        for i, data in enumerate(self.datas):
            if self.getposition(data).size == 0:
                score = self.get_score(data, i)
                if score >= self.p.min_score:
                    size = 0.1  # 10%仓位
                    self.buy(data=data, size=size)
            else:
                # 检查止损止盈
                pos = self.getposition(data)
                pnl = (data.close[0] - pos.price) / pos.price
                if pnl <= -self.p.stop_loss or pnl >= self.p.take_profit:
                    self.close(data=data)


def generate_stock_data(name, days=252):
    """生成单支股票数据"""
    np.random.seed(hash(name) % 10000)
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # 不同股票不同特性
    volatility = 0.015 + np.random.random() * 0.02
    drift = np.random.random() * 0.0003
    
    returns = np.random.randn(days) * volatility + drift
    close = 50 * np.exp(np.cumsum(returns))
    
    high = close * (1 + np.abs(np.random.randn(days)) * 0.01)
    low = close * (1 - np.abs(np.random.randn(days)) * 0.01)
    open_price = close * (1 + np.random.randn(days) * 0.005)
    volume = np.random.randint(500000, 5000000, days)
    
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


def run_multi_stock_backtest(stocks, cash=1000000):
    """多股票回测"""
    cerebro = bt.Cerebro()
    
    # 添加策略
    cerebro.addstrategy(MultiFactorStrategy)
    
    # 添加多支股票数据
    for name in stocks:
        df = generate_stock_data(name)
        data = bt.feeds.PandasData(dataname=df, name=name)
        cerebro.adddata(data)
    
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=0.001)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    
    initial = cerebro.broker.getvalue()
    results = cerebro.run()
    final = cerebro.broker.getvalue()
    
    strat = results[0]
    trades = strat.analyzers.trades.get_analysis()
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    
    total = trades.get('total', {}).get('total', 0)
    won = trades.get('won', {}).get('total', 0)
    lost = trades.get('lost', {}).get('total', 0)
    
    return {
        'initial_value': initial,
        'final_value': final,
        'total_return': (final - initial) / initial * 100,
        'total_trades': total,
        'won_trades': won,
        'lost_trades': lost,
        'win_rate': won / total * 100 if total > 0 else 0,
        'sharpe_ratio': sharpe.get('sharperatio', 0) or 0,
        'max_drawdown': drawdown.get('max', {}).get('drawdown', 0),
    }


def main():
    print("="*60)
    print("📊 多股票回测系统 - Backtrader")
    print("="*60)
    print(f"数据保存路径: {BACKTEST_DATA_DIR}")
    print("="*60)
    
    # 测试股票池
    stocks = [
        "600036", "601318", "601166", "600000", "601398",
        "601288", "601939", "601988", "600030", "601211",
        "601857", "600028", "601088", "600019", "600031",
    ]
    
    print(f"\n回测股票数: {len(stocks)}")
    print(f"回测周期: 252天（1年）")
    
    print("\n运行回测...")
    results = run_multi_stock_backtest(stocks)
    
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
    print(f"胜率: {results['win_rate']:.1f}%")
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(BACKTEST_DATA_DIR, f"multi_stock_backtest_{timestamp}.json")
    
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'strategy': 'MultiFactorStrategy',
        'stocks': stocks,
        'results': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 结果已保存: {output_file}")
    
    return results


if __name__ == '__main__':
    main()
