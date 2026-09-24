# -*- coding: utf-8 -*-

import tkinter.filedialog

import ttkbootstrap

import core
import module
import window

from constant import L


NOT_COPY = "(不复制)"


class CreateUserToplevel (object):
    """创建用户二级页面"""
    def __init__(self):
        self.windows = None


    def open(self, *args):
        if self.windows is not None:
            try:
                self.windows.deiconify()
                self.windows.lift()
                self.windows.focus_force()
                return

            except Exception:
                self.windows = None

        core.log.info("打开创建用户页面", L.WINDOW_LOGIN)
        self.build()


    def build(self):
        self.value_name = ttkbootstrap.StringVar()
        self.value_picture = ttkbootstrap.StringVar()
        self.value_game_path = ttkbootstrap.StringVar()
        self.value_classification = ttkbootstrap.StringVar(value=NOT_COPY)
        self.value_auto_login = ttkbootstrap.BooleanVar(value=True)

        self.windows = ttkbootstrap.Toplevel("创建用户")
        self.windows.transient(core.window.mainwindow)

        try:
            self.windows.iconbitmap(default=core.env.file.local.iconbitmap)
            self.windows.iconbitmap(bitmap=core.env.file.local.iconbitmap)

        except Exception:
            ...

        frame_form = ttkbootstrap.Frame(self.windows)
        frame_form.pack(side="top", fill="x", padx=15, pady=(15, 0))
        frame_form.columnconfigure(1, weight=1)

        ttkbootstrap.Label(frame_form, text="用户名").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_name = ttkbootstrap.Entry(frame_form, width=45, textvariable=self.value_name)
        self.entry_name.grid(row=0, column=1, columnspan=2, sticky="ew", padx=(10, 0), pady=6)

        ttkbootstrap.Label(frame_form, text="头像").grid(row=1, column=0, sticky="w", pady=6)
        self.entry_picture = ttkbootstrap.Entry(frame_form, textvariable=self.value_picture)
        self.entry_picture.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=6)
        self.button_picture = ttkbootstrap.Button(frame_form, text="浏览", width=6, cursor="hand2",
                                                  bootstyle="secondary-outline", command=self.bin_choice_picture)
        self.button_picture.grid(row=1, column=2, padx=(6, 0), pady=6)

        ttkbootstrap.Label(frame_form, text="游戏程序").grid(row=2, column=0, sticky="w", pady=6)
        self.entry_game_path = ttkbootstrap.Entry(frame_form, textvariable=self.value_game_path)
        self.entry_game_path.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=6)
        self.button_game_path = ttkbootstrap.Button(frame_form, text="浏览", width=6, cursor="hand2",
                                                    bootstyle="secondary-outline", command=self.bin_choice_game_path)
        self.button_game_path.grid(row=2, column=2, padx=(6, 0), pady=6)

        ttkbootstrap.Label(frame_form, text="分类配置").grid(row=3, column=0, sticky="w", pady=6)
        self.combobox_classification = ttkbootstrap.Combobox(
            frame_form, state="readonly", textvariable=self.value_classification,
            values=[NOT_COPY, *module.user_manage.get_user_list()])
        self.combobox_classification.grid(row=3, column=1, columnspan=2, sticky="ew", padx=(10, 0), pady=6)

        frame_description = ttkbootstrap.Frame(self.windows)
        frame_description.pack(side="top", fill="both", expand=True, padx=15, pady=(6, 0))

        ttkbootstrap.Label(frame_description, text="描述").pack(side="top", anchor="w")
        self.text_description = ttkbootstrap.Text(frame_description, height=5)
        self.text_description.pack(side="top", fill="both", expand=True, pady=(6, 0))

        frame_option = ttkbootstrap.Frame(self.windows)
        frame_option.pack(side="top", fill="x", padx=15, pady=(10, 0))

        self.checkbutton_auto_login = ttkbootstrap.Checkbutton(
            frame_option, text="创建后立即登录", variable=self.value_auto_login, cursor="hand2")
        self.checkbutton_auto_login.pack(side="left")

        frame_action = ttkbootstrap.Frame(self.windows)
        frame_action.pack(side="top", fill="x", padx=15, pady=15)

        self.button_ok = ttkbootstrap.Button(frame_action, text="创建", width=10, cursor="hand2",
                                             bootstyle="success-outline", command=self.bin_ok)
        self.button_ok.pack(side="right")

        self.button_cancel = ttkbootstrap.Button(frame_action, text="取消", width=10, cursor="hand2",
                                                 bootstyle="warning-outline", command=self.bin_cancel)
        self.button_cancel.pack(side="right", padx=(0, 5))

        self.label_errormsg = ttkbootstrap.Label(frame_action, text="", bootstyle="danger")
        self.label_errormsg.pack(side="left")

        self.windows.protocol("WM_DELETE_WINDOW", self.bin_cancel)
        self.windows.bind("<Escape>", self.bin_cancel)
        self.entry_name.focus_set()

        self.correction()


    def correction(self):
        """使窗口相对主窗口居中"""
        self.windows.update_idletasks()

        width = self.windows.winfo_width()
        height = self.windows.winfo_height()

        try:
            main = core.window.mainwindow
            x = main.winfo_rootx() + (main.winfo_width() - width) // 2
            y = main.winfo_rooty() + (main.winfo_height() - height) // 2 - 40

        except Exception:
            x = (self.windows.winfo_screenwidth() - width) // 2
            y = (self.windows.winfo_screenheight() - height) // 2

        if x < 0: x = 0
        if y < 0: y = 0

        self.windows.geometry(f"+{x}+{y}")
        self.windows.minsize(width, height)


    def bin_choice_picture(self, *args):
        path = tkinter.filedialog.askopenfilename(
            parent = self.windows,
            title = "选择头像图片",
            filetypes = [("图片文件", "*.png *.jpg *.jpeg *.bmp *.webp"), ("All Files", "*")])

        if not path: return None
        self.value_picture.set(path.replace("/", "\\"))


    def bin_choice_game_path(self, *args):
        path = tkinter.filedialog.askopenfilename(
            parent = self.windows,
            title = "选择游戏启动程序",
            filetypes = [("应用程序", "*.exe"), ("All Files", "*")])

        if not path: return None
        self.value_game_path.set(path.replace("/", "\\"))


    def bin_ok(self, *args):
        name = self.value_name.get()

        error = module.user_manage.verify_user_name(name)
        if error:
            self.label_errormsg.config(text=error.replace("\n", " "))
            return None

        classification_from = self.value_classification.get()
        if classification_from == NOT_COPY:
            classification_from = ""

        try:
            module.user_manage.create_user(
                user_name = name,
                description = self.text_description.get(0.0, "end").strip(),
                game_path = self.value_game_path.get(),
                picture_path = self.value_picture.get(),
                classification_from = classification_from
            )

        except Exception as e:
            self.label_errormsg.config(text=f"{e}".replace("\n", " "))
            return None

        auto_login = self.value_auto_login.get()
        self.close()

        window.login.refresh()
        window.login.select_user(name)

        if auto_login:
            window.login.bin_login()

        else:
            window.messagebox.showinfo(title="创建成功", message=f"用户 \"{name}\" 已创建")


    def bin_cancel(self, *args):
        self.close()


    def close(self):
        if self.windows is None: return

        try:
            self.windows.destroy()

        except Exception:
            ...

        self.windows = None
