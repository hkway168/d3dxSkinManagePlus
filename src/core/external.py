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
