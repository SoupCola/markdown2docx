# markdown2docx

将 Markdown 文件转换为格式化的 DOCX (Word) 文档，特别支持中文学术论文/报告的排版规范。

## 功能特性

- **标题层级** — 支持 H1/H2/H3 标题，自动应用中文字号（三号、小四等）
- **正文排版** — 首行缩进、行间距、段前段后间距
- **表格** — Markdown 表格自动转换，支持三线表样式
- **图片** — 自动插入图片，支持图表编号与题注
- **数学公式** — LaTeX 公式转为 Word OMML 公式，支持公式编号
- **参考文献** — 脚注式/编号式引文自动生成参考文献列表，支持交叉引用
- **模板系统** — 内置论文、学术文章、报告三套 YAML 模板，可从已有 DOCX 提取格式

## 项目结构

```
markdown2docx/
├── run_markdown2docx.py          # CLI 入口
├── docx_formatter/               # 核心转换模块
│   ├── pipeline.py               # 转换流水线
│   ├── md_parser.py              # Markdown 解析器
│   ├── config.py                 # YAML 模板配置
│   ├── analyzer.py               # 内容分析
│   ├── styles.py                 # 样式管理
│   ├── headings.py               # 标题格式
│   ├── paragraphs.py             # 段落格式
│   ├── pages.py                  # 页面设置
│   ├── figures.py                # 图表处理
│   ├── formulas.py               # 公式转换
│   ├── numbering.py              # 编号列表
│   ├── references.py             # 参考文献与交叉引用
│   ├── format_extractor.py       # 从 DOCX 提取格式
│   └── utils.py                  # 工具函数
├── templates/                    # YAML 模板
│   ├── thesis.yaml               # 毕业论文模板
│   ├── academic_paper.yaml       # 学术论文模板
│   └── report.yaml               # 企业报告模板
├── tests/                        # 测试用例
├── examples/                     # 示例文件
└── requirements.txt
```

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python run_markdown2docx.py input.md output.docx
```

### 指定模板

```bash
python run_markdown2docx.py input.md output.docx \
  --template-path templates/thesis.yaml
```

### 从已有 DOCX 提取格式

```bash
python run_markdown2docx.py input.md output.docx \
  --template-path templates/thesis.yaml \
  --format-docx-path format-source.docx
```

### 作为 Python 模块使用

```python
from docx_formatter.pipeline import create_from_markdown

create_from_markdown(
    md_path="input.md",
    output_path="output.docx",
    template_path="templates/thesis.yaml",
)
```

## 支持的 Markdown 内容

```markdown
# 第一章 绪论

## 1.1 研究背景

正文段落内容。

| 项目 | 配置 | 说明 |
| --- | --- | --- |
| GPU | RTX 3060 | 用于推理 |

![系统架构图](./images/architecture.png)

$$E = mc^2$$

[^1]: 张三. 论文标题[J]. 期刊名, 2024.
```

## 模板说明

| 模板 | 适用场景 | 特点 |
| --- | --- | --- |
| `thesis.yaml` | 本科/硕士毕业论文 | 章节编号、居中 H1、三线表 |
| `academic_paper.yaml` | 学术期刊论文 | 连续编号、较窄页边距 |
| `report.yaml` | 企业/项目报告 | 左对齐 H1、连续图编号 |

## 依赖

- `python-docx` — Word 文档生成
- `PyYAML` — 模板配置解析
- `markdown-it-py` — Markdown 解析
- `latex2mathml` — LaTeX 转 MathML
- `mathml2omml` — MathML 转 Word OMML

## License

MIT
