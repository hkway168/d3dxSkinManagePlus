# -*- coding: utf-8 -*-
"""扫描 src 下所有第三方 import，确认当前环境可导入，避免打包后运行时缺模块。"""

import ast
import importlib.util
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parent.parent / "src"


def collect() -> dict[str, set[str]]:
    local = {p.name for p in SRC.iterdir() if p.is_dir()} | {p.stem for p in SRC.glob("*.py")}
    found: dict[str, set[str]] = {}
    for file in SRC.rglob("*.py"):
        try:
            tree = ast.parse(file.read_text("utf-8"), str(file))
        except SyntaxError as e:
            print(f"[错误] 语法错误: {e}")
            sys.exit(2)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names = [node.module]
            else:
                continue
            for name in names:
                top = name.split(".")[0]
                if top in local or top in sys.stdlib_module_names:
                    continue
                found.setdefault(top, set()).add(str(file.relative_to(SRC)))
    return found


def main() -> int:
    missing = {m: f for m, f in collect().items() if importlib.util.find_spec(m) is None}
    if not missing:
        return 0
    print("[错误] 以下模块未安装，请加入 requirements.txt:")
    for mod, files in sorted(missing.items()):
        print(f"    {mod}  <- {', '.join(sorted(files))}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
