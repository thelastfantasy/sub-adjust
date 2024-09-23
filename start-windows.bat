@echo off
setlocal

:: 检查是否安装了 Python 3
python --version 2>nul | findstr /r "Python 3.*" >nul
if %errorlevel% neq 0 (
    echo Python 3 is not installed.
    echo Installing Python 3 using winget...

    :: 检查是否安装了winget
    winget --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Winget is not installed or not available on this system.
        echo Please install Python 3 manually from https://www.python.org/downloads/
        pause
        exit /b
    )

    :: 使用winget安装Python
    winget install python3 -e --source winget
    if %errorlevel% neq 0 (
        echo Failed to install Python using winget.
        pause
        exit /b
    )
)

:: 隐藏命令行窗口并运行 Python 脚本
start "" /min cmd /c python adjust-timestamp.py

endlocal
