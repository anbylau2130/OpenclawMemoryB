"""
Day 12 - 深度学习入门策略

实现LSTM预测、Transformer策略、强化学习交易策略
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class DeepLearningStrategies:
    """深度学习策略库"""

    @staticmethod
    def lstm_prediction_strategy(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """
        LSTM预测策略（简化版）

        使用历史数据模拟LSTM预测
        """
        df = df.copy()

        # 模拟LSTM预测（使用移动平均代替）
        df['lstm_pred'] = df['close'].rolling(window).mean().shift(-1)

        # 计算预测误差
        df['pred_error'] = abs(df['close'] - df['lstm_pred']) / df['close']

        # 预测趋势
        df['pred_trend'] = (df['lstm_pred'] - df['close']) / df['close']

        df['signal'] = 0
        # 预测上涨且误差小
        df.loc[(df['pred_trend'] > 0.02) & (df['pred_error'] < 0.05), 'signal'] = 1
        # 预测下跌且误差小
        df.loc[(df['pred_trend'] < -0.02) & (df['pred_error'] < 0.05), 'signal'] = -1

        return df

    @staticmethod
    def transformer_strategy(df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
        """
        Transformer策略（简化版）

        使用注意力机制模拟
        """
        df = df.copy()

        # 计算注意力权重（基于相关性）
        for i in range(1, window + 1):
            df[f'weight_{i}'] = df['close'].pct_change(i).abs()

        # 计算加权平均
        weight_cols = [f'weight_{i}' for i in range(1, window + 1)]
        df['attention_sum'] = df[weight_cols].sum(axis=1)

        # 归一化权重
        for col in weight_cols:
            df[col] = df[col] / df['attention_sum']

        # 计算注意力加权价格
        df['attention_price'] = 0
        for i in range(1, window + 1):
            df['attention_price'] += df[f'weight_{i}'] * df['close'].shift(i)

        # 计算趋势
        df['attention_trend'] = (df['attention_price'] - df['close']) / df['close']

        df['signal'] = 0
        df.loc[df['attention_trend'] > 0.03, 'signal'] = 1
        df.loc[df['attention_trend'] < -0.03, 'signal'] = -1

        return df

    @staticmethod
    def reinforcement_learning_strategy(df: pd.DataFrame, episodes: int = 100) -> pd.DataFrame:
        """
        强化学习策略（简化版）

        使用Q-learning模拟
        """
        df = df.copy()

        # 状态：收益率、波动率
        df['state_return'] = (df['close'].pct_change() > 0).astype(int)
        df['state_volatility'] = (df['close'].pct_change().rolling(10).std() > df['close'].pct_change().rolling(20).std()).astype(int)

        # 简化的Q表（状态 -> 动作）
        q_table = {
            (0, 0): 0,  # 下跌 + 低波动 -> 持有
            (0, 1): -1,  # 下跌 + 高波动 -> 卖出
            (1, 0): 1,  # 上涨 + 低波动 -> 买入
            (1, 1): 0,  # 上涨 + 高波动 -> 持有
        }

        # 根据状态选择动作
        df['signal'] = df.apply(
            lambda row: q_table.get((row['state_return'], row['state_volatility']), 0),
            axis=1
        )

        return df


def test_dl_strategies():
    """测试深度学习策略"""
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

    # 测试LSTM预测策略
    print("LSTM预测策略：")
    result = DeepLearningStrategies.lstm_prediction_strategy(df)
    print(result[['close', 'lstm_pred', 'pred_trend', 'signal']].tail(10))

    # 测试Transformer策略
    print("\nTransformer策略：")
    result = DeepLearningStrategies.transformer_strategy(df)
    print(result[['close', 'attention_price', 'attention_trend', 'signal']].tail(10))

    # 测试强化学习策略
    print("\n强化学习策略：")
    result = DeepLearningStrategies.reinforcement_learning_strategy(df)
    print(result[['close', 'state_return', 'state_volatility', 'signal']].tail(10))


if __name__ == '__main__':
    test_dl_strategies()
