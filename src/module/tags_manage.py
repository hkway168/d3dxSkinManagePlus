# -*- coding: utf-8 -*-
"""可选标签管理 (移植自原版 module._tags_manage)

可选标签 = 用户自定义的标签 (home/<用户>/modtags, 空格分隔, 换行分行)
         + 所有 Mod 中已出现过但未被用户列出的标签 (每 5 个一行追加在末尾)
"""

# std
import os
import copy
import threading

# local
import core
from constant import *


EXTRA_ROW_WIDTH = 5
FILE_NAME = "modtags"


class TagsManage (object):
    def __init__(self):
        self._lock = threading.RLock()
        self._userf_path: str = ""
        self._users_tags: list[list[str]] = []
        self._index_tags: list[str] = []
        self._final_tags: list[list[str]] = []
        self._content: str = ""


    # ---------------------------------------------- 内部
    def _update_final_tags(self):
        with self._lock:
            users = {tag for row in self._users_tags for tag in row}
            extra = [tag for tag in self._index_tags if tag not in users]

            self._final_tags = copy.deepcopy(self._users_tags)
            self._final_tags += [extra[i:i + EXTRA_ROW_WIDTH] for i in range(0, len(extra), EXTRA_ROW_WIDTH)]
            self._content = "".join(" ".join(row) + "\n" for row in self._final_tags)


    def _update_index_tags(self):
        lst = []
        try:
            for SHA in core.module.mods_index.get_all_sha_list():
                item = core.module.mods_index.get_item(SHA) or {}
                for tag in item.get(K.INDEX.TAGS, None) or []:
                    if tag and tag not in lst: lst.append(tag)

        except Exception as e:
            core.log.error(f"读取 Mod 标签失败 {e.__class__} {e}", L.MODULE)

        with self._lock:
            self._index_tags = lst
            self._update_final_tags()


    def _update_users_tags(self):
        with self._lock:
            content = ""
            if self._userf_path and os.path.isfile(self._userf_path):
                try:
                    with open(self._userf_path, "r", encoding="utf-8") as f: content = f.read()

                except Exception as e:
                    core.log.error(f"读取可选标签文件失败 {e.__class__} {e}", L.MODULE)

            # 文件不存在时也要重置, 避免切换用户后残留上一个用户的标签
            self.update_content(content)


    # ---------------------------------------------- 事件
    def _event_user_logged_in(self, *_):
        with self._lock:
            self._userf_path = os.path.join(core.env.base.home, core.userenv.user_name, FILE_NAME)
        self._update_users_tags()
        self._update_index_tags()


    def _event_user_logged_out(self, *_):
        with self._lock:
            self._userf_path = ""
            self._users_tags = []
            self._index_tags = []
            self._update_final_tags()


    def _event_manage_cache_refreshed(self, *_):
        self._update_index_tags()


    def initial(self):
        core.construct.event.register(E.USER_LOGGED_IN, self._event_user_logged_in)
        core.construct.event.register(E.USER_LOGGED_OUT, self._event_user_logged_out)
        core.construct.event.register(E.MODS_MANAGE_CACHE_REFRESHED, self._event_manage_cache_refreshed)


    # ---------------------------------------------- 接口 (与原版同名)
    def format_optional(self, content: str | list) -> list[list[str]]:
        if not isinstance(content, (str, list)):
            raise TypeError("optional must be a string, list of strings, or list of lists of strings.")

        rows = content.split("\n") if isinstance(content, str) else content
        result = []
        for row in rows:
            text = row if isinstance(row, str) else " ".join(row)
            items = [x for x in text.replace("\t", " ").split(" ") if x]
            if items: result.append(items)

        return result


    def update_content(self, content: str, update_file: bool = False):
        """更新用户自定义标签; update_file 为 True 时写入文件"""
        with self._lock:
            self._users_tags = self.format_optional(content)
            self._update_final_tags()

            if not update_file: return
            if not self._userf_path: raise RuntimeError("用户未登录")

            with open(self._userf_path, "w", encoding="utf-8") as f:
                f.write("".join(" ".join(row) + "\n" for row in self._users_tags))


    def get_tags(self) -> list[list[str]]:
        with self._lock:
            return copy.deepcopy(self._final_tags)


    def get_tags_content(self) -> str:
        with self._lock:
            return self._content


    def is_ready(self) -> bool:
        with self._lock:
            return bool(self._userf_path)


__all__ = ["TagsManage"]
