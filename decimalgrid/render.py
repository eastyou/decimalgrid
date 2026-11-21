"""方格图 SVG 与 A4 练习纸渲染。"""

from __future__ import annotations

import html
from typing import List, Sequence

from .model import (
    TOTAL_CELLS,
    DecimalGridError,
    GridProblem,
    check_hundredths,
    decimal_text,
)

_CSS = """
@page { size: A4; margin: 12mm; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
       color: #1f2933; background: #fff; }
.sheet { padding: 4mm; }
h1 { margin: 0 0 2mm; font-size: 22px; text-align: center; letter-spacing: 2px; }
.meta { margin: 0 0 5mm; text-align: center; color: #616e7c; font-size: 12px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.card { border: 1px solid #cbd2d9; border-radius: 3mm; padding: 3mm; page-break-inside: avoid; }
.prompt { font-size: 13px; margin: 0 0 2mm; color: #323f4b; }
.answer-line { margin-top: 2mm; border-bottom: 1px dashed #9aa5b1; height: 22px; }
.answers { page-break-before: always; margin-top: 6mm; }
.answers h2 { font-size: 18px; border-left: 4px solid #6b46c1; padding-left: 3mm; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { border: 1px solid #cbd2d9; padding: 2mm 3mm; text-align: left; }
th { background: #f5f7fa; }
@media print { .sheet { padding: 0; } }
""".strip()


def _fmt(value: float) -> str:
    return ("%.2f" % value).rstrip("0").rstrip(".")


def render_grid(shaded: int = 0, size: int = 220) -> str:
    """绘制 10×10 方格图，前 shaded 格涂色。"""
    check_hundredths(shaded)
    if isinstance(size, bool) or not isinstance(size, int) or size < 120:
        raise DecimalGridError("方格图尺寸必须是至少 120 的整数")

    cell = size / 10.0
    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
        'role="img" aria-label="小数方格图">' % (size, size, size, size),
        "<title>小数方格图</title>",
        '<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (size, size),
    ]
    for index in range(TOTAL_CELLS):
        row, col = divmod(index, 10)
        fill = "#6b46c1" if index < shaded else "#ffffff"
        parts.append(
            '<rect x="%s" y="%s" width="%s" height="%s" fill="%s" stroke="#cbd2d9" '
            'stroke-width="0.7"/>'
            % (_fmt(col * cell), _fmt(row * cell), _fmt(cell), _fmt(cell), fill)
        )
    parts.append(
        '<rect x="0.5" y="0.5" width="%s" height="%s" fill="none" stroke="#323f4b" '
        'stroke-width="1.6"/>' % (_fmt(size - 1.0), _fmt(size - 1.0))
    )
    parts.append("</svg>")
    return "\n".join(parts)


def render_worksheet(
    problems: Sequence[GridProblem],
    title: str = "小数方格图练习",
    answers: bool = False,
    size: int = 220,
) -> str:
    """生成可打印的小数方格图练习纸。"""
    items = list(problems)
    if not items:
        raise DecimalGridError("至少需要一道题")
    for item in items:
        if not isinstance(item, GridProblem):
            raise DecimalGridError("题目必须是 GridProblem")

    cards: List[str] = []
    for index, item in enumerate(items, 1):
        shaded = item.hundredths if item.kind == "read" else 0
        cards.append(
            '<div class="card">\n<p class="prompt">%d. %s</p>\n%s\n'
            '<div class="answer-line"></div>\n</div>'
            % (index, html.escape(item.prompt), render_grid(shaded, size))
        )

    sections = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % html.escape(title),
        "<style>%s</style></head><body>" % _CSS,
        '<main class="sheet">',
        "<h1>%s</h1>" % html.escape(title),
        '<p class="meta">姓名：__________　班级：__________　日期：__________</p>',
        '<section class="grid">',
        "\n".join(cards),
        "</section>",
    ]

    if answers:
        rows = []
        for index, item in enumerate(items, 1):
            rows.append(
                "<tr><td>%d</td><td>%s</td><td>%s</td></tr>"
                % (index, html.escape(item.prompt), html.escape(item.answer))
            )
        sections.append(
            '<section class="answers"><h2>参考答案</h2>'
            "<table><thead><tr><th>题号</th><th>题目</th><th>答案</th></tr></thead>"
            "<tbody>%s</tbody></table></section>" % "\n".join(rows)
        )

    sections.append("</main></body></html>")
    return "\n".join(sections)
