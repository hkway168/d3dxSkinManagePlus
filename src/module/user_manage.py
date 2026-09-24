# -*- coding: utf-8 -*-

import os
import shutil

import libs.econfiguration

import core
from constant import L


# Windows 文件名非法字符
INVALID_CHARS = '\\/:*?"<>|'

# Windows 保留设备名
RESERVED_NAMES = [
    "CON", "PRN", "AUX", "NUL",
    *[f"COM{x}" for x in range(1, 10)],
    *[f"LPT{x}" for x in range(1, 10)]
]

NAME_MAX_LENGTH = 32

# 用户目录下需要初始化的子目录
SUB_DIRECTORYS = [
    "modsIndex",
    "classification",
    "work",
    os.path.join("work", "Mods")
]


def get_user_list() -> list:
    """获取现有用户名列表"""
    home = core.env.base.home
    try:
        return [x for x in os.listdir(home) if os.path.isdir(os.path.join(home, x))]

    except Exception:
        return []


def verify_user_name(user_name: str) -> str:
    """校验用户名, 合法返回空字符串, 否则返回错误描述"""
    if not isinstance(user_name, str) or not user_name.strip():
        return "用户名不能为空"

    if user_name != user_name.strip():
        return "用户名首尾不能包含空格"

    if len(user_name) > NAME_MAX_LENGTH:
        return f"用户名长度不能超过 {NAME_MAX_LENGTH} 个字符"

    for char in INVALID_CHARS:
        if char in user_name:
            return f"用户名不能包含以下字符\n{INVALID_CHARS}"

    if user_name.endswith("."):
        return "用户名不能以 . 结尾"

    if user_name.upper() in RESERVED_NAMES:
        return f"\"{user_name}\" 是系统保留名称"

    if user_name in get_user_list():
        return f"用户 \"{user_name}\" 已存在"

    return ""


def __set_picture(user_path: str, picture_path: str) -> None:
    """设置用户头像, 非 png/jpg 格式将转换为 png"""
    suffix = os.path.splitext(picture_path)[1].lower()

    if suffix == ".png":
        shutil.copyfile(picture_path, os.path.join(user_path, "picture.png"))

    elif suffix in [".jpg", ".jpeg"]:
        shutil.copyfile(picture_path, os.path.join(user_path, "picture.jpg"))

    else:
        import PIL.Image
        with PIL.Image.open(picture_path) as image:
            image.convert("RGBA").save(os.path.join(user_path, "picture.png"))


def __copy_classification(user_path: str, source_name: str) -> None:
    """从其它用户复制分类配置"""
    source = os.path.join(core.env.base.home, source_name, "classification")
    if not os.path.isdir(source):
        return

    target = os.path.join(user_path, "classification")
    for name in os.listdir(source):
        filepath = os.path.join(source, name)
        if not os.path.isfile(filepath):
            continue

        shutil.copyfile(filepath, os.path.join(target, name))


def create_user(user_name: str, description: str = "", game_path: str = "",
                picture_path: str = "", classification_from: str = "") -> str:
    """创建用户环境

    user_name: 用户名 (同时作为用户目录名)
    description: 用户描述, 写入 description.txt
    game_path: 游戏启动程序路径, 写入用户配置的 GamePath
    picture_path: 用户头像图片路径
    classification_from: 从该用户复制分类配置

    返回创建的用户目录路径, 参数非法或创建失败时抛出异常
    """
    error = verify_user_name(user_name)
    if error:
        core.log.error(f"创建用户失败: {error}", L.MODULE_USER_MANAGE)
        raise ValueError(error)

    if picture_path and not os.path.isfile(picture_path):
        raise ValueError("头像图片文件不存在")

    if game_path and not os.path.isfile(game_path):
        raise ValueError("游戏启动程序文件不存在")

    core.log.info(f"创建用户 \"{user_name}\"", L.MODULE_USER_MANAGE)
    user_path = os.path.join(core.env.base.home, user_name)

    try:
        os.makedirs(user_path)

        for name in SUB_DIRECTORYS:
            os.makedirs(os.path.join(user_path, name), exist_ok=True)

        configuration = libs.econfiguration.Configuration()
        if game_path:
            configuration.GamePath = game_path.replace("/", "\\")
        configuration._con_asve_as_json(os.path.join(user_path, "configuration"))

        if description.strip():
            with open(os.path.join(user_path, "description.txt"), "w", encoding="utf-8") as fileobject:
                fileobject.write(description)

        if picture_path:
            __set_picture(user_path, picture_path)

        if classification_from:
            __copy_classification(user_path, classification_from)

    except Exception as e:
        core.log.error(f"创建用户 \"{user_name}\" 失败: {e}", L.MODULE_USER_MANAGE)
        shutil.rmtree(user_path, ignore_errors=True)
        raise

    core.log.info(f"用户 \"{user_name}\" 创建完成", L.MODULE_USER_MANAGE)
    return user_path
