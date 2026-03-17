"""
GitHub策略代码库
从WorldQuant Alpha101、经典策略、高级策略中学习并实现
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict

# ==================== 一、基础指标函数 ====================

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """计算RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """计算MACD"""
    ema12 = prices.ewm(span=12).mean()
    ema26 = prices.ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    histogram = macd - signal
    return macd, signal, histogram

def calculate_kdj(df: pd.DataFrame, period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """计算KDJ"""
    low_min = df['low'].rolling(period).min()
    high_max = df['high'].rolling(period).max()

    rsv = (df['close'] - low_min) / (high_max - low_min) * 100

    k = rsv.ewm(alpha=1/3).mean()
    d = k.ewm(alpha=1/3).mean()
    j = 3 * k - 2 * d

    return k, d, j

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """计算ATR"""
    high = df['high']
    low = df['low']
    close = df['close'].shift(1)

    tr1 = high - low
    tr2 = abs(high - close)
    tr3 = abs(low - close)

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()

    return atr

def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    """计算VWAP"""
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
    return vwap

# ==================== 二、经典策略 ====================

class DualMAStrategy:
    """双均线策略"""

    def __init__(self, fast: int = 5, slow: int = 20):
        self.fast = fast
        self.slow = slow
        self.name = "双均线策略"

    def generate_signals(self, df: pd.DataFrame) -> List[str]:
        ma_fast = df['close'].rolling(self.fast).mean()
        ma_slow = df['close'].rolling(self.slow).mean()

        signals = []
        for i in range(len(df)):
            if i == 0:
                signals.append('HOLD')
                continue

            if ma_fast.iloc[i] > ma_slow.iloc[i] and ma_fast.iloc[i-1] <= ma_slow.iloc[i-1]:
                signals.append('BUY')
            elif ma_fast.iloc[i] < ma_slow.iloc[i] and ma_fast.iloc[i-1] >= ma_slow.iloc[i-1]:
                signals.append('SELL')
            else:
                signals.append('HOLD')

        return signals

class BollingerBandsStrategy:
    """布林带策略"""

    def __init__(self, period: int = 20, std_dev: float = 2):
        self.period = period
        self.std_dev = std_dev
        self.name = "布林带策略"

    def generate_signals(self, df: pd.DataFrame) -> List[str]:
        middle = df['close'].rolling(self.period).mean()
        std = df['close'].rolling(self.period).std()
        upper = middle + self.std_dev * std
        lower = middle - self.std_dev * std

        signals = []
        for i in range(len(df)):
            if df['close'].iloc[i] < lower.iloc[i]:
                signals.append('BUY')
            elif df['close'].iloc[i] > upper.iloc[i]:
                signals.append('SELL')
            else:
                signals.append('HOLD')

        return signals

class RSIStrategy:
    """RSI均值回归策略"""

    def __init__(self, period: int = 14, oversold: int = 30, overbought: int = 70):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.name = "RSI均值回归"

    def generate_signals(self, df: pd.DataFrame) -> List[str]:
        rsi = calculate_rsi(df['close'], self.period)

        signals = []
        for i in range(len(df)):
            if i == 0:
                signals.append('HOLD')
                continue

            if rsi.iloc[i] < self.oversold and rsi.iloc[i-1] >= self.oversold:
                signals.append('BUY')
            elif rsi.iloc[i] > self.overbought and rsi.iloc[i-1] <= self.overbought:
                signals.append('SELL')
            else:
                signals.append('HOLD')

        return signals

class MACDStrategy:
    """MACD趋势跟踪策略"""

    def __init__(self):
        self.name = "MACD趋势跟踪"

    def generate_signals(self, df: pd.DataFrame) -> List[str]:
        macd, signal, _ = calculate_macd(df['close'])

        signals = []
        for i in range(len(df)):
            if i == 0:
                signals.append('HOLD')
                continue

            if macd.iloc[i] > signal.iloc[i] and macd.iloc[i-1] <= signal.iloc[i-1]:
                signals.append('BUY')
            elif macd.iloc[i] < signal.iloc[i] and macd.iloc[i-1] >= signal.iloc[i-1]:
                signals.append('SELL')
            else:
                signals.append('HOLD')

        return signals

class KDJStrategy:
    """KDJ超买超卖策略"""

    def __init__(self, oversold: int = 20, overbought: int = 80):
        self.oversold = oversold
        self.overbought = overbought
        self.name = "KDJ超买超卖"

    def generate_signals(self, df: pd.DataFrame) -> List[str]:
        k, d, j = calculate_kdj(df)

        signals = []
        for i in range(len(df)):
            if i == 0:
                signals.append('HOLD')
                continue

            if k.iloc[i] > d.iloc[i] and k.iloc[i-1] <= d.iloc[i-1] and j.iloc[i] < self.oversold:
                signals.append('BUY')
            elif k.iloc[i] < d.iloc[i] and k.iloc[i-1] >= d.iloc[i-1] and j.iloc[i] > self.overbought:
                signals.append('SELL')
            else:
                signals.append('HOLD')

        return signals

# ==================== 三、高级策略 ====================

class VolumePriceDivergenceStrategy:
    """量价背离策略"""

    def __init__(self):
        self.name = "量价背离"

    def generate_signals(self, df: pd.DataFrame) -> List[str]:
        price_high = df['close'].rolling(20).max()

        signals = []
        for i in range(20, len(df)):
            # 顶背离
            if (df['close'].iloc[i] >= price_high.iloc[i] * 0.99 and
                df['volume'].iloc[i] < df['volume'].iloc[i-5:i].mean()):
                signals.append('SELL')
            # 底背离
            elif (df['close'].iloc[i] <= df['close'].rolling(20).min().iloc[i] * 1.01 and
                  df['volume'].iloc[i] > df['volume'].iloc[i-5:i].mean() * 1.5):
                signals.append('BUY')
            else:
                signals.append('HOLD')

        return signals

class BreakoutPullbackStrategy:
    """突破回踩策略"""

    def __init__(self, period: int = 20):
        self.period = period
        self.name = "突破回踩"

    def generate_signals(self, df: pd.DataFrame) -> List[str]:
        high = df['high'].rolling(self.period).max()

        breakout_level = None
        signals = []

        for i in range(len(df)):
            if i == 0:
                signals.append('HOLD')
                continue

            # 突破
            if df['close'].iloc[i] > high.iloc[i-1]:
                breakout_level = high.iloc[i-1]
                signals.append('HOLD')
            # 回踩确认
            elif breakout_level and df['close'].iloc[i] < breakout_level * 1.02:
                if df['close'].iloc[i] > df['close'].iloc[i-1]:
                    signals.append('BUY')
                    breakout_level = None
                else:
                    signals.append('HOLD')
            else:
                signals.append('HOLD')

        return signals

class GapFillStrategy:
    """缺口回补策略"""

    def __init__(self):
        self.name = "缺口回补"

    def generate_signals(self, df: pd.DataFrame) -> List[str]:
        signals = []

        for i in range(1, len(df)):
            gap_up = df['low'].iloc[i] - df['high'].iloc[i-1]
            gap_down = df['high'].iloc[i] - df['low'].iloc[i-1]

            if gap_up > 0:
                target = df['high'].iloc[i-1] + gap_up * 0.5
                if df['close'].iloc[i] <= target:
                    signals.append('BUY')
                else:
                    signals.append('HOLD')
            elif gap_down < 0:
                target = df['low'].iloc[i-1] + gap_down * 0.5
                if df['close'].iloc[i] >= target:
                    signals.append('SELL')
                else:
                    signals.append('HOLD')
            else:
                signals.append('HOLD')

        return signals

class VWAPStrategy:
    """VWAP策略"""

    def __init__(self):
        self.name = "VWAP"

    def generate_signals(self, df: pd.DataFrame) -> List[str]:
        vwap = calculate_vwap(df)

        signals = []
        for i in range(1, len(df)):
            if (df['close'].iloc[i] < vwap.iloc[i] and
                df['close'].iloc[i] > df['close'].iloc[i-1] and
                df['volume'].iloc[i] > df['volume'].iloc[i-1]):
                signals.append('BUY')
            elif (df['close'].iloc[i] > vwap.iloc[i] and
                  df['close'].iloc[i] < df['close'].iloc[i-1]):
                signals.append('SELL')
            else:
                signals.append('HOLD')

        return signals

# ==================== 四、组合策略 ====================

class TripleConfirmationStrategy:
    """三重确认策略"""

    def __init__(self):
        self.name = "三重确认"

    def generate_signals(self, df: pd.DataFrame) -> List[str]:
        ma5 = df['close'].rolling(5).mean()
        ma20 = df['close'].rolling(20).mean()
        trend = ma5 > ma20

        rsi = calculate_rsi(df['close'])
        momentum = (rsi > 40) & (rsi < 70)

        volume_ma = df['volume'].rolling(5).mean()
        volume_confirm = df['volume'] > volume_ma

        signals = []
        for i in range(len(df)):
            buy_signals = [trend.iloc[i], momentum.iloc[i], volume_confirm.iloc[i]]

            if sum(buy_signals) >= 2:
                signals.append('BUY')
            elif sum(buy_signals) == 0:
                signals.append('SELL')
            else:
                signals.append('HOLD')

        return signals

# ==================== 五、A股做T专用策略 ====================

class First30MinutesStrategy:
    """早盘30分钟策略"""

    def __init__(self):
        self.name = "早盘30分钟"

    def generate_signals(self, df: pd.DataFrame) -> List[Dict]:
        """df为5分钟K线"""
        if len(df) < 6:
            return [{'signal': 'HOLD', 'reason': ''}]

        first_30 = df.iloc[:6]
        open_price = first_30['open'].iloc[0]
        high_30 = first_30['high'].max()
        low_30 = first_30['low'].min()

        # 高开 + 冲高回落
        if (first_30['close'].iloc[-1] > open_price and
            first_30['close'].iloc[-1] < high_30 * 0.98):
            return [{'signal': 'SELL', 'reason': '早盘冲高回落'}]

        # 低开 + 止跌回升
        elif (first_30['close'].iloc[-1] < open_price and
              first_30['close'].iloc[-1] > low_30 * 1.02):
            return [{'signal': 'BUY', 'reason': '早盘止跌回升'}]

        return [{'signal': 'HOLD', 'reason': ''}]

class Last30MinutesStrategy:
    """尾盘30分钟策略"""

    def __init__(self):
        self.name = "尾盘30分钟"

    def generate_signals(self, df: pd.DataFrame) -> List[Dict]:
        """df为5分钟K线"""
        if len(df) < 6:
            return [{'signal': 'HOLD', 'reason': ''}]

        last_30 = df.iloc[-6:]

        # 尾盘拉升
        if last_30['close'].iloc[-1] > last_30['close'].iloc[0] * 1.005:
            return [{'signal': 'SELL', 'reason': '尾盘拉升，次日高开概率大'}]

        # 尾盘跳水
        elif last_30['close'].iloc[-1] < last_30['close'].iloc[0] * 0.995:
            return [{'signal': 'PREPARE_BUY', 'reason': '尾盘跳水，次日低开可买入'}]

        return [{'signal': 'HOLD', 'reason': ''}]

# ==================== 六、策略注册表 ====================

STRATEGY_REGISTRY = {
    # 经典策略
    'dual_ma': DualMAStrategy,
    'bollinger': BollingerBandsStrategy,
    'rsi': RSIStrategy,
    'macd': MACDStrategy,
    'kdj': KDJStrategy,

    # 高级策略
    'volume_price_divergence': VolumePriceDivergenceStrategy,
    'breakout_pullback': BreakoutPullbackStrategy,
    'gap_fill': GapFillStrategy,
    'vwap': VWAPStrategy,

    # 组合策略
    'triple_confirmation': TripleConfirmationStrategy,

    # A股做T专用
    'first_30min': First30MinutesStrategy,
    'last_30min': Last30MinutesStrategy,
}

def get_strategy(name: str):
    """获取策略"""
    return STRATEGY_REGISTRY.get(name)

def list_strategies():
    """列出所有策略"""
    return list(STRATEGY_REGISTRY.keys())

# ==================== 七、快速使用 ====================

if __name__ == '__main__':
    print("GitHub策略库")
    print("="*60)
    print(f"已实现策略数：{len(STRATEGY_REGISTRY)}")
    print("\n可用策略：")
    for i, name in enumerate(STRATEGY_REGISTRY.keys(), 1):
        strategy = STRATEGY_REGISTRY[name]
        print(f"  {i}. {name} - {strategy().name}")
