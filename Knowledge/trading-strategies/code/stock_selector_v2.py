#!/usr/bin/env python3
"""
上证100选股系统 - 短中线策略
=====================================
功能：每天早上8点，从上证100成分股中选出可能上涨突破的股票
策略：多因子策略 + 技术分析（日线/周线）
输出：买入价、卖出价、止盈、止损
作者：小秘
日期：2026-03-17
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
import math

# ============================================================
# 一、上证100成分股列表
# ============================================================

SSE100_STOCKS = {
    "600036": "招商银行", "601318": "中国平安", "601166": "兴业银行",
    "600000": "浦发银行", "601398": "工商银行", "601288": "农业银行",
    "601939": "建设银行", "601988": "中国银行", "600030": "中信证券",
    "601211": "国泰君安", "601857": "中国石油", "600028": "中国石化",
    "601088": "中国神华", "600019": "宝钢股份", "600031": "三一重工",
    "601766": "中国中车", "600104": "上汽集团", "601390": "中国中铁",
    "600519": "贵州茅台", "000858": "五粮液", "600887": "伊利股份",
    "600276": "恒瑞医药", "000333": "美的集团", "000651": "格力电器",
    "002415": "海康威视", "600009": "上海机场", "600011": "华能国际",
    "600015": "华夏银行", "600016": "民生银行", "600018": "上港集团",
    "600048": "保利地产", "600050": "中国联通", "600309": "万华化学",
    "600585": "海螺水泥", "600690": "海尔智家", "600703": "三安光电",
    "600809": "山西汾酒", "600837": "海通证券", "600900": "长江电力",
    "601012": "隆基绿能", "601066": "中信建投", "601111": "中国国航",
    "601225": "陕西煤业", "601238": "广汽集团", "601328": "交通银行",
    "601336": "新华保险", "601601": "中国太保", "601628": "中国人寿",
    "601668": "中国建筑", "601688": "华泰证券", "601728": "中国电信",
    "601800": "中国交建", "601818": "光大银行", "601888": "中国中免",
    "601899": "紫金矿业", "601919": "中远海控", "601933": "永辉超市",
    "601985": "中国核电", "601998": "中信银行",
}


# ============================================================
# 二、模拟数据生成（实际需要接入真实数据）
# ============================================================

def get_stock_data(stock_code: str) -> Dict:
    """
    获取股票数据（模拟）
    实际需要接入：Tushare、AKShare 等数据源
    """
    import random
    random.seed(hash(stock_code) % 10000)
    
    # 模拟当前价格
    current_price = random.uniform(5, 200)
    
    # 模拟历史数据
    daily_prices = [current_price * random.uniform(0.9, 1.1) for _ in range(60)]
    weekly_prices = [current_price * random.uniform(0.85, 1.15) for _ in range(52)]
    
    # 计算技术指标
    ma5 = sum(daily_prices[-5:]) / 5
    ma10 = sum(daily_prices[-10:]) / 10
    ma20 = sum(daily_prices[-20:]) / 20
    ma60 = sum(daily_prices[-60:]) / 60
    
    # 周线MA
    weekly_ma5 = sum(weekly_prices[-5:]) / 5
    weekly_ma10 = sum(weekly_prices[-10:]) / 10
    weekly_ma20 = sum(weekly_prices[-20:]) / 20
    
    # 成交量
    volume_ratio = random.uniform(0.5, 3.0)
    
    # 近期高低点
    high_20 = max(daily_prices[-20:])
    low_20 = min(daily_prices[-20:])
    high_60 = max(daily_prices)
    low_60 = min(daily_prices)
    
    # 波动率
    volatility = math.sqrt(sum((p - sum(daily_prices)/len(daily_prices))**2 for p in daily_prices) / len(daily_prices)) / current_price
    
    return {
        'code': stock_code,
        'current_price': current_price,
        'daily_prices': daily_prices,
        'weekly_prices': weekly_prices,
        'ma5': ma5,
        'ma10': ma10,
        'ma20': ma20,
        'ma60': ma60,
        'weekly_ma5': weekly_ma5,
        'weekly_ma10': weekly_ma10,
        'weekly_ma20': weekly_ma20,
        'volume_ratio': volume_ratio,
        'high_20': high_20,
        'low_20': low_20,
        'high_60': high_60,
        'low_60': low_60,
        'volatility': volatility,
        'rsi': random.uniform(20, 80),
        'macd': random.uniform(-1, 1),
    }


# ============================================================
# 三、技术分析
# ============================================================

def analyze_daily(data: Dict) -> Dict:
    """日线分析（短线）"""
    signals = []
    score = 0
    
    # 1. 均线多头排列
    if data['ma5'] > data['ma10'] > data['ma20']:
        signals.append("均线多头排列")
        score += 2
    
    # 2. 站上MA5
    if data['current_price'] > data['ma5']:
        signals.append("站上MA5")
        score += 1
    
    # 3. 放量
    if data['volume_ratio'] > 1.5:
        signals.append(f"放量（量比{data['volume_ratio']:.2f}）")
        score += 1
    
    # 4. 突破20日高点
    if data['current_price'] >= data['high_20'] * 0.98:
        signals.append("突破20日高点")
        score += 2
    
    # 5. RSI 超卖区
    if data['rsi'] < 30:
        signals.append(f"RSI超卖({data['rsi']:.1f})")
        score += 1
    elif data['rsi'] > 70:
        signals.append(f"RSI超买({data['rsi']:.1f})")
        score -= 1
    
    # 6. MACD
    if data['macd'] > 0:
        signals.append("MACD金叉")
        score += 1
    
    return {
        'signals': signals,
        'score': score,
        'trend': 'UP' if score >= 3 else ('DOWN' if score <= 0 else 'NEUTRAL')
    }


def analyze_weekly(data: Dict) -> Dict:
    """周线分析（中线）"""
    signals = []
    score = 0
    
    # 1. 周线趋势
    if data['weekly_ma5'] > data['weekly_ma10'] > data['weekly_ma20']:
        signals.append("周线多头排列")
        score += 3
    
    # 2. 价格位置
    price_position = (data['current_price'] - data['low_60']) / (data['high_60'] - data['low_60'])
    if price_position < 0.3:
        signals.append(f"低位区({price_position:.0%})")
        score += 2
    elif price_position > 0.7:
        signals.append(f"高位区({price_position:.0%})")
        score -= 1
    
    # 3. 波动率
    if data['volatility'] < 0.02:
        signals.append("低波动")
        score += 1
    
    return {
        'signals': signals,
        'score': score,
        'trend': 'UP' if score >= 3 else ('DOWN' if score <= 0 else 'NEUTRAL'),
        'price_position': price_position
    }


# ============================================================
# 四、计算买卖价格
# ============================================================

def calculate_trade_levels(data: Dict, daily_analysis: Dict, weekly_analysis: Dict) -> Dict:
    """计算买卖价格、止盈止损、仓位管理"""
    current = data['current_price']
    
    # 买入价
    if daily_analysis['score'] >= 3:
        buy_price = round(current * 0.99, 2)
    else:
        buy_price = round(data['ma5'] * 0.98, 2)
    
    # 止损价（短线 -5%，中线 -8%）
    stop_loss_short = round(current * 0.95, 2)
    stop_loss_mid = round(current * 0.92, 2)
    
    # 止盈价（短线 +8%，中线 +15%）
    take_profit_short = round(current * 1.08, 2)
    take_profit_mid = round(current * 1.15, 2)
    
    # 卖出价（目标价）
    if weekly_analysis['score'] >= 3:
        sell_price = take_profit_mid
        is_mid_term = True
    else:
        sell_price = take_profit_short
        is_mid_term = False
    
    # 仓位建议
    if daily_analysis['score'] >= 4 and weekly_analysis['score'] >= 3:
        max_position = 40
    elif daily_analysis['score'] >= 3:
        max_position = 30
    else:
        max_position = 20
    
    # 买入仓位（分批建仓）
    buy_position_1 = round(max_position * 0.5)  # 首次建仓 50%
    buy_price_2 = round(buy_price * 0.97, 2)    # 回调加仓价
    buy_position_2 = round(max_position * 0.5)  # 加仓 50%
    
    # 卖出仓位（分批止盈）
    if is_mid_term:
        # 中线：+10%卖30%，+15%卖40%，+20%清仓
        sell_price_1 = round(current * 1.10, 2)
        sell_position_1 = round(max_position * 0.3)
        sell_price_2 = round(current * 1.15, 2)
        sell_position_2 = round(max_position * 0.4)
        sell_price_3 = round(current * 1.20, 2)
        sell_position_3 = round(max_position * 0.3)
    else:
        # 短线：+5%卖30%，+8%卖40%，+10%清仓
        sell_price_1 = round(current * 1.05, 2)
        sell_position_1 = round(max_position * 0.3)
        sell_price_2 = round(current * 1.08, 2)
        sell_position_2 = round(max_position * 0.4)
        sell_price_3 = round(current * 1.10, 2)
        sell_position_3 = round(max_position * 0.3)
    
    return {
        'buy_price': buy_price,
        'sell_price': sell_price,
        'stop_loss_short': stop_loss_short,
        'stop_loss_mid': stop_loss_mid,
        'take_profit_short': take_profit_short,
        'take_profit_mid': take_profit_mid,
        'max_position': f"{max_position}%",
        # 买入仓位
        'buy_position_1': f"{buy_position_1}%",
        'buy_price_1': buy_price,
        'buy_position_2': f"{buy_position_2}%",
        'buy_price_2': buy_price_2,
        # 卖出仓位
        'sell_price_1': sell_price_1,
        'sell_position_1': f"{sell_position_1}%",
        'sell_price_2': sell_price_2,
        'sell_position_2': f"{sell_position_2}%",
        'sell_price_3': sell_price_3,
        'sell_position_3': f"{sell_position_3}%",
        'holding_period': "中线" if is_mid_term else "短线"
    }


# ============================================================
# 五、选股逻辑
# ============================================================

def select_stocks(top_n: int = 10) -> List[Dict]:
    """选股"""
    results = []
    
    for code, name in SSE100_STOCKS.items():
        # 获取数据
        data = get_stock_data(code)
        
        # 技术分析
        daily = analyze_daily(data)
        weekly = analyze_weekly(data)
        
        # 综合得分
        total_score = daily['score'] + weekly['score']
        
        # 只选得分 > 3 的
        if total_score < 3:
            continue
        
        # 计算买卖价格
        trade_levels = calculate_trade_levels(data, daily, weekly)
        
        results.append({
            'code': code,
            'name': name,
            'current_price': data['current_price'],
            'total_score': total_score,
            'daily_score': daily['score'],
            'weekly_score': weekly['score'],
            'daily_signals': daily['signals'],
            'weekly_signals': weekly['signals'],
            'daily_trend': daily['trend'],
            'weekly_trend': weekly['trend'],
            'volume_ratio': data['volume_ratio'],
            'rsi': data['rsi'],
            **trade_levels
        })
    
    # 按得分排序
    results.sort(key=lambda x: x['total_score'], reverse=True)
    
    return results[:top_n]


# ============================================================
# 六、生成选股报告
# ============================================================

def generate_report(selected_stocks: List[Dict]) -> str:
    """生成选股报告"""
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    lines.append("=" * 70)
    lines.append(f"上证100短中线选股报告")
    lines.append(f"时间：{now}")
    lines.append("=" * 70)
    lines.append("")
    
    lines.append("【选股策略】日线+周线多因子模型")
    lines.append("  短线：MA5/10/20、放量、突破、RSI、MACD")
    lines.append("  中线：周线趋势、价格位置、波动率")
    lines.append("")
    
    lines.append(f"【今日精选】共 {len(selected_stocks)} 只")
    lines.append("=" * 70)
    
    for i, s in enumerate(selected_stocks, 1):
        # 信号强度
        if s['total_score'] >= 6:
            signal_strength = "⭐⭐⭐ 强"
        elif s['total_score'] >= 4:
            signal_strength = "⭐⭐ 中"
        else:
            signal_strength = "⭐ 弱"
        
        lines.append(f"")
        lines.append(f"【{i}】{s['code']} {s['name']}")
        lines.append(f"  当前价: ¥{s['current_price']:.2f} | 综合得分: {s['total_score']} | {signal_strength}")
        lines.append(f"  日线得分: {s['daily_score']} ({s['daily_trend']}) | 周线得分: {s['weekly_score']} ({s['weekly_trend']})")
        lines.append(f"")
        lines.append(f"  📊 交易建议：")
        lines.append(f"     买入价: ¥{s['buy_price']:.2f}")
        lines.append(f"     目标价: ¥{s['sell_price']:.2f}")
        lines.append(f"     止损价: ¥{s['stop_loss_short']:.2f} (短线) / ¥{s['stop_loss_mid']:.2f} (中线)")
        lines.append(f"     止盈价: ¥{s['take_profit_short']:.2f} (短线) / ¥{s['take_profit_mid']:.2f} (中线)")
        lines.append(f"     最大仓位: {s['max_position']} | 周期: {s['holding_period']}")
        lines.append(f"")
        lines.append(f"  💰 仓位管理：")
        lines.append(f"     【买入】首次 ¥{s['buy_price_1']:.2f} 买入 {s['buy_position_1']}")
        lines.append(f"            回调 ¥{s['buy_price_2']:.2f} 加仓 {s['buy_position_2']}")
        lines.append(f"     【卖出】第一档 ¥{s['sell_price_1']:.2f} 卖出 {s['sell_position_1']}")
        lines.append(f"            第二档 ¥{s['sell_price_2']:.2f} 卖出 {s['sell_position_2']}")
        lines.append(f"            第三档 ¥{s['sell_price_3']:.2f} 清仓 {s['sell_position_3']}")
        lines.append(f"")
        lines.append(f"  📈 日线信号: {', '.join(s['daily_signals']) if s['daily_signals'] else '无'}")
        lines.append(f"  📊 周线信号: {', '.join(s['weekly_signals']) if s['weekly_signals'] else '无'}")
        lines.append(f"  📉 技术指标: RSI={s['rsi']:.1f} 量比={s['volume_ratio']:.2f}")
        lines.append("-" * 70)
    
    lines.append("")
    lines.append("【操作纪律】")
    lines.append("  1. 严格执行止损，短线 -5% / 中线 -8%")
    lines.append("  2. 分批止盈，短线 +5% 卖一半，+8% 清仓")
    lines.append("  3. 中线持有，目标 +15% 或周线趋势改变")
    lines.append("  4. 总仓位不超过 80%，保留现金应对风险")
    lines.append("")
    lines.append("=" * 70)
    
    return "\n".join(lines)


# ============================================================
# 七、保存选股结果
# ============================================================

def save_selection(selected_stocks: List[Dict], output_dir: str = None):
    """保存选股结果"""
    if output_dir is None:
        output_dir = os.path.join("/root/.openclaw/workspace/projects/stock-tracking/selections")
    
    os.makedirs(output_dir, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(output_dir, f"selection_{today}.json")
    
    data = {
        "date": today,
        "time": datetime.now().strftime("%H:%M"),
        "stocks": selected_stocks
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filename


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("上证100短中线选股系统")
    print("=" * 70)
    print()
    
    # 选股
    selected = select_stocks(top_n=10)
    
    # 生成报告
    report = generate_report(selected)
    print(report)
    
    # 保存结果
    if selected:
        filename = save_selection(selected)
        print(f"\n选股结果已保存: {filename}")
    else:
        print("\n今日无符合条件的股票")
