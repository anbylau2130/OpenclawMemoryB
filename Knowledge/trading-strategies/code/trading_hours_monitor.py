#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易时段监控启动器
功能：在交易时段（9:30-15:00）自动启动实时监控
"""

import sys
import time
from datetime import datetime, time as dt_time
from pathlib import Path

# 添加代码目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from realtime_monitor import RealtimeMonitor


def is_trading_hours() -> bool:
    """判断当前是否在交易时段"""
    now = datetime.now()
    current_time = now.time()

    # 交易时段：9:30-11:30, 13:00-15:00
    morning_start = dt_time(9, 30)
    morning_end = dt_time(11, 30)
    afternoon_start = dt_time(13, 0)
    afternoon_end = dt_time(15, 0)

    return (morning_start <= current_time <= morning_end) or \
           (afternoon_start <= current_time <= afternoon_end)


def main():
    """主函数"""
    print("="*70)
    print("交易时段监控启动器")
    print("="*70)
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 检查是否在交易时段
    if not is_trading_hours():
        print("\n⏸️  当前不在交易时段（9:30-15:00）")
        print("监控未启动")
        return

    print("\n✅ 当前在交易时段，启动实时监控...")
    print()

    # 创建监控器（60秒扫描间隔，告警阈值3.5）
    monitor = RealtimeMonitor(
        scan_interval=60,
        alert_threshold=3.5
    )

    # 启动监控
    monitor.start()

    try:
        print("\n监控运行中... (交易时段自动监控)")
        print("按Ctrl+C停止\n")

        # 持续监控，直到交易时段结束
        while is_trading_hours():
            time.sleep(60)

            # 显示状态
            stats = monitor.get_stats()
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 运行状态:")
            print(f"  扫描次数: {stats['total_scans']}")
            print(f"  告警数量: {stats['alerts_sent']}")
            print(f"  运行时长: {stats['uptime_str']}")

        print("\n\n交易时段结束，停止监控")

    except KeyboardInterrupt:
        print("\n\n用户中断")

    finally:
        # 停止监控
        monitor.stop()

        print("\n" + "="*70)
        print("✅ 交易时段监控结束")
        print("="*70)


if __name__ == '__main__':
    main()
