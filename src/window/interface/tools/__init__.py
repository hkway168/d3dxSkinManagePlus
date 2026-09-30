# -*- coding: utf-8 -*-


import ttkbootstrap

import core

from constant import *
from . import ocd_crop
from . import cache_cleanup
from . import launch_script

TEXT = """
强迫症预览图裁剪工具

你是否因为在截取预览图时位置和大小参差不齐而烦恼
但是现在没有关系
这个工具可以帮助你截取位置和大小一致的图片
为你的强迫症之路舔砖 Java (加瓦)
"""

TEXT_CACHE_CLEANUP = """
缓存清理工具

卸载 Mod 时解压缓存会被保留以加快再次加载
但这些缓存不会因为 Mod 的删除而删除
可以通过此工具扫描并清理这些无用的缓存文件
释放硬盘空间
"""

TEXT_LAUNCH_SCRIPT = """
生成启动脚本

让你不再需要通过程序来启动 3DMiGoto
注意，这里只提供最基础的启动方式
如果你需要实现更复杂的逻辑
请自行富化脚本内容
"""

TEXT_TAGS_EDIT = """
可选标签编辑工具

你可以在此编辑 Mod 标签的可选内容和顺序
使用空格和换行来分隔多个标签
已出现过的标签会被追加到可选内容中
在 Mod 信息窗口点击 "+" 即可选择
"""

TAGS_EDIT_TIPS = "空格分隔标签, 换行分行; 每一行在标签选择器中显示为一行。\n末尾自动追加的是 Mod 中已出现过的标签, 保存后会一并记录为可选标签。"


class Tools (object):
    def __init__(self, master, *_):
        self.master = master
        self.install()


    def install(self):
        self.frame = ttkbootstrap.Frame(self.master)
        self.frame.pack(side="top", fill="x", padx=10, pady=10)

        self.button_ocd_crop = ttkbootstrap.Button(self.frame, text=TEXT, bootstyle="outline", command=self.bin_open_ocd_crop)
        self.button_cache_cleanup = ttkbootstrap.Button(self.frame, text=TEXT_CACHE_CLEANUP, bootstyle="outline", command=self.bin_open_cache_cleanup)
        self.button_launch_script = ttkbootstrap.Button(self.frame, text=TEXT_LAUNCH_SCRIPT, bootstyle="outline", command=self.bin_open_launch_script)
        self.button_tags_edit = ttkbootstrap.Button(self.frame, text=TEXT_TAGS_EDIT, bootstyle="outline", command=self.bin_open_tags_edit)

        # 两列网格排列, 避免低缩放比例下一行放不下
        buttons = (self.button_ocd_crop, self.button_cache_cleanup, self.button_launch_script, self.button_tags_edit)
        for index, button in enumerate(buttons):
            row, column = divmod(index, 2)
            button.grid(row=row, column=column, sticky="nsew", padx=(0 if column == 0 else 10, 0), pady=(0 if row == 0 else 10, 0))


    def initial(self):
        ...


    def bin_open_ocd_crop(self, *_):
        ocd_crop.OCDCrop()


    def bin_open_cache_cleanup(self, *_):
        cache_cleanup.CacheCleanup()


    def bin_open_launch_script(self, *_):
        launch_script.LaunchScript()


    def bin_open_tags_edit(self, *_):
        from window import dialogs

        tags_manage = core.module.tags_manage
        if not tags_manage.is_ready():
            core.window.messagebox.showerror(title="无法编辑", message="请先登录用户环境")
            return

        result = dialogs.text_edit("可选标签编辑", tags_manage.get_tags_content(), TAGS_EDIT_TIPS, width=600, height=450)
        if result is None: return

        try:
            tags_manage.update_content(result, True)
            core.window.status.set_status("可选标签已保存")

        except Exception as e:
            core.log.error(f"保存可选标签失败 {e.__class__} {e}", L.WINDOW)
            core.window.messagebox.showerror(title="保存失败", message=f"{e.__class__.__name__}: {e}")
