#!/bin/bash

# ==================== 天佑平台构建脚本 ====================
# 功能：自动化构建后端和前端项目
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
BACKEND_SOLUTION="$PROJECT_ROOT/backend/Tianyou.sln"
FRONTEND_PROJECT="$PROJECT_ROOT/frontend/Tianyou.Web/Tianyou.Web.csproj"
BUILD_OUTPUT="$PROJECT_ROOT/build"
LOG_FILE="$BUILD_OUTPUT/build.log"
DOTNET_VERSION="8.0"

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
    log_info "检查构建环境..."
    
    # 检查 .NET SDK
    if ! command -v dotnet &> /dev/null; then
        log_error "未找到 .NET SDK，请先安装 .NET $DOTNET_VERSION SDK"
        exit 1
    fi
    
    local dotnet_version=$(dotnet --version)
    log_info ".NET 版本: $dotnet_version"
    
    # 检查 Docker（可选）
    if command -v docker &> /dev/null; then
        log_info "Docker 版本: $(docker --version)"
    else
        log_warning "未安装 Docker，Docker 构建将被跳过"
    fi
    
    log_success "环境检查完成"
}

# ==================== 清理构建输出 ====================
clean_build() {
    log_info "清理构建输出..."
    
    rm -rf "$BUILD_OUTPUT"
    mkdir -p "$BUILD_OUTPUT/logs"
    
    log_success "清理完成"
}

# ==================== 构建后端 ====================
build_backend() {
    log_info "开始构建后端项目..."
    
    local backend_output="$BUILD_OUTPUT/backend"
    mkdir -p "$backend_output"
    
    # 恢复依赖
    log_info "恢复后端依赖包..."
    dotnet restore "$BACKEND_SOLUTION" \
        --verbosity minimal \
        > "$BUILD_OUTPUT/logs/backend-restore.log" 2>&1
    
    if [ $? -ne 0 ]; then
        log_error "后端依赖恢复失败，查看日志: $BUILD_OUTPUT/logs/backend-restore.log"
        exit 1
    fi
    log_success "后端依赖恢复完成"
    
    # 构建项目
    log_info "构建后端项目..."
    dotnet build "$BACKEND_SOLUTION" \
        --configuration Release \
        --no-restore \
        --verbosity minimal \
        > "$BUILD_OUTPUT/logs/backend-build.log" 2>&1
    
    if [ $? -ne 0 ]; then
        log_error "后端构建失败，查看日志: $BUILD_OUTPUT/logs/backend-build.log"
        exit 1
    fi
    log_success "后端构建完成"
    
    # 运行测试
    log_info "运行后端测试..."
    dotnet test "$BACKEND_SOLUTION" \
        --configuration Release \
        --no-build \
        --verbosity normal \
        --logger "trx;LogFileName=backend-test-results.trx" \
        --results-directory "$BUILD_OUTPUT/test-results" \
        > "$BUILD_OUTPUT/logs/backend-test.log" 2>&1
    
    if [ $? -ne 0 ]; then
        log_warning "后端测试失败，查看日志: $BUILD_OUTPUT/logs/backend-test.log"
    else
        log_success "后端测试通过"
    fi
    
    # 发布项目
    log_info "发布后端项目..."
    dotnet publish "$PROJECT_ROOT/backend/src/Tianyou.Api/Tianyou.Api.csproj" \
        --configuration Release \
        --no-build \
        --output "$backend_output/publish" \
        > "$BUILD_OUTPUT/logs/backend-publish.log" 2>&1
    
    if [ $? -ne 0 ]; then
        log_error "后端发布失败，查看日志: $BUILD_OUTPUT/logs/backend-publish.log"
        exit 1
    fi
    log_success "后端发布完成: $backend_output/publish"
}

# ==================== 构建前端 ====================
build_frontend() {
    log_info "开始构建前端项目..."
    
    local frontend_output="$BUILD_OUTPUT/frontend"
    mkdir -p "$frontend_output"
    
    # 恢复依赖
    log_info "恢复前端依赖包..."
    dotnet restore "$FRONTEND_PROJECT" \
        --verbosity minimal \
        > "$BUILD_OUTPUT/logs/frontend-restore.log" 2>&1
    
    if [ $? -ne 0 ]; then
        log_error "前端依赖恢复失败，查看日志: $BUILD_OUTPUT/logs/frontend-restore.log"
        exit 1
    fi
    log_success "前端依赖恢复完成"
    
    # 构建项目
    log_info "构建前端项目..."
    dotnet build "$FRONTEND_PROJECT" \
        --configuration Release \
        --no-restore \
        --verbosity minimal \
        > "$BUILD_OUTPUT/logs/frontend-build.log" 2>&1
    
    if [ $? -ne 0 ]; then
        log_error "前端构建失败，查看日志: $BUILD_OUTPUT/logs/frontend-build.log"
        exit 1
    fi
    log_success "前端构建完成"
    
    # 发布项目
    log_info "发布前端项目..."
    dotnet publish "$FRONTEND_PROJECT" \
        --configuration Release \
        --no-build \
        --output "$frontend_output/publish" \
        > "$BUILD_OUTPUT/logs/frontend-publish.log" 2>&1
    
    if [ $? -ne 0 ]; then
        log_error "前端发布失败，查看日志: $BUILD_OUTPUT/logs/frontend-publish.log"
        exit 1
    fi
    log_success "前端发布完成: $frontend_output/publish"
}

# ==================== Docker 构建 ====================
build_docker() {
    if ! command -v docker &> /dev/null; then
        log_warning "Docker 未安装，跳过 Docker 构建"
        return 0
    fi
    
    log_info "开始 Docker 构建..."
    
    cd "$PROJECT_ROOT"
    
    # 构建后端镜像
    log_info "构建后端 Docker 镜像..."
    docker build \
        --tag tianyou-backend:latest \
        --tag tianyou-backend:$(date '+%Y%m%d-%H%M%S') \
        --file "$PROJECT_ROOT/docker/backend.Dockerfile" \
        "$PROJECT_ROOT/backend" \
        > "$BUILD_OUTPUT/logs/docker-backend.log" 2>&1
    
    if [ $? -ne 0 ]; then
        log_error "后端 Docker 镜像构建失败，查看日志: $BUILD_OUTPUT/logs/docker-backend.log"
        exit 1
    fi
    log_success "后端 Docker 镜像构建完成"
    
    # 构建前端镜像
    log_info "构建前端 Docker 镜像..."
    docker build \
        --tag tianyou-frontend:latest \
        --tag tianyou-frontend:$(date '+%Y%m%d-%H%M%S') \
        --file "$PROJECT_ROOT/docker/frontend.Dockerfile" \
        "$PROJECT_ROOT/frontend" \
        > "$BUILD_OUTPUT/logs/docker-frontend.log" 2>&1
    
    if [ $? -ne 0 ]; then
        log_error "前端 Docker 镜像构建失败，查看日志: $BUILD_OUTPUT/logs/docker-frontend.log"
        exit 1
    fi
    log_success "前端 Docker 镜像构建完成"
}

# ==================== 生成构建报告 ====================
generate_build_report() {
    log_info "生成构建报告..."
    
    local report_file="$BUILD_OUTPUT/build-report.txt"
    
    cat > "$report_file" << EOF
========================================
天佑平台构建报告
========================================
构建时间: $(date '+%Y-%m-%d %H:%M:%S')
构建机器: $(hostname)
构建用户: $(whoami)
.NET 版本: $(dotnet --version)
========================================

构建输出:
- 后端: $BUILD_OUTPUT/backend/publish
- 前端: $BUILD_OUTPUT/frontend/publish

构建日志:
- 后端构建: $BUILD_OUTPUT/logs/backend-build.log
- 后端测试: $BUILD_OUTPUT/logs/backend-test.log
- 前端构建: $BUILD_OUTPUT/logs/frontend-build.log

Docker 镜像:
$(docker images | grep tianyou || echo "无 Docker 镜像")

========================================
构建完成！
========================================
EOF
    
    log_success "构建报告生成: $report_file"
    cat "$report_file"
}

# ==================== 主函数 ====================
main() {
    log_info "========================================="
    log_info "天佑平台自动化构建开始"
    log_info "========================================="
    
    local start_time=$(date +%s)
    
    # 执行构建步骤
    check_environment
    clean_build
    build_backend
    build_frontend
    build_docker
    generate_build_report
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_success "========================================="
    log_success "构建成功完成！"
    log_success "总耗时: ${duration} 秒"
    log_success "========================================="
}

# ==================== 执行构建 ====================
main "$@"
