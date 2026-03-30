# HTML Video Extractor

从HTML文件中提取Base64编码的视频数据，导出为MP4文件。

## 功能

- 拖放HTML文件到窗口即可提取视频
- 批量处理多个HTML文件
- 自动检测并解码Base64视频数据
- 提取的视频保存在HTML文件同目录下的 `extracted_videos` 文件夹

## 使用方法

### 方式一：直接运行EXE

下载 [Releases](../../releases) 中的EXE文件，双击运行，将HTML文件拖入窗口即可。

### 方式二：从源码运行

```bash
pip install tkinterdnd2
python extract_video.py
```

### 编译EXE

```bash
pip install pyinstaller tkinterdnd2
pyinstaller --onefile --windowed --name "视频提取工具" --add-data "%APPDATA%\Python\Python37\site-packages\tkinterdnd2\tkdnd;tkinterdnd2/tkdnd" --hidden-import tkinterdnd2 extract_video.py
```

编译后的EXE在 `dist/视频提取工具.exe`。
