# -*- coding: utf-8 -*-
"""右键菜单: 卸载本分类 Mods / 卸载全部 Mods

对应原版插件 unload_object_mods (卸载本分类 Mods) 与
batch_processing_tools (卸载全部 Mods) 的功能。
卸载只是给工作目录中的 Mod 文件夹加上禁用标识, 解压缓存依然保留。
"""

# project
import core


UNCLASSIFIED = '未分类'


def loaded_count(class_: str | None = None) -> int:
    try:
        return len(core.module.mods_manage.get_loaded_objects(class_))

    except Exception:
        return 0


def _status(message: str):
    try: core.window.status.set_status(message)
    except Exception: ...


def unload_class(class_: str | None):
    if not class_: return

    count = loaded_count(class_)
    if count == 0:
        _status(f"分类 \"{class_}\" 下没有已加载的 Mod")
        return

    if not core.window.messagebox.askyesno("卸载本分类 Mods", f"将卸载分类 \"{class_}\" 下已加载的 {count} 个 Mod, 是否继续?"):
        return

    done = core.module.mods_manage.unload_class(class_)
    _status(f"已卸载分类 \"{class_}\" 下的 {done} 个 Mod, 请在游戏中按 F10 重新加载")


def unload_all():
    count = loaded_count()
    if count == 0:
        _status("没有已加载的 Mod")
        return

    if not core.window.messagebox.askyesno("卸载全部 Mods", f"将卸载所有分类下已加载的 {count} 个 Mod, 是否继续?"):
        return

    done = core.module.mods_manage.unload_all()
    _status(f"已卸载全部 {done} 个 Mod, 请在游戏中按 F10 重新加载")


def add_to_menu(menu, class_: str | None, separator: bool = True, with_class: bool = True):
    """向 PopupMenu 追加卸载菜单项"""
    if separator: menu.add_separator()

    if with_class:
        menu.add_command(
            label='卸载本分类 Mods',
            command=lambda: unload_class(class_),
            enabled=bool(class_) and loaded_count(class_) > 0,
        )

    menu.add_command(label='卸载全部 Mods', command=unload_all, enabled=loaded_count() > 0)


__all__ = ["unload_class", "unload_all", "add_to_menu"]
