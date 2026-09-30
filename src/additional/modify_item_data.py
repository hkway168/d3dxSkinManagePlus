# -*- coding: utf-8 -*-

# std
import os
import time
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

from . import unload_mods


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
        self.Button_tags = ttkbootstrap.Button(self.Frame_tags, text='+', bootstyle="success-outline", command=self.set_tags)

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
        self.Button_tags.pack(side='left', padx=(5, 0))

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


    def set_tags(self, *_):
        select_tags_for_entry(self.Entry_tags, self.windows)


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


def select_tags_for_entry(entry, parent):
    """打开标签选择器, 结果写回输入框 (空格分隔)"""
    from window import dialogs

    try: optional = core.module.tags_manage.get_tags()
    except Exception: optional = []

    result = dialogs.select_tags("选择标签", optional, entry.get(), parent=parent)
    entry.delete(0, 'end')
    entry.insert(0, ' '.join(result))


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


# 应用缓存到原始文件的操作互斥锁, 防止重复执行
_apply_lock = threading.Lock()


def apply_cache_to_source(SHA: str):
    """将 work\\Mods 中的解压缓存重新打包为 7z 并替换原始文件 (SHA 随之改变)"""
    cache_path = get_cache_path(SHA)
    if cache_path is None:
        core.window.messagebox.showerror(title='缓存不存在', message='该 Mod 没有解压缓存')
        return

    if get_source_path(SHA) is None:
        core.window.messagebox.showerror(title='原始文件不存在', message='该 Mod 的原始文件不存在')
        return

    if not os.path.isfile(os.path.abspath(core.env.file.local.t7z)):
        core.window.messagebox.showerror(title='缺少 7-Zip', message=f'找不到 7-Zip\n{os.path.abspath(core.env.file.local.t7z)}')
        return

    try: empty = not os.listdir(cache_path)
    except Exception: empty = True
    if empty:
        core.window.messagebox.showerror(title='缓存为空', message='该 Mod 的缓存目录为空, 无法应用到原始文件')
        return

    message = (
        '确定将该 Mod 的缓存文件应用到原始文件?\n\n'
        '缓存目录中的内容将被重新打包为 7z 并替换原始文件\n'
        f'该 Mod 的 SHA 将会改变\n旧 SHA: {SHA}\n\n'
        '旧的原始文件将备份到 resources\\backup'
    )
    if core.module.mods_manage.is_loaded_sha(SHA):
        message += '\n\n该 Mod 正在使用, 应用前将先卸载, 完成后重新加载\n请先关闭游戏, 避免文件被占用'

    if not core.window.messagebox.askyesno(title='应用到原始文件', message=message, icon='warning'): return

    if not _apply_lock.acquire(blocking=False):
        core.window.messagebox.showerror(title='操作进行中', message='上一次应用到原始文件的操作尚未完成')
        return

    try:
        core.construct.taskpool.newtask(_apply_cache_to_source_task, (SHA, ))

    except Exception:
        _apply_lock.release()
        raise


def _apply_cache_to_source_task(SHA: str):
    try:
        _apply_cache_to_source(SHA)

    except Exception as e:
        core.log.error(f"应用缓存到原始文件失败 {SHA} {e.__class__} {e}")
        core.window.messagebox.showerror(title='应用失败', message=f'应用到原始文件失败\n{e}')

    finally:
        _apply_lock.release()


def _apply_cache_to_source(old_SHA: str):
    from . import add_mod

    item = core.module.mods_index.get_item(old_SHA)
    cache_path = get_cache_path(old_SHA)
    source_path = get_source_path(old_SHA)
    if item is None or cache_path is None or source_path is None:
        core.window.messagebox.showerror(title='应用失败', message='该 Mod 的索引、缓存或原始文件已不存在')
        return

    object_ = item[K.INDEX.OBJECT]
    work_mods = core.userenv.directory.work_mods
    temp_file = os.path.join(core.env.directory.resources.cache, f'apply-{time.time_ns():x}.7z')

    try:
        # 打包缓存目录并计算新 SHA
        if not core.external.pack_dir_7z(cache_path, temp_file) or not os.path.isfile(temp_file):
            core.window.messagebox.showerror(title='打包失败', message='7-Zip 打包缓存目录失败\n可能有文件被占用, 请关闭游戏后重试')
            return

        new_SHA = add_mod.compute_file_sha1(temp_file)

        if new_SHA == old_SHA:
            core.window.messagebox.showinfo(title='内容未变化', message='缓存打包后的内容与原始文件一致, 无需应用')
            return

        new_enabled = os.path.join(work_mods, new_SHA)
        new_disabled = os.path.join(work_mods, f'{K.DISABLED}-{new_SHA}')
        if (core.module.mods_index.get_item(new_SHA) is not None
                or os.path.exists(new_enabled) or os.path.exists(new_disabled)):
            core.window.messagebox.showerror(title='SHA 冲突', message=f'新 SHA 已存在, 已取消操作\n{new_SHA}')
            return

        was_loaded = core.module.mods_manage.is_loaded_sha(old_SHA)
        backup_path = _migrate_sha(old_SHA, new_SHA, object_, temp_file, was_loaded)

    finally:
        try:
            if os.path.isfile(temp_file): os.remove(temp_file)
        except Exception: ...

    # 若之前正在使用则重新加载 (此时缓存已存在, 仅重命名)
    if was_loaded:
        try:
            core.module.mods_manage.load(new_SHA)
        except Exception as e:
            core.log.error(f"重新加载 Mod 失败 {new_SHA} {e.__class__} {e}")
            core.window.messagebox.showwarning(title='重新加载失败', message=f'已应用到原始文件, 但重新加载失败, 请手动加载\n{e}')

    else:
        core.construct.event.set_event(E.MOD_UNLOADED)

    core.window.mainwindow.after(0, _refresh_preview_sha, old_SHA, new_SHA)

    core.window.messagebox.showinfo(
        title='应用完成',
        message=f'已应用到原始文件\n\n旧 SHA: {old_SHA}\n新 SHA: {new_SHA}\n\n旧原始文件已备份至\n{backup_path}'
    )


def _migrate_sha(old_SHA: str, new_SHA: str, object_: str, packed_file: str, was_loaded: bool) -> str:
    """将 Mod 由 old_SHA 迁移至 new_SHA, 失败时倒序回滚并抛出异常, 成功返回备份路径"""
    work_mods = core.userenv.directory.work_mods
    resources = core.env.directory.resources

    old_enabled = os.path.join(work_mods, old_SHA)
    old_disabled = os.path.join(work_mods, f'{K.DISABLED}-{old_SHA}')
    new_disabled = os.path.join(work_mods, f'{K.DISABLED}-{new_SHA}')
    old_source = os.path.join(resources.mods, old_SHA)
    new_source = os.path.join(resources.mods, new_SHA)

    backup_path = os.path.join(resources.backup, old_SHA)
    if os.path.exists(backup_path):
        backup_path = f'{backup_path}-{time.strftime("%Y%m%d%H%M%S")}'

    rollback = []

    try:
        # 1. 卸载 (缓存目录变为 disabled-旧SHA)
        if was_loaded:
            core.module.mods_manage.unload(object_, _notify=False)

        # unload 会吞掉重命名异常, 此处确保缓存处于禁用状态, 失败即说明被占用
        if not os.path.isdir(old_disabled):
            os.rename(old_enabled, old_disabled)
            rollback.append(lambda: os.rename(old_disabled, old_enabled))

        elif was_loaded:
            rollback.append(lambda: os.rename(old_disabled, old_enabled))

        # 2. 备份旧原始文件
        shutil.move(old_source, backup_path)
        rollback.append(lambda: shutil.move(backup_path, old_source))

        # 3. 新的原始文件
        shutil.move(packed_file, new_source)
        rollback.append(lambda: os.remove(new_source))

        # 4. 缓存目录改名 (需在索引刷新前完成, 避免被当作意外 SHA 清理)
        os.rename(old_disabled, new_disabled)
        rollback.append(lambda: os.rename(new_disabled, old_disabled))

        # 5. 预览图改名
        for suffix in ('.png', '.jpg'):
            old_preview = os.path.join(resources.preview, f'{old_SHA}{suffix}')
            new_preview = os.path.join(resources.preview, f'{new_SHA}{suffix}')
            if os.path.isfile(old_preview) and not os.path.exists(new_preview):
                os.rename(old_preview, new_preview)
                rollback.append(lambda o=old_preview, n=new_preview: os.rename(n, o))

        # 6. 索引换键 (保持所属 index 文件与顺序)
        if not core.module.mods_index.item_data_rekey(old_SHA, new_SHA, {K.INDEX.TYPE: K.MOD_TYPE.T7Z}):
            raise RuntimeError('索引更新失败')

    except Exception:
        for action in reversed(rollback):
            try: action()
            except Exception as e: core.log.error(f"回滚失败 {e.__class__} {e}")

        # 依据磁盘状态重建已加载表
        core.construct.event.set_event(E.MODS_INDEX_UPDATE)
        raise

    core.log.info(f"应用缓存到原始文件 {old_SHA} -> {new_SHA}, 备份 {backup_path}")
    return backup_path


def _refresh_preview_sha(old_SHA: str, new_SHA: str):
    """预览区域若正在显示旧 SHA, 切换为新 SHA"""
    try:
        interface = core.window.interface.mods_manage
        if str(interface.label_SHA['text']) == old_SHA:
            interface.sbin_update_preview(new_SHA)
    except Exception: ...


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

        iid = self.treeview.identify_row(event.y)
        is_mod = bool(iid) and core.module.mods_index.get_item(iid) is not None

        # 插件兼容: 记录右键命中的条目 (原版 value_choice_item)
        interface = core.window.interface.mods_manage
        interface.value_choice_item = iid or ""

        self.menu.clear()

        # 内置菜单仅在右键具体 Mod 时出现, 空白处 / "卸载该对象" 不显示
        if is_mod:
            # 右键时同步选中该 Mod, 便于确认操作对象
            self.treeview.selection_set(iid)
            self.treeview.focus(iid)

            cache_path = get_cache_path(iid)
            source_path = get_source_path(iid)

            self.menu.add_command(label='修改 Mod 信息', command=lambda: modify_item_data(iid))
            self.menu.add_command(label='查看缓存文件', command=lambda: open_in_explorer(cache_path), enabled=cache_path is not None)
            self.menu.add_command(label='删除缓存文件', command=lambda: delete_cache(iid), enabled=cache_path is not None)
            self.menu.add_command(label='查看原始文件', command=lambda: open_in_explorer(source_path), enabled=source_path is not None)
            self.menu.add_command(label='应用到原始文件', command=lambda: apply_cache_to_source(iid), enabled=cache_path is not None and source_path is not None)
            unload_mods.add_to_menu(self.menu, None, with_class=False)

        # 插件追加的菜单项 (treeview_choices_menu.add_label)
        extra = interface.treeview_choices_menu.apply(self.menu, iid or "", separator=is_mod)

        if is_mod or extra:
            self.menu.popup(event.x_root, event.y_root)


choices_menu: ChoicesContextMenu | None = None


def bind_context_menu(treeview):
    global choices_menu
    choices_menu = ChoicesContextMenu(treeview)
