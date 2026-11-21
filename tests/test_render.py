"""方格图与练习纸渲染测试。"""

import unittest

from decimalgrid.model import DecimalGridError, GridProblem
from decimalgrid.render import render_grid, render_worksheet


class GridTest(unittest.TestCase):
    def test_root(self):
        svg = render_grid()
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))
        self.assertIn("小数方格图", svg)

    def test_cell_count(self):
        self.assertEqual(render_grid(37).count("<rect"), 102)

    def test_shaded_count(self):
        self.assertEqual(render_grid(37).count('fill="#6b46c1"'), 37)

    def test_zero_shaded(self):
        self.assertEqual(render_grid(0).count('fill="#6b46c1"'), 0)

    def test_full_shaded(self):
        self.assertEqual(render_grid(100).count('fill="#6b46c1"'), 100)

    def test_custom_size(self):
        self.assertIn('width="300"', render_grid(20, size=300))

    def test_invalid_size(self):
        with self.assertRaises(DecimalGridError):
            render_grid(20, size=80)

    def test_invalid_shaded(self):
        with self.assertRaises(DecimalGridError):
            render_grid(101)

    def test_bool_shaded(self):
        with self.assertRaises(DecimalGridError):
            render_grid(True)


class WorksheetTest(unittest.TestCase):
    def setUp(self):
        self.problems = [
            GridProblem(37, "read"),
            GridProblem(50, "shade"),
            GridProblem(25, "convert"),
        ]

    def test_document(self):
        page = render_worksheet(self.problems)
        self.assertIn("<!DOCTYPE html>", page)
        self.assertIn("小数方格图练习", page)
        self.assertTrue(page.endswith("</html>"))

    def test_card_count(self):
        page = render_worksheet(self.problems)
        self.assertEqual(page.count('class="card"'), 3)

    def test_only_read_is_shaded(self):
        page = render_worksheet(self.problems)
        self.assertEqual(page.count('fill="#6b46c1"'), 37)

    def test_answers(self):
        page = render_worksheet(self.problems, answers=True)
        self.assertIn("参考答案", page)
        self.assertIn("0.37，37%", page)

    def test_no_answers(self):
        page = render_worksheet(self.problems)
        self.assertNotIn("参考答案", page)

    def test_custom_title(self):
        page = render_worksheet(self.problems, title="认识小数")
        self.assertIn("<title>认识小数</title>", page)

    def test_custom_size(self):
        page = render_worksheet(self.problems, size=180)
        self.assertIn('width="180"', page)

    def test_empty(self):
        with self.assertRaises(DecimalGridError):
            render_worksheet([])

    def test_bad_item(self):
        with self.assertRaises(DecimalGridError):
            render_worksheet([("37", "read")])

    def test_escaping(self):
        page = render_worksheet(self.problems, title="<i>小数</i>")
        self.assertNotIn("<i>小数</i>", page)
        self.assertIn("&lt;i&gt;", page)


if __name__ == "__main__":
    unittest.main()
