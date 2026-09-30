# -*- coding: utf-8 -*-

# std
import re
import os
import copy
import json
import threading

import numpy

import core

from constant import *


class ModsIndex (object):
    def __init__(self):
        # 原始数据表
        self.__original_index = {}
        # dict :: filepath : data
        # index 文件路径为 key
        # 其完整的原始数据为 value

        # Mods 表
        self.__table_mods = {}
        # dict :: SHA : item
        # Mod 的 SHA 为 key
        # Mod 的 数据为 value

        # SHA 来源表
        self.__table_from = {}
        # dict :: filename : SHA[]
        # index 文件路径为 key
        # 所包含的 SHA list 为 value

        # 对象 SHA 缓存
        self.__cache_object = {}
        # dict :: object_name : SHA[]
        # 对象名称为 key
        # 所包含的 SHA list 为 value

        # 操作锁
        self.__call_lock = threading._RLock()


    def clear(self):
        "清除所有索引数据"
        core.log.debug("清除索引数据...", L.MODULE_MODS_INDEX)
        with self.__call_lock:
            self.__original_index = {}
            self.__table_mods = {}
            self.__table_from = {}
            self.__cache_object = {}


    def __fill_vacancy_from_item(self, _item: dict) -> dict[str: dict]:
        """为 mod item 填充空缺的参数"""
        # todo


    def __fill_vacancy_from_mods(self, _mods: dict) -> dict[str: dict]:
        """"""
        # todo


    def __analyze_json(self, file_path: str) -> dict[str: dict]:
        if not os.path.isfile(file_path): raise FileNotFoundError()

        with open(file_path, "r", encoding="utf-8") as file_object:
            file_content = file_object.read()

        data_content = json.loads(file_content)

        return data_content


    def __analyze_npy(self, file: str) -> dict[str: dict]:
        if not os.path.isfile(file): raise FileNotFoundError()

        numpy_object = numpy.load(file, allow_pickle=True)
        data_content = numpy_object.item()

        return data_content


    def load(self, file: str, mode: str, action: str = K.ACTION_VALUE.RAISE) -> None | list:
        """加载 index 文件

        这个函数的返回值应该是 None

        若为 list 则表示 SHA 产生了交集，
        则需要从新指定 action 参数选择对重复的数据进行覆盖或跳过

        若返回了 False 则表示 action 参数不合法
        """

        core.log.info(f"加载 {file} {action} 模式", L.MODULE_MODS_INDEX)
        if not os.path.isfile(file): raise FileNotFoundError()
        if mode not in ["json", "npy"]: raise ValueError()

        if mode == "json":
            data_content = self.__analyze_json(file)

        # elif mode == "npy":
        #     _mods = self.__load_npy(file)

        else:
            core.log.error(f"不支持的加载模式 \"{mode}\"", L.MODULE_MODS_INDEX)
            raise ValueError()

        with self.__call_lock:
            # 找出所有重复的 SHA
            old_SHA = [x for x in self.__table_mods]
            new_SHA = [x for x in data_content[K.INDEX.MODS]]
            intersection = set(old_SHA) & set(new_SHA)
            length = len(intersection)

            # 若存在重复的 SHA 则返回列表
            if action == K.ACTION_VALUE.RAISE:
                if length != 0:
                    return list(intersection)

                # 不存在重复时
                self.__table_mods.update(data_content[K.INDEX.MODS])
                self.__table_from[file] = new_SHA

            # 覆盖重复的 SHA
            elif action == K.ACTION_VALUE.COVER:
                self.__table_mods.update(data_content[K.INDEX.MODS])
                self.__table_from[file] = new_SHA

                # 从 SHA 来源表中剔除重复的值
                for filename in self.__table_from:
                    now_lst = self.__table_from[filename]
                    self.__table_from[filename] = list(set(now_lst) - intersection)

            # 跳过重复的 SHA
            elif action == K.ACTION_VALUE.SKIP:
                # 不保存重复 SHA 的数据
                for SHA, item in data_content[K.INDEX.MODS].items():
                    if SHA in intersection:
                        continue

                    self.__table_mods[SHA] = item

                self.__table_from[file] = list(set(new_SHA) - intersection)

            # 意外 action 参数
            else:
                return False

            self.__original_index[file] = data_content
            self.cache_update()

        return None
        core.construct.event.set_event(E.MODS_INDEX_UPDATE)


    def cache_update(self) -> None:
        with self.__call_lock:
            self.__cache_object = {}
            for SHA, data in self.__table_mods.items():
                name = data["object"]

                if name not in self.__cache_object:
                    self.__cache_object[name] = []

                if SHA not in self.__cache_object[name]:
                    self.__cache_object[name].append(SHA)

            return None


    def get_sha_from(self, SHA: str) -> str | None:
        """获取 SHA 来原表的文件路径

        若 SHA 不存在则返回 None
        """
        with self.__call_lock:
            for filepath, SHA_lst in self.__table_from.items():
                if SHA in SHA_lst:
                    return filepath

            else:
                return None


    def get_item(self, SHA: str) -> dict | None:
        """获取 SHA 的数据

        若 SHA 不存在则返回 None
        """
        with self.__call_lock:
            data = self.__table_mods.get(SHA, None)
            if data is None:
                return None

            return copy.deepcopy(data)


    def get_object_list(self) -> list[str]:
        """获取所有对象名称列表"""
        with self.__call_lock:
            return [x for x in self.__cache_object]


    def get_object_sha_list(self, name: str) -> list[str]:
        """获取对象的所有 SHA 列表"""
        with self.__call_lock:
            return self.__cache_object.get(name, []).copy()


    def get_all_sha_list(self) -> list[str]:
        """所有 SHA 列表"""
        with self.__call_lock:
            return [x for x in self.__table_mods]


    def save_index_file(self, file_from: str) -> None:
        """保存 index 文件"""
        with self.__call_lock:
            if file_from not in self.__original_index: return None
            newfilecontent = json.dumps(self.__original_index[file_from], ensure_ascii=False, sort_keys=False, indent=4)
            with open(file_from, "w", encoding=K.CODE.U8) as fileobject: fileobject.write(newfilecontent)


    def item_data_update(self, SHA: str, data: dict) -> bool:
        """更新 item 的数据

        若 SHA 不存在则返回 False
        """
        core.log.warn(f"更新 index 数据 SHA - {SHA}", L.MODULE_MODS_INDEX)
        with self.__call_lock:
            if SHA not in self.__table_mods: return False

            # 更新缓存数据
            self.__table_mods[SHA].update(data)
            self.cache_update()

            # 更新原始数据
            from_ = self.get_sha_from(SHA)
            self.__original_index[from_][K.INDEX.MODS][SHA].update(data)

            # 保存 index 文件
            self.save_index_file(from_)

            core.construct.event.set_event(E.MODS_INDEX_UPDATE)


    def item_data_new(self, from_: str, SHA: str, data: dict) -> bool:
        """新的 item 的数据"""
        core.log.warn(f"新的 index 数据 SHA - {SHA}", L.MODULE_MODS_INDEX)
        with self.__call_lock:

            # 删除冲突的 SHA 来源
            for key, value in self.__table_from.items():
                if SHA in value: del value[value.index(SHA)]

            # 更新缓存数据
            if from_ not in self.__table_from:
                self.__table_from[from_] = [SHA]

            else:
                self.__table_from[from_].append(SHA)

            self.__table_mods[SHA] = data
            self.cache_update()

            # 更新原始数据
            if from_ not in self.__original_index:
                self.__original_index[from_] = {K.INDEX.MODS: {}}
            self.__original_index[from_][K.INDEX.MODS][SHA] = data

            # 保存 index 文件
            self.save_index_file(from_)

            core.construct.event.set_event(E.MODS_INDEX_UPDATE)


    def item_data_rekey(self, old_SHA: str, new_SHA: str, data: dict | None = None) -> bool:
        """将 item 的 SHA 由 old_SHA 替换为 new_SHA

        保持所属 index 文件与条目顺序不变, data 不为 None 时同时更新数据
        若 old_SHA 不存在或 new_SHA 已存在则返回 False
        """
        core.log.warn(f"替换 index 数据 SHA - {old_SHA} -> {new_SHA}", L.MODULE_MODS_INDEX)
        with self.__call_lock:
            if old_SHA not in self.__table_mods: return False
            if new_SHA in self.__table_mods: return False

            from_ = self.get_sha_from(old_SHA)
            if from_ is None or from_ not in self.__original_index: return False

            item = copy.deepcopy(self.__table_mods[old_SHA])
            if data: item.update(data)

            # 更新原始数据 (保持条目顺序)
            original_mods = self.__original_index[from_][K.INDEX.MODS]
            self.__original_index[from_][K.INDEX.MODS] = {
                (new_SHA if key == old_SHA else key): (item if key == old_SHA else value)
                for key, value in original_mods.items()
            }

            # 更新缓存数据
            del self.__table_mods[old_SHA]
            self.__table_mods[new_SHA] = item
            for key, value in self.__table_from.items():
                if old_SHA in value: value[value.index(old_SHA)] = new_SHA
            self.cache_update()

            # 保存 index 文件
            self.save_index_file(from_)

        core.construct.event.set_event(E.MODS_INDEX_UPDATE)
        return True


    def item_data_del(self, SHA: str):
        """删除 item 的数据

        若 SHA 不存在则返回 False
        """
        core.log.warn(f"删除 index 数据 SHA - {SHA}", L.MODULE_MODS_INDEX)
        with self.__call_lock:
            if SHA not in self.__table_mods: return False

            # 更新原始数据
            from_ = self.get_sha_from(SHA)
            del self.__original_index[from_][K.INDEX.MODS][SHA]

            # 更新缓存数据
            del self.__table_mods[SHA]
            for key, value in self.__table_from.items():
                if SHA in value: del value[value.index(SHA)]
            self.cache_update()

            # 保存 index 文件
            self.save_index_file(from_)

            core.construct.event.set_event(E.MODS_INDEX_UPDATE)

