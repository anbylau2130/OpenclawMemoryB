#!/usr/bin/env python3
"""
交易复盘系统 - 每日策略验证
=====================================
功能：每天下午4点，验证早上的选股策略是否有效
对比：预测 vs 实际涨跌
作者：小秘
日期：2026-03-17
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# ============================================================
# 一、加载当日选股结果
# ============================================================

def load_today_selection(selection_dir: str = None) -> Dict:
    """加载当天的选股结果"""
    if selection_dir is None:
        selection_dir = os.path.join(os.path.dirname(__file__), "selections")
    
    today = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(selection_dir, f"selection_{today}.json")
    
    if not os.path.exists(filename):
        return None
    
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


# ============================================================
# 二、获取实际涨跌（模拟，实际需要接入真实数据）
# ============================================================

def get_actual_returns(stock_code: str) -> Dict:
    """
    获取股票当日实际涨跌
    实际需要接入真实行情数据
    """
    import random
    random.seed(hash(stock_code + datetime.now().strftime("%Y-%m-%d")) % 10000)
    
    # 模拟当日涨跌（-5% 到 +5%）
    change_pct = random.uniform(-5, 5)
    
    # 模拟成交量变化
    volume_ratio = random.uniform(0.5, 2.0)
    
    return {
        'code': stock_code,
        'change_pct': change_pct,
        'volume_ratio': volume_ratio,
        'high': random.uniform(10, 100),
        'low': random.uniform(10, 100),
    }


# ============================================================
# 三、计算预测准确性
# ============================================================

def calculate_accuracy(selection: Dict) -> Dict:
    """计算预测准确性"""
    if not selection or 'stocks' not in selection:
        return {'error': '无选股数据'}
    
    results = []
    correct_predictions = 0
    total_predictions = 0
    total_return = 0
    
    for stock in selection['stocks']:
        code = stock['code']
        predicted_signal = stock['signal']
        predicted_score = stock['composite_score']
        
        # 获取实际涨跌
        actual = get_actual_returns(code)
        actual_change = actual['change_pct']
        
        # 判断预测是否正确
        # 买入信号 + 实际上涨 = 正确
        # 卖出信号 + 实际下跌 = 正确
        if predicted_signal == 'BUY' and actual_change > 0:
            correct = True
            correct_predictions += 1
        elif predicted_signal == 'SELL' and actual_change < 0:
            correct = True
            correct_predictions += 1
        elif predicted_signal == 'HOLD':
            # 持有信号不计入准确率
            correct = None
        else:
            correct = False
        
        if predicted_signal in ['BUY', 'SELL']:
            total_predictions += 1
        
        total_return += actual_change
        
        results.append({
            'code': code,
            'name': stock['name'],
            'predicted_signal': predicted_signal,
            'predicted_score': predicted_score,
            'actual_change': actual_change,
            'volume_ratio': actual['volume_ratio'],
            'correct': correct
        })
    
    # 计算准确率
    accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
    avg_return = total_return / len(results) if results else 0
    
    return {
        'results': results,
        'accuracy': accuracy,
        'correct_count': correct_predictions,
        'total_predictions': total_predictions,
        'avg_return': avg_return,
        'total_return': total_return
    }


# ============================================================
# 四、生成复盘报告
# ============================================================

def generate_review_report(selection: Dict, accuracy_data: Dict) -> str:
    """生成复盘报告"""
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    lines.append("=" * 60)
    lines.append(f"交易策略复盘报告")
    lines.append(f"时间：{now}")
    lines.append("=" * 60)
    lines.append("")
    
    # 选股信息
    if selection:
        lines.append("【今日选股】")
        lines.append(f"  选股时间: {selection.get('time', 'N/A')}")
        lines.append(f"  选股数量: {len(selection.get('stocks', []))} 只")
        lines.append("")
    
    # 准确率统计
    lines.append("【预测准确性】")
    lines.append(f"  准确率: {accuracy_data['accuracy']:.1%}")
    lines.append(f"  正确: {accuracy_data['correct_count']} / {accuracy_data['total_predictions']}")
    lines.append(f"  平均收益: {accuracy_data['avg_return']:+.2f}%")
    lines.append(f"  总收益: {accuracy_data['total_return']:+.2f}%")
    lines.append("")
    
    # 详细结果
    lines.append("【个股表现】")
    lines.append("-" * 60)
    
    for r in accuracy_data['results']:
        # 预测信号
        signal_emoji = "🟢" if r['predicted_signal'] == 'BUY' else ("🔴" if r['predicted_signal'] == 'SELL' else "🟡")
        
        # 实际涨跌
        if r['actual_change'] > 0:
            change_str = f"+{r['actual_change']:.2f}%"
            change_emoji = "📈"
        elif r['actual_change'] < 0:
            change_str = f"{r['actual_change']:.2f}%"
            change_emoji = "📉"
        else:
            change_str = f"{r['actual_change']:.2f}%"
            change_emoji = "➡️"
        
        # 预测结果
        if r['correct'] is True:
            result_emoji = "✅"
        elif r['correct'] is False:
            result_emoji = "❌"
        else:
            result_emoji = "➖"
        
        lines.append(f"{r['code']} {r['name']:<8} | {signal_emoji} {r['predicted_signal']:<4} | {change_emoji} {change_str:>8} | 量比:{r['volume_ratio']:.2f} | {result_emoji}")
    
    lines.append("-" * 60)
    lines.append("")
    
    # 策略评估
    lines.append("【策略评估】")
    if accuracy_data['accuracy'] >= 0.7:
        lines.append("  ✅ 策略表现优秀，继续使用")
    elif accuracy_data['accuracy'] >= 0.5:
        lines.append("  ⚠️ 策略表现一般，需要优化")
    else:
        lines.append("  ❌ 策略表现较差，需要调整")
    
    if accuracy_data['avg_return'] > 0:
        lines.append(f"  📈 平均正收益 {accuracy_data['avg_return']:+.2f}%，策略有效")
    else:
        lines.append(f"  📉 平均负收益 {accuracy_data['avg_return']:+.2f}%，需要改进")
    lines.append("")
    
    # 改进建议
    lines.append("【改进建议】")
    
    # 分析错误预测
    wrong_predictions = [r for r in accuracy_data['results'] if r['correct'] is False]
    
    if len(wrong_predictions) > 0:
        lines.append(f"  1. 错误预测 {len(wrong_predictions)} 只，分析原因：")
        
        # 分析动量因子是否失效
        momentum_fails = [r for r in wrong_predictions if r['predicted_signal'] == 'BUY' and r['actual_change'] < 0]
        if len(momentum_fails) > 0:
            lines.append(f"     - 动量因子可能失效（买入后下跌 {len(momentum_fails)} 只）")
        
        # 分析是否追高
        high_vol_fails = [r for r in wrong_predictions if r['volume_ratio'] > 1.5]
        if len(high_vol_fails) > 0:
            lines.append(f"     - 可能追高（高量比后反转 {len(high_vol_fails)} 只）")
    
    lines.append("  2. 建议调整因子权重")
    lines.append("  3. 增加成交量确认条件")
    lines.append("  4. 设置更严格的止损")
    lines.append("")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)


# ============================================================
# 五、保存复盘结果
# ============================================================

def save_review(review_data: Dict, output_dir: str = None):
    """保存复盘结果"""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "reviews")
    
    os.makedirs(output_dir, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(output_dir, f"review_{today}.json")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(review_data, f, ensure_ascii=False, indent=2)
    
    return filename


# ============================================================
# 六、历史复盘统计
# ============================================================

def calculate_historical_stats(review_dir: str = None) -> Dict:
    """计算历史统计"""
    if review_dir is None:
        review_dir = os.path.join(os.path.dirname(__file__), "reviews")
    
    if not os.path.exists(review_dir):
        return {'error': '无历史数据'}
    
    # 读取所有复盘文件
    reviews = []
    for filename in os.listdir(review_dir):
        if filename.startswith("review_") and filename.endswith(".json"):
            with open(os.path.join(review_dir, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 从 accuracy 字典中提取 accuracy 值
                if 'accuracy' in data:
                    if isinstance(data['accuracy'], dict):
                        reviews.append({
                            'accuracy': data['accuracy'].get('accuracy', 0),
                            'avg_return': data['accuracy'].get('avg_return', 0)
                        })
                    else:
                        reviews.append(data)
    
    if not reviews:
        return {'error': '无历史数据'}
    
    # 计算统计
    accuracies = [r.get('accuracy', 0) for r in reviews if isinstance(r.get('accuracy'), (int, float))]
    avg_returns = [r.get('avg_return', 0) for r in reviews if isinstance(r.get('avg_return'), (int, float))]
    
    return {
        'total_days': len(reviews),
        'avg_accuracy': sum(accuracies) / len(accuracies) if accuracies else 0,
        'avg_return': sum(avg_returns) / len(avg_returns) if avg_returns else 0,
        'best_accuracy': max(accuracies) if accuracies else 0,
        'worst_accuracy': min(accuracies) if accuracies else 0,
    }


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("交易策略复盘系统")
    print("=" * 60)
    print()
    
    # 加载当日选股
    selection = load_today_selection()
    
    if not selection:
        print("❌ 今日无选股数据，请先运行选股脚本")
        exit(1)
    
    # 计算准确性
    accuracy_data = calculate_accuracy(selection)
    
    # 生成报告
    report = generate_review_report(selection, accuracy_data)
    print(report)
    
    # 保存复盘
    review_data = {
        'date': datetime.now().strftime("%Y-%m-%d"),
        'time': datetime.now().strftime("%H:%M"),
        'selection': selection,
        'accuracy': accuracy_data
    }
    filename = save_review(review_data)
    print(f"复盘结果已保存: {filename}")
    
    # 历史统计
    stats = calculate_historical_stats()
    if 'error' not in stats:
        print()
        print("【历史统计】")
        print(f"  回测天数: {stats['total_days']}")
        print(f"  平均准确率: {stats['avg_accuracy']:.1%}")
        print(f"  平均收益: {stats['avg_return']:+.2f}%")
