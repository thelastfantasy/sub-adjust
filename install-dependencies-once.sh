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

# 检查是否已安装 docopt
if ! python3 -m pip show docopt &> /dev/null; then
    echo "docopt 未安装，正在尝试安装..."
    pip3 install docopt
    if [ $? -ne 0 ]; then
        echo "docopt 安装失败，请检查网络或 pip 配置。"
        exit 1
    fi
else
    echo "docopt 已安装，跳过安装步骤。"
fi

echo "所有依赖项已满足，可以运行程序。"
