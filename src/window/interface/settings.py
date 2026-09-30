# -*- coding: utf-8 -*-

import ttkbootstrap

import core
from constant import *


class Settings (object):
    def __init__(self, master, *_):
        self.master = master
        self.install()


    def install(self):
        self.value_show_empty_objects = ttkbootstrap.BooleanVar(value=bool(core.env.configuration.show_empty_objects))

        self.labelframe_display = ttkbootstrap.LabelFrame(self.master, text="显示设置")
        self.labelframe_display.pack(side="top", fill="x", padx=10, pady=10)

        self.checkbutton_show_empty_objects = ttkbootstrap.Checkbutton(
            self.labelframe_display,
            text="在对象列表中显示没有 Mod 的对象",
            variable=self.value_show_empty_objects,
            bootstyle="round-toggle",
            command=self.bin_set_show_empty_objects
        )
        self.checkbutton_show_empty_objects.pack(side="top", anchor="w", padx=10, pady=10)


    def initial(self):
        # 配置修正在界面创建之后执行, 这里重新同步一次
        self.value_show_empty_objects.set(bool(core.env.configuration.show_empty_objects))

        _alt_set = core.window.annotation_toplevel.register
        _alt_set(self.checkbutton_show_empty_objects, T.ANNOTATION_SHOW_EMPTY_OBJECTS, 2)


    def bin_set_show_empty_objects(self, *_):
        core.env.configuration.show_empty_objects = bool(self.value_show_empty_objects.get())
        core.construct.event.set_event(E.MODS_MANAGE_CACHE_REFRESHED)
