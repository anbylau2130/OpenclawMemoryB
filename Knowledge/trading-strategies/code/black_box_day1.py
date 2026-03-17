"""
《打开量化投资的黑箱》Day 1 - 量化思维策略

实现市场中性、统计套利策略
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class QuantitativeThinkingStrategies:
    """量化思维策略库"""

    @staticmethod
    def market_neutral_strategy(df: pd.DataFrame, beta: float = 1.0) -> pd.DataFrame:
        """
        市场中性策略

        对冲市场风险，获取alpha收益
        """
        df = df.copy()

        # 计算市场beta（简化：用收益率相关性）
        df['stock_return'] = df['close'].pct_change()
        df['market_return'] = df['stock_return'].rolling(20).mean()  # 用自身作为市场代理

        # 计算beta
        df['beta'] = df['stock_return'].rolling(20).corr(df['market_return'])

        # 对冲：持有多头 + 做空beta份市场
        df['hedged_return'] = df['stock_return'] - df['beta'] * df['market_return']

        # 生成信号
        df['signal'] = 0
        df.loc[df['hedged_return'].rolling(10).mean() > 0, 'signal'] = 1
        df.loc[df['hedged_return'].rolling(10).mean() < 0, 'signal'] = -1

        return df

    @staticmethod
    def statistical_arbitrage_strategy(df: pd.DataFrame, lookback: int = 20) -> pd.DataFrame:
        """
        统计套利策略

        利用价格偏离均值的机会
        """
        df = df.copy()

        # 计算Z-score
        df['mean'] = df['close'].rolling(lookback).mean()
        df['std'] = df['close'].rolling(lookback).std()
        df['z_score'] = (df['close'] - df['mean']) / df['std']

        # 统计套利：价格偏离均值时反向操作
        df['signal'] = 0
        df.loc[df['z_score'] < -2, 'signal'] = 1  # 价格严重低估，买入
        df.loc[df['z_score'] > 2, 'signal'] = -1  # 价格严重高估，卖出

        return df

    @staticmethod
    def pairs_trading_strategy(df1: pd.DataFrame, df2: pd.DataFrame, lookback: int = 20) -> pd.DataFrame:
        """
        配对交易策略

        交易两个相关性高的资产
        """
        # 计算价差
        spread = df1['close'] / df2['close']
        spread = pd.DataFrame({'spread': spread}, index=df1.index)

        # 计算Z-score
        spread['mean'] = spread['spread'].rolling(lookback).mean()
        spread['std'] = spread['spread'].rolling(lookback).std()
        spread['z_score'] = (spread['spread'] - spread['mean']) / spread['std']

        # 配对交易信号
        spread['signal'] = 0
        spread.loc[spread['z_score'] < -2, 'signal'] = 1  # 价差异常低，买入A卖出B
        spread.loc[spread['z_score'] > 2, 'signal'] = -1  # 价差异常高，卖出A买入B

        return spread

    @staticmethod
    def mean_reversion_strategy(df: pd.DataFrame, lookback: int = 20, threshold: float = 2.0) -> pd.DataFrame:
        """
        均值回归策略

        价格偏离长期均值时回归
        """
        df = df.copy()

        # 计算长期均值
        df['long_mean'] = df['close'].rolling(lookback).mean()
        df['deviation'] = (df['close'] - df['long_mean']) / df['long_mean']

        # 均值回归信号
        df['signal'] = 0
        df.loc[df['deviation'] < -threshold / 100, 'signal'] = 1  # 价格低于均值，买入
        df.loc[df['deviation'] > threshold / 100, 'signal'] = -1  # 价格高于均值，卖出

        return df


def test_quantitative_thinking_strategies():
    """测试量化思维策略"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta

    # 生成模拟数据
    dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
    np.random.seed(42)

    close = 100 + np.cumsum(np.random.randn(200) * 2)
    volume = np.random.randint(100000, 5000000, 200)

    df = pd.DataFrame({
        'close': close,
        'volume': volume
    }, index=dates)

    # 测试市场中性策略
    print("市场中性策略：")
    result = QuantitativeThinkingStrategies.market_neutral_strategy(df)
    print(result[['close', 'beta', 'hedged_return', 'signal']].tail(10))

    # 测试统计套利策略
    print("\n统计套利策略：")
    result = QuantitativeThinkingStrategies.statistical_arbitrage_strategy(df)
    print(result[['close', 'z_score', 'signal']].tail(10))

    # 测试均值回归策略
    print("\n均值回归策略：")
    result = QuantitativeThinkingStrategies.mean_reversion_strategy(df)
    print(result[['close', 'deviation', 'signal']].tail(10))


if __name__ == '__main__':
    test_quantitative_thinking_strategies()
