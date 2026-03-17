"""
《市场微观结构》策略实现
"""

import pandas as pd
import numpy as np


class MicrostructureStrategies:
    """市场微观结构策略"""

    @staticmethod
    def order_book_imbalance(df: pd.DataFrame) -> pd.DataFrame:
        """订单簿不平衡"""
        df = df.copy()
        df['bid_vol'] = df['volume'] * 0.6
        df['ask_vol'] = df['volume'] * 0.4
        df['imbalance'] = (df['bid_vol'] - df['ask_vol']) / df['volume']
        df['signal'] = 0
        df.loc[df['imbalance'] > 0.3, 'signal'] = 1
        df.loc[df['imbalance'] < -0.3, 'signal'] = -1
        return df

    @staticmethod
    def trade_flow(df: pd.DataFrame) -> pd.DataFrame:
        """交易流分析"""
        df = df.copy()
        df['buy_flow'] = df['volume'] * (df['close'] > df['close'].shift(1)).astype(int)
        df['sell_flow'] = df['volume'] * (df['close'] < df['close'].shift(1)).astype(int)
        df['net_flow'] = df['buy_flow'] - df['sell_flow']
        df['signal'] = 0
        df.loc[df['net_flow'] > 0, 'signal'] = 1
        df.loc[df['net_flow'] < 0, 'signal'] = -1
        return df

    @staticmethod
    def price_impact(df: pd.DataFrame) -> pd.DataFrame:
        """价格冲击"""
        df = df.copy()
        df['return'] = df['close'].pct_change()
        df['impact'] = df['return'] / np.log(df['volume'] + 1)
        df['signal'] = 0
        df.loc[df['impact'] > df['impact'].quantile(0.7), 'signal'] = 1
        return df

    @staticmethod
    def spread_capture(df: pd.DataFrame) -> pd.DataFrame:
        """价差捕获"""
        df = df.copy()
        df['spread'] = df['high'] - df['low']
        df['spread_pct'] = df['spread'] / df['close']
        df['signal'] = 0
        df.loc[df['spread_pct'] < df['spread_pct'].quantile(0.3), 'signal'] = 1  # 价差小时买入
        return df

    @staticmethod
    def liquidity_taking(df: pd.DataFrame) -> pd.DataFrame:
        """流动性消耗"""
        df = df.copy()
        df['liq_consumed'] = df['volume'] / df['volume'].rolling(20).mean()
        df['signal'] = 0
        df.loc[df['liq_consumed'] > 2, 'signal'] = 1  # 流动性消耗大时跟随
        return df

    @staticmethod
    def adverse_selection(df: pd.DataFrame) -> pd.DataFrame:
        """逆向选择保护"""
        df = df.copy()
        df['mid'] = (df['high'] + df['low']) / 2
        df['adverse'] = abs(df['close'] - df['mid']) / df['mid']
        df['signal'] = 0
        df.loc[df['adverse'] < 0.01, 'signal'] = 1  # 逆向选择风险低时交易
        return df


def test_microstructure():
    """测试微观结构策略"""
    import pandas as pd
    import numpy as np

    dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(200) * 2)
    high = close + np.random.rand(200) * 3
    low = close - np.random.rand(200) * 3
    volume = np.random.randint(100000, 5000000, 200)
    df = pd.DataFrame({'close': close, 'high': high, 'low': low, 'volume': volume}, index=dates)

    print("订单簿不平衡:", MicrostructureStrategies.order_book_imbalance(df)['signal'].value_counts().to_dict())
    print("交易流:", MicrostructureStrategies.trade_flow(df)['signal'].value_counts().to_dict())
    print("价格冲击:", MicrostructureStrategies.price_impact(df)['signal'].value_counts().to_dict())
    print("价差捕获:", MicrostructureStrategies.spread_capture(df)['signal'].value_counts().to_dict())
    print("流动性消耗:", MicrostructureStrategies.liquidity_taking(df)['signal'].value_counts().to_dict())
    print("逆向选择:", MicrostructureStrategies.adverse_selection(df)['signal'].value_counts().to_dict())


if __name__ == '__main__':
    test_microstructure()
