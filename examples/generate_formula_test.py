"""Generate a comprehensive test DOCX with formulas and images."""
from pathlib import Path
from docx_formatter import create_document

paragraphs = [
    {"type": "heading_1", "text": "第一章 理论基础"},
    {"type": "body", "text": "本章介绍基本理论公式。爱因斯坦质能方程是物理学最著名的公式之一。"},
    {"type": "formula", "latex": "E = mc^2"},
    {"type": "body", "text": "一元二次方程的求根公式如下所示。"},
    {"type": "formula", "latex": r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}"},
    {"type": "heading_2", "text": "1.1 微积分基础"},
    {"type": "body", "text": "高斯积分是一个经典的结果。"},
    {"type": "formula", "latex": r"\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}"},
    {"type": "heading_1", "text": "第二章 实验设计"},
    {"type": "body", "text": "实验部分描述。以下是平方和公式。"},
    {"type": "formula", "latex": r"S = \sum_{i=1}^{n} x_i^2"},
    {"type": "body", "text": "实验结果如下图所示。"},
    {"type": "image", "path": "examples/image.png", "caption": "图 2-1 实验结果示意图"},
    {"type": "body", "text": "从图中可以看出，实验数据与理论预测吻合。"},
    {"type": "formula", "latex": r"C_{ij} = \sum_{k=1}^{n} A_{ik} B_{kj}"},
    {"type": "heading_1", "text": "第三章 数据分析"},
    {"type": "body", "text": "正态分布的概率密度函数。"},
    {"type": "formula", "latex": r"f(x) = \frac{1}{\sigma \sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}"},
    {"type": "body", "text": "贝叶斯定理是概率论的核心公式。"},
    {"type": "formula", "latex": r"P(A|B) = \frac{P(B|A) P(A)}{P(B)}"},
]

output = Path("examples/formula_test.docx")
template = Path("templates/thesis.yaml")
create_document(output, template, paragraphs, {})
print(f"Generated: {output}")
