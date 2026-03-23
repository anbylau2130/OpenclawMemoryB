"""
书籍策略实现

《量化投资：以Python为工具》中的策略实现
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class BookStrategies:
    """书籍策略库"""

    @staticmethod
    def calculate_ma(df: pd.DataFrame, period: int) -> pd.Series:
        """计算移动平均"""
        return df['close'].rolling(period).mean()

    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int) -> pd.Series:
        """计算指数移动平均"""
        return df['close'].ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """计算RSI"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """计算MACD"""
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line

        return {
            'macd': macd,
            'signal': signal_line,
            'histogram': histogram
        }

    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> Dict:
        """计算布林带"""
        ma = df['close'].rolling(period).mean()
        std = df['close'].rolling(period).std()

        upper_band = ma + (std * std_dev)
        lower_band = ma - (std * std_dev)

        return {
            'middle': ma,
            'upper': upper_band,
            'lower': lower_band
        }

    @staticmethod
    def dual_ma_strategy(df: pd.DataFrame, fast: int = 5, slow: int = 20) -> pd.DataFrame:
        """
        双均线策略

        买入信号：短期均线上穿长期均线
        卖出信号：短期均线下穿长期均线
        """
        df = df.copy()
        df['MA_fast'] = BookStrategies.calculate_ma(df, fast)
        df['MA_slow'] = BookStrategies.calculate_ma(df, slow)

        df['signal'] = 0
        df.loc[df['MA_fast'] > df['MA_slow'], 'signal'] = 1  # 买入
        df.loc[df['MA_fast'] < df['MA_slow'], 'signal'] = -1  # 卖出

        # 检测交叉点
        df['position'] = df['signal'].diff()

        return df

    @staticmethod
    def rsi_strategy(df: pd.DataFrame, period: int = 14, oversold: int = 30, overbought: int = 70) -> pd.DataFrame:
        """
        RSI策略

        买入信号：RSI < 超卖线（30）
        卖出信号：RSI > 超买线（70）
        """
        df = df.copy()
        df['RSI'] = BookStrategies.calculate_rsi(df, period)

        df['signal'] = 0
        df.loc[df['RSI'] < oversold, 'signal'] = 1  # 买入
        df.loc[df['RSI'] > overbought, 'signal'] = -1  # 卖出

        return df

    @staticmethod
    def macd_strategy(df: pd.DataFrame) -> pd.DataFrame:
        """
        MACD策略

        买入信号：MACD上穿信号线
        卖出信号：MACD下穿信号线
        """
        df = df.copy()
        macd_dict = BookStrategies.calculate_macd(df)
        df['MACD'] = macd_dict['macd']
        df['Signal'] = macd_dict['signal']
        df['Histogram'] = macd_dict['histogram']

        df['signal'] = 0
        df.loc[df['MACD'] > df['Signal'], 'signal'] = 1  # 买入
        df.loc[df['MACD'] < df['Signal'], 'signal'] = -1  # 卖出

        return df

    @staticmethod
    def bollinger_strategy(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """
        布林带策略

        买入信号：价格触及下轨
        卖出信号：价格触及上轨
        """
        df = df.copy()
        bb_dict = BookStrategies.calculate_bollinger_bands(df, period)
        df['BB_middle'] = bb_dict['middle']
        df['BB_upper'] = bb_dict['upper']
        df['BB_lower'] = bb_dict['lower']

        df['signal'] = 0
        df.loc[df['close'] <= df['BB_lower'], 'signal'] = 1  # 买入
        df.loc[df['close'] >= df['BB_upper'], 'signal'] = -1  # 卖出

        return df

    @staticmethod
    def momentum_strategy(df: pd.DataFrame, period: int = 10) -> pd.DataFrame:
        """
        动量策略

        买入信号：价格突破N日高点
        卖出信号：价格跌破N日低点
        """
        df = df.copy()
        df['high_roll'] = df['high'].rolling(period).max()
        df['low_roll'] = df['low'].rolling(period).min()

        df['signal'] = 0
        df.loc[df['close'] > df['high_roll'].shift(1), 'signal'] = 1  # 买入
        df.loc[df['close'] < df['low_roll'].shift(1), 'signal'] = -1  # 卖出

        return df

    @staticmethod
    def mean_reversion_strategy(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """
        均值回归策略

        买入信号：价格低于均值 - N倍标准差
        卖出信号：价格高于均值 + N倍标准差
        """
        df = df.copy()
        df['mean'] = df['close'].rolling(period).mean()
        df['std'] = df['close'].rolling(period).std()

        df['upper'] = df['mean'] + (df['std'] * std_dev)
        df['lower'] = df['mean'] - (df['std'] * std_dev)

        df['signal'] = 0
        df.loc[df['close'] < df['lower'], 'signal'] = 1  # 买入
        df.loc[df['close'] > df['upper'], 'signal'] = -1  # 卖出

        return df


def test_strategies():
    """测试策略"""
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

    # 测试双均线策略
    print("双均线策略：")
    result = BookStrategies.dual_ma_strategy(df)
    print(result[['close', 'MA_fast', 'MA_slow', 'signal']].tail())

    # 测试RSI策略
    print("\nRSI策略：")
    result = BookStrategies.rsi_strategy(df)
    print(result[['close', 'RSI', 'signal']].tail())

    # 测试MACD策略
    print("\nMACD策略：")
    result = BookStrategies.macd_strategy(df)
    print(result[['close', 'MACD', 'Signal', 'signal']].tail())


if __name__ == '__main__':
    test_strategies()
