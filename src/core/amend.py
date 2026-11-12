# -*- coding: utf-8 -*-

import core

import ttkbootstrap

from constant import K

def env_config_amend():
    if not isinstance(core.env.configuration.log_level, (int, str)):
        core.env.configuration.log_level = 0

    if not isinstance(core.env.configuration.annotation_level, int):
        core.env.configuration.annotation_level = 3

    if not isinstance(core.env.configuration.style_theme, str) or core.env.configuration.style_theme not in ttkbootstrap.Style().theme_names():
        core.env.configuration.style_theme = "darkly"

    # 对象列表是否显示没有本地 Mod 的对象, 默认不显示
    if not isinstance(core.env.configuration.show_empty_objects, bool):
        core.env.configuration.show_empty_objects = False

    # 打开文件 / 目录的方式 (移植自原版, 可在配置文件中改为其他文件管理器)
    if not isinstance(core.env.configuration.view_explorer_path, str):
        core.env.configuration.view_explorer_path = "explorer"

    if not isinstance(core.env.configuration.view_file_rule, str):
        core.env.configuration.view_file_rule = "/select,{path}"

    if not isinstance(core.env.configuration.view_directory_rule, str):
        core.env.configuration.view_directory_rule = "{path}"

    # 头像名称匹配算法, 默认使用与旧版本一致的 "名称包含" 匹配
    if core.env.configuration.thumbnail_approximate_algorithm not in K.APPROXIMATE.ALL:
        core.env.configuration.thumbnail_approximate_algorithm = K.APPROXIMATE.KEY_IN_ONLY

    # 运行 fixtool 中 .py 修复脚本的 Python 解释器路径, 留空则自动查找 (py 启动器 / PATH 中的 python)
    if not isinstance(core.env.configuration.fixtool_python, str):
        core.env.configuration.fixtool_python = ""
