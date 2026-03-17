#!/bin/bash
# Edict服务启动脚本（正确绑定地址）

PROJECT_DIR="/root/.openclaw/workspace/projects/edict"
LOG_DIR="$PROJECT_DIR/logs"

echo "================================================================"
echo "Edict服务启动"
echo "================================================================"
echo ""

# 创建日志目录
mkdir -p "$LOG_DIR"

# 停止旧进程
echo "【1/4】停止旧进程..."
pkill -f "server.py" 2>/dev/null
pkill -f "run_loop.sh" 2>/dev/null
sleep 2
echo "✅ 旧进程已停止"

# 启动看板服务（绑定0.0.0.0，允许外部访问）
echo ""
echo "【2/4】启动看板服务..."
cd "$PROJECT_DIR/dashboard"
nohup python3 server.py --host 0.0.0.0 --port 7891 > "$LOG_DIR/dashboard.log" 2>&1 &
DASHBOARD_PID=$!
echo "✅ 看板服务已启动 (PID: $DASHBOARD_PID)"
echo "   访问地址: http://0.0.0.0:7891"

# 启动数据刷新服务
echo ""
echo "【3/4】启动数据刷新服务..."
cd "$PROJECT_DIR"
nohup bash scripts/run_loop.sh > "$LOG_DIR/loop.log" 2>&1 &
LOOP_PID=$!
echo "✅ 数据刷新服务已启动 (PID: $LOOP_PID)"

# 等待服务启动
echo ""
echo "【4/4】验证服务..."
sleep 3

# 检查进程
if ps -p $DASHBOARD_PID > /dev/null 2>&1; then
    echo "✅ 看板服务运行中"
else
    echo "❌ 看板服务启动失败"
    tail -20 "$LOG_DIR/dashboard.log"
fi

if ps -p $LOOP_PID > /dev/null 2>&1; then
    echo "✅ 数据刷新服务运行中"
else
    echo "❌ 数据刷新服务启动失败"
fi

# 测试访问
echo ""
echo "================================================================"
echo "测试访问"
echo "================================================================"
sleep 2
curl -I http://127.0.0.1:7891 2>&1 | head -5

echo ""
echo "================================================================"
echo "✅ Edict服务启动完成"
echo "================================================================"
echo ""
echo "访问地址:"
echo "  本地: http://127.0.0.1:7891"
echo "  局域网: http://$(hostname -I | awk '{print $1}'):7891"
echo ""
echo "管理命令:"
echo "  查看状态: ps aux | grep -E 'server.py|run_loop'"
echo "  查看日志: tail -f $LOG_DIR/dashboard.log"
echo "  停止服务: pkill -f 'server.py|run_loop'"
echo "================================================================"
