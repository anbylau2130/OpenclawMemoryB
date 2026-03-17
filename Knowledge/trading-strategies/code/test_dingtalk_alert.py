#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试钉钉告警推送
"""

import subprocess
from datetime import datetime


def test_dingtalk_push():
    """测试钉钉推送功能"""
    print("="*70)
    print("测试钉钉告警推送")
    print("="*70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 构建测试消息
    message = f"""⚠️ 测试告警 - {datetime.now().strftime('%H:%M:%S')}

股票: 600031 三一重工
价格: ¥20.85 (+1.23%)

🔴 VWAP买入信号: 股价低于VWAP 2.1%
🟡 布林带下轨: 接近下轨支撑

💡 V5实时监控系统 - 测试推送"""

    print("测试消息:")
    print(message)
    print()

    # 发送到钉钉
    cmd = [
        'openclaw', 'message', 'send',
        '--channel', 'dingtalk',
        '--account', 'default',  # 使用default账号
        '--target', '13027729771',  # 用户手机号
        '--message', message
    ]

    print("执行命令:")
    print(' '.join(cmd))
    print()

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=10
    )

    print("返回码:", result.returncode)
    print("标准输出:", result.stdout)
    if result.stderr:
        print("标准错误:", result.stderr)

    if result.returncode == 0:
        print("\n✅ 钉钉推送成功！")
    else:
        print("\n❌ 钉钉推送失败")

    print("\n" + "="*70)


if __name__ == '__main__':
    test_dingtalk_push()
