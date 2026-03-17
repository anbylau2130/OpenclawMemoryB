"""
量价交易策略库

包含10个经典量价策略，适配A股市场
"""

import backtrader as bt
import pandas as pd
import numpy as np


class VolumeBreakout(bt.Strategy):
    """成交量突破策略
    
    买入：成交量 > 20日均量 × 2.0，价格上涨
    卖出：成交量 < 5日均量 × 0.5，或盈利 > 3%
    """
    
    params = (
        ('volume_mult', 2.0),
        ('volume_period', 20),
        ('profit_target', 0.03),
    )
    
    def __init__(self):
        self.volume_ma = bt.indicators.SMA(self.data.volume, period=self.p.volume_period)
        self.volume_ma5 = bt.indicators.SMA(self.data.volume, period=5)
        self.buy_price = None
    
    def next(self):
        if not self.position:
            # 买入条件：放量突破
            if (self.data.volume[0] > self.volume_ma[0] * self.p.volume_mult and
                self.data.close[0] > self.data.close[-1]):
                self.buy()
                self.buy_price = self.data.close[0]
        else:
            # 卖出条件：缩量或止盈
            if self.data.volume[0] < self.volume_ma5[0] * 0.5:
                self.sell()
            elif self.buy_price and (self.data.close[0] - self.buy_price) / self.buy_price > self.p.profit_target:
                self.sell()


class VolumePriceDivergence(bt.Strategy):
    """量价背离策略
    
    买入：价格新低但成交量未新低（底背离）
    卖出：价格新高但成交量未新高（顶背离）
    """
    
    params = (
        ('lookback', 20),
        ('rsi_period', 14),
    )
    
    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)
        self.volume_min = bt.indicators.Min(self.data.volume, period=self.p.lookback)
        self.price_min = bt.indicators.Min(self.data.close, period=self.p.lookback)
        self.volume_max = bt.indicators.Max(self.data.volume, period=self.p.lookback)
        self.price_max = bt.indicators.Max(self.data.close, period=self.p.lookback)
    
    def next(self):
        if not self.position:
            # 底背离：价格新低，成交量未新低，RSI超卖
            if (self.data.close[0] == self.price_min[0] and
                self.data.volume[0] > self.volume_min[0] and
                self.rsi[0] < 30):
                self.buy()
        else:
            # 顶背离：价格新高，成交量未新高，RSI超买
            if (self.data.close[0] == self.price_max[0] and
                self.data.volume[0] < self.volume_max[0] and
                self.rsi[0] > 70):
                self.sell()


class OBVEnergy(bt.Strategy):
    """OBV能量潮策略
    
    买入：OBV创新高但价格未创新高（资金流入）
    卖出：OBV创新低但价格未创新低（资金流出）
    """
    
    params = (
        ('lookback', 20),
        ('obv_period', 20),
    )
    
    def __init__(self):
        # 计算OBV
        self.obv = bt.indicators.OBV(self.data)
        self.obv_ma = bt.indicators.SMA(self.obv, period=self.p.obv_period)
        
        self.obv_max = bt.indicators.Max(self.obv, period=self.p.lookback)
        self.price_max = bt.indicators.Max(self.data.close, period=self.p.lookback)
        self.obv_min = bt.indicators.Min(self.obv, period=self.p.lookback)
        self.price_min = bt.indicators.Min(self.data.close, period=self.p.lookback)
    
    def next(self):
        if not self.position:
            # 买入：OBV创新高，价格未创新高，OBV > MA
            if (self.obv[0] == self.obv_max[0] and
                self.data.close[0] < self.price_max[0] and
                self.obv[0] > self.obv_ma[0]):
                self.buy()
        else:
            # 卖出：OBV创新低，价格未创新低
            if (self.obv[0] == self.obv_min[0] and
                self.data.close[0] > self.price_min[0]):
                self.sell()


class VWAPIntraday(bt.Strategy):
    """VWAP日内策略
    
    买入：价格 < VWAP × 0.98（低于均价2%）
    卖出：价格 > VWAP × 1.02（高于均价2%）
    """
    
    params = (
        ('deviation_buy', 0.98),
        ('deviation_sell', 1.02),
        ('volume_mult', 1.0),
    )
    
    def __init__(self):
        # 计算VWAP
        self.vwap = bt.indicators.VWAP(self.data)
        self.volume_ma = bt.indicators.SMA(self.data.volume, period=5)
    
    def next(self):
        if not self.position:
            # 买入：价格低于VWAP 2%，成交量放大
            if (self.data.close[0] < self.vwap[0] * self.p.deviation_buy and
                self.data.volume[0] > self.volume_ma[0] * self.p.volume_mult):
                self.buy()
        else:
            # 卖出：价格高于VWAP 2%
            if self.data.close[0] > self.vwap[0] * self.p.deviation_sell:
                self.sell()


class MFI(bt.Strategy):
    """MFI资金流向策略
    
    买入：MFI < 20（超卖），价格企稳
    卖出：MFI > 80（超买），价格滞涨
    """
    
    params = (
        ('mfi_period', 14),
        ('oversold', 20),
        ('overbought', 80),
    )
    
    def __init__(self):
        self.mfi = bt.indicators.MFI(self.data, period=self.p.mfi_period)
        self.price_min = bt.indicators.Min(self.data.close, period=3)
        self.price_max = bt.indicators.Max(self.data.close, period=3)
    
    def next(self):
        if not self.position:
            # 买入：MFI超卖，价格企稳
            if (self.mfi[0] < self.p.oversold and
                self.data.close[0] == self.price_min[0]):
                self.buy()
        else:
            # 卖出：MFI超买，价格滞涨
            if (self.mfi[0] > self.p.overbought and
                self.data.close[0] == self.price_max[0]):
                self.sell()


class VolumeContraction(bt.Strategy):
    """量能萎缩策略
    
    买入：成交量 < 20日均量 × 0.5（极度萎缩）
    卖出：成交量突然放大 > 20日均量 × 2.0，价格突破
    """
    
    params = (
        ('volume_mult_low', 0.5),
        ('volume_mult_high', 2.0),
        ('volume_period', 20),
        ('contraction_days', 3),
    )
    
    def __init__(self):
        self.volume_ma = bt.indicators.SMA(self.data.volume, period=self.p.volume_period)
        self.contraction_count = 0
    
    def next(self):
        if not self.position:
            # 买入：成交量极度萎缩，持续3天以上
            if self.data.volume[0] < self.volume_ma[0] * self.p.volume_mult_low:
                self.contraction_count += 1
                if self.contraction_count >= self.p.contraction_days:
                    self.buy()
                    self.contraction_count = 0
            else:
                self.contraction_count = 0
        else:
            # 卖出：成交量突然放大，价格突破
            if (self.data.volume[0] > self.volume_ma[0] * self.p.volume_mult_high and
                self.data.close[0] > self.data.close[-1]):
                self.sell()


class VolumePriceSync(bt.Strategy):
    """量价齐升策略
    
    买入：价格上涨 > 2%，成交量 > 20日均量 × 1.5，连续2日
    卖出：价格上涨但成交量萎缩（量价背离）
    """
    
    params = (
        ('price_change', 0.02),
        ('volume_mult', 1.5),
        ('volume_period', 20),
        ('sync_days', 2),
        ('profit_target', 0.05),
    )
    
    def __init__(self):
        self.volume_ma = bt.indicators.SMA(self.data.volume, period=self.p.volume_period)
        self.sync_count = 0
        self.buy_price = None
    
    def next(self):
        price_change = (self.data.close[0] - self.data.close[-1]) / self.data.close[-1]
        volume_ratio = self.data.volume[0] / self.volume_ma[0]
        
        if not self.position:
            # 买入：量价齐升，连续2日
            if price_change > self.p.price_change and volume_ratio > self.p.volume_mult:
                self.sync_count += 1
                if self.sync_count >= self.p.sync_days:
                    self.buy()
                    self.buy_price = self.data.close[0]
                    self.sync_count = 0
            else:
                self.sync_count = 0
        else:
            # 卖出：量价背离或止盈
            if price_change > 0 and volume_ratio < 1.0:
                self.sell()
            elif self.buy_price and (self.data.close[0] - self.buy_price) / self.buy_price > self.p.profit_target:
                self.sell()


class VolumeWeightedRSI(bt.Strategy):
    """成交量加权RSI策略
    
    买入：VW-RSI < 30（量价加权超卖）
    卖出：VW-RSI > 70（量价加权超买）
    """
    
    params = (
        ('rsi_period', 14),
        ('oversold', 30),
        ('overbought', 70),
    )
    
    def __init__(self):
        # 计算成交量加权价格变化
        self.price_change = self.data.close - self.data.close(-1)
        self.volume_weighted_change = self.price_change * self.data.volume
        
        # 计算VW-RSI
        self.vw_rsi = bt.indicators.RSI(self.volume_weighted_change, period=self.p.rsi_period)
    
    def next(self):
        if not self.position:
            # 买入：VW-RSI超卖
            if self.vw_rsi[0] < self.p.oversold:
                self.buy()
        else:
            # 卖出：VW-RSI超买
            if self.vw_rsi[0] > self.p.overbought:
                self.sell()


class CapitalFlow(bt.Strategy):
    """资金流强度策略
    
    买入：主力净流入 > 成交额 × 10%，价格上涨
    卖出：主力净流出 > 成交额 × 10%
    
    注：需要主力资金数据，此处用简化版（大单模拟）
    """
    
    params = (
        ('flow_threshold', 0.1),
        ('volume_mult', 1.5),
    )
    
    def __init__(self):
        self.volume_ma = bt.indicators.SMA(self.data.volume, period=20)
        
        # 简化：用价格涨跌 × 成交量模拟资金流向
        self.flow = (self.data.close - self.data.open) * self.data.volume
        self.flow_ma = bt.indicators.SMA(self.flow, period=5)
    
    def next(self):
        flow_ratio = abs(self.flow[0]) / (self.data.close[0] * self.data.volume[0])
        
        if not self.position:
            # 买入：资金流入，价格上涨
            if (self.flow[0] > 0 and 
                flow_ratio > self.p.flow_threshold and
                self.data.close[0] > self.data.close[-1]):
                self.buy()
        else:
            # 卖出：资金流出
            if self.flow[0] < 0 and flow_ratio > self.p.flow_threshold:
                self.sell()


class VolumePricePattern(bt.Strategy):
    """量价形态策略
    
    买入：底部放量（下跌后放量上涨）、缩量回调（上涨中缩量）
    卖出：顶部放量（上涨后放量滞涨）、放量下跌
    """
    
    params = (
        ('volume_mult_high', 2.0),
        ('volume_mult_low', 0.5),
        ('volume_period', 20),
        ('lookback', 10),
    )
    
    def __init__(self):
        self.volume_ma = bt.indicators.SMA(self.data.volume, period=self.p.volume_period)
        self.price_min = bt.indicators.Min(self.data.close, period=self.p.lookback)
        self.price_max = bt.indicators.Max(self.data.close, period=self.p.lookback)
        
        # 趋势判断
        self.ma5 = bt.indicators.SMA(self.data.close, period=5)
        self.ma20 = bt.indicators.SMA(self.data.close, period=20)
    
    def next(self):
        volume_ratio = self.data.volume[0] / self.volume_ma[0]
        
        if not self.position:
            # 形态1：底部放量（下跌后放量上涨）
            if (self.data.close[0] == self.price_min[0] and
                volume_ratio > self.p.volume_mult_high and
                self.data.close[0] > self.data.close[-1]):
                self.buy()
            
            # 形态2：缩量回调（上涨中缩量）
            elif (self.ma5[0] > self.ma20[0] and
                  volume_ratio < self.p.volume_mult_low and
                  self.data.close[0] < self.data.close[-1]):
                self.buy()
        
        else:
            # 卖出：顶部放量（上涨后放量滞涨）
            if (self.data.close[0] == self.price_max[0] and
                volume_ratio > self.p.volume_mult_high and
                self.data.close[0] <= self.data.close[-1]):
                self.sell()
            
            # 卖出：放量下跌
            elif (volume_ratio > self.p.volume_mult_high and
                  self.data.close[0] < self.data.close[-1]):
                self.sell()


# 策略映射
VOLUME_PRICE_STRATEGIES = {
    'volume_breakout': VolumeBreakout,
    'volume_price_divergence': VolumePriceDivergence,
    'obv_energy': OBVEnergy,
    'vwap_intraday': VWAPIntraday,
    'mfi': MFI,
    'volume_contraction': VolumeContraction,
    'volume_price_sync': VolumePriceSync,
    'volume_weighted_rsi': VolumeWeightedRSI,
    'capital_flow': CapitalFlow,
    'volume_price_pattern': VolumePricePattern,
}


def get_strategy(name):
    """获取策略类"""
    return VOLUME_PRICE_STRATEGIES.get(name)


def list_strategies():
    """列出所有策略"""
    return list(VOLUME_PRICE_STRATEGIES.keys())


if __name__ == '__main__':
    print("量价交易策略库")
    print("=" * 50)
    for name, strategy in VOLUME_PRICE_STRATEGIES.items():
        print(f"- {name}: {strategy.__doc__.strip().split(chr(10))[0]}")
