"""
《打开量化投资的黑箱》Day 8-14 策略实现
"""

import pandas as pd
import numpy as np


class HFTradingStrategies:
    """Day 8 - 高频交易策略"""

    @staticmethod
    def market_making(df: pd.DataFrame, spread: float = 0.001) -> pd.DataFrame:
        df = df.copy()
        df['bid'] = df['close'] * (1 - spread)
        df['ask'] = df['close'] * (1 + spread)
        df['profit'] = df['ask'] - df['bid']
        df['signal'] = 1  # 做市商总是提供流动性
        return df

    @staticmethod
    def latency_arbitrage(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['price_change'] = df['close'].diff()
        df['signal'] = 0
        df.loc[df['price_change'] > 0, 'signal'] = 1
        df.loc[df['price_change'] < 0, 'signal'] = -1
        return df


class StatisticalArbStrategies:
    """Day 9 - 统计套利策略"""

    @staticmethod
    def cointegration(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['mean'] = df['close'].rolling(60).mean()
        df['deviation'] = df['close'] - df['mean']
        df['z_score'] = df['deviation'] / df['close'].rolling(60).std()
        df['signal'] = 0
        df.loc[df['z_score'] < -2, 'signal'] = 1
        df.loc[df['z_score'] > 2, 'signal'] = -1
        return df


class EventDrivenStrategies:
    """Day 10 - 事件驱动策略"""

    @staticmethod
    def earnings_event(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['return'] = df['close'].pct_change()
        df['volatility'] = df['return'].rolling(20).std()
        df['signal'] = 0
        df.loc[df['return'] > df['volatility'] * 2, 'signal'] = 1
        return df


class MLEnhancedStrategies:
    """Day 11 - 机器学习增强策略"""

    @staticmethod
    def ml_enhanced(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['feature1'] = df['close'].pct_change(5)
        df['feature2'] = df['close'].pct_change(20)
        df['feature3'] = df['volume'] / df['volume'].rolling(20).mean()
        df['score'] = df['feature1'] * 0.4 + df['feature2'] * 0.3 + df['feature3'] * 0.3
        df['signal'] = 0
        df.loc[df['score'] > df['score'].quantile(0.7), 'signal'] = 1
        df.loc[df['score'] < df['score'].quantile(0.3), 'signal'] = -1
        return df


class AlternativeDataStrategies:
    """Day 12 - 另类数据策略"""

    @staticmethod
    def sentiment(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['sentiment'] = np.random.randn(len(df))  # 模拟情绪数据
        df['signal'] = 0
        df.loc[df['sentiment'] > 0.5, 'signal'] = 1
        df.loc[df['sentiment'] < -0.5, 'signal'] = -1
        return df


class MarketTimingStrategies:
    """Day 13 - 择时策略"""

    @staticmethod
    def macro_timing(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['ma50'] = df['close'].rolling(50).mean()
        df['ma200'] = df['close'].rolling(200).mean()
        df['signal'] = 0
        df.loc[df['ma50'] > df['ma200'], 'signal'] = 1
        df.loc[df['ma50'] < df['ma200'], 'signal'] = -1
        return df


class AssetAllocationStrategies:
    """Day 14 - 资产配置策略"""

    @staticmethod
    def dynamic_allocation(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['return'] = df['close'].pct_change(20)
        df['volatility'] = df['close'].pct_change().rolling(20).std()
        df['risk_adjusted'] = df['return'] / df['volatility']
        df['signal'] = 0
        df.loc[df['risk_adjusted'] > 0.5, 'signal'] = 1
        df.loc[df['risk_adjusted'] < -0.5, 'signal'] = -1
        return df


def test_day8_14():
    """测试Day 8-14策略"""
    import pandas as pd
    import numpy as np

    dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(200) * 2)
    volume = np.random.randint(100000, 5000000, 200)
    df = pd.DataFrame({'close': close, 'volume': volume}, index=dates)

    print("Day 8 - 做市策略:", HFTradingStrategies.market_making(df)['signal'].value_counts().to_dict())
    print("Day 9 - 协整策略:", StatisticalArbStrategies.cointegration(df)['signal'].value_counts().to_dict())
    print("Day 10 - 事件驱动:", EventDrivenStrategies.earnings_event(df)['signal'].value_counts().to_dict())
    print("Day 11 - ML增强:", MLEnhancedStrategies.ml_enhanced(df)['signal'].value_counts().to_dict())
    print("Day 12 - 情绪策略:", AlternativeDataStrategies.sentiment(df)['signal'].value_counts().to_dict())
    print("Day 13 - 宏观择时:", MarketTimingStrategies.macro_timing(df)['signal'].value_counts().to_dict())
    print("Day 14 - 动态配置:", AssetAllocationStrategies.dynamic_allocation(df)['signal'].value_counts().to_dict())


if __name__ == '__main__':
    test_day8_14()
