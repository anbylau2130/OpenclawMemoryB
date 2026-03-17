#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V5快速信号生成器 - Fast Signal Generator
功能：毫秒级信号生成、批量处理、缓存优化
"""

import json
import time
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from functools import lru_cache
import hashlib


class FastSignalGenerator:
    """快速信号生成器"""
    
    def __init__(self):
        """初始化"""
        # 优化后的因子权重
        self.factor_weights = {
            'VWAP': 3.0,
            'BOLL': 3.0,
            'KDJ': 3.0,
            'RSI': 2.0,
            'MACD': 1.0,
            'MA': 1.0
        }
        
        # 高胜率因子（快速判断用）
        self.high_win_factors = ['VWAP', 'BOLL', 'KDJ', 'RSI']
        
        # 缓存
        self.cache = {}
        self.cache_timeout = 60  # 缓存60秒
    
    def _get_cache_key(self, symbol: str, data_hash: str) -> str:
        """生成缓存键"""
        return f"{symbol}_{data_hash}"
    
    def _hash_data(self, close_prices: np.ndarray) -> str:
        """生成数据哈希"""
        return hashlib.md5(close_prices.tobytes()).hexdigest()[:8]
    
    def calculate_vwap_fast(self, df: pd.DataFrame) -> Tuple[float, str]:
        """
        快速计算VWAP信号
        
        Args:
            df: 价格数据
            
        Returns:
            (信号得分, 信号类型)
        """
        try:
            close = df['close'].iloc[-1]
            volume = df['volume'].iloc[-1] if 'volume' in df.columns else 1
            
            # 简化计算：使用最近5日均价
            avg_price = df['close'].iloc[-5:].mean()
            
            # VWAP判断
            if close < avg_price * 0.98:  # 低于VWAP 2%
                return 3.0, 'VWAP_BUY'
            elif close > avg_price * 1.02:  # 高于VWAP 2%
                return -1.0, 'VWAP_SELL'
            else:
                return 0, 'VWAP_HOLD'
                
        except Exception:
            return 0, 'VWAP_HOLD'
    
    def calculate_boll_fast(self, df: pd.DataFrame) -> Tuple[float, str]:
        """
        快速计算布林带信号
        
        Args:
            df: 价格数据
            
        Returns:
            (信号得分, 信号类型)
        """
        try:
            close = df['close'].iloc[-1]
            
            # 20日均线和标准差
            ma20 = df['close'].iloc[-20:].mean()
            std20 = df['close'].iloc[-20:].std()
            
            upper = ma20 + 2 * std20
            lower = ma20 - 2 * std20
            
            # 布林带判断
            if close <= lower:
                return 3.0, 'BOLL_BUY'
            elif close >= upper:
                return -1.0, 'BOLL_SELL'
            else:
                return 0, 'BOLL_HOLD'
                
        except Exception:
            return 0, 'BOLL_HOLD'
    
    def calculate_rsi_fast(self, df: pd.DataFrame, period: int = 14) -> Tuple[float, str]:
        """
        快速计算RSI信号
        
        Args:
            df: 价格数据
            period: 周期
            
        Returns:
            (信号得分, 信号类型)
        """
        try:
            # 计算价格变化
            delta = df['close'].diff()
            
            # 分离上涨和下跌
            gain = delta.where(delta > 0, 0).rolling(period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
            
            # 计算RS
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = rsi.iloc[-1]
            
            # RSI判断
            if current_rsi <= 30:
                return 2.0, 'RSI_OVERSOLD'
            elif current_rsi >= 70:
                return -1.0, 'RSI_OVERBOUGHT'
            else:
                return 0, 'RSI_HOLD'
                
        except Exception:
            return 0, 'RSI_HOLD'
    
    def calculate_kdj_fast(self, df: pd.DataFrame, period: int = 9) -> Tuple[float, str]:
        """
        快速计算KDJ信号
        
        Args:
            df: 价格数据
            period: 周期
            
        Returns:
            (信号得分, 信号类型)
        """
        try:
            # 计算RSV
            low_min = df['low'].iloc[-period:].min()
            high_max = df['high'].iloc[-period:].max()
            
            close = df['close'].iloc[-1]
            
            rsv = (close - low_min) / (high_max - low_min) * 100
            
            # KDJ判断（简化：只看RSV）
            if rsv <= 20:
                return 3.0, 'KDJ_OVERSOLD'
            elif rsv >= 80:
                return -1.0, 'KDJ_OVERBOUGHT'
            else:
                return 0, 'KDJ_HOLD'
                
        except Exception:
            return 0, 'KDJ_HOLD'
    
    def generate_signal_fast(self, 
                            symbol: str,
                            df: pd.DataFrame,
                            use_cache: bool = True) -> Dict:
        """
        快速生成信号（毫秒级）
        
        Args:
            symbol: 股票代码
            df: 价格数据
            use_cache: 是否使用缓存
            
        Returns:
            信号字典
        """
        start_time = time.time()
        
        # 检查缓存
        if use_cache:
            data_hash = self._hash_data(df['close'].values)
            cache_key = self._get_cache_key(symbol, data_hash)
            
            if cache_key in self.cache:
                cached = self.cache[cache_key]
                if time.time() - cached['timestamp'] < self.cache_timeout:
                    return cached['signal']
        
        # 快速计算各因子
        factors = []
        total_score = 0
        
        # 1. VWAP（权重3.0）
        score, signal_type = self.calculate_vwap_fast(df)
        if score != 0:
            factors.append(signal_type)
            total_score += score * self.factor_weights['VWAP']
        
        # 2. 布林带（权重3.0）
        score, signal_type = self.calculate_boll_fast(df)
        if score != 0:
            factors.append(signal_type)
            total_score += score * self.factor_weights['BOLL']
        
        # 3. RSI（权重2.0）
        score, signal_type = self.calculate_rsi_fast(df)
        if score != 0:
            factors.append(signal_type)
            total_score += score * self.factor_weights['RSI']
        
        # 4. KDJ（权重3.0）
        score, signal_type = self.calculate_kdj_fast(df)
        if score != 0:
            factors.append(signal_type)
            total_score += score * self.factor_weights['KDJ']
        
        # 计算耗时
        elapsed_ms = (time.time() - start_time) * 1000
        
        # 生成信号
        signal = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'total_score': round(total_score, 2),
            'factors': factors,
            'high_win_factor_count': len([f for f in factors if any(h in f for h in self.high_win_factors)]),
            'action': 'BUY' if total_score >= 4.0 else 'SELL' if total_score <= -2.0 else 'HOLD',
            'confidence': min(abs(total_score) / 10.0, 1.0),
            'elapsed_ms': round(elapsed_ms, 2)
        }
        
        # 缓存结果
        if use_cache:
            self.cache[cache_key] = {
                'signal': signal,
                'timestamp': time.time()
            }
        
        return signal
    
    def generate_signals_batch(self,
                              symbols: List[str],
                              data_dict: Dict[str, pd.DataFrame]) -> List[Dict]:
        """
        批量生成信号
        
        Args:
            symbols: 股票代码列表
            data_dict: 数据字典 {symbol: df}
            
        Returns:
            信号列表
        """
        signals = []
        
        start_time = time.time()
        
        for symbol in symbols:
            if symbol in data_dict:
                df = data_dict[symbol]
                signal = self.generate_signal_fast(symbol, df)
                signals.append(signal)
        
        elapsed_ms = (time.time() - start_time) * 1000
        avg_ms = elapsed_ms / len(symbols) if symbols else 0
        
        print(f"批量信号生成: {len(signals)}支股票, 总耗时{elapsed_ms:.0f}ms, 平均{avg_ms:.2f}ms/支")
        
        return signals
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        print("缓存已清空")


def benchmark():
    """性能测试"""
    print("="*70)
    print("V5快速信号生成器 - 性能测试")
    print("="*70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 创建生成器
    generator = FastSignalGenerator()
    
    # 生成测试数据
    np.random.seed(42)
    
    def create_test_data(days: int = 30) -> pd.DataFrame:
        """创建测试数据"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # 生成价格数据
        base_price = 20.0
        returns = np.random.randn(days) * 0.02
        prices = base_price * (1 + returns).cumprod()
        
        df = pd.DataFrame({
            'date': dates,
            'open': prices * (1 + np.random.randn(days) * 0.01),
            'high': prices * (1 + np.abs(np.random.randn(days) * 0.02)),
            'low': prices * (1 - np.abs(np.random.randn(days) * 0.02)),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, days)
        })
        
        return df
    
    # 测试1：单只股票信号生成速度
    print("【测试1：单只股票信号生成】")
    print("-"*70)
    
    df = create_test_data(30)
    
    # 首次生成（无缓存）
    signal = generator.generate_signal_fast('600031', df, use_cache=False)
    print(f"首次生成耗时: {signal['elapsed_ms']:.2f}ms")
    
    # 再次生成（有缓存）
    signal = generator.generate_signal_fast('600031', df, use_cache=True)
    print(f"缓存命中耗时: {signal['elapsed_ms']:.2f}ms")
    
    # 测试2：批量生成
    print("\n【测试2：批量信号生成】")
    print("-"*70)
    
    symbols = [f'6000{i:03d}' for i in range(10)]
    data_dict = {symbol: create_test_data(30) for symbol in symbols}
    
    # 首次批量
    start = time.time()
    signals = generator.generate_signals_batch(symbols, data_dict)
    elapsed = (time.time() - start) * 1000
    
    print(f"\n首次批量生成: {elapsed:.0f}ms")
    print(f"平均每支: {elapsed/len(symbols):.2f}ms")
    
    # 再次批量（有缓存）
    start = time.time()
    signals = generator.generate_signals_batch(symbols, data_dict)
    elapsed = (time.time() - start) * 1000
    
    print(f"\n缓存批量生成: {elapsed:.0f}ms")
    print(f"平均每支: {elapsed/len(symbols):.2f}ms")
    
    # 测试3：高频生成（100次）
    print("\n【测试3：高频信号生成（100次）】")
    print("-"*70)
    
    start = time.time()
    for _ in range(100):
        signal = generator.generate_signal_fast('600031', df, use_cache=True)
    elapsed = (time.time() - start) * 1000
    
    print(f"100次生成总耗时: {elapsed:.0f}ms")
    print(f"平均每次: {elapsed/100:.2f}ms")
    print(f"吞吐量: {100000/elapsed:.0f}次/秒")
    
    # 显示示例信号
    print("\n【示例信号】")
    print("-"*70)
    print(json.dumps(signal, indent=2, ensure_ascii=False))
    
    print("\n" + "="*70)
    print("✅ 性能测试完成")
    print("="*70)


if __name__ == '__main__':
    benchmark()
