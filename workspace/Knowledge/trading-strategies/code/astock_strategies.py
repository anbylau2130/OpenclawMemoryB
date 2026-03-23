"""
A股专属交易策略
基于A股市场特征设计
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, time

# ==================== 一、涨跌停板策略 ====================

class LimitUpStrategy:
    """涨停板战法"""

    def __init__(self, limit_pct: float = 0.10):
        self.limit_pct = limit_pct  # 涨停幅度（主板10%，创业板20%）
        self.name = "涨停板战法"

    def generate_signals(self, df: pd.DataFrame) -> List[Dict]:
        """生成信号"""

        signals = []

        for i in range(1, len(df)):
            limit_up = df['close'].iloc[i-1] * (1 + self.limit_pct)

            # 接近涨停（95%以上）
            if df['close'].iloc[i] >= limit_up * 0.95:
                # 判断封板强度
                if df['high'].iloc[i] >= limit_up * 0.99:
                    strength = 'strong'  # 强封板
                else:
                    strength = 'weak'  # 弱封板

                signals.append({
                    'date': df.index[i],
                    'type': 'PREPARE_BUY',
                    'reason': f'涨停封板（{strength}）',
                    'strength': strength,
                    'target_date': df.index[min(i+1, len(df)-1)]
                })

        return signals

class LimitDownReboundStrategy:
    """跌停板反弹策略"""

    def __init__(self, limit_pct: float = 0.10):
        self.limit_pct = limit_pct
        self.name = "跌停板反弹"

    def generate_signals(self, df: pd.DataFrame) -> List[Dict]:
        """生成信号"""

        signals = []

        for i in range(1, len(df)):
            limit_down = df['close'].iloc[i-1] * (1 - self.limit_pct)

            # 跌停打开
            if (df['low'].iloc[i] <= limit_down * 1.01 and
                df['close'].iloc[i] > limit_down):
                rebound_pct = (df['close'].iloc[i] - limit_down) / limit_down * 100

                signals.append({
                    'date': df.index[i],
                    'type': 'BUY',
                    'reason': f'跌停打开，反弹{rebound_pct:.1f}%',
                    'confidence': min(0.65 + rebound_pct / 100, 0.75)
                })

        return signals

# ==================== 二、集合竞价策略 ====================

class AuctionStrategy:
    """集合竞价策略"""

    def __init__(self):
        self.name = "集合竞价"

    def analyze_auction(self, prev_close: float, auction_price: float) -> Optional[Dict]:
        """分析竞价结果"""

        open_change = (auction_price - prev_close) / prev_close * 100

        # 高开2-5%
        if 2 < open_change < 5:
            return {
                'signal': 'BUY',
                'reason': f'竞价高开{open_change:.2f}%',
                'confidence': 0.65,
                'open_change': open_change
            }
        # 高开>7%（可能高开低走）
        elif open_change > 7:
            return {
                'signal': 'SELL',
                'reason': f'竞价高开过多{open_change:.2f}%',
                'confidence': 0.70,
                'open_change': open_change
            }
        # 低开<-5%（可能反弹）
        elif open_change < -5:
            return {
                'signal': 'PREPARE_BUY',
                'reason': f'竞价低开{abs(open_change):.2f}%',
                'confidence': 0.60,
                'open_change': open_change
            }

        return None

# ==================== 三、板块轮动策略 ====================

class SectorRotationStrategy:
    """板块轮动策略"""

    def __init__(self, lookback: int = 5, top_n: int = 3):
        self.lookback = lookback
        self.top_n = top_n
        self.name = "板块轮动"

    def analyze_sectors(self, df_sectors: Dict[str, pd.DataFrame]) -> Dict:
        """分析板块强弱"""

        sector_returns = {}
        for sector, df in df_sectors.items():
            if len(df) >= self.lookback:
                ret = (df['close'].iloc[-1] / df['close'].iloc[-self.lookback] - 1) * 100
                sector_returns[sector] = ret

        # 排名
        ranked = sorted(sector_returns.items(), key=lambda x: x[1], reverse=True)

        return {
            'buy_sectors': [s[0] for s in ranked[:self.top_n]],
            'sell_sectors': [s[0] for s in ranked[-self.top_n:]],
            'sector_returns': sector_returns,
            'top_3': ranked[:3],
            'bottom_3': ranked[-3:]
        }

# ==================== 四、资金流向策略 ====================

class CapitalFlowStrategy:
    """主力资金跟踪策略"""

    def __init__(self, threshold: float = 0.05):
        self.threshold = threshold  # 流入/流出阈值（5%）
        self.name = "主力资金"

    def generate_signals(self, df: pd.DataFrame, capital_data: pd.DataFrame) -> List[Dict]:
        """生成信号"""

        signals = []

        for i in range(min(len(df), len(capital_data))):
            net_inflow = capital_data.iloc[i]['net_inflow']
            volume = df['volume'].iloc[i]

            if volume > 0:
                net_inflow_ratio = net_inflow / volume

                # 主力大幅流入
                if net_inflow_ratio > self.threshold:
                    signals.append({
                        'date': df.index[i],
                        'type': 'BUY',
                        'reason': f'主力净流入{net_inflow_ratio*100:.1f}%',
                        'confidence': 0.68
                    })
                # 主力大幅流出
                elif net_inflow_ratio < -self.threshold:
                    signals.append({
                        'date': df.index[i],
                        'type': 'SELL',
                        'reason': f'主力净流出{abs(net_inflow_ratio)*100:.1f}%',
                        'confidence': 0.65
                    })

        return signals

# ==================== 五、北向资金策略 ====================

class NorthboundCapitalStrategy:
    """北向资金跟踪策略"""

    def __init__(self, change_threshold: float = 10):
        self.change_threshold = change_threshold  # 增持/减持阈值（%）
        self.name = "北向资金"

    def generate_signals(self, northbound_data: pd.DataFrame) -> List[Dict]:
        """生成信号"""

        signals = []

        for i in range(1, len(northbound_data)):
            prev_holding = northbound_data.iloc[i-1]['holding']
            curr_holding = northbound_data.iloc[i]['holding']

            if prev_holding > 0:
                change_ratio = (curr_holding - prev_holding) / prev_holding * 100

                # 北向资金大幅增持
                if change_ratio > self.change_threshold:
                    signals.append({
                        'date': northbound_data.index[i],
                        'type': 'BUY',
                        'reason': f'北向资金增持{change_ratio:.1f}%',
                        'confidence': 0.70
                    })
                # 北向资金大幅减持
                elif change_ratio < -self.change_threshold:
                    signals.append({
                        'date': northbound_data.index[i],
                        'type': 'SELL',
                        'reason': f'北向资金减持{abs(change_ratio):.1f}%',
                        'confidence': 0.65
                    })

        return signals

# ==================== 六、多维度确认策略 ====================

class MultiDimensionStrategy:
    """多维度确认策略"""

    def __init__(self, min_score: int = 3):
        self.min_score = min_score
        self.name = "多维度确认"

    def generate_signals(self, df: pd.DataFrame,
                        capital_data: Optional[pd.DataFrame] = None,
                        northbound_data: Optional[pd.DataFrame] = None) -> List[Dict]:
        """生成信号"""

        signals = []

        for i in range(20, len(df)):  # 从第20天开始（确保有足够数据）
            scores = 0
            reasons = []

            # 1. 技术面：MA趋势
            ma5 = df['close'].iloc[i-5:i].mean()
            ma20 = df['close'].iloc[i-20:i].mean()
            if ma5 > ma20:
                scores += 1
                reasons.append('MA5>MA20')

            # 2. 技术面：RSI
            from strategies.github_strategies import calculate_rsi
            rsi = calculate_rsi(df['close'].iloc[:i+1]).iloc[-1]
            if 40 < rsi < 70:
                scores += 1
                reasons.append(f'RSI={rsi:.0f}')

            # 3. 成交量：放量
            vol_ma5 = df['volume'].iloc[i-5:i].mean()
            if df['volume'].iloc[i] > vol_ma5:
                scores += 1
                reasons.append('放量')

            # 4. 资金面：主力流入
            if capital_data is not None and i < len(capital_data):
                if capital_data.iloc[i]['net_inflow'] > 0:
                    scores += 1
                    reasons.append('主力流入')

            # 5. 北向资金：增持
            if northbound_data is not None and i < len(northbound_data):
                if i > 0 and northbound_data.iloc[i]['holding'] > northbound_data.iloc[i-1]['holding']:
                    scores += 1
                    reasons.append('北向增持')

            # 综合评分
            if scores >= self.min_score:
                signals.append({
                    'date': df.index[i],
                    'type': 'BUY',
                    'reason': f'多维确认（{scores}/5）：{", ".join(reasons)}',
                    'confidence': min(0.65 + scores * 0.02, 0.75)
                })
            elif scores == 0:
                signals.append({
                    'date': df.index[i],
                    'type': 'SELL',
                    'reason': '多维看空',
                    'confidence': 0.68
                })

        return signals

# ==================== 七、分时均线做T策略 ====================

class IntradayMAmStrategy:
    """分时均线做T策略"""

    def __init__(self):
        self.name = "分时均线做T"

    def generate_signals(self, df_intraday: pd.DataFrame) -> List[Dict]:
        """生成信号（df_intraday为分时数据）"""

        # 计算分时均价线（VWAP）
        df_intraday = df_intraday.copy()
        df_intraday['vwap'] = (df_intraday['close'] * df_intraday['volume']).cumsum() / df_intraday['volume'].cumsum()

        signals = []

        for i in range(1, len(df_intraday)):
            price = df_intraday['close'].iloc[i]
            vwap = df_intraday['vwap'].iloc[i]
            prev_price = df_intraday['close'].iloc[i-1]

            # 价格在均线下方且开始反弹
            if (price < vwap and
                price > prev_price and
                df_intraday['volume'].iloc[i] > df_intraday['volume'].iloc[i-1]):
                signals.append({
                    'time': df_intraday.index[i],
                    'type': 'BUY',
                    'reason': '分时均线支撑反弹',
                    'confidence': 0.65
                })
            # 价格在均线上方且开始回落
            elif (price > vwap and price < prev_price):
                signals.append({
                    'time': df_intraday.index[i],
                    'type': 'SELL',
                    'reason': '分时均线压力回落',
                    'confidence': 0.65
                })

        return signals

# ==================== 八、策略注册表 ====================

ASTOCK_STRATEGY_REGISTRY = {
    # 涨跌停板
    'limit_up': LimitUpStrategy,
    'limit_down_rebound': LimitDownReboundStrategy,

    # 集合竞价
    'auction': AuctionStrategy,

    # 板块轮动
    'sector_rotation': SectorRotationStrategy,

    # 资金流向
    'capital_flow': CapitalFlowStrategy,
    'northbound_capital': NorthboundCapitalStrategy,

    # 组合策略
    'multi_dimension': MultiDimensionStrategy,

    # 日内策略
    'intraday_ma': IntradayMAmStrategy,
}

def get_astock_strategy(name: str):
    """获取A股策略"""
    return ASTOCK_STRATEGY_REGISTRY.get(name)

def list_astock_strategies():
    """列出所有A股策略"""
    return list(ASTOCK_STRATEGY_REGISTRY.keys())

# ==================== 九、快速使用 ====================

if __name__ == '__main__':
    print("A股专属策略库")
    print("=" * 60)
    print(f"已实现策略数：{len(ASTOCK_STRATEGY_REGISTRY)}")
    print("\n可用策略：")
    for i, name in enumerate(ASTOCK_STRATEGY_REGISTRY.keys(), 1):
        strategy = ASTOCK_STRATEGY_REGISTRY[name]
        print(f"  {i}. {name:20s} - {strategy().name}")
