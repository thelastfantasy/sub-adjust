@echo off
@chcp 65001
@set PYTHONIOENCODING=utf-8

REM Check if Python is installed and accessible via environment variables
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python未安装或未正确配置环境变量，请先安装Python并确保其路径已添加到环境变量中。
    exit /b 1
)

REM Try install deps from requirements.txt
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo 依赖项安装失败，请检查错误信息并手动安装依赖项。
    exit /b 1
)

echo 所有依赖项已满足，可以运行程序。
exit /b 0
