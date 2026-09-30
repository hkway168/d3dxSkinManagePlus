# -*- coding: utf-8 -*-

# 插件加载模块 (移植自 d3dxSkinManage 1.5.19+)
# 插件目录结构: ./plugins/<plugin_name>/main.py
# 插件需提供 main() 函数, 可选 __version__ 与 description.txt

# std
import os
import re
import sys
import traceback
import importlib.util

# local
import core
from constant import L


NAME_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_\-]*$")
DISABLE_ARGUMENT = "--noplugin"


class PluginsData:
    alias_table = {}
    failed_table = {}


def is_disabled() -> bool:
    return DISABLE_ARGUMENT in sys.argv[1:]


def load_plugin(name: str, filepath: str) -> None:
    module_name = f"d3dxsm_plugin_{name.replace('-', '_')}"
    module_spec = importlib.util.spec_from_file_location(module_name, filepath)
    dynamic_module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(dynamic_module)
    dynamic_module.main()
    PluginsData.alias_table[name] = dynamic_module


def load_plugins() -> None:
    root = core.env.base.plugins
    if not os.path.isdir(root):
        return

    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if not os.path.isdir(path):
            continue

        filepath = os.path.join(path, "main.py")
        if not os.path.isfile(filepath):
            continue

        if NAME_PATTERN.match(name) is None:
            core.log.warning(f"{path} 插件目录名称不合法, 已跳过", L.MODULE_PLUGINS)
            PluginsData.failed_table[name] = "插件目录名称不合法 (仅允许英文字母、数字、下划线和短横线)"
            continue

        try:
            load_plugin(name, filepath)
            core.log.info(f"{filepath} 已加载", L.MODULE_PLUGINS)

        except BaseException as e:
            exc = traceback.format_exc()
            core.log.error(f"{filepath} 加载失败 {e.__class__} {e}\n{exc}", L.MODULE_PLUGINS)
            PluginsData.failed_table[name] = f"{e.__class__.__name__}: {e}"


def refresh_window() -> None:
    try:
        core.window.mainwindow.after(0, core.window.interface.plugins.update)

    except Exception as e:
        core.log.error(f"刷新插件页面失败 {e.__class__} {e}", L.MODULE_PLUGINS)


def main() -> None:
    try:
        if is_disabled():
            core.log.warning("已禁用插件加载", L.MODULE_PLUGINS)
            return

        load_plugins()

    except Exception as e:
        core.log.error(f"load_plugins 函数错误 {e.__class__} {e}", L.MODULE_PLUGINS)

    finally:
        refresh_window()


__all__ = [
    "PluginsData",
    "load_plugins",
    "main"
]
