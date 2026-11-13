# -*- coding: utf-8 -*-

import os
import tkinter.filedialog

import win32api
import pywintypes
import ttkbootstrap

import core
import module
from constant import *


LOG_LEVEL = {
    "ALL": ~ 0x7F,
    "TRACE": ~ 0x40,
    "DEBUG": ~ 0x20,
    "INFO": 0x00,
    "WARN": 0x20,
    "SEVERE": 0x30,
    "ERROR": 0x40,
    "FATAL": 0x60,
    "OFF": 0x7F
}

ANNOTATION_LEVEL = {
    "全部": 3,
    "较多": 2,
    "较少": 1,
    "关闭": 0
}

THUMBNAIL_APPROXIMATE = {
    "精确匹配": K.APPROXIMATE.EXACT_ONLY,
    "图片名包含于对象名": K.APPROXIMATE.KEY_IN_ONLY,
    "对象名包含于图片名": K.APPROXIMATE.NAME_IN_ONLY,
    "双向包含": K.APPROXIMATE.BIDIRECTIONAL
}



class D3dxManage(object):
    def install(self, master):
        self.master = master
        self.style = ttkbootstrap.Style()

        BUTTON_WIDTH = 32

        self.labelframe_global = ttkbootstrap.LabelFrame(self.master, text="全局设置")
        self.labelframe_userenv = ttkbootstrap.LabelFrame(self.master, text="用户设置")

        self.labelframe_global.pack(side="left", fill="both", padx=10, pady=10, expand=True)
        self.labelframe_userenv.pack(side="left", fill="both", padx=(0, 10), pady=10, expand=True)


        self.frame_theme = ttkbootstrap.Frame(self.labelframe_global)
        self.label_theme = ttkbootstrap.Label(self.frame_theme, text="主题风格")
        self.combobox_theme = ttkbootstrap.Combobox(self.frame_theme)

        self.frame_theme.pack(side="top", fill="x", padx=10, pady=(10, 10))
        self.label_theme.pack(side="left", padx=(0, 5))
        self.combobox_theme.pack(side="right")

        self.frame_log_level = ttkbootstrap.Frame(self.labelframe_global)
        self.label_log_level = ttkbootstrap.Label(self.frame_log_level, text="日志等级")
        self.combobox_log_level = ttkbootstrap.Combobox(self.frame_log_level, values=[x for x in LOG_LEVEL])

        self.frame_log_level.pack(side="top", fill="x", padx=10, pady=(0, 10))
        self.label_log_level.pack(side="left", padx=(0, 5))
        self.combobox_log_level.pack(side="right")

        self.frame_annotation_level = ttkbootstrap.Frame(self.labelframe_global)
        self.label_annotation_level = ttkbootstrap.Label(self.frame_annotation_level, text="描述提示词数量")
        self.combobox_annotation_level = ttkbootstrap.Combobox(self.frame_annotation_level, values=[x for x in ANNOTATION_LEVEL])

        self.frame_annotation_level.pack(side="top", fill="x", padx=10, pady=(0, 10))
        self.label_annotation_level.pack(side="left", padx=(0, 5))
        self.combobox_annotation_level.pack(side="right")

        self.frame_thumbnail_approximate = ttkbootstrap.Frame(self.labelframe_global)
        self.label_thumbnail_approximate = ttkbootstrap.Label(self.frame_thumbnail_approximate, text="头像匹配算法")
        self.combobox_thumbnail_approximate = ttkbootstrap.Combobox(self.frame_thumbnail_approximate, state="readonly", values=[x for x in THUMBNAIL_APPROXIMATE])

        self.frame_thumbnail_approximate.pack(side="top", fill="x", padx=10, pady=(0, 10))
        self.label_thumbnail_approximate.pack(side="left", padx=(0, 5))
        self.combobox_thumbnail_approximate.pack(side="right")

        self.value_show_empty_objects = ttkbootstrap.BooleanVar(value=bool(core.env.configuration.show_empty_objects))

        self.frame_show_empty_objects = ttkbootstrap.Frame(self.labelframe_global)
        self.label_show_empty_objects = ttkbootstrap.Label(self.frame_show_empty_objects, text="显示空对象")
        self.checkbutton_show_empty_objects = ttkbootstrap.Checkbutton(
            self.frame_show_empty_objects,
            variable=self.value_show_empty_objects,
            bootstyle="round-toggle",
            command=self.bin_set_show_empty_objects
        )

        self.frame_show_empty_objects.pack(side="top", fill="x", padx=10, pady=(0, 10))
        self.label_show_empty_objects.pack(side="left", padx=(0, 5))
        self.checkbutton_show_empty_objects.pack(side="right")


        self.labelframe_xxmi = ttkbootstrap.LabelFrame(self.labelframe_userenv, text="XXMI Launcher")
        self.labelframe_gamepath = ttkbootstrap.LabelFrame(self.labelframe_userenv, text="游戏路径")

        self.labelframe_xxmi.pack(side="top", fill="x", padx=10, pady=10)
        self.labelframe_gamepath.pack(side="top", fill="x", padx=10, pady=(0, 10))

        self.entry_xxmi = ttkbootstrap.Entry(self.labelframe_xxmi, state="readonly")
        self.entry_xxmi.pack(side="top", fill="x", expand=True, padx=10, pady=10)

        self.frame_importer = ttkbootstrap.Frame(self.labelframe_xxmi)
        self.label_importer = ttkbootstrap.Label(self.frame_importer, text="模组导入器")
        self.combobox_importer = ttkbootstrap.Combobox(self.frame_importer, state="readonly", values=[module.xxmi.importer_display(x) for x in module.xxmi.IMPORTERS])
        self.label_xxmi_status = ttkbootstrap.Label(self.frame_importer, text="")

        self.frame_importer.pack(side="top", fill="x", padx=10, pady=(0, 10))
        self.label_importer.pack(side="left", padx=(0, 10))
        self.combobox_importer.pack(side="left")
        self.label_xxmi_status.pack(side="left", padx=(10, 0))

        self.button_choice_xxmi = ttkbootstrap.Button(self.labelframe_xxmi, text="选择 XXMI 目录", bootstyle="outline", width=BUTTON_WIDTH, command=self.bin_choice_xxmi)
        self.button_launch_xxmi = ttkbootstrap.Button(self.labelframe_xxmi, text="启动 XXMI Launcher", bootstyle="outline", width=BUTTON_WIDTH, command=self.bin_launch_xxmi)
        self.button_open_work = ttkbootstrap.Button(self.labelframe_xxmi, text="打开工作目录", bootstyle="outline", width=BUTTON_WIDTH, command=self.bin_open_work)
        self.button_choice_xxmi.pack(side="left", padx=(10, 10), pady=(0, 10))
        self.button_launch_xxmi.pack(side="left", padx=(0, 10), pady=(0, 10))
        self.button_open_work.pack(side="left", padx=(0, 10), pady=(0, 10))

        self.entry_gamepath = ttkbootstrap.Entry(self.labelframe_gamepath)#, bootstyle="light")
        self.entry_gamepath.pack(side="top", fill="x", expand=True, padx=10, pady=10)

        self.button_filechoice = ttkbootstrap.Button(self.labelframe_gamepath, text="文件选择工具", bootstyle="outline", width=BUTTON_WIDTH, command=self.bin_choice_file)
        self.button_gamestart = ttkbootstrap.Button(self.labelframe_gamepath, text="启动游戏", bootstyle="outline", width=BUTTON_WIDTH, command=self.bin_launch_game)
        self.button_open_game = ttkbootstrap.Button(self.labelframe_gamepath, text="打开游戏目录", bootstyle="outline", width=BUTTON_WIDTH, command=self.bin_open_game)
        self.button_filechoice.pack(side="left", padx=(10, 10), pady=(0, 10))
        self.button_gamestart.pack(side="left", padx=(0, 10), pady=(0, 10))
        self.button_open_game.pack(side="left", padx=(0, 10), pady=(0, 10))

        self.combobox_theme.bind("<FocusIn>", lambda *_: self.combobox_theme.selection_clear())
        self.combobox_importer.bind("<FocusIn>", lambda *_: self.combobox_importer.selection_clear())
        self.combobox_log_level.bind("<FocusIn>", lambda *_: self.combobox_log_level.selection_clear())
        self.combobox_annotation_level.bind("<FocusIn>", lambda *_: self.combobox_annotation_level.selection_clear())
        self.combobox_thumbnail_approximate.bind("<FocusIn>", lambda *_: self.combobox_thumbnail_approximate.selection_clear())

        self.combobox_importer.bind("<<ComboboxSelected>>", self.bin_choice_importer)
        self.combobox_theme.bind("<<ComboboxSelected>>", self.bin_set_style_theme)
        self.combobox_log_level.bind("<<ComboboxSelected>>", self.bin_set_log_level)
        self.combobox_annotation_level.bind("<<ComboboxSelected>>", self.bin_set_annotation_level)
        self.combobox_thumbnail_approximate.bind("<<ComboboxSelected>>", self.bin_set_thumbnail_approximate)


    def initial(self):
        # 配置修正在界面创建之后执行, 这里重新同步一次
        self.value_show_empty_objects.set(bool(core.env.configuration.show_empty_objects))
        self.sbin_update_thumbnail_approximate()

        _alt_set = core.window.annotation_toplevel.register

        _alt_set(self.combobox_theme, T.ANNOTATION_STYLE_THEME, 2)
        _alt_set(self.combobox_log_level, T.ANNOTATION_LOG_LEVEL, 2)
        _alt_set(self.combobox_annotation_level, T.ANNOTATION_ANNOTATION_LEVEL, 2)
        _alt_set(self.combobox_thumbnail_approximate, T.ANNOTATION_THUMBNAIL_APPROXIMATE, 2)
        _alt_set(self.label_thumbnail_approximate, T.ANNOTATION_THUMBNAIL_APPROXIMATE, 2)
        _alt_set(self.checkbutton_show_empty_objects, T.ANNOTATION_SHOW_EMPTY_OBJECTS, 2)
        _alt_set(self.label_show_empty_objects, T.ANNOTATION_SHOW_EMPTY_OBJECTS, 2)

        _alt_set(self.entry_xxmi, T.ANNOTATION_XXMI_ROOT, 2)
        _alt_set(self.button_choice_xxmi, T.ANNOTATION_XXMI_ROOT, 2)
        _alt_set(self.combobox_importer, T.ANNOTATION_XXMI_IMPORTER, 2)
        _alt_set(self.label_xxmi_status, T.ANNOTATION_XXMI_STATUS, 2)
        _alt_set(self.button_launch_xxmi, T.ANNOTATION_XXMI_LAUNCH, 2)
        _alt_set(self.button_open_work, T.ANNOTATION_D3DX_OPEN_WORK_DIR, 2)
        _alt_set(self.entry_gamepath, T.ANNOTATION_D3DX_SET_GAME_PATH, 2)
        _alt_set(self.button_filechoice, T.ANNOTATION_D3DX_SET_GAME_PATH, 2)
        _alt_set(self.button_gamestart, T.ANNOTATION_D3DX_START, 2)
        _alt_set(self.button_open_game, T.ANNOTATION_D3DX_GAME_WORK_DIR, 2)


    def __init__(self, master):
        self.master = master
        self.install(master)


    def update(self):
        core.log.info("更新 d3dx 环境设置信息...")

        self.combobox_theme.config(values=core.window.style_theme_names)
        self.combobox_theme.set(core.env.configuration.style_theme)

        for key, value in LOG_LEVEL.items():
            if core.env.configuration.log_level == value:
                self.combobox_log_level.set(key)
                break

        for key, value in ANNOTATION_LEVEL.items():
            if core.env.configuration.annotation_level == value:
                self.combobox_annotation_level.set(key)
                break

        self.sbin_update_thumbnail_approximate()
        self.value_show_empty_objects.set(bool(core.env.configuration.show_empty_objects))

        _GamePath = core.userenv.configuration.GamePath
        if _GamePath is None: _GamePath = "< 未设置 >"
        self.sbin_update_game_path(_GamePath)

        self.sbin_update_xxmi_root()

        importer = self.sbin_get_importer()
        self.combobox_importer.set(module.xxmi.importer_display(importer) if importer else "")
        self.sbin_update_xxmi_status()


    def sbin_update_game_path(self, text):
        self.entry_gamepath.delete(0, "end")
        self.entry_gamepath.insert(0, text)


    def sbin_update_thumbnail_approximate(self):
        current = core.env.configuration.thumbnail_approximate_algorithm
        for key, value in THUMBNAIL_APPROXIMATE.items():
            if current == value:
                self.combobox_thumbnail_approximate.set(key)
                break

        else:
            self.combobox_thumbnail_approximate.set("")


    def sbin_update_xxmi_root(self):
        root = module.xxmi.get_root()
        self.entry_xxmi.config(state="normal")
        self.entry_xxmi.delete(0, "end")
        self.entry_xxmi.insert(0, root if root else "< 未设置 >")
        self.entry_xxmi.config(state="readonly")


    def sbin_get_importer(self) -> str | None:
        """当前用户的导入器, 未设置时根据游戏路径推断"""
        importer = core.userenv.configuration.XXMIImporter
        if importer in module.xxmi.IMPORTERS:
            return importer

        importer = module.xxmi.detect_importer(core.userenv.configuration.GamePath)
        if importer is not None:
            core.userenv.configuration.XXMIImporter = importer
        return importer


    def sbin_update_xxmi_status(self):
        importer = self.sbin_get_importer()

        if module.xxmi.get_root() is None:
            text, style = "未设置 XXMI Launcher 目录", "danger"
        elif importer is None:
            text, style = "请选择模组导入器", "warning"
        elif not module.xxmi.is_bound(importer):
            text, style = "未指向工作目录（启动时自动同步）", "warning"
        elif not module.xxmi.is_installed():
            text, style = "未安装，请在 XXMI Launcher 中安装", "warning"
        else:
            text, style = "已就绪", "success"

        self.label_xxmi_status.config(text=f"● {text}", bootstyle=style)


    def sbin_sync_xxmi(self, silent: bool = False) -> bool:
        """将 XXMI Launcher 的导入器目录指向当前用户 work 目录, 已指向时跳过"""
        importer = self.sbin_get_importer()

        if module.xxmi.get_root() is None:
            if not silent: core.window.messagebox.showerror(title="XXMI Launcher", message="未设置 XXMI Launcher 目录\n请先点击「选择 XXMI 目录」")
            return False

        if importer is None:
            if not silent: core.window.messagebox.showerror(title="XXMI Launcher", message="未选择模组导入器")
            return False

        if module.xxmi.is_bound(importer):
            return True

        try:
            module.xxmi.bind_work(importer, core.userenv.configuration.GamePath)
            return True
        except module.xxmi.XXMIError as e:
            if not silent: core.window.messagebox.showerror(title="XXMI Launcher", message=str(e))
        except Exception as e:
            core.log.error(f"同步 XXMI Launcher 配置失败: {e}")
            if not silent: core.window.messagebox.showerror(title="XXMI Launcher", message=f"同步 XXMI Launcher 配置失败\n{e}")
        finally:
            self.sbin_update_xxmi_status()

        return False


    def bin_set_style_theme(self, *_):
        self.combobox_theme.selection_clear()
        value = self.combobox_theme.get()
        if value not in core.window.style_theme_names:
            return
        
        core.window.style.theme_use(value)
        core.env.configuration.style_theme = value
        core.window.apply_style()

        # 主题色变化后需要重新应用选择列表的状态配色
        try: core.window.interface.mods_manage.apply_choices_tag_style()
        except Exception: ...


    def bin_set_log_level(self, *_):
        self.combobox_log_level.selection_clear()
        key = self.combobox_log_level.get()
        value = LOG_LEVEL.get(key, None)
        if value is None:
            return
        core.env.configuration.log_level = value


    def bin_set_annotation_level(self, *_):
        self.combobox_annotation_level.selection_clear()
        key = self.combobox_annotation_level.get()
        value = ANNOTATION_LEVEL.get(key, None)
        if value is None:
            return
        core.env.configuration.annotation_level = value


    def bin_set_thumbnail_approximate(self, *_):
        self.combobox_thumbnail_approximate.selection_clear()
        value = THUMBNAIL_APPROXIMATE.get(self.combobox_thumbnail_approximate.get(), None)
        if value is None:
            return

        core.env.configuration.thumbnail_approximate_algorithm = value
        # 匹配结果变化后需要重新渲染分类与对象列表的缩略图
        core.construct.event.set_event(E.MODS_MANAGE_CACHE_REFRESHED)


    def bin_set_show_empty_objects(self, *_):
        core.env.configuration.show_empty_objects = bool(self.value_show_empty_objects.get())
        core.construct.event.set_event(E.MODS_MANAGE_CACHE_REFRESHED)


    def bin_selection_clear(self, *args, **kwds):
        self.combobox_importer.selection_clear()
        self.combobox_log_level.selection_clear()
        self.combobox_annotation_level.selection_clear()
        self.combobox_thumbnail_approximate.selection_clear()


    def bin_choice_xxmi(self, *args, **kwds):
        initialdir = module.xxmi.get_root() or os.path.abspath(".")
        path = tkinter.filedialog.askdirectory(title="选择 XXMI Launcher 所在目录", initialdir=initialdir)
        if not path: return

        root = module.xxmi.resolve_root(path)
        if root is None:
            core.window.messagebox.showerror(title="XXMI Launcher", message=f"所选目录中未找到 XXMI Launcher\n\n请选择包含「Resources\\Bin\\{module.xxmi.LAUNCHER_EXE_NAME}」\n或「{module.xxmi.CONFIG_FILE_NAME}」的目录")
            return

        module.xxmi.set_root(root)
        self.sbin_update_xxmi_root()

        if self.sbin_get_importer() is not None:
            self.combobox_importer.set(module.xxmi.importer_display(self.sbin_get_importer()))

        self.sbin_sync_xxmi(silent=True)
        self.sbin_update_xxmi_status()


    def bin_choice_importer(self, *args, **kwds):
        self.bin_selection_clear()
        importer = module.xxmi.importer_from_display(self.combobox_importer.get())
        if importer is None: return

        core.userenv.configuration.XXMIImporter = importer
        self.sbin_sync_xxmi(silent=True)
        self.sbin_update_xxmi_status()


    def bin_launch_xxmi(self, *args, **kwds):
        if not self.sbin_sync_xxmi(): return

        try:
            module.xxmi.launch(self.sbin_get_importer())
        except module.xxmi.XXMIError as e:
            core.window.messagebox.showerror(title="XXMI Launcher", message=str(e))
        except pywintypes.error as e:
            core.window.messagebox.showerror(title="异常捕获", message=f"{e.args[1]}: {e.args[0]}\n{e.args[2]}")
        finally:
            self.sbin_update_xxmi_status()


    def bin_open_work(self, *args, **kwds):
        win32api.ShellExecute(None, "open", os.path.abspath(core.userenv.directory.work), None, os.path.abspath(core.userenv.directory.work), 1)


    def bin_open_game(self, *args, **kwds):
        path = core.userenv.configuration.GamePath
        if path is None:
            core.window.messagebox.showerror(title="数据未设置", message="无法打开游戏目录\n未设置游戏路径")
            return

        path = os.path.dirname(path)

        win32api.ShellExecute(None, "open", path, None, path, 1)


    def bin_choice_file(self, *args, **kdws):
        choice_PATH = tkinter.filedialog.askopenfilename(title="选择应用程序", filetypes=[("应用程序", "*.exe"), ("All Files", "*")])
        choice_PATH = choice_PATH.replace("/", "\\")
        if not choice_PATH: return None
        choice_NAME = os.path.basename(choice_PATH)

        if choice_NAME[choice_NAME.rfind("."):] != ".exe":
            core.window.messagebox.showerror(title="错误的映像名", message="你选择了一个非 .exe 后缀名的文件\n请确认选择的是应用程序文件\n操作已被阻止")
            return

        elif choice_NAME.lower() == "launcher.exe":
            core.window.messagebox.showwarning(title="意料之中的映像名", message="你似乎选择了 launcher.exe 文件\n通常情况下它是启动器程序而不是游戏启动程序")

        elif module.xxmi.detect_importer(choice_PATH) is None:
            names = "\n".join(f"- {x}" for x in ["GenshinImpact.exe", "YuanShen.exe", "StarRail.exe", "ZenlessZoneZero.exe", "Wuthering Waves.exe", "BH3.exe", "Endfield.exe"])
            core.window.messagebox.showwarning(title="意料之中的映像名", message=f"你选择的文件映像名不在白名单之中\n请确保它是游戏的启动程序\n\n{names}")

        core.userenv.configuration.GamePath = choice_PATH
        self.sbin_update_game_path(choice_PATH)

        importer = module.xxmi.detect_importer(choice_PATH)
        if importer is not None and importer != core.userenv.configuration.XXMIImporter:
            core.userenv.configuration.XXMIImporter = importer
            self.combobox_importer.set(module.xxmi.importer_display(importer))

        self.sbin_sync_xxmi(silent=True)
        self.sbin_update_xxmi_status()


    def bin_launch_game(self, *args, **kwds):
        path = core.userenv.configuration.GamePath
        if path is None:
            core.window.messagebox.showerror(title="数据未设置", message="无法启动游戏\n未设置游戏路径")
            return

        if not self.sbin_sync_xxmi(): return

        if not module.xxmi.is_installed():
            core.window.messagebox.showwarning(title="XXMI Launcher", message="工作目录中尚未安装 3DMigoto\n请先点击「启动 XXMI Launcher」并在其中完成安装")
            return

        try:
            module.xxmi.launch(self.sbin_get_importer(), nogui=True)
        except module.xxmi.XXMIError as e:
            core.window.messagebox.showerror(title="XXMI Launcher", message=str(e))
        except pywintypes.error as e:
            core.window.messagebox.showerror(title="异常捕获", message=f"{e.args[1]}: {e.args[0]}\n{e.args[2]}")
        except Exception:
            core.window.messagebox.showerror(title="程序故障", message="无法找到正确的方式启动该程序")
