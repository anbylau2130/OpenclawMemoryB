#!/bin/bash
# V5实时交易系统 - 快速启动脚本

echo "================================================================"
echo "V5实时交易系统 - 启动"
echo "================================================================"
echo ""

# 进入工作目录
cd /root/.openclaw/workspace/Knowledge/trading-strategies/code

# 检查Python环境
echo "【1/3】检查环境..."
python3 --version || {
    echo "❌ Python3未安装"
    exit 1
}

# 检查依赖
echo ""
echo "【2/3】检查依赖..."
python3 -c "import pandas, numpy" || {
    echo "❌ 缺少依赖库"
    exit 1
}
echo "✅ 依赖正常"

# 检查模块
echo ""
echo "【3/3】检查模块..."
python3 -c "
from concurrent_data_fetcher import ConcurrentDataFetcher
from fast_signal_generator import FastSignalGenerator
from alert_notifier import AlertNotifier
from trading_executor import TradingExecutor
print('✅ 所有模块正常')
" || {
    echo "❌ 模块导入失败"
    exit 1
}

echo ""
echo "================================================================"
echo "启动实时交易系统"
echo "================================================================"
echo ""
echo "监控参数:"
echo "  - 扫描间隔: 60秒"
echo "  - 信号阈值: 4.0"
echo "  - 并发数: 10"
echo "  - 监控股票: 15支"
echo ""
echo "按 Ctrl+C 停止"
echo ""

# 启动系统
python3 realtime_trading_system.py

echo ""
echo "================================================================"
echo "系统已停止"
echo "================================================================"
