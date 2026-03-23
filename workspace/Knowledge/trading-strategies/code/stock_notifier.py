#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票通知系统
=====================================
功能：发送选股、告警、复盘通知到钉钉工作通知
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict


def send_selection_notice(stocks: List[Dict], selection_data: Dict = None) -> bool:
    """发送选股通知（支持空结果）"""
    
    # 构建消息
    message = f"## 📊 今日选股结果\n\n"
    message += f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    if stocks:
        message += f"**选股数量**: {len(stocks)} 支\n\n"
        message += "---\n\n"
        
        for i, stock in enumerate(stocks, 1):
            code = stock.get('code', '')
            name = stock.get('name', '')
            price = stock.get('current_price', 0)
            score = stock.get('score', 0)
            signals = stock.get('signals', [])
            stop_loss = stock.get('stop_loss', 0)
            take_profit = stock.get('take_profit', 0)
            
            message += f"### {i}. {code} {name}\n\n"
            message += f"- **买入价**: ¥{price:.2f}\n"
            message += f"- **得分**: {score:.1f}\n"
            message += f"- **止损**: ¥{stop_loss:.2f}\n"
            message += f"- **止盈**: ¥{take_profit:.2f}\n"
            message += f"- **信号**: {', '.join(signals)}\n\n"
        
        message += "---\n\n"
        message += "💡 **风险提示**: 严格执行止损纪律，单只股票仓位不超过20%\n"
    else:
        # 无符合条件股票
        total_analyzed = selection_data.get('total_analyzed', 30) if selection_data else 30
        message += f"**选股数量**: 0 支\n\n"
        message += "---\n\n"
        message += f"📊 **分析股票数**: {total_analyzed} 支\n\n"
        message += "⚠️ **今日无符合高胜率因子的股票**\n\n"
        message += "---\n\n"
        message += "💡 **说明**: V5系统筛选条件较严格，今日市场未出现符合以下因子的股票：\n"
        message += "- VWAP买入信号（胜率92%）\n"
        message += "- 布林带下轨（胜率71%）\n"
        message += "- RSI超卖（胜率69%）\n"
        message += "- KDJ超卖（胜率70%）\n"
        message += "\n建议保持观望，等待更好的入场机会。"
    
    # 发送
    try:
        from dingtalk_work_notice import send_work_notice
        result = send_work_notice(message)
        return result.get('errcode') == 0
    except Exception as e:
        print(f"❌ 发送选股通知失败: {e}")
        return False


def send_alert_notice(alert_type: str, stock_code: str, stock_name: str, 
                       current_price: float, action: str) -> bool:
    """发送告警通知"""
    # 构建消息
    message = f"## ⚠️ 交易告警\n\n"
    message += f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    message += f"**类型**: {alert_type}\n\n"
    message += "---\n\n"
    message += f"### {stock_code} {stock_name}\n\n"
    message += f"- **当前价**: ¥{current_price:.2f}\n"
    message += f"- **建议操作**: {action}\n\n"
    message += "---\n\n"
    message += "⚠️ **请及时处理！**\n"
    
    # 发送
    try:
        from dingtalk_work_notice import send_work_notice
        result = send_work_notice(message)
        return result.get('errcode') == 0
    except Exception as e:
        print(f"❌ 发送告警通知失败: {e}")
        return False


def send_review_notice(review_data: Dict) -> bool:
    """发送复盘通知"""
    # 构建消息
    message = f"## 📈 今日复盘报告\n\n"
    message += f"**日期**: {review_data.get('date', '')}\n\n"
    message += "---\n\n"
    
    accuracy = review_data.get('accuracy', 0)
    avg_return = review_data.get('avg_return', 0)
    total_return = review_data.get('total_return', 0)
    
    message += f"### 📊 总体表现\n\n"
    message += f"- **准确率**: {accuracy:.1f}%\n"
    message += f"- **平均收益**: {avg_return:.2f}%\n"
    message += f"- **总收益**: {total_return:.2f}%\n\n"
    
    # 个股表现
    stocks = review_data.get('stocks', [])
    if stocks:
        message += "---\n\n"
        message += f"### 📋 个股表现\n\n"
        for stock in stocks:
            code = stock.get('code', '')
            name = stock.get('name', '')
            ret = stock.get('return', 0)
            status = stock.get('status', '')
            
            emoji = "✅" if ret > 0 else "❌"
            message += f"{emoji} **{code} {name}**: {ret:.2f}% ({status})\n"
    
    message += "\n---\n\n"
    message += "💡 **持续优化策略，严格执行纪律**\n"
    
    # 发送
    try:
        from dingtalk_work_notice import send_work_notice
        result = send_work_notice(message)
        return result.get('errcode') == 0
    except Exception as e:
        print(f"❌ 发送复盘通知失败: {e}")
        return False


if __name__ == '__main__':
    # 测试
    print("测试选股通知...")
    test_stocks = [
        {
            'code': '601088',
            'name': '中国神华',
            'current_price': 47.48,
            'score': 3.0,
            'signals': ['VWAP买入(97.1%)', 'KDJ偏低(K21)'],
            'stop_loss': 46.06,
            'take_profit': 52.23
        }
    ]
    
    if send_selection_notice(test_stocks):
        print("✅ 选股通知发送成功")
    else:
        print("❌ 选股通知发送失败")
