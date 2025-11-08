#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建示例Excel文件
"""

import pandas as pd
from datetime import datetime, timedelta
import random

def create_sample_excel():
    """创建示例Excel文件"""
    
    # 模拟涨停数据
    sample_data = []
    stock_codes = ["300001", "300002", "300003", "300004", "300005", "300015", "300033", "300059", "300072", "300124"]
    stock_names = ["特锐德", "神州泰岳", "乐普医疗", "南风股份", "探路者", "爱尔眼科", "同花顺", "东方财富", "三聚环保", "汇川技术"]
    
    # 生成30天的涨停记录
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(15):  # 生成15条示例记录
        stock_idx = i % len(stock_codes)
        date_offset = random.randint(0, 29)
        limit_date = base_date + timedelta(days=date_offset)
        
        # 模拟价格数据
        prev_close = round(random.uniform(10, 50), 2)
        limit_price = round(prev_close * (1 + random.uniform(0.19, 0.20)), 2)
        pct_change = round((limit_price - prev_close) / prev_close * 100, 2)
        
        record = {
            '股票代码': stock_codes[stock_idx],
            '股票名称': stock_names[stock_idx],
            '涨停日期': limit_date.strftime('%Y-%m-%d'),
            '涨停价格': limit_price,
            '前日收盘价': prev_close,
            '涨跌幅(%)': pct_change,
            '开盘价': round(prev_close * random.uniform(0.98, 1.02), 2),
            '最高价': limit_price,
            '最低价': round(prev_close * random.uniform(0.95, 0.99), 2),
            '成交量': random.randint(5000000, 50000000),
            '成交额': round(limit_price * random.randint(5000000, 50000000), 0),
            '换手率(%)': round(random.uniform(2, 15), 2)
        }
        sample_data.append(record)
    
    # 转换为DataFrame并排序
    df = pd.DataFrame(sample_data)
    df = df.sort_values('涨停日期', ascending=False)
    
    # 创建统计汇总数据
    summary_records = [
        {'统计类型': '总体统计', '统计项': '总涨停记录数', '数值': len(df)},
        {'统计类型': '总体统计', '统计项': '涉及股票数量', '数值': df['股票代码'].nunique()},
        {'统计类型': '总体统计', '统计项': '平均涨幅(%)', '数值': round(df['涨跌幅(%)'].mean(), 2)},
        {'统计类型': '总体统计', '统计项': '最大涨幅(%)', '数值': round(df['涨跌幅(%)'].max(), 2)},
        {'统计类型': '总体统计', '统计项': '最小涨幅(%)', '数值': round(df['涨跌幅(%)'].min(), 2)},
        {'统计类型': '总体统计', '统计项': '总成交额(亿元)', '数值': round(df['成交额'].sum() / 100000000, 2)}
    ]
    
    summary_df = pd.DataFrame(summary_records)
    
    # 保存到Excel
    with pd.ExcelWriter("gem_limit_up_stocks_sample.xlsx", engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='涨停股票数据', index=False)
        summary_df.to_excel(writer, sheet_name='统计汇总', index=False)
        
        # 调整列宽
        worksheet = writer.sheets['涨停股票数据']
        for column in df.columns:
            max_length = max(
                df[column].astype(str).map(len).max(),
                len(str(column))
            )
            adjusted_width = min(max(max_length + 2, 10), 30)
            col_letter = worksheet.cell(row=1, column=df.columns.get_loc(column) + 1).column_letter
            worksheet.column_dimensions[col_letter].width = adjusted_width
        
        worksheet_summary = writer.sheets['统计汇总']
        for column in summary_df.columns:
            max_length = max(
                summary_df[column].astype(str).map(len).max(),
                len(str(column))
            )
            adjusted_width = min(max(max_length + 2, 10), 30)
            col_letter = worksheet.cell(row=1, column=summary_df.columns.get_loc(column) + 1).column_letter
            worksheet_summary.column_dimensions[col_letter].width = adjusted_width
    
    print(f"✅ 示例Excel文件已创建: gem_limit_up_stocks_sample.xlsx")
    print(f"包含 {len(df)} 条涨停记录")
    print("\n数据预览:")
    print(df[['股票代码', '股票名称', '涨停日期', '涨跌幅(%)', '涨停价格']].head().to_string(index=False))
    
    return df

if __name__ == "__main__":
    create_sample_excel()