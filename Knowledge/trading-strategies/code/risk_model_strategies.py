"""
Day 14 - 风险模型策略

实现Barra风险模型、风险归因、压力测试、尾部风险对冲策略
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class RiskModelStrategies:
    """风险模型策略库"""

    @staticmethod
    def barra_risk_model_strategy(df: pd.DataFrame) -> pd.DataFrame:
        """
        Barra风险模型策略

        基于多因子风险模型
        """
        df = df.copy()

        # 计算风格因子
        # 1. 市值因子（简化：用成交量代理）
        df['size_factor'] = np.log(df['volume'])

        # 2. 动量因子
        df['momentum_factor'] = df['close'].pct_change(20)

        # 3. 波动率因子
        df['volatility_factor'] = df['close'].pct_change().rolling(20).std()

        # 4. 流动性因子
        df['liquidity_factor'] = df['volume'] / df['volume'].rolling(20).mean()

        # 计算因子风险
        df['factor_risk'] = (
            df['size_factor'].pct_change().rolling(20).std() * 0.2 +
            df['momentum_factor'].rolling(20).std() * 0.3 +
            df['volatility_factor'].rolling(20).std() * 0.3 +
            df['liquidity_factor'].rolling(20).std() * 0.2
        )

        df['signal'] = 0
        # 风险低时买入
        df.loc[df['factor_risk'] < df['factor_risk'].quantile(0.3), 'signal'] = 1
        # 风险高时卖出
        df.loc[df['factor_risk'] > df['factor_risk'].quantile(0.7), 'signal'] = -1

        return df

    @staticmethod
    def risk_attribution_strategy(df: pd.DataFrame) -> pd.DataFrame:
        """
        风险归因策略

        分析风险来源
        """
        df = df.copy()

        # 计算总风险
        df['total_risk'] = df['close'].pct_change().rolling(20).std()

        # 计算系统性风险（市场风险）
        df['market_risk'] = df['close'].pct_change().rolling(60).std()

        # 计算特质风险
        df['idiosyncratic_risk'] = np.sqrt(df['total_risk']**2 - df['market_risk']**2 * 0.7)

        # 风险归因比例
        df['systematic_ratio'] = df['market_risk'] / df['total_risk']
        df['idiosyncratic_ratio'] = df['idiosyncratic_risk'] / df['total_risk']

        df['signal'] = 0
        # 系统性风险占比低时买入
        df.loc[df['systematic_ratio'] < 0.5, 'signal'] = 1
        # 系统性风险占比高时卖出
        df.loc[df['systematic_ratio'] > 0.8, 'signal'] = -1

        return df

    @staticmethod
    def stress_test_strategy(df: pd.DataFrame, shock: float = -0.1) -> pd.DataFrame:
        """
        压力测试策略

        模拟极端情况
        """
        df = df.copy()

        # 计算VaR
        df['var_95'] = df['close'].pct_change().rolling(100).quantile(0.05)
        df['var_99'] = df['close'].pct_change().rolling(100).quantile(0.01)

        # 计算压力测试损失
        df['stress_loss'] = df['close'] * shock

        # 计算回撤
        df['drawdown'] = (df['close'] - df['close'].cummax()) / df['close'].cummax()

        df['signal'] = 0
        # 压力测试损失小且回撤小
        df.loc[(df['stress_loss'].abs() < df['close'] * 0.05) & (df['drawdown'] > -0.1), 'signal'] = 1
        # 压力测试损失大或回撤大
        df.loc[(df['stress_loss'].abs() > df['close'] * 0.1) | (df['drawdown'] < -0.2), 'signal'] = -1

        return df

    @staticmethod
    def tail_risk_hedging_strategy(df: pd.DataFrame) -> pd.DataFrame:
        """
        尾部风险对冲策略

        管理极端风险
        """
        df = df.copy()

        # 计算尾部风险指标
        # 1. 偏度
        df['skewness'] = df['close'].pct_change().rolling(60).skew()

        # 2. 峰度
        df['kurtosis'] = df['close'].pct_change().rolling(60).kurt()

        # 3. 尾部VaR
        df['tail_var'] = df['close'].pct_change().rolling(100).quantile(0.01)

        # 尾部风险得分
        df['tail_risk_score'] = (
            (df['skewness'] < 0).astype(int) * 0.3 +
            (df['kurtosis'] > 3).astype(int) * 0.3 +
            (df['tail_var'] < -0.05).astype(int) * 0.4
        )

        df['signal'] = 0
        # 尾部风险低
        df.loc[df['tail_risk_score'] < 0.3, 'signal'] = 1
        # 尾部风险高，需要对冲
        df.loc[df['tail_risk_score'] > 0.7, 'signal'] = -1

        return df


def test_risk_model_strategies():
    """测试风险模型策略"""
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

    # 测试Barra风险模型策略
    print("Barra风险模型策略：")
    result = RiskModelStrategies.barra_risk_model_strategy(df)
    print(result[['close', 'factor_risk', 'signal']].tail(10))

    # 测试风险归因策略
    print("\n风险归因策略：")
    result = RiskModelStrategies.risk_attribution_strategy(df)
    print(result[['close', 'systematic_ratio', 'idiosyncratic_ratio', 'signal']].tail(10))

    # 测试压力测试策略
    print("\n压力测试策略：")
    result = RiskModelStrategies.stress_test_strategy(df)
    print(result[['close', 'var_95', 'drawdown', 'signal']].tail(10))

    # 测试尾部风险对冲策略
    print("\n尾部风险对冲策略：")
    result = RiskModelStrategies.tail_risk_hedging_strategy(df)
    print(result[['close', 'skewness', 'kurtosis', 'tail_risk_score', 'signal']].tail(10))


if __name__ == '__main__':
    test_risk_model_strategies()
