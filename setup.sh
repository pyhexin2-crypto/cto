#!/bin/bash
# A股创业板涨停股票爬虫 - 环境设置脚本

echo "🚀 A股创业板涨停股票爬虫 - 环境设置"
echo "=================================="

# 检查Python版本
echo "📋 检查Python版本..."
python3 --version

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "⬆️  升级pip..."
pip install --upgrade pip

# 安装依赖
echo "📚 安装项目依赖..."
pip install -r requirements.txt

echo ""
echo "✅ 环境设置完成！"
echo ""
echo "🎯 使用方法："
echo "1. 直接运行爬虫: python run_scraper.py"
echo "2. 或者: source venv/bin/activate && python gem_limitup_scraper.py"
echo "3. 测试功能: python test_scraper.py"
echo "4. 生成示例: python create_sample.py"
echo ""
echo "📊 输出文件将保存为: gem_limit_up_stocks.xlsx"