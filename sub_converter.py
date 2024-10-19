import re
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from utils import detect_encoding, center_window,  custom_messagebox, display_errors

# Constant for subtitle file extension
SUBTITLE_EXTENSION = '.srt'

# Version constant
VERSION = 'v0.0.1'

class SubtitleConverterApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"ASS 字幕转换器 {VERSION}")
        self.root.geometry("500x500")
        self.root.resizable(False, False)  # Disable maximizing and resizing
        self.root.pack_propagate(False)
        self.root.configure(padx=10, pady=10)  # Set window size
        center_window(self.root)
        
        # Program description
        self.description_text = tk.Label(root, text="该程序可将SRT字幕转换为ASS字幕，自动添加自定义元数据到输出字幕中。仅支持UTF-8编码，自动作用于程序当前目录。StyleName的查找逻辑：当只有一个样式时，使用该样式；如果存在多个样式，优先选择包含‘default’字符串（不区分大小写）的样式名，如果没有包含‘default’的样式名，则使用第一个样式名。",  justify=tk.LEFT, wraplength=480)
        self.description_text.pack(fill='x', pady=(0, 0), padx=(0, 0))  # Remove unnecessary padding at the top and bottom, fixed width
        
        # Input Field
        self.input_label = tk.Label(root, text="ASS 元数据模板:", anchor='w', justify='left')
        self.input_label.pack(pady=5, anchor='w', fill='x')
        
        self.input_text = scrolledtext.ScrolledText(root, height=15, width=50, wrap=tk.CHAR, undo=True)  # Set height larger, Add scrolling with undo support
        self.input_text.pack(pady=5, fill='both', expand=True)
        
        # Enable native right-click menu by binding system clipboard operations
        self.input_text.bind_class("Text", "<Control-c>", self.copy)
        self.input_text.bind_class("Text", "<Control-x>", self.cut)
        self.input_text.bind_class("Text", "<Control-v>", self.paste)
        self.input_text.bind_class("Text", "<Control-z>", self.undo)
        self.input_text.bind_class("Text", "<Control-y>", self.redo)
        self.input_text.bind("<Button-3>", self.show_context_menu)
        self.input_text.bind("<<Modified>>", self.update_undo_redo_buttons)
        
        default_template = """[Script Info]
Title: {filename}
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,方正隶变_GBK,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1
"""
        
        self.input_text.insert(tk.END, default_template)
        
        # Convert Button
        self.convert_button = tk.Button(root, text="转换字幕", command=self.convert_subtitles)
        self.convert_button.pack(pady=10)

        # Create context menu for the input text widget
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="剪切", command=self.cut)
        self.context_menu.add_command(label="复制", command=self.copy)
        self.context_menu.add_command(label="粘贴", command=self.paste)
        self.context_menu.add_command(label="撤销", command=self.undo, state=tk.DISABLED)
        self.context_menu.add_command(label="重做", command=self.redo, state=tk.DISABLED)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="全选", command=self.select_all)
        self.context_menu.add_command(label="删除", command=self.clear_all)

        # Author contact label
        contact_label = tk.Label(root, text="联系作者: i@kayanoai.net", fg="blue", cursor="hand2")
        contact_label.pack(anchor='w', pady=(0, 0))  # Remove unnecessary padding at the bottom
        contact_label.bind("<Button-1>", self.open_email)
        contact_label.bind("<Enter>", lambda e: contact_label.config(fg="red"))
        contact_label.bind("<Leave>", lambda e: contact_label.config(fg="blue"))

    def open_email(self, event=None):
        import webbrowser
        webbrowser.open("mailto:i@kayanoai.net")

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def cut(self, event=None):
        self.root.focus_get().event_generate("<<Cut>>")
        self.update_undo_redo_buttons()

    def copy(self, event=None):
        self.root.focus_get().event_generate("<<Copy>>")

    def paste(self, event=None):
        self.root.focus_get().event_generate("<<Paste>>")
        self.update_undo_redo_buttons()

    def undo(self, event=None):
        try:
            self.root.focus_get().event_generate("<<Undo>>")
        except tk.TclError:
            pass
        self.update_undo_redo_buttons()

    def redo(self, event=None):
        try:
            self.root.focus_get().event_generate("<<Redo>>")
        except tk.TclError:
            pass
        self.update_undo_redo_buttons()

    def select_all(self, event=None):
        self.input_text.tag_add("sel", "1.0", "end")

    def clear_all(self, event=None):
        self.input_text.delete("1.0", tk.END)
        self.update_undo_redo_buttons()

    def update_undo_redo_buttons(self, event=None):
        if self.input_text.edit_modified():
            self.context_menu.entryconfig("撤销", state=tk.NORMAL)
            try:
                self.context_menu.entryconfig("重做", state=tk.NORMAL if self.input_text.edit_redo() else tk.DISABLED)
            except tk.TclError:
                self.context_menu.entryconfig("重做", state=tk.DISABLED)
        else:
            self.context_menu.entryconfig("撤销", state=tk.DISABLED)
            self.context_menu.entryconfig("重做", state=tk.DISABLED)
        self.input_text.edit_modified(False)

    def convert_subtitles(self):
        template = self.input_text.get("1.0", tk.END)
        files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith(SUBTITLE_EXTENSION)]
        if not files:
            messagebox.showerror("错误", "当前目录中未找到字幕文件。")
            return
        
        total_files = len(files)
        success_count = 0
        failure_count = 0
        advanced_syntax_files = set()  # Use a set to avoid duplicates
        
        for file in files:
            try:
                encoding = detect_encoding(file)
                with open(file, 'r', encoding=encoding) as f:
                    content = f.readlines()
                
                filename, _ext = os.path.splitext(file)
                new_filename = f"{filename}.converted.ass"
                
                # Write to new ASS file
                with open(new_filename, 'w', encoding='utf-8') as f:
                    # Write metadata from the input field
                    metadata = template.format(filename=filename)
                    f.write(metadata + '\n')
                    f.write("[Events]\n")
                    f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
                    
                    # Extract styles from the metadata
                    style_lines = [line for line in metadata.splitlines() if line.startswith("Style:")]
                    style_names = [line.split(",")[0].split(":")[1].strip() for line in style_lines]
                    
                    # Determine which style to use based on rules
                    if len(style_names) == 1:
                        style_name = style_names[0]
                    else:
                        style_name = style_names[0]  # Default to the first style name if no "default" is found
                        for name in style_names:
                            if name.lower() == "default":
                                style_name = name
                                break
                            elif "default" in name.lower():
                                style_name = name
                                break
                    
                    # Write dialogue lines
                    i = 0
                    while i < len(content):
                        line = content[i].strip()

                        # If it's a timestamp line (including non-standard formats)
                        if re.match(r'\d{2}:\d{2}:\d{2}(,\d{1,3})? --> \d{2}:\d{2}:\d{2}(,\d{1,3})?', line):
                            start_end = line.split('-->')
                            start = start_end[0].strip().replace(',', '.')
                            end = start_end[1].strip().replace(',', '.')
                            
                            # Ensure milliseconds are two digits (truncation or padding)
                            if '.' in start:
                                start = start[:-1] if len(start.split('.')[-1]) > 2 else start.ljust(len(start) + (2 - len(start.split('.')[-1])), '0')
                            else:
                                start += '.00'
                            if '.' in end:
                                end = end[:-1] if len(end.split('.')[-1]) > 2 else end.ljust(len(end) + (2 - len(end.split('.')[-1])), '0')
                            else:
                                end += '.00'
                            
                            i += 1
                            
                            # Gather all subtitle lines until an empty line is found
                            dialogue_text = []
                            while i < len(content) and content[i].strip():
                                dialogue_text.append(content[i].strip())
                                i += 1
                            
                            # Join the lines into one subtitle text
                            full_dialogue = ' '.join(dialogue_text)
                            f.write(f"Dialogue: 0,{start},{end},{style_name},,0,0,0,,{full_dialogue}\n")

                            # Check for advanced syntax like {\an1} ~ {\an9}
                            if re.search(r'\{\\an[1-9]\}', full_dialogue):
                                advanced_syntax_files.add(file)
                        i += 1
                
                success_count += 1
            
            except Exception as e:
                failure_count += 1
                
        result_message = (
            f"共处理 {total_files} 个文件。\n"
            f"成功处理 {success_count} 个文件。\n"
            f"失败处理 {failure_count} 个文件。\n"
        )
        
        if advanced_syntax_files:
            result_message += "\n以下文件包含高级语法（如 {\\an1} ~ {\\an9}），需要手动进一步处理:\n" + "\n".join(advanced_syntax_files)
        
        display_errors(self.root, result_message)

if __name__ == "__main__":
    root = tk.Tk()
    app = SubtitleConverterApp(root)
    root.mainloop()
