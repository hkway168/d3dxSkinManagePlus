# -*- coding: utf-8 -*-

# install
import windnd

# project
import core

# self
from . import hook_dropfiles
from . import modify_classification
from . import preview_actions
from . import modify_item_data


def initial():
    windnd.hook_dropfiles(core.window.frame_notebook, func=hook_dropfiles.hook_dropfiles)
    modify_classification.bind_context_menu(core.window.interface.mods_manage)
    core.window.interface.mods_manage.label_preview.bind('<Button-1>', preview_actions.bin_preview_click)
    core.window.interface.mods_manage.label_preview.bind('<Button-3>', preview_actions.bin_preview_right_click)
    modify_item_data.bind_context_menu(core.window.interface.mods_manage.treeview_choices)



# frame_notebook.drop_target_register(tkinterdnd2.DND_FILES)
# frame_notebook.dnd_bind("<<Drop>>", lambda e: print(e))
