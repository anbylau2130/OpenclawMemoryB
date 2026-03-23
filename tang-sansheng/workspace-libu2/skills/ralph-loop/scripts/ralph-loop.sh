#!/bin/bash
# ============================================
# Ralph Loop - OpenClaw 适配版
# 自主 AI 编程循环
# ============================================

set -e

# 配置
MAX_ITERATIONS=${1:-10}
CURRENT_ITERATION=0
PROJECT_ROOT=$(pwd)

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔄 Ralph Loop - 自主 AI 编程循环"
echo "=================================="
echo ""
echo "项目根目录: $PROJECT_ROOT"
echo "最大迭代次数: $MAX_ITERATIONS"
echo ""

# 检查必需文件
if [ ! -f "prd.json" ]; then
    echo -e "${RED}❌ 错误: prd.json 不存在${NC}"
    echo "请先创建 prd.json 文件"
    echo "模板: ~/.openclaw/workspace/skills/ralph-loop/templates/prd.json"
    exit 1
fi

if [ ! -f "progress.txt" ]; then
    echo -e "${YELLOW}⚠️  progress.txt 不存在，正在创建...${NC}"
    cp ~/.openclaw/workspace/skills/ralph-loop/templates/progress.txt progress.txt
fi

# 函数：检查是否有未完成任务
has_incomplete_stories() {
    local incomplete=$(cat prd.json | jq '[.userStories[] | select(.passes == false)] | length')
    if [ "$incomplete" -gt 0 ]; then
        return 0  # 有未完成任务
    else
        return 1  # 所有任务已完成
    fi
}

# 函数：获取下一个任务
get_next_story() {
    cat prd.json | jq -r '.userStories[] | select(.passes == false) | .id' | head -1
}

# 函数：获取任务标题
get_story_title() {
    local story_id=$1
    cat prd.json | jq -r ".userStories[] | select(.id == \"$story_id\") | .title"
}

# 函数：检查质量
run_quality_checks() {
    echo -e "${BLUE}🔍 运行质量检查...${NC}"
    
    # 类型检查
    if [ -f "package.json" ] && grep -q "\"typecheck\"" package.json; then
        echo "  - 类型检查..."
        if npm run typecheck > /dev/null 2>&1; then
            echo -e "    ${GREEN}✅ 类型检查通过${NC}"
        else
            echo -e "    ${RED}❌ 类型检查失败${NC}"
            return 1
        fi
    fi
    
    # 测试
    if [ -f "package.json" ] && grep -q "\"test\"" package.json; then
        echo "  - 运行测试..."
        if npm test > /dev/null 2>&1; then
            echo -e "    ${GREEN}✅ 测试通过${NC}"
        else
            echo -e "    ${RED}❌ 测试失败${NC}"
            return 1
        fi
    fi
    
    # Lint
    if [ -f "package.json" ] && grep -q "\"lint\"" package.json; then
        echo "  - 代码检查..."
        if npm run lint > /dev/null 2>&1; then
            echo -e "    ${GREEN}✅ Lint 通过${NC}"
        else
            echo -e "    ${YELLOW}⚠️  Lint 警告（继续）${NC}"
        fi
    fi
    
    return 0
}

# 主循环
while has_incomplete_stories && [ $CURRENT_ITERATION -lt $MAX_ITERATIONS ]; do
    CURRENT_ITERATION=$((CURRENT_ITERATION + 1))
    
    # 获取下一个任务
    STORY_ID=$(get_next_story)
    STORY_TITLE=$(get_story_title "$STORY_ID")
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${BLUE}📍 迭代 $CURRENT_ITERATION/$MAX_ITERATIONS${NC}"
    echo ""
    echo "任务 ID: $STORY_ID"
    echo "任务标题: $STORY_TITLE"
    echo ""
    
    # 读取 progress.txt
    if [ -s "progress.txt" ]; then
        echo -e "${YELLOW}📖 之前的学习：${NC}"
        tail -5 progress.txt
        echo ""
    fi
    
    # 提示用户
    echo -e "${YELLOW}💡 请在对话中执行以下命令：${NC}"
    echo ""
    echo "使用 Ralph Loop 方法完成任务 $STORY_ID"
    echo ""
    echo "1. 读取 prd.json（任务：$STORY_TITLE）"
    echo "2. 读取 progress.txt（了解之前的教训）"
    echo "3. 搜索代码库（不要假设未实现）"
    echo "4. 实现该任务（只做这一个）"
    echo "5. 运行质量检查"
    echo "6. 如果通过："
    echo "   - 提交代码"
    echo "   - 更新 prd.json (passes: true)"
    echo "   - 添加学习到 progress.txt"
    echo ""
    echo -e "${GREEN}按 Enter 继续...${NC}"
    read
    
    # 检查质量
    if run_quality_checks; then
        echo ""
        echo -e "${GREEN}✅ 质量检查通过！${NC}"
        
        # 检查 prd.json 是否已更新
        NEW_PASSES=$(cat prd.json | jq ".userStories[] | select(.id == \"$STORY_ID\") | .passes")
        
        if [ "$NEW_PASSES" = "true" ]; then
            echo -e "${GREEN}✅ 任务 $STORY_ID 已标记为完成${NC}"
            
            # 提交代码
            if git diff --quiet 2>/dev/null; then
                echo -e "${YELLOW}⚠️  没有代码变更${NC}"
            else
                echo "提交代码..."
                git add -A
                git commit -m "feat: $STORY_TITLE (Story $STORY_ID)"
                echo -e "${GREEN}✅ 代码已提交${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  prd.json 未更新，请手动标记任务完成${NC}"
        fi
    else
        echo ""
        echo -e "${RED}❌ 质量检查失败${NC}"
        echo "请修复问题后继续"
        echo ""
        echo -e "${GREEN}按 Enter 重试...${NC}"
        read
        CURRENT_ITERATION=$((CURRENT_ITERATION - 1))  # 重试当前迭代
    fi
    
    echo ""
done

# 检查是否所有任务完成
if has_incomplete_stories; then
    echo ""
    echo -e "${YELLOW}⚠️  达到最大迭代次数 ($MAX_ITERATIONS)${NC}"
    echo "仍有未完成的任务"
    echo ""
    echo "未完成任务："
    cat prd.json | jq -r '.userStories[] | select(.passes == false) | "- \(.id): \(.title)"'
else
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}✅ Ralph Loop 完成！${NC}"
    echo ""
    echo "所有任务已完成："
    cat prd.json | jq -r '.userStories[] | "- \(.id): \(.title) ✅"'
    echo ""
    echo "总迭代次数: $CURRENT_ITERATION"
    echo ""
    echo "查看 progress.txt 了解详细学习记录。"
fi
