# -*- coding: utf-8 -*-

import tkinter
import ttkbootstrap

from constant import *


class About (object):
    def install(self, master):
        self.master = master

        self.frame = ttkbootstrap.Frame(self.master)
        self.frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        self.scrollbar = ttkbootstrap.Scrollbar(self.frame, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        self.text_help = tkinter.Text(self.frame, wrap="word", relief="flat", borderwidth=0, padx=10, pady=10, yscrollcommand=self.scrollbar.set)
        self.text_help.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.text_help.yview)

        self.text_help.insert("end", T.TEXT_HELP)
        self.text_help.config(state="disabled")


    def __init__(self, master):
        self.master = master
        try: self.install(master)
        except Exception: ...
