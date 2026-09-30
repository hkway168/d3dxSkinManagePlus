# -*- coding: utf-8 -*-
"""生成启动脚本 (移植自原版 tools.launch_script)

生成一个 .bat 批处理文件, 可以不打开管理器直接启动 3DMigoto 加载器和游戏。
加载器与游戏的查找方式与 "环境设置" 页面的启动按钮保持一致。
"""

# std
import os
import json
import locale
import threading
import tkinter.filedialog

# site
import ttkbootstrap

# local
import core
from constant import *
from window import dialogs


class containe ():
    action = threading.Lock()


RUNAS_LINE = '%1 start "" mshta vbscript:createobject("shell.application").shellexecute("""%~0""","::",,"runas",1)(window.close)&exit\n'


def find_loader() -> str:
    """返回 3DMigoto 加载器的绝对路径, 找不到时抛出 ValueError"""
    work = core.userenv.directory.work
    schemepath = os.path.join(work, "scheme.json")

    if os.path.isfile(schemepath):
        try:
            with open(schemepath, "r", encoding="utf-8") as fileobject:
                launch_name = json.loads(fileobject.read())["launch"]

        except Exception:
            raise ValueError("scheme 数据解释失败\n请检查用户 work 目录或 d3dx 版本")

    else:
        lst = os.listdir(work)
        for launch_name in ["3DMigotoLoader.exe", "3DMigoto Loader.exe"]:
            if launch_name in lst: break
        else:
            raise ValueError("无法找到 3DMigoto 加载器\n请检查用户 work 目录或 d3dx 版本")

    path = os.path.abspath(os.path.join(work, launch_name))
    if not os.path.isfile(path):
        raise ValueError(f"3DMigoto 加载器不存在\n{path}")

    return path


def build_script(runas: bool, loader: bool, game: bool) -> str:
    content = "@echo off\n"

    if runas:
        content += RUNAS_LINE

    if loader:
        launch_file = find_loader()
        content += f"cd /d \"{os.path.dirname(launch_file)}\"\n"
        content += f"start \"\" \"{launch_file}\"\n"

    if game:
        path = core.userenv.configuration.GamePath
        if not path:
            raise ValueError("未设置游戏路径\n请先在 环境设置 页面选择游戏程序")

        path = os.path.abspath(path)
        if not os.path.isfile(path):
            raise ValueError(f"游戏程序不存在\n{path}")

        content += f"cd /d \"{os.path.dirname(path)}\"\n"
        content += f"start \"\" \"{path}\"\n"

    return content


class LaunchScript (object):
    def __init__(self):
        if not containe.action.acquire(timeout=0.01):
            core.window.messagebox.showerror(title="操作已被阻止", message="请勿重复启动该工具")
            return

        self.window = ttkbootstrap.Toplevel("生成启动脚本")
        self.window.withdraw()
        self.window.transient(core.window.mainwindow)
        self.window.resizable(width=False, height=False)
        self.window.protocol("WM_DELETE_WINDOW", self.bin_close)
        dialogs._set_icon(self.window)

        self.v_runas = ttkbootstrap.BooleanVar(value=True)
        self.v_loader = ttkbootstrap.BooleanVar(value=True)
        self.v_game = ttkbootstrap.BooleanVar(value=True)

        self.frame_option = ttkbootstrap.Frame(self.window)
        self.frame_option.pack(side="top", fill="x", padx=15, pady=(15, 5))

        options = (
            (self.v_runas, "请求管理员权限", "3DMigoto 加载器需要管理员权限才能注入"),
            (self.v_loader, "启动 3DMigoto 加载器", "使用当前用户环境 work 目录中的加载器"),
            (self.v_game, "启动游戏", "使用 环境设置 中设置的游戏路径"),
        )

        for row, (variable, text, tips) in enumerate(options):
            check = ttkbootstrap.Checkbutton(self.frame_option, text=text, variable=variable, bootstyle="round-toggle", cursor="hand2")
            check.grid(row=row * 2, column=0, sticky="w", pady=(0 if row == 0 else 10, 0))
            ttkbootstrap.Label(self.frame_option, text=tips, bootstyle="secondary").grid(row=row * 2 + 1, column=0, sticky="w", padx=(25, 0))

        self.frame_button = ttkbootstrap.Frame(self.window)
        self.frame_button.pack(side="top", fill="x", padx=15, pady=(10, 15))

        self.button_sure = ttkbootstrap.Button(self.frame_button, text="生成", width=10, bootstyle="success-outline", cursor="hand2", command=self.bin_sure)
        self.button_cancel = ttkbootstrap.Button(self.frame_button, text="取消", width=10, bootstyle="warning-outline", cursor="hand2", command=self.bin_close)
        self.button_sure.pack(side="right")
        self.button_cancel.pack(side="right", padx=(0, 5))

        dialogs.center_window(self.window)
        self.window.deiconify()
        self.window.focus_set()


    def bin_sure(self, *_):
        runas, loader, game = self.v_runas.get(), self.v_loader.get(), self.v_game.get()

        if not (loader or game):
            core.window.messagebox.showerror(title="未选择启动项", message="请至少选择 启动加载器 或 启动游戏", parent=self.window)
            return

        # 先生成内容, 校验通过后再选择保存位置
        try:
            content = build_script(runas, loader, game)

        except ValueError as e:
            core.window.messagebox.showerror(title="无法生成脚本", message=str(e), parent=self.window)
            return

        filepath = tkinter.filedialog.asksaveasfilename(
            parent=self.window,
            title="生成脚本位置",
            initialfile=f"{core.userenv.user_name}.bat",
            defaultextension=".bat",
            filetypes=[("批处理文件", "*.bat")]
        )
        if not filepath: return

        # cmd 按系统代码页读取批处理, 使用系统首选编码保证中文路径正确
        try:
            with open(filepath, "w", encoding=locale.getpreferredencoding(False), errors="strict") as f:
                f.write(content)

        except UnicodeEncodeError:
            core.window.messagebox.showerror(title="保存失败", message="路径中包含系统代码页无法表示的字符\n请调整游戏或管理器的安装路径", parent=self.window)
            return

        except Exception as e:
            core.window.messagebox.showerror(title="保存失败", message=f"{e.__class__.__name__}: {e}", parent=self.window)
            return

        core.log.info(f"已生成启动脚本 {filepath}", L.WINDOW)
        core.window.messagebox.showinfo(title="生成完成", message=f"启动脚本已保存到\n{filepath}", parent=self.window)
        self.bin_close()


    def bin_close(self, *_):
        try: self.window.destroy()
        finally: containe.action.release()


__all__ = ["LaunchScript", "build_script", "find_loader"]
