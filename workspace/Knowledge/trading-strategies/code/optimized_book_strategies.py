"""
优化后的书籍策略

添加止损和风险控制
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


class OptimizedBookStrategies:
    """优化后的书籍策略"""

    def __init__(self, stop_loss=-0.05, take_profit=0.10, max_position=0.3):
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.max_position = max_position

    def add_risk_management(self, df: pd.DataFrame, signal_col='signal') -> pd.DataFrame:
        """添加风险管理"""
        df = df.copy()

        # 止损信号
        df['stop_loss'] = 0
        df.loc[df['close'].pct_change() < self.stop_loss, 'stop_loss'] = -1

        # 止盈信号
        df['take_profit'] = 0
        df.loc[df['close'].pct_change() > self.take_profit, 'take_profit'] = -1

        # 综合信号
        df['final_signal'] = df[signal_col]
        df.loc[df['stop_loss'] == -1, 'final_signal'] = -1
        df.loc[df['take_profit'] == -1, 'final_signal'] = -1

        return df

    def macd_optimized(self, df: pd.DataFrame, fast=12, slow=26, signal=9) -> pd.DataFrame:
        """优化的MACD策略"""
        df = df.copy()

        # 计算MACD
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()

        # 生成信号
        df['signal'] = 0
        df.loc[macd > signal_line, 'signal'] = 1
        df.loc[macd < signal_line, 'signal'] = -1

        # 添加风险管理
        df = self.add_risk_management(df)

        return df

    def rsi_optimized(self, df: pd.DataFrame, period=14, oversold=30, overbought=70) -> pd.DataFrame:
        """优化的RSI策略"""
        df = df.copy()

        # 计算RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # 生成信号
        df['signal'] = 0
        df.loc[rsi < oversold, 'signal'] = 1
        df.loc[rsi > overbought, 'signal'] = -1

        # 添加风险管理
        df = self.add_risk_management(df)

        return df

    def bollinger_optimized(self, df: pd.DataFrame, period=20, std_dev=2.0) -> pd.DataFrame:
        """优化的布林带策略"""
        df = df.copy()

        # 计算布林带
        ma = df['close'].rolling(period).mean()
        std = df['close'].rolling(period).std()

        upper_band = ma + (std * std_dev)
        lower_band = ma - (std * std_dev)

        # 生成信号
        df['signal'] = 0
        df.loc[df['close'] <= lower_band, 'signal'] = 1
        df.loc[df['close'] >= upper_band, 'signal'] = -1

        # 添加风险管理
        df = self.add_risk_management(df)

        return df

    def combined_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        """组合策略（投票法）"""
        df = df.copy()

        # 生成各策略信号
        macd_df = self.macd_optimized(df)
        rsi_df = self.rsi_optimized(df)
        bollinger_df = self.bollinger_optimized(df)

        # 投票
        df['macd_signal'] = macd_df['final_signal']
        df['rsi_signal'] = rsi_df['final_signal']
        df['bollinger_signal'] = bollinger_df['final_signal']

        # 综合信号（2/3同意）
        df['signal'] = 0
        buy_votes = (df['macd_signal'] == 1).astype(int) + \
                   (df['rsi_signal'] == 1).astype(int) + \
                   (df['bollinger_signal'] == 1).astype(int)

        sell_votes = (df['macd_signal'] == -1).astype(int) + \
                    (df['rsi_signal'] == -1).astype(int) + \
                    (df['bollinger_signal'] == -1).astype(int)

        df.loc[buy_votes >= 2, 'signal'] = 1
        df.loc[sell_votes >= 2, 'signal'] = -1

        # 添加风险管理
        df = self.add_risk_management(df)

        return df


def test_optimized_strategies():
    """测试优化策略"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta

    # 生成模拟数据
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    np.random.seed(42)

    close = 100 + np.cumsum(np.random.randn(100) * 2)
    high = close + np.random.rand(100) * 3
    low = close - np.random.rand(100) * 3
    volume = np.random.randint(1000000, 5000000, 100)

    df = pd.DataFrame({
        'close': close,
        'high': high,
        'low': low,
        'volume': volume
    }, index=dates)

    # 测试优化策略
    optimizer = OptimizedBookStrategies(stop_loss=-0.05, take_profit=0.10)

    print("优化MACD策略：")
    result = optimizer.macd_optimized(df)
    print(result[['close', 'signal', 'final_signal']].tail())

    print("\n优化RSI策略：")
    result = optimizer.rsi_optimized(df)
    print(result[['close', 'signal', 'final_signal']].tail())

    print("\n组合策略：")
    result = optimizer.combined_strategy(df)
    print(result[['close', 'macd_signal', 'rsi_signal', 'bollinger_signal', 'signal']].tail())


if __name__ == '__main__':
    test_optimized_strategies()
