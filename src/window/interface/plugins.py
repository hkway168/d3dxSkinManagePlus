# -*- coding: utf-8 -*-

# std
import os

# site
import ttkbootstrap

# local
import core


class Plugins(object):
    def __init__(self, master):
        self.master = master

        self.treeview_plugins = ttkbootstrap.Treeview(self.master, selectmode="browse", show="tree")
        self.treeview_plugins.column("#0", width=300, anchor="w")
        self.treeview_plugins.pack(side="left", fill="y", padx=10, pady=10)

        self.text_description = ttkbootstrap.Text(self.master)
        self.text_description.pack(side="top", fill="both", expand=True, padx=(0, 10), pady=10)

        self.treeview_plugins.bind("<<TreeviewSelect>>", self.bin_plugins_TreeviewSelect)
        self.set_text("将插件解压到 ./plugins/<插件名>/ 目录下 (需包含 main.py), 重启程序后生效。\n"
                      "启动参数 --noplugin 可禁用插件加载。")


    def set_text(self, content: str):
        self.text_description.config(state="normal")
        self.text_description.delete(1.0, "end")
        self.text_description.insert(1.0, content)
        self.text_description.config(state="disabled")


    def read_description(self, name: str) -> str:
        path = os.path.join(core.env.base.plugins, name, "description.txt")
        if not os.path.isfile(path):
            return "没有描述"

        for encoding in ["utf-8", "gb18030"]:
            try:
                with open(path, "r", encoding=encoding) as fileobject:
                    return fileobject.read()

            except UnicodeDecodeError:
                continue

            except Exception:
                break

        return "描述文件读取失败"


    def bin_plugins_TreeviewSelect(self, *_):
        tags = self.treeview_plugins.item(self.treeview_plugins.focus()).get("tags") or []
        if not tags:
            return

        name = str(tags[0])
        failed = core.module.plugins.PluginsData.failed_table.get(name)
        if failed is not None:
            self.set_text(f"加载失败: {failed}\n\n{self.read_description(name)}")
            return

        self.set_text(self.read_description(name))


    def update(self, *_):
        self.treeview_plugins.delete(*self.treeview_plugins.get_children())

        for name, util in core.module.plugins.PluginsData.alias_table.items():
            version = getattr(util, "__version__", "版本未知")
            self.treeview_plugins.insert("", "end", iid=f"ok:{name}", text=f"{name}  {version}", tags=(name, ))

        for name in core.module.plugins.PluginsData.failed_table:
            self.treeview_plugins.insert("", "end", iid=f"err:{name}", text=f"{name}  (加载失败)", tags=(name, ))
