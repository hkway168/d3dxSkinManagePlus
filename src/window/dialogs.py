# -*- coding: utf-8 -*-
"""通用对话框 (移植自原版 widgets.dialogs)

- select_tags: 标签选择器, 从可选标签中勾选, 并允许额外输入
- text_edit:   多行文本编辑器
- center_window: 将窗口居中到父窗口
"""

# std
import tkinter

# site
import ttkbootstrap

# local
import core

# self
from . import dpi


def center_window(window, parent=None, width: int | None = None, height: int | None = None):
    """将 window 居中到 parent (默认主窗口) 上, 并限制在屏幕范围内"""
    parent = parent or core.window.mainwindow
    window.update_idletasks()

    w = width or window.winfo_reqwidth()
    h = height or window.winfo_reqheight()

    try:
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()

    except Exception:
        px, py, pw, ph = 0, 0, window.winfo_screenwidth(), window.winfo_screenheight()

    sw, sh = window.winfo_screenwidth(), window.winfo_screenheight()
    x = min(max(0, px + (pw - w) // 2), max(0, sw - w))
    y = min(max(0, py + (ph - h) // 2), max(0, sh - h))

    size = f"{w}x{h}" if width and height else ""
    window.geometry(f"{size}+{x}+{y}")


def _set_icon(window):
    try:
        window.iconbitmap(default=core.env.file.local.iconbitmap)
        window.iconbitmap(bitmap=core.env.file.local.iconbitmap)

    except Exception:
        ...


def split_rows(content: str | list) -> list[list[str]]:
    """将 "空格分隔 / 换行分行" 的内容解析为二维标签列表"""
    if isinstance(content, str):
        rows = content.split("\n")

    elif isinstance(content, list):
        rows = [x if isinstance(x, str) else " ".join(x) for x in content]

    else:
        raise TypeError("content must be a string, list of strings, or list of lists of strings.")

    result = []
    for row in rows:
        items = [x for x in row.replace("\t", " ").split(" ") if x]
        if items: result.append(items)

    return result


def split_tags(content: str | list) -> list[str]:
    """解析空格分隔的标签, 去重并保持顺序"""
    if isinstance(content, (list, tuple)): content = " ".join(content)
    return list(dict.fromkeys(x for x in str(content).split() if x))


class _ScrollFrame (ttkbootstrap.Frame):
    """可纵向滚动的容器, 内容放在 self.inner 中"""

    def __init__(self, master, **kwds):
        super().__init__(master, **kwds)

        self.canvas = tkinter.Canvas(self, highlightthickness=0, borderwidth=0)
        self.scrollbar = ttkbootstrap.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttkbootstrap.Frame(self.canvas)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self._window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner.bind("<Configure>", lambda *_: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self._window, width=e.width))
        self.bind_all_wheel()

        try: self.canvas.configure(background=core.window.style.colors.bg)
        except Exception: ...


    def bind_all_wheel(self):
        self.canvas.bind("<Enter>", lambda *_: self.canvas.bind_all("<MouseWheel>", self._on_wheel))
        self.canvas.bind("<Leave>", lambda *_: self.canvas.unbind_all("<MouseWheel>"))


    def _on_wheel(self, event):
        if self.canvas.yview() == (0.0, 1.0): return
        self.canvas.yview_scroll(int(-event.delta / 120), "units")


class SelectTags (object):
    """标签选择器 (模态)"""

    def __init__(self, title: str = "", optional: str | list = "", selected: str | list = "",
                 extracos: bool = True, *, width: int = 500, height: int = 400, parent=None):
        self.parent = parent or core.window.mainwindow
        self.extracos = extracos
        self.lst_optional = split_rows(optional)
        self.lst_selected = split_tags(selected)
        self.result: list[str] = list(self.lst_selected)
        self.vtags: dict[str, ttkbootstrap.BooleanVar] = {}

        self.window = ttkbootstrap.Toplevel(title)
        self.window.withdraw()
        self.window.transient(self.parent)
        _set_icon(self.window)

        self.scroll = _ScrollFrame(self.window)
        self.frame_option = ttkbootstrap.Frame(self.window)
        self.entry_extra = ttkbootstrap.Entry(self.window)
        self.label_extra = ttkbootstrap.Label(self.window, text="额外标签 (空格分隔):", anchor="w")
        self.button_sure = ttkbootstrap.Button(self.frame_option, text="确定", width=10, bootstyle="info-outline", command=self.bin_sure)
        self.button_cancel = ttkbootstrap.Button(self.frame_option, text="取消", width=10, bootstyle="warning-outline", command=self.bin_cancel)

        self.scroll.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        if self.extracos:
            self.label_extra.pack(side="top", fill="x", padx=5)
            self.entry_extra.pack(side="top", fill="x", padx=5, pady=(0, 5))
        self.frame_option.pack(side="top", fill="x", padx=5, pady=(0, 5))
        self.button_sure.pack(side="right")
        self.button_cancel.pack(side="right", padx=(0, 5))

        self._construct()

        self.window.protocol("WM_DELETE_WINDOW", self.bin_cancel)
        self.window.bind("<Escape>", self.bin_cancel)
        center_window(self.window, self.parent, dpi.scale(width), dpi.scale(height))
        self.window.deiconify()
        self.window.grab_set()
        self.window.focus_set()


    def _construct(self):
        if not self.lst_optional:
            ttkbootstrap.Label(self.scroll.inner, text="暂无可选标签\n可在 工具 -> 可选标签编辑 中添加", anchor="center").pack(fill="x", pady=10)

        for row, items in enumerate(self.lst_optional):
            frame = ttkbootstrap.Frame(self.scroll.inner)
            frame.pack(side="top", fill="x", pady=(0 if row == 0 else 5, 0))

            for column, tag in enumerate(items):
                if tag not in self.vtags:
                    self.vtags[tag] = ttkbootstrap.BooleanVar(value=tag in self.lst_selected)

                ttkbootstrap.Checkbutton(
                    frame, text=tag, variable=self.vtags[tag], bootstyle="success-outline-toolbutton"
                ).pack(side="left", padx=(0 if column == 0 else 5, 0))

        self.entry_extra.insert(0, " ".join(x for x in self.lst_selected if x not in self.vtags))


    def bin_sure(self, *_):
        result = [x for x in self.vtags if self.vtags[x].get()]
        if self.extracos: result += split_tags(self.entry_extra.get())
        self.result = list(dict.fromkeys(result))
        self.window.destroy()


    def bin_cancel(self, *_):
        self.result = list(self.lst_selected)
        self.window.destroy()


    def wait(self) -> list[str]:
        self.window.wait_window()
        return self.result


class TextEdit (object):
    """多行文本编辑器 (模态), 取消时返回 None"""

    def __init__(self, title: str = "", content: str = "", tips: str = "", *,
                 width: int = 500, height: int = 400, parent=None):
        self.parent = parent or core.window.mainwindow
        self.content = content
        self.result: str | None = None

        self.window = ttkbootstrap.Toplevel(title)
        self.window.withdraw()
        self.window.transient(self.parent)
        _set_icon(self.window)

        self.label_tips = ttkbootstrap.Label(self.window, text=tips, anchor="w", justify="left")
        self.text = ttkbootstrap.Text(self.window, width=0, height=0, undo=True)
        self.frame_option = ttkbootstrap.Frame(self.window)
        self.button_sure = ttkbootstrap.Button(self.frame_option, text="保存", width=10, bootstyle="info-outline", command=self.bin_sure)
        self.button_cancel = ttkbootstrap.Button(self.frame_option, text="取消", width=10, bootstyle="warning-outline", command=self.bin_cancel)

        if tips: self.label_tips.pack(side="top", fill="x", padx=5, pady=(5, 0))
        self.text.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        self.frame_option.pack(side="top", fill="x", padx=5, pady=(0, 5))
        self.button_sure.pack(side="right")
        self.button_cancel.pack(side="right", padx=(0, 5))

        self.text.insert("1.0", content)
        self.text.edit_reset()

        self.window.protocol("WM_DELETE_WINDOW", self.bin_cancel)
        center_window(self.window, self.parent, dpi.scale(width), dpi.scale(height))
        self.window.deiconify()
        self.window.grab_set()
        self.text.focus_set()


    def bin_sure(self, *_):
        self.result = self.text.get("1.0", "end-1c")
        self.window.destroy()


    def bin_cancel(self, *_):
        self.result = None
        self.window.destroy()


    def wait(self) -> str | None:
        self.window.wait_window()
        return self.result


def select_tags(title: str = "", optional: str | list = "", selected: str | list = "",
                extracos: bool = True, *, width: int = 500, height: int = 400, parent=None) -> list[str]:
    """标签选择器, 返回选中的标签列表; 取消时返回原选中项"""
    return SelectTags(title, optional, selected, extracos, width=width, height=height, parent=parent).wait()


def text_edit(title: str = "", content: str = "", tips: str = "", *,
              width: int = 500, height: int = 400, parent=None) -> str | None:
    """文本编辑器, 返回编辑后的内容; 取消时返回 None"""
    return TextEdit(title, content, tips, width=width, height=height, parent=parent).wait()


__all__ = ["center_window", "split_rows", "split_tags", "select_tags", "text_edit", "SelectTags", "TextEdit"]
