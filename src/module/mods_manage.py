# -*- coding: utf-8 -*-

# std
import os
import json
import shutil
import threading

import core
from constant import *


UNCLASSIFIED = "未分类"


class ModsManage (object):
    def __init__(self):
        # 分类参照
        self.__reference_classification = {}
        # dict :: 分类名称 : 对象名称[]
        # 储存完整的分类作为参照体

        # 已加载 Mods
        self.__table_loads = {}
        # dict :: 对象名称 : SHA
        # 记录已加载 Mod 的 SHA

        # 本地 SHA 列表
        self.__local_sha_lst = []
        # 记录已下载的 SHA 列表

        # 本地 对象 列表
        self.__local_object_lst = []
        # 仅记录已下载 SHA 的对象名称列表

        # 本地 对象: SHA 列表
        self.__local_object_sha_lst = {}
        # dict :: 对象名称 : SHA
        # 仅记录本地已有对象的 SHA 列表

        # 本地 分类: 对象 列表
        self.__classification = {}
        # dict :: 分类名称 : 对象名称[]
        # 仅记录本地已有的分类及其对象名称列表

        # 本地 分类 列表
        self.__classification_lst = []
        # 仅记录本地已有的分类列表

        # 操作锁
        self.__call_lock = threading._RLock()


    def clear(self):
        core.log.debug("清除缓存索引数据...", L.MODULE_MODS_MANAGE)
        with self.__call_lock:
            self.__reference_classification = {}
            self.__table_loads = {}
            self.__local_sha_lst = []
            self.__local_object_lst = []
            self.__local_object_sha_lst = {}
            self.__classification = {}
            self.__classification_lst = []


    def update_reference_classification(self):
        core.log.debug("更新分类参照...", L.MODULE_MODS_MANAGE)
        with self.__call_lock:
            for class_ in os.listdir(core.userenv.directory.classification):
                path = os.path.join(core.userenv.directory.classification, class_)
                if not os.path.isfile(path): continue

                with open(path, "r", encoding="utf-8") as file_object:
                    file_content = file_object.readlines()

                object_list = [x.strip() for x in file_content if x.strip()]

                self.__reference_classification[class_] = list(dict.fromkeys(object_list))

            self.__dedupe_reference_classification()


    def __ordered_reference_classes(self) -> list[str]:
        """分类参照按用户自定义顺序排列 (不含 "未分类")"""
        index = {name: i for i, name in enumerate(_read_class_order())}
        lst = [x for x in self.__reference_classification if x != UNCLASSIFIED]
        lst.sort(key=lambda x: (index.get(x, len(index)), _list_sort_for_class_name(x)))
        return lst


    def __dedupe_reference_classification(self):
        """保证一个对象只属于一个分类: 按分类顺序保留首次出现, 其余分类中的重复项移除并写回文件"""
        with self.__call_lock:
            seen = set()
            for class_ in self.__ordered_reference_classes():
                objects = self.__reference_classification[class_]
                unique = [x for x in objects if x not in seen]
                seen.update(unique)
                if len(unique) == len(objects): continue

                core.log.warn(f"分类 \"{class_}\" 中的对象已存在于其他分类, 已移除: {[x for x in objects if x not in unique]}", L.MODULE_MODS_MANAGE)
                self.__reference_classification[class_] = unique
                try: self.__write_reference_file(class_, unique)
                except Exception as e: core.log.error(f"写入分类 \"{class_}\" 失败 {e.__class__} {e}", L.MODULE_MODS_MANAGE)


    def __write_reference_file(self, class_: str, objects: list[str]) -> None:
        path = os.path.join(core.userenv.directory.classification, class_)
        with open(path, "w", encoding="utf-8") as file_object:
            file_object.write("".join(f"{x}\n" for x in objects))


    def get_object_class(self, object_: str) -> str | None:
        """返回对象所属的分类, 未归类返回 None"""
        with self.__call_lock:
            for class_, objects in self.__reference_classification.items():
                if object_ in objects: return class_
        return None


    def update_local_sha_list(self):
        core.log.debug("更新本地 SHA...", L.MODULE_MODS_MANAGE)
        with self.__call_lock:
            SHA_lst = core.module.mods_index.get_all_sha_list()
            for SHA in os.listdir(core.env.directory.resources.mods):
                path = os.path.join(core.env.directory.resources.mods, SHA)
                if not os.path.isfile(path): continue
                if SHA not in SHA_lst: continue
                self.__local_sha_lst.append(SHA)


    def update_local_object_list(self):
        core.log.debug("构建本地对象列表...", L.MODULE_MODS_MANAGE)
        with self.__call_lock:
            self.__local_object_lst = []
            for SHA in self.__local_sha_lst:
                item = core.module.mods_index.get_item(SHA)
                if item is None:
                    continue

                object_name = item["object"]
                if object_name in self.__local_object_lst:
                    continue

                self.__local_object_lst.append(object_name)


    def update_local_object_sha_list(self):
        core.log.debug("构建本地对象 SHA 列表...", L.MODULE_MODS_MANAGE)
        with self.__call_lock:
            _local_SHA_set = set(self.__local_sha_lst)
            for object_ in self.__local_object_lst:
                SHA_list = core.module.mods_index.get_object_sha_list(object_)
                intersection = set(SHA_list) & _local_SHA_set
                self.__local_object_sha_lst[object_] = list(intersection)


    def update_local_classification(self):
        core.log.debug("构建本地分类...", L.MODULE_MODS_MANAGE)
        with self.__call_lock:
            _object_lst = set(self.__local_object_lst)

            for class_, object_list in self.__reference_classification.items():
                intersection = _object_lst & set(object_list)
                if len(intersection) == 0: continue

                self.__classification[class_] = list(intersection)
                _object_lst -= intersection

            if len(_object_lst) != 0:
                if "未分类" not in self.__classification: self.__classification["未分类"] = []
                self.__classification["未分类"] += list(_object_lst)

        # 对 Mod 列表排序 (依据 Mod 名称)
        for _, lst in self.__local_object_sha_lst.items(): lst.sort(key=_list_sort_for_item_name)

        # 对 Mod 列表排序 (依据 Mod 分级)
        for _, lst in self.__local_object_sha_lst.items(): lst.sort(key=_list_sort_for_item_grading)

        # 对分类的每个列表进行排序
        for _, lst in self.__classification.items(): lst.sort()

        # ! 本地分类列表
        # self.__classification_lst = [x for x in self.__classification if x != '未分类']

        # ! 参照分类列表
        self.__sort_class_list()


    def __sort_class_list(self):
        """按用户自定义顺序排列分类, 未记录顺序的分类按默认规则排在其后, "未分类" 固定在最后"""
        with self.__call_lock:
            self.__classification_lst = self.__ordered_reference_classes() + [UNCLASSIFIED]


    def set_class_order(self, order: list[str]) -> None:
        """保存分类的自定义顺序并立即应用到分类列表"""
        with self.__call_lock:
            _write_class_order([x for x in order if x and x != UNCLASSIFIED])
            self.__sort_class_list()

        core.construct.event.set_event(E.MODS_MANAGE_CACHE_REFRESHED)


    def update_loaded_mods(self):
        core.log.debug("更新加载模组...", L.MODULE_MODS_MANAGE)
        with self.__call_lock:
            _accident = []
            _conflict = []
            all_sha_list = core.module.mods_index.get_all_sha_list()
            for SHA in os.listdir(core.userenv.directory.work_mods):
                # 排除禁用字段开头的名称
                if SHA.lower().startswith(K.DISABLED): continue

                # 排除 _ 字段开头的名称
                if SHA.startswith("_"): continue

                # 排除不是文件夹的名称
                path = os.path.join(core.userenv.directory.work_mods, SHA)
                if not os.path.isdir(path): continue

                # 检查 SHA 是否在 all_sha_list 中
                if SHA not in all_sha_list:
                    _accident.append(SHA)
                    continue # ! 检查到意外的 SHA

                # 检查是否有相同的 object 被加载
                object_ = core.module.mods_index.get_item(SHA)['object']
                if object_ in self.__table_loads:
                    _conflict.append(SHA)
                    continue
                else:
                    self.__table_loads[object_] = SHA

            # 移除意外的和冲突的 SHA
            if len(_accident) >= 1:
                core.log.warn(f"检查到意外的 SHA: {_accident}", L.MODULE_MODS_MANAGE)

            if len(_conflict) >= 1:
                core.log.warn(f"检查到冲突的 SHA: {_conflict}", L.MODULE_MODS_MANAGE)

            for SHA in _accident + _conflict:
                self.remove(SHA)


    def get_class_list(self) -> list[str]:
        # return [x for x in self.__reference_classification] + ["未分类"]
        return self.__classification_lst.copy()


    def get_reference_object_list(self, class_: str) -> list[str]:
        return self.__reference_classification.get(class_, []).copy()


    def get_object_list(self, class_: str) -> list[str]:
        """返回分类下的对象列表

        顺序与分类参照文件一致 (可在 "管理子对象" 中调整),
        "未分类" 按名称排序;
        未开启 "显示没有 Mod 的对象" 时, 仅返回本地已有 Mod 的对象
        """
        local = self.__classification.get(class_, [])
        if class_ == UNCLASSIFIED:
            return sorted(local)

        result = list(dict.fromkeys(self.__reference_classification.get(class_, [])))
        result += sorted(set(local) - set(result))

        if not core.env.configuration.show_empty_objects:
            result = [x for x in result if self.__local_object_sha_lst.get(x)]

        return result


    def set_reference_object_list(self, class_: str, objects: list[str]) -> None:
        """保存分类参照中的对象列表 (仅调整顺序时无需完整刷新)

        一个对象只能属于一个分类, 列表中的对象会从其他分类中移除
        """
        if not class_ or class_ == UNCLASSIFIED: return

        objects = [x for x in dict.fromkeys(x.strip() for x in objects) if x]
        with self.__call_lock:
            _objects = set(objects)
            for other, other_objects in self.__reference_classification.items():
                if other == class_ or not (_objects & set(other_objects)): continue
                remain = [x for x in other_objects if x not in _objects]
                self.__write_reference_file(other, remain)
                self.__reference_classification[other] = remain

            self.__write_reference_file(class_, objects)
            self.__reference_classification[class_] = objects

        core.construct.event.set_event(E.MODS_MANAGE_CACHE_REFRESHED)


    def get_object_sha_list(self, object_: str) -> list[str]:
        return self.__local_object_sha_lst.get(object_, []).copy()


    def get_load_object_sha(self, object_: str) -> str | None:
        return self.__table_loads.get(object_, None)


    def is_load_object(self, object_: str):
        if object_ in self.__table_loads: return True
        return False


    def is_local_sha(self, SHA: str):
        if SHA in self.__local_sha_lst: return True
        return False


    def is_loaded_sha(self, SHA: str) -> bool:
        """该 SHA 是否正在被使用 (已加载到工作目录且处于启用状态)"""
        with self.__call_lock:
            return SHA in self.__table_loads.values()


    def is_cached_sha(self, SHA: str) -> bool:
        """该 SHA 是否在工作目录中存在解压缓存 (含已启用与已卸载)

        直接探测文件系统而不依赖内存缓存, 避免状态与磁盘实际情况不一致
        """
        for name in (SHA, f"{K.DISABLED}-{SHA}"):
            try:
                if os.path.isdir(os.path.join(core.userenv.directory.work_mods, name)):
                    return True

            except Exception:
                return False

        return False


    # ---------------------------------------------- 插件兼容 (原版 1.5.19+ 同名接口)
    def is_load_sha(self, sha: str) -> bool:
        """是否为已加载 SHA (同 is_loaded_sha)"""
        return self.is_loaded_sha(sha)


    def is_have_cache_load(self, sha: str) -> bool:
        """是否拥有已卸载的缓存 (工作目录中存在 DISABLED-SHA 文件夹)"""
        try:
            return os.path.isdir(os.path.join(core.userenv.directory.work_mods, f"{K.DISABLED}-{sha}"))

        except Exception:
            return False


    def refresh(self):
        core.log.info("刷新 Mods 管理索引缓存...", L.MODULE_MODS_MANAGE)
        self.clear()

        with self.__call_lock:
            self.update_reference_classification()
            self.update_local_sha_list()
            self.update_local_object_list()
            self.update_local_object_sha_list()
            self.update_local_classification()
            self.update_loaded_mods()

        core.construct.event.set_event(E.MODS_MANAGE_CACHE_REFRESHED)


    def load(self, SHA: str) -> None:
        core.log.debug(f"加载 Mod {SHA}", L.MODULE_MODS_MANAGE)
        with self.__call_lock:
            item = core.module.mods_index.get_item(SHA)
            object_ = item['object']

            # 如果 SHA 已经被加载则不做任何操作
            if SHA == self.__table_loads.get(object_, None):
                return

            # 如果 SHA 存在且拥有禁用标识则去除
            dsname = f"{K.DISABLED}-{SHA}"
            if dsname in os.listdir(core.userenv.directory.work_mods):
                old_path = os.path.join(core.userenv.directory.work_mods, dsname)
                new_path = os.path.join(core.userenv.directory.work_mods, SHA)
                os.rename(old_path, new_path)

            # 如果 SHA 不存在则从资源部署
            else:
                from_file = os.path.join(core.env.directory.resources.mods, SHA)
                to_path = os.path.join(core.userenv.directory.work_mods, SHA)

                mod_type = str(item.get(K.INDEX.TYPE, '')).lower()

                # 单文件形式的 Mod (例如 .ini) 无需解压, 直接复制到工作目录
                if mod_type in K.MOD_TYPE.PLAIN:
                    _deploy_plain_mod(from_file, to_path, item.get(K.INDEX.NAME, ''), mod_type, SHA)

                else:
                    core.external.x7z(from_file, to_path)

            # 卸载冲突对象的 SHA Mod
            # 由本方法统一发出 MOD_LOADED 事件, 无需 unload 重复通知
            try: self.unload(object_, _notify=False)
            except Exception: ...

            # 更新缓存
            self.__table_loads[object_] = SHA

        core.construct.event.set_event(E.MOD_LOADED)
        return None


    def unload(self, object_: str, _notify: bool = True) -> None:
        core.log.debug(f"卸载 Mod {object_}", L.MODULE_MODS_MANAGE)
        with self.__call_lock:
            SHA = self.__table_loads.get(object_, None)
            if SHA is None: return None

            try:
                # 在文件夹前面加上禁用标识
                dsname = f"{K.DISABLED}-{SHA}"
                old_path = os.path.join(core.userenv.directory.work_mods, SHA)
                new_path = os.path.join(core.userenv.directory.work_mods, dsname)
                os.rename(old_path, new_path)
                # target = os.path.join(core.userenv.directory.work_mods, SHA)
                # shutil.rmtree(target)

            except FileNotFoundError:
                ...

            except Exception:
                ...

            finally:
                del self.__table_loads[object_]

        # 卸载只是重命名目录, 解压缓存依然保留
        if _notify: core.construct.event.set_event(E.MOD_UNLOADED)
        return None


    def get_loaded_objects(self, class_: str | None = None) -> list[str]:
        """返回已加载 Mod 的对象列表; 指定 class_ 时仅返回该分类下的对象

        对象所属分类以分类参照为准, 不在任何分类参照中的对象视为 "未分类"
        """
        with self.__call_lock:
            objects = list(self.__table_loads)
            if class_ is None: return objects
            return [x for x in objects if (self.get_object_class(x) or UNCLASSIFIED) == class_]


    def unload_objects(self, objects: list[str]) -> int:
        """批量卸载指定对象的 Mod, 只发出一次 MOD_UNLOADED 事件, 返回实际卸载的数量"""
        count = 0
        with self.__call_lock:
            for object_ in list(objects):
                if object_ not in self.__table_loads: continue
                try:
                    self.unload(object_, _notify=False)
                    count += 1

                except Exception as e:
                    core.log.error(f"卸载 \"{object_}\" 失败 {e.__class__} {e}", L.MODULE_MODS_MANAGE)

        core.log.info(f"批量卸载 Mod {count} 个", L.MODULE_MODS_MANAGE)
        if count: core.construct.event.set_event(E.MOD_UNLOADED)
        return count


    def unload_class(self, class_: str) -> int:
        """卸载分类下全部已加载的 Mod"""
        return self.unload_objects(self.get_loaded_objects(class_))


    def unload_all(self) -> int:
        """卸载全部已加载的 Mod (所有分类)"""
        return self.unload_objects(self.get_loaded_objects())


    def remove(self, SHA: str) -> None:
        with self.__call_lock:
            target = os.path.join(core.userenv.directory.work_mods, SHA)
            shutil.rmtree(target)


def _safe_filename(name: str, default: str) -> str:
    """将任意文本转换为安全的文件名主干 (不含扩展名)"""
    text = ''.join('_' if char in '\\/:*?"<>|' else char for char in str(name))
    text = ''.join(char for char in text if char.isprintable()).strip(' .')
    if not text: return default
    return text[:64].strip(' .') or default


def _deploy_plain_mod(from_file: str, to_path: str, name: str, mod_type: str, SHA: str) -> None:
    """部署单文件形式的 Mod

    归档形式的 Mod 由 7zip 解压出目录结构, 而单文件形式的 Mod (例如 .ini)
    在 resources/mods 中就是文件本体, 只需要在工作目录中建立同名文件夹并复制进去
    """
    # 与 7zip 解压失败时的行为保持一致: 不抛出异常, 仅记录日志
    if not os.path.isfile(from_file):
        core.log.error(f"部署单文件 Mod 失败: 找不到 Mod 文件 {from_file}", L.MODULE_MODS_MANAGE)
        return

    filename = f"{_safe_filename(name, SHA)}.{mod_type}"
    core.log.debug(f"部署单文件 Mod {SHA} -> {filename}", L.MODULE_MODS_MANAGE)

    try:
        os.makedirs(to_path, exist_ok=True)
        shutil.copyfile(from_file, os.path.join(to_path, filename))

    except Exception as e:
        core.log.error(f"部署单文件 Mod 失败 {SHA} {e.__class__} {e}", L.MODULE_MODS_MANAGE)


def _read_class_order() -> list[str]:
    """读取分类自定义顺序 list :: 分类名称[]"""
    try:
        with open(core.userenv.file.classification_order, "r", encoding="utf-8") as file_object:
            data = json.load(file_object)
    except Exception:
        return []

    if not isinstance(data, list): return []
    return [x for x in data if isinstance(x, str)]


def _write_class_order(order: list[str]) -> None:
    with open(core.userenv.file.classification_order, "w", encoding="utf-8") as file_object:
        json.dump(order, file_object, ensure_ascii=False, indent=4)


def _list_sort_for_item_name(key) -> str:
    try:
        return core.module.mods_index.get_item(key)["name"]

    except Exception:
        return key


def _list_sort_for_item_grading(key) -> str:
    try:
        return core.module.mods_index.get_item(key)[K.INDEX.GRADING]

    except Exception:
        return key


CLASS_NAME_SORT_LIST = ["角色", "武器", "."]


def _list_sort_for_class_name(key) -> int:
    for index, value in enumerate(CLASS_NAME_SORT_LIST):
        if value in key:
            return index

    else:
        return len(CLASS_NAME_SORT_LIST)
