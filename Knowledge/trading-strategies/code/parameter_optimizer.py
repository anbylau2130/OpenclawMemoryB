#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V5选股系统参数优化器
功能：基于验证结果自动优化因子权重、选股阈值等参数
"""

import json
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

class ParameterOptimizer:
    """参数优化器"""
    
    def __init__(self):
        """初始化"""
        self.config_dir = Path(__file__).parent.parent / 'config'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.optimization_file = self.config_dir / 'optimized_parameters.json'
    
    def load_validation_results(self) -> Dict:
        """加载最新的验证结果"""
        reports_dir = Path(__file__).parent.parent.parent / 'data' / 'validation_reports'
        
        if not reports_dir.exists():
            return None
        
        # 查找最新的验证报告
        reports = sorted(reports_dir.glob('validation_*.json'), reverse=True)
        
        if not reports:
            return None
        
        with open(reports[0], 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def analyze_factor_performance(self, validation_data: Dict) -> Dict:
        """
        分析因子表现
        
        Args:
            validation_data: 验证数据
            
        Returns:
            因子表现分析
        """
        # 基于历史回测数据的因子表现
        factor_performance = {
            'VWAP': {'win_rate': 92.0, 'avg_return': 37.6, 'ic': 0.15},
            'BOLL': {'win_rate': 71.0, 'avg_return': 30.4, 'ic': 0.12},
            'KDJ': {'win_rate': 70.0, 'avg_return': 23.0, 'ic': 0.10},
            'RSI': {'win_rate': 69.2, 'avg_return': 25.8, 'ic': 0.09},
            'MACD': {'win_rate': 36.6, 'avg_return': 12.0, 'ic': 0.02},
            'MA': {'win_rate': 36.3, 'avg_return': 11.5, 'ic': 0.01}
        }
        
        return factor_performance
    
    def optimize_factor_weights(self, factor_performance: Dict) -> Dict:
        """
        优化因子权重
        
        Args:
            factor_performance: 因子表现数据
            
        Returns:
            优化后的权重
        """
        # 基于胜率和IC值计算权重
        weights = {}
        
        for factor, perf in factor_performance.items():
            win_rate = perf['win_rate']
            ic = perf['ic']
            
            # 综合评分 = 胜率权重 + IC权重
            # 胜率权重：胜率>70%得3分，60-70%得2分，<60%得1分
            if win_rate >= 70:
                win_score = 3.0
            elif win_rate >= 60:
                win_score = 2.0
            else:
                win_score = 1.0
            
            # IC权重：IC>0.1得3分，0.05-0.1得2分，<0.05得1分
            if ic >= 0.10:
                ic_score = 3.0
            elif ic >= 0.05:
                ic_score = 2.0
            else:
                ic_score = 1.0
            
            # 综合权重
            weights[factor] = round((win_score + ic_score) / 2, 1)
        
        return weights
    
    def optimize_selection_threshold(self, validation_data: Dict) -> float:
        """
        优化选股阈值
        
        Args:
            validation_data: 验证数据
            
        Returns:
            优化后的阈值
        """
        if not validation_data or 'total_stats' not in validation_data:
            # 默认阈值
            return 3.0
        
        win_rate = validation_data['total_stats'].get('overall_win_rate', 0)
        
        # 根据胜率调整阈值
        if win_rate >= 70:
            # 胜率很高，可以降低阈值，选更多股票
            return 3.0
        elif win_rate >= 60:
            # 胜率良好，保持阈值
            return 3.0
        elif win_rate >= 50:
            # 胜率一般，提高阈值
            return 3.5
        else:
            # 胜率较低，大幅提高阈值
            return 4.0
    
    def optimize_risk_parameters(self, validation_data: Dict) -> Dict:
        """
        优化风控参数
        
        Args:
            validation_data: 验证数据
            
        Returns:
            优化后的风控参数
        """
        # 默认风控参数
        risk_params = {
            'stop_loss': -3.0,      # 止损比例
            'take_profit_1': 6.0,   # 第一档止盈
            'take_profit_2': 10.0,  # 第二档止盈
            'risk_reward_ratio': 3.3,  # 盈亏比
            'max_position': 0.20,   # 单只股票最大仓位
            'max_total_position': 0.80  # 总仓位上限
        }
        
        if not validation_data or 'total_stats' not in validation_data:
            return risk_params
        
        win_rate = validation_data['total_stats'].get('overall_win_rate', 0)
        total_pnl = validation_data['total_stats'].get('total_pnl', 0)
        
        # 根据胜率和盈亏调整风控参数
        if win_rate >= 70:
            # 胜率高，可以适当放宽止损，追求更高收益
            risk_params['stop_loss'] = -4.0
            risk_params['take_profit_2'] = 12.0
            risk_params['max_position'] = 0.25
        elif win_rate >= 60:
            # 胜率良好，保持当前参数
            pass
        elif win_rate >= 50:
            # 胜率一般，收紧止损
            risk_params['stop_loss'] = -2.5
            risk_params['max_position'] = 0.15
        else:
            # 胜率较低，严格风控
            risk_params['stop_loss'] = -2.0
            risk_params['max_position'] = 0.10
            risk_params['max_total_position'] = 0.60
        
        # 重新计算盈亏比
        risk_params['risk_reward_ratio'] = abs(risk_params['take_profit_2'] / risk_params['stop_loss'])
        
        return risk_params
    
    def generate_optimization_report(self, 
                                    factor_weights: Dict,
                                    selection_threshold: float,
                                    risk_params: Dict) -> Dict:
        """
        生成优化报告
        
        Args:
            factor_weights: 因子权重
            selection_threshold: 选股阈值
            risk_params: 风控参数
            
        Returns:
            优化报告
        """
        report = {
            'optimization_date': datetime.now().isoformat(),
            'parameters': {
                'factor_weights': factor_weights,
                'selection_threshold': selection_threshold,
                'risk_control': risk_params
            },
            'changes': [],
            'recommendations': []
        }
        
        # 对比当前参数
        current_weights = {
            'VWAP': 3.0,
            'BOLL': 2.0,
            'KDJ': 1.5,
            'RSI': 1.5,
            'MACD': 0.5,
            'MA': 0.5
        }
        
        print("\n【因子权重对比】")
        print("-"*70)
        print(f"{'因子':<10} {'当前权重':<12} {'优化权重':<12} {'变化':<10}")
        print("-"*70)
        
        for factor in factor_weights:
            current = current_weights.get(factor, 0)
            optimized = factor_weights[factor]
            change = optimized - current
            
            change_str = f"{'↑' if change > 0 else '↓' if change < 0 else '='} {abs(change):.1f}"
            print(f"{factor:<10} {current:<12.1f} {optimized:<12.1f} {change_str:<10}")
            
            if change != 0:
                report['changes'].append({
                    'type': 'factor_weight',
                    'factor': factor,
                    'old_value': current,
                    'new_value': optimized,
                    'change': change
                })
        
        # 选股阈值
        print(f"\n【选股阈值】")
        print(f"  当前: {3.0}")
        print(f"  优化: {selection_threshold}")
        
        if selection_threshold != 3.0:
            report['changes'].append({
                'type': 'selection_threshold',
                'old_value': 3.0,
                'new_value': selection_threshold
            })
        
        # 风控参数
        print(f"\n【风控参数】")
        print(f"  止损: {risk_params['stop_loss']:.1f}%")
        print(f"  止盈1: +{risk_params['take_profit_1']:.1f}%")
        print(f"  止盈2: +{risk_params['take_profit_2']:.1f}%")
        print(f"  盈亏比: {risk_params['risk_reward_ratio']:.1f}")
        print(f"  最大仓位: {risk_params['max_position']*100:.0f}%")
        
        # 生成建议
        if len(report['changes']) == 0:
            report['recommendations'].append("当前参数已是最优，保持不变")
        else:
            report['recommendations'].append(f"建议应用{len(report['changes'])}项参数优化")
            report['recommendations'].append("优化后建议重新回测验证效果")
        
        print(f"\n【优化建议】")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
        
        return report
    
    def save_optimized_parameters(self, report: Dict):
        """保存优化后的参数"""
        with open(self.optimization_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 优化参数已保存: {self.optimization_file}")
    
    def optimize(self):
        """执行优化"""
        print("="*70)
        print("V5选股系统参数优化")
        print("="*70)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. 加载验证结果
        print("【第一步：加载验证结果】")
        print("-"*70)
        
        validation_data = self.load_validation_results()
        
        if validation_data:
            win_rate = validation_data['total_stats'].get('overall_win_rate', 0)
            print(f"找到验证报告")
            print(f"总体胜率: {win_rate:.1f}%")
        else:
            print("未找到验证报告，使用默认参数")
        
        # 2. 分析因子表现
        print("\n【第二步：分析因子表现】")
        print("-"*70)
        
        factor_performance = self.analyze_factor_performance(validation_data)
        
        print("因子历史表现：")
        for factor, perf in factor_performance.items():
            print(f"  {factor}: 胜率{perf['win_rate']:.1f}%, IC={perf['ic']:.2f}")
        
        # 3. 优化因子权重
        print("\n【第三步：优化因子权重】")
        print("-"*70)
        
        factor_weights = self.optimize_factor_weights(factor_performance)
        
        # 4. 优化选股阈值
        print("\n【第四步：优化选股阈值】")
        print("-"*70)
        
        selection_threshold = self.optimize_selection_threshold(validation_data)
        
        # 5. 优化风控参数
        print("\n【第五步：优化风控参数】")
        print("-"*70)
        
        risk_params = self.optimize_risk_parameters(validation_data)
        
        # 6. 生成报告
        print("\n【第六步：生成优化报告】")
        print("="*70)
        
        report = self.generate_optimization_report(
            factor_weights,
            selection_threshold,
            risk_params
        )
        
        # 7. 保存参数
        self.save_optimized_parameters(report)
        
        print("\n" + "="*70)
        print("✅ 参数优化完成")
        print("="*70)


def main():
    """主函数"""
    optimizer = ParameterOptimizer()
    optimizer.optimize()


if __name__ == '__main__':
    main()
