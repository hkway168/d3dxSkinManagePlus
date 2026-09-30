# -*- coding: utf-8 -*-
"""缓存清理工具 (移植自原版 tools.cache_cleanup)

扫描 work\\Mods 中已卸载 Mod 留下的解压缓存 (disabled-SHA 文件夹), 按三档统计并清理:
- 无效缓存:   SHA 已不在 Mod 数据中 (例如 Mod 已被删除)
- 不常用缓存: SHA 在 Mod 数据中, 但本地没有原始文件
- 常用缓存:   本地有原始文件, 清理后下次加载需要重新解压

正在使用的 Mod (未加禁用标识的文件夹) 不会被扫描, 也不会被清理。
"""

# std
import os
import shutil
import threading

# site
import ttkbootstrap

# local
import core
from constant import *
from window import dialogs


class containe ():
    action = threading.Lock()
    operation = threading.Lock()


INVALID = "invalid"
RARELY = "rarely"
OFTEN = "often"

LEVELS = (
    (INVALID, "无效缓存", "Mod 数据中已不存在的 SHA, 可放心清理", "success-outline"),
    (RARELY, "不常用缓存", "本地没有原始文件的 Mod", "warning-outline"),
    (OFTEN, "常用缓存", "本地有原始文件, 清理后再次加载需要重新解压", "danger-outline"),
)


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


class CountItemFrame (ttkbootstrap.Frame):
    def __init__(self, master, description: str):
        super().__init__(master)

        self.label_description = ttkbootstrap.Label(self, text=description, anchor="w")
        self.label_count = ttkbootstrap.Label(self, text="项目数量: -", anchor="w")
        self.label_size = ttkbootstrap.Label(self, text="占用空间: -", anchor="w")

        self.label_description.pack(side="top", fill="x", padx=10, pady=(5, 0))
        self.label_count.pack(side="top", fill="x", padx=10)
        self.label_size.pack(side="top", fill="x", padx=10, pady=(0, 5))


    def set_value(self, count: int | None = None, size: int | None = None):
        if count is None:
            self.label_count.config(text="项目数量: -")
            self.label_size.config(text="占用空间: -")
            return

        self.label_count.config(text=f"项目数量: {count} 个")
        self.label_size.config(text=f"占用空间: {size / 1024 / 1024:.2f} MiB")


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

        for key, title, description, style in LEVELS:
            frame = ttkbootstrap.LabelFrame(self.window, text=title)
            frame.pack(side="top", fill="x", padx=10, pady=(10, 0))

            button = ttkbootstrap.Button(frame, text="清理", width=10, bootstyle=style, cursor="hand2",
                                         command=lambda k=key: self.bin_clean(k))
            button.pack(side="right", padx=10)

            item = CountItemFrame(frame, description)
            item.pack(side="left", fill="x", expand=True)

            self.items[key] = item
            self.buttons[key] = button

        self.frame_option = ttkbootstrap.Frame(self.window)
        self.frame_option.pack(side="top", fill="x", padx=10, pady=10)

        self.label_status = ttkbootstrap.Label(self.frame_option, text="", anchor="w")
        self.label_status.pack(side="left", fill="x", expand=True)

        self.button_scan = ttkbootstrap.Button(self.frame_option, text="重新扫描", width=12, bootstyle="info-outline",
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
        status = ""

        try:
            root = core.userenv.directory.work_mods
            all_sha = set(core.module.mods_index.get_all_sha_list())

            for dirname in os.listdir(root):
                path = os.path.join(root, dirname)
                if not os.path.isdir(path): continue

                SHA = parse_disabled_sha(dirname)
                if not SHA: continue

                data[classify(SHA, all_sha)].append((path, get_folder_size(path)))

            status = "扫描完成"

        except Exception as e:
            core.log.error(f"缓存扫描失败 {e.__class__} {e}", L.WINDOW)
            status = f"扫描失败: {e}"

        finally:
            self.data = data
            self.scanned = True
            containe.operation.release()
            self._ui(self._refresh_view, status)


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
            root = os.path.abspath(core.userenv.directory.work_mods)
            for path, _ in list(self.data[key]):
                # 仅删除 work\Mods 下带禁用标识的文件夹
                if os.path.dirname(os.path.abspath(path)) != root: continue
                if parse_disabled_sha(os.path.basename(path)) is None: continue

                try:
                    shutil.rmtree(path)
                    done += 1

                except Exception as e:
                    failed.append(os.path.basename(path))
                    core.log.error(f"删除缓存失败 {path} {e.__class__} {e}", L.WINDOW)

            self.data[key] = [x for x in self.data[key] if os.path.isdir(x[0])]

        finally:
            containe.operation.release()

        status = f"已清理{title} {done} 个" + (f", {len(failed)} 个失败 (可能被占用)" if failed else "")
        core.log.info(status, L.WINDOW)
        self._ui(self._refresh_view, status)

        # 刷新 Mod 列表中的缓存状态着色
        try: core.construct.event.set_event(E.MODS_MANAGE_CACHE_REFRESHED)
        except Exception: ...


    def bin_close(self, *_):
        if containe.operation.locked():
            core.window.messagebox.showwarning(title="请稍候", message="正在执行操作, 请等待完成后再关闭", parent=self.window)
            return

        self.window.destroy()
        containe.action.release()


__all__ = ["CacheCleanup"]
