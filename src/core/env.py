# -*- coding: utf-8 -*-

# std
import os
from os.path import join as __

# self
import libs.econfiguration
from .exceptions import *
from .structure import *


PROJECT = "d3dxSkinManage"

CODE_NAME = "kamisa"


class __base (Directory):
    cwd = os.getcwd()
    home = "home"
    resources = "resources"
    local = "local"
    plugins = "plugins"

base = __base()



class directory (Directory):
    class __resources (Directory):
        mods = __(base.resources, "mods")
        preview = __(base.resources, "preview")
        thumbnail = __(base.resources, "thumbnail")
        cache = __(base.resources, "cache")
        backup = __(base.resources, "backup")


    class __local (Directory):
        t7zip = __(base.local, "7zip")

    resources = __resources()
    local = __local()



class file (static):
    class resources (static):
        redirection = __(directory.resources.thumbnail, "_redirection.ini")


    class local (static):
        t7z = __(base.local, "7zip", "7z.exe")
        iconbitmap = __(base.local, "iconbitmap.ico")
        configuration = __(base.local, "configuration")


class configuration(libs.econfiguration.Configuration):
    log_level: int | str # 日志等级
    annotation_level: int # 描述提示词等级
    style_theme: str # 主题风格
    xxmi_launcher_root: str # XXMI Launcher 根目录 (配置文件所在目录)


try:
    configuration = libs.econfiguration.Configuration(file.local.configuration)

except Exception:
    configuration = libs.econfiguration.Configuration()


__all__ = [
    "PROJECT",
    "CODE_NAME",
    "base",
    "directory",
    "file",
    "configuration"
]
