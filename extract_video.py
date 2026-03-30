import os
import re
import base64
import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD


class VideoExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HTML to Video")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        self.main_frame = tk.Frame(root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.drop_frame = tk.Frame(
            self.main_frame,
            bg="#ffffff",
            relief=tk.GROOVE,
            bd=2,
            highlightbackground="#ccc",
            highlightthickness=2
        )
        self.drop_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        self.drop_label = tk.Label(
            self.drop_frame,
            text="拖动文件到这里解包",
            font=("微软雅黑", 14),
            fg="#999",
            bg="#ffffff"
        )
        self.drop_label.pack(expand=True)

        self.status_label = tk.Label(
            self.main_frame,
            text="准备就绪",
            font=("微软雅黑", 10),
            fg="#333",
            bg="#f0f0f0"
        )
        self.status_label.pack(pady=(0, 15))

        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind("<<DragEnter>>", self.on_drag_enter)
        self.drop_frame.dnd_bind("<<DragLeave>>", self.on_drag_leave)
        self.drop_frame.dnd_bind("<<Drop>>", self.on_drop)

    def on_drag_enter(self, event):
        self.drop_frame.config(bg="#e8f0fe", highlightbackground="#4a90d9")
        self.drop_label.config(fg="#4a90d9", bg="#e8f0fe")

    def on_drag_leave(self, event):
        self.drop_frame.config(bg="#ffffff", highlightbackground="#ccc")
        self.drop_label.config(fg="#999", bg="#ffffff")

    def on_drop(self, event):
        self.drop_frame.config(bg="#ffffff", highlightbackground="#ccc")
        self.drop_label.config(fg="#999", bg="#ffffff")

        file_paths = self.root.tk.splitlist(event.data)
        for file_path in file_paths:
            file_path = file_path.strip().strip("{}")
            if file_path.lower().endswith('.html'):
                self.process_file(file_path)
            else:
                messagebox.showwarning("警告", f"文件 {os.path.basename(file_path)} 不是HTML文件")

    def process_file(self, html_path):
        try:
            self.status_label.config(text=f"正在处理: {os.path.basename(html_path)}")
            self.root.update()

            base_name = os.path.splitext(os.path.basename(html_path))[0]
            output_dir = os.path.join(os.path.dirname(html_path), "extracted_videos")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{base_name}.mp4")

            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()

            chunks_pattern = r'chunks\.push\("([^"]*)"\)'
            matches = re.findall(chunks_pattern, content)

            if not matches:
                messagebox.showerror("错误", f"在文件 {os.path.basename(html_path)} 中未找到视频数据")
                self.status_label.config(text="准备就绪")
                return

            all_data = b''
            total_size = 0

            for i, chunk in enumerate(matches):
                if len(chunk) % 4 != 0:
                    padding = 4 - (len(chunk) % 4)
                    chunk += '=' * padding
                decoded_chunk = base64.b64decode(chunk)
                total_size += len(decoded_chunk)
                all_data += decoded_chunk

            if not all_data:
                messagebox.showerror("错误", "没有成功解码任何数据块")
                self.status_label.config(text="准备就绪")
                return

            with open(output_path, 'wb') as f:
                f.write(all_data)

            file_size = os.path.getsize(output_path)
            size_mb = file_size / (1024 * 1024)

            if file_size == total_size:
                messagebox.showinfo("成功", f"视频已提取完成!\n\n大小: {size_mb:.2f} MB\n保存到: {output_path}")
            else:
                messagebox.showwarning("警告", f"视频提取可能不完整\n文件大小与解码后数据大小不一致")

        except Exception as e:
            messagebox.showerror("错误", f"处理失败: {str(e)}")
        finally:
            self.status_label.config(text="准备就绪")


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = VideoExtractorApp(root)
    root.mainloop()
