#!/bin/bash

# 安装依赖脚本
echo "================================"
echo "开始安装项目依赖..."
echo "================================"

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo "安装项目依赖..."
pip install -r requirements.txt

# 检查安装结果
if [ $? -eq 0 ]; then
    echo "================================"
    echo "依赖安装成功！"
    echo "================================"
    echo "下一步："
    echo "1. 修改 config.py 文件中的配置"
    echo "2. 运行 python run.py 初始化数据库"
    echo "3. 访问 /admin/register 创建管理员账号"
else
    echo "================================"
    echo "依赖安装失败，请检查错误信息"
    echo "================================"
    exit 1
fi