# -*- coding: utf-8 -*-

import os
import threading
import subprocess

from . import env


def is_main_thread(*args, **kwds) -> bool:
    return threading.current_thread() is threading.main_thread()


def x7z(from_file: str, to_path: str):
    PIPE = subprocess.PIPE
    DEVNULL = subprocess.DEVNULL
    command = (env.file.local.t7z, 'x', '-y', f'-o{to_path}', from_file)
    task = subprocess.Popen(command, shell=True, stdin=PIPE, stdout=DEVNULL, stderr=DEVNULL, cwd=env.base.cwd)
    task.wait()


def a7z(from_file: str, to_path: str):
    PIPE = subprocess.PIPE
    DEVNULL = subprocess.DEVNULL
    command = (env.file.local.t7z, 'a', '-t7z', to_path, from_file)
    task = subprocess.Popen(command, shell=True, stdin=PIPE, stdout=DEVNULL, stderr=DEVNULL, cwd=env.base.cwd)
    task.wait()


def pack_dir_7z(source_dir: str, to_file: str) -> bool:
    """将目录内的全部内容 (不含目录本身) 打包为 7z, 返回是否成功"""
    DEVNULL = subprocess.DEVNULL
    t7z = os.path.abspath(env.file.local.t7z)
    command = (t7z, 'a', '-t7z', '-y', os.path.abspath(to_file), '*')
    try:
        task = subprocess.run(command, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL, cwd=source_dir,
                              creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except Exception:
        return False
    return task.returncode == 0


def _view(path: str, rule_key: str, default_rule: str):
    import win32api

    configuration = env.configuration
    program = configuration.view_explorer_path if isinstance(configuration.view_explorer_path, str) else "explorer"
    rule = getattr(configuration, rule_key)
    if not isinstance(rule, str): rule = default_rule

    # 路径可能含空格, 规则中未自带引号时自动加上
    path = os.path.normpath(path)
    argument = rule.replace("{path}", path) if '"{path}"' in rule else rule.replace("{path}", f'"{path}"')
    win32api.ShellExecute(0, "open", program, argument, None, 1)


def view_file(path: str):
    """在文件管理器中定位文件 (程序和参数规则可在全局配置文件中修改)"""
    _view(path, "view_file_rule", "/select,{path}")


def view_directory(path: str):
    """在文件管理器中打开目录 (程序和参数规则可在全局配置文件中修改)"""
    _view(path, "view_directory_rule", "{path}")
