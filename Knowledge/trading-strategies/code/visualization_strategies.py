"""
Day 8 - 数据可视化策略

实现图表形态识别、趋势线突破、支撑阻力可视化策略
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class VisualizationStrategies:
    """数据可视化策略库"""

    @staticmethod
    def identify_chart_patterns(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """
        图表形态识别策略

        识别头肩顶、头肩底、双顶、双底等形态
        """
        df = df.copy()

        # 计算局部高点和低点
        df['local_high'] = df['high'].rolling(window, center=True).max()
        df['local_low'] = df['low'].rolling(window, center=True).min()

        # 识别双顶形态
        df['double_top'] = (
            (df['high'] == df['local_high']) &
            (df['high'].shift(-window) == df['local_high'].shift(-window))
        )

        # 识别双底形态
        df['double_bottom'] = (
            (df['low'] == df['local_low']) &
            (df['low'].shift(-window) == df['local_low'].shift(-window))
        )

        df['signal'] = 0
        df.loc[df['double_bottom'], 'signal'] = 1  # 双底买入
        df.loc[df['double_top'], 'signal'] = -1  # 双顶卖出

        return df

    @staticmethod
    def trendline_breakout_strategy(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """
        趋势线突破策略

        识别上升趋势线和下降趋势线突破
        """
        df = df.copy()

        # 计算趋势线（简化版：线性回归）
        df['trend'] = df['close'].rolling(window).apply(
            lambda x: np.polyfit(np.arange(len(x)), x, 1)[0] if len(x) == window else 0
        )

        # 计算趋势线价格
        df['trendline'] = df['close'].rolling(window).mean()

        df['signal'] = 0
        # 价格突破上升趋势线
        df.loc[(df['close'] > df['trendline']) & (df['trend'] > 0), 'signal'] = 1
        # 价格跌破下降趋势线
        df.loc[(df['close'] < df['trendline']) & (df['trend'] < 0), 'signal'] = -1

        return df

    @staticmethod
    def support_resistance_visualization(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """
        支撑阻力可视化策略

        识别支撑位和阻力位
        """
        df = df.copy()

        # 计算支撑位（局部低点）
        df['support'] = df['low'].rolling(window).min()

        # 计算阻力位（局部高点）
        df['resistance'] = df['high'].rolling(window).max()

        # 计算价格位置（0-1之间）
        df['price_position'] = (df['close'] - df['support']) / (df['resistance'] - df['support'])

        df['signal'] = 0
        # 价格触及支撑位
        df.loc[df['price_position'] < 0.2, 'signal'] = 1
        # 价格触及阻力位
        df.loc[df['price_position'] > 0.8, 'signal'] = -1

        return df

    @staticmethod
    def candlestick_pattern_strategy(df: pd.DataFrame) -> pd.DataFrame:
        """
        K线形态识别策略

        识别锤子线、上吊线、吞没形态等
        """
        df = df.copy()

        # 计算实体大小
        df['body'] = abs(df['close'] - df['open'])
        df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']

        # 识别锤子线（看涨）
        df['hammer'] = (
            (df['lower_shadow'] > 2 * df['body']) &
            (df['upper_shadow'] < df['body'] * 0.5)
        )

        # 识别上吊线（看跌）
        df['hanging_man'] = (
            (df['upper_shadow'] > 2 * df['body']) &
            (df['lower_shadow'] < df['body'] * 0.5)
        )

        # 识别看涨吞没
        df['bullish_engulfing'] = (
            (df['close'] > df['open']) &
            (df['close'].shift(1) < df['open'].shift(1)) &
            (df['close'] > df['open'].shift(1)) &
            (df['open'] < df['close'].shift(1))
        )

        # 识别看跌吞没
        df['bearish_engulfing'] = (
            (df['close'] < df['open']) &
            (df['close'].shift(1) > df['open'].shift(1)) &
            (df['close'] < df['open'].shift(1)) &
            (df['open'] > df['close'].shift(1))
        )

        df['signal'] = 0
        df.loc[df['hammer'] | df['bullish_engulfing'], 'signal'] = 1
        df.loc[df['hanging_man'] | df['bearish_engulfing'], 'signal'] = -1

        return df


def test_visualization_strategies():
    """测试可视化策略"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta

    # 生成模拟数据
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    np.random.seed(42)

    close = 100 + np.cumsum(np.random.randn(100) * 2)
    high = close + np.random.rand(100) * 3
    low = close - np.random.rand(100) * 3
    open_price = close + np.random.randn(100) * 1
    volume = np.random.randint(100000, 5000000, 100)

    df = pd.DataFrame({
        'open': open_price,
        'close': close,
        'high': high,
        'low': low,
        'volume': volume
    }, index=dates)

    # 测试图表形态识别策略
    print("图表形态识别策略：")
    result = VisualizationStrategies.identify_chart_patterns(df)
    print(result[['close', 'double_top', 'double_bottom', 'signal']].tail(10))

    # 测试趋势线突破策略
    print("\n趋势线突破策略：")
    result = VisualizationStrategies.trendline_breakout_strategy(df)
    print(result[['close', 'trend', 'trendline', 'signal']].tail(10))

    # 测试支撑阻力可视化策略
    print("\n支撑阻力可视化策略：")
    result = VisualizationStrategies.support_resistance_visualization(df)
    print(result[['close', 'support', 'resistance', 'price_position', 'signal']].tail(10))

    # 测试K线形态识别策略
    print("\nK线形态识别策略：")
    result = VisualizationStrategies.candlestick_pattern_strategy(df)
    print(result[['close', 'hammer', 'hanging_man', 'signal']].tail(10))


if __name__ == '__main__':
    test_visualization_strategies()
