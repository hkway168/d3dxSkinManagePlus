# -*- coding: utf-8 -*-

class CODE ():
    U8 = "utf-8"
    GB18030 = "gb18030"

    GB = GB18030


class RE ():
    PATH_SPLIT = "/|\\\\"


class INDEX ():
    INFORMATION = "information"
    MODS = "mods"

    OBJECT = "object"
    TYPE = "type"
    NAME = "name"
    EXPLAIN = "explain"
    GRADING = "grading"
    AUTHOR = "author"
    TAGS = "tags"


class MOD_TYPE ():
    """Mod 原始文件类型

    与索引项中的 type 字段对应, 统一使用小写且不含前导点
    """
    ZIP = "zip"
    RAR = "rar"
    T7Z = "7z"
    INI = "ini"

    # 需要经由 7zip 解压的归档类型
    ARCHIVE = [ZIP, RAR, T7Z]
    # 无需解压, 以单个文件形式存储并直接部署的类型
    PLAIN = [INI]

    ARCHIVE_SUFFIXES = [f".{x}" for x in ARCHIVE]
    PLAIN_SUFFIXES = [f".{x}" for x in PLAIN]


class ACTION_VALUE ():
    RAISE = "raise"
    COVER = "cover"
    SKIP = "skip"


DISABLED = "disabled"
DISABLED_UPPER = "DISABLED"
SUFFIX_JSON = ".json"


__all__ = [
    "RE",
    "INDEX",
    "MOD_TYPE",
    "DISABLED",
    "SUFFIX_JSON"
]
