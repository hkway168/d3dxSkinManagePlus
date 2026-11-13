# -*- coding: utf-8 -*-

# std
import os
import threading

# libs
import ttkbootstrap
# import tkinterdnd2

# self
from .messagebox import Messagebox
from .title import Title
from .status import Status
from .login import Login
from .block import Block
from .interface import Interface
from .annotation_toplevel import AnnotationToplevel
from . import dpi

from constant import *

import core


mainwindow = ttkbootstrap.Window()
# mainwindow = tkinterdnd2.TkinterDnD.Tk()
# mainwindow.overrideredirect(True)
dpi.initial(mainwindow)
messagebox = Messagebox(mainwindow)
annotation_toplevel = AnnotationToplevel()

treeview_thumbnail = core.module.image.ImageTkThumbnailGroup(dpi.thumbnail_size(), dpi.thumbnail_size())

frame_title = ttkbootstrap.Frame(mainwindow)
frame_status = ttkbootstrap.Frame(mainwindow)
frame_login = ttkbootstrap.Frame(mainwindow)
frame_block = ttkbootstrap.Frame(mainwindow)
frame_notebook = ttkbootstrap.Frame(mainwindow)


# title = Title(frame_title)
status = Status(frame_status)
login = Login(frame_login)
block = Block(frame_block)
interface = Interface(frame_notebook)

style = ttkbootstrap.Style()
style_theme_names = style.theme_names()

# 选中行背景 = 列表底色向前景色方向提亮 / 压暗的比例 (中性灰高亮, 不带色相)
# 深色主题取 0.18, 与旧版 darkly 的选中色 (#2f2f2f -> #555555) 基本一致
TREEVIEW_SELECT_MIX_DARK = 0.18
TREEVIEW_SELECT_MIX_LIGHT = 0.12


def _mix_color(base: str, overlay: str, ratio: float) -> str:
    """按 ratio 将 overlay 混合到 base 上, 返回 #rrggbb"""
    r1, g1, b1 = (v // 257 for v in mainwindow.winfo_rgb(base))
    r2, g2, b2 = (v // 257 for v in mainwindow.winfo_rgb(overlay))
    mix = lambda a, b: round(a + (b - a) * ratio)
    return f"#{mix(r1, r2):02x}{mix(g1, g2):02x}{mix(b1, b2):02x}"


def apply_treeview_select_style() -> None:
    """
    自定义 Treeview 选中行配色。

    主题默认的选中色在深色主题下是浅灰底 + 黑字, 且 style map 中的选中文字色会覆盖条目标签的文字色,
    导致 "正在使用" 等状态色在选中时丢失。这里改为中性灰高亮背景 (由列表底色向前景色混合得到, 不带色相),
    并移除选中状态的文字色, 让标签色保留。
    """
    try:
        colors = style.colors
        is_light = style.theme.mode == "light"
        ratio = TREEVIEW_SELECT_MIX_LIGHT if is_light else TREEVIEW_SELECT_MIX_DARK
        select_bg = _mix_color(colors.inputbg, colors.fg, ratio)

        foreground = [
            item for item in style.map("Treeview", "foreground")
            if "selected" not in " ".join(map(str, item[:-1])).split()
        ]
        style.map("Treeview", background=[("selected", select_bg)], foreground=foreground)

    except Exception as e:
        core.log.warn(f"Treeview 选中配色应用失败 {e.__class__.__name__}: {e}", L.WINDOW)


def apply_style() -> None:
    """应用主题相关的自定义样式, 切换主题后需要重新调用"""
    dpi.apply_style(style)
    apply_treeview_select_style()


def exec_in_main_thread(callobject, *args, **kwds):
    """
    在主线程中执行 callobject 并返回其结果。

    Tcl/Tk 只允许在创建解释器的线程中调用，
    子线程直接创建控件会抛出 RuntimeError: Calling Tcl from different apartment，
    因此子线程需要将界面操作交由主线程执行并等待其完成。
    """
    if threading.current_thread() is threading.main_thread():
        return callobject(*args, **kwds)

    event = threading.Event()
    box = {}

    def _call():
        try:
            box["result"] = callobject(*args, **kwds)

        except BaseException as e:
            box["exception"] = e

        finally:
            event.set()

    mainwindow.after(0, _call)
    event.wait()

    if "exception" in box:
        raise box["exception"]

    return box.get("result")


def initial():
    core.log.info("初始化主窗口...", L.WINDOW)

    style.theme_use(core.env.configuration.style_theme)
    apply_style()

    mainwindow.title(core.env.PROJECT)
    _sw = mainwindow.winfo_screenwidth()
    _sh = mainwindow.winfo_screenheight()
    _w = min(dpi.scale(1440), _sw - dpi.scale(40))
    _h = min(dpi.scale(900), _sh - dpi.scale(80))
    _x = max(0, (_sw - _w) // 2)
    _y = max(0, (_sh - _h) // 2 - dpi.scale(40))
    mainwindow.geometry(f"{_w}x{_h}+{_x}+{_y}")
    mainwindow.minsize(min(dpi.scale(1280), _w), min(dpi.scale(600), _h))

    _icon = core.env.file.local.iconbitmap
    if not os.path.isfile(_icon):
        core.log.warn(f"窗口图标文件 {_icon} 不存在, 使用系统默认图标", L.WINDOW)

    else:
        try:
            mainwindow.iconbitmap(default=_icon)
            mainwindow.iconbitmap(bitmap=_icon)

        except Exception as e:
            core.log.error(f"窗口图标设置异常 {e.__class__.__name__}: {e}", L.WINDOW)

    frame_title.pack(side="top", fill="x")
    frame_block.pack(side="top", fill="both", expand=True)
    frame_status.pack(side="bottom", fill="x")

    _alt_set = annotation_toplevel.register
    _alt_set(login.label_description, T.ANNOTATION_USER_DESCRIPTION, 2)
    _alt_set(login.button_login, T.ANNOTATION_LOGIN, 1)
    _alt_set(status.label_logout, T.ANNOTATION_LOGOUT, 1)
    interface.initial()




def ready_login():
    core.log.info("就绪", L.WINDOW)
    frame_block.pack_forget()
    frame_block.pack_forget()
    frame_login.pack(side="top", fill="both", expand=True)


def _login(__name):
    core.log.info("登录用户界面...", L.WINDOW)
    frame_login.pack_forget()
    frame_notebook.pack(side='top', fill='both', expand=True)
    status.set_userName(__name)
    status.set_logout_visible(True)


def _logout():
    core.log.info("退出用户界面...", L.WINDOW)

    # 清空用户相关的列表内容
    for callobject in [
        interface.mods_manage.update_classification_list,
        interface.mods_manage.update_objects_list,
        interface.mods_manage.update_choices_list,
    ]:
        try:
            callobject()

        except Exception:
            ...

    try:
        interface.mods_manage.sbin_update_preview(None)

    except Exception:
        ...

    frame_notebook.pack_forget()
    frame_login.pack(side="top", fill="both", expand=True)

    status.set_logout_visible(False)
    status.set_userName("/")
    status.set_status("-")
    login.label_description["text"] = ""
    login.refresh()
