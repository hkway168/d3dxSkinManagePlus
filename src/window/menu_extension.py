# -*- coding: utf-8 -*-
"""右键菜单扩展注册表

兼容原版 d3dxSkinManage (1.5.19+) 中 widgets.DynamicMenu.add_label 的接口,
供插件向本地自绘的 PopupMenu 追加菜单项。本类只负责登记与筛选, 不绑定任何事件,
实际弹出仍由各自的右键菜单完成。
"""

# std
import threading
import traceback

# local
import core


try:
    infinity = float("inf")

except Exception:
    infinity = 10 ** 10


class MenuExtension (object):
    def __init__(self):
        self._lock = threading.RLock()
        self._table: dict[int, list[dict]] = {}


    def add_label(self, label: str, command: object, group: int = 100, order: int = -1,
                  condition: bool | object = True, state_condition: bool | object = True, need_value: bool = False):
        """
        ## 添加标签 (与原版 DynamicMenu.add_label 参数一致)

        ```
        label: str 标签文本内容
        command: object 点击标签后执行的函数 (无参数调用)
        group: int 所属组, 同时决定组的排序, 不同的组之间会有分割线
        order: int 组内排序, -1 表示排在末尾
        condition: bool | object 显示条件, 结果为 True 才会显示
        state_condition: bool | object 状态条件, 结果为 False 时菜单项置灰
        need_value: bool 条件函数是否需要参数 (右键命中的条目 iid)
        ```
        """
        if not isinstance(label, str) or not callable(command):
            raise TypeError("label must be str and command must be callable.")

        with self._lock:
            self._table.setdefault(int(group), []).append({
                "label": label,
                "command": self._safe_command(label, command),
                "order": infinity if order == -1 else order,
                "condition": condition,
                "state_condition": state_condition,
                "need_value": bool(need_value),
            })
            self._table[int(group)].sort(key=lambda x: x["order"])


    @staticmethod
    def _safe_command(label: str, command):
        """包装插件命令: 异常写入日志并在状态栏提示, 不再被静默丢弃"""
        def wrapper(*args, **kwds):
            try:
                return command(*args, **kwds)

            except Exception as e:
                exc = traceback.format_exc()
                core.log.error(f"菜单标签 \"{label}\" 执行异常 {e.__class__} {e}\n{exc}")
                try: core.window.status.set_status(f"\"{label}\" 执行异常 {e.__class__.__name__}: {e}", 1)
                except Exception: ...

        return wrapper


    def __len__(self):
        with self._lock:
            return sum(len(x) for x in self._table.values())


    @staticmethod
    def _judge(cond, need_value: bool, value) -> bool:
        if isinstance(cond, bool): return cond
        if callable(cond): return bool(cond(value) if need_value else cond())
        return True


    def collect(self, value) -> list[list[tuple[str, object, bool]]]:
        """按组返回满足显示条件的菜单项 [(label, command, enabled), ...]"""
        result = []

        with self._lock:
            groups = [(g, list(items)) for g, items in sorted(self._table.items())]

        for _, items in groups:
            group_result = []

            for item in items:
                label = item["label"]
                try:
                    if not self._judge(item["condition"], item["need_value"], value): continue
                    enabled = self._judge(item["state_condition"], item["need_value"], value)
                    group_result.append((label, item["command"], enabled))

                except Exception as e:
                    core.log.error(f"添加菜单标签 \"{label}\" 时出现异常 {e.__class__} {e}")

            if group_result:
                result.append(group_result)

        return result


    def apply(self, menu, value, separator: bool) -> int:
        """将扩展项追加到 PopupMenu, 返回追加的菜单项数量"""
        count = 0

        for group in self.collect(value):
            if separator or count:
                menu.add_separator()

            for label, command, enabled in group:
                menu.add_command(label=label, command=command, enabled=enabled)
                count += 1

        return count


__all__ = ["MenuExtension"]
