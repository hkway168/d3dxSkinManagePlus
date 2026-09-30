# -*- coding: utf-8 -*-

# std
import os
import shutil
import subprocess
import tkinter.filedialog
import threading

# install
import win32gui
import ttkbootstrap

# project
import core
from constant import *
from window.popup_menu import PopupMenu


class selfstatus (object):
    action = threading.Lock()


class ModifyItemData (object):
    def __init__(self, SHA):
        result = selfstatus.action.acquire(timeout=0.01)
        if not result:
            core.window.messagebox.showerror(title='互斥锁请求超时', message='互斥锁正在被其他线程占用\n上一次操作未结束或锁没有被正确释放\n亦或是你想测试这个操作是不是线程安全的')
            return

        self.SHA = SHA

        self.windows = ttkbootstrap.Toplevel('修改 SHA 信息 - new construction options')
        # 先隐藏, 待计算好位置后再显示, 避免窗口先出现在默认位置再跳到鼠标附近
        self.windows.withdraw()
        self.windows.transient(core.window.mainwindow)
        # self.windows.grab_set()
        # self.windows = tkinter.Toplevel(core.window.mainwindow)

        try:
            self.windows.iconbitmap(default=core.env.file.local.iconbitmap)
            self.windows.iconbitmap(bitmap=core.env.file.local.iconbitmap)
        except Exception:
            ...

        width = 60

        self.Label_SHA = ttkbootstrap.Label(self.windows, text=f'SHA: {self.SHA}')

        self.Frame_object = ttkbootstrap.Frame(self.windows)
        self.Entry_object = ttkbootstrap.Entry(self.Frame_object, width=width)
        self.Label_object = ttkbootstrap.Label(self.Frame_object, text='作用对象：')

        self.Frame_name = ttkbootstrap.Frame(self.windows)
        self.Entry_name = ttkbootstrap.Entry(self.Frame_name, width=width)
        self.Label_name = ttkbootstrap.Label(self.Frame_name, text='模组名称：')

        self.Frame_author = ttkbootstrap.Frame(self.windows)
        self.Entry_author = ttkbootstrap.Entry(self.Frame_author, width=width)
        self.Label_author = ttkbootstrap.Label(self.Frame_author, text='模组作者：')

        self.Frame_grading = ttkbootstrap.Frame(self.windows)
        self.Combobox_grading = ttkbootstrap.Combobox(self.Frame_grading,
                                                      values=['G - 大众级', 'P - 指导级', 'R - 成人级'])
        self.Label_grading = ttkbootstrap.Label(self.Frame_grading, text='年龄分级：')

        self.Frame_explain = ttkbootstrap.Frame(self.windows)
        self.Entry_explain = ttkbootstrap.Entry(self.Frame_explain, width=width)
        self.Label_explain = ttkbootstrap.Label(self.Frame_explain, text='附加描述：')

        self.Frame_tags = ttkbootstrap.Frame(self.windows)
        self.Entry_tags = ttkbootstrap.Entry(self.Frame_tags, width=width)
        self.Label_tags = ttkbootstrap.Label(self.Frame_tags, text='类型标签：')

        self.Button_ok = ttkbootstrap.Button(self.windows, text='保存', width=10, bootstyle="info-outline", command=self.bin_ok)
        self.Button_cancel = ttkbootstrap.Button(self.windows, text='取消', width=10, bootstyle="success-outline", command=self.bin_cancel)
        self.Button_remove = ttkbootstrap.Button(self.windows, text='删除', width=10, bootstyle="warning-outline", command=self.bin_remove)
        self.Button_delete = ttkbootstrap.Button(self.windows, text='完全移除', width=10, bootstyle="danger-outline", command=self.bin_delete)

        self.Label_except = ttkbootstrap.Label(self.windows, anchor='w', text='', foreground='red')

        self.Label_SHA.pack(side='top', fill='x', padx=10, pady=10)

        self.Frame_object.pack(side='top', fill='x', padx=10, pady=(0, 10))
        self.Label_object.pack(side='left', padx=(0, 5))
        self.Entry_object.pack(side='left', fill='x', expand=1)

        self.Frame_name.pack(side='top', fill='x', padx=10, pady=(0, 10))
        self.Label_name.pack(side='left', padx=(0, 5))
        self.Entry_name.pack(side='left', fill='x', expand=1)

        self.Frame_grading.pack(side='top', fill='x', padx=10, pady=(0, 10))
        self.Label_grading.pack(side='left', padx=(0, 5))
        self.Combobox_grading.pack(side='left', fill='x', expand=1)

        self.Frame_author.pack(side='top', fill='x', padx=10, pady=(0, 10))
        self.Label_author.pack(side='left', padx=(0, 5))
        self.Entry_author.pack(side='left', fill='x', expand=1)

        self.Frame_explain.pack(side='top', fill='x', padx=10, pady=(0, 10))
        self.Label_explain.pack(side='left', padx=(0, 5))
        self.Entry_explain.pack(side='left', fill='x', expand=1)

        self.Frame_tags.pack(side='top', fill='x', padx=10, pady=(0, 10))
        self.Label_tags.pack(side='left', padx=(0, 5))
        self.Entry_tags.pack(side='left', fill='x', expand=1)

        self.Button_ok.pack(side='right', padx=10, pady=(0, 10))
        self.Button_cancel.pack(side='right', padx=(10, 0), pady=(0, 10))
        self.Button_remove.pack(side='right', padx=(10, 0), pady=(0, 10))
        self.Button_delete.pack(side='right', padx=(10, 0), pady=(0, 10))

        self.Label_except.pack(side='right', fill='x', expand=True, padx=(10, 0), pady=(0, 10))

        self.windows.protocol('WM_DELETE_WINDOW', self.bin_cancel)

        _alt_set = core.window.annotation_toplevel.register
        _alt_set(self.Label_SHA, T.ANNOTATION_SHA, 2)
        _alt_set(self.Entry_object, T.ANNOTATION_OBJECT, 2)
        _alt_set(self.Entry_name, T.ANNOTATION_NAME, 2)
        _alt_set(self.Entry_author, T.ANNOTATION_AUTHOR, 2)
        _alt_set(self.Combobox_grading, T.ANNOTATION_GRADING, 2)
        _alt_set(self.Entry_explain, T.ANNOTATION_EXPLAIN, 2)
        _alt_set(self.Entry_tags, T.ANNOTATION_TAGS, 2)
        _alt_set(self.Button_ok, T.ANNOTATION_MODIFY_ITEM_OK, 2)
        _alt_set(self.Button_cancel, T.ANNOTATION_MODIFY_ITEM_CANCEL, 2)
        _alt_set(self.Button_remove, T.ANNOTATION_MODIFY_ITEM_REMOVE, 1)
        _alt_set(self.Button_delete, T.ANNOTATION_MODIFY_ITEM_DELETE, 1)

        # 窗口隐藏时 winfo_width 无效, 使用布局请求的尺寸
        self.windows.update_idletasks()

        width = self.windows.winfo_reqwidth()
        height = self.windows.winfo_reqheight()

        sw = self.windows.winfo_screenwidth()
        sh = self.windows.winfo_screenheight()

        mx = sw - width
        my = sh - height

        _x, _y = win32gui.GetCursorInfo()[2]

        x = _x - width // 2
        y = _y - height // 2 - 20

        if x < 0: x = 0
        if y < 0: y = 0

        if x > mx: x = mx
        if y > my: y = my

        self.windows.geometry(f'+{x}+{y}')
        self.windows.resizable(False, False)
        self.windows.deiconify()


        data = core.module.mods_index.get_item(self.SHA)

        self.old_object = data['object']
        self.old_name = data['name']
        self.old_explain = data.get('explain', '').replace("\n", "\\n")
        self.old_grading = data.get('grading', '')
        self.old_author = data.get('author', '')
        self.old_tags = ' '.join(data.get('tags', []))

        self.Entry_object.insert(0, self.old_object)
        self.Entry_name.insert(0, self.old_name)
        self.Entry_explain.insert(0, self.old_explain)
        self.Entry_author.insert(0, self.old_author)
        self.Combobox_grading.insert(0, self.old_grading)
        self.Entry_tags.insert(0, self.old_tags)


    def bin_ok(self, **args):
        s_object = self.Entry_object.get()
        s_name = self.Entry_name.get()
        s_grading = self.Combobox_grading.get()
        s_explain = self.Entry_explain.get()
        s_author = self.Entry_author.get()
        s_tags = self.Entry_tags.get()

        self.new_object = s_object.strip()
        self.new_name = s_name.strip()
        self.new_grading = s_grading[0] if s_grading else ''
        self.new_explain = s_explain.strip().replace("\\n", "\n")
        self.new_tags = [x for x in s_tags.split(' ') if x]
        self.new_author = s_author.strip()

        if not self.new_object:
            self.Label_except['text'] = '未填写 作用对象'
            return

        if not self.new_name:
            self.Label_except['text'] = '未填写 模组名称'
            return

        if not self.new_grading:
            self.Label_except['text'] = '未填写 年龄分级'
            return

        if self.new_grading not in ['G', 'P', 'R']:
            self.Label_except['text'] = '年龄分级 只能是 G P R 其中之一'
            return

        newdata = {
            'object': self.new_object,
            'name': self.new_name,
            'explain': self.new_explain,
            'grading': self.new_grading,
            'author': self.new_author,
            'get': [],
            'tags': self.new_tags
        }

        if self.old_object != self.new_object:
            core.module.mods_manage.unload(self.old_object)

        core.module.mods_index.item_data_update(self.SHA, newdata)
        self.bin_cancel()


    def bin_cancel(self, *args):
        self.windows.destroy()
        core.window.annotation_toplevel.withdraw()
        selfstatus.action.release()


    def bin_delete(self, *args):
        core.module.mods_manage.unload(self.old_object)

        core.module.mods_index.item_data_del(self.SHA)

        try:
            os.remove(os.path.join(core.env.directory.resources.mods, self.SHA))

        except Exception:
            ...

        self.bin_cancel()


    def bin_remove(self, *args):
        core.module.mods_manage.unload(self.old_object)

        try:
            os.remove(os.path.join(core.env.directory.resources.mods, self.SHA))

        except Exception:
            ...

        self.bin_cancel()


def modify_item_data(SHA: str | None = None):
    if SHA is None:
        SHA = core.window.interface.mods_manage.sbin_get_select_choices()
    if SHA is None: return
    if core.module.mods_index.get_item(SHA) is None: return
    ModifyItemData(SHA)


def get_cache_path(SHA: str) -> str | None:
    """Mod 解压后的缓存目录 (已加载为 SHA, 已卸载为 disabled-SHA)"""
    for name in (SHA, f'{K.DISABLED}-{SHA}'):
        path = os.path.abspath(os.path.join(core.userenv.directory.work_mods, name))
        if os.path.isdir(path): return path
    return None


def get_source_path(SHA: str) -> str | None:
    """Mod 原始压缩文件"""
    path = os.path.abspath(os.path.join(core.env.directory.resources.mods, SHA))
    return path if os.path.isfile(path) else None


def open_in_explorer(path: str | None):
    """在资源管理器中定位并选中目标"""
    if not path or not os.path.exists(path):
        core.window.messagebox.showerror(title='路径不存在', message=f'目标不存在\n{path or ""}')
        return
    subprocess.Popen(f'explorer /select,"{os.path.normpath(path)}"')


def delete_cache(SHA: str):
    """删除 Mod 在 work\\Mods 中的解压缓存 (若正在使用则先卸载)"""
    if get_cache_path(SHA) is None:
        core.window.messagebox.showerror(title='缓存不存在', message='该 Mod 没有解压缓存')
        return

    loaded = core.module.mods_manage.is_loaded_sha(SHA)
    message = '确定删除该 Mod 的缓存文件?'
    if loaded: message += '\n该 Mod 正在使用, 删除前将先卸载'
    if not core.window.messagebox.askyesno(title='删除缓存文件', message=message): return

    try:
        if loaded:
            object_ = core.module.mods_index.get_item(SHA)['object']
            core.module.mods_manage.unload(object_, _notify=False)

        for name in (SHA, f'{K.DISABLED}-{SHA}'):
            path = os.path.join(core.userenv.directory.work_mods, name)
            if os.path.isdir(path): shutil.rmtree(path)

    except Exception as e:
        core.window.messagebox.showerror(title='删除失败', message=f'删除缓存文件失败\n{e}')

    finally:
        core.construct.event.set_event(E.MOD_UNLOADED)


class ChoicesContextMenu (object):
    """Mod 选择列表右键菜单: 修改 Mod 信息 (需右键选中具体 Mod)"""

    def __init__(self, treeview):
        self.treeview = treeview
        self.menu = PopupMenu(treeview)
        treeview.bind('<ButtonRelease-3>', self.bin_release, add='+')

    def bin_release(self, event):
        self.menu.close()

        try: core.window.annotation_toplevel.withdraw()
        except Exception: ...

        # 仅在右键具体 Mod 时弹出菜单, 空白处 / "卸载该对象" 不显示
        iid = self.treeview.identify_row(event.y)
        if not iid or core.module.mods_index.get_item(iid) is None: return

        # 右键时同步选中该 Mod, 便于确认操作对象
        self.treeview.selection_set(iid)
        self.treeview.focus(iid)

        cache_path = get_cache_path(iid)
        source_path = get_source_path(iid)

        self.menu.clear()
        self.menu.add_command(label='修改 Mod 信息', command=lambda: modify_item_data(iid))
        self.menu.add_command(label='查看缓存文件', command=lambda: open_in_explorer(cache_path), enabled=cache_path is not None)
        self.menu.add_command(label='删除缓存文件', command=lambda: delete_cache(iid), enabled=cache_path is not None)
        self.menu.add_command(label='查看原始文件', command=lambda: open_in_explorer(source_path), enabled=source_path is not None)
        self.menu.popup(event.x_root, event.y_root)


choices_menu: ChoicesContextMenu | None = None


def bind_context_menu(treeview):
    global choices_menu
    choices_menu = ChoicesContextMenu(treeview)
