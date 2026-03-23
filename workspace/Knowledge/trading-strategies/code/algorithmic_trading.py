"""
《量化交易：如何建立自己的算法交易》策略实现
"""

import pandas as pd
import numpy as np


class AlgorithmicTrading:
    """算法交易策略"""

    @staticmethod
    def trend_following(df: pd.DataFrame) -> pd.DataFrame:
        """趋势跟踪"""
        df = df.copy()
        df['ma_fast'] = df['close'].rolling(10).mean()
        df['ma_slow'] = df['close'].rolling(30).mean()
        df['signal'] = 0
        df.loc[df['ma_fast'] > df['ma_slow'], 'signal'] = 1
        df.loc[df['ma_fast'] < df['ma_slow'], 'signal'] = -1
        return df

    @staticmethod
    def breakout(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """突破策略"""
        df = df.copy()
        df['high'] = df['close'].rolling(window).max()
        df['low'] = df['close'].rolling(window).min()
        df['signal'] = 0
        df.loc[df['close'] > df['high'].shift(1), 'signal'] = 1
        df.loc[df['close'] < df['low'].shift(1), 'signal'] = -1
        return df

    @staticmethod
    def mean_reversion(df: pd.DataFrame) -> pd.DataFrame:
        """均值回归"""
        df = df.copy()
        df['mean'] = df['close'].rolling(20).mean()
        df['std'] = df['close'].rolling(20).std()
        df['upper'] = df['mean'] + 2 * df['std']
        df['lower'] = df['mean'] - 2 * df['std']
        df['signal'] = 0
        df.loc[df['close'] < df['lower'], 'signal'] = 1
        df.loc[df['close'] > df['upper'], 'signal'] = -1
        return df

    @staticmethod
    def momentum(df: pd.DataFrame) -> pd.DataFrame:
        """动量策略"""
        df = df.copy()
        df['momentum'] = df['close'].pct_change(10)
        df['signal'] = 0
        df.loc[df['momentum'] > 0.05, 'signal'] = 1
        df.loc[df['momentum'] < -0.05, 'signal'] = -1
        return df

    @staticmethod
    def volatility_breakout(df: pd.DataFrame) -> pd.DataFrame:
        """波动率突破"""
        df = df.copy()
        df['volatility'] = df['close'].pct_change().rolling(20).std()
        df['vol_ma'] = df['volatility'].rolling(50).mean()
        df['signal'] = 0
        df.loc[df['volatility'] > df['vol_ma'] * 1.5, 'signal'] = 1  # 高波动买入
        return df

    @staticmethod
    def statistical_arbitrage(df: pd.DataFrame) -> pd.DataFrame:
        """统计套利"""
        df = df.copy()
        df['z_score'] = (df['close'] - df['close'].rolling(60).mean()) / df['close'].rolling(60).std()
        df['signal'] = 0
        df.loc[df['z_score'] < -2, 'signal'] = 1
        df.loc[df['z_score'] > 2, 'signal'] = -1
        return df

    @staticmethod
    def pair_trading(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        """配对交易"""
        spread = df1['close'] / df2['close']
        spread = pd.DataFrame({'spread': spread}, index=df1.index)
        spread['mean'] = spread['spread'].rolling(30).mean()
        spread['std'] = spread['spread'].rolling(30).std()
        spread['z'] = (spread['spread'] - spread['mean']) / spread['std']
        spread['signal'] = 0
        spread.loc[spread['z'] < -2, 'signal'] = 1
        spread.loc[spread['z'] > 2, 'signal'] = -1
        return spread

    @staticmethod
    def market_making(df: pd.DataFrame) -> pd.DataFrame:
        """做市策略"""
        df = df.copy()
        df['spread'] = df['high'] - df['low']
        df['spread_ma'] = df['spread'].rolling(20).mean()
        df['signal'] = 0
        df.loc[df['spread'] > df['spread_ma'] * 1.2, 'signal'] = 1  # 价差扩大时提供流动性
        return df


def test_algorithmic_trading():
    """测试算法交易策略"""
    import pandas as pd
    import numpy as np

    dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(200) * 2)
    high = close + np.random.rand(200) * 3
    low = close - np.random.rand(200) * 3
    volume = np.random.randint(100000, 5000000, 200)
    df = pd.DataFrame({'close': close, 'high': high, 'low': low, 'volume': volume}, index=dates)

    print("趋势跟踪:", AlgorithmicTrading.trend_following(df)['signal'].value_counts().to_dict())
    print("突破策略:", AlgorithmicTrading.breakout(df)['signal'].value_counts().to_dict())
    print("均值回归:", AlgorithmicTrading.mean_reversion(df)['signal'].value_counts().to_dict())
    print("动量策略:", AlgorithmicTrading.momentum(df)['signal'].value_counts().to_dict())
    print("波动突破:", AlgorithmicTrading.volatility_breakout(df)['signal'].value_counts().to_dict())
    print("统计套利:", AlgorithmicTrading.statistical_arbitrage(df)['signal'].value_counts().to_dict())
    print("做市策略:", AlgorithmicTrading.market_making(df)['signal'].value_counts().to_dict())


if __name__ == '__main__':
    test_algorithmic_trading()
