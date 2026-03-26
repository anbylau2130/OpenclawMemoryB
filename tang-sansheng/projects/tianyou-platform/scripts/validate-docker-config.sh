#!/bin/bash

# ========================================
# Docker配置验证脚本
# ========================================

set -e

echo "========================================"
echo "Docker配置验证"
echo "========================================"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查函数
check_file() {
    local file=$1
    local description=$2
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description: $file"
        return 0
    else
        echo -e "${RED}✗${NC} $description: $file (缺失)"
        return 1
    fi
}

# 检查必要文件
echo ""
echo "检查必要文件..."
errors=0

check_file "docker-compose.yml" "Docker Compose配置" || ((errors++))
check_file ".env.example" "环境变量示例" || ((errors++))
check_file "backend/.dockerignore" "后端Docker忽略文件" || ((errors++))
check_file "backend/src/Tianyou.Api/Dockerfile" "后端API Dockerfile" || ((errors++))
check_file "frontend/Tianyou.Web/.dockerignore" "前端Docker忽略文件" || ((errors++))
check_file "frontend/Tianyou.Web/Dockerfile" "前端Web Dockerfile" || ((errors++))
check_file "frontend/Tianyou.Web/nginx.conf" "Nginx配置" || ((errors++))
check_file "DOCKER_DEPLOYMENT.md" "部署文档" || ((errors++))

echo ""
echo "========================================"

if [ $errors -eq 0 ]; then
    echo -e "${GREEN}所有配置文件检查通过！${NC}"
    echo ""
    echo "下一步操作："
    echo "1. 复制环境变量配置: cp .env.example .env"
    echo "2. 编辑配置文件: vim .env"
    echo "3. 构建镜像: docker compose build"
    echo "4. 启动服务: docker compose up -d"
    exit 0
else
    echo -e "${RED}发现 $errors 个错误，请检查！${NC}"
    exit 1
fi
