#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V5选股系统 + 信号模块整合版
整合真实数据源 + 信号过滤 + 交易决策
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# 添加代码路径
sys.path.insert(0, str(Path(__file__).parent))

from data_fetcher import RobustDataFetcher
from factor_calculator import calculate_all_factors
from signal_filter import SignalModule

class StockSelectorV5Integrated:
    """V5选股系统整合版"""
    
    def __init__(self):
        """初始化"""
        self.data_fetcher = RobustDataFetcher()
        self.signal_module = SignalModule(min_score=3.0, combine_method='ic_weighted')
        
        # 输出目录
        self.output_dir = Path(__file__).parent.parent.parent / 'projects' / 'stock-tracking' / 'selections'
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_stock(self, symbol: str, name: str) -> dict:
        """
        分析单只股票
        
        Args:
            symbol: 股票代码
            name: 股票名称
            
        Returns:
            分析结果
        """
        print(f"分析 {symbol} {name}...")
        
        # 1. 获取真实数据
        df = self.data_fetcher.get_realtime_data(symbol)
        
        if df is None or len(df) == 0:
            print(f"  ❌ 数据获取失败")
            return None
        
        # 2. 计算因子（使用函数）
        factors = calculate_all_factors(df)
        
        if not factors:
            print(f"  ❌ 因子计算失败")
            return None
        
        # 3. 生成原始信号
        total_score = factors.get('total_score', 0)
        active_factors = factors.get('active_factors', [])
        
        signal = {
            'symbol': symbol,
            'name': name,
            'total_score': total_score,
            'factors': active_factors,
            'buy_price': df['close'].iloc[-1] if 'close' in df.columns else 0,
            'data_source': factors.get('data_source', 'unknown'),
            'timestamp': datetime.now().isoformat()
        }
        
        return signal
    
    def select_stocks(self, stock_list: list) -> dict:
        """
        批量选股
        
        Args:
            stock_list: 股票列表 [{'symbol': '600031', 'name': '三一重工'}, ...]
            
        Returns:
            选股结果
        """
        print("="*60)
        print(f"V5选股系统 + 信号模块")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 1. 分析所有股票
        raw_signals = []
        for stock in stock_list:
            signal = self.analyze_stock(stock['symbol'], stock['name'])
            if signal:
                raw_signals.append(signal)
        
        print(f"\n📊 原始信号数量: {len(raw_signals)}")
        
        # 2. 信号处理（过滤 + 组合 + 验证）
        processed = self.signal_module.process_signals(raw_signals)
        
        print(f"✅ 过滤后信号: {processed['filtered_count']}")
        print(f"✅ 有效信号: {processed['valid_count']}")
        
        # 3. 为每个有效信号生成交易决策
        final_selections = []
        for signal in processed['signals']:
            decision = self.signal_module.generate_trading_decision(
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
            
            # 计算止盈止损
            buy_price = signal.get('buy_price', 0)
            if buy_price > 0:
                selection['stop_loss'] = round(buy_price * 0.97, 2)  # -3%
                selection['take_profit_1'] = round(buy_price * 1.06, 2)  # +6%
                selection['take_profit_2'] = round(buy_price * 1.10, 2)  # +10%
            
            final_selections.append(selection)
        
        # 4. 保存结果
        result = {
            'version': 'V5_Integrated',
            'timestamp': datetime.now().isoformat(),
            'data_source': 'real',
            'signal_module': {
                'method': 'ic_weighted',
                'min_score': 3.0
            },
            'total_analyzed': len(stock_list),
            'raw_signals': len(raw_signals),
            'filtered_signals': processed['filtered_count'],
            'valid_signals': processed['valid_count'],
            'selected_count': len(final_selections),
            'stocks': final_selections
        }
        
        # 保存JSON
        timestamp = datetime.now().strftime('%Y-%m-%d')
        output_file = self.output_dir / f'selection_{timestamp}_v5_integrated.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        print(f"\n💾 结果已保存: {output_file}")
        
        return result


def main():
    """主函数"""
    # 上证50成分股（前30支测试）
    stock_list = [
        {'symbol': '600031', 'name': '三一重工'},
        {'symbol': '600036', 'name': '招商银行'},
        {'symbol': '600519', 'name': '贵州茅台'},
        {'symbol': '600887', 'name': '伊利股份'},
        {'symbol': '601318', 'name': '中国平安'},
        # ... 可以添加更多
    ]
    
    # 创建选股器
    selector = StockSelectorV5Integrated()
    
    # 执行选股
    result = selector.select_stocks(stock_list)
    
    # 打印结果摘要
    print("\n" + "="*60)
    print("📊 选股结果摘要")
    print("="*60)
    print(f"分析股票: {result['total_analyzed']}")
    print(f"原始信号: {result['raw_signals']}")
    print(f"过滤后: {result['filtered_signals']}")
    print(f"有效信号: {result['valid_signals']}")
    print(f"最终入选: {result['selected_count']}")
    
    if result['selected_count'] > 0:
        print("\n✅ 入选股票:")
        for stock in result['stocks']:
            print(f"\n  {stock['symbol']} {stock['name']}")
            print(f"    操作: {stock['action']}")
            print(f"    得分: {stock['total_score']:.2f}")
            print(f"    信心度: {stock['confidence']:.1%}")
            print(f"    因子: {', '.join(stock['factors'])}")
            print(f"    买入价: ¥{stock['buy_price']:.2f}")
            print(f"    止损: ¥{stock['stop_loss']:.2f} (-3%)")
            print(f"    止盈1: ¥{stock['take_profit_1']:.2f} (+6%)")
            print(f"    止盈2: ¥{stock['take_profit_2']:.2f} (+10%)")
    else:
        print("\n⚠️ 无股票入选")
        print("可能原因：")
        print("  - 市场上涨，无超卖机会")
        print("  - 信号得分低于阈值（3.0）")
        print("  - 因子质量不达标")


if __name__ == '__main__':
    main()
