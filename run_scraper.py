#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股创业板涨停股票爬虫 - 快速启动脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gem_limitup_scraper import main
    
    if __name__ == "__main__":
        print("🚀 启动A股创业板涨停股票爬虫...")
        print("=" * 50)
        main()
        
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ 程序运行出错: {e}")
    sys.exit(1)