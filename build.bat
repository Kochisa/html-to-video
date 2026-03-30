@echo off
cd /d "%~dp0"
pyinstaller --onefile --windowed --name "HTML_to_Video" --add-data "C:\Users\Moy\AppData\Roaming\Python\Python37\site-packages\tkinterdnd2\tkdnd;tkinterdnd2/tkdnd" --hidden-import tkinterdnd2 extract_video.py
echo.
echo 编译完成！EXE文件在 dist 目录下
pause
