# -*- coding: utf-8 -*-

# std
import os
import threading

# install
import win32gui
import ttkbootstrap

# project
import core
from constant import *
from window import dpi
from window.popup_menu import PopupMenu

from . import unload_mods


illegalchat = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']

UNCLASSIFIED = '未分类'


class selfstatus (object):
    action = threading.Lock()


def _classification_path(classname: str) -> str:
    return os.path.join(core.userenv.directory.classification, classname)


def _check_classname(classname: str) -> str | None:
    if not classname: return "分类名称不能为空"
    if classname == UNCLASSIFIED: return f"\"{UNCLASSIFIED}\" 为保留名称"
    for chat in illegalchat:
        if chat in classname: return "分类名称包含非法字符"
    return None


def _write_classification_file(classname: str, content: str) -> None:
    with open(_classification_path(classname), 'w', encoding='utf-8') as f:
        f.write(content)


def _remove_classification_file(classname: str) -> None:
    try: os.remove(_classification_path(classname))
    except FileNotFoundError: ...


def _reference_objects(classname: str) -> list[str]:
    """分类参照中的对象列表 (去重, 保持文件顺序)"""
    return list(dict.fromkeys(core.module.mods_manage.get_reference_object_list(classname)))


def _unclassified_objects() -> list[str]:
    """尚未归入任何分类的对象: 本地已有 Mod 的对象在前, 其余在后, 各自按名称排序"""
    classified = set()
    for classname in core.module.mods_manage.get_class_list():
        if classname == UNCLASSIFIED: continue
        classified |= set(core.module.mods_manage.get_reference_object_list(classname))

    objects = [x for x in dict.fromkeys(core.module.mods_index.get_object_list()) if x and x not in classified]
    local = sorted(x for x in objects if core.module.mods_manage.get_object_sha_list(x))
    others = sorted(x for x in objects if x not in set(local))
    return local + others


def _refresh_in_background():
    threading.Thread(None, core.module.mods_manage.refresh, 'classification-refresh', daemon=True).start()


def _place_near_cursor(windows) -> None:
    """将窗口居中放置在鼠标附近, 并禁止调整大小

    窗口创建后处于隐藏状态, 定位完成后再显示, 避免先出现在默认位置再跳到鼠标附近
    """
    windows.update_idletasks()

    width = windows.winfo_reqwidth()
    height = windows.winfo_reqheight()

    _x, _y = win32gui.GetCursorInfo()[2]

    x = max(0, _x - width // 2)
    y = max(0, _y - height // 2 - 20)

    windows.geometry(f'+{x}+{y}')
    windows.resizable(False, False)
    windows.deiconify()


def _askyesno(title: str, message: str, parent=None) -> bool:
    options = {'icon': 'warning'}
    if parent is not None: options['parent'] = parent
    return bool(core.window.messagebox.askyesno(title=title, message=message, **options))


# ================================================================== 基础窗口
class _Dialog (object):
    """分类相关窗口基类: 互斥锁 + 窗口创建"""
    title = ''

    def __init__(self):
        result = selfstatus.action.acquire(timeout=0.01)
        if not result:
            core.window.messagebox.showerror(title='互斥锁请求超时', message='互斥锁正在被其他线程占用\n上一次操作未结束或锁没有被正确释放\n亦或是你想测试这个操作是不是线程安全的')
            return

        try:
            self.windows = ttkbootstrap.Toplevel(self.title)
            self.windows.withdraw()
            self.windows.transient(core.window.mainwindow)

            try:
                self.windows.iconbitmap(default=core.env.file.local.iconbitmap)
                self.windows.iconbitmap(bitmap=core.env.file.local.iconbitmap)
            except Exception:
                ...

            self.windows.protocol('WM_DELETE_WINDOW', self.bin_cancel)
            self.install()
            _place_near_cursor(self.windows)

        except Exception:
            try: self.windows.destroy()
            except Exception: ...
            selfstatus.action.release()
            raise

    def install(self):
        raise NotImplementedError

    def bin_cancel(self, *args):
        self.windows.destroy()
        selfstatus.action.release()


class _ManageList (_Dialog):
    """列表管理窗口基类: 排序 (置顶 / 上移 / 下移 / 置底) + 删除 + 可选的重命名"""
    STYLE = 'ClassManage.Treeview'

    delete_text = '删除'
    empty_text = '列表为空'
    renamable = False
    rename_label = '名称'

    def __init__(self, preset: str | None = None):
        self.preset = preset
        super().__init__()

    # -------------------------------------------------- 子类实现
    def install_header(self): ...
    def load_items(self) -> list[str]: raise NotImplementedError
    def item_text(self, name: str) -> str: return name
    def save_order(self, order: list[str]) -> None: raise NotImplementedError
    def delete_item(self, name: str) -> bool: raise NotImplementedError
    def rename_item(self, old: str, new: str) -> str | None: raise NotImplementedError

    # -------------------------------------------------- 界面
    def install(self):
        S = dpi.scale

        self.order = self.load_items()

        # 列表只显示单行文字, 使用独立样式覆盖主界面 Treeview 的双行行高
        try: core.window.style.configure(self.STYLE, rowheight=dpi.line_height() + S(10))
        except Exception: ...

        self.install_header()

        self.Frame_body = ttkbootstrap.Frame(self.windows)
        self.Frame_list = ttkbootstrap.Frame(self.Frame_body)
        self.Treeview_list = ttkbootstrap.Treeview(self.Frame_list, show='tree', selectmode='browse', height=12, style=self.STYLE)
        self.Scrollbar_list = ttkbootstrap.Scrollbar(self.Frame_list, command=self.Treeview_list.yview)
        self.Treeview_list.config(yscrollcommand=self.Scrollbar_list.set)
        self.Treeview_list.column('#0', width=S(260), stretch=True, anchor='w')

        self.Frame_buttons = ttkbootstrap.Frame(self.Frame_body)
        button = lambda text, command, style='primary-outline': ttkbootstrap.Button(self.Frame_buttons, text=text, width=10, bootstyle=style, command=command)
        self.Button_top = button('置顶', lambda: self.bin_move('top'))
        self.Button_up = button('上移', lambda: self.bin_move('up'))
        self.Button_down = button('下移', lambda: self.bin_move('down'))
        self.Button_bottom = button('置底', lambda: self.bin_move('bottom'))
        self.Button_delete = button(self.delete_text, self.bin_delete, 'danger-outline')

        self.Frame_options = ttkbootstrap.Frame(self.windows)
        self.Label_errormsg = ttkbootstrap.Label(self.Frame_options, text='', bootstyle='danger')
        self.Button_close = ttkbootstrap.Button(self.Frame_options, text='关闭', width=10, bootstyle='warning-outline', command=self.bin_cancel)

        self.Frame_body.pack(side='top', fill='both', expand=True, padx=10, pady=10)
        self.Frame_list.pack(side='left', fill='both', expand=True)
        self.Scrollbar_list.pack(side='right', fill='y', padx=(S(2), 0))
        self.Treeview_list.pack(side='left', fill='both', expand=True)
        self.Frame_buttons.pack(side='left', fill='y', padx=(10, 0))
        for widget in (self.Button_top, self.Button_up, self.Button_down, self.Button_bottom):
            widget.pack(side='top', pady=(0, 5))
        self.Button_delete.pack(side='top', pady=(15, 0))

        if self.renamable:
            self.Frame_rename = ttkbootstrap.Frame(self.windows)
            self.Label_rename = ttkbootstrap.Label(self.Frame_rename, text=self.rename_label)
            self.Entry_rename = ttkbootstrap.Entry(self.Frame_rename)
            self.Button_rename = ttkbootstrap.Button(self.Frame_rename, text='重命名', width=10, bootstyle='success-outline', command=self.bin_rename)

            self.Frame_rename.pack(side='top', fill='x', padx=10, pady=(0, 10))
            self.Label_rename.pack(side='left')
            self.Button_rename.pack(side='right', padx=(10, 0))
            self.Entry_rename.pack(side='left', fill='x', expand=True, padx=(10, 0))
            self.Entry_rename.bind('<Return>', self.bin_rename)

        self.Frame_options.pack(side='top', fill='x', padx=10, pady=(0, 10))
        self.Button_close.pack(side='right')
        self.Label_errormsg.pack(side='left')

        self.Treeview_list.bind('<<TreeviewSelect>>', self.bin_select)
        self.windows.bind('<Escape>', self.bin_cancel)

        self.update_list()
        preset = self.preset if self.preset in self.order else (self.order[0] if self.order else None)
        self.select(preset)

    # -------------------------------------------------- 列表
    def update_list(self):
        tree = self.Treeview_list
        tree.delete(*tree.get_children())
        for name in self.order:
            tree.insert('', 'end', name, text=self.item_text(name))

        if not self.order:
            self.Label_errormsg.config(text=self.empty_text)

        self.update_buttons()

    def select(self, name: str | None):
        if name and self.Treeview_list.exists(name):
            self.Treeview_list.selection_set(name)
            self.Treeview_list.focus(name)
            self.Treeview_list.see(name)

        self.update_buttons()

    def selected(self) -> str | None:
        selection = self.Treeview_list.selection()
        return selection[0] if selection else None

    def update_buttons(self):
        name = self.selected()
        index = self.order.index(name) if name in self.order else -1
        last = len(self.order) - 1

        def state(enabled): return 'normal' if enabled else 'disabled'
        self.Button_top.config(state=state(index > 0))
        self.Button_up.config(state=state(index > 0))
        self.Button_down.config(state=state(0 <= index < last))
        self.Button_bottom.config(state=state(0 <= index < last))
        self.Button_delete.config(state=state(index >= 0))
        if self.renamable: self.Button_rename.config(state=state(index >= 0))

    def bin_select(self, *args):
        name = self.selected()
        if self.renamable:
            self.Entry_rename.delete(0, 'end')
            if name: self.Entry_rename.insert(0, name)
        self.Label_errormsg.config(text='')
        self.update_buttons()

    # -------------------------------------------------- 操作
    def bin_move(self, where: str):
        name = self.selected()
        if name not in self.order: return

        index = self.order.index(name)
        target = {
            'top': 0,
            'up': index - 1,
            'down': index + 1,
            'bottom': len(self.order) - 1,
        }[where]
        target = max(0, min(target, len(self.order) - 1))
        if target == index: return

        self.order.insert(target, self.order.pop(index))
        self.Treeview_list.move(name, '', target)
        self.select(name)

        self.save_order(self.order)

    def bin_rename(self, *args):
        old = self.selected()
        if old not in self.order: return

        new = self.Entry_rename.get().strip()
        if new == old: return

        errormsg = self.rename_item(old, new)
        if errormsg is not None:
            self.Label_errormsg.config(text=errormsg)
            return

        index = self.order.index(old)
        self.order[index] = new
        self.Treeview_list.delete(old)
        self.Treeview_list.insert('', index, new, text=self.item_text(new))
        self.select(new)
        self.Label_errormsg.config(text='')

    def bin_delete(self, *args):
        name = self.selected()
        if name not in self.order: return

        index = self.order.index(name)
        if not self.delete_item(name): return

        self.order.remove(name)
        self.Treeview_list.delete(name)
        if self.order: self.select(self.order[min(index, len(self.order) - 1)])
        else: self.update_list()


# ================================================================== 分类
class AddClassification (_Dialog):
    """添加分类: 仅需输入分类名称"""
    title = '添加分类'

    def install(self):
        self.Frame_classname = ttkbootstrap.Frame(self.windows)
        self.Label_classname = ttkbootstrap.Label(self.Frame_classname, text='分类名称')
        self.Entry_classname = ttkbootstrap.Entry(self.Frame_classname, width=40)
        self.Frame_options = ttkbootstrap.Frame(self.windows)
        self.Button_ok = ttkbootstrap.Button(self.Frame_options, text='保存', width=10, bootstyle="success-outline", command=self.bin_ok)
        self.Button_cancel = ttkbootstrap.Button(self.Frame_options, text='取消', width=10, bootstyle="warning-outline", command=self.bin_cancel)
        self.Label_errormsg = ttkbootstrap.Label(self.Frame_options, text='', bootstyle="danger")

        self.Frame_classname.pack(side='top', fill='x', padx=10, pady=10)
        self.Label_classname.pack(side='left', padx=0, pady=0)
        self.Entry_classname.pack(side='left', fill='x', expand=True, padx=(10, 0), pady=0)
        self.Frame_options.pack(side='top', fill='x', padx=10, pady=(0, 10))
        self.Button_ok.pack(side='right', padx=0, pady=0)
        self.Button_cancel.pack(side='right', padx=(0, 5), pady=0)
        self.Label_errormsg.pack(side='left', padx=(0, 5), pady=0)

        self.windows.bind('<Return>', self.bin_ok)
        self.windows.bind('<Escape>', self.bin_cancel)

        _alt_set = core.window.annotation_toplevel.register
        _alt_set(self.Entry_classname, T.ANNOTATION_CLASS_NAME, 2)
        _alt_set(self.Button_ok, T.ANNOTATION_MODIFY_CLASS_OK, 2)
        _alt_set(self.Button_cancel, T.ANNOTATION_MODIFY_CLASS_CANCEL, 2)

        self.Entry_classname.focus_set()

    def bin_ok(self, *args):
        classname = self.Entry_classname.get().strip()
        core.log.debug(f"添加分类 \"{classname}\" ")

        errormsg = _check_classname(classname)
        if errormsg is None and os.path.exists(_classification_path(classname)):
            errormsg = "分类名称已存在或被占用"

        if errormsg is not None:
            self.Label_errormsg.config(text=errormsg)
            return

        _write_classification_file(classname, '')
        self.bin_cancel()
        _refresh_in_background()


class ManageClassification (_ManageList):
    """管理分类: 排序 / 重命名 / 删除"""
    title = '管理分类'
    empty_text = '暂无分类'
    renamable = True
    rename_label = '分类名称'

    def load_items(self):
        return [x for x in core.module.mods_manage.get_class_list() if x != UNCLASSIFIED]

    def item_text(self, name):
        return f'{name}  [{len(core.module.mods_manage.get_object_list(name))}]'

    def save_order(self, order):
        core.module.mods_manage.set_class_order(order)

    def rename_item(self, old, new):
        errormsg = _check_classname(new)
        if errormsg is None and os.path.exists(_classification_path(new)):
            errormsg = "分类名称已存在或被占用"
        if errormsg is not None: return errormsg

        os.rename(_classification_path(old), _classification_path(new))
        self.save_order([new if x == old else x for x in self.order])
        _refresh_in_background()

    def delete_item(self, name):
        count = len(_reference_objects(name))
        message = f'确定要删除分类 "{name}" 吗？'
        if count: message += f'\n\n该分类下的 {count} 个对象将一并从分类中移除，对应的 Mod 不会被删除。'
        message += '\n\n此操作不可撤销。'
        if not _askyesno('删除分类', message, parent=self.windows): return False

        _remove_classification_file(name)
        self.save_order([x for x in self.order if x != name])
        _refresh_in_background()
        return True

    def install(self):
        super().install()
        _alt_set = core.window.annotation_toplevel.register
        _alt_set(self.Entry_rename, T.ANNOTATION_CLASS_NAME, 2)
        _alt_set(self.Button_delete, T.ANNOTATION_MODIFY_CLASS_DELETE, 2)


# ================================================================== 对象
class AddObject (_Dialog):
    """添加对象: 向分类中添加一个具体对象 (追加到分类参照文件)"""
    title = '添加对象'

    def __init__(self, classname: str):
        self.classname = classname
        super().__init__()

    def install(self):
        width = 40

        self.exist_objects = set(_reference_objects(self.classname))
        candidates = _unclassified_objects()

        self.Frame_parent = ttkbootstrap.Frame(self.windows)
        self.Label_parent = ttkbootstrap.Label(self.Frame_parent, text='所属分类')
        self.Entry_parent = ttkbootstrap.Entry(self.Frame_parent, width=width)
        self.Frame_object = ttkbootstrap.Frame(self.windows)
        self.Label_object = ttkbootstrap.Label(self.Frame_object, text='对象名称')
        self.Combobox_object = ttkbootstrap.Combobox(self.Frame_object, width=width, values=candidates)
        self.Frame_options = ttkbootstrap.Frame(self.windows)
        self.Button_ok = ttkbootstrap.Button(self.Frame_options, text='保存', width=10, bootstyle="success-outline", command=self.bin_ok)
        self.Button_cancel = ttkbootstrap.Button(self.Frame_options, text='取消', width=10, bootstyle="warning-outline", command=self.bin_cancel)
        self.Label_errormsg = ttkbootstrap.Label(self.Frame_options, text='', bootstyle="danger")

        self.Entry_parent.insert(0, self.classname)
        self.Entry_parent.config(state='readonly')

        self.Frame_parent.pack(side='top', fill='x', padx=10, pady=(10, 0))
        self.Label_parent.pack(side='left', padx=0, pady=0)
        self.Entry_parent.pack(side='left', fill='x', expand=True, padx=(10, 0), pady=0)
        self.Frame_object.pack(side='top', fill='x', padx=10, pady=10)
        self.Label_object.pack(side='left', padx=0, pady=0)
        self.Combobox_object.pack(side='left', fill='x', expand=True, padx=(10, 0), pady=0)
        self.Frame_options.pack(side='top', fill='x', padx=10, pady=(0, 10))
        self.Button_ok.pack(side='right', padx=0, pady=0)
        self.Button_cancel.pack(side='right', padx=(0, 5), pady=0)
        self.Label_errormsg.pack(side='left', padx=(0, 5), pady=0)

        self.windows.bind('<Return>', self.bin_ok)
        self.windows.bind('<Escape>', self.bin_cancel)

        _alt_set = core.window.annotation_toplevel.register
        _alt_set(self.Combobox_object, T.ANNOTATION_ADD_OBJECT, 2)
        _alt_set(self.Button_ok, T.ANNOTATION_MODIFY_CLASS_OK, 2)
        _alt_set(self.Button_cancel, T.ANNOTATION_MODIFY_CLASS_CANCEL, 2)

        self.Combobox_object.focus_set()

    def bin_ok(self, *args):
        object_ = self.Combobox_object.get().strip()
        core.log.debug(f"分类 \"{self.classname}\" 添加对象 \"{object_}\" ")

        if not object_:
            self.Label_errormsg.config(text="对象名称不能为空")
            return

        if object_ in self.exist_objects:
            self.Label_errormsg.config(text="该对象已在分类中")
            return

        # 一个对象只能属于一个分类, 已在其他分类中时询问是否移动
        other = core.module.mods_manage.get_object_class(object_)
        if other is not None and other != self.classname:
            message = f'对象 "{object_}" 已在分类 "{other}" 中。\n\n一个对象只能属于一个分类，是否将其移动到分类 "{self.classname}"？'
            if not _askyesno('移动对象', message, parent=self.windows): return

        core.module.mods_manage.set_reference_object_list(self.classname, _reference_objects(self.classname) + [object_])

        self.bin_cancel()
        _refresh_in_background()


class ManageObjects (_ManageList):
    """管理子对象: 调整分类中对象的顺序 / 从分类中移除对象"""
    title = '管理子对象'
    delete_text = '移除'
    empty_text = '该分类下暂无对象'

    def __init__(self, classname: str, preset: str | None = None):
        self.classname = classname
        super().__init__(preset)

    def install_header(self):
        self.Frame_parent = ttkbootstrap.Frame(self.windows)
        self.Label_parent = ttkbootstrap.Label(self.Frame_parent, text='所属分类')
        self.Entry_parent = ttkbootstrap.Entry(self.Frame_parent)
        self.Entry_parent.insert(0, self.classname)
        self.Entry_parent.config(state='readonly')

        self.Frame_parent.pack(side='top', fill='x', padx=10, pady=(10, 0))
        self.Label_parent.pack(side='left')
        self.Entry_parent.pack(side='left', fill='x', expand=True, padx=(10, 0))

    def load_items(self):
        return _reference_objects(self.classname)

    def item_text(self, name):
        local_ = len(core.module.mods_manage.get_object_sha_list(name))
        all_ = len(core.module.mods_index.get_object_sha_list(name))
        return f'{name}  [{local_}/{all_}]'

    def save_order(self, order):
        core.module.mods_manage.set_reference_object_list(self.classname, order)

    def delete_item(self, name):
        message = f'确定要将对象 "{name}" 从分类 "{self.classname}" 中移除吗？\n\n对应的 Mod 不会被删除。'
        if not _askyesno('移除对象', message, parent=self.windows): return False

        self.save_order([x for x in self.order if x != name])
        _refresh_in_background()
        return True


# ================================================================== 右键菜单
class _ContextMenu (object):
    def __init__(self, treeview):
        self.treeview = treeview
        self.menu = PopupMenu(treeview)
        treeview.bind('<ButtonRelease-3>', self.bin_release, add='+')

    def bin_release(self, event):
        self.menu.close()

        try: core.window.annotation_toplevel.withdraw()
        except Exception: ...

        iid = self.treeview.identify_row(event.y)

        self.menu.clear()
        self.build(iid)
        self.apply_extension(iid or "")
        self.menu.popup(event.x_root, event.y_root)

    def build(self, iid: str):
        raise NotImplementedError

    def apply_extension(self, iid: str):
        """插件兼容: 追加通过 treeview_*_menu.add_label 注册的菜单项"""
        ...


def _extension_of(name: str, value_name: str, iid: str, menu):
    interface = core.window.interface.mods_manage
    setattr(interface, value_name, iid)
    extension = getattr(interface, name, None)
    if extension is not None:
        extension.apply(menu, iid, separator=True)


class ClassificationContextMenu (_ContextMenu):
    """分类列表右键菜单: 添加分类 / 管理分类"""

    def build(self, iid):
        preset = iid if iid and iid != UNCLASSIFIED else None
        self.menu.add_command(label='添加分类', command=add_classification)
        self.menu.add_command(label='管理分类', command=lambda: manage_classification(preset))
        unload_mods.add_to_menu(self.menu, iid or None)

    def apply_extension(self, iid):
        _extension_of("treeview_classification_menu", "value_classification_item", iid, self.menu)


class ObjectContextMenu (_ContextMenu):
    """对象列表右键菜单: 添加对象 / 管理子对象 (作用于当前选中的分类)"""

    def build(self, iid):
        classname = core.window.interface.mods_manage.sbin_get_select_classification()
        enabled = bool(classname) and classname != UNCLASSIFIED

        self.menu.add_command(label='添加对象', command=lambda: add_object(classname), enabled=enabled)
        self.menu.add_command(label='管理子对象', command=lambda: manage_objects(classname, iid or None), enabled=enabled)
        unload_mods.add_to_menu(self.menu, classname)

    def apply_extension(self, iid):
        _extension_of("treeview_objects_menu", "value_object_item", iid, self.menu)


def _start(target, *args):
    # Tk 控件必须在主线程中创建, 否则会抛出 RuntimeError: Calling Tcl from different apartment
    core.window.exec_in_main_thread(target, *args)


def add_classification(*_):
    _start(AddClassification)


def manage_classification(preset: str | None = None):
    _start(ManageClassification, preset)


def add_object(classname: str):
    if not classname or classname == UNCLASSIFIED: return
    _start(AddObject, classname)


def manage_objects(classname: str, preset: str | None = None):
    if not classname or classname == UNCLASSIFIED: return
    _start(ManageObjects, classname, preset)


classification_menu: ClassificationContextMenu | None = None
object_menu: ObjectContextMenu | None = None


def bind_context_menu(interface):
    """为分类列表与对象列表绑定右键菜单, interface 为 mods_manage 界面实例"""
    global classification_menu, object_menu
    classification_menu = ClassificationContextMenu(interface.treeview_classification)
    object_menu = ObjectContextMenu(interface.treeview_objects)
