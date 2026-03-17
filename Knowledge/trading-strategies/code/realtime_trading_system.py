#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V5实时交易系统 - 完整集成
功能：实时监控 + 快速信号 + 并发数据 + 告警推送
"""

import time
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
from pathlib import Path

# 导入所有模块
from concurrent_data_fetcher import ConcurrentDataFetcher
from fast_signal_generator import FastSignalGenerator
from alert_notifier import AlertNotifier
from trading_executor import TradingExecutor


class RealtimeTradingSystem:
    """实时交易系统"""
    
    def __init__(self,
                 scan_interval: int = 60,
                 signal_threshold: float = 4.0,
                 max_workers: int = 10):
        """
        初始化
        
        Args:
            scan_interval: 扫描间隔（秒）
            signal_threshold: 信号阈值
            max_workers: 最大并发数
        """
        self.scan_interval = scan_interval
        self.signal_threshold = signal_threshold
        self.max_workers = max_workers
        
        # 初始化各模块
        self.data_fetcher = ConcurrentDataFetcher(max_workers=max_workers)
        self.signal_generator = FastSignalGenerator()
        self.alert_notifier = AlertNotifier(alert_cooldown=300, max_alerts_per_minute=20)
        self.executor = TradingExecutor(initial_capital=100000)
        
        # 监控列表
        self.watch_list = []
        
        # 运行状态
        self.running = False
        self.monitor_thread = None
        
        # 统计
        self.stats = {
            'start_time': None,
            'total_scans': 0,
            'signals_generated': 0,
            'alerts_sent': 0,
            'trades_executed': 0
        }
        
        # 日志目录
        self.log_dir = Path(__file__).parent.parent.parent / 'data' / 'realtime_logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        print("="*70)
        print("V5实时交易系统初始化")
        print("="*70)
        print(f"扫描间隔: {scan_interval}秒")
        print(f"信号阈值: {signal_threshold}")
        print(f"最大并发: {max_workers}")
        print(f"初始资金: ¥{self.executor.portfolio.initial_capital:,.0f}")
        print("="*70)
    
    def load_watch_list(self) -> List[Dict]:
        """加载监控列表"""
        # 默认：上证50前15支
        return [
            {'symbol': '600031', 'name': '三一重工'},
            {'symbol': '600036', 'name': '招商银行'},
            {'symbol': '600519', 'name': '贵州茅台'},
            {'symbol': '600887', 'name': '伊利股份'},
            {'symbol': '601318', 'name': '中国平安'},
            {'symbol': '601398', 'name': '工商银行'},
            {'symbol': '601939', 'name': '建设银行'},
            {'symbol': '601288', 'name': '农业银行'},
            {'symbol': '600030', 'name': '中信证券'},
            {'symbol': '601888', 'name': '中国中免'},
            {'symbol': '600276', 'name': '恒瑞医药'},
            {'symbol': '600000', 'name': '浦发银行'},
            {'symbol': '600016', 'name': '民生银行'},
            {'symbol': '601166', 'name': '兴业银行'},
            {'symbol': '600104', 'name': '上汽集团'}
        ]
    
    def scan_market(self) -> Dict:
        """
        扫描市场
        
        Returns:
            扫描结果
        """
        start_time = time.time()
        
        # 获取所有股票数据
        symbols = [stock['symbol'] for stock in self.watch_list]
        data_dict = self.data_fetcher.get_realtime_data_batch(symbols, use_cache=True)
        
        # 生成信号
        signals = []
        
        for stock in self.watch_list:
            symbol = stock['symbol']
            name = stock['name']
            
            if symbol not in data_dict:
                continue
            
            df = data_dict[symbol]
            
            # 快速生成信号
            signal = self.signal_generator.generate_signal_fast(symbol, df)
            signal['name'] = name
            
            # 检查是否达到阈值
            if signal['total_score'] >= self.signal_threshold:
                signals.append(signal)
                
                # 发送买入信号告警
                self.alert_notifier.notify(
                    symbol=symbol,
                    name=name,
                    alert_type='SIGNAL_BUY',
                    price=signal.get('price', df['close'].iloc[-1]),
                    channels=['console', 'file'],
                    score=signal['total_score']
                )
                
                self.stats['alerts_sent'] += 1
        
        # 排序（按得分降序）
        signals.sort(key=lambda x: x['total_score'], reverse=True)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        self.stats['total_scans'] += 1
        self.stats['signals_generated'] += len(signals)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'scan_count': len(data_dict),
            'signal_count': len(signals),
            'signals': signals[:5],  # 只返回前5个
            'elapsed_ms': elapsed_ms
        }
    
    def monitor_loop(self):
        """监控循环"""
        print(f"\n{'='*70}")
        print(f"实时监控已启动")
        print(f"{'='*70}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"监控股票: {len(self.watch_list)}支")
        print(f"扫描间隔: {self.scan_interval}秒")
        print(f"{'='*70}\n")
        
        while self.running:
            try:
                # 扫描市场
                result = self.scan_market()
                
                # 显示扫描结果
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 扫描 #{self.stats['total_scans']}")
                print(f"  扫描股票: {result['scan_count']}支")
                print(f"  有效信号: {result['signal_count']}个")
                print(f"  耗时: {result['elapsed_ms']:.0f}ms")
                
                if result['signals']:
                    print(f"\n  💰 买入信号:")
                    for i, sig in enumerate(result['signals'], 1):
                        print(f"  {i}. {sig['symbol']} {sig['name']}")
                        print(f"     得分: {sig['total_score']:.1f}")
                        print(f"     因子: {', '.join(sig['factors'][:3])}")
                
                # 每10次扫描显示统计
                if self.stats['total_scans'] % 10 == 0:
                    self.show_stats()
                
                # 等待下次扫描
                time.sleep(self.scan_interval)
                
            except Exception as e:
                print(f"❌ 监控异常: {e}")
                time.sleep(5)
    
    def show_stats(self):
        """显示统计信息"""
        uptime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        print(f"\n{'='*70}")
        print(f"系统统计")
        print(f"{'='*70}")
        print(f"运行时长: {str(timedelta(seconds=int(uptime)))}")
        print(f"扫描次数: {self.stats['total_scans']}")
        print(f"信号生成: {self.stats['signals_generated']}")
        print(f"告警发送: {self.stats['alerts_sent']}")
        
        # 数据获取统计
        data_stats = self.data_fetcher.get_stats()
        print(f"\n数据获取:")
        print(f"  缓存命中率: {data_stats['cache_hit_rate']:.1f}%")
        print(f"  平均延迟: {data_stats['avg_latency_ms']:.2f}ms")
        
        # 告警统计
        alert_stats = self.alert_notifier.get_stats()
        print(f"\n告警推送:")
        print(f"  已发送: {alert_stats['alerts_sent']}")
        print(f"  已过滤: {alert_stats['alerts_dropped']}")
        
        print(f"{'='*70}\n")
    
    def start(self):
        """启动系统"""
        # 加载监控列表
        self.watch_list = self.load_watch_list()
        
        if not self.watch_list:
            print("❌ 监控列表为空")
            return
        
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print("✅ 实时交易系统已启动")
    
    def stop(self):
        """停止系统"""
        self.running = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        print("\n" + "="*70)
        print("实时交易系统已停止")
        print("="*70)
        
        self.show_stats()
    
    def handle_signal(self, signum, frame):
        """处理信号"""
        print(f"\n\n收到停止信号...")
        self.stop()
        sys.exit(0)


def main():
    """主函数"""
    print("\n" + "="*70)
    print("V5实时交易系统")
    print("="*70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 创建系统
    system = RealtimeTradingSystem(
        scan_interval=60,
        signal_threshold=4.0,
        max_workers=10
    )
    
    # 注册信号处理
    signal.signal(signal.SIGINT, system.handle_signal)
    signal.signal(signal.SIGTERM, system.handle_signal)
    
    # 启动系统
    system.start()
    
    try:
        # 运行指定时间（演示5分钟）
        print("\n系统运行中... (演示5分钟，按Ctrl+C停止)\n")
        time.sleep(300)
        
    except KeyboardInterrupt:
        print("\n\n用户中断")
    
    finally:
        system.stop()


if __name__ == '__main__':
    main()
