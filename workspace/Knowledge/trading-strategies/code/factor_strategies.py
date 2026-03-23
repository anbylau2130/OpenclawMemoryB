"""
Day 13 - 因子研究策略

实现动量因子、价值因子、质量因子、多因子组合策略
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class FactorStrategies:
    """因子研究策略库"""

    @staticmethod
    def momentum_factor_strategy(df: pd.DataFrame, lookback: int = 20) -> pd.DataFrame:
        """
        动量因子策略

        基于价格动量
        """
        df = df.copy()

        # 计算动量因子
        df['momentum_1m'] = df['close'].pct_change(lookback)
        df['momentum_3m'] = df['close'].pct_change(lookback * 3)
        df['momentum_6m'] = df['close'].pct_change(lookback * 6)

        # 计算动量得分
        df['momentum_score'] = (
            df['momentum_1m'] * 0.5 +
            df['momentum_3m'] * 0.3 +
            df['momentum_6m'] * 0.2
        )

        df['signal'] = 0
        df.loc[df['momentum_score'] > df['momentum_score'].quantile(0.7), 'signal'] = 1
        df.loc[df['momentum_score'] < df['momentum_score'].quantile(0.3), 'signal'] = -1

        return df

    @staticmethod
    def value_factor_strategy(df: pd.DataFrame) -> pd.DataFrame:
        """
        价值因子策略

        基于估值指标
        """
        df = df.copy()

        # 计算价值因子（简化版：价格/均线）
        df['price_to_ma20'] = df['close'] / df['close'].rolling(20).mean()
        df['price_to_ma50'] = df['close'] / df['close'].rolling(50).mean()
        df['price_to_ma100'] = df['close'] / df['close'].rolling(100).mean()

        # 价值得分（价格越低越好）
        df['value_score'] = (
            (1 / df['price_to_ma20']) * 0.4 +
            (1 / df['price_to_ma50']) * 0.3 +
            (1 / df['price_to_ma100']) * 0.3
        )

        df['signal'] = 0
        df.loc[df['value_score'] > df['value_score'].quantile(0.7), 'signal'] = 1
        df.loc[df['value_score'] < df['value_score'].quantile(0.3), 'signal'] = -1

        return df

    @staticmethod
    def quality_factor_strategy(df: pd.DataFrame) -> pd.DataFrame:
        """
        质量因子策略

        基于盈利能力、财务稳定性
        """
        df = df.copy()

        # 计算质量因子（简化版：波动率倒数）
        df['volatility_20'] = df['close'].pct_change().rolling(20).std()
        df['volatility_50'] = df['close'].pct_change().rolling(50).std()

        # 计算夏普比率（简化版）
        df['sharpe_20'] = df['close'].pct_change().rolling(20).mean() / df['volatility_20']
        df['sharpe_50'] = df['close'].pct_change().rolling(50).mean() / df['volatility_50']

        # 质量得分
        df['quality_score'] = (
            (1 / df['volatility_20']) * 0.3 +
            (1 / df['volatility_50']) * 0.3 +
            df['sharpe_20'] * 0.2 +
            df['sharpe_50'] * 0.2
        )

        df['signal'] = 0
        df.loc[df['quality_score'] > df['quality_score'].quantile(0.7), 'signal'] = 1
        df.loc[df['quality_score'] < df['quality_score'].quantile(0.3), 'signal'] = -1

        return df

    @staticmethod
    def multi_factor_combination_strategy(df: pd.DataFrame) -> pd.DataFrame:
        """
        多因子组合策略

        综合动量、价值、质量因子
        """
        df = df.copy()

        # 计算各个因子
        # 动量因子
        df['momentum'] = df['close'].pct_change(20)

        # 价值因子
        df['value'] = 1 / (df['close'] / df['close'].rolling(50).mean())

        # 质量因子
        df['quality'] = 1 / df['close'].pct_change().rolling(20).std()

        # 标准化因子
        for factor in ['momentum', 'value', 'quality']:
            df[f'{factor}_norm'] = (df[factor] - df[factor].mean()) / df[factor].std()

        # 多因子组合（等权重）
        df['multi_factor_score'] = (
            df['momentum_norm'] * 0.4 +
            df['value_norm'] * 0.3 +
            df['quality_norm'] * 0.3
        )

        df['signal'] = 0
        df.loc[df['multi_factor_score'] > df['multi_factor_score'].quantile(0.7), 'signal'] = 1
        df.loc[df['multi_factor_score'] < df['multi_factor_score'].quantile(0.3), 'signal'] = -1

        return df


def test_factor_strategies():
    """测试因子策略"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta

    # 生成模拟数据
    dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
    np.random.seed(42)

    close = 100 + np.cumsum(np.random.randn(200) * 2)
    high = close + np.random.rand(200) * 3
    low = close - np.random.rand(200) * 3
    volume = np.random.randint(100000, 5000000, 200)

    df = pd.DataFrame({
        'close': close,
        'high': high,
        'low': low,
        'volume': volume
    }, index=dates)

    # 测试动量因子策略
    print("动量因子策略：")
    result = FactorStrategies.momentum_factor_strategy(df)
    print(result[['close', 'momentum_score', 'signal']].tail(10))

    # 测试价值因子策略
    print("\n价值因子策略：")
    result = FactorStrategies.value_factor_strategy(df)
    print(result[['close', 'value_score', 'signal']].tail(10))

    # 测试质量因子策略
    print("\n质量因子策略：")
    result = FactorStrategies.quality_factor_strategy(df)
    print(result[['close', 'quality_score', 'signal']].tail(10))

    # 测试多因子组合策略
    print("\n多因子组合策略：")
    result = FactorStrategies.multi_factor_combination_strategy(df)
    print(result[['close', 'multi_factor_score', 'signal']].tail(10))


if __name__ == '__main__':
    test_factor_strategies()
