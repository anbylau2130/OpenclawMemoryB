#!/usr/bin/env python3
"""
用户消息记录系统 - 只记录陛下说的话
位置: /root/.openclaw/workspace/scripts/user_message_recorder.py
规则: 只保存用户消息，不保存agent回复
"""

import json
import re
from datetime import datetime
from pathlib import Path

class UserMessageRecorder:
    """用户消息记录器 - 只记录陛下说的话"""

    def __init__(self):
        self.workspace = Path("/root/.openclaw/workspace")
        self.conversation_dir = self.workspace / "docs" / "Conversation"
        self.conversation_dir.mkdir(parents=True, exist_ok=True)

    def record_user_message(self, message: str, channel: str = "dingtalk"):
        """
        记录用户说的话（只记录用户消息，不记录回复）

        Args:
            message: 用户消息内容
            channel: 渠道（dingtalk, wechat等）
        """
        today = datetime.now().strftime("%Y-%m-%d")
        conversation_file = self.conversation_dir / f"{today}.md"

        # 获取当前时间
        time_str = datetime.now().strftime("%H:%M")

        # 准备要追加的内容（只记录用户消息）
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
            "message": message,
            "note": "只记录用户消息，不记录agent回复"
        }

    def _update_timestamp(self, file_path: Path):
        """更新文件中的时间戳"""
        content = file_path.read_text(encoding='utf-8')

        # 替换最后更新时间
        pattern = r'_最后更新: \d{4}-\d{2}-\d{2} \d{2}:\d{2}'
        replacement = f'_最后更新: {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        content = re.sub(pattern, replacement, content)

        file_path.write_text(content, encoding='utf-8')

    def get_today_messages(self) -> list:
        """获取今日用户消息（只返回用户消息，不包含回复）"""
        today = datetime.now().strftime("%Y-%m-%d")
        conversation_file = self.conversation_dir / f"{today}.md"

        if not conversation_file.exists():
            return []

        messages = []
        with open(conversation_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析用户消息
        pattern = r'## (\d{2}:\d{2})\n- "(.+)"'
        matches = re.findall(pattern, content)

        for time_str, message in matches:
            messages.append({
                "time": time_str,
                "message": message,
                "type": "user_message"  # 标记为用户消息
            })

        return messages

    def get_stats(self) -> dict:
        """获取统计信息"""
        today = datetime.now().strftime("%Y-%m-%d")
        conversation_file = self.conversation_dir / f"{today}.md"

        messages = self.get_today_messages()

        return {
            "date": today,
            "total_user_messages": len(messages),
            "file_exists": conversation_file.exists(),
            "file_path": str(conversation_file),
            "note": "只记录用户消息，不记录agent回复"
        }


# 使用示例
if __name__ == "__main__":
    recorder = UserMessageRecorder()

    # 记录用户消息
    result = recorder.record_user_message("测试用户消息")
    print(f"✅ 已记录用户消息: {result}")

    # 获取统计
    stats = recorder.get_stats()
    print(f"📊 今日统计: {stats}")

    # 获取今日用户消息
    messages = recorder.get_today_messages()
    print(f"📋 今日用户消息: {len(messages)}条")
