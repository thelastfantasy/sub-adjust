@echo off
@chcp 65001
@set PYTHONIOENCODING=utf-8

REM Check if Python is installed and accessible via environment variables
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python未安装或未正确配置环境变量，请先安装Python并确保其路径已添加到环境变量中。
    exit /b 1
)

REM Check if docopt is installed
python -m pip show docopt >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo docopt未安装，正在尝试安装...
    python -m pip install docopt
    if %ERRORLEVEL% NEQ 0 (
        echo docopt安装失败，请检查网络或pip配置。
        exit /b 1
    )
) else (
    echo docopt已安装，跳过安装步骤。
)

echo 所有依赖项已满足，可以运行程序。
exit /b 0
