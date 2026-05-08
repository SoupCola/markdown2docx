"""Generate a test DOCX with cross-references for figures, formulas, and bibliography."""
from pathlib import Path
from docx_formatter import create_document

paragraphs = [
    {"type": "heading_1", "text": "第一章 理论基础"},
    {"type": "body", "text": "本章介绍基本理论。如{fig:theory}所示，系统架构分为三层。"},
    {"type": "image", "path": "examples/image.png", "key": "fig:theory", "caption": "理论框架"},
    {"type": "body", "text": "爱因斯坦质能方程如下。"},
    {"type": "formula", "latex": "E = mc^2", "key": "formula:emc2"},
    {"type": "body", "text": "由公式{formula:emc2}可得，能量与质量成正比。"},
    {"type": "heading_1", "text": "第二章 实验设计"},
    {"type": "body", "text": "实验结果见{fig:result}。"},
    {"type": "image", "path": "examples/image.png", "key": "fig:result", "caption": "实验结果"},
    {"type": "formula", "latex": r"\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}", "key": "formula:quad"},
    {"type": "body", "text": "根据研究{ref:smith}和{ref:zhang}，实验数据与理论吻合。"},
]

references = [
    {"key": "ref:smith", "text": "Smith J. Deep Learning Applications. Nature, 2024, 12(3): 45-50."},
    {"key": "ref:zhang", "text": "张三. 机器学习导论[M]. 北京: 科学出版社, 2023."},
]

output = Path("examples/xref_test.docx")
template = Path("templates/thesis.yaml")
create_document(output, template, paragraphs, {}, references=references)
print(f"Generated: {output}")
