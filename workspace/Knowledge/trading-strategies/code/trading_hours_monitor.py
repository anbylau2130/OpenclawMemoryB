#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易时段监控启动器
功能：在交易时段（9:30-15:00）自动启动实时监控，定期生成报告
"""

import sys
import time
from datetime import datetime, time as dt_time
from pathlib import Path

# 添加代码目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from realtime_monitor import RealtimeMonitor
from optimized_report_generator import OptimizedTradingReportGenerator
from data_fetcher import RobustDataFetcher
from data_manager import DataManager


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

    # 创建报告生成器
    config_path = '/root/.openclaw/workspace/trading/config.ini'
    report_generator = OptimizedTradingReportGenerator(config_path)
    data_fetcher = RobustDataFetcher()
    data_manager = DataManager()

    # 报告生成间隔（30分钟）
    report_interval = 1800
    last_report_time = time.time()

    # 监控股票列表
    watch_list = [
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

            # 检查是否需要生成报告（每30分钟）
            current_time = time.time()
            if current_time - last_report_time >= report_interval:
                print("\n📊 生成定期监控报告...")
                
                # 获取市场数据（用于市场情绪分析）
                market_data = data_manager.get_market_data(watch_list)

                # 为每只股票生成报告
                for stock in watch_list:
                    try:
                        stock_data = data_fetcher.get_stock_data(stock['symbol'])
                        if stock_data:
                            # 添加股票信息
                            stock_data['code'] = stock['symbol']
                            stock_data['name'] = stock['name']
                            
                            # 获取历史数据（用于量价分析）
                            historical_data = data_manager.get_historical_data(stock['symbol'], days=5)
                            
                            # 生成报告（迭代10次）
                            result = report_generator.generate_report(
                                stock_data,
                                scan_count=stats['total_scans'],
                                historical_data=historical_data,
                                market_data=market_data,
                                iteration=10
                            )
                            print(f"  ✅ {stock['name']} 报告已保存")
                    except Exception as e:
                        print(f"  ⚠️  {stock['name']} 报告生成失败: {e}")

                print("✅ 定期报告生成完成\n")
                last_report_time = current_time

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
