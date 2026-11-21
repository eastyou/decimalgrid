# decimalgrid

[![CI](https://github.com/eastyou/decimalgrid/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/decimalgrid/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

把 10×10 方格图当作“1”，涂色格数就是百分位：涂色读数、按小数涂色、小数与百分数和最简分数互化，生成可打印的 A4 练习纸。

## 安装

```bash
pip install -e .
```

只需要 Python 3.9+，零第三方依赖。

## 用法

```bash
# 生成 8 道读数 / 涂色 / 互化混合练习，附答案
decimalgrid sheet --count 8 --answers -o sheet.html

# 只练读数，格数限定在 10–90
decimalgrid sheet --kinds read --min 10 --max 90 -o read.html

# 输出涂 37 格的方格图 SVG
decimalgrid grid 37 -o grid.svg

# 小数、百分数、分数互化
decimalgrid convert 0.75
# 小数：0.75
# 百分数：75%
# 最简分数：3/4
# 涂色格数：75
```

## 功能

- 10×10 方格图，涂色格数对应 0.00–1.00
- 读数题、涂色题、互化题三种题型
- 百分数转最简分数自动约分
- 小数与百分数输入校验，最多两位小数
- 题目去重、支持随机种子复现
- 输出 A4 打印样式，答案单独一页

## 测试

```bash
python -m unittest discover -s tests -v
```

## 许可

[MIT](LICENSE) © 2026 eastyou
