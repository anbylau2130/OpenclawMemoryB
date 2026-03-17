"""
《算法交易与DMA》策略实现
"""

import pandas as pd
import numpy as np


class DMAStrategies:
    """直接市场准入策略"""

    @staticmethod
    def vwap_execution(df: pd.DataFrame) -> pd.DataFrame:
        """VWAP执行"""
        df = df.copy()
        df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
        df['signal'] = 0
        df.loc[df['close'] < df['vwap'], 'signal'] = 1
        df.loc[df['close'] > df['vwap'], 'signal'] = -1
        return df

    @staticmethod
    def twap_execution(df: pd.DataFrame) -> pd.DataFrame:
        """TWAP执行"""
        df = df.copy()
        df['twap'] = df['close'].expanding().mean()
        df['signal'] = 0
        df.loc[df['close'] < df['twap'], 'signal'] = 1
        return df

    @staticmethod
    def pov_execution(df: pd.DataFrame, target_pov: float = 0.1) -> pd.DataFrame:
        """参与率执行"""
        df = df.copy()
        df['cumvol'] = df['volume'].cumsum()
        df['target_vol'] = df['cumvol'] * target_pov
        df['signal'] = 0
        df.loc[df['volume'] > df['target_vol'].diff(), 'signal'] = 1
        return df

    @staticmethod
    def implementation_shortfall(df: pd.DataFrame) -> pd.DataFrame:
        """实施差额优化"""
        df = df.copy()
        df['arrival_price'] = df['close'].iloc[0]
        df[' shortfall'] = (df['close'] - df['arrival_price']) / df['arrival_price']
        df['signal'] = 0
        df.loc[df['shortfall'].abs() < 0.01, 'signal'] = 1
        return df

    @staticmethod
    def market_impact(df: pd.DataFrame) -> pd.DataFrame:
        """市场冲击最小化"""
        df = df.copy()
        df['impact'] = df['volume'] / df['volume'].rolling(20).mean()
        df['signal'] = 0
        df.loc[df['impact'] < 1.5, 'signal'] = 1  # 低冲击时交易
        return df

    @staticmethod
    def smart_order_routing(df: pd.DataFrame) -> pd.DataFrame:
        """智能订单路由"""
        df = df.copy()
        df['best_bid'] = df['low']
        df['best_ask'] = df['high']
        df['spread'] = df['best_ask'] - df['best_bid']
        df['signal'] = 0
        df.loc[df['spread'] < df['spread'].quantile(0.3), 'signal'] = 1  # 价差小时交易
        return df


def test_dma():
    """测试DMA策略"""
    import pandas as pd
    import numpy as np

    dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(200) * 2)
    high = close + np.random.rand(200) * 3
    low = close - np.random.rand(200) * 3
    volume = np.random.randint(100000, 5000000, 200)
    df = pd.DataFrame({'close': close, 'high': high, 'low': low, 'volume': volume}, index=dates)

    print("VWAP:", DMAStrategies.vwap_execution(df)['signal'].value_counts().to_dict())
    print("TWAP:", DMAStrategies.twap_execution(df)['signal'].value_counts().to_dict())
    print("POV:", DMAStrategies.pov_execution(df)['signal'].value_counts().to_dict())
    print("市场冲击:", DMAStrategies.market_impact(df)['signal'].value_counts().to_dict())
    print("智能路由:", DMAStrategies.smart_order_routing(df)['signal'].value_counts().to_dict())


if __name__ == '__main__':
    test_dma()
