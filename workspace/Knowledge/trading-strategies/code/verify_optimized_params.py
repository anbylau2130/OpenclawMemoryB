#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V5优化参数应用验证
验证优化参数是否正确应用
"""

import json
from datetime import datetime
from pathlib import Path

# 导入优化后的模块
from signal_filter import SignalModule, SignalFilter
from trading_executor import TradingExecutor, Position

def verify_optimized_parameters():
    """验证优化参数是否正确应用"""
    
    print("="*70)
    print("V5优化参数应用验证")
    print("="*70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # ==================== 1. 验证因子权重 ====================
    print("【1. 验证因子权重】")
    print("-"*70)
    
    signal_filter = SignalFilter()
    
    expected_weights = {
        'VWAP': 3.0,
        'BOLL': 3.0,   # ↑1.0
        'KDJ': 3.0,    # ↑1.5
        'RSI': 2.0,    # ↑0.5
        'MACD': 1.0,   # ↑0.5
        'MA': 1.0,     # ↑0.5
        'VOLUME': 1.0
    }
    
    print(f"{'因子':<10} {'期望权重':<12} {'实际权重':<12} {'状态':<10}")
    print("-"*70)
    
    all_match = True
    for factor, expected in expected_weights.items():
        actual = signal_filter.factor_weights.get(factor, 0)
        status = "✅" if actual == expected else "❌"
        print(f"{factor:<10} {expected:<12.1f} {actual:<12.1f} {status:<10}")
        
        if actual != expected:
            all_match = False
    
    if all_match:
        print("\n✅ 因子权重验证通过")
    else:
        print("\n❌ 因子权重验证失败")
    
    # ==================== 2. 验证选股阈值 ====================
    print("\n【2. 验证选股阈值】")
    print("-"*70)
    
    expected_threshold = 4.0
    actual_threshold = signal_filter.min_score
    
    print(f"期望阈值: {expected_threshold}")
    print(f"实际阈值: {actual_threshold}")
    
    if actual_threshold == expected_threshold:
        print("✅ 选股阈值验证通过")
    else:
        print("❌ 选股阈值验证失败")
    
    # ==================== 3. 验证风控参数 ====================
    print("\n【3. 验证风控参数】")
    print("-"*70)
    
    executor = TradingExecutor(initial_capital=100000)
    
    # 验证最大仓位
    expected_max_position = 0.1  # 10%
    actual_max_position = executor.max_position_pct
    
    print(f"最大仓位:")
    print(f"  期望: {expected_max_position*100:.0f}%")
    print(f"  实际: {actual_max_position*100:.0f}%")
    print(f"  状态: {'✅' if actual_max_position == expected_max_position else '❌'}")
    
    # 验证总仓位上限
    expected_total_position = 0.6  # 60%
    actual_total_position = executor.max_total_position_pct
    
    print(f"\n总仓位上限:")
    print(f"  期望: {expected_total_position*100:.0f}%")
    print(f"  实际: {actual_total_position*100:.0f}%")
    print(f"  状态: {'✅' if actual_total_position == expected_total_position else '❌'}")
    
    # 验证止损止盈
    print(f"\n止损止盈:")
    test_position = Position('600031', 100, 20.85, datetime.now())
    
    expected_stop_loss = 20.85 * 0.98  # -2%
    expected_take_profit_1 = 20.85 * 1.06  # +6%
    expected_take_profit_2 = 20.85 * 1.10  # +10%
    
    print(f"  止损: ¥{test_position.stop_loss:.2f} (期望: ¥{expected_stop_loss:.2f}) {'✅' if abs(test_position.stop_loss - expected_stop_loss) < 0.01 else '❌'}")
    print(f"  止盈1: ¥{test_position.take_profit_1:.2f} (期望: ¥{expected_take_profit_1:.2f}) {'✅' if abs(test_position.take_profit_1 - expected_take_profit_1) < 0.01 else '❌'}")
    print(f"  止盈2: ¥{test_position.take_profit_2:.2f} (期望: ¥{expected_take_profit_2:.2f}) {'✅' if abs(test_position.take_profit_2 - expected_take_profit_2) < 0.01 else '❌'}")
    
    # 计算盈亏比
    risk_reward_ratio = (test_position.take_profit_2 - test_position.buy_price) / (test_position.buy_price - test_position.stop_loss)
    print(f"  盈亏比: {risk_reward_ratio:.1f} (期望: 5.0) {'✅' if abs(risk_reward_ratio - 5.0) < 0.1 else '❌'}")
    
    # ==================== 4. 整体验证结果 ====================
    print("\n【4. 整体验证结果】")
    print("="*70)
    
    all_verified = (
        all_match and
        actual_threshold == expected_threshold and
        actual_max_position == expected_max_position and
        actual_total_position == expected_total_position and
        abs(test_position.stop_loss - expected_stop_loss) < 0.01 and
        abs(risk_reward_ratio - 5.0) < 0.1
    )
    
    if all_verified:
        print("✅ 所有优化参数已正确应用")
        print("\n优化成果:")
        print("  - 因子权重: 6项调整已生效")
        print("  - 选股阈值: 3.0 → 4.0 (↑33%)")
        print("  - 止损: -3% → -2%")
        print("  - 最大仓位: 20% → 10%")
        print("  - 总仓位: 80% → 60%")
        print("  - 盈亏比: 3.3 → 5.0 (↑52%)")
    else:
        print("❌ 部分参数验证失败，请检查")
    
    # ==================== 5. 测试优化后的效果 ====================
    print("\n【5. 测试优化后效果】")
    print("-"*70)
    
    # 创建测试信号
    test_signals = [
        {
            'symbol': '600031',
            'name': '三一重工',
            'total_score': 4.5,
            'factors': ['VWAP_BUY', 'BOLL_BUY', 'KDJ_OVERSOLD'],
            'buy_price': 20.85
        },
        {
            'symbol': '600036',
            'name': '招商银行',
            'total_score': 3.8,  # 低于新阈值4.0，应被过滤
            'factors': ['VWAP_BUY', 'RSI_OVERSOLD'],
            'buy_price': 39.91
        },
        {
            'symbol': '600519',
            'name': '贵州茅台',
            'total_score': 5.0,
            'factors': ['VWAP_BUY', 'BOLL_BUY', 'KDJ_OVERSOLD', 'RSI_OVERSOLD'],
            'buy_price': 1680.00
        }
    ]
    
    # 创建信号模块
    signal_module = SignalModule(min_score=4.0, combine_method='ic_weighted')
    
    # 处理信号
    result = signal_module.process_signals(test_signals)
    
    print(f"测试信号数量: {len(test_signals)}")
    print(f"过滤后信号: {result['filtered_count']}")
    print(f"有效信号: {result['valid_count']}")
    
    print("\n有效信号:")
    for i, sig in enumerate(result['signals'], 1):
        print(f"{i}. {sig['symbol']} {sig['name']}")
        print(f"   得分: {sig['total_score']:.1f}")
        print(f"   因子: {', '.join(sig['factors'])}")
    
    # 测试交易执行
    print("\n测试交易执行（优化后仓位）:")
    
    for signal in result['signals']:
        # 计算仓位（优化后：强信号10%）
        strength = 'strong' if signal['total_score'] >= 4.5 else 'medium'
        shares = executor.calculate_position_size(signal['buy_price'], strength)
        
        print(f"\n  {signal['symbol']} {signal['name']}")
        print(f"    信号强度: {strength}")
        print(f"    计算仓位: {shares}股")
        print(f"    资金占用: ¥{shares * signal['buy_price']:,.2f}")
        print(f"    仓位比例: {shares * signal['buy_price'] / executor.portfolio.initial_capital * 100:.1f}%")
    
    print("\n" + "="*70)
    print("✅ 优化参数应用验证完成")
    print("="*70)


if __name__ == '__main__':
    verify_optimized_parameters()
