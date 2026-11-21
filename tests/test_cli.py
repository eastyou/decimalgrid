"""命令行行为测试。"""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from decimalgrid.cli import main


def run(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(args)
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def test_help(self):
        with self.assertRaises(SystemExit) as ctx:
            main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_convert_decimal(self):
        code, out, _ = run(["convert", "0.75"])
        self.assertEqual(code, 0)
        self.assertIn("百分数：75%", out)
        self.assertIn("最简分数：3/4", out)

    def test_convert_percent(self):
        code, out, _ = run(["convert", "20%"])
        self.assertEqual(code, 0)
        self.assertIn("小数：0.20", out)
        self.assertIn("最简分数：1/5", out)

    def test_convert_invalid(self):
        code, _, err = run(["convert", "2.5"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_grid_stdout(self):
        code, out, _ = run(["grid", "37"])
        self.assertEqual(code, 0)
        self.assertIn("<svg", out)
        self.assertEqual(out.count('fill="#6b46c1"'), 37)

    def test_grid_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "grid.svg"
            code, out, _ = run(["grid", "12", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())
            self.assertIn("已写入", out)

    def test_grid_invalid(self):
        code, _, err = run(["grid", "120"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_sheet_stdout(self):
        code, out, _ = run(["sheet", "--count", "2", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)

    def test_sheet_answers(self):
        code, out, _ = run(["sheet", "--count", "2", "--seed", "2", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_sheet_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "sheet.html"
            code, _, _ = run(["sheet", "--count", "4", "--seed", "5", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertEqual(target.read_text(encoding="utf-8").count('class="card"'), 4)

    def test_sheet_bad_kind(self):
        code, _, err = run(["sheet", "--kinds", "read,guess"])
        self.assertEqual(code, 2)
        self.assertIn("题型", err)

    def test_sheet_empty_kind(self):
        code, _, err = run(["sheet", "--kinds", " , "])
        self.assertEqual(code, 2)
        self.assertIn("题型", err)

    def test_sheet_bad_range(self):
        code, _, err = run(["sheet", "--min", "50", "--max", "20"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_nested_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "a" / "sheet.html"
            code, _, _ = run(["sheet", "--count", "1", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()
