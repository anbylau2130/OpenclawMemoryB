"""
Day 2 - 技术指标策略

实现趋势、震荡、成交量、波动率指标策略
"""

import pandas as pd
import numpy as np
from typing import Dict


class TechnicalIndicators:
    """技术指标库"""

    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> Dict:
        """计算ADX指标"""
        high = df['high']
        low = df['low']
        close = df['close']

        # 计算+DM和-DM
        plus_dm = high.diff()
        minus_dm = -low.diff()

        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0

        # 计算TR
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # 计算ATR
        atr = tr.rolling(period).mean()

        # 计算+DI和-DI
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr)

        # 计算DX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)

        # 计算ADX
        adx = dx.rolling(period).mean()

        return {
            'adx': adx,
            'plus_di': plus_di,
            'minus_di': minus_di
        }

    @staticmethod
    def calculate_kdj(df: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> Dict:
        """计算KDJ指标"""
        low_n = df['low'].rolling(n).min()
        high_n = df['high'].rolling(n).max()

        rsv = (df['close'] - low_n) / (high_n - low_n) * 100

        k = rsv.ewm(alpha=1/m1, adjust=False).mean()
        d = k.ewm(alpha=1/m2, adjust=False).mean()
        j = 3 * k - 2 * d

        return {
            'K': k,
            'D': d,
            'J': j
        }

    @staticmethod
    def calculate_cci(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """计算CCI指标"""
        tp = (df['high'] + df['low'] + df['close']) / 3
        ma = tp.rolling(period).mean()
        md = tp.rolling(period).apply(lambda x: np.abs(x - x.mean()).mean())

        cci = (tp - ma) / (0.015 * md)

        return cci

    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.Series:
        """计算OBV指标"""
        obv = [0]

        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.append(obv[-1] + df['volume'].iloc[i])
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.append(obv[-1] - df['volume'].iloc[i])
            else:
                obv.append(obv[-1])

        return pd.Series(obv, index=df.index)

    @staticmethod
    def calculate_vwap(df: pd.DataFrame) -> pd.Series:
        """计算VWAP指标"""
        vwap = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
        return vwap

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """计算ATR指标"""
        high = df['high']
        low = df['low']
        close = df['close']

        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()

        return atr

    @staticmethod
    def calculate_keltner(df: pd.DataFrame, period: int = 20, atr_mult: float = 2.0) -> Dict:
        """计算肯特纳通道"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        atr = TechnicalIndicators.calculate_atr(df, period)

        middle = typical_price.rolling(period).mean()
        upper = middle + (atr * atr_mult)
        lower = middle - (atr * atr_mult)

        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }


class TechnicalStrategies:
    """技术指标策略库"""

    @staticmethod
    def adx_trend_strategy(df: pd.DataFrame, period: int = 14, threshold: int = 25) -> pd.DataFrame:
        """
        ADX趋势跟踪策略

        买入：ADX > 25 且 +DI > -DI
        卖出：ADX > 25 且 +DI < -DI
        """
        df = df.copy()
        adx_dict = TechnicalIndicators.calculate_adx(df, period)
        df['ADX'] = adx_dict['adx']
        df['+DI'] = adx_dict['plus_di']
        df['-DI'] = adx_dict['minus_di']

        df['signal'] = 0
        df.loc[(df['ADX'] > threshold) & (df['+DI'] > df['-DI']), 'signal'] = 1
        df.loc[(df['ADX'] > threshold) & (df['+DI'] < df['-DI']), 'signal'] = -1

        return df

    @staticmethod
    def kdj_strategy(df: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
        """
        KDJ金叉死叉策略

        买入：K上穿D且J<20（超卖区金叉）
        卖出：K下穿D且J>80（超买区死叉）
        """
        df = df.copy()
        kdj_dict = TechnicalIndicators.calculate_kdj(df, n, m1, m2)
        df['K'] = kdj_dict['K']
        df['D'] = kdj_dict['D']
        df['J'] = kdj_dict['J']

        df['signal'] = 0
        # K上穿D且J<20
        df.loc[(df['K'] > df['D']) & (df['K'].shift(1) <= df['D'].shift(1)) & (df['J'] < 20), 'signal'] = 1
        # K下穿D且J>80
        df.loc[(df['K'] < df['D']) & (df['K'].shift(1) >= df['D'].shift(1)) & (df['J'] > 80), 'signal'] = -1

        return df

    @staticmethod
    def obv_divergence_strategy(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """
        OBV量价背离策略

        买入：价格下跌，OBV上升（底背离）
        卖出：价格上涨，OBV下降（顶背离）
        """
        df = df.copy()
        df['OBV'] = TechnicalIndicators.calculate_obv(df)

        # 计算价格和OBV的趋势
        df['price_trend'] = df['close'].diff(period)
        df['obv_trend'] = df['OBV'].diff(period)

        df['signal'] = 0
        # 底背离
        df.loc[(df['price_trend'] < 0) & (df['obv_trend'] > 0), 'signal'] = 1
        # 顶背离
        df.loc[(df['price_trend'] > 0) & (df['obv_trend'] < 0), 'signal'] = -1

        return df

    @staticmethod
    def vwap_strategy(df: pd.DataFrame, threshold: float = 0.02) -> pd.DataFrame:
        """
        VWAP支撑阻力策略

        买入：价格低于VWAP 2%以上
        卖出：价格高于VWAP 2%以上
        """
        df = df.copy()
        df['VWAP'] = TechnicalIndicators.calculate_vwap(df)

        # 计算偏离度
        df['deviation'] = (df['close'] - df['VWAP']) / df['VWAP']

        df['signal'] = 0
        df.loc[df['deviation'] < -threshold, 'signal'] = 1
        df.loc[df['deviation'] > threshold, 'signal'] = -1

        return df

    @staticmethod
    def keltner_strategy(df: pd.DataFrame, period: int = 20, atr_mult: float = 2.0) -> pd.DataFrame:
        """
        肯特纳通道突破策略

        买入：价格突破上轨
        卖出：价格跌破下轨
        """
        df = df.copy()
        keltner_dict = TechnicalIndicators.calculate_keltner(df, period, atr_mult)
        df['KC_upper'] = keltner_dict['upper']
        df['KC_middle'] = keltner_dict['middle']
        df['KC_lower'] = keltner_dict['lower']

        df['signal'] = 0
        df.loc[df['close'] > df['KC_upper'], 'signal'] = 1
        df.loc[df['close'] < df['KC_lower'], 'signal'] = -1

        return df


def test_technical_strategies():
    """测试技术指标策略"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta

    # 生成模拟数据
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    np.random.seed(42)

    close = 100 + np.cumsum(np.random.randn(100) * 2)
    high = close + np.random.rand(100) * 3
    low = close - np.random.rand(100) * 3
    volume = np.random.randint(1000000, 5000000, 100)

    df = pd.DataFrame({
        'close': close,
        'high': high,
        'low': low,
        'volume': volume
    }, index=dates)

    # 测试ADX策略
    print("ADX趋势跟踪策略：")
    result = TechnicalStrategies.adx_trend_strategy(df)
    print(result[['close', 'ADX', '+DI', '-DI', 'signal']].tail())

    # 测试KDJ策略
    print("\nKDJ金叉死叉策略：")
    result = TechnicalStrategies.kdj_strategy(df)
    print(result[['close', 'K', 'D', 'J', 'signal']].tail())

    # 测试OBV策略
    print("\nOBV量价背离策略：")
    result = TechnicalStrategies.obv_divergence_strategy(df)
    print(result[['close', 'OBV', 'signal']].tail())

    # 测试VWAP策略
    print("\nVWAP支撑阻力策略：")
    result = TechnicalStrategies.vwap_strategy(df)
    print(result[['close', 'VWAP', 'deviation', 'signal']].tail())

    # 测试肯特纳通道策略
    print("\n肯特纳通道突破策略：")
    result = TechnicalStrategies.keltner_strategy(df)
    print(result[['close', 'KC_upper', 'KC_lower', 'signal']].tail())


if __name__ == '__main__':
    test_technical_strategies()
