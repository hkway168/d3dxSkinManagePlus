# -*- coding: utf-8 -*-

# std
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

from constant import *

import core


mainwindow = ttkbootstrap.Window()
# mainwindow = tkinterdnd2.TkinterDnD.Tk()
# mainwindow.overrideredirect(True)
messagebox = Messagebox(mainwindow)
annotation_toplevel = AnnotationToplevel()

treeview_thumbnail = core.module.image.ImageTkThumbnailGroup(40, 40)

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
    style.configure("Treeview", rowheight=48)

    mainwindow.title(core.env.MAIN_TITLE)
    _sw = mainwindow.winfo_screenwidth()
    _sh = mainwindow.winfo_screenheight()
    _w, _h = 1280, 800
    _w, _h = 1440, 900
    mainwindow.geometry(f"{_w}x{_h}+{(_sw - _w) // 2}+{(_sh - _h) // 2 - 40}")
    mainwindow.minsize(960, 600)

    try:
        mainwindow.iconbitmap(default=core.env.file.local.iconbitmap)
        mainwindow.iconbitmap(bitmap=core.env.file.local.iconbitmap)

    except Exception as e:
        core.log.error(f"窗口图标设置异常", L.WINDOW)

    frame_title.pack(side="top", fill="x")
    frame_block.pack(side="top", fill="both", expand=True)
    frame_status.pack(side="bottom", fill="x")

    _alt_set = annotation_toplevel.register
    _alt_set(login.label_description, T.ANNOTATION_USER_DESCRIPTION, 2)
    _alt_set(login.button_login, T.ANNOTATION_LOGIN, 1)
    _alt_set(status.label_help, T.ANNOTATION_HELP, 1)
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
        interface.mods_warehouse.refresh
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
