#!/usr/bin/env python3
"""
定时任务执行器
=====================================
通过心跳触发，在指定时间执行任务
"""

import json
import os
from datetime import datetime, time
from typing import Dict, List

STATE_FILE = "/root/.openclaw/workspace/memory/heartbeat-state.json"
TASKS_DIR = "/root/.openclaw/workspace/data/backtest"

# 任务定义
TASKS = {
    "morning_selection": {
        "time": time(8, 0),    # 8:00
        "tolerance": 30,        # ±30分钟
        "script": "stock_selector_v5_real.py",
        "description": "早间选股"
    },
    "afternoon_review": {
        "time": time(16, 0),   # 16:00
        "tolerance": 30,
        "script": "stock_review_v2.py",
        "description": "午后复盘"
    }
}


def load_state() -> Dict:
    """加载状态"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_state(state: Dict):
    """保存状态"""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def should_run_task(task_name: str, task: Dict, state: Dict) -> bool:
    """判断任务是否应该执行"""
    now = datetime.now()
    current_time = now.time()
    task_time = task["time"]
    tolerance = task["tolerance"]
    
    # 检查时间是否在允许范围内
    from datetime import timedelta
    task_datetime = datetime.combine(now.date(), task_time)
    start = (task_datetime - timedelta(minutes=tolerance)).time()
    end = (task_datetime + timedelta(minutes=tolerance)).time()
    
    if not (start <= current_time <= end):
        return False
    
    # 检查今天是否已执行
    today = now.strftime("%Y-%m-%d")
    last_run = state.get("trading", {}).get(f"last_{task_name}", "")
    
    if last_run.startswith(today):
        return False
    
    return True


def run_task(task_name: str, task: Dict) -> Dict:
    """执行任务"""
    import subprocess
    
    script_path = f"/root/.openclaw/workspace/Knowledge/trading-strategies/code/{task['script']}"
    
    if not os.path.exists(script_path):
        return {
            "success": False,
            "error": f"脚本不存在: {script_path}"
        }
    
    log_file = os.path.join(TASKS_DIR, f"{task_name}_{datetime.now().strftime('%Y%m%d')}.log")
    
    try:
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=os.path.dirname(script_path)
        )
        
        # 写日志
        with open(log_file, 'w') as f:
            f.write(f"任务: {task['description']}\n")
            f.write(f"时间: {datetime.now().isoformat()}\n")
            f.write(f"脚本: {script_path}\n")
            f.write("\n--- 输出 ---\n")
            f.write(result.stdout)
            if result.stderr:
                f.write("\n--- 错误 ---\n")
                f.write(result.stderr)
        
        return {
            "success": result.returncode == 0,
            "log_file": log_file,
            "output": result.stdout[:500] if result.stdout else ""
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def check_and_run_tasks() -> List[Dict]:
    """检查并执行任务"""
    state = load_state()
    results = []
    
    for task_name, task in TASKS.items():
        if should_run_task(task_name, task, state):
            print(f"执行任务: {task['description']}")
            result = run_task(task_name, task)
            results.append({
                "task": task_name,
                "description": task['description'],
                **result
            })
            
            # 更新状态
            if "trading" not in state:
                state["trading"] = {}
            state["trading"][f"last_{task_name}"] = datetime.now().isoformat()
    
    if results:
        save_state(state)
    
    return results


def main():
    """主函数"""
    print("="*60)
    print("⏰ 定时任务检查")
    print("="*60)
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = check_and_run_tasks()
    
    if results:
        print(f"\n执行了 {len(results)} 个任务:")
        for r in results:
            status = "✅" if r.get("success") else "❌"
            print(f"  {status} {r['description']}")
            if r.get("error"):
                print(f"     错误: {r['error']}")
    else:
        print("无需执行任务")
    
    return results


if __name__ == "__main__":
    main()
