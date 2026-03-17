"""
Day 5 - 风险管理策略

实现VaR止损、动态仓位管理、风险平价策略
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


class RiskStrategies:
    """风险管理策略库"""

    @staticmethod
    def calculate_var(df: pd.DataFrame, confidence: float = 0.95, window: int = 20) -> pd.Series:
        """计算VaR（风险价值）"""
        returns = df['close'].pct_change()
        var = returns.rolling(window).quantile(1 - confidence)
        return var

    @staticmethod
    def calculate_sharpe_ratio(df: pd.DataFrame, risk_free_rate: float = 0.03, window: int = 20) -> pd.Series:
        """计算夏普比率"""
        returns = df['close'].pct_change()
        excess_returns = returns - risk_free_rate / 252

        sharpe = excess_returns.rolling(window).mean() / excess_returns.rolling(window).std()
        return sharpe * np.sqrt(252)

    @staticmethod
    def var_stop_loss_strategy(df: pd.DataFrame, confidence: float = 0.95, var_threshold: float = -0.05) -> pd.DataFrame:
        """
        VaR止损策略

        当VaR超过阈值时止损
        """
        df = df.copy()
        df['VaR'] = RiskStrategies.calculate_var(df, confidence)

        df['signal'] = 0
        # VaR超过阈值，卖出止损
        df.loc[df['VaR'] < var_threshold, 'signal'] = -1

        return df

    @staticmethod
    def dynamic_position_sizing(df: pd.DataFrame, target_volatility: float = 0.02) -> pd.DataFrame:
        """
        动态仓位管理策略

        根据波动率调整仓位
        """
        df = df.copy()

        # 计算波动率
        df['volatility'] = df['close'].pct_change().rolling(20).std()

        # 计算仓位比例
        df['position_ratio'] = target_volatility / df['volatility']
        df['position_ratio'] = df['position_ratio'].clip(0, 1)  # 限制在0-1之间

        df['signal'] = 0
        # 仓位比例 > 0.5时买入
        df.loc[df['position_ratio'] > 0.5, 'signal'] = 1
        df.loc[df['position_ratio'] < 0.3, 'signal'] = -1

        return df

    @staticmethod
    def risk_parity_strategy(df: pd.DataFrame, target_risk: float = 0.15) -> pd.DataFrame:
        """
        风险平价策略

        根据风险贡献分配仓位
        """
        df = df.copy()

        # 计算波动率
        df['volatility'] = df['close'].pct_change().rolling(20).std() * np.sqrt(252)

        # 计算风险贡献
        df['risk_contribution'] = df['volatility'] / target_risk

        df['signal'] = 0
        # 风险贡献 < 1时买入（风险较低）
        df.loc[df['risk_contribution'] < 1.0, 'signal'] = 1
        df.loc[df['risk_contribution'] > 1.2, 'signal'] = -1

        return df

    @staticmethod
    def max_drawdown_control_strategy(df: pd.DataFrame, max_drawdown: float = 0.1) -> pd.DataFrame:
        """
        最大回撤控制策略

        当回撤超过阈值时减仓
        """
        df = df.copy()

        # 计算累计收益
        df['cummax'] = df['close'].cummax()
        df['drawdown'] = (df['close'] - df['cummax']) / df['cummax']

        df['signal'] = 0
        # 回撤超过阈值，卖出
        df.loc[df['drawdown'] < -max_drawdown, 'signal'] = -1

        return df


def test_risk_strategies():
    """测试风险管理策略"""
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

    # 测试VaR止损策略
    print("VaR止损策略：")
    result = RiskStrategies.var_stop_loss_strategy(df)
    print(result[['close', 'VaR', 'signal']].tail(10))

    # 测试动态仓位管理策略
    print("\n动态仓位管理策略：")
    result = RiskStrategies.dynamic_position_sizing(df)
    print(result[['close', 'volatility', 'position_ratio', 'signal']].tail(10))

    # 测试风险平价策略
    print("\n风险平价策略：")
    result = RiskStrategies.risk_parity_strategy(df)
    print(result[['close', 'volatility', 'risk_contribution', 'signal']].tail(10))

    # 测试最大回撤控制策略
    print("\n最大回撤控制策略：")
    result = RiskStrategies.max_drawdown_control_strategy(df)
    print(result[['close', 'drawdown', 'signal']].tail(10))


if __name__ == '__main__':
    test_risk_strategies()
