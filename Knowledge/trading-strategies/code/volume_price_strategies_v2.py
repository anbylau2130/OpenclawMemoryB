"""
量价交易策略库（修复版）

包含10个经典量价策略，适配A股市场和Backtrader框架
"""

import backtrader as bt
import pandas as pd
import numpy as np


class OBVIndicator(bt.Indicator):
    """手动实现OBV指标"""
    lines = ('obv',)
    
    def __init__(self):
        self.addminperiod(1)
    
    def next(self):
        if len(self.data) == 1:
            self.lines.obv[0] = self.data.volume[0]
        else:
            if self.data.close[0] > self.data.close[-1]:
                self.lines.obv[0] = self.lines.obv[-1] + self.data.volume[0]
            elif self.data.close[0] < self.data.close[-1]:
                self.lines.obv[0] = self.lines.obv[-1] - self.data.volume[0]
            else:
                self.lines.obv[0] = self.lines.obv[-1]


class VWAPIndicator(bt.Indicator):
    """手动实现VWAP指标"""
    lines = ('vwap',)
    params = (('period', 1),)
    
    def __init__(self):
        self.addminperiod(1)
        self.cum_volume = 0
        self.cum_volume_price = 0
    
    def next(self):
        typical_price = (self.data.high[0] + self.data.low[0] + self.data.close[0]) / 3
        self.cum_volume += self.data.volume[0]
        self.cum_volume_price += typical_price * self.data.volume[0]
        
        if self.cum_volume > 0:
            self.lines.vwap[0] = self.cum_volume_price / self.cum_volume
        else:
            self.lines.vwap[0] = self.data.close[0]


class MFIIndicator(bt.Indicator):
    """手动实现MFI指标"""
    lines = ('mfi',)
    params = (('period', 14),)
    
    def __init__(self):
        self.addminperiod(self.p.period + 1)
    
    def next(self):
        if len(self.data) <= self.p.period:
            self.lines.mfi[0] = 50
            return
        
        # 计算典型价格
        typical_prices = []
        for i in range(-self.p.period, 0):
            tp = (self.data.high[i] + self.data.low[i] + self.data.close[i]) / 3
            typical_prices.append(tp)
        
        # 计算资金流
        positive_flow = 0
        negative_flow = 0
        
        for i in range(1, len(typical_prices)):
            tp_current = typical_prices[i]
            tp_prev = typical_prices[i - 1]
            volume = self.data.volume[i - self.p.period + i]
            
            raw_money_flow = tp_current * volume
            
            if tp_current > tp_prev:
                positive_flow += raw_money_flow
            elif tp_current < tp_prev:
                negative_flow += raw_money_flow
        
        # 计算MFI
        if positive_flow + negative_flow > 0:
            money_ratio = positive_flow / (positive_flow + negative_flow)
            self.lines.mfi[0] = 100 * money_ratio
        else:
            self.lines.mfi[0] = 50


class VolumeBreakout(bt.Strategy):
    """成交量突破策略（优化版）
    
    买入：成交量 > 20日均量 × 1.5，价格上涨
    卖出：成交量 < 5日均量 × 0.7，或盈利 > 3%
    """
    
    params = (
        ('volume_mult', 1.5),
        ('volume_period', 20),
        ('profit_target', 0.03),
        ('stop_loss', 0.02),
    )
    
    def __init__(self):
        self.volume_ma = bt.indicators.SMA(self.data.volume, period=self.p.volume_period)
        self.volume_ma5 = bt.indicators.SMA(self.data.volume, period=5)
        self.buy_price = None
    
    def next(self):
        if not self.position:
            # 买入条件：放量突破
            if (self.data.volume[0] > self.volume_ma[0] * self.p.volume_mult and
                self.data.close[0] > self.data.close[-1] and
                self.data.close[0] > self.data.open[0]):
                self.buy()
                self.buy_price = self.data.close[0]
        else:
            # 卖出条件：缩量或止盈止损
            if self.buy_price:
                pnl_ratio = (self.data.close[0] - self.buy_price) / self.buy_price
                
                # 止损
                if pnl_ratio < -self.p.stop_loss:
                    self.sell()
                    self.buy_price = None
                # 止盈
                elif pnl_ratio > self.p.profit_target:
                    self.sell()
                    self.buy_price = None
                # 缩量卖出
                elif self.data.volume[0] < self.volume_ma5[0] * 0.7:
                    self.sell()
                    self.buy_price = None


class VolumePriceDivergence(bt.Strategy):
    """量价背离策略（优化版）
    
    买入：价格新低但成交量未新低（底背离）
    卖出：价格新高但成交量未新高（顶背离）
    
    优化后参数：缩短RSI周期（14→10天），提升灵敏度
    """
    
    params = (
        ('lookback', 20),
        ('rsi_period', 10),  # 优化：14→10
    )
    
    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)
    
    def next(self):
        if len(self.data) < self.p.lookback:
            return
        
        # 获取历史数据
        closes = [self.data.close[i] for i in range(-self.p.lookback + 1, 1)]
        volumes = [self.data.volume[i] for i in range(-self.p.lookback + 1, 1)]
        
        if not self.position:
            # 底背离：价格新低，成交量未新低，RSI超卖
            if (self.data.close[0] == min(closes) and
                self.data.volume[0] > min(volumes) and
                self.rsi[0] < 30):
                self.buy()
        else:
            # 顶背离：价格新高，成交量未新高，RSI超买
            if (self.data.close[0] == max(closes) and
                self.data.volume[0] < max(volumes) and
                self.rsi[0] > 70):
                self.sell()


class OBVEnergy(bt.Strategy):
    """OBV能量潮策略（修复版）
    
    买入：OBV创新高但价格未创新高（资金流入）
    卖出：OBV创新低但价格未创新低（资金流出）
    """
    
    params = (
        ('lookback', 20),
        ('obv_period', 20),
    )
    
    def __init__(self):
        self.obv = OBVIndicator(self.data)
        self.obv_ma = bt.indicators.SMA(self.obv, period=self.p.obv_period)
    
    def next(self):
        if len(self.data) < self.p.lookback:
            return
        
        # 获取历史数据
        closes = [self.data.close[i] for i in range(-self.p.lookback + 1, 1)]
        obvs = [self.obv[0] + (self.obv[i] if hasattr(self.obv, '__getitem__') else 0) 
                for i in range(-self.p.lookback + 1, 1)]
        
        if not self.position:
            # 买入：OBV创新高，价格未创新高，OBV > MA
            if (self.obv[0] == max(obvs) and
                self.data.close[0] < max(closes) and
                self.obv[0] > self.obv_ma[0]):
                self.buy()
        else:
            # 卖出：OBV创新低，价格未创新低
            if (self.obv[0] == min(obvs) and
                self.data.close[0] > min(closes)):
                self.sell()


class VWAPIntraday(bt.Strategy):
    """VWAP日内策略（优化版）
    
    买入：价格 < VWAP × 0.97（低于均价3%）
    卖出：价格 > VWAP × 1.02（高于均价2%）
    
    优化后参数：放宽买入条件（0.98→0.97），降低成交量要求（1.2→1.0）
    """
    
    params = (
        ('deviation_buy', 0.97),   # 优化：0.98→0.97
        ('deviation_sell', 1.02),
        ('volume_mult', 1.0),      # 优化：1.2→1.0
    )
    
    def __init__(self):
        self.vwap = VWAPIndicator(self.data)
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
    """MFI资金流向策略（修复版）
    
    买入：MFI < 20（超卖），价格企稳
    卖出：MFI > 80（超买），价格滞涨
    """
    
    params = (
        ('mfi_period', 14),
        ('oversold', 20),
        ('overbought', 80),
    )
    
    def __init__(self):
        self.mfi = MFIIndicator(self.data, period=self.p.mfi_period)
    
    def next(self):
        if len(self.data) < self.p.mfi_period + 1:
            return
        
        if not self.position:
            # 买入：MFI超卖
            if self.mfi[0] < self.p.oversold:
                self.buy()
        else:
            # 卖出：MFI超买
            if self.mfi[0] > self.p.overbought:
                self.sell()


class VolumeContraction(bt.Strategy):
    """量能萎缩策略（优化版）
    
    买入：成交量 < 20日均量 × 0.6（萎缩）
    卖出：成交量突然放大 > 20日均量 × 1.8，价格突破
    
    优化后参数：萎缩持续4天（原2天），提升信号质量
    """
    
    params = (
        ('volume_mult_low', 0.6),
        ('volume_mult_high', 1.8),
        ('volume_period', 20),
        ('contraction_days', 4),  # 优化：2→4天
    )
    
    def __init__(self):
        self.volume_ma = bt.indicators.SMA(self.data.volume, period=self.p.volume_period)
        self.contraction_count = 0
    
    def next(self):
        if not self.position:
            # 买入：成交量萎缩，持续2天以上
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
    """量价齐升策略（优化版）
    
    买入：价格上涨 > 1.5%，成交量 > 20日均量 × 1.3，连续2日
    卖出：价格上涨但成交量萎缩（量价背离）
    """
    
    params = (
        ('price_change', 0.015),
        ('volume_mult', 1.3),
        ('volume_period', 20),
        ('sync_days', 2),
        ('profit_target', 0.04),
    )
    
    def __init__(self):
        self.volume_ma = bt.indicators.SMA(self.data.volume, period=self.p.volume_period)
        self.sync_count = 0
        self.buy_price = None
    
    def next(self):
        price_change = (self.data.close[0] - self.data.close[-1]) / self.data.close[-1]
        volume_ratio = self.data.volume[0] / self.volume_ma[0] if self.volume_ma[0] > 0 else 0
        
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
            if price_change > 0 and volume_ratio < 0.8:
                self.sell()
                self.buy_price = None
            elif self.buy_price and (self.data.close[0] - self.buy_price) / self.buy_price > self.p.profit_target:
                self.sell()
                self.buy_price = None


class VolumeWeightedRSI(bt.Strategy):
    """成交量加权RSI策略（优化版）
    
    买入：RSI < 30 且成交量 > 5日均量
    卖出：RSI > 70 且成交量 < 5日均量
    
    优化后参数：缩短RSI周期（14→10天），提升灵敏度
    """
    
    params = (
        ('rsi_period', 10),  # 优化：14→10
        ('oversold', 30),
        ('overbought', 70),
    )
    
    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)
        self.volume_ma = bt.indicators.SMA(self.data.volume, period=5)
    
    def next(self):
        if not self.position:
            # 买入：RSI超卖 + 放量
            if self.rsi[0] < self.p.oversold and self.data.volume[0] > self.volume_ma[0]:
                self.buy()
        else:
            # 卖出：RSI超买 + 缩量
            if self.rsi[0] > self.p.overbought and self.data.volume[0] < self.volume_ma[0]:
                self.sell()


class CapitalFlow(bt.Strategy):
    """资金流强度策略（简化版）
    
    买入：价格上涨 + 成交量放大
    卖出：价格下跌 + 成交量放大
    """
    
    params = (
        ('volume_mult', 1.5),
        ('volume_period', 20),
    )
    
    def __init__(self):
        self.volume_ma = bt.indicators.SMA(self.data.volume, period=self.p.volume_period)
    
    def next(self):
        volume_ratio = self.data.volume[0] / self.volume_ma[0] if self.volume_ma[0] > 0 else 0
        
        if not self.position:
            # 买入：价格上涨 + 放量
            if (self.data.close[0] > self.data.open[0] and
                volume_ratio > self.p.volume_mult):
                self.buy()
        else:
            # 卖出：价格下跌 + 放量
            if (self.data.close[0] < self.data.open[0] and
                volume_ratio > self.p.volume_mult):
                self.sell()


class VolumePricePattern(bt.Strategy):
    """量价形态策略（优化版）
    
    买入：底部放量（下跌后放量上涨）
    卖出：顶部放量（上涨后放量滞涨）
    """
    
    params = (
        ('volume_mult_high', 1.8),
        ('volume_mult_low', 0.6),
        ('volume_period', 20),
        ('lookback', 10),
    )
    
    def __init__(self):
        self.volume_ma = bt.indicators.SMA(self.data.volume, period=self.p.volume_period)
        self.ma5 = bt.indicators.SMA(self.data.close, period=5)
        self.ma20 = bt.indicators.SMA(self.data.close, period=20)
    
    def next(self):
        if len(self.data) < self.p.lookback:
            return
        
        volume_ratio = self.data.volume[0] / self.volume_ma[0] if self.volume_ma[0] > 0 else 0
        
        # 获取历史数据
        closes = [self.data.close[i] for i in range(-self.p.lookback + 1, 1)]
        
        if not self.position:
            # 形态1：底部放量（下跌后放量上涨）
            if (self.data.close[0] == min(closes) and
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
            if (self.data.close[0] == max(closes) and
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
    print("量价交易策略库（修复版）")
    print("=" * 50)
    for name, strategy in VOLUME_PRICE_STRATEGIES.items():
        print(f"- {name}: {strategy.__doc__.strip().split(chr(10))[0]}")
