# About
字幕时间戳批量调整工具&srt转ass字幕工具，各种文本编码处理起来太麻烦所以只支持UTF-8（有无BOM无所谓），编码错误会报错，省略了麻烦的选择文件功能，程序放到哪就自动针对该目录下的字幕文件进行操作。

功能没sushi强大，但是主打一个轻巧、快速、简单。

# 说明
解压后如果是首次运行，执行对应平台的install_dependencies_once.bat (Windows) 或 install_dependencies_once.sh (Linux & MacOS) 即可简单安装依赖工具。

运行各个start_xxx.bat (Windows) 或 start_xxx.sh (Linux & MacOS) 即可启动对应工具的GUI版本。
sub_adjust命令行版本帮助请点击GUI界面右下角按钮查阅。

<font color="red">两款工具均只支持UTF-8编码字幕文件。</font>

sub_adjust: 
调轴工具，支持srt、ass、ssa三种格式，支持批量操作（默认读取程序目录下的字幕文件，不含子目录），可双击GUI运行亦可命令行运行。
命令行版本帮助请点击GUI界面右下角。

sub_converter:
srt转ass字幕工具，支持批量操作（默认读取程序目录下的字幕文件，不含子目录），可使用自定义元数据，目前仅可GUI运行。

timecode_converter:
字幕时间轴转换工具，支持srt、ass、ssa三种格式，支持选取文件操作，可双击GUI运行。选择或输入源字幕匹配的视频的对应帧率，然后选择想要匹配的目标视频的帧率，即可转换时间轴。

# 为什么不提供编译好的可执行文件？
编译后太大了，可以尝试自行编译

编译步骤：
1. 安装Git并克隆本项目源码
2. 执行install_dependencies_once.bat (Windows) 或 install_dependencies_once.sh (Linux & MacOS) 安装Python等依赖工具
3. 安装pyinstaller: `pip install -U pyinstaller`
4. 在项目目录下执行 `pyinstaller -w --onefile sub_adjust.py` ， `pyinstaller -w --onefile sub_converter.py` 即可在`./dist`目录下生成可执行文件