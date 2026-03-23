#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V5并发数据获取器 - Concurrent Data Fetcher
功能：多线程并发获取、智能缓存、失败重试
"""

import time
import threading
import queue
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import hashlib
import json
from pathlib import Path


class ConcurrentDataFetcher:
    """并发数据获取器"""
    
    def __init__(self, max_workers: int = 10, cache_timeout: int = 60):
        """
        初始化
        
        Args:
            max_workers: 最大并发数
            cache_timeout: 缓存超时（秒）
        """
        self.max_workers = max_workers
        self.cache_timeout = cache_timeout
        
        # 缓存
        self.cache = {}
        self.cache_lock = threading.Lock()
        
        # 导入数据获取器
        from data_fetcher import RobustDataFetcher
        self.fetcher = RobustDataFetcher()
        
        # 统计
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0,
            'avg_latency_ms': 0
        }
        self.stats_lock = threading.Lock()
    
    def _get_cache_key(self, symbol: str, data_type: str = 'realtime') -> str:
        """生成缓存键"""
        minute = datetime.now().strftime('%Y%m%d%H%M')
        return f"{symbol}_{data_type}_{minute}"
    
    def get_realtime_data_single(self, 
                                 symbol: str,
                                 use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        获取单只股票实时数据（带缓存）
        
        Args:
            symbol: 股票代码
            use_cache: 是否使用缓存
            
        Returns:
            DataFrame或None
        """
        start_time = time.time()
        
        # 检查缓存
        if use_cache:
            cache_key = self._get_cache_key(symbol)
            
            with self.cache_lock:
                if cache_key in self.cache:
                    cached_data, cached_time = self.cache[cache_key]
                    
                    if time.time() - cached_time < self.cache_timeout:
                        # 缓存命中
                        with self.stats_lock:
                            self.stats['cache_hits'] += 1
                            self.stats['total_requests'] += 1
                        
                        return cached_data
        
        # 缓存未命中，获取数据
        try:
            df = self.fetcher.get_realtime_data(symbol)
            
            if df is not None and len(df) > 0:
                # 更新缓存
                if use_cache:
                    cache_key = self._get_cache_key(symbol)
                    
                    with self.cache_lock:
                        self.cache[cache_key] = (df, time.time())
                
                # 更新统计
                with self.stats_lock:
                    self.stats['cache_misses'] += 1
                    self.stats['total_requests'] += 1
                    elapsed_ms = (time.time() - start_time) * 1000
                    self.stats['avg_latency_ms'] = (
                        (self.stats['avg_latency_ms'] * (self.stats['total_requests'] - 1) + elapsed_ms)
                        / self.stats['total_requests']
                    )
                
                return df
            else:
                with self.stats_lock:
                    self.stats['errors'] += 1
                    self.stats['total_requests'] += 1
                
                return None
                
        except Exception as e:
            with self.stats_lock:
                self.stats['errors'] += 1
                self.stats['total_requests'] += 1
            
            return None
    
    def get_realtime_data_batch(self,
                               symbols: List[str],
                               use_cache: bool = True,
                               timeout: int = 30) -> Dict[str, pd.DataFrame]:
        """
        并发获取多只股票实时数据
        
        Args:
            symbols: 股票代码列表
            use_cache: 是否使用缓存
            timeout: 超时时间（秒）
            
        Returns:
            {symbol: DataFrame}
        """
        start_time = time.time()
        results = {}
        
        # 使用线程池并发获取
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_symbol = {
                executor.submit(self.get_realtime_data_single, symbol, use_cache): symbol
                for symbol in symbols
            }
            
            # 收集结果
            for future in as_completed(future_to_symbol, timeout=timeout):
                symbol = future_to_symbol[future]
                
                try:
                    df = future.result()
                    if df is not None:
                        results[symbol] = df
                except Exception as e:
                    print(f"⚠️ 获取 {symbol} 失败: {e}")
        
        elapsed_ms = (time.time() - start_time) * 1000
        avg_ms = elapsed_ms / len(symbols) if symbols else 0
        
        print(f"并发获取: {len(results)}/{len(symbols)}支成功, "
              f"总耗时{elapsed_ms:.0f}ms, 平均{avg_ms:.1f}ms/支")
        
        return results
    
    def get_realtime_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        快速获取实时价格（优化版）
        
        Args:
            symbols: 股票代码列表
            
        Returns:
            {symbol: price}
        """
        prices = {}
        
        data_dict = self.get_realtime_data_batch(symbols, use_cache=True, timeout=10)
        
        for symbol, df in data_dict.items():
            if df is not None and len(df) > 0:
                prices[symbol] = df['close'].iloc[-1]
        
        return prices
    
    def clear_expired_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        
        with self.cache_lock:
            expired_keys = [
                key for key, (_, cached_time) in self.cache.items()
                if current_time - cached_time > self.cache_timeout * 2
            ]
            
            for key in expired_keys:
                del self.cache[key]
        
        if expired_keys:
            print(f"清理过期缓存: {len(expired_keys)}个")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        with self.stats_lock:
            stats = self.stats.copy()
        
        cache_size = 0
        with self.cache_lock:
            cache_size = len(self.cache)
        
        stats['cache_size'] = cache_size
        stats['cache_hit_rate'] = (
            stats['cache_hits'] / stats['total_requests'] * 100
            if stats['total_requests'] > 0 else 0
        )
        
        return stats
    
    def reset_stats(self):
        """重置统计"""
        with self.stats_lock:
            self.stats = {
                'total_requests': 0,
                'cache_hits': 0,
                'cache_misses': 0,
                'errors': 0,
                'avg_latency_ms': 0
            }


def benchmark_concurrent_fetch():
    """并发数据获取性能测试"""
    print("="*70)
    print("V5并发数据获取器 - 性能测试")
    print("="*70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 创建获取器
    fetcher = ConcurrentDataFetcher(max_workers=10, cache_timeout=60)
    
    # 测试股票列表（上证50前10支）
    symbols = [
        '600031', '600036', '600519', '600887', '601318',
        '601398', '601939', '601288', '600030', '601888'
    ]
    
    # 测试1：首次获取（无缓存）
    print("【测试1：首次获取（无缓存）】")
    print("-"*70)
    
    start = time.time()
    results = fetcher.get_realtime_data_batch(symbols, use_cache=False, timeout=30)
    elapsed = (time.time() - start) * 1000
    
    print(f"成功获取: {len(results)}/{len(symbols)}支")
    print(f"总耗时: {elapsed:.0f}ms")
    print(f"平均每支: {elapsed/len(symbols):.1f}ms")
    
    # 测试2：再次获取（有缓存）
    print("\n【测试2：再次获取（有缓存）】")
    print("-"*70)
    
    start = time.time()
    results = fetcher.get_realtime_data_batch(symbols, use_cache=True, timeout=10)
    elapsed = (time.time() - start) * 1000
    
    print(f"成功获取: {len(results)}/{len(symbols)}支")
    print(f"总耗时: {elapsed:.0f}ms")
    print(f"平均每支: {elapsed/len(symbols):.1f}ms")
    
    # 测试3：高频获取（100次）
    print("\n【测试3：高频获取（100次，有缓存）】")
    print("-"*70)
    
    fetcher.reset_stats()
    
    start = time.time()
    for _ in range(100):
        results = fetcher.get_realtime_data_batch(symbols, use_cache=True, timeout=10)
    elapsed = (time.time() - start) * 1000
    
    print(f"100次获取总耗时: {elapsed:.0f}ms")
    print(f"平均每次: {elapsed/100:.1f}ms")
    print(f"吞吐量: {100000/elapsed:.0f}次/秒")
    
    # 统计信息
    stats = fetcher.get_stats()
    
    print("\n【统计信息】")
    print("-"*70)
    print(f"总请求数: {stats['total_requests']}")
    print(f"缓存命中: {stats['cache_hits']}")
    print(f"缓存未命中: {stats['cache_misses']}")
    print(f"缓存命中率: {stats['cache_hit_rate']:.1f}%")
    print(f"平均延迟: {stats['avg_latency_ms']:.2f}ms")
    print(f"错误次数: {stats['errors']}")
    print(f"缓存大小: {stats['cache_size']}")
    
    print("\n" + "="*70)
    print("✅ 性能测试完成")
    print("="*70)


if __name__ == '__main__':
    benchmark_concurrent_fetch()
