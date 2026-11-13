# d3dxSkinManagePlus

## 简介

3DMigoto Mods 管理工具，基于 [numlinka/d3dxSkinManage](https://d3dxskinmanage.numlinka.com/) v1.5.6 修改。

本分支为**纯本地运行**版本：已移除启动自动更新、在线 Mod 仓库与下载功能，不再依赖网络。

## 主要改动

- **多用户管理**：登录界面可直接创建用户（用户名、描述、头像、游戏路径，可从已有用户复制分类配置），支持注销返回登录界面。
- **对接 XXMI Launcher**：不再内置 3DMigoto 版本压缩包，改为将 [XXMI Launcher](https://github.com/SpectrumQT/XXMI-Launcher) 对应导入器（GIMI / SRMI / ZZMI / WWMI / HIMI / EFMI）的目录指向当前用户的 `work` 目录，由其负责 3DMigoto 的下载、更新与注入启动。
- **高 DPI 适配**：适配 4K 等高缩放比例屏幕，行高、列宽、缩略图按系统 DPI 自动换算。
- **分类管理增强**：分类支持添加、置顶 / 上移 / 下移 / 置底、重命名、删除；对象支持排序、移出分类。
- **预览图增强**：
  - 左键预览区域全屏查看，单击或 `Esc` 关闭；
  - 右键预览区域将剪贴板图片设为预览图；
  - 拖入图片设置预览图，支持 `.png` / `.jpg` / `.jpeg` / `.bmp` / `.gif` / `.webp`，非 png/jpg 自动转换；
  - 替换已有预览图前会提示是否覆盖，并自动清理旧文件。
- **主题化右键菜单**：右键菜单跟随 ttkbootstrap 主题样式。
- **内置使用帮助**：「关于」页面替换为完整的使用说明。
- **一键打包**：提供 `buildtools/build.bat`，自动创建虚拟环境、安装依赖并用 PyInstaller 打包。

## 运行

### 运行环境

```
Python 3.10+
Windows 10+
```

### 依赖库

```
pillow
pywin32
ttkbootstrap
windnd
pygetwindow
pynput
```

安装：

```
pip install -r requirements.txt
```

### 运行

```
python ./src/d3dxSkinManage.py
```

> 导入与加载 Mod 依赖 7-Zip，请确保 `local/7zip/7z.exe`（及 `7z.dll`）存在。

## 打包

双击运行 `buildtools/build.bat`，或在命令行中执行：

```
buildtools\build.bat [onedir] [nopause]
```

| 参数      | 说明                                        |
| --------- | ------------------------------------------- |
| `onedir`  | 生成目录版（启动更快），默认生成单文件 exe  |
| `nopause` | 结束时不暂停                                |

脚本流程：

1. 检查 Python 3.10+；
2. 在项目根目录创建 `.venv` 虚拟环境；
3. 安装 `requirements.txt` 与 PyInstaller，并通过 `buildtools/check_imports.py` 检查 `src` 中的第三方模块是否均已安装；
4. PyInstaller 打包（若存在 `local/iconbitmap.ico` 则作为程序图标）；
5. 复制 `local/7zip` 与图标等运行组件。

输出目录：`dist/d3dxSkinManage/`

## 快速上手

> 前置条件：先安装 [XXMI Launcher](https://github.com/SpectrumQT/XXMI-Launcher)，3DMigoto 本体由它负责下载与更新。

1. 在登录界面创建或选择一个用户并登录（每个用户的数据相互独立）。
2. 进入「环境设置」，点击「选择 XXMI 目录」，选择模组导入器，并通过「文件选择工具」选择游戏主程序。
3. 点击「启动 XXMI Launcher」，在其中完成 3DMigoto 的安装 / 更新（会部署到当前用户的 `work` 目录）。
4. 回到「Mods 管理」，在分类列表右键「添加分类」，在对象列表右键「添加对象」。
5. 将 Mod 压缩包（`.zip` / `.rar` / `.7z`）、单个 `.ini` 文件或文件夹拖入主窗口，填写 Mod 信息后确定。
6. 在「选择」列表中双击 Mod 即可加载；选中 Mod 后拖入图片可设置预览图。
7. 点击「启动游戏」，由 XXMI Launcher 注入并启动游戏。

更详细的说明见程序内「关于」页面。

## 工作方式

将 Mod 压缩包以其 SHA1 值命名储存在 `./resources/mods` 中，并使用索引文件记录 Mod 文件的相关信息。

在加载 Mod 时将压缩包释放到对应用户 3DMigoto 工作目录的 Mods 文件夹（`home/<用户名>/work/Mods`），该工作目录同时作为 XXMI Launcher 的导入器目录。

单个 `.ini` 文件形式的 Mod 同样以 SHA1 命名直接储存，加载时无需解压，会被复制到 `home/<用户名>/work/Mods/<SHA1>/` 下。

[文件结构](doc/file-structure.md)

## 许可证

[GPL-3.0](LICENSE)
