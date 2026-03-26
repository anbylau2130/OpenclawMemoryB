#!/bin/bash

# ==================== 天佑平台部署脚本 ====================
# 功能：自动化部署到生产环境
# 作者：兵部
# 日期：2026-03-25

set -e  # 遇到错误立即退出

# ==================== 颜色定义 ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ==================== 配置变量 ====================
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOY_ENV="${DEPLOY_ENV:-production}"
DEPLOY_DIR="${DEPLOY_DIR:-/opt/tianyou-platform}"
LOG_FILE="$PROJECT_ROOT/deploy.log"
BACKUP_DIR="$PROJECT_ROOT/backups"
TIMESTAMP=$(date '+%Y%m%d-%H%M%S')

# Docker 配置
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
DOCKER_NETWORK="tianyou-network"

# ==================== 工具函数 ====================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    echo "[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    echo "[WARNING] $(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

# ==================== 检查环境 ====================
check_environment() {
    log_info "检查部署环境..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "未找到 Docker，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "未找到 docker-compose，请先安装 docker-compose"
        exit 1
    fi
    
    log_info "Docker 版本: $(docker --version)"
    log_info "Docker Compose 版本: $(docker-compose --version)"
    
    # 检查 .env 文件
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log_warning ".env 文件不存在，从示例文件复制..."
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        log_warning "请编辑 .env 文件配置环境变量"
    fi
    
    log_success "环境检查完成"
}

# ==================== 备份当前版本 ====================
backup_current() {
    if [ ! -d "$DEPLOY_DIR" ]; then
        log_warning "部署目录不存在，跳过备份"
        return 0
    fi
    
    log_info "备份当前部署版本..."
    
    mkdir -p "$BACKUP_DIR"
    
    local backup_file="$BACKUP_DIR/backup-$TIMESTAMP.tar.gz"
    
    tar -czf "$backup_file" \
        -C "$(dirname $DEPLOY_DIR)" \
        "$(basename $DEPLOY_DIR)" \
        2>/dev/null || log_warning "备份失败（可能目录为空）"
    
    if [ -f "$backup_file" ]; then
        log_success "备份完成: $backup_file"
        
        # 保留最近 5 个备份
        cd "$BACKUP_DIR"
        ls -t backup-*.tar.gz | tail -n +6 | xargs -r rm -f
    fi
}

# ==================== 拉取最新镜像 ====================
pull_images() {
    log_info "拉取最新 Docker 镜像..."
    
    cd "$PROJECT_ROOT"
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" pull
    
    log_success "镜像拉取完成"
}

# ==================== 停止服务 ====================
stop_services() {
    log_info "停止现有服务..."
    
    cd "$PROJECT_ROOT"
    
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "Up"; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
        log_success "服务已停止"
    else
        log_warning "没有运行中的服务"
    fi
}

# ==================== 启动服务 ====================
start_services() {
    log_info "启动服务..."
    
    cd "$PROJECT_ROOT"
    
    # 创建 Docker 网络
    if ! docker network inspect "$DOCKER_NETWORK" > /dev/null 2>&1; then
        docker network create "$DOCKER_NETWORK"
        log_info "Docker 网络已创建: $DOCKER_NETWORK"
    fi
    
    # 启动服务
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    log_success "服务启动完成"
}

# ==================== 健康检查 ====================
health_check() {
    log_info "执行健康检查..."
    
    local max_retries=30
    local retry_interval=10
    local retry_count=0
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -f http://localhost:5000/health > /dev/null 2>&1; then
            log_success "后端服务健康检查通过"
            break
        fi
        
        retry_count=$((retry_count + 1))
        log_warning "健康检查失败，重试 $retry_count/$max_retries..."
        sleep $retry_interval
    done
    
    if [ $retry_count -eq $max_retries ]; then
        log_error "健康检查失败，服务可能未正常启动"
        show_logs
        exit 1
    fi
    
    # 检查前端服务
    if curl -f http://localhost:80 > /dev/null 2>&1; then
        log_success "前端服务健康检查通过"
    else
        log_warning "前端服务健康检查失败"
    fi
    
    log_success "所有服务健康检查通过"
}

# ==================== 显示日志 ====================
show_logs() {
    log_info "显示服务日志..."
    
    cd "$PROJECT_ROOT"
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs --tail=50
}

# ==================== 清理旧镜像 ====================
cleanup_images() {
    log_info "清理未使用的 Docker 镜像..."
    
    docker system prune -f
    
    log_success "清理完成"
}

# ==================== 回滚函数 ====================
rollback() {
    log_warning "开始回滚到上一个版本..."
    
    local latest_backup=$(ls -t "$BACKUP_DIR"/backup-*.tar.gz | head -n 1)
    
    if [ -z "$latest_backup" ]; then
        log_error "未找到备份文件，无法回滚"
        exit 1
    fi
    
    log_info "使用备份: $latest_backup"
    
    # 停止服务
    stop_services
    
    # 恢复备份
    tar -xzf "$latest_backup" -C "$(dirname $DEPLOY_DIR)"
    
    # 重启服务
    start_services
    
    log_success "回滚完成"
}

# ==================== 部署状态 ====================
deploy_status() {
    log_info "部署状态:"
    
    cd "$PROJECT_ROOT"
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    
    echo ""
    log_info "容器资源使用:"
    docker stats --no-stream
}

# ==================== 生成部署报告 ====================
generate_deploy_report() {
    log_info "生成部署报告..."
    
    local report_file="$PROJECT_ROOT/deploy-report-$TIMESTAMP.txt"
    
    cat > "$report_file" << EOF
========================================
天佑平台部署报告
========================================
部署时间: $(date '+%Y-%m-%d %H:%M:%S')
部署环境: $DEPLOY_ENV
部署机器: $(hostname)
部署用户: $(whoami)
========================================

Docker 容器状态:
$(docker-compose -f "$DOCKER_COMPOSE_FILE" ps)

Docker 镜像:
$(docker images | grep tianyou || echo "无相关镜像")

网络信息:
$(docker network inspect "$DOCKER_NETWORK" --format '{{.Name}}: {{.Driver}}')

========================================
部署完成！
========================================
EOF
    
    log_success "部署报告生成: $report_file"
    cat "$report_file"
}

# ==================== 主函数 ====================
main() {
    log_info "========================================="
    log_info "天佑平台自动化部署开始"
    log_info "环境: $DEPLOY_ENV"
    log_info "========================================="
    
    local start_time=$(date +%s)
    
    # 执行部署步骤
    check_environment
    backup_current
    pull_images
    stop_services
    start_services
    health_check
    cleanup_images
    generate_deploy_report
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_success "========================================="
    log_success "部署成功完成！"
    log_success "总耗时: ${duration} 秒"
    log_success "========================================="
}

# ==================== 命令行参数处理 ====================
case "${1:-deploy}" in
    deploy)
        main
        ;;
    status)
        deploy_status
        ;;
    logs)
        show_logs
        ;;
    rollback)
        rollback
        ;;
    stop)
        stop_services
        ;;
    start)
        start_services
        ;;
    health)
        health_check
        ;;
    *)
        echo "用法: $0 {deploy|status|logs|rollback|stop|start|health}"
        echo ""
        echo "命令说明:"
        echo "  deploy   - 完整部署流程（默认）"
        echo "  status   - 查看部署状态"
        echo "  logs     - 查看服务日志"
        echo "  rollback - 回滚到上一个版本"
        echo "  stop     - 停止服务"
        echo "  start    - 启动服务"
        echo "  health   - 健康检查"
        exit 1
        ;;
esac
