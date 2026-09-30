# -*- coding: utf-8 -*-

from . import image
from . import construct
from . import synchronization
from . import extension
from . import user_manage
from . import plugins

from .index_manage import IndexManage
from .mods_index import ModsIndex
from .mods_manage import ModsManage
from .tags_manage import TagsManage

index_manage = IndexManage()
mods_index = ModsIndex()
mods_manage = ModsManage()
tags_manage = TagsManage()

__all__ = [
    "image",
    "construct",
    "synchronization",
    "extension",
    "user_manage",
    "plugins",
    "index_manage",
    "mods_index",
    "mods_manage",
    "tags_manage"
]
