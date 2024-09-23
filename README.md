# About
This is a GUI tool for adjust subtitle timestamps written in Python. It can be used to adjust timestamp UTF-8 encoded .srt, .ass and .ssa subtitle files.
就是个字幕时间戳批量调整工具，各种文本编码处理起来太麻烦所以只支持UTF-8（有无BOM无所谓），编码错误会报错，省略了麻烦的选择文件功能，程序放到哪就自动针对该目录下的字幕文件进行操作。

# Requirements & Usage
1. Install Python 3, add python to PATH, and install pip，记得装Python 3，还有添加环境变量，可能也要装pip。
  - Windows: https://www.python.org/downloads/windows/
  - Linux: （下面是Copilot生成的，错了概不负责，根据自己的包管理器找正确的Python安装命令）
    - debian: `sudo apt-get install python3 python3-pip`
    - fedora: `sudo dnf install python3 python3-pip`
    - arch: `sudo pacman -S python python-pip`
    - gentoo: `sudo emerge -av dev-lang/python dev-python/pip`
    - suse: `sudo zypper install python3 python3-pip`
    - alpine: `sudo apk add python3 py3-pip`
2. Just run the start script
  - Windows: `start-windows.bat`，可以双击bat运行
  - Linux: `./start-linux.sh`
3. Check the GUI for the instructions