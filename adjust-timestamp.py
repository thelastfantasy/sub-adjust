import os
import platform
import tkinter as tk
from tkinter import (messagebox, scrolledtext)
import webbrowser
import winsound

# 时间和文件处理函数
def time_to_ms(h, m, s, cs):
    return max(0, (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(cs) * 10)

def ms_to_time(ms):
    h = ms // 3600000
    m = (ms % 3600000) // 60000
    s = (ms % 60000) // 1000
    cs = (ms % 1000) // 10

    # 将浮点数转为整数
    h = int(h)
    m = int(m)
    s = int(s)
    cs = int(cs)

    # 正确格式化时间字符串
    formatted_time = f"{h}:{m:02}:{s:02}.{cs:02}"
    
    return formatted_time

def srt_time_to_ms(h, m, s, ms):
    return max(0, (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms))

def ms_to_srt_time(ms):
    h = int(ms // 3600000)
    m = int((ms % 3600000) // 60000)
    s = int((ms % 60000) // 1000)
    ms = int(ms % 1000)

    # 返回格式化为 hh:mm:ss,ms 格式的时间字符串
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

                    # 确保时间戳不会变成负数
                    start_ms = max(0, start_ms)
                    end_ms = max(0, end_ms)

                    # 将时间转换回 SRT 格式
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
                    parts = line.split(",", 9)  # 只分割前9个字段，保留文本内容不变
                    layer = int(parts[0].split(":")[1])
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

                        # 确保时间戳不会变成负数
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

def center_window(window):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    size = tuple(int(_) for _ in window.geometry().split('+')[0].split('x'))
    x = screen_width // 2 - size[0] // 2
    y = screen_height // 2 - size[1] // 2
    window.geometry(f"{size[0]}x{size[1]}+{x}+{y}")

def play_system_sound():
    system = platform.system()
    if system == "Windows":
        winsound.MessageBeep(winsound.MB_OK)
    elif system == "Linux":
        # 在这里添加适用于 Linux 的音效播放代码
        pass
    elif system == "Darwin":  # macOS
        # 在这里添加适用于 macOS 的音效播放代码
        pass
    else:
        # 不支持的操作系统
        pass

def custom_messagebox(root, message):
    # 播放系统完成音效
    play_system_sound()

    # 创建新的顶层窗口
    custom_box = tk.Toplevel(root)
    custom_box.title("处理结果")

    # 显示消息
    tk.Label(custom_box, text=message, wraplength=300, justify=tk.LEFT).pack(padx=20, pady=20)

    # 创建按钮容器
    button_frame = tk.Frame(custom_box)
    button_frame.pack(padx=10, pady=10)

    # 确定按钮
    tk.Button(button_frame, text="确定", command=custom_box.destroy).pack(side=tk.LEFT, padx=5)

    # 退出按钮
    tk.Button(button_frame, text="退出", command=root.destroy).pack(side=tk.LEFT, padx=5)

    center_window(custom_box)  # 将结果窗口置于屏幕中央
    custom_box.transient(root)  # 确保对话框在主窗口之上
    custom_box.grab_set()  # 阻止用户与其他窗口交互
    root.wait_window(custom_box)  # 直到对话框关闭

def display_errors(root, errors):
    # 播放系统完成音效
    play_system_sound()

    # 创建一个新的顶层窗口
    error_window = tk.Toplevel(root)
    error_window.title("错误信息")

    # 创建一个滚动文本框用于显示错误信息
    error_text = scrolledtext.ScrolledText(error_window, wrap=tk.WORD, state='disabled')
    error_text.pack(expand=True, fill='both')

    # 插入错误信息
    error_text.config(state='normal')
    error_text.insert(tk.END, errors)
    error_text.config(state='disabled')

    # 将结果窗口置于屏幕中央
    center_window(error_window)


def shift_times_in_directory(directory, shift_value, shift_direction, layer_numbers):
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
        # 使用自定义文本组件显示结果
        display_errors(root, result_message)
    else:
        # 所有文件处理成功，使用原本的自定义messagebox，并显示处理数量
        result_message = (
            f"共处理 {total_files} 个文件。\n"
            f"成功处理 {success_count} 个文件。\n"
        )
        custom_messagebox(root, result_message)


# 打开默认邮件客户端发送邮件
def open_mail(event=None):
    webbrowser.open("mailto:i@kayanoai.net")

# GUI部分
def main():
    global root
    root = tk.Tk()
    root.title("字幕时间轴调整")

    # 功能详细说明
    explanation = (
        "批量处理字幕时间轴脚本\n\n"
        "该工具用于批量将当前目录中的所有ASS、SSA、SRT字幕文件的时间轴根据配置延迟或提前。\n\n"
        "使用方法：\n"
        "1. 输入时间偏移量（秒），支持小数。例如，输入 '10.5' 表示延迟或提前10.5秒。\n"
        "2. 选择调整方向。可以选择 '延后' 或 '提前'。\n"
        "3. 输入层号（Layer编号, 可选）。留空或输入 'all' 表示对所有层进行调整。输入特定的层号（用逗号分隔）只对特定层进行调整。\n"
        "4. 点击 '处理' 按钮，脚本将处理当前目录中的所有 .ass、.ssa 和 .srt 文件，并根据配置调整字幕时间轴。\n\n"
        "注意：\n"
        "- 脚本执行后会覆盖原始字幕文件，因此在运行脚本之前建议备份文件。\n"
        "- 本工具假设所有字幕文件均使用 UTF-8 编码格式。请确保文件编码正确，以避免处理错误。"
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

    center_window(root)  # 将主窗口置于屏幕中央
    root.mainloop()

if __name__ == "__main__":
    main()
