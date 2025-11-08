#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股创业板涨停股票爬虫
功能：查找近一个月以来中国A股创业板所有出现过涨停的股票
涨停标准：19% 以上涨幅（创业板涨停限制为20%）
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GEMLimitUpScraper:
    """创业板涨停股票爬虫类"""
    
    def __init__(self):
        """初始化爬虫"""
        self.limit_up_threshold = 19.0  # 涨停阈值（19%以上）
        self.output_file = "gem_limit_up_stocks.xlsx"
        
    def get_gem_stock_list(self):
        """获取创业板股票列表"""
        try:
            logger.info("正在获取创业板股票列表...")
            # 获取A股股票基本信息表
            stock_basic = ak.stock_info_a_code_name()
            # 筛选创业板股票（股票代码以300开头）
            gem_stocks = stock_basic[stock_basic['code'].str.startswith('300')]
            logger.info(f"获取到 {len(gem_stocks)} 只创业板股票")
            return gem_stocks
        except Exception as e:
            logger.error(f"获取创业板股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_stock_daily_data(self, stock_code, start_date, end_date):
        """获取单只股票的日线数据"""
        try:
            # akshare需要股票代码格式为sz300xxx
            ak_code = f"sz{stock_code}"
            # 获取股票日线数据
            stock_data = ak.stock_zh_a_hist(symbol=ak_code, 
                                           period="daily", 
                                           start_date=start_date.replace('-', ''), 
                                           end_date=end_date.replace('-', ''),
                                           adjust="qfq")  # 前复权
            return stock_data
        except Exception as e:
            logger.warning(f"获取股票 {stock_code} 数据失败: {e}")
            return pd.DataFrame()
    
    def identify_limit_up_stocks(self, stock_data, stock_code, stock_name):
        """识别涨停股票"""
        if stock_data.empty:
            return []
        
        limit_up_records = []
        
        for idx, row in stock_data.iterrows():
            # 计算涨跌幅
            if idx == 0:
                continue  # 第一天没有前一日数据，跳过
            
            prev_close = stock_data.iloc[idx-1]['收盘']
            current_close = row['收盘']
            pct_change = (current_close - prev_close) / prev_close * 100
            
            # 判断是否涨停（涨幅 >= 19%）
            if pct_change >= self.limit_up_threshold:
                record = {
                    '股票代码': stock_code,
                    '股票名称': stock_name,
                    '涨停日期': row['日期'],
                    '涨停价格': current_close,
                    '前日收盘价': prev_close,
                    '涨跌幅(%)': round(pct_change, 2),
                    '开盘价': row['开盘'],
                    '最高价': row['最高'],
                    '最低价': row['最低'],
                    '成交量': row['成交量'],
                    '成交额': row['成交额'],
                    '换手率(%)': row['换手率'] if '换手率' in row else None
                }
                limit_up_records.append(record)
        
        return limit_up_records
    
    def scrape_limit_up_stocks(self, days_back=30):
        """爬取涨停股票数据"""
        # 计算时间范围
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        logger.info(f"开始爬取 {start_date} 至 {end_date} 期间的创业板涨停股票数据")
        
        # 获取创业板股票列表
        gem_stocks = self.get_gem_stock_list()
        if gem_stocks.empty:
            logger.error("无法获取创业板股票列表")
            return pd.DataFrame()
        
        all_limit_up_records = []
        total_stocks = len(gem_stocks)
        
        for idx, (_, stock) in enumerate(gem_stocks.iterrows(), 1):
            stock_code = stock['code']
            stock_name = stock['name']
            
            logger.info(f"处理股票 {idx}/{total_stocks}: {stock_code} - {stock_name}")
            
            # 获取股票数据
            stock_data = self.get_stock_daily_data(stock_code, start_date, end_date)
            
            if not stock_data.empty:
                # 识别涨停记录
                limit_up_records = self.identify_limit_up_stocks(stock_data, stock_code, stock_name)
                all_limit_up_records.extend(limit_up_records)
            
            # 添加延时避免请求过于频繁
            time.sleep(0.1)
        
        # 转换为DataFrame
        if all_limit_up_records:
            result_df = pd.DataFrame(all_limit_up_records)
            # 按日期排序
            result_df = result_df.sort_values('涨停日期', ascending=False)
            logger.info(f"共发现 {len(result_df)} 条涨停记录")
        else:
            logger.warning("未发现涨停记录")
            result_df = pd.DataFrame()
        
        return result_df
    
    def save_to_excel(self, data, filename=None):
        """保存数据到Excel文件"""
        if filename is None:
            filename = self.output_file
        
        if data.empty:
            logger.warning("没有数据可保存")
            return
        
        try:
            # 创建Excel writer对象
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # 保存主数据
                data.to_excel(writer, sheet_name='涨停股票数据', index=False)
                
                # 创建统计汇总表
                summary_data = self.create_summary_data(data)
                summary_data.to_excel(writer, sheet_name='统计汇总', index=False)
                
                # 获取工作表对象并调整列宽
                worksheet = writer.sheets['涨停股票数据']
                self.adjust_column_width(worksheet, data)
                
                worksheet_summary = writer.sheets['统计汇总']
                self.adjust_column_width(worksheet_summary, summary_data)
            
            logger.info(f"数据已保存到 {filename}")
            logger.info(f"文件路径: {os.path.abspath(filename)}")
            
        except Exception as e:
            logger.error(f"保存Excel文件失败: {e}")
    
    def create_summary_data(self, data):
        """创建统计汇总数据"""
        if data.empty:
            return pd.DataFrame()
        
        summary_records = []
        
        # 按股票统计涨停次数
        stock_stats = data.groupby(['股票代码', '股票名称']).agg({
            '涨停日期': 'count',
            '涨跌幅(%)': ['max', 'mean', 'min'],
            '成交量': 'sum'
        }).round(2)
        
        stock_stats.columns = ['涨停次数', '最大涨幅(%)', '平均涨幅(%)', '最小涨幅(%)', '总成交量']
        stock_stats = stock_stats.reset_index()
        stock_stats = stock_stats.sort_values('涨停次数', ascending=False)
        
        # 按日期统计涨停股票数量
        date_stats = data.groupby('涨停日期').size().reset_index(name='涨停股票数')
        date_stats = date_stats.sort_values('涨停日期', ascending=False)
        
        summary_records.append({
            '统计类型': '总体统计',
            '统计项': '总涨停记录数',
            '数值': len(data)
        })
        
        summary_records.append({
            '统计类型': '总体统计',
            '统计项': '涉及股票数量',
            '数值': data['股票代码'].nunique()
        })
        
        summary_records.append({
            '统计类型': '总体统计',
            '统计项': '平均涨幅(%)',
            '数值': round(data['涨跌幅(%)'].mean(), 2)
        })
        
        summary_records.append({
            '统计类型': '总体统计',
            '统计项': '最大涨幅(%)',
            '数值': round(data['涨跌幅(%)'].max(), 2)
        })
        
        summary_df = pd.DataFrame(summary_records)
        
        return summary_df
    
    def adjust_column_width(self, worksheet, data):
        """调整Excel列宽"""
        for column in data.columns:
            max_length = max(
                data[column].astype(str).map(len).max(),
                len(str(column))
            )
            # 设置合适的列宽，最小10，最大30
            adjusted_width = min(max(max_length + 2, 10), 30)
            worksheet.column_dimensions[worksheet.cell(row=1, column=data.columns.get_loc(column) + 1).column_letter].width = adjusted_width
    
    def run(self, days_back=30):
        """运行爬虫"""
        logger.info("=== A股创业板涨停股票爬虫启动 ===")
        
        # 爬取数据
        result_data = self.scrape_limit_up_stocks(days_back)
        
        # 保存到Excel
        if not result_data.empty:
            self.save_to_excel(result_data)
            
            # 显示部分结果
            print("\n=== 涨停股票数据预览 ===")
            print(result_data.head(10).to_string(index=False))
            
            print(f"\n=== 统计信息 ===")
            print(f"总涨停记录数: {len(result_data)}")
            print(f"涉及股票数量: {result_data['股票代码'].nunique()}")
            print(f"平均涨幅: {result_data['涨跌幅(%)'].mean():.2f}%")
            print(f"最大涨幅: {result_data['涨跌幅(%)'].max():.2f}%")
            
        else:
            logger.warning("未找到任何涨停记录")
        
        logger.info("=== 爬虫执行完成 ===")
        return result_data


def main():
    """主函数"""
    try:
        # 创建爬虫实例
        scraper = GEMLimitUpScraper()
        
        # 运行爬虫（默认查询近30天）
        result = scraper.run(days_back=30)
        
        if result is not None and not result.empty:
            print(f"\n✅ 成功！数据已保存到 {scraper.output_file}")
        else:
            print("\n⚠️  未发现涨停数据")
            
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        print(f"\n❌ 程序执行失败: {e}")


if __name__ == "__main__":
    main()