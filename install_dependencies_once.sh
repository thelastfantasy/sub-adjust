#!/bin/bash
# for Linux & macOS
# 本脚本仅需运行一次，用于检查并安装程序运行所需的依赖项

# 检查 Python 是否已安装
if ! command -v python3 &> /dev/null; then
    echo "Python 未安装，请先安装 Python。"
    exit 1
fi

# 检查是否已安装 pip
if ! command -v pip3 &> /dev/null; then
    echo "pip 未安装，正在尝试使用 Python 安装 pip..."
    python3 -m ensurepip --upgrade
    if ! command -v pip3 &> /dev/null; then
        echo "ensurepip 安装失败，请手动安装 pip。"
        exit 1
    fi
fi

# Try install deps from requirements.txt
if [ -f requirements.txt ]; then
    echo "正在安装依赖项..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "依赖项安装失败，请手动安装依赖项。"
        exit 1
    fi
else
    echo "未找到 requirements.txt 文件，无法安装依赖项。"
    exit 1
fi

echo "所有依赖项已满足，可以运行程序。"
