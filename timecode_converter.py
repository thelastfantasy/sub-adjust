import os
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
import webbrowser
from utils import center_window, display_errors, custom_messagebox
import queue

__version__ = 'timecode_converter v0.1'

USAGE = f"""
{__version__}
Usage:
  timecode_converter --help
  timecode_converter --version
Options:
  --version                               显示版本信息
  -h --help                               显示帮助信息
"""

COMMON_FRAMERATES = ["23.976", "24", "24.417", "25", "29.97", "30", "50", "59.94", "60", "120"]

def parse_time_to_ms(time_str):
    """
    将时间格式 (h:mm:ss.cs) 转换为毫秒。
    """
    h, m, s_cs = time_str.split(":")
    s, cs = s_cs.split(".")

    # 根据毫秒的实际位数处理
    if len(cs) == 2:
        cs = cs.ljust(3, '0')  # 补齐到三位（毫秒），如果不足三位则补0
        ms = int(cs)
    elif len(cs) == 3:
        ms = int(cs)  # 直接是毫秒
    else:
        raise ValueError("Unsupported subtitle time format")

    return max(0, (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + ms)

def convert_time(time_str, source_rate, target_rate):
    """
    将时间格式根据源帧率和目标帧率转换。
    """
    ms = parse_time_to_ms(time_str)
    converted_ms = round(ms * (source_rate / target_rate))
    h = int(converted_ms // 3600000)
    m = int((converted_ms % 3600000) // 60000)
    s = int((converted_ms % 60000) // 1000)
    ms_remainder = int(converted_ms % 1000)

    if len(time_str.split('.')[-1]) == 2:
        cs = str(round(ms_remainder / 10)).zfill(2)  # 保留两位 centiseconds，四舍五入
        return f"{h}:{m:02}:{s:02}.{cs}"
    else:
        return f"{h:02}:{m:02}:{s:02},{ms_remainder:03}"

def process_file(filepath, source_rate, target_rate):
    """
    进行帧率转换的过程。保留原始文件，转换后的文件使用.transformed.作为名称后缀。
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()

        new_lines = []
        for line in lines:
            if " --> " in line:  # 处理 SRT
                start_time, end_time = line.split(" --> ")
                new_start_time = convert_time(start_time, source_rate, target_rate)
                new_end_time = convert_time(end_time, source_rate, target_rate)
                new_lines.append(f"{new_start_time} --> {new_end_time}\n")
            elif line.startswith("Dialogue: "):
                parts = line.split(",", 9)
                start_time, end_time = parts[1], parts[2]
                parts[1] = convert_time(start_time, source_rate, target_rate)
                parts[2] = convert_time(end_time, source_rate, target_rate)
                new_lines.append(",".join(parts))
            else:
                new_lines.append(line)

        save_directory = os.path.dirname(filepath)
        new_filepath = os.path.join(save_directory, f"{os.path.basename(filepath)}.{target_rate}-converted.{filepath.split('.')[-1]}")
        with open(new_filepath, 'w', encoding='utf-8') as outfile:
            outfile.writelines(new_lines)

        return True, None
    except Exception as e:
        return False, str(e)

def on_convert():
    filepaths = selected_files_text.get('1.0', tk.END).strip().split('\n')
    if not filepaths or filepaths == ['']:  # 检查是否选择了文件
        messagebox.showerror("错误", "请先选择需要转换的字幕文件。")
        return
    # 表单检查
    if not source_framerate_combo.get() or not target_framerate_combo.get():
        messagebox.showerror("错误", "源帧率和目标帧率不能为空。")
        return
    try:
        source_rate = float(source_framerate_combo.get())
    except ValueError:
        messagebox.showerror("错误", "源帧率必须是有效的数字。")
        return
    try:
        target_rate = float(target_framerate_combo.get())
    except ValueError:
        messagebox.showerror("错误", "目标帧率必须是有效的数字。")
        return

    result_queue = queue.Queue()

    def process_files():
        total_files = len(filepaths)
        success_count = 0
        failure_count = 0
        failure_reasons = []

        for filepath in filepaths:
            success, reason = process_file(filepath, source_rate, target_rate)
            if success:
                success_count += 1
            else:
                failure_count += 1
                failure_reasons.append(f"{filepath}: {reason}")

        result_message = (
            f"运行完毕。\n"
            f"共处理 {total_files} 个文件。\n"
            f"成功处理 {success_count} 个文件。\n"
            f"失败处理 {failure_count} 个文件。\n"
        )

        if failure_count > 0:
            result_message += "\n失败原因:\n" + "\n".join(failure_reasons)
            result_queue.put(result_message)
        else:
            result_queue.put(result_message)

    def check_queue():
        try:
            result_message = result_queue.get_nowait()
            if result_message:
                if "失败原因" in result_message:
                    display_errors(root, result_message)
                else:
                    custom_messagebox(root, result_message)
        except queue.Empty:
            root.after(100, check_queue)

    threading.Thread(target=process_files, daemon=True).start()
    root.after(100, check_queue)

def open_mail(event=None):
    webbrowser.open("mailto:i@kayanoai.net")

def show_usage(root):
    usage_window = tk.Toplevel(root)
    usage_window.title("命令行帮助")

    usage_text = scrolledtext.ScrolledText(usage_window, wrap=tk.CHAR, state='disabled')
    usage_text.pack(expand=True, fill='both')

    usage_text.config(state='normal')
    usage_text.insert(tk.END, USAGE)
    usage_text.config(state='disabled')

    center_window(usage_window)

# GUI
root = tk.Tk()
root.title(f"{__version__} - 时间码转换工具")

# Program explanation
tk.Label(root, text="字幕帧率转换工具，支持ASS/SSA/SRT格式。", wraplength=400, justify=tk.LEFT).grid(row=0, column=0, columnspan=3, padx=10, pady=10)

# File selection
file_selection_label = tk.Label(root, text="选择字幕文件:")
file_selection_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)

def select_files():
    filepaths = filedialog.askopenfilenames(title="选择需要转换的字幕文件", filetypes=[("Subtitle Files", "*.ass *.ssa *.srt")])
    if filepaths:
        selected_files_text.delete(1.0, tk.END)
        selected_files_text.insert(tk.END, '\n'.join(filepaths))

file_selection_button = tk.Button(root, text="选择文件", command=select_files)
file_selection_button.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

# Selected files display
selected_files_text = scrolledtext.ScrolledText(root, height=5, wrap=tk.WORD)
selected_files_text.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky=tk.W)

# Source framerate
source_framerate_combo = ttk.Combobox(root, values=COMMON_FRAMERATES)
source_framerate_combo.set("23.976")
tk.Label(root, text="源帧率:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.E)
source_framerate_combo.grid(row=3, column=1, padx=10, pady=5)

# Target framerate
target_framerate_combo = ttk.Combobox(root, values=COMMON_FRAMERATES)
target_framerate_combo.set("")
tk.Label(root, text="目标帧率:").grid(row=3, column=2, padx=10, pady=5, sticky=tk.E)
target_framerate_combo.grid(row=3, column=3, padx=10, pady=5)

# Convert button
tk.Button(root, text="转换", command=on_convert).grid(row=4, columnspan=4, pady=10)

# Contact author
contact_label = tk.Label(root, text="联系作者: i@kayanoai.net", fg="blue", cursor="hand2")
contact_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)
contact_label.bind("<Button-1>", open_mail)
contact_label.bind("<Enter>", lambda e: contact_label.config(fg="red"))
contact_label.bind("<Leave>", lambda e: contact_label.config(fg="blue"))

# Usage button
# usage_button = tk.Button(root, text="命令行帮助", command=lambda: show_usage(root))
# usage_button.grid(row=5, column=3, padx=10, pady=10, sticky=tk.E)

center_window(root)
root.mainloop()
