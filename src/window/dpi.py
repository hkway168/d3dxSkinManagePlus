# -*- coding: utf-8 -*-
"""高 DPI 适配

程序启用了 DPI 感知 (SetProcessDpiAwareness), Tk 字体会按系统缩放放大,
但以像素为单位的尺寸 (行高、列宽、窗口大小、缩略图) 不会自动缩放,
在 4K 等高缩放比例下会导致文字重叠、区域过窄, 因此统一在此换算。
"""

import tkinter.font


BASE_DPI = 96.0

_factor = 1.0
_root = None


def initial(root) -> None:
    global _factor, _root
    _root = root

    try:
        dpi = float(root.winfo_fpixels("1i"))
        _factor = max(1.0, dpi / BASE_DPI)

    except Exception:
        _factor = 1.0


def factor() -> float:
    return _factor


def scale(value: int | float) -> int:
    """将 96 DPI 下的像素值换算为当前 DPI 下的像素值"""
    return int(round(value * _factor))


def line_height() -> int:
    """默认字体单行高度 (像素)"""
    heights = []
    for name in ("TkDefaultFont", "TkTextFont"):
        try:
            font = tkinter.font.Font(root=_root, name=name, exists=True)
            heights.append(int(font.metrics("linespace")))

        except Exception:
            ...

    return max(heights) if heights else scale(16)


def thumbnail_size() -> int:
    return scale(40)


def treeview_row_height(lines: int = 2) -> int:
    """容纳 lines 行文字与缩略图的 Treeview 行高"""
    return max(line_height() * lines, thumbnail_size()) + scale(8)


def apply_style(style) -> None:
    """应用与 DPI 相关的样式, 切换主题后需要重新调用"""
    style.configure("Treeview", rowheight=treeview_row_height(2))
