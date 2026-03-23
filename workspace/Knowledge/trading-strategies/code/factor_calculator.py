#!/usr/bin/env python3
"""
量化因子计算器 - Factor Calculator (纯Python版)
=====================================
功能：计算股票的六大核心因子，并进行多因子组合回测
作者：小秘
日期：2026-03-16
版本：v1.0 (无外部依赖版)
"""

import math
import statistics
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


# ============================================================
# 一、辅助函数
# ============================================================

def zscore(values: List[float]) -> List[float]:
    """Z-Score标准化"""
    if len(values) < 2:
        return [0] * len(values)
    
    mean = statistics.mean(values)
    std = statistics.stdev(values)
    
    if std == 0:
        return [0] * len(values)
    
    return [(v - mean) / std for v in values]


def spearman_correlation(x: List[float], y: List[float]) -> float:
    """计算Spearman相关系数（IC值）"""
    if len(x) != len(y) or len(x) < 3:
        return 0.0
    
    # 转换为秩
    def rank(values):
        sorted_idx = sorted(range(len(values)), key=lambda i: values[i] if not math.isnan(values[i]) else float('inf'))
        ranks = [0] * len(values)
        for rank, idx in enumerate(sorted_idx, 1):
            ranks[idx] = rank
        return ranks
    
    x_rank = rank(x)
    y_rank = rank(y)
    
    # 计算Pearson相关系数
    n = len(x_rank)
    sum_x = sum(x_rank)
    sum_y = sum(y_rank)
    sum_xy = sum(xr * yr for xr, yr in zip(x_rank, y_rank))
    sum_x2 = sum(xr ** 2 for xr in x_rank)
    sum_y2 = sum(yr ** 2 for yr in y_rank)
    
    numerator = n * sum_xy - sum_x * sum_y
    denominator = math.sqrt((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2))
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator


def quantile_cut(values: List[float], n_groups: int) -> List[int]:
    """将值分成n_groups组"""
    if len(values) < n_groups:
        return [0] * len(values)
    
    # 排序获取分位点
    sorted_values = sorted([v for v in values if not math.isnan(v)])
    if len(sorted_values) < n_groups:
        return [0] * len(values)
    
    # 计算分位点
    quantiles = []
    for i in range(1, n_groups):
        idx = int(len(sorted_values) * i / n_groups)
        quantiles.append(sorted_values[idx])
    
    # 分组
    groups = []
    for v in values:
        if math.isnan(v):
            groups.append(-1)
        else:
            group = 0
            for q in quantiles:
                if v > q:
                    group += 1
            groups.append(group)
    
    return groups


# ============================================================
# 二、单因子计算函数
# ============================================================

def calc_value_factor(data: Dict[str, List[float]]) -> List[float]:
    """
    价值因子计算
    -----------------
    输入：data字典，包含 price, book_value, eps, dividend
    输出：价值因子得分列表
    
    公式：-(PB_z + PE_z - 股息率_z) / 3
    """
    prices = data.get('price', [])
    book_values = data.get('book_value_per_share', [])
    eps = data.get('eps', [])
    dividends = data.get('dividend_per_share', [])
    
    n = len(prices)
    if n == 0:
        return []
    
    # 计算指标
    pb = [prices[i] / book_values[i] if book_values[i] != 0 else float('nan') for i in range(n)]
    pe = [prices[i] / eps[i] if eps[i] != 0 else float('nan') for i in range(n)]
    dy = [dividends[i] / prices[i] if prices[i] != 0 else float('nan') for i in range(n)]
    
    # 标准化
    pb_z = zscore([v if not math.isnan(v) else 0 for v in pb])
    pe_z = zscore([v if not math.isnan(v) else 0 for v in pe])
    dy_z = zscore([v if not math.isnan(v) else 0 for v in dy])
    
    # 综合得分（负号表示低PB/PE是好的）
    value_score = [-(pb_z[i] + pe_z[i] - dy_z[i]) / 3 for i in range(n)]
    
    return value_score


def calc_momentum_factor(data: Dict[str, List[float]], 
                        lookback: int = 252, 
                        exclude_recent: int = 21) -> List[float]:
    """
    动量因子计算
    -----------------
    输入：data字典，包含 price
    输出：动量因子得分列表
    
    公式：过去lookback天收益（排除最近exclude_recent天）
    """
    prices = data.get('price', [])
    n = len(prices)
    
    if n < lookback:
        return [0] * n
    
    momentum = []
    for i in range(n):
        if i < lookback - exclude_recent:
            momentum.append(float('nan'))
        else:
            start_idx = i - lookback + exclude_recent
            end_idx = i - exclude_recent
            if start_idx < 0 or end_idx < 0:
                momentum.append(float('nan'))
            else:
                ret = prices[end_idx] / prices[start_idx] - 1
                momentum.append(ret)
    
    # 标准化
    momentum_z = zscore([v if not math.isnan(v) else 0 for v in momentum])
    
    return momentum_z


def calc_quality_factor(data: Dict[str, List[float]]) -> List[float]:
    """
    质量因子计算
    -----------------
    输入：data字典，包含财务数据
    输出：质量因子得分列表
    
    公式：(ROE_z + ROA_z + 毛利率_z - 负债率_z) / 4
    """
    net_income = data.get('net_income', [])
    total_equity = data.get('total_equity', [])
    total_assets = data.get('total_assets', [])
    total_debt = data.get('total_debt', [])
    revenue = data.get('revenue', [])
    cost_of_revenue = data.get('cost_of_revenue', [])
    
    n = len(net_income)
    if n == 0:
        return []
    
    # 计算指标
    roe = [net_income[i] / total_equity[i] if total_equity[i] != 0 else float('nan') for i in range(n)]
    roa = [net_income[i] / total_assets[i] if total_assets[i] != 0 else float('nan') for i in range(n)]
    gm = [(revenue[i] - cost_of_revenue[i]) / revenue[i] if revenue[i] != 0 else float('nan') for i in range(n)]
    dr = [total_debt[i] / total_assets[i] if total_assets[i] != 0 else float('nan') for i in range(n)]
    
    # 标准化
    roe_z = zscore([v if not math.isnan(v) else 0 for v in roe])
    roa_z = zscore([v if not math.isnan(v) else 0 for v in roa])
    gm_z = zscore([v if not math.isnan(v) else 0 for v in gm])
    dr_z = zscore([-v if not math.isnan(v) else 0 for v in dr])  # 负号：低负债好
    
    # 综合得分
    quality_score = [(roe_z[i] + roa_z[i] + gm_z[i] + dr_z[i]) / 4 for i in range(n)]
    
    return quality_score


def calc_size_factor(data: Dict[str, List[float]]) -> List[float]:
    """
    规模因子计算
    -----------------
    输入：data字典，包含 price, total_shares
    输出：规模因子得分列表（负值表示小盘股）
    
    公式：-log(市值)_z
    """
    prices = data.get('price', [])
    total_shares = data.get('total_shares', [])
    
    n = len(prices)
    if n == 0:
        return []
    
    # 计算市值
    market_cap = [prices[i] * total_shares[i] for i in range(n)]
    log_mc = [math.log(mc) if mc > 0 else float('nan') for mc in market_cap]
    
    # 标准化（负号：小市值好）
    size_z = zscore([-v if not math.isnan(v) else 0 for v in log_mc])
    
    return size_z


def calc_low_vol_factor(data: Dict[str, List[float]], lookback: int = 252) -> List[float]:
    """
    低波动因子计算
    -----------------
    输入：data字典，包含 price
    输出：低波动因子得分列表（负值表示低波动）
    
    公式：-波动率_z
    """
    prices = data.get('price', [])
    n = len(prices)
    
    if n < lookback:
        return [0] * n
    
    # 计算收益率
    returns = [(prices[i] / prices[i-1] - 1) if prices[i-1] != 0 else 0 for i in range(1, n)]
    
    # 滚动波动率
    volatility = [float('nan')] * lookback
    for i in range(lookback, n):
        window_returns = returns[i-lookback:i]
        if len(window_returns) > 0:
            mean_ret = statistics.mean(window_returns)
            var_ret = statistics.mean([(r - mean_ret) ** 2 for r in window_returns])
            vol = math.sqrt(var_ret * 252)  # 年化
            volatility.append(vol)
        else:
            volatility.append(float('nan'))
    
    # 标准化（负号：低波动好）
    vol_z = zscore([-v if not math.isnan(v) else 0 for v in volatility])
    
    return vol_z


def calc_growth_factor(data: Dict[str, List[float]], period: int = 252) -> List[float]:
    """
    成长因子计算
    -----------------
    输入：data字典，包含 revenue, eps
    输出：成长因子得分列表
    
    公式：(营收增长率_z + EPS增长率_z) / 2
    """
    revenue = data.get('revenue', [])
    eps = data.get('eps', [])
    
    n = len(revenue)
    if n < period:
        return [0] * n
    
    # 计算增长率
    rev_growth = [float('nan')] * period
    eps_growth = [float('nan')] * period
    
    for i in range(period, n):
        if revenue[i-period] != 0:
            rev_growth.append((revenue[i] / revenue[i-period]) - 1)
        else:
            rev_growth.append(float('nan'))
        
        if eps[i-period] != 0:
            eps_growth.append((eps[i] / eps[i-period]) - 1)
        else:
            eps_growth.append(float('nan'))
    
    # 标准化
    rev_z = zscore([v if not math.isnan(v) else 0 for v in rev_growth])
    eps_z = zscore([v if not math.isnan(v) else 0 for v in eps_growth])
    
    # 综合得分
    growth_score = [(rev_z[i] + eps_z[i]) / 2 for i in range(n)]
    
    return growth_score


# ============================================================
# 三、多因子组合
# ============================================================

def calc_multifactor_score(data: Dict[str, List[float]], 
                          factor_weights: Dict[str, float]) -> List[float]:
    """
    多因子综合得分
    -----------------
    输入：
    - data: 股票数据字典
    - factor_weights: 因子权重字典
    
    输出：综合得分列表
    """
    n = len(data.get('price', []))
    if n == 0:
        return []
    
    # 计算各因子得分
    factor_scores = {}
    
    if 'value' in factor_weights:
        factor_scores['value'] = calc_value_factor(data)
    
    if 'momentum' in factor_weights:
        factor_scores['momentum'] = calc_momentum_factor(data)
    
    if 'quality' in factor_weights:
        factor_scores['quality'] = calc_quality_factor(data)
    
    if 'size' in factor_weights:
        factor_scores['size'] = calc_size_factor(data)
    
    if 'low_vol' in factor_weights:
        factor_scores['low_vol'] = calc_low_vol_factor(data)
    
    if 'growth' in factor_weights:
        factor_scores['growth'] = calc_growth_factor(data)
    
    # 加权合成
    composite_score = [0.0] * n
    total_weight = 0
    
    for factor_name, weight in factor_weights.items():
        if factor_name in factor_scores:
            score = factor_scores[factor_name]
            for i in range(n):
                composite_score[i] += score[i] * weight
            total_weight += weight
    
    if total_weight > 0:
        composite_score = [s / total_weight for s in composite_score]
    
    return composite_score


# ============================================================
# 四、回测函数
# ============================================================

def calc_ic(factor_values: List[float], forward_returns: List[float]) -> Tuple[float, str]:
    """
    计算IC值
    -----------------
    返回：(IC值, IC质量)
    """
    # 去除NaN
    valid_pairs = [(f, r) for f, r in zip(factor_values, forward_returns) 
                   if not math.isnan(f) and not math.isnan(r)]
    
    if len(valid_pairs) < 10:
        return 0.0, '数据不足'
    
    factors = [p[0] for p in valid_pairs]
    returns = [p[1] for p in valid_pairs]
    
    ic = spearman_correlation(factors, returns)
    
    if abs(ic) > 0.05:
        quality = '优秀'
    elif abs(ic) > 0.03:
        quality = '良好'
    elif abs(ic) > 0.01:
        quality = '一般'
    else:
        quality = '较差'
    
    return ic, quality


def backtest_single_factor(factor_values: List[float], 
                          returns: List[float],
                          n_groups: int = 5) -> Dict:
    """
    单因子分组回测
    -----------------
    返回：各组收益、胜率、IC等
    """
    # 去除NaN
    valid_pairs = [(f, r) for f, r in zip(factor_values, returns) 
                   if not math.isnan(f) and not math.isnan(r)]
    
    if len(valid_pairs) < n_groups * 10:
        return {'error': '数据不足'}
    
    factors = [p[0] for p in valid_pairs]
    rets = [p[1] for p in valid_pairs]
    
    # 分组
    groups = quantile_cut(factors, n_groups)
    
    # 计算各组统计
    group_stats = []
    for g in range(n_groups):
        group_returns = [rets[i] for i in range(len(groups)) if groups[i] == g]
        if len(group_returns) > 0:
            avg_ret = statistics.mean(group_returns)
            win_rate = sum(1 for r in group_returns if r > 0) / len(group_returns)
            group_stats.append({
                'group': g + 1,
                'avg_return': avg_ret,
                'win_rate': win_rate,
                'count': len(group_returns)
            })
    
    # 多空收益
    if len(group_stats) >= 2:
        long_short = group_stats[-1]['avg_return'] - group_stats[0]['avg_return']
    else:
        long_short = 0
    
    # IC值
    ic, ic_quality = calc_ic(factors, rets)
    
    return {
        'group_stats': group_stats,
        'long_short_return': long_short,
        'ic': ic,
        'ic_quality': ic_quality
    }


def calc_win_rate(returns: List[float]) -> float:
    """计算胜率"""
    valid_returns = [r for r in returns if not math.isnan(r)]
    if len(valid_returns) == 0:
        return 0.0
    
    win_count = sum(1 for r in valid_returns if r > 0)
    return win_count / len(valid_returns)


def calc_sharpe_ratio(returns: List[float], 
                     risk_free_rate: float = 0.03,
                     periods_per_year: int = 252) -> float:
    """计算夏普比率"""
    valid_returns = [r for r in returns if not math.isnan(r)]
    if len(valid_returns) < 10:
        return 0.0
    
    annual_return = statistics.mean(valid_returns) * periods_per_year
    annual_vol = statistics.stdev(valid_returns) * math.sqrt(periods_per_year)
    
    if annual_vol == 0:
        return 0.0
    
    return (annual_return - risk_free_rate) / annual_vol


def calc_max_drawdown(prices: List[float]) -> float:
    """计算最大回撤"""
    valid_prices = [p for p in prices if not math.isnan(p) and p > 0]
    if len(valid_prices) < 2:
        return 0.0
    
    peak = valid_prices[0]
    max_dd = 0
    
    for price in valid_prices:
        if price > peak:
            peak = price
        dd = (peak - price) / peak
        if dd > max_dd:
            max_dd = dd
    
    return max_dd


# ============================================================
# 五、完整回测报告
# ============================================================

def generate_backtest_report(data: Dict[str, List[float]],
                            factor_weights: Dict[str, float],
                            forward_periods: int = 21) -> str:
    """
    生成完整回测报告
    -----------------
    """
    prices = data.get('price', [])
    n = len(prices)
    
    if n < forward_periods + 50:
        return "错误：数据不足"
    
    # 计算综合得分
    composite_score = calc_multifactor_score(data, factor_weights)
    
    # 计算未来收益
    forward_returns = []
    for i in range(n):
        if i + forward_periods < n:
            ret = (prices[i + forward_periods] / prices[i]) - 1
            forward_returns.append(ret)
        else:
            forward_returns.append(float('nan'))
    
    # 回测
    result = backtest_single_factor(composite_score, forward_returns)
    
    if 'error' in result:
        return f"回测失败: {result['error']}"
    
    # 生成报告
    lines = []
    lines.append("=" * 60)
    lines.append("量化因子回测报告")
    lines.append("=" * 60)
    lines.append("")
    
    # 因子权重
    lines.append("【因子权重】")
    for factor, weight in factor_weights.items():
        lines.append(f"  {factor}: {weight:.1%}")
    lines.append("")
    
    # 回测结果
    lines.append("【回测结果】")
    lines.append(f"  样本数量: {n}")
    lines.append(f"  预测周期: {forward_periods}天")
    lines.append(f"  IC值: {result['ic']:.4f} ({result['ic_quality']})")
    lines.append(f"  多空收益: {result['long_short_return']:.2%}")
    lines.append("")
    
    # 分组收益
    lines.append("【分组收益】")
    for stat in result['group_stats']:
        lines.append(f"  第{stat['group']}组: 收益={stat['avg_return']:.2%}, 胜率={stat['win_rate']:.1%}")
    lines.append("")
    
    # 胜率统计
    lines.append("【胜率统计】")
    win_rates = [s['win_rate'] for s in result['group_stats']]
    lines.append(f"  最高组胜率: {max(win_rates):.1%}")
    lines.append(f"  最低组胜率: {min(win_rates):.1%}")
    lines.append(f"  平均胜率: {statistics.mean(win_rates):.1%}")
    lines.append("")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)


# ============================================================
# 六、预设因子组合
# ============================================================

CONSERVATIVE_WEIGHTS = {'value': 0.30, 'quality': 0.30, 'low_vol': 0.40}
GROWTH_WEIGHTS = {'momentum': 0.35, 'growth': 0.35, 'quality': 0.30}
BALANCED_WEIGHTS = {'value': 0.20, 'momentum': 0.20, 'quality': 0.25, 'size': 0.15, 'low_vol': 0.20}
A_STOCK_WEIGHTS = {'value': 0.15, 'momentum': 0.20, 'quality': 0.30, 'size': 0.20, 'low_vol': 0.15}


# ============================================================
# 七、主程序
# ============================================================

if __name__ == "__main__":
    import random
    random.seed(42)
    
    print("=" * 60)
    print("量化因子计算器 v1.0")
    print("=" * 60)
    print()
    
    # 生成模拟数据
    n = 500
    data = {
        'price': [10 + random.uniform(-0.5, 0.5) * i * 0.1 for i in range(n)],
        'book_value_per_share': [random.uniform(5, 15) for _ in range(n)],
        'eps': [random.uniform(0.5, 2) for _ in range(n)],
        'dividend_per_share': [random.uniform(0.1, 0.5) for _ in range(n)],
        'total_shares': [random.uniform(1e8, 1e10) for _ in range(n)],
        'net_income': [random.uniform(1e8, 1e10) for _ in range(n)],
        'total_equity': [random.uniform(5e8, 5e10) for _ in range(n)],
        'total_assets': [random.uniform(1e9, 1e11) for _ in range(n)],
        'total_debt': [random.uniform(1e8, 5e10) for _ in range(n)],
        'revenue': [random.uniform(1e9, 1e11) for _ in range(n)],
        'cost_of_revenue': [random.uniform(5e8, 5e10) for _ in range(n)]
    }
    
    # 测试因子计算
    print("【因子计算测试】")
    value = calc_value_factor(data)
    quality = calc_quality_factor(data)
    size = calc_size_factor(data)
    
    print(f"  价值因子: 均值={statistics.mean(value):.3f}")
    print(f"  质量因子: 均值={statistics.mean(quality):.3f}")
    print(f"  规模因子: 均值={statistics.mean(size):.3f}")
    print()
    
    # 测试回测报告
    print(generate_backtest_report(data, BALANCED_WEIGHTS))
