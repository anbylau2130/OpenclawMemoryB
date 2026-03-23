#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V5实时监控系统 - Real-time Monitor
功能：盘中实时监控、快速信号生成、秒级响应
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import queue

class RealtimeMonitor:
    """实时监控器"""
    
    def __init__(self, 
                 scan_interval: int = 60,
                 alert_threshold: float = 3.5):
        """
        初始化实时监控器
        
        Args:
            scan_interval: 扫描间隔（秒），默认60秒
            alert_threshold: 告警阈值，默认3.5
        """
        self.scan_interval = scan_interval
        self.alert_threshold = alert_threshold
        self.running = False
        self.watch_list = []
        self.alerts = queue.Queue()
        
        # 导入必要模块
        from signal_filter import SignalModule
        from data_fetcher import RobustDataFetcher
        
        self.signal_module = SignalModule(min_score=alert_threshold)
        self.data_fetcher = RobustDataFetcher()
        
        # 日志目录
        self.log_dir = Path(__file__).parent.parent.parent / 'data' / 'realtime_logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 监控统计
        self.stats = {
            'total_scans': 0,
            'signals_generated': 0,
            'alerts_sent': 0,
            'start_time': None,
            'uptime': 0
        }
    
    def load_watch_list(self) -> List[Dict]:
        """
        加载监控股票列表
        
        Returns:
            股票列表
        """
        # 从最新选股结果加载
        selections_dir = Path(__file__).parent.parent.parent / 'projects' / 'stock-tracking' / 'selections'
        
        # 查找最新的V5选股文件
        selection_files = sorted(selections_dir.glob('selection_*_v5*.json'), reverse=True)
        
        if not selection_files:
            # 如果没有选股文件，使用上证50成分股
            return self.get_default_watch_list()
        
        with open(selection_files[0], 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        stocks = data.get('stocks', [])
        
        if len(stocks) == 0:
            # 如果选股结果为空，使用默认列表
            return self.get_default_watch_list()
        
        return stocks
    
    def get_default_watch_list(self) -> List[Dict]:
        """获取默认监控列表（上证50前10支）"""
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
            {'symbol': '601888', 'name': '中国中免'}
        ]
    
    def quick_scan(self, symbol: str) -> Optional[Dict]:
        """
        快速扫描单只股票
        
        Args:
            symbol: 股票代码
            
        Returns:
            扫描结果
        """
        try:
            # 获取实时数据（使用缓存，1分钟有效期）
            data = self.data_fetcher.get_stock_data(symbol)

            if data is None:
                return None

            # 从字典中提取数据
            close = data.get('current_price', 0)
            volume = data.get('volume', 0)
            change_pct = data.get('change_pct', 0)
            name = data.get('name', symbol)

            # 快速信号生成（简化版）
            # 这里只检查最关键的几个条件
            signal = {
                'symbol': symbol,
                'name': name,
                'price': close,
                'change_pct': round(change_pct, 2),
                'volume': volume,
                'timestamp': datetime.now().isoformat(),
                'alerts': []
            }
            
            # 检查是否触发告警条件
            # 1. 急跌（-2%以上）
            if change_pct <= -2.0:
                signal['alerts'].append({
                    'type': 'RAPID_DROP',
                    'message': f"急跌{abs(change_pct):.2f}%",
                    'priority': 'HIGH'
                })
            
            # 2. 急涨（+3%以上）
            elif change_pct >= 3.0:
                signal['alerts'].append({
                    'type': 'RAPID_RISE',
                    'message': f"急涨{change_pct:.2f}%",
                    'priority': 'HIGH'
                })
            
            # 3. 放量（暂不检测，需要历史数据）
            # TODO: 后续可添加历史成交量对比
            
            return signal
            
        except Exception as e:
            print(f"⚠️ 扫描 {symbol} 失败: {e}")
            return None
    
    def scan_all(self) -> List[Dict]:
        """
        扫描所有监控股票
        
        Returns:
            扫描结果列表
        """
        results = []
        
        for stock in self.watch_list:
            symbol = stock['symbol']
            result = self.quick_scan(symbol)
            
            if result:
                result['name'] = stock.get('name', '')
                results.append(result)
        
        return results
    
    def process_alerts(self, scan_results: List[Dict]):
        """
        处理告警
        
        Args:
            scan_results: 扫描结果
        """
        for result in scan_results:
            if result.get('alerts'):
                alert = {
                    'symbol': result['symbol'],
                    'name': result.get('name', ''),
                    'price': result['price'],
                    'change_pct': result['change_pct'],
                    'alerts': result['alerts'],
                    'timestamp': result['timestamp']
                }
                
                self.alerts.put(alert)
                self.stats['alerts_sent'] += 1
                
                # 打印告警
                self.print_alert(alert)
    
    def print_alert(self, alert: Dict):
        """打印告警"""
        symbol = alert['symbol']
        name = alert['name']
        price = alert['price']
        change = alert['change_pct']

        print(f"\n{'='*70}")
        print(f"⚠️  实时告警 - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*70}")
        print(f"股票: {symbol} {name}")
        print(f"价格: ¥{price:.2f} ({change:+.2f}%)")

        for a in alert['alerts']:
            priority = a['priority']
            icon = '🔴' if priority == 'HIGH' else '🟡'
            print(f"{icon} {a['type']}: {a['message']}")

        print(f"{'='*70}\n")

        # 推送到钉钉工作通知
        self.send_dingtalk_alert(alert)

    def send_dingtalk_alert(self, alert: Dict):
        """推送告警到钉钉工作通知"""
        try:
            from dingtalk_work_notice import send_work_notice
            
            # 构建告警消息
            symbol = alert['symbol']
            name = alert['name']
            price = alert['price']
            change = alert['change_pct']
            time_str = datetime.now().strftime('%H:%M:%S')

            # 格式化告警内容
            alert_lines = []
            for a in alert['alerts']:
                priority = a['priority']
                icon = '🔴' if priority == 'HIGH' else '🟡'
                alert_lines.append(f"{icon} {a['type']}: {a['message']}")

            message = f"""⚠️ 实时告警 - {time_str}

股票: {symbol} {name}
价格: ¥{price:.2f} ({change:+.2f}%)

{chr(10).join(alert_lines)}

💡 V5实时监控系统"""

            # 发送工作通知
            result = send_work_notice(message)
            
            if result.get('errcode') == 0:
                print(f"✅ 告警已推送到钉钉工作通知")
            else:
                print(f"⚠️ 推送失败: {result.get('errmsg')}")

        except Exception as e:
            print(f"⚠️ 工作通知推送异常: {e}")
    
    def log_scan(self, scan_results: List[Dict]):
        """记录扫描日志"""
        log_file = self.log_dir / f"scan_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'scan_count': len(scan_results),
            'results': scan_results
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def monitor_loop(self):
        """监控循环"""
        print(f"\n{'='*70}")
        print(f"V5实时监控系统启动")
        print(f"{'='*70}")
        print(f"扫描间隔: {self.scan_interval}秒")
        print(f"告警阈值: {self.alert_threshold}")
        print(f"监控股票: {len(self.watch_list)}支")
        print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        while self.running:
            try:
                # 扫描所有股票
                scan_results = self.scan_all()
                
                # 处理告警
                self.process_alerts(scan_results)
                
                # 记录日志
                self.log_scan(scan_results)
                
                # 更新统计
                self.stats['total_scans'] += 1
                self.stats['uptime'] = (datetime.now() - self.stats['start_time']).total_seconds()
                
                # 显示扫描摘要
                if self.stats['total_scans'] % 10 == 0:  # 每10次扫描显示一次
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 扫描 #{self.stats['total_scans']} - "
                          f"{len(scan_results)}支股票 - {self.stats['alerts_sent']}个告警")
                
                # 等待下次扫描
                time.sleep(self.scan_interval)
                
            except Exception as e:
                print(f"❌ 监控异常: {e}")
                time.sleep(5)
    
    def start(self):
        """启动监控"""
        # 加载监控列表
        self.watch_list = self.load_watch_list()
        
        if not self.watch_list:
            print("❌ 监控列表为空，无法启动")
            return
        
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print("✅ 实时监控已启动")
    
    def stop(self):
        """停止监控"""
        self.running = False
        
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
        
        print("\n监控已停止")
        print(f"统计信息:")
        print(f"  总扫描次数: {self.stats['total_scans']}")
        print(f"  发送告警: {self.stats['alerts_sent']}")
        print(f"  运行时长: {self.stats['uptime']:.0f}秒")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'uptime_str': str(timedelta(seconds=int(self.stats['uptime']))),
            'watch_list_count': len(self.watch_list),
            'pending_alerts': self.alerts.qsize()
        }


def main():
    """主函数 - 实时监控演示"""
    
    print("="*70)
    print("V5实时监控系统")
    print("="*70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 创建监控器（60秒扫描间隔）
    monitor = RealtimeMonitor(
        scan_interval=60,
        alert_threshold=3.5
    )
    
    # 启动监控
    monitor.start()
    
    try:
        # 运行5分钟演示
        print("\n监控运行中... (演示5分钟，按Ctrl+C停止)\n")
        
        for i in range(5):
            time.sleep(60)
            stats = monitor.get_stats()
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 运行状态:")
            print(f"  扫描次数: {stats['total_scans']}")
            print(f"  告警数量: {stats['alerts_sent']}")
            print(f"  运行时长: {stats['uptime_str']}")
        
    except KeyboardInterrupt:
        print("\n\n用户中断")
    
    finally:
        # 停止监控
        monitor.stop()
        
        print("\n" + "="*70)
        print("✅ 实时监控演示完成")
        print("="*70)


if __name__ == '__main__':
    main()
