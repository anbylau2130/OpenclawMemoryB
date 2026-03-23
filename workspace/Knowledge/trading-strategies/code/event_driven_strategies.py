"""
Day 9 - 事件驱动回测策略

实现事件驱动回测框架、订单管理、撮合引擎优化策略
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime
from queue import Queue


class EventDrivenStrategies:
    """事件驱动回测策略库"""

    @staticmethod
    def event_driven_backtest(df: pd.DataFrame, initial_capital: float = 100000) -> pd.DataFrame:
        """
        事件驱动回测框架

        基于事件驱动的回测系统
        """
        df = df.copy()

        # 初始化事件队列
        events = Queue()
        position = 0
        capital = initial_capital

        # 生成事件
        for i in range(len(df)):
            events.put({
                'type': 'market',
                'date': df.index[i],
                'price': df['close'].iloc[i]
            })

        # 处理事件
        results = []
        while not events.empty():
            event = events.get()

            if event['type'] == 'market':
                # 简单的双均线策略
                ma5 = df['close'].rolling(5).mean().iloc[i]
                ma20 = df['close'].rolling(20).mean().iloc[i]

                if ma5 > ma20 and position == 0:
                    # 买入
                    shares = int(capital * 0.95 / event['price'])
                    capital -= shares * event['price']
                    position = shares
                    results.append({
                        'date': event['date'],
                        'action': 'buy',
                        'price': event['price'],
                        'shares': shares
                    })

                elif ma5 < ma20 and position > 0:
                    # 卖出
                    capital += position * event['price']
                    results.append({
                        'date': event['date'],
                        'action': 'sell',
                        'price': event['price'],
                        'shares': position
                    })
                    position = 0

        df['signal'] = 0
        # 基于事件驱动生成信号
        for result in results:
            if result['action'] == 'buy':
                df.loc[result['date'], 'signal'] = 1
            elif result['action'] == 'sell':
                df.loc[result['date'], 'signal'] = -1

        return df

    @staticmethod
    def order_management_strategy(df: pd.DataFrame, max_orders: int = 5) -> pd.DataFrame:
        """
        订单管理策略

        限制同时持有的订单数量
        """
        df = df.copy()

        # 计算信号
        df['MA5'] = df['close'].rolling(5).mean()
        df['MA20'] = df['close'].rolling(20).mean()

        df['signal'] = 0
        order_count = 0

        for i in range(len(df)):
            if df['MA5'].iloc[i] > df['MA20'].iloc[i] and order_count < max_orders:
                df.iloc[i, df.columns.get_loc('signal')] = 1
                order_count += 1
            elif df['MA5'].iloc[i] < df['MA20'].iloc[i] and order_count > 0:
                df.iloc[i, df.columns.get_loc('signal')] = -1
                order_count -= 1

        return df

    @staticmethod
    def matching_engine_strategy(df: pd.DataFrame, slippage: float = 0.001) -> pd.DataFrame:
        """
        撮合引擎优化策略

        模拟真实的撮合过程
        """
        df = df.copy()

        # 计算信号
        df['RSI'] = 50  # 简化RSI
        df['signal'] = 0
        df.loc[df['RSI'] < 30, 'signal'] = 1
        df.loc[df['RSI'] > 70, 'signal'] = -1

        # 添加滑点
        df['execution_price'] = df['close'] * (1 + slippage * np.random.randn(len(df)))

        return df


def test_event_driven_strategies():
    """测试事件驱动策略"""
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

    # 测试事件驱动回测框架
    print("事件驱动回测框架：")
    result = EventDrivenStrategies.event_driven_backtest(df)
    print(result[['close', 'signal']].tail(10))

    # 测试订单管理策略
    print("\n订单管理策略：")
    result = EventDrivenStrategies.order_management_strategy(df)
    print(result[['close', 'MA5', 'MA20', 'signal']].tail(10))

    # 测试撮合引擎优化策略
    print("\n撮合引擎优化策略：")
    result = EventDrivenStrategies.matching_engine_strategy(df)
    print(result[['close', 'execution_price', 'signal']].tail(10))


if __name__ == '__main__':
    test_event_driven_strategies()
