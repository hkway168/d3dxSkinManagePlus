# -*- coding: utf-8 -*-


import webbrowser
import ttkbootstrap

import core



class Status (object):
    def __init__(self, master):
        self.master = master

        self.sizegrip = ttkbootstrap.Sizegrip(self.master)
        self.label_username = ttkbootstrap.Label(self.master, text="* /")
        self.label_mark = ttkbootstrap.Label(self.master, text="[S]")
        self.label_status = ttkbootstrap.Label(self.master, text="-")
        self.progressbar_step = ttkbootstrap.Progressbar(self.master)

        self.sizegrip.pack(side="right", fill="y")

        self.label_help = ttkbootstrap.Label(self.master, text="[ 帮助 ]", cursor="hand2")
        self.label_help.pack(side="right", padx=10, pady=5 )

        self.label_logout = ttkbootstrap.Label(self.master, text="[ 退出用户 ]", cursor="hand2")
        self.label_logout.pack(side="right", padx=10, pady=5 )

        self.label_username.pack(side="left", padx=5, pady=5)
        self.label_mark.pack(side="left", padx=5, pady=5)
        self.label_status.pack(side="left", padx=5, pady=5)
        self.progressbar_step.pack(side="left", padx=5, pady=5)

        self.label_help.bind("<Button-1>", self.bin_open_help)
        self.label_logout.bind("<Button-1>", self.bin_logout)

        self.set_logout_visible(False)


    def set_logout_visible(self, visible: bool) -> None:
        "控制退出用户入口的显示"
        if visible:
            self.label_logout.pack(side="right", padx=10, pady=5, before=self.label_help)

        else:
            self.label_logout.pack_forget()


    def bin_open_help(self, *args):
        webbrowser.open(core.env.Link.help)


    def bin_logout(self, *args):
        answer = core.window.messagebox.askyesno(
            title = "退出用户",
            message = "是否退出当前用户并返回登录界面\n未完成的下载任务将被中断")

        if not answer: return None

        try:
            core.logout()

        except Exception as e:
            core.window.messagebox.showerror(title="操作异常", message=f"{e}")


    def set_userName(self, userName):
        self.label_username["text"] = f"* {userName}"


    def set_mark(self, mark):
        self.label_mark["text"] = f"[{mark}]"


    def set_status(self, status, LEVEL: int = 0):
        if not isinstance(LEVEL, int): LEVEL = 0
        color = ["", "red", "orange"][LEVEL]
        self.label_status["text"] = status
        self.label_status["foreground"] = color
