#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V5告警推送系统 - Alert Notifier
功能：多渠道告警、优先级管理、去重防刷
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from pathlib import Path
from collections import defaultdict
import queue


class AlertNotifier:
    """告警推送系统"""
    
    def __init__(self,
                 alert_cooldown: int = 300,
                 max_alerts_per_minute: int = 10):
        """
        初始化
        
        Args:
            alert_cooldown: 告警冷却时间（秒）
            max_alerts_per_minute: 每分钟最大告警数
        """
        self.alert_cooldown = alert_cooldown
        self.max_alerts_per_minute = max_alerts_per_minute
        
        # 告警队列
        self.alert_queue = queue.Queue()
        
        # 告警历史（去重）
        self.alert_history: Dict[str, float] = {}
        self.history_lock = threading.Lock()
        
        # 告警计数
        self.alert_counts = defaultdict(int)
        self.counts_lock = threading.Lock()
        
        # 优先级定义
        self.priority_levels = {
            'CRITICAL': 4,  # 关键：立即通知
            'HIGH': 3,      # 高：立即通知
            'MEDIUM': 2,    # 中：批量通知
            'LOW': 1        # 低：仅记录
        }
        
        # 告警类型定义
        self.alert_types = {
            'RAPID_DROP': {
                'name': '急跌',
                'priority': 'HIGH',
                'icon': '🔴',
                'template': '{symbol} {name} 急跌{change:.2f}%，当前价¥{price:.2f}'
            },
            'RAPID_RISE': {
                'name': '急涨',
                'priority': 'HIGH',
                'icon': '🟢',
                'template': '{symbol} {name} 急涨{change:.2f}%，当前价¥{price:.2f}'
            },
            'HIGH_VOLUME': {
                'name': '放量',
                'priority': 'MEDIUM',
                'icon': '📊',
                'template': '{symbol} {name} 放量{volume_ratio:.1f}倍'
            },
            'SIGNAL_BUY': {
                'name': '买入信号',
                'priority': 'CRITICAL',
                'icon': '💰',
                'template': '{symbol} {name} 买入信号，得分{score:.1f}，建议价¥{price:.2f}'
            },
            'SIGNAL_SELL': {
                'name': '卖出信号',
                'priority': 'CRITICAL',
                'icon': '💵',
                'template': '{symbol} {name} 卖出信号，当前价¥{price:.2f}'
            },
            'STOP_LOSS': {
                'name': '触发止损',
                'priority': 'CRITICAL',
                'icon': '🚨',
                'template': '{symbol} {name} 触发止损，当前价¥{price:.2f}，亏损{loss:.2f}%'
            },
            'TAKE_PROFIT': {
                'name': '触发止盈',
                'priority': 'HIGH',
                'icon': '🎉',
                'template': '{symbol} {name} 触发止盈，当前价¥{price:.2f}，盈利{profit:.2f}%'
            }
        }
        
        # 日志目录
        self.log_dir = Path(__file__).parent.parent.parent / 'data' / 'alert_logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 统计
        self.stats = {
            'total_alerts': 0,
            'alerts_sent': 0,
            'alerts_dropped': 0,
            'alerts_by_priority': defaultdict(int)
        }
    
    def _generate_alert_key(self, symbol: str, alert_type: str) -> str:
        """生成告警去重键"""
        hour = datetime.now().strftime('%Y%m%d%H')
        return f"{symbol}_{alert_type}_{hour}"
    
    def _should_send_alert(self, symbol: str, alert_type: str) -> bool:
        """
        判断是否应该发送告警（去重）
        
        Args:
            symbol: 股票代码
            alert_type: 告警类型
            
        Returns:
            是否应该发送
        """
        alert_key = self._generate_alert_key(symbol, alert_type)
        current_time = time.time()
        
        with self.history_lock:
            # 检查冷却时间
            if alert_key in self.alert_history:
                last_alert_time = self.alert_history[alert_key]
                
                if current_time - last_alert_time < self.alert_cooldown:
                    return False
            
            # 更新告警时间
            self.alert_history[alert_key] = current_time
            
            # 清理过期历史
            expired_keys = [
                key for key, timestamp in self.alert_history.items()
                if current_time - timestamp > 3600  # 1小时后过期
            ]
            
            for key in expired_keys:
                del self.alert_history[key]
            
            return True
    
    def _check_rate_limit(self) -> bool:
        """
        检查频率限制
        
        Returns:
            是否在限制内
        """
        current_minute = datetime.now().strftime('%Y%m%d%H%M')
        
        with self.counts_lock:
            count = self.alert_counts[current_minute]
            
            if count >= self.max_alerts_per_minute:
                return False
            
            self.alert_counts[current_minute] += 1
            
            # 清理过期计数
            expired_minutes = [
                minute for minute in self.alert_counts.keys()
                if minute < current_minute
            ]
            
            for minute in expired_minutes:
                del self.alert_counts[minute]
            
            return True
    
    def create_alert(self,
                    symbol: str,
                    name: str,
                    alert_type: str,
                    price: float,
                    **kwargs) -> Optional[Dict]:
        """
        创建告警
        
        Args:
            symbol: 股票代码
            name: 股票名称
            alert_type: 告警类型
            price: 当前价格
            **kwargs: 其他参数
            
        Returns:
            告警字典或None
        """
        # 检查告警类型是否有效
        if alert_type not in self.alert_types:
            print(f"⚠️ 无效的告警类型: {alert_type}")
            return None
        
        # 检查是否应该发送（去重）
        if not self._should_send_alert(symbol, alert_type):
            self.stats['alerts_dropped'] += 1
            return None
        
        # 检查频率限制
        if not self._check_rate_limit():
            self.stats['alerts_dropped'] += 1
            return None
        
        # 获取告警配置
        alert_config = self.alert_types[alert_type]
        
        # 生成告警消息
        message = alert_config['template'].format(
            symbol=symbol,
            name=name,
            price=price,
            **kwargs
        )
        
        # 创建告警
        alert = {
            'id': f"{symbol}_{alert_type}_{int(time.time()*1000)}",
            'symbol': symbol,
            'name': name,
            'type': alert_type,
            'type_name': alert_config['name'],
            'priority': alert_config['priority'],
            'priority_level': self.priority_levels[alert_config['priority']],
            'icon': alert_config['icon'],
            'message': message,
            'price': price,
            'timestamp': datetime.now().isoformat(),
            'data': kwargs
        }
        
        # 更新统计
        self.stats['total_alerts'] += 1
        self.stats['alerts_by_priority'][alert['priority']] += 1
        
        return alert
    
    def send_alert(self, alert: Dict, channels: List[str] = None) -> bool:
        """
        发送告警
        
        Args:
            alert: 告警字典
            channels: 发送渠道列表（默认：console）
            
        Returns:
            是否发送成功
        """
        if channels is None:
            channels = ['console']
        
        success = False
        
        for channel in channels:
            try:
                if channel == 'console':
                    success = self._send_to_console(alert)
                elif channel == 'file':
                    success = self._send_to_file(alert)
                elif channel == 'dingtalk':
                    success = self._send_to_dingtalk(alert)
                else:
                    print(f"⚠️ 未知渠道: {channel}")
            except Exception as e:
                print(f"❌ 发送告警到 {channel} 失败: {e}")
        
        if success:
            self.stats['alerts_sent'] += 1
        
        return success
    
    def _send_to_console(self, alert: Dict) -> bool:
        """发送到控制台"""
        print(f"\n{alert['icon']} {alert['type_name']} [{alert['priority']}]")
        print(f"股票: {alert['symbol']} {alert['name']}")
        print(f"消息: {alert['message']}")
        print(f"时间: {alert['timestamp']}")
        
        return True
    
    def _send_to_file(self, alert: Dict) -> bool:
        """发送到文件"""
        log_file = self.log_dir / f"alerts_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(alert, ensure_ascii=False) + '\n')
        
        return True
    
    def _send_to_dingtalk(self, alert: Dict) -> bool:
        """发送到钉钉（预留接口）"""
        # TODO: 实现钉钉推送
        # 这里可以调用钉钉机器人API
        return True
    
    def notify(self,
              symbol: str,
              name: str,
              alert_type: str,
              price: float,
              channels: List[str] = None,
              **kwargs) -> bool:
        """
        快捷通知方法
        
        Args:
            symbol: 股票代码
            name: 股票名称
            alert_type: 告警类型
            price: 当前价格
            channels: 发送渠道
            **kwargs: 其他参数
            
        Returns:
            是否发送成功
        """
        # 创建告警
        alert = self.create_alert(symbol, name, alert_type, price, **kwargs)
        
        if alert is None:
            return False
        
        # 发送告警
        return self.send_alert(alert, channels)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'alerts_by_priority': dict(self.stats['alerts_by_priority'])
        }
    
    def clear_history(self):
        """清空历史"""
        with self.history_lock:
            self.alert_history.clear()
        
        with self.counts_lock:
            self.alert_counts.clear()


def test_alert_notifier():
    """告警系统测试"""
    print("="*70)
    print("V5告警推送系统 - 测试")
    print("="*70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 创建告警器
    notifier = AlertNotifier(alert_cooldown=60, max_alerts_per_minute=10)
    
    # 测试1：各种类型告警
    print("【测试1：各种类型告警】")
    print("-"*70)
    
    test_cases = [
        {
            'symbol': '600031',
            'name': '三一重工',
            'alert_type': 'RAPID_DROP',
            'price': 20.50,
            'change': -2.5
        },
        {
            'symbol': '600036',
            'name': '招商银行',
            'alert_type': 'RAPID_RISE',
            'price': 40.20,
            'change': 3.5
        },
        {
            'symbol': '600519',
            'name': '贵州茅台',
            'alert_type': 'HIGH_VOLUME',
            'price': 1680.00,
            'volume_ratio': 2.5
        },
        {
            'symbol': '601318',
            'name': '中国平安',
            'alert_type': 'SIGNAL_BUY',
            'price': 45.30,
            'score': 4.5
        },
        {
            'symbol': '601398',
            'name': '工商银行',
            'alert_type': 'STOP_LOSS',
            'price': 4.85,
            'loss': -2.2
        }
    ]
    
    for case in test_cases:
        success = notifier.notify(
            case['symbol'],
            case['name'],
            case['alert_type'],
            case['price'],
            channels=['console', 'file'],
            **{k: v for k, v in case.items() if k not in ['symbol', 'name', 'alert_type', 'price']}
        )
        
        if success:
            print(f"✅ {case['alert_type']} 告警发送成功")
        else:
            print(f"❌ {case['alert_type']} 告警发送失败")
        
        time.sleep(0.5)
    
    # 测试2：去重测试
    print("\n【测试2：去重测试】")
    print("-"*70)
    
    print("发送相同告警（应该被过滤）...")
    for i in range(3):
        success = notifier.notify(
            '600031',
            '三一重工',
            'RAPID_DROP',
            20.50,
            change=-2.5
        )
        
        if success:
            print(f"  第{i+1}次: ✅ 发送成功")
        else:
            print(f"  第{i+1}次: ⏭️ 已过滤（去重）")
    
    # 测试3：统计信息
    print("\n【统计信息】")
    print("-"*70)
    stats = notifier.get_stats()
    
    print(f"总告警数: {stats['total_alerts']}")
    print(f"已发送: {stats['alerts_sent']}")
    print(f"已过滤: {stats['alerts_dropped']}")
    print(f"按优先级:")
    for priority, count in stats['alerts_by_priority'].items():
        print(f"  {priority}: {count}")
    
    print("\n" + "="*70)
    print("✅ 测试完成")
    print("="*70)


if __name__ == '__main__':
    test_alert_notifier()
