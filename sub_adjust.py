import os
import re
import tkinter as tk
from tkinter import (messagebox, scrolledtext)
import webbrowser
from docopt import docopt

from utils import center_window, custom_messagebox, display_errors

__version__ = 'sub_adjust v1.2.0'

USAGE = f"""
{__version__}

Usage:
  sub_adjust --offset <subtitle_shift_seconds> [--file <inputfile>] [--layers <layer_numbers>]
  sub_adjust --files <inputfiles>... [--layers <layer_numbers>]
  sub_adjust --version
  sub_adjust

Options:
  -t --offset <subtitle_shift_seconds>    字幕偏移量（单位：秒，1s = 1000ms），支持小数、负数、正数，负数为提前，正数为延后。此参数不存在时将不会进入命令行模式，而是进入图形界面
  -i --file <inputfile>                   输入字幕路径，同时也是输出路径，可以是相对路径或绝对路径。不存在的话会在当前活动目录下读取
  --files <inputfiles>...                 多文件模式，接收多个路径，--file 参数存在时会忽略 --files 参数
  --layers <layer_numbers>                可选参数，将时间调整仅应用到此处设置的Layer中。默认为 all
  --version                               显示版本信息
  -h --help                               显示帮助信息

Examples (二进制版本):
  # 将字幕提前2.5秒
  sub_adjust --offset -2.5 --file example.ass
  
  # 将多个字幕文件延后3秒
  sub_adjust --offset 3 --files "example.ass" "e:\sub-adjust\example.srt"
  
  # 显示版本信息
  sub_adjust --version


Examples (Python运行源码):
  # 将字幕提前2.5秒
  python sub_adjust.py --offset -2.5 --file example.ass
  
  # 将多个字幕文件延后3秒
  python sub_adjust.py --offset 3 --files "example.ass" "e:\sub-adjust\example.srt"
  
  # 显示版本信息
  python sub_adjust.py --version
"""



# 时间和文件处理函数
def time_to_ms(h, m, s, cs):
    return max(0, (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(cs) * 10)

def ms_to_time(ms):
    h = ms // 3600000
    m = (ms % 3600000) // 60000
    s = (ms % 60000) // 1000
    cs = (ms % 1000) // 10
    return f"{int(h)}:{int(m):02}:{int(s):02}.{int(cs):02}"

def srt_time_to_ms(h, m, s, ms):
    return max(0, (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms))

def ms_to_srt_time(ms):
    h = int(ms // 3600000)
    m = int((ms % 3600000) // 60000)
    s = int((ms % 60000) // 1000)
    ms = int(ms % 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def process_srt_file(filepath, adjusted_shift_value):
    try:
        with open(filepath, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()

        with open(filepath, 'w', encoding='utf-8') as outfile:
            for line in lines:
                if " --> " in line:
                    start_time, end_time = line.split(" --> ")
                    h1, m1, s1, ms1 = start_time.replace(',', ':').split(':')
                    h2, m2, s2, ms2 = end_time.replace(',', ':').split(':')

                    start_ms = srt_time_to_ms(h1, m1, s1, ms1) + adjusted_shift_value
                    end_ms = srt_time_to_ms(h2, m2, s2, ms2) + adjusted_shift_value

                    start_ms = max(0, start_ms)
                    end_ms = max(0, end_ms)

                    new_start_time = ms_to_srt_time(start_ms)
                    new_end_time = ms_to_srt_time(end_ms)

                    line = f"{new_start_time} --> {new_end_time}\n"
                outfile.write(line)
        return True, None
    except Exception as e:
        print(f"Error processing file {filepath}: {str(e)}")
        return False, str(e)

def parse_layers(layer_numbers):
    if not layer_numbers or layer_numbers.lower() == "all":
        return []
    return [int(layer) for layer in layer_numbers.split(',')]

def is_layer_included(layer, layers):
    if not layers:
        return True
    return layer in layers


def process_ass_ssa_file(filepath, adjusted_shift_value, layers):
    try:
        with open(filepath, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()

        with open(filepath, 'w', encoding='utf-8') as outfile:
            for line in lines:
                if line.startswith("Dialogue: "):
                    parts = line.split(",", 9)
                    
                    # 使用正则表达式处理SSA和ASS的layer部分
                    layer_match = re.match(r"Dialogue: (Marked=)?(\d+)", parts[0])
                    if layer_match:
                        layer = int(layer_match.group(2))
                    else:
                        print(f"Error parsing layer in line: {line}")
                        continue
                    
                    # 判断当前层是否在处理范围内
                    if is_layer_included(layer, layers):
                        start_time = parts[1]
                        end_time = parts[2]

                        try:
                            h1, m1, s1_cs1 = start_time.split(":")
                            s1, cs1 = s1_cs1.split(".")
                            h2, m2, s2_cs2 = end_time.split(":")
                            s2, cs2 = s2_cs2.split(".")
                        except ValueError:
                            print(f"Error parsing time: {start_time} or {end_time}")
                            continue

                        start_ms = time_to_ms(h1, m1, s1, cs1) + adjusted_shift_value
                        end_ms = time_to_ms(h2, m2, s2, cs2) + adjusted_shift_value

                        start_ms = max(0, start_ms)
                        end_ms = max(0, end_ms)

                        parts[1] = ms_to_time(start_ms)
                        parts[2] = ms_to_time(end_ms)

                    line = ",".join(parts)
                outfile.write(line)
        return True, None
    except Exception as e:
        print(f"Error processing file {filepath}: {str(e)}")
        return False, str(e)

def shift_times_in_directory(directory, shift_value, shift_direction, layer_numbers):
    if shift_direction is None:
        shift_direction = "delay"
    adjusted_shift_value = -shift_value if shift_direction == "advance" else shift_value
    layers = parse_layers(layer_numbers)

    subtitle_files = [f for f in os.listdir(directory) if f.endswith((".ass", ".ssa", ".srt"))]
    if not subtitle_files:
        messagebox.showwarning("警告", "目录中没有找到字幕文件。")
        return

    total_files = len(subtitle_files)
    success_count = 0
    failure_count = 0
    failure_reasons = []

    for file in subtitle_files:
        filepath = os.path.join(directory, file)
        if file.endswith(".ass") or file.endswith(".ssa"):
            success, reason = process_ass_ssa_file(filepath, adjusted_shift_value, layers)
        elif file.endswith(".srt"):
            success, reason = process_srt_file(filepath, adjusted_shift_value)
        
        if success:
            success_count += 1
        else:
            failure_count += 1
            failure_reasons.append(f"{file}: {reason}")

    result_message = (
        f"共处理 {total_files} 个文件。\n"
        f"成功处理 {success_count} 个文件。\n"
        f"失败处理 {failure_count} 个文件。\n"
    )

    if failure_count > 0:
        result_message += "\n失败原因:\n" + "\n".join(failure_reasons)
        display_errors(root, result_message)
    else:
        custom_messagebox(root, result_message)

def open_mail(event=None):
    webbrowser.open("mailto:i@kayanoai.net")

def show_usage(root):
    usage_window = tk.Toplevel(root)
    usage_window.title("命令行帮助")

    # 创建一个滚动文本框用于显示USAGE内容
    usage_text = scrolledtext.ScrolledText(usage_window, wrap=tk.CHAR, state='disabled')
    usage_text.pack(expand=True, fill='both')

    # 插入USAGE信息
    usage_text.config(state='normal')
    usage_text.insert(tk.END, USAGE)
    usage_text.config(state='disabled')

    # 将结果窗口置于屏幕中央
    center_window(usage_window)

# GUI部分
def start_ui():
    global root
    root = tk.Tk()
    root.title(f"{__version__} - 字幕时间轴调整")

    # 功能详细说明
    explanation = (
        "批量处理字幕时间轴程序\n\n"
        "该工具用于批量将当前目录中的所有ASS、SSA、SRT字幕文件的时间轴根据配置延迟或提前。\n\n"
        "使用方法：\n"
        "1.\u00A0输入时间偏移量（秒），支持小数。例如，输入\u00A0'10.5'\u00A0表示延迟或提前 10.5 秒。\n"
        "2.\u00A0选择调整方向。可以选择 '延后' 或 '提前'。\n"
        "3.\u00A0输入层号（Layer编号,\u00A0可选）。留空或输入\u00A0'all'\u00A0表示对所有层进行调整。输入特定的层号（用逗号分隔）只对特定层进行调整。\n"
        "4.\u00A0点击 '处理' 按钮，程序将处理当前目录中的所有 .ass、.ssa 和 .srt 文件，并根据配置调整字幕时间轴。\n\n"
        "注意：\n"
        "-\u00A0程序执行后会覆盖原始字幕文件，因此在运行程序之前建议备份文件。\n"
        "-\u00A0本工具假设所有字幕文件均使用\u00A0UTF-8\u00A0编码格式。请确保文件编码正确，以避免处理错误。"
    )
    tk.Label(root, text=explanation, wraplength=400, justify=tk.LEFT).grid(row=0, column=0, columnspan=3, padx=10, pady=10)

    # 偏移量输入
    tk.Label(root, text="时间偏移量（秒）:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
    shift_value_entry = tk.Entry(root)
    shift_value_entry.grid(row=1, column=1, padx=10, pady=5)
    shift_value_entry.insert(0, "10.5")

    # 调整方向选择 (上下排列)
    tk.Label(root, text="调整方向:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)
    direction = tk.StringVar(value="delay")
    tk.Radiobutton(root, text="延后", variable=direction, value="delay").grid(row=2, column=1, sticky=tk.W)
    tk.Radiobutton(root, text="提前", variable=direction, value="advance").grid(row=3, column=1, sticky=tk.W)

    # 层号输入
    tk.Label(root, text="层号（可选）:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.E)
    layer_entry = tk.Entry(root)
    layer_entry.grid(row=4, column=1, padx=10, pady=5)
    layer_entry.insert(0, "all")

    def on_submit():
        # 获取和处理时间偏移量输入
        shift_value_str = shift_value_entry.get().strip()
        if not shift_value_str:
            return  # 输入为空时不进行处理
        try:
            shift_value = float(shift_value_str)
        except ValueError:
            messagebox.showerror("错误", "时间偏移量必须是合法的数字（整数或浮点数）。")
            return

        layer_numbers = layer_entry.get()
        shift_times_in_directory(os.getcwd(), shift_value * 1000, direction.get(), layer_numbers)

    tk.Button(root, text="处理", command=on_submit).grid(row=5, columnspan=3, pady=10)

    # 联系作者
    contact_label = tk.Label(root, text="联系作者: i@kayanoai.net", fg="blue", cursor="hand2")
    contact_label.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky=tk.W)
    contact_label.bind("<Button-1>", open_mail)
    contact_label.bind("<Enter>", lambda e: contact_label.config(fg="red"))
    contact_label.bind("<Leave>", lambda e: contact_label.config(fg="blue"))

    # 添加按钮，显示USAGE
    usage_button = tk.Button(root, text="命令行帮助", command=lambda: show_usage(root))
    usage_button.grid(row=6, column=2, padx=10, pady=10, sticky=tk.E)

    center_window(root)  # 将主窗口置于屏幕中央
    root.mainloop()

def main():
    # 使用 options_first=True 确保没有参数时不会直接触发 Usage 输出
    args = docopt(USAGE, version=__version__, options_first=True)

    input_file = args["--file"]
    input_files = args["--files"]

    # 如果用户请求版本信息，显示版本信息
    if args["--version"]:
        print(__version__)
        return  # 退出程序，避免启动GUI

    # 如果有 -- offset 参数，则执行命令行模式逻辑
    elif args["--offset"]:
        print("进入命令行模式...")
        shift_value = float(args["--offset"]) * 1000
        layer_numbers = args["--layers"]
        if input_file:
            if input_file.endswith(".ass") or input_file.endswith(".ssa"):
                process_ass_ssa_file(input_file, shift_value, layer_numbers)
            elif input_file.endswith(".srt"):
                process_srt_file(input_file, shift_value)
        elif input_files:
            for filepath in input_files:
                if filepath.endswith(".ass") or filepath.endswith(".ssa"):
                    process_ass_ssa_file(filepath, shift_value, layer_numbers)
                elif filepath.endswith(".srt"):
                    process_srt_file(filepath, shift_value)
        else:
            shift_times_in_directory(os.getcwd(), shift_value, None, layer_numbers)

    # 否则启动GUI（没有提供 --offset 时）
    else:
        print("正在启动GUI...")
        start_ui()

if __name__ == "__main__":
    main()

