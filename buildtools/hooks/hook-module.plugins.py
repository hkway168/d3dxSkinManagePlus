# -*- coding: utf-8 -*-
"""PyInstaller hook: 插件运行时依赖

插件是运行时从 ./plugins/<name>/main.py 动态加载的, PyInstaller 无法分析到插件的 import,
只会打包主程序本身用到的模块。这里把插件常用的标准库和已安装的第三方模块一并打包,
避免插件在打包后的程序中因缺少模块而加载失败。

模块 module.plugins 被打包时 PyInstaller 会自动应用本 hook (通过 --additional-hooks-dir)。
不存在的模块会被自动跳过, 不影响打包。
"""

import importlib.util

from PyInstaller.utils.hooks import collect_submodules


STDLIB = [
    # 常用基础
    "json", "re", "time", "datetime", "calendar", "shutil", "subprocess", "threading", "queue",
    "hashlib", "hmac", "secrets", "random", "uuid", "base64", "binascii", "struct", "copy",
    "glob", "fnmatch", "pathlib", "tempfile", "io", "string", "textwrap", "difflib", "pprint",
    "collections", "itertools", "functools", "operator", "bisect", "heapq", "math", "statistics",
    "decimal", "fractions", "enum", "dataclasses", "typing", "inspect", "traceback", "logging",
    "locale", "platform", "configparser", "csv", "html", "xml.etree.ElementTree", "xml.dom.minidom",
    # 压缩归档
    "zipfile", "tarfile", "gzip", "bz2", "lzma",
    # 并发与网络
    "concurrent.futures", "asyncio", "urllib.request", "urllib.parse", "http.client", "webbrowser",
    # 数据库
    "sqlite3",
    # Windows
    "ctypes", "ctypes.wintypes", "winreg", "winsound", "msvcrt",
    # 界面
    "tkinter", "tkinter.ttk", "tkinter.font", "tkinter.filedialog", "tkinter.messagebox",
    "tkinter.simpledialog", "tkinter.colorchooser", "tkinter.scrolledtext", "tkinter.dnd",
]

THIRD_PARTY = [
    # pywin32
    "win32api", "win32con", "win32gui", "win32process", "win32clipboard", "win32event", "win32file",
    "win32com.client", "pywintypes",
    # Pillow
    "PIL.Image", "PIL.ImageTk", "PIL.ImageGrab", "PIL.ImageDraw", "PIL.ImageFont", "PIL.ImageOps",
    "PIL.ImageFilter", "PIL.ImageEnhance", "PIL.ImageColor", "PIL.ImageChops",
    # requirements.txt 中的其他依赖
    # numpy 体积较大 (约 26 MB) 且主程序未使用, 不打包
    "windnd", "pygetwindow", "pynput", "pynput.keyboard", "pynput.mouse",
]

# ttkbootstrap 的命令行 / 主题转换工具不需要
TTKBOOTSTRAP_EXCLUDE = ("ttkbootstrap.__main__", "ttkbootstrap.cli", "ttkbootstrap.convert_theme")


def _exists(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None

    except Exception:
        return False


hiddenimports = [name for name in STDLIB + THIRD_PARTY if _exists(name)]

hiddenimports += collect_submodules(
    "ttkbootstrap",
    filter=lambda name: not name.startswith(TTKBOOTSTRAP_EXCLUDE),
    on_error="ignore",
)
