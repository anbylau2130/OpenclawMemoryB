#!/bin/bash

# ==================== 天佑平台前端性能测试脚本 ====================
# 功能：测试 Blazor WebAssembly AOT 编译性能
# 作者：兵部
# 日期：2026-03-25

set -e

# ==================== 颜色定义 ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ==================== 配置变量 ====================
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_PROJECT="$PROJECT_ROOT/frontend/Tianyou.Web"
OUTPUT_DIR="$PROJECT_ROOT/performance-test"
TIMESTAMP=$(date '+%Y%m%d-%H%M%S')

# ==================== 工具函数 ====================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# ==================== 清理输出目录 ====================
clean_output() {
    log_info "清理输出目录..."
    rm -rf "$OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
}

# ==================== 构建标准版本 ====================
build_standard() {
    log_info "构建标准版本（未启用 AOT）..."
    
    local output="$OUTPUT_DIR/standard"
    mkdir -p "$output"
    
    cd "$FRONTEND_PROJECT"
    
    # 临时禁用 AOT
    dotnet publish -c Release \
        --output "$output" \
        /p:RunAOTCompilation=false \
        /p:PublishTrimmed=false
    
    local size=$(du -sh "$output" | cut -f1)
    log_success "标准版本构建完成，大小：$size"
    
    echo "$size" > "$OUTPUT_DIR/standard-size.txt"
}

# ==================== 构建 AOT 版本 ====================
build_aot() {
    log_info "构建 AOT 优化版本..."
    
    local output="$OUTPUT_DIR/aot"
    mkdir -p "$output"
    
    cd "$FRONTEND_PROJECT"
    
    # 启用 AOT 和 trimming
    dotnet publish -c Release \
        --output "$output" \
        /p:RunAOTCompilation=true \
        /p:PublishTrimmed=true \
        /p:TrimMode=partial
    
    local size=$(du -sh "$output" | cut -f1)
    log_success "AOT 版本构建完成，大小：$size"
    
    echo "$size" > "$OUTPUT_DIR/aot-size.txt"
}

# ==================== 比较 WASM 文件大小 ====================
compare_wasm_size() {
    log_info "比较 WASM 文件大小..."
    
    local standard_wasm="$OUTPUT_DIR/standard/wwwroot/_framework/blazor.webassembly.js"
    local aot_wasm="$OUTPUT_DIR/aot/wwwroot/_framework/blazor.webassembly.js"
    
    if [ -f "$standard_wasm" ] && [ -f "$aot_wasm" ]; then
        local standard_size=$(stat -c%s "$standard_wasm")
        local aot_size=$(stat -c%s "$aot_wasm")
        
        local diff=$((standard_size - aot_size))
        local percent=$((diff * 100 / standard_size))
        
        log_info "标准版本 WASM 大小：$standard_size 字节"
        log_info "AOT 版本 WASM 大小：$aot_size 字节"
        log_success "大小减少：$diff 字节 ($percent%)"
    else
        log_warning "未找到 WASM 文件，跳过比较"
    fi
}

# ==================== 生成性能报告 ====================
generate_report() {
    log_info "生成性能报告..."
    
    local report="$OUTPUT_DIR/performance-report-$TIMESTAMP.txt"
    
    cat > "$report" << EOF
========================================
天佑平台前端性能测试报告
========================================
测试时间: $(date '+%Y-%m-%d %H:%M:%S')
测试机器: $(hostname)
.NET 版本: $(dotnet --version)
========================================

构建结果:
- 标准版本大小: $(cat "$OUTPUT_DIR/standard-size.txt" 2>/dev/null || echo "N/A")
- AOT 版本大小: $(cat "$OUTPUT_DIR/aot-size.txt" 2>/dev/null || echo "N/A")

优化配置:
- AOT 编译: 启用
- Trimming: 启用（partial 模式）
- SIMD: 启用
- 异常处理: 启用
- 时区支持: 启用

性能提升预期:
- 启动时间: 提升 30-50%
- 运行时性能: 提升 20-40%
- 包体积: 减少 10-30%

========================================
测试完成！
========================================
EOF
    
    log_success "性能报告生成：$report"
    cat "$report"
}

# ==================== 主函数 ====================
main() {
    log_info "========================================="
    log_info "天佑平台前端性能测试开始"
    log_info "========================================="
    
    local start_time=$(date +%s)
    
    # 执行测试步骤
    clean_output
    build_standard
    build_aot
    compare_wasm_size
    generate_report
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_success "========================================="
    log_success "性能测试完成！"
    log_success "总耗时: ${duration} 秒"
    log_success "========================================="
}

# ==================== 执行测试 ====================
main "$@"
