#!/usr/bin/env python3
"""
多因子策略真实数据回测
===========================
使用AKShare获取真实历史数据
回测上证50成分股的选股策略效果
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import time
import random

# 上证50成分股代码（从akshare获取）
def get_sse50_stocks():
    """获取上证50成分股"""
    try:
        df = ak.index_stock_cons_weight_csindex(symbol="000016")
        # 提取股票代码
        codes = df['成分券代码'].tolist() if '成分券代码' in df.columns else []
        if not codes:
            # 备用：手动列表
            codes = [
                "600036", "601318", "601166", "600000", "601398",
                "601288", "601939", "601988", "600030", "601211",
                "601857", "600028", "601088", "600019", "600031",
                "601766", "600104", "601390", "600519", "000858",
                "600887", "600276", "000333", "000651", "002415",
                "600009", "600011", "600015", "600016", "600018",
                "600048", "600050", "600309", "600585", "600690",
                "600703", "600809", "600837", "600900", "601012",
                "601066", "601111", "601225", "601238", "601328",
                "601336", "601601", "601628", "601668", "601688"
            ]
        return codes
    except Exception as e:
        print(f"获取成分股失败: {e}")
        return []

def get_stock_history(code, start_date, end_date):
    """获取股票历史数据（带重试）"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(1, 2))  # 随机延时避免被限制
            df = ak.stock_zh_a_hist(
                symbol=code, 
                period="daily", 
                start_date=start_date, 
                end_date=end_date, 
                adjust="qfq"  # 前复权
            )
            if df.empty:
                return None
            df['code'] = code
            return df
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3)  # 失败后等待更长时间
                continue
            print(f"  {code} 数据获取失败: {e}")
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
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = df['收盘'].ewm(span=12).mean()
    ema26 = df['收盘'].ewm(span=26).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_SIGNAL'] = df['MACD'].ewm(span=9).mean()
    df['MACD_HIST'] = df['MACD'] - df['MACD_SIGNAL']
    
    # 涨跌幅
    df['PCT_CHANGE'] = df['收盘'].pct_change()
    
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
    """
    回测策略
    - 买入条件：多因子得分 >= min_score
    - 卖出条件：持有hold_days天 或 止损/止盈
    """
    if df is None or len(df) < 100:
        return None
    
    trades = []
    position = None
    
    for i in range(60, len(df)):
        row = df.iloc[i]
        
        # 无持仓时，检查买入信号
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
            # 有持仓，检查卖出条件
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

def run_backtest(start_date="20250101", end_date="20260317", min_score=4):
    """运行完整回测"""
    print(f"开始回测: {start_date} ~ {end_date}")
    print(f"买入条件: 多因子得分 >= {min_score}")
    print("="*60)
    
    # 获取股票列表
    codes = get_sse50_stocks()
    print(f"股票池: 上证50 ({len(codes)}支)")
    
    all_trades = []
    success_count = 0
    
    for i, code in enumerate(codes[:5]):  # 限制5支避免超时
        print(f"[{i+1}/{min(len(codes),20)}] 获取 {code}...", end=" ")
        
        df = get_stock_history(code, start_date, end_date)
        if df is None:
            print("失败")
            continue
        
        df = calculate_indicators(df)
        if df is None:
            print("指标计算失败")
            continue
        
        df = calculate_factors(df)
        if df is None:
            print("因子计算失败")
            continue
        
        trades = backtest_strategy(df, code, min_score=min_score)
        if trades:
            all_trades.extend(trades)
            success_count += 1
            print(f"OK ({len(trades)}笔交易)")
        else:
            print("OK (无交易)")
    
    print("="*60)
    print(f"成功获取: {success_count}/{min(len(codes),5)} 支")
    
    return all_trades

def analyze_results(trades):
    """分析回测结果"""
    if not trades:
        print("无交易记录")
        return
    
    df = pd.DataFrame(trades)
    
    print("\n" + "="*60)
    print("回测结果分析")
    print("="*60)
    
    # 基本统计
    print(f"\n总交易次数: {len(df)}")
    print(f"盈利次数: {len(df[df['pnl_pct'] > 0])}")
    print(f"亏损次数: {len(df[df['pnl_pct'] <= 0])}")
    
    win_rate = len(df[df['pnl_pct'] > 0]) / len(df) * 100
    print(f"胜率: {win_rate:.1f}%")
    
    avg_pnl = df['pnl_pct'].mean()
    print(f"平均收益: {avg_pnl:.2f}%")
    
    avg_win = df[df['pnl_pct'] > 0]['pnl_pct'].mean() if len(df[df['pnl_pct'] > 0]) > 0 else 0
    avg_loss = df[df['pnl_pct'] <= 0]['pnl_pct'].mean() if len(df[df['pnl_pct'] <= 0]) > 0 else 0
    print(f"平均盈利: {avg_win:.2f}%")
    print(f"平均亏损: {avg_loss:.2f}%")
    
    total_return = df['pnl_pct'].sum()
    print(f"累计收益: {total_return:.2f}%")
    
    # 按卖出原因分析
    print("\n按卖出原因分类:")
    for reason in df['sell_reason'].unique():
        subset = df[df['sell_reason'] == reason]
        r_win = len(subset[subset['pnl_pct'] > 0]) / len(subset) * 100 if len(subset) > 0 else 0
        print(f"  {reason}: {len(subset)}笔, 胜率{r_win:.0f}%, 平均{subset['pnl_pct'].mean():.2f}%")
    
    # Top 10 最佳交易
    print("\nTop 10 最佳交易:")
    top10 = df.nlargest(10, 'pnl_pct')[['code', 'buy_date', 'sell_date', 'pnl_pct', 'signals']]
    for _, row in top10.iterrows():
        print(f"  {row['code']} {row['buy_date']}→{row['sell_date']} +{row['pnl_pct']:.1f}% | {row['signals'][:30]}")
    
    # Top 10 最差交易
    print("\nTop 10 最差交易:")
    worst10 = df.nsmallest(10, 'pnl_pct')[['code', 'buy_date', 'sell_date', 'pnl_pct', 'signals']]
    for _, row in worst10.iterrows():
        print(f"  {row['code']} {row['buy_date']}→{row['sell_date']} {row['pnl_pct']:.1f}% | {row['signals'][:30]}")
    
    return df

if __name__ == "__main__":
    # 运行回测
    trades = run_backtest(
        start_date="20250101",
        end_date="20260317",
        min_score=4
    )
    
    # 分析结果
    df = analyze_results(trades)
    
    # 保存结果
    if trades:
        output_path = "/root/.openclaw/workspace/Knowledge/trading-strategies/backtest/backtest_real_data_results.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(trades, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存: {output_path}")
