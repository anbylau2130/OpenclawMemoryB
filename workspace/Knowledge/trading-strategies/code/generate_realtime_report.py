#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成优化报告生成器到监控系统
功能：从监控系统获取数据，生成优化报告
作者：小秘
日期：2026-03-20
"""

import json
from datetime import datetime
from pathlib import Path
import sys

# 添加代码目录
sys.path.insert(0, str(Path(__file__).parent))

from optimized_report_generator import OptimizedTradingReportGenerator
from data_fetcher import RobustDataFetcher


def generate_realtime_report(stock_code: str, scan_count: int):
    """
    生成实时优化报告
    
    Args:
        stock_code: 股票代码
        scan_count: 扫描次数
    """
    print(f"\n{'='*70}")
    print(f"生成优化交易报告 - {stock_code}")
    print(f"{'='*70}")
    
    # 初始化
    config_path = '/root/.openclaw/workspace/trading/config.ini'
    generator = OptimizedTradingReportGenerator(config_path)
    data_fetcher = RobustDataFetcher()
    
    # 获取股票数据
    print(f"\n[1/5] 获取 {stock_code} 实时数据...")
    stock_data = data_fetcher.get_stock_data(stock_code)
    
    if not stock_data:
        print(f"❌ 无法获取 {stock_code} 数据")
        return None
    
    print(f"✅ 数据获取成功")
    print(f"   价格: ¥{stock_data.get('current_price', 0):.2f}")
    print(f"   涨跌: {stock_data.get('change_pct', 0):+.2f}%")
    
    # 获取历史数据（模拟，实际应从数据库获取）
    print(f"\n[2/5] 获取历史数据...")
    historical_data = []
    # TODO: 从数据库获取历史数据
    print(f"⚠️  暂无历史数据")
    
    # 构造市场数据（模拟，实际应从大盘数据获取）
    print(f"\n[3/5] 构造市场数据...")
    market_data = {
        'price_change': stock_data.get('change_pct', 0) / 100,
        'volume_change': 0.5,  # 模拟数据
        'momentum': 65,  # 模拟数据
        'breadth': 0.6,  # 模拟数据
        'volatility': 0.025  # 模拟数据
    }
    print(f"✅ 市场数据构造完成")
    
    # 生成报告（迭代10次）
    print(f"\n[4/5] 生成优化报告（迭代10次）...")
    result = generator.generate_report(
        stock_data,
        scan_count=scan_count,
        historical_data=historical_data,
        market_data=market_data,
        iteration=10
    )
    
    print(f"✅ 报告生成完成")
    print(f"   保存路径: {result['save_path']}")
    print(f"   迭代次数: {result['iteration']}")
    
    # 显示最终建议
    if 'final_recommendation' in result['advice']:
        print(f"\n[5/5] 最终建议:")
        print(f"   {result['advice']['final_recommendation']}")
    
    # 显示交易建议
    print(f"\n{'='*70}")
    print(f"交易建议摘要:")
    print(f"{'='*70}")
    
    short_term = result['advice'].get('short_term', {})
    mid_term = result['advice'].get('mid_term', {})
    long_term = result['advice'].get('long_term', {})
    
    print(f"\n【短期策略（1-2周）】")
    print(f"  操作: {short_term.get('action', 'HOLD')}")
    print(f"  仓位: {short_term.get('position', 0):.0%}")
    print(f"  信心: {short_term.get('confidence', 0):.0%}")
    print(f"  理由: {short_term.get('reason', '暂无')}")
    
    print(f"\n【中期策略（1个月）】")
    print(f"  操作: {mid_term.get('action', 'HOLD')}")
    print(f"  仓位: {mid_term.get('position', 0):.0%}")
    print(f"  信心: {mid_term.get('confidence', 0):.0%}")
    print(f"  理由: {mid_term.get('reason', '暂无')}")
    
    print(f"\n【长期策略（3个月）】")
    print(f"  操作: {long_term.get('action', 'VALUE_INVEST')}")
    print(f"  仓位: {long_term.get('position', 0):.0%}")
    print(f"  信心: {long_term.get('confidence', 0):.0%}")
    print(f"  理由: {long_term.get('reason', '暂无')}")
    
    print(f"\n{'='*70}\n")
    
    return result


if __name__ == '__main__':
    # 生成中国石油的报告
    result = generate_realtime_report('601857', scan_count=84)
    
    if result:
        print("✅ 报告生成成功！")
        print(f"\n查看完整报告:")
        print(f"cat {result['save_path']}")
