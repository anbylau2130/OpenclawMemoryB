#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V5选股系统 - 信号模块整合演示
演示如何将信号模块集成到选股流程中
"""

import json
from datetime import datetime
from pathlib import Path

# 导入信号模块
from signal_filter import SignalModule

def main():
    """主函数 - 演示信号模块功能"""
    
    print("="*60)
    print("V5选股系统 - 信号模块整合演示")
    print("="*60)
    
    # 模拟V5选股系统的原始信号（实际应该从data_fetcher获取）
    # 这里使用测试数据演示信号过滤和组合
    raw_signals = [
        {
            'symbol': '600031',
            'name': '三一重工',
            'total_score': 4.5,
            'factors': ['VWAP_BUY', 'BOLL_BUY', 'RSI_OVERSOLD'],
            'buy_price': 20.85
        },
        {
            'symbol': '600036',
            'name': '招商银行',
            'total_score': 3.2,
            'factors': ['VWAP_BUY', 'KDJ_OVERSOLD'],
            'buy_price': 39.91
        },
        {
            'symbol': '601318',
            'name': '中国平安',
            'total_score': 2.8,  # 低于阈值，会被过滤
            'factors': ['MACD_BUY'],  # 低效因子
            'buy_price': 60.48
        },
        {
            'symbol': '600519',
            'name': '贵州茅台',
            'total_score': 5.0,
            'factors': ['VWAP_BUY', 'BOLL_BUY', 'KDJ_OVERSOLD', 'RSI_OVERSOLD'],
            'buy_price': 1680.00
        }
    ]
    
    print(f"\n📊 原始信号数量: {len(raw_signals)}")
    print("\n原始信号:")
    for i, sig in enumerate(raw_signals, 1):
        print(f"{i}. {sig['symbol']} {sig['name']}")
        print(f"   得分: {sig['total_score']:.1f}, 因子: {', '.join(sig['factors'])}")
    
    # 创建信号模块
    signal_module = SignalModule(min_score=3.0, combine_method='ic_weighted')
    
    # 处理信号
    print("\n" + "="*60)
    print("处理信号...")
    print("="*60)
    
    result = signal_module.process_signals(raw_signals)
    
    print(f"\n✅ 过滤后信号: {result['filtered_count']}")
    print(f"✅ 有效信号: {result['valid_count']}")
    
    # 显示有效信号
    if result['signals']:
        print("\n有效信号:")
        for i, sig in enumerate(result['signals'], 1):
            print(f"{i}. {sig['symbol']} {sig['name']}")
            print(f"   得分: {sig['total_score']:.1f}")
            print(f"   因子: {', '.join(sig['factors'])}")
            print(f"   方向: {sig['direction']}")
    
    # 组合信号
    if result.get('combined_signal'):
        combined = result['combined_signal']
        print(f"\n📊 组合信号:")
        print(f"   方法: {combined['method']}")
        print(f"   综合得分: {combined['combined_score']:.2f}")
        print(f"   方向: {combined['direction']}")
        print(f"   因子: {', '.join(combined['factors'])}")
    
    # 为每个有效信号生成交易决策
    print("\n" + "="*60)
    print("交易决策")
    print("="*60)
    
    final_selections = []
    
    for signal in result['signals']:
        decision = signal_module.generate_trading_decision(
            [signal], 
            market_condition='normal'
        )
        
        # 合并信号和决策
        selection = {
            **signal,
            'action': decision['action'],
            'confidence': decision['confidence'],
            'reasons': decision['reasons']
        }
        
        # 计算止盈止损（V5规则：盈亏比3.3）
        buy_price = signal.get('buy_price', 0)
        if buy_price > 0:
            selection['stop_loss'] = round(buy_price * 0.97, 2)  # -3%
            selection['take_profit_1'] = round(buy_price * 1.06, 2)  # +6%
            selection['take_profit_2'] = round(buy_price * 1.10, 2)  # +10%
            selection['risk_reward_ratio'] = 3.3  # 盈亏比
        
        final_selections.append(selection)
        
        print(f"\n{selection['symbol']} {selection['name']}")
        print(f"  操作: {selection['action']}")
        print(f"  信心度: {selection['confidence']:.1%}")
        print(f"  买入价: ¥{selection['buy_price']:.2f}")
        print(f"  止损: ¥{selection['stop_loss']:.2f} (-3%)")
        print(f"  止盈1: ¥{selection['take_profit_1']:.2f} (+6%)")
        print(f"  止盈2: ¥{selection['take_profit_2']:.2f} (+10%)")
        print(f"  盈亏比: {selection['risk_reward_ratio']}")
        print(f"  原因: {'; '.join(selection['reasons'])}")
    
    # 保存结果
    output = {
        'version': 'V5_Integrated_Demo',
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'raw_signals': len(raw_signals),
            'filtered_signals': result['filtered_count'],
            'valid_signals': result['valid_count'],
            'final_selections': len(final_selections)
        },
        'signal_processing': {
            'method': 'ic_weighted',
            'min_score': 3.0,
            'high_efficiency_factors': ['VWAP', 'BOLL', 'KDJ', 'RSI'],
            'low_efficiency_factors': ['MACD', 'MA']
        },
        'trading_rules': {
            'stop_loss': '-3%',
            'take_profit_1': '+6% (卖30%)',
            'take_profit_2': '+10% (卖40%)',
            'risk_reward_ratio': 3.3
        },
        'selections': final_selections
    }
    
    output_file = Path(__file__).parent.parent.parent / 'projects' / 'stock-tracking' / 'selections' / f'selection_{datetime.now().strftime("%Y-%m-%d")}_v5_demo.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 结果已保存: {output_file}")
    
    print("\n" + "="*60)
    print("✅ 信号模块整合完成")
    print("="*60)
    print("\n模块功能:")
    print("  1. ✅ 信号过滤（按得分、因子质量）")
    print("  2. ✅ 信号组合（IC加权）")
    print("  3. ✅ 信号验证（有效性检查）")
    print("  4. ✅ 交易决策（根据市场环境）")
    print("  5. ✅ 风控计算（止盈止损）")


if __name__ == '__main__':
    main()
