# DOCX 格式化 Skill 设计文档

## 概述

创建一个 Claude Code skill，用于对 docx 文档进行精确格式化。支持学术论文和通用办公文档场景，覆盖标题、正文、图表标题、页面设置等全部常见格式化需求。

**技术栈**：python-docx + PyYAML
**调用方式**：Claude 对话驱动

## 核心需求

1. **格式化已有文档**：读取已有 docx 文件，根据格式要求重新设置样式并保存
2. **创建新文档**：根据用户提供的内容和格式要求，从头生成新的 docx 文件
3. **双重配置方式**：
   - 对话描述：用户通过自然语言描述格式要求
   - 配置模板：使用 YAML 预设模板（毕业论文/学术论文/企业报告等）
   - 运行前交互确认最终格式设置

## 项目结构

```
docx_skill/
├── skill.md                    # Skill 定义文件
├── docx_formatter/             # Python 包
│   ├── __init__.py             # 包入口，暴露公共 API
│   ├── headings.py             # 标题样式处理
│   ├── paragraphs.py           # 正文段落格式
│   ├── figures.py              # 图表标题处理
│   ├── pages.py                # 页面设置
│   ├── styles.py               # 样式定义与注册
│   ├── analyzer.py             # 文档分析器
│   └── utils.py                # 工具函数
├── templates/
│   ├── thesis.yaml             # 毕业论文预设模板
│   ├── academic_paper.yaml     # 学术论文预设模板
│   └── report.yaml             # 企业报告预设模板
└── requirements.txt            # 依赖
```

## 模块详细设计

### 1. `headings.py` — 标题样式处理

处理一级到五级标题，每级可设置：

| 属性 | 说明 | 示例 |
|------|------|------|
| font_cn | 中文字体 | 黑体、宋体 |
| font_en | 西文字体 | Times New Roman, Arial |
| size | 字号（支持中国字号名和磅值） | 三号/16pt |
| bold | 是否加粗 | true/false |
| italic | 是否斜体 | true/false |
| align | 对齐方式 | center/left/justify |
| space_before | 段前间距 | 24pt |
| space_after | 段后间距 | 18pt |
| outline_level | 大纲级别 | 0-4 |

**实现要点**：
- 使用 python-docx 的 `document.styles` 创建/修改 Heading 1-5 样式
- 同时设置中文字体（`rPr.rFonts` 的 `w:eastAsia` 属性）和西文字体
- 字号使用 `shared.Pt()` 设置，需从中国字号名转换

### 2. `paragraphs.py` — 正文段落格式

| 属性 | 说明 | 示例 |
|------|------|------|
| font_cn | 中文字体 | 宋体 |
| font_en | 西文字体 | Times New Roman |
| size | 字号 | 小四/12pt |
| first_line_indent | 首行缩进 | 2字符/24pt |
| line_spacing | 行距 | 1.5倍/28pt固定 |
| line_spacing_rule | 行距规则 | multiple/at_least/exactly |
| space_before | 段前间距 | 0pt |
| space_after | 段后间距 | 0pt |
| align | 对齐方式 | justify/left |

**实现要点**：
- 首行缩进：`paragraph_format.first_line_indent`，支持"字符"单位（需根据字号换算磅值）
- 行距：通过 `paragraph_format.line_spacing` 和 `paragraph_format.line_spacing_rule` 控制
- 对已有文档：遍历所有段落，识别正文段落（排除标题、表格内容等），批量应用格式
- 区分 Normal 样式修改（影响全局）和逐段落修改（精确控制）

### 3. `figures.py` — 图表标题处理

**图题**：
- 格式："图 X-X 标题内容"
- 位置：图下方
- 字体/字号可配置

**表题**：
- 格式："表 X-X 标题内容"
- 位置：表上方
- 字体/字号可配置

**编号方式**：
- `chapter`：按章节编号（图1-1, 图2-1）
- `continuous`：全文连续编号（图1, 图2）

**表格样式**：
- 三线表支持（上下粗线 + 表头下细线）
- 可配置线宽

**实现要点**：
- 识别已有的图题/表题段落（通过正则匹配"图 X-X"、"表 X-X"模式）
- 重新编号时需遍历文档保持顺序
- 使用 python-docx 的表格 API 设置边框样式

### 4. `pages.py` — 页面设置

| 属性 | 说明 | 示例 |
|------|------|------|
| page_size | 纸张大小 | A4/Letter |
| margins | 页边距（上/下/左/右） | 2.54cm |
| header_content | 页眉内容 | "XX大学毕业论文" |
| header_font | 页眉字体 | 宋体 |
| header_size | 页眉字号 | 小五 |
| footer_content | 页脚内容 | 自定义文本 |
| page_number_position | 页码位置 | bottom_center |
| page_number_format | 页码格式 | arabic/roman |
| page_number_start | 页码起始编号 | 1 |
| different_first_page | 首页不同 | true/false |
| odd_even_different | 奇偶页不同 | true/false |

**实现要点**：
- 页边距使用 `shared.Cm()` 或 `shared.Inches()` 设置
- 页眉/页脚通过 `section.header`/`section.footer` 访问
- 页码通过 XML 操作插入（python-docx 不直接提供页码 API）
- 分节符处理：支持不同节使用不同页面设置

### 5. `styles.py` — 样式注册

职责：统一管理所有样式定义，将 YAML 配置映射为 python-docx 样式对象。

- `register_styles(document, config)`: 根据 YAML 配置注册所有样式
- `get_or_create_style(document, name, style_type)`: 获取或创建样式
- `apply_font(run, font_cn, font_en, size, bold, italic)`: 统一设置字体属性

**设计原则**：
- 所有样式集中注册，其他模块通过调用 styles 模块获取样式对象
- 避免各模块重复设置字体属性的代码

### 6. `analyzer.py` — 文档分析

读取已有 docx 文件，返回结构信息供 Claude 决策：

```python
def analyze(filepath) -> dict:
    return {
        "paragraphs": [
            {"index": 0, "text": "第一章 绪论", "style": "Heading 1", "font": "黑体"},
            {"index": 1, "text": "正文内容...", "style": "Normal", "font": "宋体"},
        ],
        "tables": [{"index": 0, "rows": 5, "cols": 3, "has_caption": true}],
        "images": [{"index": 0, "has_caption": false}],
        "sections": [{"page_size": "A4", "margins": {"top": 2.54}}],
        "total_paragraphs": 150,
        "headings_count": {"level_1": 3, "level_2": 8, "level_3": 5}
    }
```

### 7. `utils.py` — 工具函数

**中国字号与磅值转换表**：

| 字号名 | 磅值 |
|--------|------|
| 初号 | 42pt |
| 小初 | 36pt |
| 一号 | 26pt |
| 小一 | 24pt |
| 二号 | 22pt |
| 小二 | 18pt |
| 三号 | 16pt |
| 小三 | 15pt |
| 四号 | 14pt |
| 小四 | 12pt |
| 五号 | 10.5pt |
| 小五 | 9pt |
| 六号 | 7.5pt |
| 小六 | 6.5pt |
| 七号 | 5.5pt |

**单位转换**：
- `cn_size_to_pt(name)` → 磅值
- `chars_to_pt(chars, font_size_pt)` → 首行缩进磅值
- `parse_distance(value)` → 解析"2.54cm"/"1in"/"24pt"为 Emu

## YAML 配置模板格式

```yaml
name: "模板名称"
description: "模板描述"

page:
  size: A4                    # A4/Letter/等
  margins:
    top: 2.54cm
    bottom: 2.54cm
    left: 3.17cm
    right: 3.17cm
  header:
    content: "页眉文本"
    font_cn: "宋体"
    font_en: "Times New Roman"
    size: "小五"
  footer:
    content: ""               # 空则只显示页码
  page_number:
    position: bottom_center   # top_center/bottom_center/top_right/等
    format: arabic            # arabic/roman
    start: 1

headings:
  level_1:
    font_cn: "黑体"
    font_en: "Times New Roman"
    size: "三号"
    bold: true
    align: center
    space_before: 24pt
    space_after: 18pt
  level_2:
    font_cn: "黑体"
    font_en: "Times New Roman"
    size: "小三"
    bold: true
    align: left
    space_before: 13pt
    space_after: 13pt
  level_3:
    font_cn: "黑体"
    font_en: "Times New Roman"
    size: "四号"
    bold: true
    align: left
    space_before: 13pt
    space_after: 13pt

body:
  font_cn: "宋体"
  font_en: "Times New Roman"
  size: "小四"
  first_line_indent: 2chars
  line_spacing: 1.5lines
  line_spacing_rule: multiple
  align: justify
  space_before: 0pt
  space_after: 0pt

figures:
  caption_font_cn: "宋体"
  caption_font_en: "Times New Roman"
  caption_size: "五号"
  caption_bold: false
  figure_caption_position: below   # 图题在图下方
  table_caption_position: above    # 表题在表上方
  numbering: chapter               # chapter/continuous
  table_style: three_line          # three_line/none
```

## 交互流程设计

### 用户触发
用户通过对话描述需求，例如：
- "帮我把 `论文.docx` 按毕业论文格式排版"
- "把这个报告的一级标题设成黑体三号居中"
- "创建一个新文档，用企业报告模板"

### Claude 执行步骤

**Step 1：分析文档**
- 读取目标 docx 文件
- 调用 `analyzer.analyze()` 获取文档结构
- 向用户简要报告文档内容（段落数、标题数、图表数等）

**Step 2：确认格式要求**
提供三种选择：
- A) 选择预设模板（展示可用模板列表）
- B) 对话描述自定义格式
- C) 先选模板，再局部调整

**Step 3：展示确认清单**
将最终要应用的所有格式设置以表格形式列出，请用户确认：
```
即将应用的格式设置：
┌─────────┬──────────────────────────────┐
│ 项目     │ 设置                         │
├─────────┼──────────────────────────────┤
│ 纸张     │ A4                           │
│ 页边距   │ 上下2.54cm，左右3.17cm       │
│ 一级标题 │ 黑体 三号 加粗 居中           │
│ 二级标题 │ 黑体 小三 加粗 左对齐         │
│ 正文     │ 宋体 小四 首行缩进2字符 1.5倍 │
│ ...      │ ...                          │
└─────────┴──────────────────────────────┘
确认执行？(Y/n)
```

**Step 4：执行格式化**
- 按顺序调用各模块：pages → styles → headings → paragraphs → figures
- 保存到新文件（原文件名 + `_formatted.docx`），不覆盖原文件

**Step 5：报告结果**
- 输出文件路径
- 处理统计（修改了多少段落/标题/图表）
- 如有异常（如无法识别的段落样式）列出提醒用户手动检查

## 错误处理

- 文件不存在或无法读取：明确报错
- 非标准段落样式：记录并提醒用户，不强制修改
- python-docx 不支持的特性（如复杂页码格式）：通过 XML 操作补充
- 保存失败（如文件被占用）：提示关闭文件后重试

## 依赖

```
python-docx>=0.8.11
PyYAML>=6.0
```

## Skill 定义（skill.md 要点）

- 触发条件：用户要求格式化/创建/排版 docx 文件
- 职责：Claude 在 skill 指导下调用 Python 脚本处理文档
- 不直接修改原文件，始终输出新文件
- 每次执行前必须与用户确认格式设置
