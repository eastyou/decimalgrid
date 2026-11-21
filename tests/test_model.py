"""小数、百分数与分数互化测试。"""

import math
import unittest
from dataclasses import FrozenInstanceError
from decimal import Decimal

from decimalgrid.model import (
    KINDS,
    TOTAL_CELLS,
    DecimalGridError,
    GridProblem,
    check_hundredths,
    decimal_text,
    fraction_pair,
    fraction_text,
    generate_problems,
    parse_decimal,
    parse_percent,
    percent_text,
)


class GeneratedConversionTest(unittest.TestCase):
    """逐一验证 0–100 格的三种表示。"""


def _make_conversion_test(hundredths):
    def test(self):
        self.assertEqual(decimal_text(hundredths), "%d.%02d" % divmod(hundredths, 100))
        self.assertEqual(percent_text(hundredths), "%d%%" % hundredths)
        numerator, denominator = fraction_pair(hundredths)
        self.assertEqual(numerator * TOTAL_CELLS, denominator * hundredths)
        if numerator != 0:
            self.assertEqual(math.gcd(numerator, denominator), 1)
        value = Decimal(decimal_text(hundredths))
        self.assertEqual(value, Decimal(hundredths) / TOTAL_CELLS)

    test.__doc__ = "%d 格的三种表示" % hundredths
    return test


for _hundredths in range(0, TOTAL_CELLS + 1):
    setattr(
        GeneratedConversionTest,
        "test_%03d" % _hundredths,
        _make_conversion_test(_hundredths),
    )


class CheckTest(unittest.TestCase):
    def test_bounds(self):
        self.assertEqual(check_hundredths(0), 0)
        self.assertEqual(check_hundredths(100), 100)

    def test_negative(self):
        with self.assertRaises(DecimalGridError):
            check_hundredths(-1)

    def test_too_many(self):
        with self.assertRaises(DecimalGridError):
            check_hundredths(101)

    def test_bool(self):
        with self.assertRaises(DecimalGridError):
            check_hundredths(True)

    def test_float(self):
        with self.assertRaises(DecimalGridError):
            check_hundredths(3.5)

    def test_string(self):
        with self.assertRaises(DecimalGridError):
            check_hundredths("37")

    def test_custom_name(self):
        with self.assertRaisesRegex(DecimalGridError, "最小格数"):
            check_hundredths(-2, "最小格数")


class TextTest(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(decimal_text(0), "0.00")

    def test_full(self):
        self.assertEqual(decimal_text(100), "1.00")

    def test_leading_zero(self):
        self.assertEqual(decimal_text(5), "0.05")

    def test_percent_zero(self):
        self.assertEqual(percent_text(0), "0%")

    def test_percent_full(self):
        self.assertEqual(percent_text(100), "100%")

    def test_fraction_half(self):
        self.assertEqual(fraction_text(50), "1/2")

    def test_fraction_quarter(self):
        self.assertEqual(fraction_text(25), "1/4")

    def test_fraction_fifth(self):
        self.assertEqual(fraction_text(20), "1/5")

    def test_fraction_three_quarters(self):
        self.assertEqual(fraction_text(75), "3/4")

    def test_fraction_odd(self):
        self.assertEqual(fraction_text(37), "37/100")

    def test_fraction_full(self):
        self.assertEqual(fraction_text(100), "1/1")


class ParseTest(unittest.TestCase):
    def test_decimal(self):
        self.assertEqual(parse_decimal("0.37"), 37)

    def test_decimal_short(self):
        self.assertEqual(parse_decimal(".5"), 50)

    def test_decimal_full(self):
        self.assertEqual(parse_decimal("1.00"), 100)

    def test_decimal_zero(self):
        self.assertEqual(parse_decimal("0"), 0)

    def test_decimal_too_precise(self):
        with self.assertRaises(DecimalGridError):
            parse_decimal("0.375")

    def test_decimal_out_of_range(self):
        with self.assertRaises(DecimalGridError):
            parse_decimal("1.5")

    def test_decimal_negative(self):
        with self.assertRaises(DecimalGridError):
            parse_decimal("-0.2")

    def test_decimal_not_number(self):
        with self.assertRaises(DecimalGridError):
            parse_decimal("abc")

    def test_decimal_empty(self):
        with self.assertRaises(DecimalGridError):
            parse_decimal("  ")

    def test_decimal_percent_sign(self):
        with self.assertRaises(DecimalGridError):
            parse_decimal("37%")

    def test_percent(self):
        self.assertEqual(parse_percent("37%"), 37)

    def test_percent_full(self):
        self.assertEqual(parse_percent("100%"), 100)

    def test_percent_missing_sign(self):
        with self.assertRaises(DecimalGridError):
            parse_percent("37")

    def test_percent_not_integer(self):
        with self.assertRaises(DecimalGridError):
            parse_percent("37.5%")

    def test_percent_out_of_range(self):
        with self.assertRaises(DecimalGridError):
            parse_percent("120%")

    def test_percent_not_number(self):
        with self.assertRaises(DecimalGridError):
            parse_percent("abc%")

    def test_percent_empty(self):
        with self.assertRaises(DecimalGridError):
            parse_percent("")


class ProblemTest(unittest.TestCase):
    def test_read_prompt(self):
        problem = GridProblem(37, "read")
        self.assertIn("小数和百分数", problem.prompt)
        self.assertEqual(problem.answer, "0.37，37%")

    def test_shade_prompt(self):
        problem = GridProblem(37, "shade")
        self.assertIn("0.37", problem.prompt)
        self.assertEqual(problem.answer, "涂 37 格")

    def test_convert_prompt(self):
        problem = GridProblem(50, "convert")
        self.assertIn("0.50", problem.prompt)
        self.assertEqual(problem.answer, "50%，1/2")

    def test_bad_kind(self):
        with self.assertRaises(DecimalGridError):
            GridProblem(50, "guess")

    def test_out_of_range(self):
        with self.assertRaises(DecimalGridError):
            GridProblem(101, "read")

    def test_frozen(self):
        with self.assertRaises(FrozenInstanceError):
            GridProblem(50, "read").hundredths = 60


class GenerationTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(generate_problems(8, seed=1)), 8)

    def test_deterministic(self):
        self.assertEqual(generate_problems(6, seed=3), generate_problems(6, seed=3))

    def test_unique(self):
        items = generate_problems(12, seed=2)
        keys = {(item.hundredths, item.kind) for item in items}
        self.assertEqual(len(keys), len(items))

    def test_range(self):
        for item in generate_problems(10, min_hundredths=20, max_hundredths=40, seed=4):
            self.assertGreaterEqual(item.hundredths, 20)
            self.assertLessEqual(item.hundredths, 40)

    def test_single_kind(self):
        for item in generate_problems(6, kinds=("shade",), seed=5):
            self.assertEqual(item.kind, "shade")

    def test_invalid_count(self):
        for bad in (0, -1, 2.5, True, "8"):
            with self.assertRaises(DecimalGridError):
                generate_problems(bad)

    def test_too_many(self):
        with self.assertRaises(DecimalGridError):
            generate_problems(41)

    def test_invalid_bounds(self):
        with self.assertRaises(DecimalGridError):
            generate_problems(2, min_hundredths=50, max_hundredths=20)
        with self.assertRaises(DecimalGridError):
            generate_problems(2, min_hundredths=-1)
        with self.assertRaises(DecimalGridError):
            generate_problems(2, max_hundredths=200)

    def test_empty_kinds(self):
        with self.assertRaises(DecimalGridError):
            generate_problems(2, kinds=())

    def test_unknown_kind(self):
        with self.assertRaises(DecimalGridError):
            generate_problems(2, kinds=("read", "guess"))

    def test_impossible(self):
        with self.assertRaises(DecimalGridError):
            generate_problems(5, min_hundredths=50, max_hundredths=50, kinds=("read",))

    def test_answers(self):
        for item in generate_problems(10, seed=7):
            self.assertTrue(item.answer)
            self.assertIn(item.kind, KINDS)


if __name__ == "__main__":
    unittest.main()
