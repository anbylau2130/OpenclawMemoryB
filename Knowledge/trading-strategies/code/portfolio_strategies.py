"""
Day 6 - 组合优化策略

实现均值方差优化、风险预算、多因子组合策略
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class PortfolioStrategies:
    """组合优化策略库"""

    @staticmethod
    def calculate_portfolio_return(returns: pd.DataFrame, weights: np.ndarray) -> float:
        """计算组合收益率"""
        return np.dot(returns.mean(), weights) * 252

    @staticmethod
    def calculate_portfolio_volatility(returns: pd.DataFrame, weights: np.ndarray) -> float:
        """计算组合波动率"""
        return np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))

    @staticmethod
    def mean_variance_optimization_strategy(df: pd.DataFrame, target_return: float = 0.15) -> pd.DataFrame:
        """
        均值方差优化策略

        在目标收益下最小化风险
        """
        df = df.copy()

        # 计算收益率
        returns = df['close'].pct_change()

        # 计算统计量
        mean_return = returns.mean() * 252
        volatility = returns.std() * np.sqrt(252)

        # 简化版：根据夏普比率决定仓位
        sharpe_ratio = mean_return / volatility if volatility > 0 else 0

        df['signal'] = 0
        # 夏普比率 > 0.5时买入
        df.loc[sharpe_ratio > 0.5, 'signal'] = 1
        df.loc[sharpe_ratio < 0, 'signal'] = -1

        return df

    @staticmethod
    def risk_budget_strategy(df: pd.DataFrame, risk_budget: float = 0.02) -> pd.DataFrame:
        """
        风险预算策略

        根据风险预算分配仓位
        """
        df = df.copy()

        # 计算波动率
        df['volatility'] = df['close'].pct_change().rolling(20).std() * np.sqrt(252)

        # 计算仓位
        df['position'] = risk_budget / df['volatility']
        df['position'] = df['position'].clip(0, 1)

        df['signal'] = 0
        df.loc[df['position'] > 0.5, 'signal'] = 1
        df.loc[df['position'] < 0.3, 'signal'] = -1

        return df

    @staticmethod
    def multi_factor_strategy(df: pd.DataFrame) -> pd.DataFrame:
        """
        多因子组合策略

        综合动量、价值、质量因子
        """
        df = df.copy()

        # 动量因子
        df['momentum'] = df['close'].pct_change(20)

        # 价值因子（简化：价格偏离MA）
        df['value'] = (df['close'] - df['close'].rolling(50).mean()) / df['close'].rolling(50).mean()

        # 质量因子（简化：波动率倒数）
        df['quality'] = 1 / df['close'].pct_change().rolling(20).std()

        # 综合得分
        df['score'] = df['momentum'] * 0.4 + df['value'] * 0.3 + df['quality'] * 0.3

        df['signal'] = 0
        df.loc[df['score'] > df['score'].quantile(0.7), 'signal'] = 1
        df.loc[df['score'] < df['score'].quantile(0.3), 'signal'] = -1

        return df

    @staticmethod
    def kelly_criterion_strategy(df: pd.DataFrame, kelly_fraction: float = 0.25) -> pd.DataFrame:
        """
        凯利公式策略

        根据凯利公式计算最优仓位
        """
        df = df.copy()

        # 计算收益率统计
        returns = df['close'].pct_change()
        win_rate = (returns > 0).rolling(50).mean()
        avg_win = returns[returns > 0].rolling(50).mean()
        avg_loss = abs(returns[returns < 0].rolling(50).mean())

        # 凯利公式
        kelly_ratio = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        kelly_ratio = kelly_ratio * kelly_fraction  # 使用部分凯利

        df['signal'] = 0
        df.loc[kelly_ratio > 0.1, 'signal'] = 1
        df.loc[kelly_ratio < 0, 'signal'] = -1

        return df


def test_portfolio_strategies():
    """测试组合优化策略"""
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

    # 测试均值方差优化策略
    print("均值方差优化策略：")
    result = PortfolioStrategies.mean_variance_optimization_strategy(df)
    print(result[['close', 'signal']].tail(10))

    # 测试风险预算策略
    print("\n风险预算策略：")
    result = PortfolioStrategies.risk_budget_strategy(df)
    print(result[['close', 'volatility', 'position', 'signal']].tail(10))

    # 测试多因子策略
    print("\n多因子组合策略：")
    result = PortfolioStrategies.multi_factor_strategy(df)
    print(result[['close', 'momentum', 'value', 'quality', 'score', 'signal']].tail(10))

    # 测试凯利公式策略
    print("\n凯利公式策略：")
    result = PortfolioStrategies.kelly_criterion_strategy(df)
    print(result[['close', 'signal']].tail(10))


if __name__ == '__main__':
    test_portfolio_strategies()
