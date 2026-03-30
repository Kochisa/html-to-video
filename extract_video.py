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
        html_files = []
        skipped_files = []
        for file_path in file_paths:
            file_path = file_path.strip().strip("{}")
            if os.path.isdir(file_path):
                for root_dir, dirs, files in os.walk(file_path):
                    for f in files:
                        if f.lower().endswith('.html'):
                            html_files.append(os.path.join(root_dir, f))
            elif file_path.lower().endswith('.html'):
                html_files.append(file_path)
            else:
                skipped_files.append(os.path.basename(file_path))

        if not html_files and skipped_files:
            messagebox.showwarning("警告", "没有找到HTML文件")
            return

        results = []
        total = len(html_files)
        for i, file_path in enumerate(html_files):
            self.status_label.config(text=f"正在处理 ({i + 1}/{total}): {os.path.basename(file_path)}")
            self.root.update()
            result = self.process_file(file_path)
            results.append(result)

        success = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'error']
        warning = [r for r in results if r['status'] == 'warning']

        if total == 1 and not skipped_files:
            r = results[0]
            if r['status'] == 'success':
                messagebox.showinfo("成功", f"视频已提取完成!\n\n大小: {r['size_mb']:.2f} MB\n保存到: {r['output_path']}")
            elif r['status'] == 'warning':
                messagebox.showwarning("警告", f"视频提取可能不完整\n文件大小与解码后数据大小不一致\n保存到: {r['output_path']}")
            else:
                messagebox.showerror("错误", r['message'])
        elif total > 1:
            lines = []
            if success:
                lines.append(f"✅ 成功: {len(success)} 个文件")
                for r in success:
                    lines.append(f"  • {os.path.basename(r['output_path'])} ({r['size_mb']:.2f} MB)")
            if warning:
                lines.append(f"⚠️ 警告: {len(warning)} 个文件")
                for r in warning:
                    lines.append(f"  • {os.path.basename(r['output_path'])} (可能不完整)")
            if failed:
                lines.append(f"❌ 失败: {len(failed)} 个文件")
                for r in failed:
                    lines.append(f"  • {r['file_name']}: {r['message']}")
            if skipped_files:
                lines.append(f"⏭️ 跳过: {len(skipped_files)} 个非HTML文件")

            summary = "\n".join(lines)
            if failed:
                messagebox.showwarning("处理完成", summary)
            else:
                messagebox.showinfo("处理完成", summary)

        self.status_label.config(text="准备就绪")

    def process_file(self, html_path):
        file_name = os.path.basename(html_path)
        try:
            base_name = os.path.splitext(file_name)[0]
            output_dir = os.path.join(os.path.dirname(html_path), "extracted_videos")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{base_name}.mp4")

            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()

            chunks_pattern = r'(?:chunks|videoChunks)\.push\("([^"]*)"\)'
            matches = re.findall(chunks_pattern, content)

            data_uri_pattern = r'data:video/[^;]+;base64,([A-Za-z0-9+/=]+)'
            data_uri_matches = re.findall(data_uri_pattern, content)

            if not matches and not data_uri_matches:
                return {'status': 'error', 'file_name': file_name, 'message': f"在文件 {file_name} 中未找到视频数据"}

            all_data = b''
            total_size = 0

            if matches:
                for i, chunk in enumerate(matches):
                    if len(chunk) % 4 != 0:
                        padding = 4 - (len(chunk) % 4)
                        chunk += '=' * padding
                    decoded_chunk = base64.b64decode(chunk)
                    total_size += len(decoded_chunk)
                    all_data += decoded_chunk
            else:
                for b64str in data_uri_matches:
                    decoded = base64.b64decode(b64str)
                    total_size += len(decoded)
                    all_data += decoded

            if not all_data:
                return {'status': 'error', 'file_name': file_name, 'message': "没有成功解码任何数据块"}

            with open(output_path, 'wb') as f:
                f.write(all_data)

            file_size = os.path.getsize(output_path)
            size_mb = file_size / (1024 * 1024)

            if file_size == total_size:
                return {'status': 'success', 'file_name': file_name, 'output_path': output_path, 'size_mb': size_mb}
            else:
                return {'status': 'warning', 'file_name': file_name, 'output_path': output_path, 'size_mb': size_mb}

        except Exception as e:
            return {'status': 'error', 'file_name': file_name, 'message': str(e)}


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = VideoExtractorApp(root)
    root.mainloop()
