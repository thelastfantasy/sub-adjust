
import platform
import winsound
import tkinter as tk
from tkinter import scrolledtext
import chardet
import sys

def hide_console():
    """在 Windows 下隐藏控制台窗口"""
    if sys.platform == "win32":
        import ctypes
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)
            ctypes.windll.kernel32.CloseHandle(whnd)

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    result = chardet.detect(raw_data)
    return result['encoding']

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
        pass  # Linux sound handling can be added if needed
    elif system == "Darwin":
        pass  # macOS sound handling can be added if needed

def custom_messagebox(root, message):
    play_system_sound()
    custom_box = tk.Toplevel(root)
    custom_box.title("处理结果")
    tk.Label(custom_box, text=message, wraplength=300, justify=tk.LEFT).pack(padx=20, pady=20)
    button_frame = tk.Frame(custom_box)
    button_frame.pack(padx=10, pady=10)
    tk.Button(button_frame, text="确定", command=custom_box.destroy).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="退出", command=root.destroy).pack(side=tk.LEFT, padx=5)
    center_window(custom_box)
    custom_box.transient(root)
    custom_box.grab_set()
    root.wait_window(custom_box)

def display_errors(root, infos):
    play_system_sound()
    error_window = tk.Toplevel(root)
    error_window.title("错误信息")
    error_text = scrolledtext.ScrolledText(error_window, wrap=tk.CHAR, state='disabled')
    error_text.pack(expand=True, fill='both')
    error_text.config(state='normal')
    error_text.insert(tk.END, infos)
    error_text.config(state='disabled')
    center_window(error_window)