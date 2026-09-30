# -*- coding: utf-8 -*-

import ttkbootstrap

from .about import About
from .mods_manage import ModsManage
from .d3dx_manage import D3dxManage
from .tools import Tools
from .settings import Settings
from .plugins import Plugins


class Interface(object):
    def __init__(self, master):
        self.master = master

        self.notebook = ttkbootstrap.Notebook(self.master)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=(5, 0))

        self.frame_mods_manage = ttkbootstrap.Frame(self.notebook)
        self.notebook.add(self.frame_mods_manage, text='Mods 管理')

        self.frame_d3dx_manage = ttkbootstrap.Frame(self.notebook)
        self.notebook.add(self.frame_d3dx_manage, text='环境设置')

        self.frame_about = ttkbootstrap.Frame(self.notebook)
        self.notebook.add(self.frame_about, text='关于')

        self.frame_tools = ttkbootstrap.Frame(self.notebook)
        self.notebook.add(self.frame_tools, text='工具')

        self.frame_settings = ttkbootstrap.Frame(self.notebook)
        self.notebook.add(self.frame_settings, text='设置')

        self.frame_plugins = ttkbootstrap.Frame(self.notebook)
        self.notebook.add(self.frame_plugins, text='插件')

        self.mods_manage = ModsManage(self.frame_mods_manage)
        self.d3dx_manage = D3dxManage(self.frame_d3dx_manage)
        self.about = About(self.frame_about)
        self.tools = Tools(self.frame_tools)
        self.settings = Settings(self.frame_settings)
        self.plugins = Plugins(self.frame_plugins)


    def initial(self):
        self.mods_manage.initial()
        self.d3dx_manage.initial()
        self.settings.initial()