# -*- coding: utf-8 -*-

# std
import io
import os

# install
import PIL.Image
import PIL.ImageGrab

# project
import core


# 预览图最终保存的格式 (读取预览图时只识别这两种)
PREVIEW_SUFFIXES = ('.png', '.jpg')

# 允许作为预览图导入的图片格式 (非 png/jpg 会被转换为 png)
IMAGE_SUFFIXES = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')


def _image_to_png(image: PIL.Image.Image) -> bytes:
    if image.mode not in ('RGB', 'RGBA', 'L', 'LA', 'P'):
        image = image.convert('RGBA')

    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


def normalize_image(content: bytes, suffix: str) -> tuple[bytes, str]:
    """统一图片格式, 返回 (图片内容, 小写后缀名 .png / .jpg)"""
    suffix = suffix.lower()
    if suffix == '.jpeg': suffix = '.jpg'
    if suffix in PREVIEW_SUFFIXES: return content, suffix

    with PIL.Image.open(io.BytesIO(content)) as image:
        return _image_to_png(image), '.png'


def has_preview(SHA: str) -> bool:
    """该 Mod 是否已有预览图 (包括 Mod 文件夹内自带的预览图)"""
    directory = core.env.directory.resources.preview

    for suffix in PREVIEW_SUFFIXES:
        if os.path.isfile(os.path.join(directory, f'{SHA}{suffix}')): return True
        if os.path.isfile(os.path.join(core.userenv.directory.work_mods, SHA, f'preview{suffix}')): return True

    return False


def save_preview(SHA: str, content: bytes, suffix: str) -> None:
    """保存预览图, 并删除其他格式的旧预览图, 避免旧图片被优先读取"""
    content, suffix = normalize_image(content, suffix)
    directory = core.env.directory.resources.preview
    os.makedirs(directory, exist_ok=True)

    for old_suffix in PREVIEW_SUFFIXES:
        if old_suffix == suffix: continue
        old_path = os.path.join(directory, f'{SHA}{old_suffix}')
        if os.path.isfile(old_path): os.remove(old_path)

    with open(os.path.join(directory, f'{SHA}{suffix}'), 'wb') as fileobject:
        fileobject.write(content)


def apply_preview(SHA: str, content: bytes, suffix: str) -> bool:
    """将图片设为 Mod 的预览图, 已有预览图时提示是否覆盖

    返回是否设置成功
    """
    if has_preview(SHA):
        answer = core.window.messagebox.askyesno(title='覆盖预览图', message='该 Mod 已有预览图\n是否覆盖?')
        if not answer: return False

    try:
        save_preview(SHA, content, suffix)

    except Exception as e:
        core.window.messagebox.showerror(title='操作失败', message=f'预览图设置失败\n{e}')
        return False

    core.window.mainwindow.after(0, core.window.interface.mods_manage.sbin_update_preview, SHA)
    return True


def apply_preview_from_file(SHA: str, filepath: str) -> bool:
    try:
        with open(filepath, 'rb') as fileobject: content = fileobject.read()

    except Exception as e:
        core.window.messagebox.showerror(title='图片读取失败', message=f'无法读取该图片\n{e}')
        return False

    return apply_preview(SHA, content, os.path.splitext(filepath)[1])


def get_clipboard_image() -> tuple[bytes, str] | None:
    """读取剪贴板中的图片

    支持截图等位图数据, 以及在资源管理器中复制的图片文件
    返回 (图片内容, 后缀名), 剪贴板中没有图片时返回 None
    """
    try:
        data = PIL.ImageGrab.grabclipboard()
    except Exception:
        return None

    if isinstance(data, list):
        for path in data:
            suffix = os.path.splitext(path)[1].lower()
            if not os.path.isfile(path) or suffix not in IMAGE_SUFFIXES: continue

            try:
                with open(path, 'rb') as fileobject:
                    return normalize_image(fileobject.read(), suffix)
            except Exception:
                continue

        return None

    if isinstance(data, PIL.Image.Image):
        return _image_to_png(data), '.png'

    return None


def add_preview(filepath: str):
    """拖入图片: 直接设为当前 Mod 的预览图"""
    SHA = core.window.interface.mods_manage.sbin_get_select_choices()

    if SHA is None:
        object_ = core.window.interface.mods_manage.sbin_get_select_objects()
        SHA = core.module.mods_manage.get_load_object_sha(object_)

    if SHA is None:
        core.window.messagebox.showerror(title='未选中错误', message='需要先选中一个 Mod\n才能添加预览图')
        return

    # 延后到主循环执行, 避免在拖放回调中直接弹出对话框
    core.window.mainwindow.after(0, apply_preview_from_file, SHA, filepath)
