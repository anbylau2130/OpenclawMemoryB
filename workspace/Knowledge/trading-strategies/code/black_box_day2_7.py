"""
《打开量化投资的黑箱》Day 2-7 策略实现
"""

import pandas as pd
import numpy as np


class FactorInvestingStrategies:
    """Day 2 - 因子投资策略"""

    @staticmethod
    def momentum_factor(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['momentum'] = df['close'].pct_change(20)
        df['signal'] = 0
        df.loc[df['momentum'] > df['momentum'].quantile(0.7), 'signal'] = 1
        df.loc[df['momentum'] < df['momentum'].quantile(0.3), 'signal'] = -1
        return df

    @staticmethod
    def value_factor(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['value'] = 1 / (df['close'] / df['close'].rolling(60).mean())
        df['signal'] = 0
        df.loc[df['value'] > df['value'].quantile(0.7), 'signal'] = 1
        df.loc[df['value'] < df['value'].quantile(0.3), 'signal'] = -1
        return df


class RiskModelStrategies:
    """Day 3 - 风险模型策略"""

    @staticmethod
    def risk_parity(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['volatility'] = df['close'].pct_change().rolling(20).std()
        df['risk_weight'] = 1 / df['volatility']
        df['signal'] = 0
        df.loc[df['risk_weight'] > df['risk_weight'].quantile(0.7), 'signal'] = 1
        return df

    @staticmethod
    def risk_budget(df: pd.DataFrame, budget: float = 0.02) -> pd.DataFrame:
        df = df.copy()
        df['var'] = df['close'].pct_change().rolling(20).quantile(0.05)
        df['signal'] = 0
        df.loc[df['var'].abs() < budget, 'signal'] = 1
        return df


class PortfolioOptimizationStrategies:
    """Day 4 - 组合优化策略"""

    @staticmethod
    def mean_variance(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['return'] = df['close'].pct_change(20)
        df['vol'] = df['close'].pct_change().rolling(20).std()
        df['sharpe'] = df['return'] / df['vol']
        df['signal'] = 0
        df.loc[df['sharpe'] > df['sharpe'].quantile(0.7), 'signal'] = 1
        return df

    @staticmethod
    def rebalance(df: pd.DataFrame, threshold: float = 0.1) -> pd.DataFrame:
        df = df.copy()
        df['target_weight'] = 0.5
        df['current_weight'] = df['close'] / df['close'].iloc[0]
        df['drift'] = abs(df['current_weight'] - df['target_weight'])
        df['signal'] = 0
        df.loc[df['drift'] > threshold, 'signal'] = 1
        return df


class ExecutionStrategies:
    """Day 5 - 执行算法策略"""

    @staticmethod
    def vwap(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['vwap'] = (df['close'] * df['volume']).rolling(20).sum() / df['volume'].rolling(20).sum()
        df['signal'] = 0
        df.loc[df['close'] < df['vwap'], 'signal'] = 1  # 低于VWAP买入
        df.loc[df['close'] > df['vwap'], 'signal'] = -1  # 高于VWAP卖出
        return df

    @staticmethod
    def twap(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['twap'] = df['close'].rolling(20).mean()
        df['signal'] = 0
        df.loc[df['close'] < df['twap'], 'signal'] = 1
        return df


class BacktestFrameworkStrategies:
    """Day 6 - 回测框架策略"""

    @staticmethod
    def event_driven(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['ma5'] = df['close'].rolling(5).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        df['signal'] = 0
        df.loc[df['ma5'] > df['ma20'], 'signal'] = 1
        df.loc[df['ma5'] < df['ma20'], 'signal'] = -1
        return df


class RiskManagementStrategies:
    """Day 7 - 风险管理策略"""

    @staticmethod
    def var_limit(df: pd.DataFrame, limit: float = 0.05) -> pd.DataFrame:
        df = df.copy()
        df['var_95'] = df['close'].pct_change().rolling(100).quantile(0.05)
        df['signal'] = 0
        df.loc[df['var_95'].abs() < limit, 'signal'] = 1
        return df

    @staticmethod
    def stress_test(df: pd.DataFrame, shock: float = -0.1) -> pd.DataFrame:
        df = df.copy()
        df['stressed_price'] = df['close'] * (1 + shock)
        df['loss'] = df['close'] - df['stressed_price']
        df['signal'] = 0
        df.loc[df['loss'].abs() < df['close'] * 0.05, 'signal'] = 1
        return df


def test_day2_7():
    """测试Day 2-7策略"""
    import pandas as pd
    import numpy as np

    dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(200) * 2)
    volume = np.random.randint(100000, 5000000, 200)
    df = pd.DataFrame({'close': close, 'volume': volume}, index=dates)

    print("Day 2 - 动量因子:", FactorInvestingStrategies.momentum_factor(df)['signal'].value_counts().to_dict())
    print("Day 3 - 风险平价:", RiskModelStrategies.risk_parity(df)['signal'].value_counts().to_dict())
    print("Day 4 - 均值方差:", PortfolioOptimizationStrategies.mean_variance(df)['signal'].value_counts().to_dict())
    print("Day 5 - VWAP:", ExecutionStrategies.vwap(df)['signal'].value_counts().to_dict())
    print("Day 6 - 事件驱动:", BacktestFrameworkStrategies.event_driven(df)['signal'].value_counts().to_dict())
    print("Day 7 - VaR限制:", RiskManagementStrategies.var_limit(df)['signal'].value_counts().to_dict())


if __name__ == '__main__':
    test_day2_7()
