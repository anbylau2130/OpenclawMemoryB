#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据管理模块
功能：管理历史数据和市场数据，用于量价分析和市场情绪分析
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from data_fetcher import RobustDataFetcher


class DataManager:
    """数据管理器"""
    
    def __init__(self, data_dir: str = None):
        """初始化"""
        self.data_dir = Path(data_dir or '/root/.openclaw/workspace/data/stock_history')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.data_fetcher = RobustDataFetcher()
    
    def get_historical_data(self, symbol: str, days: int = 5) -> List[Dict]:
        """
        获取历史数据
        
        Args:
            symbol: 股票代码
            days: 天数
            
        Returns:
            历史数据列表
        """
        # 从缓存文件读取
        cache_file = self.data_dir / f"{symbol}_history.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 检查数据是否过期（超过1小时）
                    cache_time = data.get('cache_time', 0)
                    if time.time() - cache_time < 3600:
                        return data.get('history', [])
            except:
                pass
        
        # 如果没有缓存，生成模拟历史数据
        # TODO: 实际应该从数据库或API获取真实历史数据
        history = self._generate_mock_history(symbol, days)
        
        # 保存缓存
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'cache_time': time.time(),
                'history': history
            }, f, indent=2)
        
        return history
    
    def _generate_mock_history(self, symbol: str, days: int) -> List[Dict]:
        """生成模拟历史数据（临时方案）"""
        # 获取当前数据
        current_data = self.data_fetcher.get_stock_data(symbol)
        if not current_data:
            return []
        
        current_volume = current_data.get('volume', 100000000)
        history = []
        
        # 生成过去5天的模拟数据
        for i in range(days):
            # 模拟成交量波动（±20%）
            import random
            volume_variation = random.uniform(0.8, 1.2)
            mock_volume = int(current_volume * volume_variation)
            
            history.append({
                'date': (datetime.now() - timedelta(days=days-i)).strftime('%Y-%m-%d'),
                'volume': mock_volume,
                'price': current_data.get('current_price', 10) * (1 + random.uniform(-0.02, 0.02))
            })
        
        return history
    
    def get_market_data(self, watch_list: List[Dict]) -> Dict:
        """
        获取市场数据
        
        Args:
            watch_list: 监控股票列表
            
        Returns:
            市场数据
        """
        # 获取所有股票数据
        stocks_data = []
        up_count = 0
        down_count = 0
        total_change = 0
        
        for stock in watch_list[:10]:  # 只取前10只
            data = self.data_fetcher.get_stock_data(stock['symbol'])
            if data:
                stocks_data.append(data)
                change = data.get('change_pct', 0)
                total_change += change
                
                if change > 0:
                    up_count += 1
                elif change < 0:
                    down_count += 1
        
        # 计算市场广度（上涨股票占比）
        breadth = up_count / len(stocks_data) if stocks_data else 0.5
        
        # 计算平均价格变化
        avg_change = total_change / len(stocks_data) if stocks_data else 0
        
        # 计算波动率（标准差）
        if len(stocks_data) > 1:
            import numpy as np
            changes = [s.get('change_pct', 0) for s in stocks_data]
            volatility = float(np.std(changes))
        else:
            volatility = 0.02
        
        # 计算动量（简化版：平均涨跌幅）
        momentum = 50 + avg_change * 10  # 转换为0-100
        momentum = max(0, min(100, momentum))
        
        return {
            'price_change': avg_change / 100,  # 转换为小数
            'volume_change': 0.3,  # 简化：假设成交量增加30%
            'momentum': momentum,
            'breadth': breadth,
            'volatility': volatility
        }
    
    def update_stock_history(self, symbol: str, data: Dict):
        """
        更新股票历史数据
        
        Args:
            symbol: 股票代码
            data: 股票数据
        """
        cache_file = self.data_dir / f"{symbol}_history.json"
        
        # 读取现有数据
        history = []
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    history = cached.get('history', [])
            except:
                pass
        
        # 添加新数据
        new_entry = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'volume': data.get('volume', 0),
            'price': data.get('current_price', 0),
            'change_pct': data.get('change_pct', 0)
        }
        
        history.append(new_entry)
        
        # 只保留最近30天的数据
        if len(history) > 30:
            history = history[-30:]
        
        # 保存
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'cache_time': time.time(),
                'history': history
            }, f, indent=2)


if __name__ == '__main__':
    # 测试
    manager = DataManager()
    
    # 测试获取历史数据
    print("=== 测试历史数据获取 ===")
    history = manager.get_historical_data('600031', days=5)
    print(f"获取到 {len(history)} 条历史数据")
    for h in history:
        print(f"  {h['date']}: 成交量={h['volume']:,}")
    
    # 测试获取市场数据
    print("\n=== 测试市场数据获取 ===")
    watch_list = [
        {'symbol': '600031', 'name': '三一重工'},
        {'symbol': '600036', 'name': '招商银行'},
        {'symbol': '600519', 'name': '贵州茅台'}
    ]
    market_data = manager.get_market_data(watch_list)
    print(f"市场数据: {json.dumps(market_data, indent=2)}")
