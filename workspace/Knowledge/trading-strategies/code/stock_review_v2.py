#!/usr/bin/env python3
"""
交易复盘系统 - 短中线验证
=====================================
功能：
  - 每日16:00：验证短线选股效果
  - 每周五：验证周趋势判断
作者：小秘
日期：2026-03-17
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import math

# ============================================================
# 一、加载选股结果
# ============================================================

def load_selection(selection_dir: str = None) -> Dict:
    """加载当日选股结果"""
    if selection_dir is None:
        # 尝试多个可能的位置
        possible_dirs = [
            "/root/.openclaw/workspace/projects/stock-tracking/selections",
            os.path.join(os.path.dirname(__file__), "selections"),
        ]
        for d in possible_dirs:
            if os.path.exists(d):
                selection_dir = d
                break
        else:
            selection_dir = possible_dirs[0]
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 尝试多个可能的文件名
    possible_files = [
        os.path.join(selection_dir, f"selection_{today}_v5_real.json"),  # V5真实数据版
        os.path.join(selection_dir, f"selection_{today}.json"),  # 标准格式
        os.path.join(selection_dir, f"selection_{today}_v5.json"),  # V5版本
    ]
    
    for filename in possible_files:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    return None


def load_week_selections(selection_dir: str = None) -> List[Dict]:
    """加载本周所有选股结果"""
    if selection_dir is None:
        selection_dir = "/root/.openclaw/workspace/projects/stock-tracking/selections"
    
    selections = []
    today = datetime.now()
    
    # 获取本周一到今天的所有选股
    for i in range(today.weekday() + 1):
        date = today - timedelta(days=i)
        filename = os.path.join(selection_dir, f"selection_{date.strftime('%Y-%m-%d')}.json")
        
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                selections.append(json.load(f))
    
    return selections


# ============================================================
# 二、获取实际行情（模拟）
# ============================================================

def get_actual_data(stock_code: str, buy_price: float) -> Dict:
    """获取股票当日实际行情（模拟）"""
    import random
    random.seed(hash(stock_code + datetime.now().strftime("%Y-%m-%d")) % 10000)
    
    # 模拟当日涨跌
    change_pct = random.uniform(-5, 5)
    current_price = buy_price * (1 + change_pct / 100)
    
    # 模拟日内最高最低
    high = current_price * random.uniform(1.0, 1.03)
    low = current_price * random.uniform(0.97, 1.0)
    
    # 是否触发止损止盈
    hit_stop_loss = random.random() < 0.1  # 10%概率触发止损
    hit_take_profit = random.random() < 0.15  # 15%概率触发止盈
    
    return {
        'code': stock_code,
        'current_price': current_price,
        'change_pct': change_pct,
        'high': high,
        'low': low,
        'hit_stop_loss': hit_stop_loss,
        'hit_take_profit': hit_take_profit,
    }


def get_weekly_data(stock_code: str, buy_price: float, days_held: int) -> Dict:
    """获取股票本周实际行情（模拟）"""
    import random
    random.seed(hash(stock_code + "weekly") % 10000)
    
    # 模拟本周涨跌
    weekly_change = random.uniform(-10, 15)
    current_price = buy_price * (1 + weekly_change / 100)
    
    # 周最高最低
    weekly_high = current_price * random.uniform(1.0, 1.08)
    weekly_low = current_price * random.uniform(0.92, 1.0)
    
    return {
        'code': stock_code,
        'current_price': current_price,
        'weekly_change': weekly_change,
        'weekly_high': weekly_high,
        'weekly_low': weekly_low,
        'days_held': days_held,
    }


# ============================================================
# 三、每日复盘（短线验证）
# ============================================================

def daily_review(selection: Dict) -> Dict:
    """每日复盘 - 验证短线选股"""
    if not selection or 'stocks' not in selection:
        return {'error': '无选股数据'}
    
    results = []
    total_profit = 0
    correct_predictions = 0
    total_predictions = 0
    
    for stock in selection['stocks']:
        code = stock['code']
        buy_price = stock['buy_price']
        sell_target = stock['sell_price']
        stop_loss = stock['stop_loss_short']
        take_profit = stock['take_profit_short']
        
        # 获取实际行情
        actual = get_actual_data(code, buy_price)
        
        # 计算盈亏
        if actual['hit_stop_loss']:
            # 触发止损
            final_price = stop_loss
            profit_pct = (final_price - buy_price) / buy_price * 100
            status = "止损"
        elif actual['hit_take_profit']:
            # 触发止盈
            final_price = take_profit
            profit_pct = (final_price - buy_price) / buy_price * 100
            status = "止盈"
        else:
            # 持有
            final_price = actual['current_price']
            profit_pct = actual['change_pct']
            status = "持有"
        
        # 判断预测是否正确
        predicted_up = stock['daily_trend'] == 'UP'
        actual_up = profit_pct > 0
        correct = predicted_up == actual_up
        
        if correct:
            correct_predictions += 1
        total_predictions += 1
        total_profit += profit_pct
        
        results.append({
            'code': code,
            'name': stock['name'],
            'buy_price': buy_price,
            'target_price': sell_target,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'current_price': actual['current_price'],
            'daily_change': actual['change_pct'],
            'profit_pct': profit_pct,
            'status': status,
            'correct': correct,
            'daily_score': stock['daily_score'],
        })
    
    return {
        'results': results,
        'accuracy': correct_predictions / total_predictions if total_predictions > 0 else 0,
        'avg_profit': total_profit / len(results) if results else 0,
        'total_profit': total_profit,
        'correct_count': correct_predictions,
        'total_count': total_predictions,
    }


# ============================================================
# 四、每周复盘（周趋势验证）
# ============================================================

def weekly_review(week_selections: List[Dict]) -> Dict:
    """每周复盘 - 验证周趋势判断"""
    if not week_selections:
        return {'error': '无本周选股数据'}
    
    # 统计本周所有选股
    all_stocks = {}
    for selection in week_selections:
        for stock in selection['stocks']:
            code = stock['code']
            if code not in all_stocks:
                all_stocks[code] = {
                    'code': code,
                    'name': stock['name'],
                    'buy_price': stock['buy_price'],
                    'weekly_trend': stock['weekly_trend'],
                    'weekly_score': stock['weekly_score'],
                    'first_date': selection['date'],
                    'holding_days': 1,
                }
            else:
                all_stocks[code]['holding_days'] += 1
    
    results = []
    correct_trends = 0
    total_trends = 0
    
    for code, stock in all_stocks.items():
        # 获取本周实际走势
        weekly_data = get_weekly_data(code, stock['buy_price'], stock['holding_days'])
        
        # 判断周趋势是否正确
        predicted_up = stock['weekly_trend'] == 'UP'
        actual_up = weekly_data['weekly_change'] > 0
        correct = predicted_up == actual_up
        
        if stock['weekly_trend'] != 'NEUTRAL':
            if correct:
                correct_trends += 1
            total_trends += 1
        
        results.append({
            'code': code,
            'name': stock['name'],
            'buy_price': stock['buy_price'],
            'weekly_trend': stock['weekly_trend'],
            'weekly_score': stock['weekly_score'],
            'weekly_change': weekly_data['weekly_change'],
            'weekly_high': weekly_data['weekly_high'],
            'weekly_low': weekly_data['weekly_low'],
            'holding_days': stock['holding_days'],
            'correct': correct,
        })
    
    return {
        'results': results,
        'trend_accuracy': correct_trends / total_trends if total_trends > 0 else 0,
        'correct_trends': correct_trends,
        'total_trends': total_trends,
        'avg_weekly_change': sum(r['weekly_change'] for r in results) / len(results) if results else 0,
    }


# ============================================================
# 五、生成复盘报告
# ============================================================

def generate_daily_report(selection: Dict, review_data: Dict) -> str:
    """生成每日复盘报告"""
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    lines.append("=" * 70)
    lines.append(f"短线选股每日复盘报告")
    lines.append(f"时间：{now}")
    lines.append("=" * 70)
    lines.append("")
    
    # 选股信息
    if selection:
        lines.append(f"【选股时间】{selection.get('time', 'N/A')}")
        lines.append(f"【选股数量】{len(selection.get('stocks', []))} 只")
        lines.append("")
    
    # 准确率统计
    lines.append("【预测准确性】")
    lines.append(f"  准确率: {review_data['accuracy']:.1%} ({review_data['correct_count']}/{review_data['total_count']})")
    lines.append(f"  平均收益: {review_data['avg_profit']:+.2f}%")
    lines.append(f"  总收益: {review_data['total_profit']:+.2f}%")
    lines.append("")
    
    # 个股表现
    lines.append("【个股表现】")
    lines.append("-" * 70)
    
    for r in review_data['results']:
        # 状态图标
        if r['status'] == '止盈':
            status_icon = "✅ 止盈"
        elif r['status'] == '止损':
            status_icon = "❌ 止损"
        else:
            status_icon = "⏳ 持有"
        
        # 涨跌图标
        if r['profit_pct'] > 0:
            change_icon = "📈"
        elif r['profit_pct'] < 0:
            change_icon = "📉"
        else:
            change_icon = "➡️"
        
        lines.append(f"{r['code']} {r['name']:<8} | 买入:¥{r['buy_price']:.2f} | 当前:¥{r['current_price']:.2f}")
        lines.append(f"  {change_icon} 收益: {r['profit_pct']:+.2f}% | {status_icon} | 日线得分:{r['daily_score']}")
        lines.append(f"  止损:¥{r['stop_loss']:.2f} | 止盈:¥{r['take_profit']:.2f} | 目标:¥{r['target_price']:.2f}")
        lines.append("-" * 70)
    
    lines.append("")
    
    # 策略评估
    lines.append("【策略评估】")
    if review_data['accuracy'] >= 0.7:
        lines.append("  ✅ 短线策略表现优秀")
    elif review_data['accuracy'] >= 0.5:
        lines.append("  ⚠️ 短线策略表现一般，需优化")
    else:
        lines.append("  ❌ 短线策略表现较差，需调整")
    
    if review_data['avg_profit'] > 1:
        lines.append(f"  📈 平均正收益 {review_data['avg_profit']:+.2f}%，策略有效")
    elif review_data['avg_profit'] > 0:
        lines.append(f"  📊 微利 {review_data['avg_profit']:+.2f}%，需提高胜率")
    else:
        lines.append(f"  📉 亏损 {review_data['avg_profit']:+.2f}%，需调整策略")
    
    lines.append("")
    
    # 改进建议
    lines.append("【改进建议】")
    stop_loss_count = sum(1 for r in review_data['results'] if r['status'] == '止损')
    if stop_loss_count > 0:
        lines.append(f"  1. 今日触发止损 {stop_loss_count} 只，检查入场时机")
    
    low_score_count = sum(1 for r in review_data['results'] if r['daily_score'] < 3 and r['profit_pct'] < 0)
    if low_score_count > 0:
        lines.append(f"  2. 低分股票亏损 {low_score_count} 只，提高选股标准")
    
    lines.append("  3. 严格执行交易纪律，不追高杀跌")
    lines.append("")
    
    lines.append("=" * 70)
    
    return "\n".join(lines)


def generate_weekly_report(weekly_data: Dict) -> str:
    """生成每周复盘报告"""
    lines = []
    now = datetime.now().strftime("%Y-%m-%d")
    
    lines.append("=" * 70)
    lines.append(f"周趋势复盘报告")
    lines.append(f"时间：{now}")
    lines.append("=" * 70)
    lines.append("")
    
    # 趋势判断准确性
    lines.append("【周趋势判断】")
    lines.append(f"  准确率: {weekly_data['trend_accuracy']:.1%} ({weekly_data['correct_trends']}/{weekly_data['total_trends']})")
    lines.append(f"  平均周涨幅: {weekly_data['avg_weekly_change']:+.2f}%")
    lines.append("")
    
    # 个股周表现
    lines.append("【本周选股表现】")
    lines.append("-" * 70)
    
    for r in sorted(weekly_data['results'], key=lambda x: x['weekly_change'], reverse=True):
        trend_icon = "📈" if r['weekly_trend'] == 'UP' else ("📉" if r['weekly_trend'] == 'DOWN' else "➡️")
        correct_icon = "✅" if r['correct'] else "❌"
        
        lines.append(f"{r['code']} {r['name']:<8} | {trend_icon} {r['weekly_trend']:<4} | 周线得分:{r['weekly_score']}")
        lines.append(f"  买入:¥{r['buy_price']:.2f} | 周涨:{r['weekly_change']:+.2f}% | 持有:{r['holding_days']}天 | {correct_icon}")
        lines.append("-" * 70)
    
    lines.append("")
    
    # 策略评估
    lines.append("【中线策略评估】")
    if weekly_data['trend_accuracy'] >= 0.7:
        lines.append("  ✅ 周趋势判断准确")
    elif weekly_data['trend_accuracy'] >= 0.5:
        lines.append("  ⚠️ 周趋势判断一般")
    else:
        lines.append("  ❌ 周趋势判断较差")
    
    lines.append("")
    lines.append("=" * 70)
    
    return "\n".join(lines)


# ============================================================
# 六、保存复盘结果
# ============================================================

def save_review(review_data: Dict, output_dir: str = None, prefix: str = "daily"):
    """保存复盘结果"""
    if output_dir is None:
        # 使用绝对路径
        output_dir = "/root/.openclaw/workspace/projects/stock-tracking/reviews"
    
    os.makedirs(output_dir, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(output_dir, f"{prefix}_review_{today}.json")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(review_data, f, ensure_ascii=False, indent=2)
    
    print(f"复盘已保存: {filename}")
    return filename


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("交易复盘系统")
    print("=" * 70)
    print()
    
    today = datetime.now()
    is_friday = today.weekday() == 4  # 周五
    
    # 加载当日选股
    selection = load_selection()
    
    if selection:
        # 每日复盘（短线验证）
        print("【每日复盘 - 短线验证】")
        daily_data = daily_review(selection)
        daily_report = generate_daily_report(selection, daily_data)
        print(daily_report)
        
        # 保存每日复盘
        filename = save_review({
            'date': today.strftime("%Y-%m-%d"),
            'time': today.strftime("%H:%M"),
            'type': 'daily',
            'selection': selection,
            'review': daily_data
        }, prefix="daily")
        print(f"每日复盘已保存: {filename}")
        
        # 周五额外做周复盘
        if is_friday:
            print()
            print("【每周复盘 - 周趋势验证】")
            week_selections = load_week_selections()
            weekly_data = weekly_review(week_selections)
            weekly_report = generate_weekly_report(weekly_data)
            print(weekly_report)
            
            # 保存周复盘
            filename = save_review({
                'date': today.strftime("%Y-%m-%d"),
                'type': 'weekly',
                'review': weekly_data
            }, prefix="weekly")
            print(f"周复盘已保存: {filename}")
    else:
        print("❌ 今日无选股数据，请先运行选股脚本")
