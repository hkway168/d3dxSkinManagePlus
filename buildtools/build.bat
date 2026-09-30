@echo off
chcp 65001 >nul
setlocal EnableExtensions

rem ============================================================
rem  d3dxSkinManage 一键编译脚本
rem  用法: 双击运行，或 buildtools\build.bat [onedir] [nopause]
rem    onedir  - 生成目录版 (启动更快)，默认生成单文件 exe
rem    nopause - 结束时不暂停
rem  输出: dist\d3dxSkinManage\
rem ============================================================

set "APP_NAME=d3dxSkinManage"
set "MODE=--onefile"
set "NOPAUSE="
for %%A in (%*) do (
    if /I "%%~A"=="onedir" set "MODE=--onedir"
    if /I "%%~A"=="nopause" set "NOPAUSE=1"
)

pushd "%~dp0.."
set "ROOT=%CD%"
set "VENV=%ROOT%\.venv"
set "OUT=%ROOT%\dist\%APP_NAME%"
set "WORK=%ROOT%\build"

echo [1/5] 检查 Python ...
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY ( where py >nul 2>nul && set "PY=py -3" )
if not defined PY (
    echo [错误] 未找到 Python，请安装 Python 3.10+ 并加入 PATH
    goto :fail
)
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"
if errorlevel 1 (
    echo [错误] 需要 Python 3.10 及以上版本
    goto :fail
)

echo [2/5] 准备虚拟环境 .venv ...
if not exist "%VENV%\Scripts\python.exe" (
    %PY% -m venv "%VENV%"
    if errorlevel 1 ( echo [错误] 创建虚拟环境失败 & goto :fail )
)
set "VPY=%VENV%\Scripts\python.exe"

echo [3/5] 安装依赖 ...
"%VPY%" -m pip install --disable-pip-version-check -q --upgrade pip
"%VPY%" -m pip install --disable-pip-version-check -q -r "%ROOT%\requirements.txt" pyinstaller
if errorlevel 1 ( echo [错误] 依赖安装失败 & goto :fail )
"%VPY%" "%ROOT%\buildtools\check_imports.py"
if errorlevel 1 goto :fail

echo [4/5] PyInstaller 打包 ...
set "ICON_ARG="
if exist "%ROOT%\local\iconbitmap.ico" set "ICON_ARG=--icon "%ROOT%\local\iconbitmap.ico""
if exist "%OUT%" rmdir /s /q "%OUT%"

"%VPY%" -m PyInstaller -y --clean --noconfirm %MODE% --windowed ^
    --name "%APP_NAME%" ^
    --paths "%ROOT%\src" ^
    --collect-data ttkbootstrap ^
    --distpath "%ROOT%\dist\_pyi" ^
    --workpath "%WORK%" ^
    --specpath "%WORK%" ^
    %ICON_ARG% ^
    "%ROOT%\src\%APP_NAME%.py"
if errorlevel 1 ( echo [错误] 打包失败 & goto :fail )

if /I "%MODE%"=="--onefile" (
    mkdir "%OUT%" >nul 2>nul
    move /y "%ROOT%\dist\_pyi\%APP_NAME%.exe" "%OUT%\" >nul
) else (
    move /y "%ROOT%\dist\_pyi\%APP_NAME%" "%OUT%" >nul
)
rmdir /s /q "%ROOT%\dist\_pyi" >nul 2>nul

echo [5/5] 复制运行组件 ...
mkdir "%OUT%\local\7zip" >nul 2>nul
if exist "%ROOT%\local\7zip\7z.exe" (
    copy /y "%ROOT%\local\7zip\7z.exe" "%OUT%\local\7zip\" >nul
    if exist "%ROOT%\local\7zip\7z.dll" copy /y "%ROOT%\local\7zip\7z.dll" "%OUT%\local\7zip\" >nul
    if exist "%ROOT%\local\7zip\License.txt" copy /y "%ROOT%\local\7zip\License.txt" "%OUT%\local\7zip\" >nul
) else (
    echo [警告] 未找到 local\7zip\7z.exe，请手动放入 "%OUT%\local\7zip\"
)
if exist "%ROOT%\local\iconbitmap.ico" copy /y "%ROOT%\local\iconbitmap.ico" "%OUT%\local\" >nul

echo.
echo [完成] 输出目录: %OUT%
popd
if not defined NOPAUSE pause
exit /b 0

:fail
popd
if not defined NOPAUSE pause
exit /b 1
