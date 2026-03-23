"""
Day 4 - 回测框架策略

实现交易成本优化、滑点控制策略
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class BacktestStrategies:
    """回测框架策略库"""

    @staticmethod
    def calculate_transaction_cost(price: float, shares: int, commission_rate: float = 0.0003) -> float:
        """计算交易成本"""
        return price * shares * commission_rate

    @staticmethod
    def calculate_slippage(price: float, slippage_rate: float = 0.001) -> float:
        """计算滑点"""
        return price * slippage_rate

    @staticmethod
    def commission_optimization_strategy(df: pd.DataFrame, min_trade_value: float = 10000) -> pd.DataFrame:
        """
        交易成本优化策略

        只在交易金额足够大时才交易，降低成本比例
        """
        df = df.copy()

        df['trade_value'] = df['close'] * 100  # 假设每次交易100股

        df['signal'] = 0
        # 交易金额 > 最小值时才交易
        df.loc[df['trade_value'] > min_trade_value, 'signal'] = 1

        return df

    @staticmethod
    def slippage_control_strategy(df: pd.DataFrame, max_slippage: float = 0.005) -> pd.DataFrame:
        """
        滑点控制策略

        在波动率低时交易，降低滑点影响
        """
        df = df.copy()

        # 计算波动率
        df['volatility'] = df['close'].pct_change().rolling(20).std()

        df['signal'] = 0
        # 波动率 < 阈值时交易
        df.loc[df['volatility'] < max_slippage, 'signal'] = 1

        return df

    @staticmethod
    def market_impact_strategy(df: pd.DataFrame, volume_threshold: float = 0.1) -> pd.DataFrame:
        """
        市场冲击策略

        在流动性好时交易，降低市场冲击
        """
        df = df.copy()

        # 计算成交量占比
        df['volume_ma'] = df['volume'].rolling(20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']

        df['signal'] = 0
        # 成交量 > 平均时交易（流动性好）
        df.loc[df['volume_ratio'] > volume_threshold, 'signal'] = 1

        return df

    @staticmethod
    def optimal_execution_strategy(df: pd.DataFrame, twap_periods: int = 5) -> pd.DataFrame:
        """
        最优执行策略（TWAP）

        分批交易，降低市场冲击
        """
        df = df.copy()

        # 简化版TWAP：在多个时段分批交易
        df['signal'] = 0

        # 每5个交易日交易一次
        for i in range(0, len(df), twap_periods):
            df.iloc[i, df.columns.get_loc('signal')] = 1

        return df


def test_backtest_strategies():
    """测试回测策略"""
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

    # 测试交易成本优化策略
    print("交易成本优化策略：")
    result = BacktestStrategies.commission_optimization_strategy(df)
    print(result[['close', 'trade_value', 'signal']].tail(10))

    # 测试滑点控制策略
    print("\n滑点控制策略：")
    result = BacktestStrategies.slippage_control_strategy(df)
    print(result[['close', 'volatility', 'signal']].tail(10))

    # 测试市场冲击策略
    print("\n市场冲击策略：")
    result = BacktestStrategies.market_impact_strategy(df)
    print(result[['close', 'volume_ratio', 'signal']].tail(10))

    # 测试最优执行策略
    print("\n最优执行策略（TWAP）：")
    result = BacktestStrategies.optimal_execution_strategy(df)
    print(result[['close', 'signal']].tail(10))


if __name__ == '__main__':
    test_backtest_strategies()
