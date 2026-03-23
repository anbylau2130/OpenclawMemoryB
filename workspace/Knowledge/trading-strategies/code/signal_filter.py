#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信号过滤与组合模块 - Signal Module
功能：过滤低质量信号，组合多因子信号，生成最终交易决策
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class SignalFilter:
    """信号过滤器"""
    
    def __init__(self, min_score: float = 4.0, min_win_rate: float = 60.0):
        """
        初始化信号过滤器
        
        Args:
            min_score: 最低得分要求
            min_win_rate: 最低胜率要求（%）
        """
        self.min_score = min_score
        self.min_win_rate = min_win_rate
        
        # 高胜率因子配置（基于上证50回测 + 2026-03-17优化）
        self.factor_weights = {
            'VWAP': 3.0,      # 胜率92%，IC=0.15
            'BOLL': 3.0,      # 胜率71%，IC=0.12（↑1.0 优化）
            'KDJ': 3.0,       # 胜率70%，IC=0.10（↑1.5 优化）
            'RSI': 2.0,       # 胜率69%，IC=0.09（↑0.5 优化）
            'MACD': 1.0,      # 胜率36.6%，IC=0.02（↑0.5 优化）
            'MA': 1.0,        # 胜率36.3%，IC=0.01（↑0.5 优化）
            'VOLUME': 1.0,    # 胜率未知
        }
        
        # 低效因子（权重<1）
        self.low_efficiency_factors = ['MACD', 'MA']
    
    def filter_by_score(self, signals: List[Dict]) -> List[Dict]:
        """
        按得分过滤信号
        
        Args:
            signals: 信号列表
            
        Returns:
            过滤后的信号列表
        """
        filtered = []
        
        for signal in signals:
            if signal.get('total_score', 0) >= self.min_score:
                filtered.append(signal)
        
        return filtered
    
    def filter_by_factor_quality(self, signals: List[Dict]) -> List[Dict]:
        """
        过滤低效因子
        
        Args:
            signals: 信号列表
            
        Returns:
            过滤后的信号列表
        """
        filtered = []
        
        for signal in signals:
            # 检查是否包含高效因子
            high_eff_factors = [
                f for f in signal.get('factors', [])
                if f not in self.low_efficiency_factors
            ]
            
            # 至少包含1个高效因子
            if len(high_eff_factors) >= 1:
                filtered.append(signal)
        
        return filtered
    
    def remove_low_quality_signals(self, signals: List[Dict]) -> List[Dict]:
        """
        移除低质量信号（综合过滤）
        
        Args:
            signals: 信号列表
            
        Returns:
            高质量信号列表
        """
        # 1. 按得分过滤
        filtered = self.filter_by_score(signals)
        
        # 2. 按因子质量过滤
        filtered = self.filter_by_factor_quality(filtered)
        
        # 3. 移除冲突信号（同时出现买入和卖出）
        final = []
        for signal in filtered:
            buy_signals = [f for f in signal.get('factors', []) if 'BUY' in f.upper()]
            sell_signals = [f for f in signal.get('factors', []) if 'SELL' in f.upper()]
            
            # 只保留单一方向信号
            if len(buy_signals) > 0 and len(sell_signals) == 0:
                signal['direction'] = 'BUY'
                final.append(signal)
            elif len(sell_signals) > 0 and len(buy_signals) == 0:
                signal['direction'] = 'SELL'
                final.append(signal)
        
        return final


class SignalCombiner:
    """信号组合器"""
    
    def __init__(self, method: str = 'ic_weighted'):
        """
        初始化信号组合器
        
        Args:
            method: 组合方法（'equal'等权, 'ic_weighted'IC加权, 'score_weighted'得分加权）
        """
        self.method = method
        
        # 因子IC值（基于上证50回测）
        self.factor_ic = {
            'VWAP': 0.15,     # IC=0.15
            'BOLL': 0.12,     # IC=0.12
            'KDJ': 0.10,      # IC=0.10
            'RSI': 0.09,      # IC=0.09
            'MACD': 0.02,     # IC=0.02（低效）
            'MA': 0.01,       # IC=0.01（低效）
        }
    
    def equal_weight(self, signals: List[Dict]) -> Dict:
        """
        等权组合
        
        Args:
            signals: 信号列表
            
        Returns:
            组合后的信号
        """
        if not signals:
            return None
        
        # 计算平均得分
        avg_score = np.mean([s.get('total_score', 0) for s in signals])
        
        # 合并因子
        all_factors = []
        for signal in signals:
            all_factors.extend(signal.get('factors', []))
        
        # 去重
        unique_factors = list(set(all_factors))
        
        return {
            'method': 'equal_weight',
            'combined_score': avg_score,
            'factors': unique_factors,
            'signal_count': len(signals),
            'direction': 'BUY' if avg_score >= 3.0 else 'HOLD'
        }
    
    def ic_weighted(self, signals: List[Dict]) -> Dict:
        """
        IC加权组合
        
        Args:
            signals: 信号列表
            
        Returns:
            组合后的信号
        """
        if not signals:
            return None
        
        # 计算加权得分
        weighted_scores = []
        total_weight = 0
        
        for signal in signals:
            for factor in signal.get('factors', []):
                # 提取因子名称（去掉BUY/SELL后缀）
                factor_name = factor.split('_')[0] if '_' in factor else factor
                ic = self.factor_ic.get(factor_name, 0.01)
                
                weighted_scores.append(signal.get('total_score', 0) * ic)
                total_weight += ic
        
        if total_weight == 0:
            return self.equal_weight(signals)
        
        combined_score = sum(weighted_scores) / total_weight
        
        # 合并因子
        all_factors = []
        for signal in signals:
            all_factors.extend(signal.get('factors', []))
        
        unique_factors = list(set(all_factors))
        
        return {
            'method': 'ic_weighted',
            'combined_score': combined_score,
            'factors': unique_factors,
            'signal_count': len(signals),
            'direction': 'BUY' if combined_score >= 3.0 else 'HOLD'
        }
    
    def combine(self, signals: List[Dict]) -> Dict:
        """
        组合信号
        
        Args:
            signals: 信号列表
            
        Returns:
            组合后的信号
        """
        if self.method == 'equal':
            return self.equal_weight(signals)
        elif self.method == 'ic_weighted':
            return self.ic_weighted(signals)
        else:
            return self.equal_weight(signals)


class SignalValidator:
    """信号验证器"""
    
    def __init__(self):
        """初始化信号验证器"""
        pass
    
    def validate_signal(self, signal: Dict) -> Tuple[bool, str]:
        """
        验证信号有效性
        
        Args:
            signal: 信号字典
            
        Returns:
            (是否有效, 原因)
        """
        # 检查必要字段
        required_fields = ['symbol', 'total_score', 'factors']
        for field in required_fields:
            if field not in signal:
                return False, f"缺少必要字段: {field}"
        
        # 检查得分范围
        score = signal.get('total_score', 0)
        if score < 0 or score > 10:
            return False, f"得分超出范围: {score}"
        
        # 检查因子数量
        factors = signal.get('factors', [])
        if len(factors) == 0:
            return False, "没有有效因子"
        
        # 检查价格
        if 'buy_price' in signal:
            if signal['buy_price'] <= 0:
                return False, f"无效买入价: {signal['buy_price']}"
        
        return True, "有效信号"
    
    def validate_signals(self, signals: List[Dict]) -> List[Dict]:
        """
        批量验证信号
        
        Args:
            signals: 信号列表
            
        Returns:
            有效信号列表
        """
        valid_signals = []
        
        for signal in signals:
            is_valid, reason = self.validate_signal(signal)
            if is_valid:
                signal['validated'] = True
                signal['validation_time'] = datetime.now().isoformat()
                valid_signals.append(signal)
            else:
                print(f"⚠️ 无效信号: {signal.get('symbol', 'Unknown')} - {reason}")
        
        return valid_signals


class SignalModule:
    """信号模块主类"""
    
    def __init__(self, 
                 min_score: float = 3.0,
                 combine_method: str = 'ic_weighted'):
        """
        初始化信号模块
        
        Args:
            min_score: 最低得分要求
            combine_method: 组合方法
        """
        self.filter = SignalFilter(min_score=min_score)
        self.combiner = SignalCombiner(method=combine_method)
        self.validator = SignalValidator()
    
    def process_signals(self, 
                       raw_signals: List[Dict],
                       filter_enabled: bool = True,
                       combine_enabled: bool = True) -> Dict:
        """
        处理信号（过滤 + 组合 + 验证）
        
        Args:
            raw_signals: 原始信号列表
            filter_enabled: 是否启用过滤
            combine_enabled: 是否启用组合
            
        Returns:
            处理结果
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'raw_count': len(raw_signals),
            'filtered_count': 0,
            'valid_count': 0,
            'signals': [],
            'combined_signal': None
        }
        
        # 1. 过滤
        if filter_enabled:
            filtered = self.filter.remove_low_quality_signals(raw_signals)
        else:
            filtered = raw_signals
        
        result['filtered_count'] = len(filtered)
        
        # 2. 验证
        validated = self.validator.validate_signals(filtered)
        result['valid_count'] = len(validated)
        result['signals'] = validated
        
        # 3. 组合
        if combine_enabled and len(validated) > 0:
            combined = self.combiner.combine(validated)
            result['combined_signal'] = combined
        
        return result
    
    def generate_trading_decision(self, 
                                 signals: List[Dict],
                                 market_condition: str = 'normal') -> Dict:
        """
        生成交易决策
        
        Args:
            signals: 信号列表
            market_condition: 市场环境（'normal', 'bull', 'bear'）
            
        Returns:
            交易决策
        """
        # 处理信号
        result = self.process_signals(signals)
        
        # 生成决策
        decision = {
            'timestamp': datetime.now().isoformat(),
            'action': 'HOLD',
            'confidence': 0.0,
            'reasons': [],
            'signals': result['signals'],
            'market_condition': market_condition
        }
        
        valid_signals = result['signals']
        
        if len(valid_signals) == 0:
            decision['action'] = 'HOLD'
            decision['reasons'].append('无有效信号')
            return decision
        
        # 计算综合得分
        combined = result.get('combined_signal')
        if combined:
            score = combined.get('combined_score', 0)
            factors = combined.get('factors', [])
            
            # 根据得分和市场环境决策
            if market_condition == 'normal':
                if score >= 4.0:
                    decision['action'] = 'STRONG_BUY'
                    decision['confidence'] = 0.8
                elif score >= 3.0:
                    decision['action'] = 'BUY'
                    decision['confidence'] = 0.6
                elif score <= 1.0:
                    decision['action'] = 'SELL'
                    decision['confidence'] = 0.6
            elif market_condition == 'bull':
                # 牛市：降低买入门槛
                if score >= 3.0:
                    decision['action'] = 'BUY'
                    decision['confidence'] = 0.7
            elif market_condition == 'bear':
                # 熊市：提高买入门槛
                if score >= 5.0:
                    decision['action'] = 'BUY'
                    decision['confidence'] = 0.5
                elif score <= 2.0:
                    decision['action'] = 'SELL'
                    decision['confidence'] = 0.7
            
            decision['reasons'].append(f"综合得分: {score:.2f}")
            decision['reasons'].append(f"有效因子: {', '.join(factors)}")
            decision['reasons'].append(f"信号数量: {len(valid_signals)}")
        
        return decision


# 使用示例
if __name__ == '__main__':
    # 创建信号模块
    signal_module = SignalModule(min_score=3.0, combine_method='ic_weighted')
    
    # 测试信号
    test_signals = [
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
            'total_score': 2.5,  # 低于阈值，会被过滤
            'factors': ['MACD_BUY'],
            'buy_price': 39.91
        }
    ]
    
    # 处理信号
    result = signal_module.process_signals(test_signals)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n" + "="*50)
    
    # 生成交易决策
    decision = signal_module.generate_trading_decision(test_signals, market_condition='normal')
    print(json.dumps(decision, indent=2, ensure_ascii=False))
