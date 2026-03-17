#!/bin/bash
# Edict项目完整部署脚本
# 包含：安装 + 开机自启配置

set -e

PROJECT_DIR="/root/.openclaw/workspace/projects/edict"

echo "================================================================"
echo "Edict项目部署 - 完整版（含开机自启）"
echo "================================================================"
echo ""

# 1. 检查OpenClaw
echo "【1/6】检查OpenClaw环境..."
if ! command -v openclaw &> /dev/null; then
    echo "❌ OpenClaw未安装"
    exit 1
fi
echo "✅ OpenClaw已安装"

# 2. 克隆项目
echo ""
echo "【2/6】克隆Edict项目..."
if [ -d "$PROJECT_DIR" ]; then
    echo "⚠️  项目已存在，跳过克隆"
else
    mkdir -p /root/.openclaw/workspace/projects
    cd /root/.openclaw/workspace/projects
    git clone https://github.com/cft0808/edict.git
    echo "✅ 项目克隆完成"
fi

# 3. 安装
echo ""
echo "【3/6】安装Edict（配置Agent）..."
cd "$PROJECT_DIR"
if [ ! -f "install.sh" ]; then
    echo "❌ install.sh不存在"
    exit 1
fi
chmod +x install.sh
./install.sh
echo "✅ 安装完成"

# 4. 配置API Key（提醒）
echo ""
echo "【4/6】API Key配置..."
if ! grep -q "api_key" ~/.openclaw/agents/taizi/openclaw.json 2>/dev/null; then
    echo "⚠️  需要配置API Key"
    echo ""
    echo "请运行以下命令配置："
    echo "  openclaw agents add taizi"
    echo "  # 输入您的API Key"
    echo "  cd $PROJECT_DIR"
    echo "  ./install.sh  # 重新运行以同步API Key"
    echo ""
    echo "配置完成后，重新运行此脚本："
    echo "  bash $0"
    exit 0
fi
echo "✅ API Key已配置"

# 5. 安装systemd服务
echo ""
echo "【5/6】配置开机自启..."

# 服务文件路径
SERVICE_DIR="/root/.openclaw/workspace/docs"
LOOP_SERVICE="$SERVICE_DIR/edict-loop.service"
DASHBOARD_SERVICE="$SERVICE_DIR/edict-dashboard.service"

# 检查服务文件
if [ ! -f "$LOOP_SERVICE" ] || [ ! -f "$DASHBOARD_SERVICE" ]; then
    echo "❌ 服务文件不存在，请检查 $SERVICE_DIR"
    exit 1
fi

# 复制服务文件（root用户不需要sudo）
cp "$LOOP_SERVICE" /etc/systemd/system/
cp "$DASHBOARD_SERVICE" /etc/systemd/system/

# 重载systemd
systemctl daemon-reload

# 启用服务
systemctl enable edict-loop.service
systemctl enable edict-dashboard.service

echo "✅ 开机自启已配置"

# 6. 启动服务
echo ""
echo "【6/6】启动服务..."
sudo systemctl start edict-loop.service
sudo systemctl start edict-dashboard.service

# 等待服务启动
sleep 3

# 检查状态
if sudo systemctl is-active --quiet edict-loop.service; then
    echo "✅ 数据刷新服务已启动"
else
    echo "❌ 数据刷新服务启动失败"
    sudo systemctl status edict-loop.service
fi

if sudo systemctl is-active --quiet edict-dashboard.service; then
    echo "✅ 看板服务已启动"
else
    echo "❌ 看板服务启动失败"
    sudo systemctl status edict-dashboard.service
fi

# 完成
echo ""
echo "================================================================"
echo "✅ 部署完成！"
echo "================================================================"
echo ""
echo "访问看板: http://127.0.0.1:7891"
echo ""
echo "管理命令:"
echo "  查看状态: sudo systemctl status edict-loop edict-dashboard"
echo "  停止服务: sudo systemctl stop edict-loop edict-dashboard"
echo "  重启服务: sudo systemctl restart edict-loop edict-dashboard"
echo "  查看日志: sudo journalctl -u edict-loop -u edict-dashboard -f"
echo ""
echo "开机自启: ✅ 已启用"
echo "================================================================"
