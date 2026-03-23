"""
Day 3 - 数据获取与处理策略

实现数据质量检测、异常值过滤、缺失值处理策略
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


class DataStrategies:
    """数据处理策略库"""

    @staticmethod
    def detect_anomalies(df: pd.DataFrame, z_threshold: float = 3.0) -> pd.DataFrame:
        """
        异常值检测

        使用Z-score检测异常值
        """
        df = df.copy()

        # 计算Z-score
        df['z_score'] = (df['close'] - df['close'].mean()) / df['close'].std()

        # 标记异常值
        df['is_anomaly'] = False
        df.loc[abs(df['z_score']) > z_threshold, 'is_anomaly'] = True

        return df

    @staticmethod
    def fill_missing_data(df: pd.DataFrame, method: str = 'linear') -> pd.DataFrame:
        """
        缺失值填充

        method: 'linear', 'forward', 'backward', 'mean'
        """
        df = df.copy()

        if method == 'linear':
            df = df.interpolate(method='linear')
        elif method == 'forward':
            df = df.fillna(method='ffill')
        elif method == 'backward':
            df = df.fillna(method='bfill')
        elif method == 'mean':
            df = df.fillna(df.mean())

        return df

    @staticmethod
    def data_quality_filter(df: pd.DataFrame, min_volume: int = 100000) -> pd.DataFrame:
        """
        数据质量过滤

        过滤成交量过小的数据
        """
        df = df.copy()
        df['quality_ok'] = df['volume'] >= min_volume
        return df

    @staticmethod
    def anomaly_trading_strategy(df: pd.DataFrame, z_threshold: float = 3.0) -> pd.DataFrame:
        """
        异常值交易策略

        买入：价格异常下跌（Z-score < -3）
        卖出：价格异常上涨（Z-score > 3）
        """
        df = df.copy()
        df = DataStrategies.detect_anomalies(df, z_threshold)

        df['signal'] = 0
        df.loc[df['z_score'] < -z_threshold, 'signal'] = 1  # 异常下跌，买入
        df.loc[df['z_score'] > z_threshold, 'signal'] = -1  # 异常上涨，卖出

        return df

    @staticmethod
    def volume_filter_strategy(df: pd.DataFrame, min_volume_ratio: float = 0.5) -> pd.DataFrame:
        """
        成交量过滤策略

        买入：成交量 > 平均成交量的50%
        卖出：成交量 < 平均成交量的50%
        """
        df = df.copy()
        df['avg_volume'] = df['volume'].rolling(20).mean()
        df['volume_ratio'] = df['volume'] / df['avg_volume']

        df['signal'] = 0
        df.loc[df['volume_ratio'] > min_volume_ratio, 'signal'] = 1
        df.loc[df['volume_ratio'] < min_volume_ratio, 'signal'] = -1

        return df

    @staticmethod
    def data_completeness_strategy(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
        """
        数据完整性策略

        买入：数据完整度高（无缺失）
        卖出：数据完整度低（有缺失）
        """
        df = df.copy()

        # 检查数据完整性
        df['completeness'] = df['close'].rolling(window).apply(lambda x: x.notna().sum() / len(x))

        df['signal'] = 0
        df.loc[df['completeness'] == 1.0, 'signal'] = 1  # 数据完整，买入
        df.loc[df['completeness'] < 0.8, 'signal'] = -1  # 数据缺失多，卖出

        return df


def test_data_strategies():
    """测试数据处理策略"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta

    # 生成模拟数据（包含异常值）
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    np.random.seed(42)

    close = 100 + np.cumsum(np.random.randn(100) * 2)
    # 添加异常值
    close[20] = 150  # 异常高
    close[50] = 60   # 异常低

    high = close + np.random.rand(100) * 3
    low = close - np.random.rand(100) * 3
    volume = np.random.randint(100000, 5000000, 100)

    df = pd.DataFrame({
        'close': close,
        'high': high,
        'low': low,
        'volume': volume
    }, index=dates)

    # 测试异常值交易策略
    print("异常值交易策略：")
    result = DataStrategies.anomaly_trading_strategy(df)
    print(result[['close', 'z_score', 'is_anomaly', 'signal']].tail(10))

    # 测试成交量过滤策略
    print("\n成交量过滤策略：")
    result = DataStrategies.volume_filter_strategy(df)
    print(result[['close', 'volume', 'volume_ratio', 'signal']].tail(10))

    # 测试数据完整性策略
    print("\n数据完整性策略：")
    result = DataStrategies.data_completeness_strategy(df)
    print(result[['close', 'completeness', 'signal']].tail(10))


if __name__ == '__main__':
    test_data_strategies()
