#!/usr/bin/env python3
"""
定时任务执行器 - 用于心跳检查时执行
=====================================
功能：
  - 8:00-9:00：执行选股（如果今天还没选股）
  - 16:00-17:00：执行复盘（如果今天还没复盘）
  - 9:30-15:00：自动启动交易监控（如果未运行）
作者：小秘
日期：2026-03-18
"""

import os
import json
import subprocess
from datetime import datetime, time as dt_time
from pathlib import Path

# 配置
CODE_DIR = Path("/root/.openclaw/workspace/Knowledge/trading-strategies/code")
SELECTION_DIR = Path("/root/.openclaw/workspace/projects/stock-tracking/selections")
REVIEW_DIR = Path("/root/.openclaw/workspace/projects/stock-tracking/reviews")
LOG_FILE = Path("/root/.openclaw/workspace/logs/scheduled_tasks.log")
PID_FILE = Path("/root/.openclaw/workspace/logs/trading_monitor.pid")


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    # 写入日志文件
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + "\n")


def is_trading_hours() -> bool:
    """判断当前是否在交易时段"""
    now = datetime.now()
    current_time = now.time()
    
    # 交易时段：9:30-11:30, 13:00-15:00
    morning_start = dt_time(9, 30)
    morning_end = dt_time(11, 30)
    afternoon_start = dt_time(13, 0)
    afternoon_end = dt_time(15, 0)
    
    return (morning_start <= current_time <= morning_end) or \
           (afternoon_start <= current_time <= afternoon_end)


def is_monitor_running() -> bool:
    """检查交易监控是否正在运行"""
    # 检查PID文件
    if PID_FILE.exists():
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            # 检查进程是否存在
            import signal
            try:
                os.kill(pid, 0)  # 发送信号0，不会真的杀死进程，只是检查是否存在
                return True
            except OSError:
                # 进程不存在，清理PID文件
                PID_FILE.unlink()
                return False
        except (ValueError, IOError):
            return False
    
    # 备用检查：通过进程名检查
    try:
        result = subprocess.run(
            ["pgrep", "-f", "trading_hours_monitor.py"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return bool(result.stdout.strip())
    except:
        return False


def start_trading_monitor():
    """后台启动交易监控"""
    log("=" * 60)
    log("启动交易时段监控...")
    
    try:
        # 使用nohup后台启动
        monitor_script = CODE_DIR / "trading_hours_monitor.py"
        log_file = LOG_FILE.parent / "trading_monitor.log"
        
        # 启动进程
        with open(log_file, 'a') as log_f:
            process = subprocess.Popen(
                ["python3", str(monitor_script)],
                cwd=CODE_DIR,
                stdout=log_f,
                stderr=log_f,
                start_new_session=True  # 创建新的会话，避免随父进程退出
            )
        
        # 保存PID
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PID_FILE, 'w') as f:
            f.write(str(process.pid))
        
        log(f"✅ 交易监控已启动 (PID: {process.pid})")
        return True
        
    except Exception as e:
        log(f"❌ 启动交易监控失败: {e}")
        return False


def check_and_start_monitor():
    """检查并启动交易监控"""
    if not is_trading_hours():
        return
    
    if is_monitor_running():
        log("⏭️  交易监控已在运行，跳过")
        return
    
    # 启动监控
    start_trading_monitor()


def check_selection_done_today() -> bool:
    """检查今天是否已经完成选股"""
    today = datetime.now().strftime("%Y-%m-%d")
    selection_file = SELECTION_DIR / f"selection_{today}_v5_real.json"
    return selection_file.exists()


def check_review_done_today() -> bool:
    """检查今天是否已经完成复盘"""
    today = datetime.now().strftime("%Y-%m-%d")
    # 尝试多个可能的复盘文件名
    review_files = [
        REVIEW_DIR / f"daily_review_{today}.json",
        REVIEW_DIR / f"weekly_review_{today}.json",
    ]
    return any(f.exists() for f in review_files)


def run_stock_selector():
    """执行选股任务"""
    log("=" * 60)
    log("开始执行选股任务...")
    
    try:
        result = subprocess.run(
            ["python3", "stock_selector_v5_real.py"],
            cwd=CODE_DIR,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            log("✅ 选股任务执行成功")
            # 更新软链接
            today = datetime.now().strftime("%Y-%m-%d")
            src = SELECTION_DIR / f"selection_{today}_v5_real.json"
            dst = CODE_DIR / "selections" / f"selection_{today}.json"
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                if dst.exists() or dst.is_symlink():
                    dst.unlink()
                dst.symlink_to(src)
                log(f"✅ 已更新软链接: {dst}")
                
                # 发送钉钉通知（无论是否有股票都要通知）
                try:
                    import json
                    with open(src, 'r', encoding='utf-8') as f:
                        selection_data = json.load(f)
                    
                    stocks = selection_data.get('stocks', [])
                    from stock_notifier import send_selection_notice
                    if send_selection_notice(stocks, selection_data):
                        log(f"✅ 已发送选股通知到钉钉（选出{len(stocks)}支股票）")
                    else:
                        log("⚠️  发送选股通知失败")
                except Exception as e:
                    log(f"⚠️  发送选股通知异常: {e}")
        else:
            log(f"❌ 选股任务执行失败: {result.stderr}")
            
    except Exception as e:
        log(f"❌ 选股任务异常: {e}")


def run_stock_review():
    """执行复盘任务"""
    log("=" * 60)
    log("开始执行复盘任务...")
    
    try:
        result = subprocess.run(
            ["python3", "stock_review_v2.py"],
            cwd=CODE_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            log("✅ 复盘任务执行成功")
            
            # 发送钉钉通知
            try:
                today = datetime.now().strftime("%Y-%m-%d")
                # 检查多个可能的路径
                possible_paths = [
                    REVIEW_DIR / f"daily_review_{today}.json",
                    CODE_DIR.parent / "projects" / "stock-tracking" / "reviews" / f"daily_review_{today}.json",
                ]
                
                review_file = None
                for path in possible_paths:
                    if path.exists():
                        review_file = path
                        break
                
                if review_file:
                    import json
                    with open(review_file, 'r', encoding='utf-8') as f:
                        review_data = json.load(f)
                    
                    from stock_notifier import send_review_notice
                    if send_review_notice(review_data.get('review', {})):
                        log("✅ 已发送复盘通知到钉钉")
                    else:
                        log("⚠️  发送复盘通知失败")
                else:
                    log("⚠️  未找到复盘文件")
            except Exception as e:
                log(f"⚠️  发送复盘通知异常: {e}")
        else:
            log(f"❌ 复盘任务执行失败: {result.stderr}")
            
    except Exception as e:
        log(f"❌ 复盘任务异常: {e}")


def main():
    """主函数 - 检查时间并执行相应任务"""
    now = datetime.now()
    hour = now.hour
    weekday = now.weekday()  # 0=周一, 4=周五
    
    log(f"\n{'='*60}")
    log(f"定时任务检查 - {now.strftime('%Y-%m-%d %H:%M:%S')} (周{'一二三四五六日'[weekday]})")
    log(f"{'='*60}")
    
    # 8:00-9:00 - 执行选股
    if 8 <= hour < 9:
        if check_selection_done_today():
            log("⏭️  今天已完成选股，跳过")
        else:
            run_stock_selector()
    
    # 9:30-15:00 - 检查并启动交易监控
    if is_trading_hours():
        check_and_start_monitor()
    
    # 16:00-17:00 - 执行复盘
    if 16 <= hour < 17:
        if check_review_done_today():
            log("⏭️  今天已完成复盘，跳过")
        else:
            if check_selection_done_today():
                run_stock_review()
            else:
                log("⚠️  今天未完成选股，先执行选股...")
                run_stock_selector()
                run_stock_review()
    
    # 16:30-17:30 周五 - 执行周复盘
    if weekday == 4 and 16.5 <= hour < 17.5:
        log("📅 今天是周五，检查周复盘...")
        # 这里可以添加周复盘逻辑
    
    # 19:00-23:00 - 执行学习任务
    if 19 <= hour < 23:
        check_and_learn()
    
    log("\n定时任务检查完成")


def check_and_learn():
    """检查并执行学习任务"""
    try:
        from trading_learner import is_learning_time, has_learned_today
        
        if not is_learning_time():
            return
        
        if has_learned_today():
            log("⏭️  今天已完成学习，跳过")
            return
        
        log("=" * 60)
        log("开始执行学习任务...")
        
        # 导入并执行学习模块
        import trading_learner
        trading_learner.main()
        
    except Exception as e:
        log(f"❌ 学习任务异常: {e}")


if __name__ == "__main__":
    main()
