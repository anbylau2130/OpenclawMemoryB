#!/bin/bash
# Edict启动脚本（无systemd版本）

PROJECT_DIR="/root/.openclaw/workspace/projects/edict"
LOG_DIR="/root/.openclaw/workspace/projects/edict/logs"
PID_DIR="/root/.openclaw/workspace/projects/edict"

echo "================================================================"
echo "启动Edict服务"
echo "================================================================"
echo ""

# 创建日志和PID目录
mkdir -p "$LOG_DIR"
mkdir -p "$PID_DIR"

# 检查是否已运行
if [ -f "$PID_DIR/edict-loop.pid" ]; then
    LOOP_PID=$(cat "$PID_DIR/edict-loop.pid")
    if ps -p $LOOP_PID > /dev/null 2>&1; then
        echo "⚠️  数据刷新服务已在运行 (PID: $LOOP_PID)"
    else
        rm -f "$PID_DIR/edict-loop.pid"
    fi
fi

if [ -f "$PID_DIR/edict-dashboard.pid" ]; then
    DASHBOARD_PID=$(cat "$PID_DIR/edict-dashboard.pid")
    if ps -p $DASHBOARD_PID > /dev/null 2>&1; then
        echo "⚠️  看板服务已在运行 (PID: $DASHBOARD_PID)"
    else
        rm -f "$PID_DIR/edict-dashboard.pid"
    fi
fi

# 启动数据刷新服务
echo "【1/2】启动数据刷新服务..."
cd "$PROJECT_DIR"
nohup bash scripts/run_loop.sh > "$LOG_DIR/edict-loop.log" 2>&1 &
LOOP_PID=$!
echo $LOOP_PID > "$PID_DIR/edict-loop.pid"
echo "✅ 数据刷新服务已启动 (PID: $LOOP_PID)"

# 启动看板服务
echo ""
echo "【2/2】启动看板服务..."
cd "$PROJECT_DIR"
nohup python3 dashboard/server.py > "$LOG_DIR/edict-dashboard.log" 2>&1 &
DASHBOARD_PID=$!
echo $DASHBOARD_PID > "$PID_DIR/edict-dashboard.pid"
echo "✅ 看板服务已启动 (PID: $DASHBOARD_PID)"

# 等待服务启动
echo ""
echo "等待服务启动..."
sleep 3

# 检查服务状态
echo ""
echo "【服务状态】"
if ps -p $LOOP_PID > /dev/null 2>&1; then
    echo "✅ 数据刷新服务运行中 (PID: $LOOP_PID)"
else
    echo "❌ 数据刷新服务启动失败"
fi

if ps -p $DASHBOARD_PID > /dev/null 2>&1; then
    echo "✅ 看板服务运行中 (PID: $DASHBOARD_PID)"
    echo ""
    echo "================================================================"
    echo "✅ Edict服务启动完成！"
    echo "================================================================"
    echo ""
    echo "访问看板: http://127.0.0.1:7891"
    echo ""
    echo "管理命令:"
    echo "  查看状态: bash $PROJECT_DIR/edict_status.sh"
    echo "  停止服务: bash $PROJECT_DIR/edict_stop.sh"
    echo "  查看日志: tail -f $LOG_DIR/edict-*.log"
    echo "================================================================"
else
    echo "❌ 看板服务启动失败"
    echo ""
    echo "查看错误日志:"
    echo "  tail -n 50 $LOG_DIR/edict-dashboard.log"
fi
