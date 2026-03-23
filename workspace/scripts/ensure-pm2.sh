#!/bin/bash
# 确保 PM2 服务运行（用于 cron 定期检查）

# 检查 Dashboard 是否可访问
if ! curl -s http://localhost:18795 > /dev/null 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Dashboard 不可访问，正在恢复..."
    /root/.openclaw/workspace/scripts/pm2-auto-restart.sh
fi
