"""
Day 11 - 机器学习基础策略

实现机器学习分类、特征工程、集成学习策略
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class MachineLearningStrategies:
    """机器学习基础策略库"""

    @staticmethod
    def ml_classification_strategy(df: pd.DataFrame) -> pd.DataFrame:
        """
        机器学习分类策略

        使用简单规则模拟机器学习分类
        """
        df = df.copy()

        # 特征工程
        df['return_1d'] = df['close'].pct_change(1)
        df['return_5d'] = df['close'].pct_change(5)
        df['return_10d'] = df['close'].pct_change(10)

        df['volatility_5d'] = df['return_1d'].rolling(5).std()
        df['volatility_10d'] = df['return_1d'].rolling(10).std()

        df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()

        # 简单分类规则（模拟机器学习模型）
        df['score'] = 0

        # 收益率因子
        df.loc[df['return_5d'] > 0, 'score'] += 1
        df.loc[df['return_10d'] > 0, 'score'] += 1

        # 波动率因子
        df.loc[df['volatility_5d'] < df['volatility_10d'], 'score'] += 1

        # 成交量因子
        df.loc[df['volume_ratio'] > 1, 'score'] += 1

        df['signal'] = 0
        df.loc[df['score'] >= 3, 'signal'] = 1  # 买入
        df.loc[df['score'] <= 1, 'signal'] = -1  # 卖出

        return df

    @staticmethod
    def feature_engineering_strategy(df: pd.DataFrame) -> pd.DataFrame:
        """
        特征工程优化策略

        创建多个技术特征
        """
        df = df.copy()

        # 价格特征
        df['price_momentum'] = df['close'] / df['close'].shift(10) - 1
        df['price_acceleration'] = df['price_momentum'].diff()

        # 成交量特征
        df['volume_trend'] = df['volume'] / df['volume'].shift(10) - 1
        df['volume_acceleration'] = df['volume_trend'].diff()

        # 波动率特征
        df['volatility'] = df['close'].pct_change().rolling(20).std()
        df['volatility_change'] = df['volatility'].diff()

        # 趋势特征
        df['ma_ratio'] = df['close'].rolling(5).mean() / df['close'].rolling(20).mean()

        # 综合得分
        df['feature_score'] = (
            df['price_momentum'] * 0.3 +
            df['volume_trend'] * 0.2 +
            df['ma_ratio'] * 0.3 +
            (1 - df['volatility']) * 0.2
        )

        df['signal'] = 0
        df.loc[df['feature_score'] > df['feature_score'].quantile(0.7), 'signal'] = 1
        df.loc[df['feature_score'] < df['feature_score'].quantile(0.3), 'signal'] = -1

        return df

    @staticmethod
    def ensemble_strategy(df: pd.DataFrame) -> pd.DataFrame:
        """
        集成学习策略

        组合多个策略的信号
        """
        df = df.copy()

        # 策略1：双均线
        df['ma_signal'] = 0
        df.loc[df['close'].rolling(5).mean() > df['close'].rolling(20).mean(), 'ma_signal'] = 1
        df.loc[df['close'].rolling(5).mean() < df['close'].rolling(20).mean(), 'ma_signal'] = -1

        # 策略2：RSI
        df['rsi_signal'] = 0
        rsi = 50  # 简化RSI
        df.loc[:, 'rsi_signal'] = 0

        # 策略3：成交量
        df['vol_signal'] = 0
        df.loc[df['volume'] > df['volume'].rolling(20).mean(), 'vol_signal'] = 1
        df.loc[df['volume'] < df['volume'].rolling(20).mean(), 'vol_signal'] = -1

        # 集成（投票法）
        df['vote'] = df['ma_signal'] + df['rsi_signal'] + df['vol_signal']

        df['signal'] = 0
        df.loc[df['vote'] >= 2, 'signal'] = 1  # 多数同意买入
        df.loc[df['vote'] <= -2, 'signal'] = -1  # 多数同意卖出

        return df


def test_ml_strategies():
    """测试机器学习策略"""
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

    # 测试机器学习分类策略
    print("机器学习分类策略：")
    result = MachineLearningStrategies.ml_classification_strategy(df)
    print(result[['close', 'score', 'signal']].tail(10))

    # 测试特征工程优化策略
    print("\n特征工程优化策略：")
    result = MachineLearningStrategies.feature_engineering_strategy(df)
    print(result[['close', 'feature_score', 'signal']].tail(10))

    # 测试集成学习策略
    print("\n集成学习策略：")
    result = MachineLearningStrategies.ensemble_strategy(df)
    print(result[['close', 'ma_signal', 'vol_signal', 'vote', 'signal']].tail(10))


if __name__ == '__main__':
    test_ml_strategies()
