#!/bin/bash
# 批量启动三省六部所有agents

AGENTS=("中书省" "门下省" "尚书省" "御史台" "兵部" "户部" "礼部" "工部" "刑部" "吏部" "史官")

echo "🚀 开始启动所有agents..."

for agent in "${AGENTS[@]}"; do
    echo "启动 $agent..."
    nohup python3 "office-push-${agent}.py" > "/tmp/office-${agent}.log" 2>&1 &
    sleep 1
done

echo "✅ 所有agents启动完成！"
echo ""
echo "📋 查看日志："
for agent in "${AGENTS[@]}"; do
    echo "  $agent: tail -f /tmp/office-${agent}.log"
done

echo ""
echo "⏳ 等待10秒让agents加入办公室..."
sleep 10

echo ""
echo "🔍 检查agents状态："
curl -s http://192.168.50.251:19000/agents | python3 -m json.tool
