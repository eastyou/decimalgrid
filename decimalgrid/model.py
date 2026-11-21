"""小数方格图：涂色格数、小数 / 百分数 / 分数互化与出题。"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, List, Optional, Sequence, Tuple

TOTAL_CELLS = 100
KINDS: Tuple[str, ...] = ("read", "shade", "convert")


class DecimalGridError(ValueError):
    """小数方格图相关的输入错误。"""


def check_hundredths(value: Any, name: str = "涂色格数") -> int:
    """校验涂色格数是 0–100 的整数。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise DecimalGridError("%s必须是整数" % name)
    if value < 0 or value > TOTAL_CELLS:
        raise DecimalGridError("%s必须在 0–100 之间：%d" % (name, value))
    return value


def decimal_text(hundredths: int) -> str:
    """把百分位格数写成两位小数，如 37 → 0.37。"""
    check_hundredths(hundredths)
    whole, part = divmod(hundredths, 100)
    return "%d.%02d" % (whole, part)


def percent_text(hundredths: int) -> str:
    """把百分位格数写成百分数，如 37 → 37%。"""
    check_hundredths(hundredths)
    return "%d%%" % hundredths


def fraction_pair(hundredths: int) -> Tuple[int, int]:
    """返回最简分数（分子, 分母）。"""
    check_hundredths(hundredths)
    divisor = math.gcd(hundredths, TOTAL_CELLS)
    return hundredths // divisor, TOTAL_CELLS // divisor


def fraction_text(hundredths: int) -> str:
    """返回最简分数文本，如 50 → 1/2。"""
    numerator, denominator = fraction_pair(hundredths)
    return "%d/%d" % (numerator, denominator)


def parse_decimal(text: str) -> int:
    """把 0–1 的小数文本解析成百分位格数。"""
    if not isinstance(text, str) or not text.strip():
        raise DecimalGridError("小数不能为空")
    cleaned = text.strip()
    if cleaned.endswith("%"):
        raise DecimalGridError("百分数请去掉百分号后再试")
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        raise DecimalGridError("无法识别的小数：%s" % text)
    if value < 0 or value > 1:
        raise DecimalGridError("小数必须在 0–1 之间：%s" % text)
    scaled = value * TOTAL_CELLS
    if scaled != scaled.to_integral_value():
        raise DecimalGridError("小数最多两位：%s" % text)
    return int(scaled)


def parse_percent(text: str) -> int:
    """把百分数文本解析成百分位格数。"""
    if not isinstance(text, str) or not text.strip():
        raise DecimalGridError("百分数不能为空")
    cleaned = text.strip()
    if not cleaned.endswith("%"):
        raise DecimalGridError("百分数需要以 %% 结尾：%s" % text)
    try:
        value = Decimal(cleaned[:-1])
    except InvalidOperation:
        raise DecimalGridError("无法识别的百分数：%s" % text)
    if value < 0 or value > 100:
        raise DecimalGridError("百分数必须在 0–100 之间：%s" % text)
    if value != value.to_integral_value():
        raise DecimalGridError("百分数必须是整数：%s" % text)
    return int(value)


@dataclass(frozen=True)
class GridProblem:
    """一道涂色读数、涂色操作或互化题。"""

    hundredths: int
    kind: str

    def __post_init__(self) -> None:
        check_hundredths(self.hundredths)
        if self.kind not in KINDS:
            raise DecimalGridError("未知题型：%s" % self.kind)

    @property
    def prompt(self) -> str:
        if self.kind == "read":
            return "图中涂色部分用小数和百分数表示分别是多少？"
        if self.kind == "shade":
            return "在方格图中涂出 %s" % decimal_text(self.hundredths)
        return "把 %s 化成百分数和最简分数" % decimal_text(self.hundredths)

    @property
    def answer(self) -> str:
        if self.kind == "read":
            return "%s，%s" % (decimal_text(self.hundredths), percent_text(self.hundredths))
        if self.kind == "shade":
            return "涂 %d 格" % self.hundredths
        return "%s，%s" % (percent_text(self.hundredths), fraction_text(self.hundredths))


def generate_problems(
    count: int = 8,
    kinds: Sequence[str] = KINDS,
    min_hundredths: int = 1,
    max_hundredths: int = 99,
    seed: Optional[int] = None,
) -> List[GridProblem]:
    """生成不重复的方格图题目。"""
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise DecimalGridError("题目数量必须是正整数")
    if count > 40:
        raise DecimalGridError("题目数量不能超过 40")
    check_hundredths(min_hundredths, "最小格数")
    check_hundredths(max_hundredths, "最大格数")
    if min_hundredths > max_hundredths:
        raise DecimalGridError("最小格数不能大于最大格数")
    chosen = tuple(kinds)
    if not chosen:
        raise DecimalGridError("至少需要一种题型")
    for kind in chosen:
        if kind not in KINDS:
            raise DecimalGridError("未知题型：%s" % kind)

    rng = random.Random(seed)
    values = list(range(min_hundredths, max_hundredths + 1))
    if count > len(values) * len(chosen):
        raise DecimalGridError("可用题目不足 %d 道" % count)
    result: List[GridProblem] = []
    used = set()
    attempts = 0
    while len(result) < count and attempts < count * 100:
        attempts += 1
        hundredths = rng.choice(values)
        kind = rng.choice(chosen)
        key = (hundredths, kind)
        if key in used:
            continue
        used.add(key)
        result.append(GridProblem(hundredths, kind))
    if len(result) < count:
        raise DecimalGridError("可用题目不足 %d 道" % count)
    return result
