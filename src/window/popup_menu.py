# -*- coding: utf-8 -*-
"""跟随 ttkbootstrap 主题的右键弹出菜单

tkinter.Menu 在 Windows 下为系统原生样式, 无法与程序主题保持一致,
因此使用无边框 Toplevel 自绘, 外观与悬浮提示 (AnnotationToplevel) 统一。
"""

import tkinter
import ttkbootstrap

import core

from . import dpi


class PopupMenu (object):
    def __init__(self, master):
        self.master = master
        self.toplevel = None
        self.frame = None
        self.__items = []
        self.__rows = []

    # -------------------------------------------------- 菜单项
    def clear(self):
        self.__items = []

    def add_command(self, label: str, command=None, enabled: bool = True):
        self.__items.append((label, command, enabled))

    # -------------------------------------------------- 构建
    def __colors(self):
        try:
            c = core.window.style.colors
            return c.bg, c.fg, c.selectbg, c.selectfg, c.secondary

        except Exception:
            return "#222222", "#ffffff", "#555555", "#ffffff", "#777777"

    def __ensure_toplevel(self):
        if self.toplevel is not None and self.toplevel.winfo_exists():
            return

        self.toplevel = ttkbootstrap.Toplevel()
        self.toplevel.withdraw()
        self.toplevel.overrideredirect(True)
        self.toplevel.attributes("-topmost", True)

        self.frame = ttkbootstrap.Frame(self.toplevel, borderwidth=2, relief="solid")
        self.frame.pack(fill="both", expand=True)

        self.toplevel.bind("<FocusOut>", self.__on_focus_out)
        self.toplevel.bind("<Escape>", lambda *_: self.close())

    def __build(self):
        for row in self.__rows: row.destroy()
        self.__rows = []

        bg, fg, sbg, sfg, dfg = self.__colors()
        S = dpi.scale

        inner = tkinter.Frame(self.frame, bg=bg)
        inner.pack(fill="both", expand=True, padx=S(2), pady=S(2))
        self.__rows.append(inner)

        for label, command, enabled in self.__items:
            row = tkinter.Label(
                inner, text=label, anchor="w", bg=bg, fg=fg if enabled else dfg,
                font="TkDefaultFont", padx=S(16), pady=S(5), cursor="hand2" if enabled else "arrow",
            )
            row.pack(fill="x")
            if not enabled: continue

            row.bind("<Enter>", lambda _, w=row: w.config(bg=sbg, fg=sfg))
            row.bind("<Leave>", lambda _, w=row: w.config(bg=bg, fg=fg))
            row.bind("<ButtonRelease-1>", lambda _, cmd=command: self.__invoke(cmd))

    # -------------------------------------------------- 显示 / 关闭
    def popup(self, x: int, y: int):
        if not self.__items: return

        self.__ensure_toplevel()
        self.__build()

        self.toplevel.update_idletasks()
        w = self.toplevel.winfo_reqwidth()
        h = self.toplevel.winfo_reqheight()
        sw = self.toplevel.winfo_screenwidth()
        sh = self.toplevel.winfo_screenheight()

        x = x - w if x + w > sw else x
        y = y - h if y + h > sh else y

        self.toplevel.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.toplevel.deiconify()
        self.toplevel.lift()
        self.toplevel.focus_force()

    def close(self):
        if self.toplevel is None: return
        try: self.toplevel.withdraw()
        except Exception: ...

    def is_visible(self) -> bool:
        try: return bool(self.toplevel and self.toplevel.winfo_viewable())
        except Exception: return False

    def __on_focus_out(self, *_):
        # 焦点离开菜单 (点击其他位置 / 切换窗口) 时关闭
        self.toplevel.after(10, self.__check_focus)

    def __check_focus(self):
        try: focus = self.toplevel.focus_get()
        except Exception: focus = None

        if focus is None or not str(focus).startswith(str(self.toplevel)):
            self.close()

    def __invoke(self, command):
        self.close()
        if command is not None:
            self.master.after(0, command)
