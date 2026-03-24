#!/usr/bin/env python3
"""
对话记录系统 - 自动保存用户说的话
位置: /root/.openclaw/workspace/scripts/conversation_recorder.py
"""

import json
import os
from datetime import datetime
from pathlib import Path

class ConversationRecorder:
    """对话记录器"""

    def __init__(self):
        self.workspace = Path("/root/.openclaw/workspace")
        self.conversation_dir = self.workspace / "docs" / "Conversation"
        self.conversation_dir.mkdir(parents=True, exist_ok=True)

    def record_user_message(self, message: str, channel: str = "dingtalk", agent: str = "main"):
        """
        记录用户说的话

        Args:
            message: 用户消息内容
            channel: 渠道（dingtalk, wechat等）
            agent: 对话的agent
        """
        today = datetime.now().strftime("%Y-%m-%d")
        conversation_file = self.conversation_dir / f"{today}.md"

        # 获取当前时间
        time_str = datetime.now().strftime("%H:%M")

        # 准备要追加的内容
        content = f"\n## {time_str}\n- \"{message}\"\n"

        # 追加到文件
        with open(conversation_file, 'a', encoding='utf-8') as f:
            f.write(content)

        # 更新最后更新时间
        self._update_timestamp(conversation_file)

        return {
            "status": "success",
            "file": str(conversation_file),
            "time": time_str,
            "message": message
        }

    def _update_timestamp(self, file_path: Path):
        """更新文件中的时间戳"""
        content = file_path.read_text(encoding='utf-8')

        # 替换最后更新时间
        import re
        pattern = r'_最后更新: \d{4}-\d{2}-\d{2} \d{2}:\d{2}'
        replacement = f'_最后更新: {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        content = re.sub(pattern, replacement, content)

        file_path.write_text(content, encoding='utf-8')

    def get_today_conversations(self) -> list:
        """获取今日对话记录"""
        today = datetime.now().strftime("%Y-%m-%d")
        conversation_file = self.conversation_dir / f"{today}.md"

        if not conversation_file.exists():
            return []

        conversations = []
        with open(conversation_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析对话
        import re
        pattern = r'## (\d{2}:\d{2})\n- "(.+)"'
        matches = re.findall(pattern, content)

        for time_str, message in matches:
            conversations.append({
                "time": time_str,
                "message": message
            })

        return conversations

    def get_stats(self) -> dict:
        """获取统计信息"""
        today = datetime.now().strftime("%Y-%m-%d")
        conversation_file = self.conversation_dir / f"{today}.md"

        conversations = self.get_today_conversations()

        return {
            "date": today,
            "total_conversations": len(conversations),
            "file_exists": conversation_file.exists(),
            "file_path": str(conversation_file)
        }


# 使用示例
if __name__ == "__main__":
    recorder = ConversationRecorder()

    # 记录消息
    result = recorder.record_user_message("测试消息")
    print(f"✅ 已记录: {result}")

    # 获取统计
    stats = recorder.get_stats()
    print(f"📊 今日统计: {stats}")

    # 获取今日对话
    conversations = recorder.get_today_conversations()
    print(f"📋 今日对话: {len(conversations)}条")
