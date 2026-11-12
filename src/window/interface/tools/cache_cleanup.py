# -*- coding: utf-8 -*-
"""缓存清理工具 (移植自原版 tools.cache_cleanup, 并合并原版插件 cache_clearup / temp_cache_clearup 的功能)

临时文件: resources\\cache 中残留的临时压缩包 / 图片 (添加 Mod、应用修改等操作异常中断时留下)

扫描 work\\Mods 中已卸载 Mod 留下的解压缓存 (disabled-SHA 文件夹), 按三档统计并清理:
- 无效缓存:   SHA 已不在 Mod 数据中 (例如 Mod 已被删除)
- 不常用缓存: SHA 在 Mod 数据中, 但本地没有原始文件
- 常用缓存:   本地有原始文件, 清理后下次加载需要重新解压

正在使用的 Mod (未加禁用标识的文件夹) 不会被扫描, 也不会被清理。
删除失败的项目会列出原因, 并可在资源管理器中定位后手动删除。
"""

# std
import os
import sys
import stat
import time
import shutil
import threading
import subprocess

# site
import ttkbootstrap

# local
import core
from constant import *
from window import dialogs
from window import dpi


class containe ():
    action = threading.Lock()
    operation = threading.Lock()


TEMP = "temp"
INVALID = "invalid"
RARELY = "rarely"
OFTEN = "often"

LEVELS = (
    (TEMP, "临时文件", "操作中断时残留的临时压缩包和图片, 可放心清理", "success-outline"),
    (INVALID, "无效缓存", "Mod 数据中已不存在的 SHA, 可放心清理", "success-outline"),
    (RARELY, "不常用缓存", "本地没有原始文件的 Mod", "warning-outline"),
    (OFTEN, "常用缓存", "本地有原始文件, 清理后再次加载需要重新解压", "danger-outline"),
)

# 临时文件: 只处理这些后缀, 且跳过最近修改过的文件 (可能正在被添加 Mod 等操作使用)
TEMP_SUFFIXES = {".7z", ".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}
TEMP_MIN_AGE = 10 * 60


def get_folder_size(folder_path: str) -> int:
    total = 0
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            try: total += os.path.getsize(os.path.join(dirpath, filename))
            except OSError: ...
    return total


def parse_disabled_sha(dirname: str) -> str | None:
    """从 disabled-SHA / DISABLEDSHA 文件夹名中取出 SHA, 不是缓存文件夹返回 None"""
    upper = dirname.upper()
    prefix = K.DISABLED_UPPER

    if upper.startswith(f"{prefix}-"): return dirname[len(prefix) + 1:]
    if upper.startswith(prefix): return dirname[len(prefix):]
    return None


def classify(SHA: str, all_sha: set) -> str:
    if core.module.mods_manage.is_local_sha(SHA): return OFTEN
    if SHA in all_sha: return RARELY

    # 兼容原版: 文件夹名可能带有后缀, 只取前 40 位 SHA
    if len(SHA) > 40: return classify(SHA[:40], all_sha) if SHA[:40] in all_sha else INVALID
    return INVALID


def muted_foreground(ratio: float = 0.65) -> str:
    """按当前主题生成比正文略淡的文字颜色 (前景色向背景色混合)"""
    try:
        colors = ttkbootstrap.Style().colors
        fg, bg = colors.fg.lstrip("#"), colors.bg.lstrip("#")
        mix = [round(int(fg[i:i + 2], 16) * ratio + int(bg[i:i + 2], 16) * (1 - ratio)) for i in (0, 2, 4)]
        return "#%02x%02x%02x" % tuple(mix)
    except Exception:
        return "gray"


def is_safe_target(key: str, path: str) -> bool:
    """删除前再次确认目标在允许的范围内"""
    path = os.path.abspath(path)
    parent, name = os.path.dirname(path), os.path.basename(path)

    if key == TEMP:
        return (parent == os.path.abspath(core.env.directory.resources.cache)
                and os.path.splitext(name)[1].lower() in TEMP_SUFFIXES
                and not os.path.isdir(path))

    return parent == os.path.abspath(core.userenv.directory.work_mods) and parse_disabled_sha(name) is not None


def _on_remove_error(func, path, _):
    """去掉只读属性后重试一次; 目标已不存在视为成功"""
    if not os.path.lexists(path): return
    os.chmod(path, stat.S_IWRITE)
    func(path)


def remove_path(path: str):
    """删除文件或文件夹, 目标已不存在时直接返回"""
    if not os.path.lexists(path): return

    if os.path.isdir(path) and not os.path.islink(path):
        if sys.version_info >= (3, 12): shutil.rmtree(path, onexc=_on_remove_error)
        else: shutil.rmtree(path, onerror=_on_remove_error)
        return

    try:
        os.remove(path)
    except PermissionError:
        os.chmod(path, stat.S_IWRITE)
        os.remove(path)


def describe_error(e: Exception) -> str:
    if isinstance(e, PermissionError): return "权限不足或被占用"
    return f"{e.__class__.__name__}: {e}"


def open_in_explorer(path: str):
    """在资源管理器中定位目标, 目标不存在时打开其所在目录"""
    path = os.path.normpath(path)
    if os.path.exists(path):
        subprocess.Popen(f'explorer /select,"{path}"')
        return

    parent = os.path.dirname(path)
    if os.path.isdir(parent): os.startfile(parent)


class CountItemFrame (ttkbootstrap.Frame):
    def __init__(self, master, description: str):
        super().__init__(master)

        self.label_description = ttkbootstrap.Label(self, text=description, anchor="w", foreground=muted_foreground())
        self.label_description.pack(side="top", fill="x", padx=10, pady=(10, 0))

        frame_row = ttkbootstrap.Frame(self)
        frame_row.pack(side="top", fill="x")

        frame_prefix = ttkbootstrap.Frame(frame_row)
        frame_suffix = ttkbootstrap.Frame(frame_row)
        frame_counts = ttkbootstrap.Frame(frame_row)

        frame_prefix.pack(side="left", fill="y", padx=10, pady=(5, 10))
        frame_suffix.pack(side="right", fill="y", padx=10, pady=(5, 10))
        frame_counts.pack(side="top", fill="x", pady=(5, 10))

        ttkbootstrap.Label(frame_prefix, text="项目数量:").pack(side="top", fill="x")
        ttkbootstrap.Label(frame_prefix, text="占用空间:").pack(side="top", fill="x")

        ttkbootstrap.Label(frame_suffix, text="Items").pack(side="top", fill="x")
        ttkbootstrap.Label(frame_suffix, text="MiBytes").pack(side="top", fill="x")

        self.label_count = ttkbootstrap.Label(frame_counts, text="-", anchor="e", width=32)
        self.label_size = ttkbootstrap.Label(frame_counts, text="-", anchor="e", width=32)
        self.label_count.pack(side="top", fill="x")
        self.label_size.pack(side="top", fill="x")


    def set_value(self, count: int | None = None, size: int | None = None):
        if count is None:
            self.label_count.config(text="-")
            self.label_size.config(text="-")
            return

        self.label_count.config(text=f"{count}")
        self.label_size.config(text=f"{size / 1024 / 1024:.2f}")


class FailedDialog (object):
    """列出删除失败的项目, 可在资源管理器中定位后手动删除"""
    def __init__(self, parent, title: str, failed: list[tuple[str, str]]):
        self.failed = failed

        self.window = ttkbootstrap.Toplevel(f"{title}清理失败")
        self.window.withdraw()
        self.window.transient(parent)
        self.window.minsize(dpi.scale(480), dpi.scale(240))
        dialogs._set_icon(self.window)

        tips = (f"以下 {len(failed)} 个项目未能删除, 通常是文件被占用 (例如游戏正在运行) 或权限不足。\n"
                "可以关闭占用程序后重新清理, 或在资源管理器中定位后手动删除。")
        ttkbootstrap.Label(self.window, text=tips, anchor="w", justify="left").pack(side="top", fill="x", padx=10, pady=10)

        frame_option = ttkbootstrap.Frame(self.window)
        frame_option.pack(side="bottom", fill="x", padx=10, pady=(0, 10))

        frame_list = ttkbootstrap.Frame(self.window)
        frame_list.pack(side="top", fill="both", expand=True, padx=10, pady=(0, 10))

        self.treeview = ttkbootstrap.Treeview(frame_list, columns=("name", "reason"), show="headings",
                                              selectmode="browse", height=min(max(len(failed), 3), 10))
        self.treeview.heading("name", text="名称", anchor="w")
        self.treeview.heading("reason", text="原因", anchor="w")
        self.treeview.column("name", width=dpi.scale(420), anchor="w")
        self.treeview.column("reason", width=dpi.scale(220), anchor="w")

        scrollbar = ttkbootstrap.Scrollbar(frame_list, orient="vertical", command=self.treeview.yview)
        self.treeview.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.treeview.pack(side="left", fill="both", expand=True)

        for index, (path, reason) in enumerate(failed):
            self.treeview.insert("", "end", iid=str(index), values=(os.path.basename(path), reason))

        if failed: self.treeview.selection_set("0")
        self.treeview.bind("<Double-1>", self.bin_open)

        ttkbootstrap.Button(frame_option, text="关闭", width=10, bootstyle="warning-outline", cursor="hand2",
                            command=self.window.destroy).pack(side="right")
        ttkbootstrap.Button(frame_option, text="打开文件所在目录", bootstyle="info-outline", cursor="hand2",
                            command=self.bin_open).pack(side="right", padx=(0, 10))

        dialogs.center_window(self.window, parent)
        self.window.deiconify()
        self.window.focus_set()


    def bin_open(self, *_):
        selection = self.treeview.selection()
        if not selection: return
        path = self.failed[int(selection[0])][0]

        try: open_in_explorer(path)
        except Exception as e:
            core.window.messagebox.showerror(title="打开失败", message=f"{e.__class__.__name__}: {e}", parent=self.window)


class CacheCleanup (object):
    def __init__(self):
        if not containe.action.acquire(timeout=0.01):
            core.window.messagebox.showerror(title="操作已被阻止", message="请勿重复启动该工具")
            return

        self.data: dict[str, list[tuple[str, int]]] = {key: [] for key, *_ in LEVELS}
        self.scanned = False

        self.window = ttkbootstrap.Toplevel("缓存清理工具")
        self.window.withdraw()
        self.window.transient(core.window.mainwindow)
        self.window.resizable(width=False, height=False)
        self.window.protocol("WM_DELETE_WINDOW", self.bin_close)
        dialogs._set_icon(self.window)

        self.items: dict[str, CountItemFrame] = {}
        self.buttons: dict[str, ttkbootstrap.Button] = {}

        for index, (key, title, description, style) in enumerate(LEVELS):
            frame = ttkbootstrap.LabelFrame(self.window, text=title)
            frame.pack(side="top", fill="x", padx=10, pady=(10 if index == 0 else 0, 10))

            button = ttkbootstrap.Button(frame, text="清理", width=10, bootstyle=style, cursor="hand2",
                                         command=lambda k=key: self.bin_clean(k))
            button.pack(side="right", padx=10)

            item = CountItemFrame(frame, description)
            item.pack(side="left", fill="x", expand=True)

            self.items[key] = item
            self.buttons[key] = button

        self.frame_option = ttkbootstrap.Frame(self.window)
        self.frame_option.pack(side="top", fill="x", padx=10, pady=(0, 10))

        self.label_status = ttkbootstrap.Label(self.frame_option, text="", anchor="w")
        self.label_status.pack(side="left", fill="x", expand=True)

        self.button_scan = ttkbootstrap.Button(self.frame_option, text="重新扫描缓存文件", width=30, bootstyle="info-outline",
                                               cursor="hand2", command=self.bin_scan)
        self.button_scan.pack(side="right")

        dialogs.center_window(self.window)
        self.window.deiconify()

        self.bin_scan()


    # ---------------------------------------------- 界面更新 (统一回到主线程)
    def _ui(self, func, *args):
        try: core.window.mainwindow.after(0, func, *args)
        except Exception: ...


    def _refresh_view(self, status: str = ""):
        if not self._alive(): return
        for key, *_ in LEVELS:
            lst = self.data[key]
            self.items[key].set_value(len(lst) if self.scanned else None, sum(x[1] for x in lst))
            self.buttons[key].config(state="normal" if self.scanned and lst else "disabled")

        self.button_scan.config(state="normal" if not containe.operation.locked() else "disabled")
        self.label_status.config(text=status)


    def _alive(self) -> bool:
        try: return bool(self.window.winfo_exists())
        except Exception: return False


    def _busy(self) -> bool:
        if containe.operation.acquire(timeout=0.01): return False
        core.window.messagebox.showerror(title="互斥动作", message="请等待当前操作完成", parent=self.window)
        return True


    # ---------------------------------------------- 扫描
    def bin_scan(self, *_):
        if self._busy(): return
        self.scanned = False
        self._refresh_view("正在扫描...")
        core.construct.taskpool.newtask(self._task_scan)


    def _task_scan(self):
        data = {key: [] for key, *_ in LEVELS}
        errors = []

        for name, scan in (("临时文件", self._scan_temp), ("Mod 缓存", self._scan_work_mods)):
            try:
                scan(data)

            except Exception as e:
                core.log.error(f"{name}扫描失败 {e.__class__} {e}", L.WINDOW)
                errors.append(f"{name}扫描失败: {e}")

        self.data = data
        self.scanned = True
        containe.operation.release()
        self._ui(self._refresh_view, "; ".join(errors) or "扫描完成")


    @staticmethod
    def _scan_temp(data: dict):
        root = core.env.directory.resources.cache
        if not os.path.isdir(root): return
        now = time.time()

        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.splitext(name)[1].lower() not in TEMP_SUFFIXES: continue

            try:
                info = os.stat(path)
            except OSError:
                continue

            if not stat.S_ISREG(info.st_mode): continue
            if now - info.st_mtime < TEMP_MIN_AGE: continue
            data[TEMP].append((path, info.st_size))


    @staticmethod
    def _scan_work_mods(data: dict):
        root = core.userenv.directory.work_mods
        all_sha = set(core.module.mods_index.get_all_sha_list())

        for dirname in os.listdir(root):
            path = os.path.join(root, dirname)
            if not os.path.isdir(path): continue

            SHA = parse_disabled_sha(dirname)
            if not SHA: continue

            data[classify(SHA, all_sha)].append((path, get_folder_size(path)))


    # ---------------------------------------------- 清理
    def bin_clean(self, key: str):
        lst = self.data.get(key, [])
        if not lst: return

        title = next(x[1] for x in LEVELS if x[0] == key)
        size = sum(x[1] for x in lst) / 1024 / 1024
        message = f"将删除 {len(lst)} 个{title}, 共 {size:.2f} MiB\n此操作不可撤销, 是否继续?"
        if key == OFTEN: message += "\n\n清理后再次加载这些 Mod 时需要重新解压"

        if not core.window.messagebox.askyesno(title=f"清理{title}", message=message, parent=self.window): return
        if self._busy(): return

        self._refresh_view(f"正在清理{title}...")
        for button in self.buttons.values(): button.config(state="disabled")
        core.construct.taskpool.newtask(self._task_clean, (key, title))


    def _task_clean(self, key: str, title: str):
        done, failed = 0, []

        try:
            for path, _ in list(self.data[key]):
                try:
                    # 仅删除允许范围内的目标: work\Mods 下带禁用标识的文件夹 / resources\cache 下的临时文件
                    if not is_safe_target(key, path): continue

                    # 目标已不存在 (被其他程序或手动删除) 视为已清理
                    remove_path(path)
                    done += 1

                except Exception as e:
                    if not os.path.lexists(path):
                        done += 1
                        continue

                    failed.append((path, describe_error(e)))
                    core.log.error(f"删除缓存失败 {path} {e.__class__} {e}", L.WINDOW)

            self.data[key] = [x for x in self.data[key] if os.path.lexists(x[0])]

        finally:
            containe.operation.release()

        status = f"已清理{title} {done} 个" + (f", {len(failed)} 个失败" if failed else "")
        core.log.info(status, L.WINDOW)
        self._ui(self._refresh_view, status)
        if failed: self._ui(self._show_failed, title, failed)

        # 刷新 Mod 列表中的缓存状态着色
        if key != TEMP:
            try: core.construct.event.set_event(E.MODS_MANAGE_CACHE_REFRESHED)
            except Exception: ...


    def _show_failed(self, title: str, failed: list[tuple[str, str]]):
        if not self._alive(): return
        FailedDialog(self.window, title, failed)


    def bin_close(self, *_):
        if containe.operation.locked():
            core.window.messagebox.showwarning(title="请稍候", message="正在执行操作, 请等待完成后再关闭", parent=self.window)
            return

        self.window.destroy()
        containe.action.release()


__all__ = ["CacheCleanup"]
