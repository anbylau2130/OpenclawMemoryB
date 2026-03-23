#!/bin/bash
# PM2 服务监控守护进程
# 每分钟检查一次 Dashboard，如果不可访问则自动恢复

LOG_FILE="/root/.openclaw/workspace/logs/pm2-watchdog.log"
LOG_DIR=$(dirname "$LOG_FILE")
CHECK_INTERVAL=60  # 检查间隔（秒）

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== PM2 Watchdog 启动 ==="

while true; do
    # 检查 Dashboard 是否可访问
    if ! curl -s -f http://localhost:18795 > /dev/null 2>&1; then
        log "⚠️ Dashboard 不可访问，正在恢复..."
        
        # 检查 PM2 是否有进程运行
        PM2_ONLINE=$(pm2 list 2>/dev/null | grep -c "online" || echo "0")
        
        if [ "$PM2_ONLINE" -eq 0 ]; then
            # 尝试从保存的配置恢复
            if [ -f "/root/.pm2/dump.pm2" ]; then
                pm2 resurrect >> "$LOG_FILE" 2>&1
                log "✅ 已从 dump.pm2 恢复"
            else
                # 手动启动
                cd /root/clawd/gui/server
                if [ -f "package.json" ]; then
                    pm2 start package.json >> "$LOG_FILE" 2>&1
                    pm2 save >> "$LOG_FILE" 2>&1
                    log "✅ 已手动启动 Dashboard"
                fi
            fi
        fi
        
        # 等待服务启动
        sleep 5
        
        # 验证是否恢复成功
        if curl -s -f http://localhost:18795 > /dev/null 2>&1; then
            log "✅ Dashboard 已恢复"
        else
            log "❌ Dashboard 恢复失败"
        fi
    fi
    
    sleep $CHECK_INTERVAL
done
