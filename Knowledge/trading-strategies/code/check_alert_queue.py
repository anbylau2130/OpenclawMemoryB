#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查并推送告警队列
功能：心跳时检查是否有待推送的告警，如果有则推送到钉钉工作通知
"""

import json
from pathlib import Path


def check_and_push_alert_queue():
    """检查告警队列并推送到钉钉工作通知"""
    alert_queue_file = Path(__file__).parent.parent.parent.parent / 'data' / 'alert_queue.json'

    if not alert_queue_file.exists():
        return []

    try:
        with open(alert_queue_file, 'r', encoding='utf-8') as f:
            queue = json.load(f)

        if not queue:
            return []

        # 推送所有待推送的告警
        from dingtalk_work_notice import send_work_notice
        
        pushed = []
        for alert in queue:
            result = send_work_notice(alert['message'])
            if result.get('errcode') == 0:
                pushed.append(alert)
                print(f"✅ 推送成功: {alert['timestamp']}")
            else:
                print(f"❌ 推送失败: {result.get('errmsg')}")

        # 清空队列
        with open(alert_queue_file, 'w', encoding='utf-8') as f:
            json.dump([], f)

        return pushed

    except Exception as e:
        print(f"❌ 推送告警队列失败: {e}")
        return []


if __name__ == '__main__':
    print("="*70)
    print("检查告警队列")
    print("="*70)
    
    pushed = check_and_push_alert_queue()
    
    if pushed:
        print(f"\n✅ 已推送 {len(pushed)} 条告警到工作通知")
    else:
        print("\n✅ 无待推送告警")
