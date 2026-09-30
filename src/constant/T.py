# -*- coding: utf-8 -*-


TEXT_HELP = """d3dxSkinManage 使用帮助
（3DMigoto Mods 辅助管理工具）


一、快速上手
    1. 在登录界面创建或选择一个用户并登录（每个用户的数据相互独立）。
    2. 进入「环境设置」，选择 3DMigoto 版本，并通过「文件选择工具」设置游戏路径。
    3. 回到「Mods 管理」，在分类列表右键「添加分类」，在对象列表右键「添加对象」。
    4. 将 Mod 压缩包或文件夹拖入主窗口，填写 Mod 信息后确定。
    5. 在「选择」列表中双击 Mod 即可加载；拖入图片可为 Mod 设置预览图。
    6. 先点击「启动 3DMiGoto 加载器」，再点击「启动游戏」。


二、Mods 管理
    界面从左到右依次为：分类 / 对象 / 选择 / 预览。

    ● 分类列表
        左键：查看该分类下的对象
        右键：添加分类 / 管理分类（置顶、上移、下移、置底、重命名、删除）
        删除分类不会删除任何 Mod，其中的对象会回到「未分类」。
        分类名不能为空、不能为「未分类」、不能包含 / \\ : * ? " < > | 且不能重名。

    ● 对象列表
        左键：查看该对象的全部 Mod
        右键：添加对象 / 管理子对象（排序、移出分类）
        一个对象只能属于一个分类；添加已在其他分类中的对象时，会询问是否移动过来。
        [a/b] 表示：本地已有 Mod 数 / 索引中的 Mod 总数。
        「启用 Mod」列显示该对象当前加载的 Mod。

    ● 选择列表
        单击：查看预览图；鼠标悬停可查看名称、作者、描述与标签
        双击：加载该 Mod（同一对象只能同时启用一个 Mod，会自动替换）
        双击「- [X] 卸载该对象 -」：卸载该对象当前的 Mod
        名称颜色表示 Mod 的状态：
            绿色  正在使用（已加载并处于启用状态）
            黄色  已解压缓存（曾经加载过，文件仍留在 work\\Mods 中）
            默认  尚未解压到工作目录
        右键 Mod：
            修改 Mod 信息
            查看缓存文件（打开已解压到 work\\Mods 中的文件夹）
            删除缓存文件（删除 work\\Mods 中的解压缓存，正在使用时会先卸载）
            查看原始文件（打开 resources\\mods 中的原始压缩包）

    ● 预览
        左键：全屏预览该预览图，单击或按 Esc 关闭；
              若该 Mod 暂无预览图，可选择使用剪贴板中的图片或从文件中选择图片进行设置。
        右键：将剪贴板中的图片（截图或复制的图片文件）直接设为预览图。
        已有预览图时，替换前会提示是否覆盖。

    ● 搜索
        在选择列表下方的输入框中输入关键字，实时筛选。
        可匹配：名称、对象、分级、标签、作者。
        多个关键字用空格分隔，需同时满足；以 ! 开头表示排除该关键字。


三、导入 Mod
    ● 登录后将文件拖入主窗口即可导入，一次仅支持拖入一个文件。
    ● 支持 .zip / .rar / .7z 压缩包；拖入文件夹时会询问是否打包后导入。
    ● 也支持直接拖入单个 .ini 文件，无需先打包成压缩包；
      这类 Mod 不会被压缩，加载时会直接复制到工作目录的 Mods\\<SHA> 文件夹中。
    ● 导入时需填写：
        作用对象（必填）、模组名称（必填）、年龄分级（必填：G 大众级 / P 指导级 / R 成人级）
        模组作者、附加描述、类型标签（多个标签以空格分隔）为选填。
    ● Mod 以其 SHA-1 值作为唯一标识，重复导入同一文件会直接进入修改信息界面。

    ● 修改信息界面中：
        「删除」      仅删除 Mod 文件，保留索引信息
        「完全移除」  同时删除 Mod 文件与索引信息
        以上操作不可撤销，请谨慎使用。


四、设置预览图
    ● 先在选择列表中选中一个 Mod，再将图片拖入主窗口，即可直接设为预览图。
        支持 .png / .jpg / .jpeg / .bmp / .gif / .webp（不区分大小写），非 png/jpg 格式会自动转换为 png。
    ● 也可以复制图片后右键预览区域，直接设为预览图。
    ● 重新设置即可替换原有预览图（会提示是否覆盖），旧的预览图文件会被自动清理。
    ● 若 Mod 文件夹内自带 preview.png/jpg，将会被自动采用。


五、环境设置
    ● 全局设置
        主题风格：立即生效
        日志等级：重启后生效
        描述提示词数量：控制鼠标悬停提示的详细程度

    ● 3DMigoto 版本
        从 resources\\3dmigoto 中选择版本压缩包。
        注意：切换版本会清空工作目录中除 Mods 以外的全部内容，请勿在 3DMigoto 运行时切换。
        「启动 3DMiGoto 加载器」以管理员权限运行加载器。
        「打开工作目录」打开当前用户的 work 文件夹。

    ● 游戏路径
        请务必通过「文件选择工具」选择游戏主程序（而不是启动器 launcher.exe）。
        选择后会自动修改 d3dx.ini 中的 target 项。
        「启动游戏」/「打开游戏目录」

    ● 切换用户：点击窗口右下角「[ 退出用户 ]」返回登录界面。


六、工具
    ● 强迫症预览图裁剪工具
        用于截取位置与尺寸统一的预览图，结果保存为桌面上的 preview.png。
        要求游戏以 1920×1080 分辨率运行。
        方式一：将完整的游戏截图拖入工具窗口。
        方式二：游戏窗口化运行时，双击工具窗口自动截取游戏画面。

    ● 设置
        在对象列表中显示没有 Mod 的对象：默认关闭，关闭时本地没有任何 Mod 的对象不在对象列表中显示。


七、目录结构
    home\\<用户名>\\
        classification\\       分类配置
        modsIndex\\            Mod 索引（self-index.json）
        work\\                 3DMigoto 工作目录（Mods 解压于 work\\Mods）
        description.txt       用户描述
        picture.png/jpg       用户头像
    resources\\
        3dmigoto\\             3DMigoto 版本压缩包
        mods\\                 以 SHA 命名的 Mod 原始文件
        preview\\              预览图
        thumbnail\\            分类与对象缩略图（_redirection.ini 可配置映射）
    local\\
        7zip\\7z.exe           导入与加载 Mod 所依赖的解压程序


八、常见问题
    ● 拖入文件没有反应？
        请确认已登录，且一次只拖入一个文件。
    ● Mod 加载后游戏内不生效？
        请确认已选择 3DMigoto 版本、游戏路径正确，并且先启动加载器再启动游戏。
    ● 卸载后的 Mod 去哪了？
        卸载只会将 work\\Mods 中的文件夹重命名为 disabled-<SHA>，再次加载时直接恢复，不会重复解压。
"""


ANNOTATION_USER_DESCRIPTION = """这是该用户的描述文档
你可以修改 ./home/<USERNAME>/ 下的 description.txt 文件来修改这项描述"""

ANNOTATION_LOGIN = """点一下，玩一年，皮肤不花一分钱。
一刀满级绿色版，账号回收秒到账。"""

ANNOTATION_LOGOUT = """点击退出当前用户并返回登录界面
退出前会自动保存索引数据和用户配置
未完成的下载任务将被中断"""

ANNOTATION_MANAGE_CLASSIFICATION = "\n".join([
    "左键单击 查看对应类别的对象",
    "右键单击 添加分类 / 管理分类"
])

ANNOTATION_MANAGE_OBJECTS = "\n".join([
    "左键单击 查看对应对象的 Mod",
    "右键单击 添加对象 / 管理子对象"
])

ANNOTATION_MANAGE_CHOICES = "\n".join([
    "左键单击 查看对应 Mod 的预览图",
    "左键双击 加载对应 Mod 至 3DMiGoto",
    "右键单击 Mod 修改信息 / 查看、删除缓存文件 / 查看原始文件",
    "左键双击 \"卸载该对象\" 卸载 Mod"
])

ANNOTATION_MANAGE_SEARCH = """可通过以下字段的内容筛选 Mod
SHA、对象、名称、分级、作者、标签
使用空格分割多个关键字
使用 "!" 符号开头拒绝对应关键词
切换对象仍然有效"""

ANNOTATION_STYLE_THEME = """主题风格
挑选一个你喜欢的色彩搭配

该项设置立即生效"""

ANNOTATION_LOG_LEVEL = """日志等级
等级越高记录的信息越多

ALL - 记录所有级别的日志
OFF - 关闭日志记录器

该项设置在重启后生效"""

ANNOTATION_ANNOTATION_LEVEL = """描述提示词数量
显示操作描述的数量

若你已经了解该软件的相关操作
可以适当减少一些操作描述

该项设置立即生效"""

ANNOTATION_SHOW_EMPTY_OBJECTS = """在对象列表中显示没有 Mod 的对象
关闭时，本地没有任何 Mod 的对象不会出现在对象列表中
分类后的数量也只统计有 Mod 的对象

默认关闭，该项设置立即生效"""

ANNOTATION_D3DX_VERSION = """点击右侧的下拉箭头或输入框底部唤出下拉菜单
在下拉菜单中选择需要切换到的版本
不要尝试在 3DMiGoto 运行时切换版本"""

ANNOTATION_D3DX_INJECTION = """我知道你在想什么\n但这个玩意儿确实不能用"""

ANNOTATION_D3DX_START = "先 启动 3DMiGoto 加载器\n再 启动游戏"

ANNOTATION_D3DX_OPEN_WORK_DIR = "在文件资源管理器中打开 3DMiGoto 的工作目录"

ANNOTATION_D3DX_SET_GAME_PATH = "用户必须使用文件选择工具修改游戏路径\n直接修改输入框的内容是不生效的"

ANNOTATION_D3DX_GAME_WORK_DIR = "在文件资源管理器中打开游戏所在目录"

ANNOTATION_CLASS_NAME = "分类名称\n同时也是分类参照的文件名\n不能包含特殊字符"
ANNOTATION_ADD_OBJECT = "分类中的具体对象\n下拉列表仅显示尚未分类的对象, 也可直接输入\n保存后显示在该分类的对象列表中"

ANNOTATION_MODIFY_CLASS_OK = "修改数据并保存"
ANNOTATION_MODIFY_CLASS_CANCEL = "什么都不做"
ANNOTATION_MODIFY_CLASS_DELETE = "删除该分类"

ANNOTATION_SHA = """Mod 压缩包的文件散列值（哈希值）
使用 SHA-1 算法并被用作为 Mod 的唯一标识符"""

ANNOTATION_OBJECT = "标识 Mod 所作用的对象\n* 必要"

ANNOTATION_NAME = "标识 Mod 的名称\n用于标记和区分同作用对象的 Mod\n* 必要"

ANNOTATION_AUTHOR = "标识 Mod 的作者"

ANNOTATION_GRADING = """标识年龄分级
G - 表示大众级 : 没有不适宜或可以被大众所接受的内容
P - 表示指导级 : 带有不适宜、性暗示或诱惑的内容
R - 表示成人级 : 带有性、暴力、血腥、恐怖或令人感到不适的内容
* 必要"""

ANNOTATION_EXPLAIN = "对 Mod 的额外描述内容"

ANNOTATION_TAGS = """描述该 Mod 所包含的内容标签
使用空格分隔多个 标签"""

ANNOTATION_ADD_MOD_OK = "确认导入该 Mod"

ANNOTATION_MODIFY_ITEM_OK = "修改数据并保存"
ANNOTATION_MODIFY_ITEM_CANCEL = "什么都不做"
ANNOTATION_MODIFY_ITEM_REMOVE = "删除 Mod 文件"
ANNOTATION_MODIFY_ITEM_DELETE = "删除 Mod 文件和索引数据"
