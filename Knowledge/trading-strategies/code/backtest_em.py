#!/usr/bin/env python3
"""
多因子策略回测 - 东方财富数据源
使用东方财富API直接获取数据
"""

import requests
import pandas as pd
import numpy as np
import json
import time
from datetime import datetime

# 东方财富API
def get_stock_history_em(code, start_date="20250101", end_date="20260317"):
    """从东方财富获取股票历史数据"""
    # 转换代码格式
    if code.startswith('6'):
        secid = f"1.{code}"
    else:
        secid = f"0.{code}"
    
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "secid": secid,
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "klt": "101",  # 日线
        "fqt": "1",    # 前复权
        "beg": start_date,
        "end": end_date,
        "ut": "fa5fd1943c7b386f172d6893dbfba10b"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://quote.eastmoney.com/"
    }
    
    try:
        time.sleep(0.5)  # 避免请求过快
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        data = resp.json()
        
        if data.get("data") and data["data"].get("klines"):
            klines = data["data"]["klines"]
            rows = []
            for kline in klines:
                parts = kline.split(",")
                rows.append({
                    "日期": parts[0],
                    "开盘": float(parts[1]),
                    "收盘": float(parts[2]),
                    "最高": float(parts[3]),
                    "最低": float(parts[4]),
                    "成交量": float(parts[5]),
                    "成交额": float(parts[6]),
                    "振幅": float(parts[7]),
                    "涨跌幅": float(parts[8]),
                    "涨跌额": float(parts[9]),
                    "换手率": float(parts[10])
                })
            df = pd.DataFrame(rows)
            df['code'] = code
            return df
        return None
    except Exception as e:
        print(f"  {code} 获取失败: {e}")
        return None

def calculate_indicators(df):
    """计算技术指标"""
    if df is None or len(df) < 60:
        return None
    
    df = df.copy()
    
    # 均线
    df['MA5'] = df['收盘'].rolling(5).mean()
    df['MA10'] = df['收盘'].rolling(10).mean()
    df['MA20'] = df['收盘'].rolling(20).mean()
    df['MA60'] = df['收盘'].rolling(60).mean()
    
    # 成交量均线
    df['VOL_MA5'] = df['成交量'].rolling(5).mean()
    df['VOL_MA20'] = df['成交量'].rolling(20).mean()
    
    # 量比
    df['VOL_RATIO'] = df['成交量'] / df['VOL_MA20']
    
    # RSI
    delta = df['收盘'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss.replace(0, 0.001)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = df['收盘'].ewm(span=12).mean()
    ema26 = df['收盘'].ewm(span=26).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_SIGNAL'] = df['MACD'].ewm(span=9).mean()
    df['MACD_HIST'] = df['MACD'] - df['MACD_SIGNAL']
    
    # 高低点
    df['HIGH_20'] = df['最高'].rolling(20).max()
    df['LOW_20'] = df['最低'].rolling(20).min()
    
    return df

def calculate_factors(df):
    """计算多因子得分"""
    if df is None or len(df) < 60:
        return None
    
    df = df.copy()
    df['SCORE'] = 0
    df['SIGNALS'] = [[] for _ in range(len(df))]
    
    for i in range(60, len(df)):
        score = 0
        signals = []
        row = df.iloc[i]
        prev = df.iloc[i-1]
        
        # 1. 均线多头排列 (+2)
        if row['MA5'] > row['MA10'] > row['MA20']:
            score += 2
            signals.append("均线多头")
        
        # 2. 站上MA5 (+1)
        if row['收盘'] > row['MA5']:
            score += 1
            signals.append("站上MA5")
        
        # 3. 放量 (+1)
        if row['VOL_RATIO'] > 1.5:
            score += 1
            signals.append(f"放量({row['VOL_RATIO']:.1f})")
        
        # 4. MACD金叉 (+1)
        if row['MACD'] > row['MACD_SIGNAL'] and prev['MACD'] <= prev['MACD_SIGNAL']:
            score += 1
            signals.append("MACD金叉")
        
        # 5. RSI超卖 (+1)
        if row['RSI'] < 30:
            score += 1
            signals.append(f"RSI超卖({row['RSI']:.0f})")
        
        # 6. 突破20日高点 (+1)
        if row['收盘'] >= row['HIGH_20'] * 0.98:
            score += 1
            signals.append("突破高点")
        
        df.iloc[i, df.columns.get_loc('SCORE')] = score
        df.iloc[i, df.columns.get_loc('SIGNALS')] = signals
    
    return df

def backtest_strategy(df, code, min_score=4, hold_days=5, stop_loss=-0.05, take_profit=0.08):
    """回测策略"""
    if df is None or len(df) < 100:
        return None
    
    trades = []
    position = None
    
    for i in range(60, len(df)):
        row = df.iloc[i]
        
        if position is None:
            if row['SCORE'] >= min_score:
                position = {
                    'buy_date': row['日期'],
                    'buy_price': row['收盘'],
                    'score': row['SCORE'],
                    'signals': row['SIGNALS'],
                    'buy_idx': i
                }
        else:
            hold_day = i - position['buy_idx']
            pnl_pct = (row['收盘'] - position['buy_price']) / position['buy_price']
            
            sell_reason = None
            if hold_day >= hold_days:
                sell_reason = "到期"
            elif pnl_pct <= stop_loss:
                sell_reason = "止损"
            elif pnl_pct >= take_profit:
                sell_reason = "止盈"
            
            if sell_reason:
                trades.append({
                    'code': code,
                    'buy_date': position['buy_date'],
                    'sell_date': row['日期'],
                    'buy_price': position['buy_price'],
                    'sell_price': row['收盘'],
                    'hold_days': hold_day,
                    'pnl_pct': pnl_pct * 100,
                    'score': position['SCORE'],
                    'signals': ', '.join(position['signals'][:3]),
                    'sell_reason': sell_reason
                })
                position = None
    
    return trades

# 上证50部分成分股
TEST_STOCKS = [
    "600031",  # 三一重工
    "600036",  # 招商银行
    "601318",  # 中国平安
    "600519",  # 贵州茅台
    "601398",  # 工商银行
    "600000",  # 浦发银行
    "601288",  # 农业银行
    "601939",  # 建设银行
    "600030",  # 中信证券
    "601088",  # 中国神华
]

def run_backtest(stocks=TEST_STOCKS, start_date="20250101", end_date="20260317", min_score=4):
    """运行回测"""
    print(f"开始回测: {start_date} ~ {end_date}")
    print(f"买入条件: 多因子得分 >= {min_score}")
    print(f"股票池: {len(stocks)} 支")
    print("="*60)
    
    all_trades = []
    success_count = 0
    
    for i, code in enumerate(stocks):
        print(f"[{i+1}/{len(stocks)}] 获取 {code}...", end=" ", flush=True)
        
        df = get_stock_history_em(code, start_date, end_date)
        if df is None:
            print("失败")
            continue
        
        df = calculate_indicators(df)
        df = calculate_factors(df)
        
        trades = backtest_strategy(df, code, min_score=min_score)
        if trades:
            all_trades.extend(trades)
            success_count += 1
            print(f"OK ({len(trades)}笔)")
        else:
            print("OK (无交易)")
    
    print("="*60)
    print(f"成功: {success_count}/{len(stocks)} 支")
    
    return all_trades

def analyze_results(trades):
    """分析结果"""
    if not trades:
        print("无交易记录")
        return None
    
    df = pd.DataFrame(trades)
    
    print("\n" + "="*60)
    print("📊 回测结果分析")
    print("="*60)
    
    print(f"\n总交易: {len(df)} 笔")
    print(f"盈利: {len(df[df['pnl_pct'] > 0])} 笔")
    print(f"亏损: {len(df[df['pnl_pct'] <= 0])} 笔")
    
    win_rate = len(df[df['pnl_pct'] > 0]) / len(df) * 100
    print(f"\n✅ 胜率: {win_rate:.1f}%")
    
    avg_pnl = df['pnl_pct'].mean()
    print(f"📈 平均收益: {avg_pnl:.2f}%")
    
    avg_win = df[df['pnl_pct'] > 0]['pnl_pct'].mean() if len(df[df['pnl_pct'] > 0]) > 0 else 0
    avg_loss = df[df['pnl_pct'] <= 0]['pnl_pct'].mean() if len(df[df['pnl_pct'] <= 0]) > 0 else 0
    print(f"平均盈利: +{avg_win:.2f}%")
    print(f"平均亏损: {avg_loss:.2f}%")
    
    total = df['pnl_pct'].sum()
    print(f"\n💰 累计收益: {total:.2f}%")
    
    # 盈亏比
    if avg_loss != 0:
        profit_loss_ratio = abs(avg_win / avg_loss)
        print(f"盈亏比: {profit_loss_ratio:.2f}")
    
    print("\n按卖出原因:")
    for reason in df['sell_reason'].unique():
        subset = df[df['sell_reason'] == reason]
        r_win = len(subset[subset['pnl_pct'] > 0]) / len(subset) * 100 if len(subset) > 0 else 0
        print(f"  {reason}: {len(subset)}笔, 胜率{r_win:.0f}%, 平均{subset['pnl_pct'].mean():.2f}%")
    
    print("\n🏆 Top 5 最佳:")
    for _, row in df.nlargest(5, 'pnl_pct').iterrows():
        print(f"  {row['code']} {row['buy_date']}→{row['sell_date']} +{row['pnl_pct']:.1f}%")
    
    print("\n📉 Top 5 最差:")
    for _, row in df.nsmallest(5, 'pnl_pct').iterrows():
        print(f"  {row['code']} {row['buy_date']}→{row['sell_date']} {row['pnl_pct']:.1f}%")
    
    return df

if __name__ == "__main__":
    trades = run_backtest(min_score=4)
    df = analyze_results(trades)
    
    if trades:
        output = "/root/.openclaw/workspace/Knowledge/trading-strategies/backtest/backtest_em_results.json"
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(trades, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存: {output}")
