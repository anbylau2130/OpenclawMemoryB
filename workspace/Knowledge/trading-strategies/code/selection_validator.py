#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选股准确率验证系统
功能：验证V5选股系统的历史准确率，计算胜率、盈亏比等关键指标
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

class SelectionValidator:
    """选股验证器"""
    
    def __init__(self):
        """初始化"""
        self.selections_dir = Path(__file__).parent.parent.parent / 'projects' / 'stock-tracking' / 'selections'
        self.reports_dir = Path(__file__).parent.parent.parent / 'data' / 'validation_reports'
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def load_historical_selections(self, days: int = 30) -> List[Dict]:
        """
        加载历史选股记录
        
        Args:
            days: 加载最近N天的记录
            
        Returns:
            选股记录列表
        """
        selections = []
        
        # 查找最近N天的选股文件
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # 查找该日期的选股文件（优先V5）
            patterns = [
                f'selection_{date_str}_v5_real.json',
                f'selection_{date_str}_v5_integrated.json',
                f'selection_{date_str}_v5_demo.json',
                f'selection_{date_str}_v4.json',
                f'selection_{date_str}_v3.json'
            ]
            
            for pattern in patterns:
                file_path = self.selections_dir / pattern
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        data['date'] = date_str
                        selections.append(data)
                    break
            
            current_date += timedelta(days=1)
        
        return selections
    
    def simulate_price_movement(self, buy_price: float, days: int = 5) -> Tuple[float, float]:
        """
        模拟价格走势（用于演示，实际应使用真实数据）
        
        Args:
            buy_price: 买入价
            days: 持有天数
            
        Returns:
            (最高价, 收盘价)
        """
        # 模拟价格波动（-10% 到 +15%）
        np.random.seed(hash(str(buy_price) + str(days)) % 2**32)
        change_pct = np.random.uniform(-0.10, 0.15)
        final_price = buy_price * (1 + change_pct)
        
        # 模拟最高价（比收盘价高0-5%）
        high_change = np.random.uniform(0, 0.05)
        high_price = final_price * (1 + high_change)
        
        return high_price, final_price
    
    def validate_selection(self, selection: Dict) -> Dict:
        """
        验证单次选股结果
        
        Args:
            selection: 选股记录
            
        Returns:
            验证结果
        """
        date = selection.get('date', 'unknown')
        stocks = selection.get('stocks', [])
        version = selection.get('version', 'unknown')
        
        results = {
            'date': date,
            'version': version,
            'total_selected': len(stocks),
            'trades': [],
            'summary': {
                'total_trades': 0,
                'win_trades': 0,
                'loss_trades': 0,
                'total_pnl': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0
            }
        }
        
        for stock in stocks:
            symbol = stock.get('symbol')
            name = stock.get('name')
            buy_price = stock.get('buy_price', 0)
            
            if buy_price <= 0:
                continue
            
            # 模拟5日后的价格（实际应使用真实历史数据）
            high_price, final_price = self.simulate_price_movement(buy_price, days=5)
            
            # 计算盈亏
            pnl_pct = (final_price - buy_price) / buy_price * 100
            pnl_amount = (final_price - buy_price) * 100  # 假设每只买100股
            
            # 检查是否触发止损止盈
            stop_loss = buy_price * 0.97  # -3%
            take_profit_1 = buy_price * 1.06  # +6%
            take_profit_2 = buy_price * 1.10  # +10%
            
            triggered = None
            exit_price = final_price
            
            # 检查止损
            if high_price >= stop_loss and final_price <= stop_loss:
                triggered = 'STOP_LOSS'
                exit_price = stop_loss
                pnl_pct = -3.0
                pnl_amount = -3.0 * 100 / 100 * 100  # -3% * 100股
            
            # 检查第一档止盈
            elif high_price >= take_profit_1:
                triggered = 'TAKE_PROFIT_1'
                exit_price = take_profit_1
                pnl_pct = 6.0
                pnl_amount = 6.0 * 100 / 100 * 100
            
            # 检查第二档止盈
            elif high_price >= take_profit_2:
                triggered = 'TAKE_PROFIT_2'
                exit_price = take_profit_2
                pnl_pct = 10.0
                pnl_amount = 10.0 * 100 / 100 * 100
            
            trade = {
                'symbol': symbol,
                'name': name,
                'buy_price': buy_price,
                'final_price': round(final_price, 2),
                'high_price': round(high_price, 2),
                'exit_price': round(exit_price, 2),
                'pnl_pct': round(pnl_pct, 2),
                'pnl_amount': round(pnl_amount, 2),
                'triggered': triggered,
                'is_win': pnl_pct > 0
            }
            
            results['trades'].append(trade)
            results['summary']['total_trades'] += 1
            
            if pnl_pct > 0:
                results['summary']['win_trades'] += 1
                results['summary']['total_pnl'] += pnl_amount
            else:
                results['summary']['loss_trades'] += 1
                results['summary']['total_pnl'] += pnl_amount
        
        # 计算汇总指标
        if results['summary']['total_trades'] > 0:
            results['summary']['win_rate'] = results['summary']['win_trades'] / results['summary']['total_trades'] * 100
            
            wins = [t['pnl_amount'] for t in results['trades'] if t['is_win']]
            losses = [t['pnl_amount'] for t in results['trades'] if not t['is_win']]
            
            if wins:
                results['summary']['avg_win'] = np.mean(wins)
            if losses:
                results['summary']['avg_loss'] = np.mean(losses)
            
            if losses and np.mean(losses) != 0:
                results['summary']['profit_factor'] = abs(np.mean(wins) / np.mean(losses)) if wins else 0
        
        return results
    
    def validate_all_selections(self, days: int = 30) -> Dict:
        """
        验证所有历史选股
        
        Args:
            days: 验证最近N天
            
        Returns:
            汇总结果
        """
        selections = self.load_historical_selections(days)
        
        if not selections:
            return {
                'error': '未找到历史选股记录',
                'suggestion': '请先运行选股系统'
            }
        
        all_results = []
        total_stats = {
            'total_selections': len(selections),
            'total_trades': 0,
            'total_win': 0,
            'total_loss': 0,
            'total_pnl': 0,
            'by_version': {}
        }
        
        for selection in selections:
            result = self.validate_selection(selection)
            all_results.append(result)
            
            # 汇总统计
            total_stats['total_trades'] += result['summary']['total_trades']
            total_stats['total_win'] += result['summary']['win_trades']
            total_stats['total_loss'] += result['summary']['loss_trades']
            total_stats['total_pnl'] += result['summary']['total_pnl']
            
            # 按版本统计
            version = result['version']
            if version not in total_stats['by_version']:
                total_stats['by_version'][version] = {
                    'selections': 0,
                    'trades': 0,
                    'wins': 0,
                    'pnl': 0
                }
            
            total_stats['by_version'][version]['selections'] += 1
            total_stats['by_version'][version]['trades'] += result['summary']['total_trades']
            total_stats['by_version'][version]['wins'] += result['summary']['win_trades']
            total_stats['by_version'][version]['pnl'] += result['summary']['total_pnl']
        
        # 计算总体胜率
        if total_stats['total_trades'] > 0:
            total_stats['overall_win_rate'] = total_stats['total_win'] / total_stats['total_trades'] * 100
        else:
            total_stats['overall_win_rate'] = 0
        
        # 生成报告
        report = {
            'validation_date': datetime.now().isoformat(),
            'validation_period': f'最近{days}天',
            'total_stats': total_stats,
            'daily_results': all_results
        }
        
        # 保存报告
        report_file = self.reports_dir / f"validation_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 验证报告已保存: {report_file}")
        
        return report


def main():
    """主函数"""
    print("="*70)
    print("V5选股系统准确率验证")
    print("="*70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 创建验证器
    validator = SelectionValidator()
    
    # 验证最近30天的选股
    print("【第一步：加载历史选股记录】")
    print("-"*70)
    
    selections = validator.load_historical_selections(days=30)
    
    if not selections:
        print("❌ 未找到历史选股记录")
        print("\n建议：")
        print("  1. 先运行选股系统：python3 stock_selector_v5_real.py")
        print("  2. 等待几个交易日积累数据")
        print("  3. 重新运行验证")
        return
    
    print(f"找到 {len(selections)} 个选股记录")
    
    for i, sel in enumerate(selections, 1):
        date = sel.get('date', 'unknown')
        version = sel.get('version', 'unknown')
        count = sel.get('selected_count', sel.get('total_analyzed', 0))
        print(f"{i}. {date} - {version} - {count}支股票")
    
    # 执行验证
    print("\n【第二步：验证选股准确率】")
    print("-"*70)
    
    report = validator.validate_all_selections(days=30)
    
    # 显示汇总结果
    print("\n【第三步：验证结果汇总】")
    print("="*70)
    
    stats = report['total_stats']
    
    print(f"\n总体统计（{stats['total_selections']}次选股）：")
    print(f"  总交易次数: {stats['total_trades']}")
    print(f"  盈利次数: {stats['total_win']}")
    print(f"  亏损次数: {stats['total_loss']}")
    print(f"  总体胜率: {stats['overall_win_rate']:.1f}%")
    print(f"  总盈亏: ¥{stats['total_pnl']:,.2f}")
    
    # 按版本显示
    if stats['by_version']:
        print(f"\n按版本统计：")
        for version, v_stats in stats['by_version'].items():
            v_win_rate = v_stats['wins'] / v_stats['trades'] * 100 if v_stats['trades'] > 0 else 0
            print(f"\n  {version}:")
            print(f"    选股次数: {v_stats['selections']}")
            print(f"    交易次数: {v_stats['trades']}")
            print(f"    胜率: {v_win_rate:.1f}%")
            print(f"    盈亏: ¥{v_stats['pnl']:,.2f}")
    
    # 优化建议
    print("\n【第四步：优化建议】")
    print("="*70)
    
    win_rate = stats['overall_win_rate']
    
    if win_rate >= 70:
        print("✅ 胜率优秀（≥70%）")
        print("  建议：保持当前策略，可适当增加仓位")
    elif win_rate >= 60:
        print("🟡 胜率良好（60-70%）")
        print("  建议：保持当前策略，观察更多数据")
    elif win_rate >= 50:
        print("🟠 胜率一般（50-60%）")
        print("  建议：优化因子权重，提高选股标准")
    else:
        print("🔴 胜率较低（<50%）")
        print("  建议：")
        print("  1. 提高选股阈值（min_score从3.0提升到3.5）")
        print("  2. 移除低效因子")
        print("  3. 增加风控措施")
    
    # 风险提示
    print("\n【风险提示】")
    print("-"*70)
    print("⚠️ 以上验证使用模拟数据，仅供参考")
    print("⚠️ 实盘前建议使用真实历史数据验证")
    print("⚠️ 小资金测试至少2周后再加大投入")


if __name__ == '__main__':
    main()
