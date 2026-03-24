#!/usr/bin/env python3
"""批量创建三省六部agents的推送脚本"""

import os

# 11个agents的正确名称
AGENTS = [
    "中书省", "门下省", "尚书省", "御史台",
    "兵部", "户部", "礼部", "工部", "刑部", "吏部", "史官"
]

# 原始脚本路径
ORIGINAL_SCRIPT = "/root/.openclaw/tang-sansheng/workspace-zhongshu/office-agent-push.py"

# 读取原始脚本
with open(ORIGINAL_SCRIPT, "r", encoding="utf-8") as f:
    template = f.read()

# 为每个agent创建脚本
for agent_name in AGENTS:
    # 替换AGENT_NAME
    script_content = template.replace(
        'AGENT_NAME = "中书省"',
        f'AGENT_NAME = "{agent_name}"'
    )
    
    # 修改STATE_FILE，使用独立的文件名
    script_content = script_content.replace(
        'STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "office-agent-state.json")',
        f'STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "office-agent-state-{agent_name}.json")'
    )
    
    # 写入新脚本
    script_path = f"/root/.openclaw/tang-sansheng/workspace-zhongshu/office-push-{agent_name}.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print(f"✅ 已创建脚本: office-push-{agent_name}.py")

print(f"\n🎉 完成！共创建 {len(AGENTS)} 个agent脚本")
