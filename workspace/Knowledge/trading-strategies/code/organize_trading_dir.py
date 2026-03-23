#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整理trading目录结构
功能：将报告按股票名称分类到不同文件夹
"""

import os
import shutil
from pathlib import Path
import re

def organize_trading_directory():
    """整理trading目录"""
    trading_dir = Path('/root/.openclaw/workspace/trading')
    
    # 需要保留在根目录的文件
    keep_in_root = ['config.ini', 'OPTIMIZATION_SUMMARY.md']
    
    # 遍历所有markdown文件
    for md_file in trading_dir.glob('*.md'):
        # 跳过保留文件
        if md_file.name in keep_in_root:
            continue
        
        # 提取股票名称（格式：股票名称-日期-次数.md）
        match = re.match(r'(.+)-\d{4}-\d{2}-\d{2}-\d+\.md', md_file.name)
        if match:
            stock_name = match.group(1)
            
            # 创建股票文件夹
            stock_dir = trading_dir / stock_name
            stock_dir.mkdir(exist_ok=True)
            
            # 移动文件
            dest_file = stock_dir / md_file.name
            shutil.move(str(md_file), str(dest_file))
            print(f"✅ 移动: {md_file.name} -> {stock_name}/")

if __name__ == '__main__':
    print("=== 整理trading目录结构 ===\n")
    organize_trading_directory()
    print("\n✅ 整理完成！")
