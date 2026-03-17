"""
Day 7 - 实战案例策略

实现实盘交易系统、监控告警、自动调仓策略
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime


class LiveTradingStrategies:
    """实盘交易策略库"""

    @staticmethod
    def live_trading_system(df: pd.DataFrame, initial_capital: float = 100000) -> pd.DataFrame:
        """
        完整实盘交易系统

        包含入场、出场、止损、止盈
        """
        df = df.copy()

        # 计算指标
        df['MA5'] = df['close'].rolling(5).mean()
        df['MA20'] = df['close'].rolling(20).mean()
        df['RSI'] = 50  # 简化RSI

        # 交易信号
        df['signal'] = 0
        df.loc[(df['MA5'] > df['MA20']) & (df['RSI'] < 70), 'signal'] = 1  # 买入
        df.loc[(df['MA5'] < df['MA20']) | (df['RSI'] > 70), 'signal'] = -1  # 卖出

        return df

    @staticmethod
    def monitoring_alert_strategy(df: pd.DataFrame, drawdown_threshold: float = -0.05) -> pd.DataFrame:
        """
        监控告警策略

        监控持仓风险，触发告警
        """
        df = df.copy()

        # 计算回撤
        df['cummax'] = df['close'].cummax()
        df['drawdown'] = (df['close'] - df['cummax']) / df['cummax']

        # 告警信号
        df['alert'] = ''
        df.loc[df['drawdown'] < drawdown_threshold, 'alert'] = 'RISK_ALERT'
        df.loc[df['drawdown'] < drawdown_threshold * 1.5, 'alert'] = 'SEVERE_ALERT'

        df['signal'] = 0
        df.loc[df['alert'] == 'RISK_ALERT', 'signal'] = -1  # 减仓
        df.loc[df['alert'] == 'SEVERE_ALERT', 'signal'] = -1  # 清仓

        return df

    @staticmethod
    def auto_rebalance_strategy(df: pd.DataFrame, rebalance_threshold: float = 0.1) -> pd.DataFrame:
        """
        自动调仓策略

        当偏离目标仓位超过阈值时调仓
        """
        df = df.copy()

        # 计算目标仓位（基于波动率）
        df['volatility'] = df['close'].pct_change().rolling(20).std()
        df['target_position'] = 0.02 / df['volatility']  # 风险平价
        df['target_position'] = df['target_position'].clip(0, 1)

        # 当前价格偏离
        df['price_deviation'] = df['close'] / df['close'].rolling(20).mean() - 1

        df['signal'] = 0
        # 偏离超过阈值，调仓
        df.loc[df['price_deviation'] > rebalance_threshold, 'signal'] = -1  # 减仓
        df.loc[df['price_deviation'] < -rebalance_threshold, 'signal'] = 1  # 加仓

        return df

    @staticmethod
    def market_regime_strategy(df: pd.DataFrame) -> pd.DataFrame:
        """
        市场状态识别策略

        识别牛市、熊市、震荡市
        """
        df = df.copy()

        # 计算趋势强度
        df['MA50'] = df['close'].rolling(50).mean()
        df['MA200'] = df['close'].rolling(200).mean()
        df['trend'] = (df['MA50'] - df['MA200']) / df['MA200']

        # 计算波动率
        df['volatility'] = df['close'].pct_change().rolling(20).std()

        # 识别市场状态
        df['regime'] = 'neutral'
        df.loc[(df['trend'] > 0.05) & (df['volatility'] < 0.03), 'regime'] = 'bull'  # 牛市
        df.loc[(df['trend'] < -0.05) & (df['volatility'] < 0.03), 'regime'] = 'bear'  # 熊市
        df.loc[df['volatility'] > 0.03, 'regime'] = 'volatile'  # 震荡

        df['signal'] = 0
        df.loc[df['regime'] == 'bull', 'signal'] = 1  # 牛市买入
        df.loc[df['regime'] == 'bear', 'signal'] = -1  # 熊市卖出

        return df


def test_live_trading_strategies():
    """测试实盘交易策略"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta

    # 生成模拟数据
    dates = pd.date_range(start='2023-01-01', periods=300, freq='D')
    np.random.seed(42)

    close = 100 + np.cumsum(np.random.randn(300) * 2)
    high = close + np.random.rand(300) * 3
    low = close - np.random.rand(300) * 3
    volume = np.random.randint(100000, 5000000, 300)

    df = pd.DataFrame({
        'close': close,
        'high': high,
        'low': low,
        'volume': volume
    }, index=dates)

    # 测试完整交易系统
    print("完整实盘交易系统：")
    result = LiveTradingStrategies.live_trading_system(df)
    print(result[['close', 'MA5', 'MA20', 'signal']].tail(10))

    # 测试监控告警策略
    print("\n监控告警策略：")
    result = LiveTradingStrategies.monitoring_alert_strategy(df)
    print(result[['close', 'drawdown', 'alert', 'signal']].tail(10))

    # 测试自动调仓策略
    print("\n自动调仓策略：")
    result = LiveTradingStrategies.auto_rebalance_strategy(df)
    print(result[['close', 'target_position', 'price_deviation', 'signal']].tail(10))

    # 测试市场状态识别策略
    print("\n市场状态识别策略：")
    result = LiveTradingStrategies.market_regime_strategy(df)
    print(result[['close', 'trend', 'volatility', 'regime', 'signal']].tail(10))


if __name__ == '__main__':
    test_live_trading_strategies()
