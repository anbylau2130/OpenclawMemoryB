#!/bin/bash
# PM2 自动恢复脚本
# 用于容器重启后自动启动 PM2 服务

LOG_FILE="/root/.openclaw/workspace/logs/pm2-auto-restart.log"
LOG_DIR=$(dirname "$LOG_FILE")

# 创建日志目录
mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== PM2 自动恢复脚本启动 ==="

# 1. 检查 PM2 是否已安装
if ! command -v pm2 &> /dev/null; then
    log "❌ PM2 未安装"
    exit 1
fi

# 2. 检查 PM2 是否已有进程运行
PM2_RUNNING=$(pm2 list 2>/dev/null | grep -c "online" || echo "0")

if [ "$PM2_RUNNING" -gt 0 ]; then
    log "✅ PM2 已有 $PM2_RUNNING 个进程运行"
    exit 0
fi

# 3. 恢复 PM2 服务
log "正在恢复 PM2 服务..."

# 方案A：从保存的配置恢复
if [ -f "/root/.pm2/dump.pm2" ]; then
    pm2 resurrect 2>&1 | tee -a "$LOG_FILE"
    log "✅ 已从 dump.pm2 恢复"
fi

# 方案B：如果恢复失败，手动启动 Dashboard
if [ $(pm2 list 2>/dev/null | grep -c "online" || echo "0") -eq 0 ]; then
    log "手动启动 Dashboard..."
    cd /root/clawd/gui/server
    
    if [ -f "package.json" ]; then
        pm2 start package.json 2>&1 | tee -a "$LOG_FILE"
        pm2 save 2>&1 | tee -a "$LOG_FILE"
        log "✅ Dashboard 已启动"
    else
        log "❌ 未找到 /root/clawd/gui/server/package.json"
        exit 1
    fi
fi

# 4. 验证服务状态
sleep 3
ONLINE_COUNT=$(pm2 list 2>/dev/null | grep -c "online" || echo "0")
log "✅ PM2 服务已恢复，当前 $ONLINE_COUNT 个进程在线"

# 5. 验证 Dashboard 可访问
if curl -s http://localhost:18795 > /dev/null 2>&1; then
    log "✅ Dashboard (18795) 可访问"
else
    log "⚠️ Dashboard (18795) 不可访问"
fi

log "=== PM2 自动恢复完成 ==="
