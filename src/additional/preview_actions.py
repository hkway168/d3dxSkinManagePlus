# -*- coding: utf-8 -*-

import tkinter
import tkinter.filedialog

import core

from .add_preview import apply_preview, apply_preview_from_file, get_clipboard_image, has_preview, IMAGE_SUFFIXES


class FullScreenPreview (object):
    """全屏显示预览图, 单击或按 Esc 关闭"""
    def __init__(self, tkimg):
        self.tkimg = tkimg

        self.windows = tkinter.Toplevel(core.window.mainwindow)
        self.windows.configure(background='black', cursor='hand2')
        self.windows.attributes('-fullscreen', True)
        self.windows.attributes('-topmost', True)

        self.label_image = tkinter.Label(self.windows, image=self.tkimg, background='black', borderwidth=0)
        self.label_image.pack(side='top', fill='both', expand=True)

        for widget in (self.windows, self.label_image):
            widget.bind('<Button-1>', self.close)
            widget.bind('<Button-3>', self.close)

        self.windows.bind('<Escape>', self.close)
        self.windows.focus_force()


    def close(self, *args):
        self.windows.destroy()


def show_full_screen_preview(SHA: str) -> bool:
    """全屏显示 Mod 的预览图, 返回是否成功显示"""
    width = core.window.mainwindow.winfo_screenwidth()
    height = core.window.mainwindow.winfo_screenheight()

    try:
        tkimg = core.module.image.get_preview_image(SHA, width, height)
    except Exception as e:
        core.window.messagebox.showerror(title='预览失败', message=f'无法读取预览图\n{e}')
        return True

    if tkimg is None: return False

    FullScreenPreview(tkimg)
    return True


def get_current_sha() -> str | None:
    """获取预览区域当前对应的 Mod SHA, 未选中时提示并返回 None"""
    SHA = str(core.window.interface.mods_manage.label_SHA['text'])

    if not SHA or SHA == 'SHA' or core.module.mods_index.get_item(SHA) is None:
        core.window.messagebox.showinfo(title='未选中 Mod', message='请先在选择列表中选中一个 Mod')
        return None

    return SHA


def bin_preview_click(*args):
    """左键预览区域: 有预览图时全屏预览, 暂无预览图时引导用户设置"""
    SHA = get_current_sha()
    if SHA is None: return
    if has_preview(SHA) and show_full_screen_preview(SHA): return

    clipboard = get_clipboard_image()

    if clipboard is not None:
        answer = core.window.messagebox.askyesnocancel(
            title='暂无预览图',
            message='该 Mod 暂无预览图\n检测到剪贴板中有图片, 是否将其设为预览图?\n\n是：使用剪贴板中的图片\n否：从文件中选择图片')

        if answer is None: return

        if answer:
            content, suffix = clipboard
            apply_preview(SHA, content, suffix)
            return

        select_preview_file(SHA)
        return

    answer = core.window.messagebox.askyesno(
        title='暂无预览图',
        message='该 Mod 暂无预览图\n是否选择一张图片作为预览图?\n\n也可以直接将图片拖入窗口')

    if not answer: return

    select_preview_file(SHA)


def select_preview_file(SHA: str):
    patterns = ' '.join(f'*{x}' for x in IMAGE_SUFFIXES)
    filepath = tkinter.filedialog.askopenfilename(
        title='选择预览图',
        filetypes=[('图片', patterns), ('所有文件', '*')])

    if not filepath: return

    apply_preview_from_file(SHA, filepath)


def bin_preview_right_click(*args):
    """右键预览区域: 将剪贴板中的图片设为预览图"""
    SHA = get_current_sha()
    if SHA is None: return

    clipboard = get_clipboard_image()
    if clipboard is None:
        core.window.messagebox.showinfo(
            title='剪贴板中没有图片',
            message='请先复制一张图片 (截图或图片文件)\n再右键预览区域将其设为预览图')
        return

    content, suffix = clipboard
    apply_preview(SHA, content, suffix)
