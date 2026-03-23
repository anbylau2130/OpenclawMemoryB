"""
《日本蜡烛图技术》策略实现
"""

import pandas as pd
import numpy as np


class CandlestickStrategies:
    """蜡烛图形态策略"""

    @staticmethod
    def hammer(df: pd.DataFrame) -> pd.DataFrame:
        """锤子线（看涨）"""
        df = df.copy()
        df['body'] = abs(df['close'] - df['open'])
        df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
        df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['is_hammer'] = (
            (df['lower_shadow'] > 2 * df['body']) &
            (df['upper_shadow'] < df['body'] * 0.5)
        )
        df['signal'] = 0
        df.loc[df['is_hammer'], 'signal'] = 1
        return df

    @staticmethod
    def shooting_star(df: pd.DataFrame) -> pd.DataFrame:
        """流星线（看跌）"""
        df = df.copy()
        df['body'] = abs(df['close'] - df['open'])
        df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
        df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['is_star'] = (
            (df['upper_shadow'] > 2 * df['body']) &
            (df['lower_shadow'] < df['body'] * 0.5)
        )
        df['signal'] = 0
        df.loc[df['is_star'], 'signal'] = -1
        return df

    @staticmethod
    def bullish_engulfing(df: pd.DataFrame) -> pd.DataFrame:
        """看涨吞没"""
        df = df.copy()
        df['prev_bullish'] = df['close'].shift(1) > df['open'].shift(1)
        df['curr_bearish'] = df['close'] < df['open']
        df['engulfing'] = (
            (df['close'] > df['open'].shift(1)) &
            (df['open'] < df['close'].shift(1))
        )
        df['signal'] = 0
        df.loc[df['engulfing'] & df['prev_bullish'], 'signal'] = 1
        return df

    @staticmethod
    def bearish_engulfing(df: pd.DataFrame) -> pd.DataFrame:
        """看跌吞没"""
        df = df.copy()
        df['prev_bearish'] = df['close'].shift(1) < df['open'].shift(1)
        df['curr_bullish'] = df['close'] > df['open']
        df['engulfing'] = (
            (df['close'] < df['open'].shift(1)) &
            (df['open'] > df['close'].shift(1))
        )
        df['signal'] = 0
        df.loc[df['engulfing'] & df['prev_bearish'], 'signal'] = -1
        return df

    @staticmethod
    def doji(df: pd.DataFrame) -> pd.DataFrame:
        """十字星"""
        df = df.copy()
        df['body'] = abs(df['close'] - df['open'])
        df['range'] = df['high'] - df['low']
        df['is_doji'] = df['body'] < df['range'] * 0.1
        df['signal'] = 0
        df.loc[df['is_doji'], 'signal'] = 1  # 十字星表示反转可能
        return df

    @staticmethod
    def morning_star(df: pd.DataFrame) -> pd.DataFrame:
        """启明星（看涨）"""
        df = df.copy()
        df['day1_bearish'] = df['close'].shift(2) < df['open'].shift(2)
        df['day2_small'] = abs(df['close'].shift(1) - df['open'].shift(1)) < (df['high'].shift(1) - df['low'].shift(1)) * 0.3
        df['day3_bullish'] = df['close'] > df['open']
        df['is_morning'] = df['day1_bearish'] & df['day2_small'] & df['day3_bullish']
        df['signal'] = 0
        df.loc[df['is_morning'], 'signal'] = 1
        return df

    @staticmethod
    def evening_star(df: pd.DataFrame) -> pd.DataFrame:
        """黄昏星（看跌）"""
        df = df.copy()
        df['day1_bullish'] = df['close'].shift(2) > df['open'].shift(2)
        df['day2_small'] = abs(df['close'].shift(1) - df['open'].shift(1)) < (df['high'].shift(1) - df['low'].shift(1)) * 0.3
        df['day3_bearish'] = df['close'] < df['open']
        df['is_evening'] = df['day1_bullish'] & df['day2_small'] & df['day3_bearish']
        df['signal'] = 0
        df.loc[df['is_evening'], 'signal'] = -1
        return df

    @staticmethod
    def three_white_soldiers(df: pd.DataFrame) -> pd.DataFrame:
        """三只白兵（看涨）"""
        df = df.copy()
        df['day1_bullish'] = df['close'].shift(2) > df['open'].shift(2)
        df['day2_bullish'] = df['close'].shift(1) > df['open'].shift(1)
        df['day3_bullish'] = df['close'] > df['open']
        df['is_soldiers'] = df['day1_bullish'] & df['day2_bullish'] & df['day3_bullish']
        df['signal'] = 0
        df.loc[df['is_soldiers'], 'signal'] = 1
        return df

    @staticmethod
    def three_black_crows(df: pd.DataFrame) -> pd.DataFrame:
        """三只乌鸦（看跌）"""
        df = df.copy()
        df['day1_bearish'] = df['close'].shift(2) < df['open'].shift(2)
        df['day2_bearish'] = df['close'].shift(1) < df['open'].shift(1)
        df['day3_bearish'] = df['close'] < df['open']
        df['is_crows'] = df['day1_bearish'] & df['day2_bearish'] & df['day3_bearish']
        df['signal'] = 0
        df.loc[df['is_crows'], 'signal'] = -1
        return df

    @staticmethod
    def piercing_line(df: pd.DataFrame) -> pd.DataFrame:
        """刺透线（看涨）"""
        df = df.copy()
        df['day1_bearish'] = df['close'].shift(1) < df['open'].shift(1)
        df['day2_bullish'] = df['close'] > df['open']
        df['penetrates'] = df['close'] > (df['open'].shift(1) + df['close'].shift(1)) / 2
        df['is_piercing'] = df['day1_bearish'] & df['day2_bullish'] & df['penetrates']
        df['signal'] = 0
        df.loc[df['is_piercing'], 'signal'] = 1
        return df


def test_candlestick():
    """测试蜡烛图策略"""
    import pandas as pd
    import numpy as np

    dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(200) * 2)
    high = close + np.random.rand(200) * 3
    low = close - np.random.rand(200) * 3
    open_price = close + np.random.randn(200) * 1
    volume = np.random.randint(100000, 5000000, 200)
    df = pd.DataFrame({
        'open': open_price,
        'close': close,
        'high': high,
        'low': low,
        'volume': volume
    }, index=dates)

    print("锤子线:", CandlestickStrategies.hammer(df)['signal'].value_counts().to_dict())
    print("流星线:", CandlestickStrategies.shooting_star(df)['signal'].value_counts().to_dict())
    print("看涨吞没:", CandlestickStrategies.bullish_engulfing(df)['signal'].value_counts().to_dict())
    print("看跌吞没:", CandlestickStrategies.bearish_engulfing(df)['signal'].value_counts().to_dict())
    print("十字星:", CandlestickStrategies.doji(df)['signal'].value_counts().to_dict())
    print("启明星:", CandlestickStrategies.morning_star(df)['signal'].value_counts().to_dict())
    print("黄昏星:", CandlestickStrategies.evening_star(df)['signal'].value_counts().to_dict())
    print("三只白兵:", CandlestickStrategies.three_white_soldiers(df)['signal'].value_counts().to_dict())
    print("三只乌鸦:", CandlestickStrategies.three_black_crows(df)['signal'].value_counts().to_dict())
    print("刺透线:", CandlestickStrategies.piercing_line(df)['signal'].value_counts().to_dict())


if __name__ == '__main__':
    test_candlestick()
