# docx_skill

将 Markdown 文件转换为格式化的 DOCX (Word) 文档，支持中文学术论文/报告排版规范，并提供论文工作流编排能力。

## 功能特性

### docx_formatter (文档转换)

- **标题层级** — 支持 H1/H2/H3 标题，自动应用中文字号（三号、小四等）
- **正文排版** — 首行缩进、行间距、段前段后间距
- **表格** — Markdown 表格自动转换，支持三线表样式
- **图片** — 自动插入图片，支持图表编号与题注
- **数学公式** — LaTeX 公式转为 Word OMML 公式，支持公式编号
- **参考文献** — 脚注式/编号式引文自动生成参考文献列表，支持交叉引用
- **模板系统** — 内置论文、学术文章、报告三套 YAML 模板，可从已有 DOCX 提取格式

### paper_workflow (论文编排)

- **配置驱动** — 使用 `thesis.config.yaml` 定义项目结构和构建参数
- **一键构建** — `build-docx` 命令消费现有产物生成最终 DOCX
- **全流程编排** — `full-build` 命令支持上游能力检查与协调
- **图片任务管理** — `make-figure` 命令扫描 markdown 中的图片声明，报告缺失图片并输出生成指令
- **内容生成集成** — 集成 bishe-guider skill，支持论文内容生成/润色/审查
- **完整性检查** — `full-build` 自动检查图片和章节完整性，缺失时给出明确提示

## 项目结构

```
docx_skill/
├── docx_formatter/               # 核心转换模块
│   ├── cli.py                    # docx_formatter CLI 入口
│   ├── pipeline.py               # 转换流水线
│   ├── md_parser.py              # Markdown 解析器
│   ├── config.py                 # YAML 模板配置
│   ├── templates/                # 内置模板
│   │   ├── thesis.yaml           # 毕业论文模板
│   │   ├── academic_paper.yaml   # 学术论文模板
│   │   └── report.yaml           # 企业报告模板
│   └── ...
├── paper_workflow/               # 论文工作流编排层
│   ├── cli.py                    # paper-workflow CLI 入口
│   ├── config.py                 # 配置加载与验证
│   ├── build.py                  # build-docx / full-build 实现
│   ├── figures.py                # make-figure 图片任务扫描
│   └── __main__.py               # python -m paper_workflow 支持
├── pyproject.toml                # 包定义与 CLI 入口
├── tests/                        # 测试用例
├── examples/                     # 示例文件
└── .claude/skills/               # Claude Skill 定义
    ├── markdown2docx             # 文档转换 skill
    ├── bishe-guider              # 论文写作指导 skill
    └── trellis-*                 # Trellis 工作流 skills
```

## 安装

```bash
pip install -e .
```

## 使用方法

### docx_formatter CLI

```bash
# 转换 markdown 到 docx
python -m docx_formatter convert chapter1.md chapter2.md -o paper.docx -t thesis
python -m docx_formatter convert *.md -o paper.docx -t thesis --override body.size=小四

# 格式化已有 docx
python -m docx_formatter format draft.docx -t thesis

# 安装后的命令行入口
docx-format convert chapter1.md -o paper.docx -t thesis
```

### paper-workflow CLI

```bash
# 使用配置文件构建
python -m paper_workflow build-docx -c thesis.config.yaml -r /path/to/project

# 完整工作流编排
python -m paper_workflow full-build -c thesis.config.yaml -r /path/to/project

# 扫描 markdown 中的图片任务并报告缺失
python -m paper_workflow make-figure -c thesis.config.yaml -r /path/to/project

# 安装后的命令行入口
paper-workflow build-docx -c thesis.config.yaml
paper-workflow make-figure -c thesis.config.yaml
```

### 声明图片生成任务

在 markdown 中使用 HTML 注释声明图片生成任务：

```markdown
<!-- figure:prompt="系统架构图，包含前端、后端、数据库三层" -->
![系统架构](assets/figures/architecture.png)

<!-- figure:prompt="数据处理流程图" -->
<!-- figure:drawio=dataflow.drawio -->
![数据流](assets/figures/dataflow.png)
```

### Python API

```python
from docx_formatter import create_from_markdown, format_document

# Markdown -> DOCX
create_from_markdown(
    output_path=Path("output.docx"),
    md_paths=[Path("chapter1.md"), Path("chapter2.md")],
    template_path=Path("templates/thesis.yaml"),
    overrides={"body.size": "小四"},
)
```

## 完整论文生产工作流

```
1. 配置项目
   └─ 创建 thesis.config.yaml 定义章节、图片、格式

2. 生成图片 (DrawIO MCP)
   ├─ 在 markdown 中声明图片任务
   ├─ 运行 make-figure 检查缺失
   └─ AI agent 调用 DrawIO MCP 生成图片

3. 生成内容 (bishe-guider)
   └─ AI agent 使用 bishe-guider 生成/润色章节

4. 构建文档 (docx_formatter)
   └─ 运行 full-build 生成完整 DOCX
```

### 示例

```bash
# 1. 检查图片任务
python -m paper_workflow make-figure -c thesis.config.yaml

# 2. AI agent 生成图片（调用 DrawIO MCP）

# 3. AI agent 生成章节（使用 bishe-guider）

# 4. 构建最终文档
python -m paper_workflow full-build -c thesis.config.yaml
```

## 论文项目结构

```text
my-thesis-project/
├─ thesis.config.yaml             # 项目配置
├─ content/                       # 论文正文
│  ├─ 01-intro.md
│  ├─ 02-related-work.md
│  └─ references.md
├─ assets/
│  ├─ figures/                    # 最终图片
│  └─ drawio/                     # 源文件
├─ refs/
│  ├─ papers/                     # 参考文献
│  └─ style-samples/              # 格式参考
├─ build/
│  └─ thesis.docx                 # 最终产物
└─ .paper-workflow/
   ├─ cache/
   └─ runs/
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
