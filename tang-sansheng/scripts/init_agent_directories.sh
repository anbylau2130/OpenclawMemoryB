#!/bin/bash
# 三省六部 Agent 目录结构初始化脚本
# 版本: v1.0
# 时间: 2026-03-24 09:01
# 制定: 中书省

set -e

WORKSPACE_BASE="/root/.openclaw/tang-sansheng"
DEPARTMENTS=("zhongshu" "menxia" "shangshu" "yushitai" "bingbu" "libu" "hubu" "gongbu" "libu2" "xingbu")

echo "==================================="
echo "三省六部目录结构初始化"
echo "==================================="
echo ""

for dept in "${DEPARTMENTS[@]}"; do
    workspace="${WORKSPACE_BASE}/workspace-${dept}"
    
    echo "📁 初始化 ${dept} 工作目录..."
    
    # 创建根目录
    mkdir -p "${workspace}"
    
    # 创建核心配置文件
    touch "${workspace}/AGENTS.md"
    touch "${workspace}/SOUL.md"
    touch "${workspace}/TOOLS.md"
    touch "${workspace}/USER.md"
    touch "${workspace}/IDENTITY.md"
    touch "${workspace}/HEARTBEAT.md"
    touch "${workspace}/.gitignore"
    touch "${workspace}/README.md"
    
    # 创建系统目录
    mkdir -p "${workspace}/.openclaw"
    mkdir -p "${workspace}/.clawhub"
    
    # 创建数据目录
    mkdir -p "${workspace}/data/input"
    mkdir -p "${workspace}/data/output"
    mkdir -p "${workspace}/data/cache"
    
    # 创建文档目录
    mkdir -p "${workspace}/docs/reports"
    mkdir -p "${workspace}/docs/guides"
    mkdir -p "${workspace}/docs/drafts"
    mkdir -p "${workspace}/docs/archives"
    
    # 创建项目目录
    mkdir -p "${workspace}/projects/active"
    mkdir -p "${workspace}/projects/completed"
    mkdir -p "${workspace}/projects/pending"
    
    # 创建记忆目录
    mkdir -p "${workspace}/memory/daily"
    mkdir -p "${workspace}/memory/projects"
    mkdir -p "${workspace}/memory/lessons"
    
    # 创建知识库目录
    mkdir -p "${workspace}/Knowledge/references"
    mkdir -p "${workspace}/Knowledge/standards"
    mkdir -p "${workspace}/Knowledge/best-practices"
    
    # 创建学习记录目录
    mkdir -p "${workspace}/.learnings"
    touch "${workspace}/.learnings/ERRORS.md"
    touch "${workspace}/.learnings/LEARNINGS.md"
    touch "${workspace}/.learnings/FEATURE_REQUESTS.md"
    touch "${workspace}/.learnings/README.md"
    
    # 创建技能目录
    mkdir -p "${workspace}/skills/installed"
    mkdir -p "${workspace}/skills/custom"
    mkdir -p "${workspace}/skills/templates"
    
    # 创建脚本目录
    mkdir -p "${workspace}/scripts/automation"
    mkdir -p "${workspace}/scripts/deployment"
    mkdir -p "${workspace}/scripts/utilities"
    
    # 创建工具目录
    mkdir -p "${workspace}/tools/generators"
    mkdir -p "${workspace}/tools/validators"
    mkdir -p "${workspace}/tools/analyzers"
    
    # 创建临时文件目录
    mkdir -p "${workspace}/temp"
    mkdir -p "${workspace}/logs/system"
    mkdir -p "${workspace}/logs/errors"
    mkdir -p "${workspace}/logs/debug"
    mkdir -p "${workspace}/cache"
    
    # 创建部门特定目录
    case ${dept} in
        "zhongshu")
            mkdir -p "${workspace}/drafts/pending"
            mkdir -p "${workspace}/drafts/approved"
            mkdir -p "${workspace}/drafts/rejected"
            mkdir -p "${workspace}/policies"
            mkdir -p "${workspace}/coordination"
            ;;
        "menxia")
            mkdir -p "${workspace}/reviews/pending"
            mkdir -p "${workspace}/reviews/approved"
            mkdir -p "${workspace}/reviews/rejected"
            mkdir -p "${workspace}/questions"
            mkdir -p "${workspace}/feedback"
            ;;
        "shangshu")
            mkdir -p "${workspace}/dispatches/active"
            mkdir -p "${workspace}/dispatches/completed"
            mkdir -p "${workspace}/dispatches/overdue"
            mkdir -p "${workspace}/schedules"
            mkdir -p "${workspace}/progress"
            ;;
        "yushitai")
            mkdir -p "${workspace}/audits/code"
            mkdir -p "${workspace}/audits/security"
            mkdir -p "${workspace}/audits/quality"
            mkdir -p "${workspace}/violations"
            mkdir -p "${workspace}/recommendations"
            ;;
        "bingbu")
            mkdir -p "${workspace}/code/backend"
            mkdir -p "${workspace}/code/frontend"
            mkdir -p "${workspace}/code/tests"
            mkdir -p "${workspace}/architecture"
            mkdir -p "${workspace}/deployments"
            ;;
        "libu")
            mkdir -p "${workspace}/marketing/campaigns"
            mkdir -p "${workspace}/marketing/content"
            mkdir -p "${workspace}/marketing/social"
            mkdir -p "${workspace}/branding"
            mkdir -p "${workspace}/communications"
            ;;
        "hubu")
            mkdir -p "${workspace}/finance/budgets"
            mkdir -p "${workspace}/finance/reports"
            mkdir -p "${workspace}/finance/analysis"
            mkdir -p "${workspace}/resources"
            mkdir -p "${workspace}/planning"
            ;;
        "gongbu")
            mkdir -p "${workspace}/infrastructure/servers"
            mkdir -p "${workspace}/infrastructure/networks"
            mkdir -p "${workspace}/infrastructure/security"
            mkdir -p "${workspace}/deployment"
            mkdir -p "${workspace}/monitoring"
            ;;
        "libu2")
            mkdir -p "${workspace}/hr/evaluations"
            mkdir -p "${workspace}/hr/assignments"
            mkdir -p "${workspace}/hr/records"
            mkdir -p "${workspace}/training"
            mkdir -p "${workspace}/organization"
            ;;
        "xingbu")
            mkdir -p "${workspace}/legal/contracts"
            mkdir -p "${workspace}/legal/compliance"
            mkdir -p "${workspace}/legal/policies"
            mkdir -p "${workspace}/risk"
            mkdir -p "${workspace}/review"
            ;;
    esac
    
    echo "✅ ${dept} 初始化完成"
done

echo ""
echo "==================================="
echo "🎉 所有部门目录结构初始化完成！"
echo "==================================="
echo ""
echo "📊 统计信息："
echo "  - 初始化部门数: ${#DEPARTMENTS[@]}"
echo "  - 基础目录数: 35+"
echo "  - 部门特定目录: 5+"
echo ""
echo "📋 下一步："
echo "  1. 查看规范: cat ${WORKSPACE_BASE}/workspace-zhongshu/三省六部Agent目录结构规范_v1.0.md"
echo "  2. 配置 AGENTS.md"
echo "  3. 开始使用标准目录结构"
