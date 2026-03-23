#!/usr/bin/env python3
"""
股票跟踪分析脚本
使用方法: python3 track_stock.py 600031
"""

import requests
import json
import sys
from datetime import datetime

def get_stock_data(code):
    """获取股票实时数据"""
    # 确定市场
    market = "1" if code.startswith("6") else "0"
    secid = f"{market}.{code}"

    # 获取实时数据
    url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f55,f57,f58,f60,f170,f171"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get('data'):
            d = data['data']
            return {
                'code': code,
                'name': d.get('f58', 'N/A'),
                'current': d.get('f43', 0) / 100,
                'high': d.get('f44', 0) / 100,
                'low': d.get('f45', 0) / 100,
                'open': d.get('f46', 0) / 100,
                'prev_close': d.get('f60', 0) / 100,
                'volume': d.get('f47', 0),
                'amount': d.get('f48', 0) / 100000000,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    except Exception as e:
        print(f"获取数据失败: {e}")

    return None

def get_history_data(code, days=30):
    """获取历史数据"""
    market = "1" if code.startswith("6") else "0"
    secid = f"{market}.{code}"

    url = f"http://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57&klt=101&fqt=1&end=20500101&lmt={days}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get('data') and data['data'].get('klines'):
            klines = []
            for k in data['data']['klines']:
                parts = k.split(',')
                klines.append({
                    'date': parts[0],
                    'open': float(parts[1]),
                    'close': float(parts[2]),
                    'high': float(parts[3]),
                    'low': float(parts[4]),
                    'volume': int(parts[5])
                })
            return klines
    except Exception as e:
        print(f"获取历史数据失败: {e}")

    return []

def analyze_stock(code, name=None):
    """分析股票"""
    print("=" * 60)
    print(f"股票跟踪分析 - {code}")
    print("=" * 60)

    # 获取实时数据
    realtime = get_stock_data(code)
    if not realtime:
        print("无法获取数据")
        return

    # 获取历史数据
    history = get_history_data(code, 30)

    if name:
        realtime['name'] = name

    print(f"\n【实时行情】 {realtime['time']}")
    print(f"股票: {realtime['name']} ({code})")
    print(f"当前: {realtime['current']:.2f}")

    # 计算涨跌
    change = realtime['current'] - realtime['prev_close']
    change_pct = (change / realtime['prev_close'] * 100) if realtime['prev_close'] > 0 else 0
    print(f"涨跌: {change_pct:+.2f}%")

    print(f"今开: {realtime['open']:.2f}")
    print(f"最高: {realtime['high']:.2f}")
    print(f"最低: {realtime['low']:.2f}")
    print(f"昨收: {realtime['prev_close']:.2f}")
    print(f"成交量: {realtime['volume']/10000:.0f}万手")
    print(f"成交额: {realtime['amount']:.2f}亿")

    # 技术分析
    if len(history) >= 20:
        print("\n" + "=" * 60)
        print("【技术分析】")
        print("=" * 60)

        closes = [k['close'] for k in history]
        vols = [k['volume'] for k in history]

        # 均线
        ma5 = sum(closes[-5:]) / 5
        ma10 = sum(closes[-10:]) / 10
        ma20 = sum(closes[-20:]) / 20

        print(f"\n1️⃣ 均线系统")
        print(f"MA5:  {ma5:.2f}")
        print(f"MA10: {ma10:.2f}")
        print(f"MA20: {ma20:.2f}")

        current = realtime['current']
        if current > ma5 > ma10 > ma20:
            print("✅ 完美多头排列")
            ma_status = "多头"
        elif current > ma5 and current > ma10:
            print("✅ 短期多头")
            ma_status = "偏多"
        elif current < ma5 and current < ma10:
            print("❌ 短期空头")
            ma_status = "空头"
        else:
            print("➡️ 均线纠缠")
            ma_status = "中性"

        # 成交量
        vol_ma5 = sum(vols[-5:]) / 5
        vol_ma10 = sum(vols[-10:]) / 10
        vol_ratio = realtime['volume'] / vol_ma5

        print(f"\n2️⃣ 成交量分析")
        print(f"成交量MA5:  {vol_ma5/10000:.0f}万手")
        print(f"成交量MA10: {vol_ma10/10000:.0f}万手")
        print(f"量比:       {vol_ratio:.2f}")

        if vol_ratio > 2:
            print("✅ 放量")
            vol_status = "放量"
        elif vol_ratio > 1.2:
            print("✅ 温和放量")
            vol_status = "温和放量"
        elif vol_ratio < 0.5:
            print("⚠️  严重缩量")
            vol_status = "严重缩量"
        else:
            print("➡️  成交量正常")
            vol_status = "正常"

        # 区间位置
        high_20 = max(closes[-20:])
        low_20 = min(closes[-20:])
        position = (current - low_20) / (high_20 - low_20) * 100 if high_20 != low_20 else 50

        print(f"\n3️⃣ 区间位置")
        print(f"近20日最高: {high_20:.2f}")
        print(f"近20日最低: {low_20:.2f}")
        print(f"当前位置:   {position:.1f}%")

        if position > 80:
            print("✅ 高位")
            pos_status = "高位"
        elif position < 20:
            print("⚠️  低位")
            pos_status = "低位"
        else:
            print("➡️  中位")
            pos_status = "中位"

        # 量价配合
        print(f"\n4️⃣ 量价配合")
        if change_pct > 0 and vol_ratio > 1.2:
            print("✅ 价涨量增 - 健康上涨")
            signal = "看多"
        elif change_pct > 0 and vol_ratio < 0.8:
            print("⚠️  价涨量缩 - 动力不足")
            signal = "谨慎"
        elif change_pct < 0 and vol_ratio > 1.2:
            print("⚠️  价跌量增 - 抛压较大")
            signal = "看空"
        elif change_pct < 0 and vol_ratio < 0.8:
            print("➡️  价跌量缩 - 正常回调")
            signal = "观望"
        else:
            signal = "中性"

        # 综合评分
        print("\n" + "=" * 60)
        print("【综合评分】")
        print("=" * 60)

        score = 0
        if current > ma5: score += 1
        if current > ma10: score += 1
        if current > ma20: score += 1
        if ma5 > ma10: score += 1
        if change_pct > 0: score += 1
        if vol_ratio > 1: score += 1
        if position > 50: score += 1

        print(f"\n技术得分: {score}/7")

        if score >= 6:
            rating = "强烈看多 ⭐⭐⭐⭐⭐"
            action = "积极买入"
        elif score >= 4:
            rating = "偏多 ⭐⭐⭐⭐"
            action = "逢低买入"
        elif score >= 3:
            rating = "中性 ⭐⭐⭐"
            action = "观望等待"
        elif score >= 1:
            rating = "偏空 ⭐⭐"
            action = "减仓或观望"
        else:
            rating = "看空 ⭐"
            action = "空仓或止损"

        print(f"综合评级: {rating}")
        print(f"操作建议: {action}")

        # 操作建议
        print("\n" + "=" * 60)
        print("【操作建议】")
        print("=" * 60)

        print(f"\n当前价: {current:.2f}")
        print(f"止损位: {current * 0.95:.2f} (-5%)")
        print(f"止盈位: {current * 1.10:.2f} (+10%)")

        # 关键价位
        print(f"\n关键价位:")
        print(f"强压力: {high_20:.2f}")
        print(f"强支撑: {low_20:.2f}")

        # 返回分析结果
        return {
            'code': code,
            'name': realtime['name'],
            'current': current,
            'change_pct': change_pct,
            'volume': realtime['volume'],
            'vol_ratio': vol_ratio,
            'ma_status': ma_status,
            'vol_status': vol_status,
            'pos_status': pos_status,
            'signal': signal,
            'score': score,
            'rating': rating,
            'action': action
        }

    return None

def main():
    if len(sys.argv) < 2:
        print("使用方法: python3 track_stock.py <股票代码> [股票名称]")
        print("示例: python3 track_stock.py 600031 三一重工")
        sys.exit(1)

    code = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else None

    result = analyze_stock(code, name)

    if result:
        # 保存结果
        filename = f"/root/.openclaw/workspace/projects/stock-tracking/{code}_latest.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 分析结果已保存: {filename}")

if __name__ == "__main__":
    main()
