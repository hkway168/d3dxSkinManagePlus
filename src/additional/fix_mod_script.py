# -*- coding: utf-8 -*-
"""使用脚本修复 Mod

从 fixtool 目录选取修复脚本 (*.py) 或由脚本打包的可执行文件 (*.exe),
在新的控制台窗口中以目标目录为工作目录运行:
    - 修复单个 Mod: Mod 的解压缓存目录 (work\\Mods\\SHA 或 disabled-SHA)
    - 修复所有 Mod: Mod 根目录 (work\\Mods)

修复脚本通常以当前工作目录为处理对象, 且可能需要交互输入 (例如按回车确认),
因此不捕获输出, 直接打开独立控制台供用户查看与操作。

.py 脚本的解释器查找顺序:
    1. 配置项 fixtool_python (local\\configuration, 可填写 python.exe 的完整路径)
    2. 源码运行时使用当前解释器
    3. PATH 中的 py 启动器 (py -3) / python
"""

# std
import os
import sys
import shutil
import threading
import subprocess
import tkinter.filedialog

# project
import core
from constant import *


FIXTOOL_DIRNAME = 'fixtool'
SCRIPT_SUFFIXES = ('.py', '.exe')

# 控制台窗口被关闭 / Ctrl+C 中断时的退出码
# 点击右上角关闭时系统发送 CTRL_CLOSE_EVENT, 默认处理以 STATUS_CONTROL_C_EXIT 结束进程
CLOSED_EXIT_CODES = {
    0xC000013A,  # STATUS_CONTROL_C_EXIT
}

# 正在运行修复脚本的目标 (Mod SHA 或 ALL_KEY), 防止对同一目录重复执行
ALL_KEY = '*'
_running: set[str] = set()
_running_lock = threading.Lock()


def get_fixtool_directory() -> str:
    path = os.path.abspath(os.path.join(core.env.base.cwd, FIXTOOL_DIRNAME))
    try: os.makedirs(path, exist_ok=True)
    except Exception: ...
    return path


def _get_cache_path(SHA: str) -> str | None:
    for name in (SHA, f'{K.DISABLED}-{SHA}'):
        path = os.path.abspath(os.path.join(core.userenv.directory.work_mods, name))
        if os.path.isdir(path): return path
    return None


def _get_mods_root() -> str | None:
    try: path = os.path.abspath(core.userenv.directory.work_mods)
    except Exception: return None
    return path if os.path.isdir(path) else None


def find_python() -> list[str] | None:
    """返回运行 .py 脚本的命令前缀, 找不到返回 None"""
    configured = core.env.configuration.fixtool_python
    if isinstance(configured, str) and configured.strip():
        configured = os.path.abspath(os.path.expandvars(configured.strip().strip('"')))
        if os.path.isfile(configured): return [configured]
        core.log.warn(f"配置的修复脚本解释器不存在 {configured}")

    if not getattr(sys, 'frozen', False) and sys.executable:
        executable = sys.executable
        # pythonw 没有控制台, 换为同目录的 python.exe 以便显示输出 / 接收输入
        if os.path.basename(executable).lower() == 'pythonw.exe':
            console = os.path.join(os.path.dirname(executable), 'python.exe')
            if os.path.isfile(console): executable = console
        return [executable]

    launcher = shutil.which('py')
    if launcher: return [launcher, '-3']

    python = shutil.which('python')
    if python: return [python]

    return None


def build_command(script: str) -> list[str] | None:
    suffix = os.path.splitext(script)[1].lower()
    if suffix == '.exe':
        return [script]

    if suffix == '.py':
        python = find_python()
        if python is None: return None
        return [*python, script]

    return None


def select_script() -> str | None:
    filepath = tkinter.filedialog.askopenfilename(
        title='选择修复脚本',
        initialdir=get_fixtool_directory(),
        filetypes=[('修复脚本', ' '.join(f'*{x}' for x in SCRIPT_SUFFIXES)),
                   ('Python 脚本', '*.py'), ('可执行文件', '*.exe')],
        parent=core.window.mainwindow)

    return os.path.abspath(filepath) if filepath else None


def _busy_unlocked(key: str) -> bool:
    """修复全部与修复单个 Mod 的目录存在包含关系, 两者互斥 (调用方需持有 _running_lock)"""
    if key == ALL_KEY: return bool(_running)
    return key in _running or ALL_KEY in _running


def _is_busy(key: str) -> bool:
    with _running_lock: return _busy_unlocked(key)


def _busy_error():
    core.window.messagebox.showerror(title='操作进行中', message='修复脚本仍在运行\n请先关闭上一次的修复窗口')


# ================================================================== 菜单入口
def fix_with_script(SHA: str):
    """Mod 右键菜单: 选择脚本并在该 Mod 的缓存目录中执行"""
    cache_path = _get_cache_path(SHA)
    if cache_path is None:
        core.window.messagebox.showerror(title='缓存不存在', message='该 Mod 没有解压缓存\n请先加载一次该 Mod 以生成缓存')
        return

    message = (
        '确定使用以下脚本修复该 Mod?\n\n'
        '脚本: {script}\n'
        f'目录: {cache_path}\n\n'
        '脚本将直接修改缓存目录中的文件, 原始文件不受影响\n'
        '如修复结果不理想, 可删除缓存文件后重新加载以还原\n'
        '修复满意后可通过 "应用到原始文件" 保存修改'
    )

    def reload_hint() -> str:
        if core.module.mods_manage.is_loaded_sha(SHA):
            return ', 该 Mod 正在使用, 请在游戏中按 F10 重新加载'
        return ''

    _run(SHA, cache_path, '使用脚本修复Mod', message, reload_hint)


def fix_all_with_script():
    """分类 / 对象右键菜单: 选择脚本并在 Mod 根目录 (work\\Mods) 中执行"""
    mods_root = _get_mods_root()
    if mods_root is None:
        core.window.messagebox.showerror(title='目录不存在', message='Mod 根目录不存在\n请先登录用户并加载 Mod')
        return

    message = (
        '确定使用以下脚本修复所有 Mod?\n\n'
        '脚本: {script}\n'
        f'目录: {mods_root}\n\n'
        '脚本将直接修改该目录下所有 Mod 缓存 (包括未加载的) 中的文件, 原始文件不受影响\n'
        '如修复结果不理想, 可删除对应 Mod 的缓存文件后重新加载以还原'
    )

    def reload_hint() -> str:
        if core.module.mods_manage.get_loaded_objects(None):
            return ', 请在游戏中按 F10 重新加载'
        return ''

    _run(ALL_KEY, mods_root, '使用脚本修复所有Mod', message, reload_hint)


# ================================================================== 执行
def _run(key: str, cwd: str, title: str, message: str, reload_hint):
    if _is_busy(key):
        _busy_error()
        return

    script = select_script()
    if not script: return

    if not os.path.isfile(script) or os.path.splitext(script)[1].lower() not in SCRIPT_SUFFIXES:
        core.window.messagebox.showerror(title='无效的脚本', message=f'仅支持 .py 脚本或 .exe 可执行文件\n{script}')
        return

    command = build_command(script)
    if command is None:
        core.window.messagebox.showerror(
            title='未找到 Python',
            message='运行 .py 脚本需要 Python 解释器, 但未能找到\n\n'
                    '请安装 Python 并加入 PATH,\n'
                    '或在 local\\configuration 中设置 fixtool_python 为 python.exe 的完整路径,\n'
                    '或改用脚本打包后的 .exe')
        return

    message = message.replace('{script}', os.path.basename(script))
    if not core.window.messagebox.askyesno(title=title, message=message, icon='warning'): return

    with _running_lock:
        busy = _busy_unlocked(key)
        if not busy: _running.add(key)
    if busy:
        _busy_error()
        return

    try:
        process = subprocess.Popen(
            command, cwd=cwd,
            creationflags=getattr(subprocess, 'CREATE_NEW_CONSOLE', 0))

    except Exception as e:
        with _running_lock: _running.discard(key)
        core.log.error(f"启动修复脚本失败 {command} {e.__class__} {e}")
        core.window.messagebox.showerror(title='启动失败', message=f'启动修复脚本失败\n{e}')
        return

    core.log.info(f"运行修复脚本 {key} {command} cwd={cwd}")
    _set_status(f'正在运行修复脚本 {os.path.basename(script)} ...')

    threading.Thread(target=_wait_process, args=(key, script, process, reload_hint), daemon=True).start()


def _wait_process(key: str, script: str, process: subprocess.Popen, reload_hint):
    name = os.path.basename(script)
    try:
        code = process.wait()

    except Exception as e:
        core.log.error(f"等待修复脚本失败 {key} {e.__class__} {e}")
        _set_status(f'修复脚本 {name} 状态未知: {e}', 2)
        return

    finally:
        with _running_lock: _running.discard(key)

    core.log.info(f"修复脚本结束 {key} {name} returncode={code}")

    try: hint = reload_hint()
    except Exception: hint = ''

    if code == 0:
        _set_status(f'修复脚本 {name} 已完成{hint}')

    elif (code & 0xFFFFFFFF) in CLOSED_EXIT_CODES:
        # 点击控制台右上角关闭 / Ctrl+C 结束, 无法得知脚本是否已处理完毕, 不视为错误
        _set_status(f'修复窗口已关闭 ({name}), 请自行确认修复结果{hint}')

    else:
        _set_status(f'修复脚本 {name} 异常退出 (返回码 {code}), 请检查脚本窗口输出', 1)


def _set_status(message: str, level: int = 0):
    try: core.window.mainwindow.after(0, core.window.status.set_status, message, level)
    except Exception: ...
