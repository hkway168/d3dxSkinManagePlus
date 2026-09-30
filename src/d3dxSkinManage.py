# -*- coding: utf-8 -*-

import os
import sys
import ctypes

# 无控制台模式 (pythonw / PyInstaller --windowed) 下 stdout/stderr 为 None
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

import core


# ! 禁用 Windows 缩放
# * 让程序使用自己的 DPI 适配
try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception: ...


def main():
    core.run()


if __name__ == '__main__':
    main()
    sys.exit(0)
