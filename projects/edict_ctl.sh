#!/bin/bash
# Edict项目管理脚本

PROJECT_DIR="/root/.openclaw/workspace/projects/edict"

case "$1" in
    start)
        echo "启动Edict服务..."
        sudo systemctl start edict-loop.service
        sudo systemctl start edict-dashboard.service
        echo "✅ 服务已启动"
        ;;
    
    stop)
        echo "停止Edict服务..."
        sudo systemctl stop edict-loop.service
        sudo systemctl stop edict-dashboard.service
        echo "✅ 服务已停止"
        ;;
    
    restart)
        echo "重启Edict服务..."
        sudo systemctl restart edict-loop.service
        sudo systemctl restart edict-dashboard.service
        echo "✅ 服务已重启"
        ;;
    
    status)
        echo "Edict服务状态:"
        echo ""
        echo "【数据刷新服务】"
        sudo systemctl status edict-loop.service --no-pager
        echo ""
        echo "【看板服务】"
        sudo systemctl status edict-dashboard.service --no-pager
        ;;
    
    logs)
        echo "查看Edict日志（Ctrl+C退出）..."
        sudo journalctl -u edict-loop -u edict-dashboard -f
        ;;
    
    enable)
        echo "启用开机自启..."
        sudo systemctl enable edict-loop.service
        sudo systemctl enable edict-dashboard.service
        echo "✅ 已启用开机自启"
        ;;
    
    disable)
        echo "禁用开机自启..."
        sudo systemctl disable edict-loop.service
        sudo systemctl disable edict-dashboard.service
        echo "✅ 已禁用开机自启"
        ;;
    
    install)
        echo "安装Edict项目..."
        if [ -d "$PROJECT_DIR" ]; then
            echo "⚠️  项目已存在"
        else
            mkdir -p /root/.openclaw/workspace/projects
            cd /root/.openclaw/workspace/projects
            git clone https://github.com/cft0808/edict.git
            echo "✅ 项目克隆完成"
        fi
        ;;
    
    deploy)
        echo "完整部署Edict（含开机自启）..."
        bash /root/.openclaw/workspace/projects/deploy_edict.sh
        ;;
    
    *)
        echo "Edict项目管理"
        echo ""
        echo "用法: $0 {start|stop|restart|status|logs|enable|disable|install|deploy}"
        echo ""
        echo "命令:"
        echo "  install - 克隆项目"
        echo "  deploy  - 完整部署（含开机自启）"
        echo "  start   - 启动服务"
        echo "  stop    - 停止服务"
        echo "  restart - 重启服务"
        echo "  status  - 查看状态"
        echo "  logs    - 查看日志"
        echo "  enable  - 启用开机自启"
        echo "  disable - 禁用开机自启"
        exit 1
        ;;
esac

exit 0
