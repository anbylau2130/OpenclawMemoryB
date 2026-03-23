"""
《打开量化投资的黑箱》Day 15-21 策略实现
"""

import pandas as pd
import numpy as np


class StrategyCombinations:
    """Day 15 - 策略组合"""

    @staticmethod
    def multi_strategy_combo(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # 策略1: 均值回归
        df['s1'] = (df['close'] < df['close'].rolling(20).mean()).astype(int)
        # 策略2: 动量
        df['s2'] = (df['close'].pct_change(10) > 0).astype(int)
        # 组合
        df['vote'] = df['s1'] + df['s2']
        df['signal'] = 0
        df.loc[df['vote'] >= 2, 'signal'] = 1
        return df


class LeverageManagement:
    """Day 16 - 杠杆管理"""

    @staticmethod
    def dynamic_leverage(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['volatility'] = df['close'].pct_change().rolling(20).std()
        df['leverage'] = 0.02 / df['volatility']  # 波动率目标2%
        df['leverage'] = df['leverage'].clip(0.5, 2.0)
        df['signal'] = df['leverage'] - 1  # 正数做多，负数做空
        return df


class TransactionCosts:
    """Day 17 - 交易成本"""

    @staticmethod
    def cost_optimization(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['turnover'] = df['close'].pct_change().abs().rolling(20).sum()
        df['signal'] = 0
        df.loc[df['turnover'] < df['turnover'].quantile(0.3), 'signal'] = 1  # 低换手率买入
        return df


class LiquidityManagement:
    """Day 18 - 流动性管理"""

    @staticmethod
    def liquidity_adjusted(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['liquidity'] = df['volume'] * df['close']
        df['liq_ma'] = df['liquidity'].rolling(20).mean()
        df['signal'] = 0
        df.loc[df['liquidity'] > df['liq_ma'], 'signal'] = 1  # 流动性高时买入
        return df


class TailRiskHedging:
    """Day 19 - 尾部风险对冲"""

    @staticmethod
    def var_hedge(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['var_99'] = df['close'].pct_change().rolling(100).quantile(0.01)
        df['signal'] = 0
        df.loc[df['var_99'] > -0.05, 'signal'] = 1  # 风险低时买入
        return df


class PerformanceAttribution:
    """Day 20 - 绩效归因"""

    @staticmethod
    def factor_attribution(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['market_factor'] = df['close'].pct_change(20)
        df['size_factor'] = np.log(df['volume'])
        df['value_factor'] = 1 / df['close'].rolling(60).mean()
        df['alpha'] = df['market_factor'] - df['market_factor'].mean()
        df['signal'] = 0
        df.loc[df['alpha'] > 0, 'signal'] = 1
        return df


class TradingSystem:
    """Day 21 - 完整交易系统"""

    @staticmethod
    def complete_system(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # 1. 信号生成
        df['ma_signal'] = (df['close'].rolling(5).mean() > df['close'].rolling(20).mean()).astype(int)
        # 2. 风险管理
        df['risk_signal'] = (df['close'].pct_change().rolling(20).std() < 0.02).astype(int)
        # 3. 执行优化
        df['exec_signal'] = (df['close'] < (df['close'] * df['volume']).rolling(20).sum() / df['volume'].rolling(20).sum()).astype(int)
        # 4. 组合决策
        df['final_signal'] = df['ma_signal'] + df['risk_signal'] + df['exec_signal']
        df['signal'] = 0
        df.loc[df['final_signal'] >= 2, 'signal'] = 1
        df.loc[df['final_signal'] <= 0, 'signal'] = -1
        return df


def test_day15_21():
    """测试Day 15-21策略"""
    import pandas as pd
    import numpy as np

    dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(200) * 2)
    volume = np.random.randint(100000, 5000000, 200)
    df = pd.DataFrame({'close': close, 'volume': volume}, index=dates)

    print("Day 15 - 策略组合:", StrategyCombinations.multi_strategy_combo(df)['signal'].value_counts().to_dict())
    print("Day 16 - 动态杠杆:", LeverageManagement.dynamic_leverage(df)['signal'].mean())
    print("Day 17 - 成本优化:", TransactionCosts.cost_optimization(df)['signal'].value_counts().to_dict())
    print("Day 18 - 流动性:", LiquidityManagement.liquidity_adjusted(df)['signal'].value_counts().to_dict())
    print("Day 19 - 尾部对冲:", TailRiskHedging.var_hedge(df)['signal'].value_counts().to_dict())
    print("Day 20 - 绩效归因:", PerformanceAttribution.factor_attribution(df)['signal'].value_counts().to_dict())
    print("Day 21 - 完整系统:", TradingSystem.complete_system(df)['signal'].value_counts().to_dict())


if __name__ == '__main__':
    test_day15_21()
