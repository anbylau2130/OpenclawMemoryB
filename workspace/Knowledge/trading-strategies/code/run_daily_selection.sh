#!/bin/bash
# 每日选股任务 - V5真实数据版
# 执行时间: 每天8:00

cd /root/.openclaw/workspace/Knowledge/trading-strategies/code

LOG_FILE="/root/.openclaw/workspace/data/backtest/selection_$(date +%Y%m%d).log"

echo "========================================" >> $LOG_FILE
echo "选股任务开始: $(date '+%Y-%m-%d %H:%M:%S')" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# 运行选股
python3 stock_selector_v5_real.py >> $LOG_FILE 2>&1

echo "选股任务完成: $(date '+%Y-%m-%d %H:%M:%S')" >> $LOG_FILE
echo "" >> $LOG_FILE
