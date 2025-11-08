#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 用于验证爬虫功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gem_limitup_scraper import GEMLimitUpScraper
import pandas as pd
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)

def test_gem_stock_list():
    """测试获取创业板股票列表"""
    print("=== 测试获取创业板股票列表 ===")
    scraper = GEMLimitUpScraper()
    gem_stocks = scraper.get_gem_stock_list()
    
    if not gem_stocks.empty:
        print(f"✅ 成功获取 {len(gem_stocks)} 只创业板股票")
        print("前5只股票:")
        print(gem_stocks.head().to_string(index=False))
        return True
    else:
        print("❌ 获取创业板股票列表失败")
        return False

def test_single_stock_data():
    """测试获取单只股票数据"""
    print("\n=== 测试获取单只股票数据 ===")
    scraper = GEMLimitUpScraper()
    
    # 测试一只知名的创业板股票
    test_code = "300001"  # 特斯拉
    start_date = "2024-01-01"
    end_date = "2024-01-31"
    
    stock_data = scraper.get_stock_daily_data(test_code, start_date, end_date)
    
    if not stock_data.empty:
        print(f"✅ 成功获取股票 {test_code} 的数据")
        print(f"数据行数: {len(stock_data)}")
        print("前3行数据:")
        print(stock_data.head(3).to_string(index=False))
        return True
    else:
        print(f"❌ 获取股票 {test_code} 数据失败")
        return False

def test_limit_up_identification():
    """测试涨停识别功能"""
    print("\n=== 测试涨停识别功能 ===")
    scraper = GEMLimitUpScraper()
    
    # 测试一只股票的数据
    test_code = "300001"
    test_name = "测试股票"
    start_date = "2024-01-01"
    end_date = "2024-01-31"
    
    stock_data = scraper.get_stock_daily_data(test_code, start_date, end_date)
    
    if not stock_data.empty:
        limit_up_records = scraper.identify_limit_up_stocks(stock_data, test_code, test_name)
        
        if limit_up_records:
            print(f"✅ 识别到 {len(limit_up_records)} 条涨停记录")
            print("涨停记录:")
            for record in limit_up_records:
                print(f"  {record['涨停日期']}: {record['股票代码']} - {record['股票名称']} - 涨幅 {record['涨跌幅(%)']}%")
        else:
            print("ℹ️  该时间段内未识别到涨停记录")
        
        return True
    else:
        print("❌ 无法获取股票数据进行涨停识别测试")
        return False

def test_small_batch_scraping():
    """测试小批量爬取"""
    print("\n=== 测试小批量爬取（前10只股票） ===")
    scraper = GEMLimitUpScraper()
    
    # 修改爬虫方法，只处理前10只股票进行测试
    gem_stocks = scraper.get_gem_stock_list()
    if gem_stocks.empty:
        print("❌ 无法获取创业板股票列表")
        return False
    
    # 只取前10只股票进行测试
    test_stocks = gem_stocks.head(10)
    end_date = "2024-01-31"
    start_date = "2024-01-01"
    
    all_limit_up_records = []
    
    for idx, (_, stock) in enumerate(test_stocks.iterrows(), 1):
        stock_code = stock['code']
        stock_name = stock['name']
        
        print(f"测试股票 {idx}/10: {stock_code} - {stock_name}")
        
        stock_data = scraper.get_stock_daily_data(stock_code, start_date, end_date)
        
        if not stock_data.empty:
            limit_up_records = scraper.identify_limit_up_stocks(stock_data, stock_code, stock_name)
            all_limit_up_records.extend(limit_up_records)
    
    if all_limit_up_records:
        result_df = pd.DataFrame(all_limit_up_records)
        print(f"✅ 小批量测试完成，发现 {len(result_df)} 条涨停记录")
        print("涨停记录预览:")
        print(result_df[['股票代码', '股票名称', '涨停日期', '涨跌幅(%)']].head().to_string(index=False))
        return True
    else:
        print("ℹ️  小批量测试未发现涨停记录")
        return True  # 这不算失败

def main():
    """运行所有测试"""
    print("开始运行A股创业板涨停股票爬虫测试...")
    
    tests = [
        test_gem_stock_list,
        test_single_stock_data,
        test_limit_up_identification,
        test_small_batch_scraping
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"测试 {test_func.__name__} 失败")
        except Exception as e:
            print(f"测试 {test_func.__name__} 出错: {e}")
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✅ 所有测试通过！爬虫功能正常")
    else:
        print("⚠️  部分测试失败，请检查网络连接和API配置")

if __name__ == "__main__":
    main()