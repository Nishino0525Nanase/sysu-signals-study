"""Export the reviewed textbook and original exercises with mathematical typesetting.

Requires Python 3, Pandoc, XeLaTeX, Inkscape, and Noto Serif/Sans CJK SC.
The website remains the canonical interactive edition; this PDF uses the same JSON.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "android/build/workbook"
BUILD.mkdir(parents=True, exist_ok=True)
catalog = json.loads((ROOT / "content/catalog.json").read_text())
assert len(catalog["oppenheim"]) == 40
assert all(q.get("solution") for q in catalog["oppenheim"])


def asset_path(name):
    name = Path(name).name
    path = ROOT / "dist/assets" / name
    if path.suffix.lower() == ".svg":
        destination = BUILD / (path.stem + ".pdf")
        subprocess.run(
            ["inkscape", str(path), "--export-type=pdf", "--export-text-to-path",
             "--export-filename=" + str(destination)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return destination
    return path


def fix_images(text):
    return re.sub(r"!\[([^]]*)\]\((?:assets/)?([^()]+)\)",
                  lambda m: f"![{m[1]}]({asset_path(m[2])}){{width=90%}}", text)


parts = ["""---
title: "中大信号研习室"
subtitle: "奥本海姆课后题与专项训练 · 逐步答案"
author: "40组所选课后题 · 22道迁移题 · 10道模拟题"
lang: zh-CN
toc-title: "题目导航"
---

\\newpage

# 使用说明

本册与网页共用逐题答案。每题依次给出必要已知、入手理由、逐步推导、关键结果及易错点。
奥本海姆部分按英文第二版的题号与已选小问组织，用中文简述题意；原始图形与完整上下文请对照教材。
推导为独立编写，题面存在条件歧义时分别说明成立范围。原创迁移和模拟题均给出完整题目与答案。

建议先独立计算，再逐行核对。卷积先画支撑交集；频谱先标尺度、幅度与边界；变换先写收敛域；初态题先区分零输入和零状态。

网页：https://nishino0525nanase.github.io/sysu-signals-study/
"""]

for heading, items in [
    ("奥本海姆第二版 · 所选课后题", catalog["oppenheim"]),
    ("原创专项迁移训练", [q for q in catalog["training"] if q["id"].startswith("E")]),
    ("原创模拟综合训练", [q for q in catalog["training"] if q["id"].startswith("M")]),
]:
    parts.extend(["\\newpage", "# " + heading])
    for q in items:
        parts.extend(["\\newpage", f"## {q['id']}　{q['title']}"])
        if q.get("scope"):
            parts.append("**原书范围：** " + q["scope"] + "。")
        parts.extend(["### 题意与已知", fix_images(q["statement"]),
                      "### 第一步为什么这样想", q["firstStep"],
                      "### 逐步解答", fix_images(q["solution"])])
        for f in q.get("figures", []):
            name = f if isinstance(f, str) else f.get("path") or f.get("file") or f.get("src")
            caption = "对应图解" if isinstance(f, str) else f.get("caption") or f.get("title") or "对应图解"
            parts.append(f"![{caption}]({asset_path(name)}){{width=95%}}")
        parts.extend(["### 关键结果", q["answer"]])
        if q.get("pitfalls"):
            parts.extend(["### 易错点与检查", "\n".join("- " + p for p in q["pitfalls"])])

markdown = "\n\n".join(parts)
subscripts = str.maketrans("₀₁₂₃₄₅₆₇₈₉ₖ", "0123456789k")
superscripts = str.maketrans({"⁻": "-", "⁺": "+", "ᵗ": "t", "ⁿ": "n", "²": "2", "³": "3"})


def normalize_unicode_math(text, inside_math=False):
    def sub(m):
        tex = m[1] + "_{" + m[2].translate(subscripts) + "}"
        return tex if inside_math else "$" + tex + "$"
    def sup(m):
        tex = m[1] + "^{" + m[2].translate(superscripts) + "}"
        return tex if inside_math else "$" + tex + "$"
    text = re.sub(r"([A-Za-zα-ωΑ-Ω]+)([₀₁₂₃₄₅₆₇₈₉ₖ]+)", sub, text)
    return re.sub(r"([A-Za-zα-ωΑ-Ω]+)([⁻⁺ᵗⁿ²³]+)", sup, text)


segments = re.split(r"(\$\$[\s\S]*?\$\$|\$[^$\n]+\$)", markdown)
markdown = "".join(normalize_unicode_math(part, part.startswith("$")) for part in segments)
# Solution subheadings stay below the enclosing exercise and section headings.
markdown = re.sub(r"(?m)^### (\d+[．.、].*)$", r"#### \1", markdown)
md_path = BUILD / "workbook.md"
md_path.write_text(markdown)
header = BUILD / "header.tex"
header.write_text(r"""
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{titlesec}
\definecolor{studygreen}{HTML}{285D50}
\definecolor{studygold}{HTML}{9A6A28}
\XeTeXlinebreaklocale "zh"
\XeTeXlinebreakskip=0pt plus 1pt
\setlength{\emergencystretch}{4em}
\setlength{\parskip}{5pt}
\setcounter{tocdepth}{2}
\allowdisplaybreaks
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\color{studygreen}中大信号研习室}
\fancyhead[R]{\small 课后与专项训练逐步答案}
\fancyfoot[C]{\small\thepage}
\setlength{\headheight}{15pt}
\titleformat{\section}{\Large\bfseries\color{studygreen}}{}{0em}{}
\titleformat{\subsection}{\large\bfseries\color{studygreen}}{}{0em}{}
\titleformat{\subsubsection}{\normalsize\bfseries\color{studygold}}{}{0em}{}
\providecommand{\sinc}{\operatorname{sinc}}
\providecommand{\Sa}{\operatorname{Sa}}
\providecommand{\rect}{\operatorname{rect}}
\providecommand{\sgn}{\operatorname{sgn}}
""")
output = ROOT / "dist/downloads/oppenheim-workbook.pdf"
subprocess.run([
    "pandoc", str(md_path), "--standalone", "--toc", "--toc-depth=2", "--pdf-engine=xelatex",
    "--resource-path=" + str(ROOT / "dist"), "--include-in-header=" + str(header),
    "-V", "documentclass=article", "-V", "fontsize=11pt",
    "-V", "papersize=a4",
    "-V", "geometry:top=25mm,bottom=23mm,left=22mm,right=22mm",
    "-V", "mainfont=Noto Serif CJK SC", "-V", "sansfont=Noto Sans CJK SC",
    "-V", "monofont=DejaVu Sans Mono", "-V", "linestretch=1.22",
    "-V", "colorlinks=true", "-V", "linkcolor=studygreen",
    "-o", str(output),
], check=True)
print(json.dumps({"output": str(output), "bytes": output.stat().st_size,
                  "textbook_groups": 40, "training": 32}, ensure_ascii=False))
