# -*- coding: utf-8 -*-

# XXMI Launcher 对接模块
# 3DMigoto 本体 (GIMI / SRMI / ZZMI ...) 不再由本程序内置, 统一交由外部的 XXMI Launcher 下载与更新.
# 本模块负责: 定位 XXMI Launcher、将导入器目录指向当前用户的 work 目录、通过 XXMI Launcher 启动游戏.

import os
import json
import shutil
import subprocess

import win32api

import core


LAUNCHER_EXE_NAME = "XXMI Launcher.exe"
CONFIG_FILE_NAME = "XXMI Launcher Config.json"

# 导入器 -> 显示名称
IMPORTERS = {
    "GIMI": "原神",
    "SRMI": "崩坏：星穹铁道",
    "ZZMI": "绝区零",
    "WWMI": "鸣潮",
    "HIMI": "崩坏3",
    "EFMI": "明日方舟：终末地",
}

# 游戏主程序 -> 导入器 (XXMI 配置不可读时的兜底)
GAME_EXE_IMPORTER = {
    "genshinimpact.exe": "GIMI",
    "yuanshen.exe": "GIMI",
    "starrail.exe": "SRMI",
    "zenlesszonezero.exe": "ZZMI",
    "zenlesszonezerobeta.exe": "ZZMI",
    "wuthering waves.exe": "WWMI",
    "client-win64-shipping.exe": "WWMI",
    "bh3.exe": "HIMI",
    "endfield.exe": "EFMI",
}


class XXMIError (Exception): ...


def importer_display(importer: str) -> str:
    return f"{importer} - {IMPORTERS.get(importer, importer)}"


def importer_from_display(text: str) -> str | None:
    key = (text or "").split("-", 1)[0].strip().upper()
    return key if key in IMPORTERS else None


def resolve_root(path: str) -> str | None:
    """根据用户选择的目录或文件, 解析出 XXMI Launcher 的根目录 (配置文件所在目录)"""
    if not path: return None
    path = os.path.abspath(path)
    if os.path.isfile(path): path = os.path.dirname(path)

    # 允许选择根目录、Resources 或 Resources\Bin
    for candidate in [path, os.path.dirname(path), os.path.dirname(os.path.dirname(path))]:
        if os.path.isfile(os.path.join(candidate, "Resources", "Bin", LAUNCHER_EXE_NAME)):
            return candidate
        if os.path.isfile(os.path.join(candidate, CONFIG_FILE_NAME)):
            return candidate

    return None


def get_root() -> str | None:
    root = core.env.configuration.xxmi_launcher_root
    if isinstance(root, str) and root and os.path.isdir(root):
        return root
    return None


def set_root(root: str | None) -> None:
    core.env.configuration.xxmi_launcher_root = root


def get_exe(root: str | None = None) -> str | None:
    root = root or get_root()
    if root is None: return None
    for path in [os.path.join(root, "Resources", "Bin", LAUNCHER_EXE_NAME), os.path.join(root, LAUNCHER_EXE_NAME)]:
        if os.path.isfile(path): return path
    return None


def get_config_path(root: str | None = None) -> str | None:
    root = root or get_root()
    if root is None: return None
    return os.path.join(root, CONFIG_FILE_NAME)


def is_running() -> bool:
    """XXMI Launcher 退出时会回写配置, 运行期间修改配置会被覆盖"""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {LAUNCHER_EXE_NAME}", "/NH"],
            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        return LAUNCHER_EXE_NAME.lower() in result.stdout.lower()
    except Exception:
        return False


def load_config(root: str | None = None) -> dict | None:
    path = get_config_path(root)
    if path is None or not os.path.isfile(path): return None
    with open(path, "r", encoding="utf-8") as fileobject:
        return json.load(fileobject)


def detect_importer(game_path: str | None, root: str | None = None) -> str | None:
    """根据游戏主程序名推断导入器"""
    if not game_path: return None
    exe_name = os.path.basename(game_path).lower()

    try:
        config = load_config(root) or {}
        for importer, value in config.get("Importers", {}).items():
            names = value.get("Importer", {}).get("game_exe_names", [])
            if exe_name in [x.lower() for x in names] and importer in IMPORTERS:
                return importer
    except Exception:
        ...

    return GAME_EXE_IMPORTER.get(exe_name)


def work_folder() -> str:
    return os.path.abspath(core.userenv.directory.work).replace("\\", "/").rstrip("/") + "/"


def get_importer_folder(importer: str, root: str | None = None) -> str | None:
    try:
        config = load_config(root) or {}
        folder = config["Importers"][importer]["Importer"]["importer_folder"]
    except Exception:
        return None
    root = root or get_root()
    if not os.path.isabs(folder) and root is not None:
        folder = os.path.join(root, folder)
    return os.path.abspath(folder)


def is_bound(importer: str, root: str | None = None) -> bool:
    """导入器目录是否已指向当前用户的 work 目录"""
    folder = get_importer_folder(importer, root)
    if folder is None: return False
    return os.path.normcase(folder) == os.path.normcase(os.path.abspath(core.userenv.directory.work))


def is_installed() -> bool:
    """work 目录中是否已存在 XXMI 部署的 3DMigoto 文件"""
    work = core.userenv.directory.work
    return os.path.isfile(os.path.join(work, "d3dx.ini")) and os.path.isfile(os.path.join(work, "d3d11.dll"))


def bind_work(importer: str, game_path: str | None = None, root: str | None = None) -> None:
    """
    修改 XXMI Launcher 配置:
        - 导入器目录 (importer_folder) 指向当前用户 work 目录, XXMI 会将 3DMigoto 下载到此处
        - 设为当前激活的导入器
        - 同步游戏目录 (game_folder)
    """
    root = root or get_root()
    if root is None:
        raise XXMIError("未设置 XXMI Launcher 目录")

    if importer not in IMPORTERS:
        raise XXMIError(f"未知的导入器: {importer}")

    path = get_config_path(root)
    if not os.path.isfile(path):
        raise XXMIError("未找到 XXMI Launcher 配置文件\n请先运行一次 XXMI Launcher 后再试")

    if is_running():
        raise XXMIError("XXMI Launcher 正在运行\n其退出时会覆盖配置, 请先关闭 XXMI Launcher 后再试")

    with open(path, "r", encoding="utf-8") as fileobject:
        config = json.load(fileobject)

    importers = config.setdefault("Importers", {})
    section = importers.setdefault(importer, {}).setdefault("Importer", {})
    section["importer_folder"] = work_folder()
    if game_path:
        section["game_folder"] = os.path.dirname(os.path.abspath(game_path))

    launcher = config.setdefault("Launcher", {})
    launcher["active_importer"] = importer
    enabled = launcher.setdefault("enabled_importers", [])
    if importer not in enabled: enabled.append(importer)

    try: shutil.copyfile(path, path + ".d3dxsm.bak")
    except Exception: ...

    temp = path + ".d3dxsm.tmp"
    with open(temp, "w", encoding="utf-8") as fileobject:
        json.dump(config, fileobject, indent=4, ensure_ascii=False)
    os.replace(temp, path)

    core.log.info(f"XXMI Launcher 导入器 {importer} 已指向 {work_folder()}")


def launch(importer: str | None = None, nogui: bool = False) -> None:
    """
    启动 XXMI Launcher
        nogui=True 且指定 importer 时, 由 XXMI Launcher 直接注入并启动游戏
    """
    exe = get_exe()
    if exe is None:
        raise XXMIError("未找到 XXMI Launcher.exe\n请检查 XXMI Launcher 目录设置")

    args = []
    if nogui: args.append("--nogui")
    if importer: args += ["--xxmi", importer]

    win32api.ShellExecute(None, "open", exe, " ".join(args) or None, os.path.dirname(exe), 1)
