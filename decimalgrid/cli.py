"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    KINDS,
    TOTAL_CELLS,
    DecimalGridError,
    decimal_text,
    fraction_text,
    generate_problems,
    parse_decimal,
    parse_percent,
    percent_text,
)
from .render import render_grid, render_worksheet


def build_parser() -> argparse.ArgumentParser:
    """构造命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="decimalgrid",
        description="小数方格图：10×10 涂色读数与小数、百分数、分数互化练习纸",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sheet = subparsers.add_parser("sheet", help="生成 A4 练习纸 HTML")
    sheet.add_argument("--count", type=int, default=8, help="题目数量，默认 8")
    sheet.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet.add_argument(
        "--kinds",
        default=",".join(KINDS),
        help="题型，用逗号分隔：read（读数）、shade（涂色）、convert（互化）",
    )
    sheet.add_argument("--min", dest="min_hundredths", type=int, default=1, help="最小涂色格数，默认 1")
    sheet.add_argument("--max", dest="max_hundredths", type=int, default=99, help="最大涂色格数，默认 99")
    sheet.add_argument("--size", type=int, default=220, help="方格图边长，默认 220")
    sheet.add_argument("--title", default="小数方格图练习", help="练习纸标题")
    sheet.add_argument("--answers", action="store_true", help="追加参考答案")
    sheet.add_argument("-o", "--output", default=None, help="输出文件")

    grid = subparsers.add_parser("grid", help="输出单个方格图 SVG")
    grid.add_argument("shaded", type=int, help="涂色格数（0–%d）" % TOTAL_CELLS)
    grid.add_argument("--size", type=int, default=220, help="边长，默认 220")
    grid.add_argument("-o", "--output", default=None, help="输出文件")

    convert = subparsers.add_parser("convert", help="小数、百分数与分数互化")
    convert.add_argument("value", help="小数（0.37）或百分数（37%%）")
    return parser


def _write_output(text: str, output: Optional[str]) -> None:
    if not output:
        print(text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("已写入 %s" % path)


def _parse_kinds(text: str) -> List[str]:
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        raise DecimalGridError("至少需要一种题型")
    return parts


def main(argv: Optional[List[str]] = None) -> int:
    """命令行主函数，返回进程退出码。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "grid":
            _write_output(render_grid(args.shaded, args.size), args.output)
            return 0
        if args.command == "convert":
            raw = args.value.strip()
            hundredths = parse_percent(raw) if raw.endswith("%") else parse_decimal(raw)
            print("小数：%s" % decimal_text(hundredths))
            print("百分数：%s" % percent_text(hundredths))
            print("最简分数：%s" % fraction_text(hundredths))
            print("涂色格数：%d" % hundredths)
            return 0
        problems = generate_problems(
            args.count,
            _parse_kinds(args.kinds),
            args.min_hundredths,
            args.max_hundredths,
            args.seed,
        )
        _write_output(
            render_worksheet(problems, args.title, args.answers, args.size),
            args.output,
        )
        return 0
    except DecimalGridError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1
