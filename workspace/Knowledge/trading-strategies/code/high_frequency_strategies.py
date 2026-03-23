"""
Day 10 - 高频数据处理策略

实现订单簿不平衡、Tick数据动量、高频因子组合策略
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class HighFrequencyStrategies:
    """高频数据处理策略库"""

    @staticmethod
    def order_book_imbalance_strategy(df: pd.DataFrame) -> pd.DataFrame:
        """
        订单簿不平衡策略

        基于买卖盘力量对比
        """
        df = df.copy()

        # 模拟订单簿数据（实际应从Level-2数据获取）
        df['bid_volume'] = df['volume'] * 0.6  # 买盘
        df['ask_volume'] = df['volume'] * 0.4  # 卖盘

        # 计算订单簿不平衡
        df['imbalance'] = (df['bid_volume'] - df['ask_volume']) / df['volume']

        df['signal'] = 0
        # 买盘力量强
        df.loc[df['imbalance'] > 0.3, 'signal'] = 1
        # 卖盘力量强
        df.loc[df['imbalance'] < -0.3, 'signal'] = -1

        return df

    @staticmethod
    def tick_momentum_strategy(df: pd.DataFrame, window: int = 10) -> pd.DataFrame:
        """
        Tick数据动量策略

        基于高频价格变化
        """
        df = df.copy()

        # 计算价格变化
        df['price_change'] = df['close'].diff()

        # 计算动量
        df['momentum'] = df['price_change'].rolling(window).sum()

        # 计算波动率
        df['volatility'] = df['price_change'].rolling(window).std()

        df['signal'] = 0
        # 动量向上且波动率低
        df.loc[(df['momentum'] > 0) & (df['volatility'] < df['volatility'].quantile(0.3)), 'signal'] = 1
        # 动量向下且波动率低
        df.loc[(df['momentum'] < 0) & (df['volatility'] < df['volatility'].quantile(0.3)), 'signal'] = -1

        return df

    @staticmethod
    def high_frequency_factor_strategy(df: pd.DataFrame) -> pd.DataFrame:
        """
        高频因子组合策略

        综合多个高频因子
        """
        df = df.copy()

        # 计算高频因子
        # 1. 成交量加权价格变化
        df['vwap_change'] = (df['close'] * df['volume']).rolling(10).sum() / df['volume'].rolling(10).sum()
        df['vwap_change'] = df['vwap_change'].pct_change()

        # 2. 价格冲击
        df['price_impact'] = df['close'].pct_change() / np.log(df['volume'] + 1)

        # 3. 订单流
        df['order_flow'] = df['close'].diff() * df['volume']

        # 综合因子
        df['factor'] = (
            df['vwap_change'] * 0.4 +
            df['price_impact'] * 0.3 +
            df['order_flow'] * 0.3
        )

        df['signal'] = 0
        df.loc[df['factor'] > df['factor'].quantile(0.7), 'signal'] = 1
        df.loc[df['factor'] < df['factor'].quantile(0.3), 'signal'] = -1

        return df

    @staticmethod
    def microstructure_strategy(df: pd.DataFrame) -> pd.DataFrame:
        """
        市场微观结构策略

        基于买卖价差和成交频率
        """
        df = df.copy()

        # 计算买卖价差（简化）
        df['spread'] = (df['high'] - df['low']) / df['close']

        # 计算成交频率
        df['trade_frequency'] = df['volume'].rolling(20).mean()

        # 计算市场深度（简化）
        df['market_depth'] = df['volume'] / df['spread']

        df['signal'] = 0
        # 价差收窄且深度增加
        df.loc[(df['spread'] < df['spread'].quantile(0.3)) &
               (df['market_depth'] > df['market_depth'].quantile(0.7)), 'signal'] = 1
        # 价差扩大且深度减少
        df.loc[(df['spread'] > df['spread'].quantile(0.7)) &
               (df['market_depth'] < df['market_depth'].quantile(0.3)), 'signal'] = -1

        return df


def test_high_frequency_strategies():
    """测试高频数据策略"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta

    # 生成模拟数据
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    np.random.seed(42)

    close = 100 + np.cumsum(np.random.randn(100) * 2)
    high = close + np.random.rand(100) * 3
    low = close - np.random.rand(100) * 3
    volume = np.random.randint(100000, 5000000, 100)

    df = pd.DataFrame({
        'close': close,
        'high': high,
        'low': low,
        'volume': volume
    }, index=dates)

    # 测试订单簿不平衡策略
    print("订单簿不平衡策略：")
    result = HighFrequencyStrategies.order_book_imbalance_strategy(df)
    print(result[['close', 'imbalance', 'signal']].tail(10))

    # 测试Tick数据动量策略
    print("\nTick数据动量策略：")
    result = HighFrequencyStrategies.tick_momentum_strategy(df)
    print(result[['close', 'momentum', 'volatility', 'signal']].tail(10))

    # 测试高频因子组合策略
    print("\n高频因子组合策略：")
    result = HighFrequencyStrategies.high_frequency_factor_strategy(df)
    print(result[['close', 'factor', 'signal']].tail(10))

    # 测试市场微观结构策略
    print("\n市场微观结构策略：")
    result = HighFrequencyStrategies.microstructure_strategy(df)
    print(result[['close', 'spread', 'market_depth', 'signal']].tail(10))


if __name__ == '__main__':
    test_high_frequency_strategies()
