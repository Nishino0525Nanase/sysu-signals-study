"""Create the self-contained Chinese course digest from the same data as the app.

Requires Pandoc, XeLaTeX, Inkscape and Noto CJK. Original course videos are not
reproduced; all worked examples and explanations are independently composed.
"""
from pathlib import Path
import json,re,subprocess,os

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'android/build/course-digest'
BUILD.mkdir(parents=True,exist_ok=True)
guides=json.loads((ROOT/'content/study-guides.json').read_text())['guides']
sources={s['id']:s for s in json.loads((ROOT/'content/resources.json').read_text())['sources']}
parts=['''---
title: "中大信号研习室"
subtitle: "中文课程精讲整理"
author: "12篇章节精讲 · 完整例题 · 易错点与自检"
lang: zh-CN
toc-title: "章节导航"
---

\\newpage

# 怎么用这份整理

课程中与真题有关的方法已经整理成中文讲解。每章先给结论，再解释第一步怎么想、公式怎么来，随后完整计算例题，最后列出易错点、自检答案与对应练习。

时间紧时先读第4、7、9、10章，再回补第2、3、5章。先用开头的结论定位问题；看不懂的地方往下对照例题，不必为了找一个方法补看整门课程。

这些讲解依据可读取的课程文字稿或讲义组织，例题由本项目独立演算。只读到目录的视频不作为正文知识依据。来源放在每章末尾供核对。

网页包含所有对应题目的详细答案：https://nishino0525nanase.github.io/sysu-signals-study/#resources

个人备考整理，非中山大学官方课程或官方答案。
''']

def image(m):
    src=ROOT/'dist'/m[2]
    if src.suffix=='.svg':
        dst=BUILD/(src.stem+'.pdf')
        subprocess.run(['inkscape',str(src),'--export-type=pdf','--export-text-to-path','--export-filename='+str(dst)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    else:dst=src
    return f'![{m[1]}]({dst}){{width=95%}}'

for g in guides:
    name='补充专题' if g['chapter']=='S' else '第'+g['chapter']+'章'
    body=re.sub(r'!\[([^]]*)\]\((assets/[^()]+)\)',image,g['body'])
    # Shift body sections below the chapter heading.
    body=re.sub(r'(?m)^### ','## ',body)
    parts.extend(['\\newpage',f"# {name}　{g['title']}",g['summary'],
        '## 先记住这几条','\n'.join('- '+t for t in g['quickTakeaways']),body,
        '## 易错点','\n'.join('- '+t for t in g['pitfalls']),
        '## 读完立即自检','\n'.join(f'{i+1}. {t}' for i,t in enumerate(g['selfCheck'])),
        '## 对应练习','、'.join(g['practiceIds'])+'。网页点击对应题号即可打开逐步答案。',
        '**讲解依据：** '+'；'.join(f"[{sources[i]['title']}]({sources[i]['url']})" for i in g['sourceIds'])+'。'])
markdown='\n\n'.join(parts)
# Existing exercises occasionally contain Unicode superscripts in prose.
subtable=str.maketrans('₀₁₂₃₄₅₆₇₈₉ₖ','0123456789k')
suptable=str.maketrans({'⁻':'-','⁺':'+','ᵗ':'t','ⁿ':'n','²':'2','³':'3'})
def normalize(t,math):
    def wrap(tex):return tex if math else '$'+tex+'$'
    t=re.sub(r'([A-Za-zα-ωΑ-Ω]+)([₀₁₂₃₄₅₆₇₈₉ₖ]+)',lambda m:wrap(m[1]+'_{'+m[2].translate(subtable)+'}'),t)
    return re.sub(r'([A-Za-zα-ωΑ-Ω0-9]+|\([^()\n]+\))([⁻⁺ᵗⁿ²³]+)',lambda m:wrap(m[1]+'^{'+m[2].translate(suptable)+'}'),t)
markdown=''.join(normalize(t,t.startswith('$')) for t in re.split(r'(\$\$[\s\S]*?\$\$|\$[^$\n]+\$)',markdown))
md=BUILD/'course-digest.md';md.write_text(markdown)
header=BUILD/'header.tex';header.write_text(r'''
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{titlesec}
\definecolor{studygreen}{HTML}{285D50}
\definecolor{studygold}{HTML}{9A6A28}
\XeTeXlinebreaklocale "zh"
\XeTeXlinebreakskip=0pt plus 1pt
\setlength{\emergencystretch}{4em}
\setlength{\parskip}{5pt}
\allowdisplaybreaks
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\color{studygreen}中大信号研习室}
\fancyhead[R]{\small 中文课程精讲}
\fancyfoot[C]{\small\thepage}
\setlength{\headheight}{15pt}
\titleformat{\section}{\Large\bfseries\color{studygreen}}{}{0em}{}
\titleformat{\subsection}{\large\bfseries\color{studygold}}{}{0em}{}
\providecommand{\sinc}{\operatorname{sinc}}
\providecommand{\Sa}{\operatorname{Sa}}
\providecommand{\rect}{\operatorname{rect}}
\providecommand{\sgn}{\operatorname{sgn}}
''')
out=ROOT/'dist/downloads/course-digest.pdf';tmp=BUILD/'course-digest.pdf'
subprocess.run(['pandoc',str(md),'--standalone','--toc','--toc-depth=1','--pdf-engine=xelatex','--include-in-header='+str(header),
    '-V','documentclass=article','-V','fontsize=11pt','-V','papersize=a4',
    '-V','geometry:top=25mm,bottom=23mm,left=22mm,right=22mm',
    '-V','mainfont=Noto Serif CJK SC','-V','sansfont=Noto Sans CJK SC','-V','monofont=DejaVu Sans Mono',
    '-V','linestretch=1.22','-V','colorlinks=true','-V','linkcolor=studygreen','-o',str(tmp)],check=True)
outtmp=out.with_suffix('.pdf.tmp');outtmp.write_bytes(tmp.read_bytes());os.replace(outtmp,out)
print(json.dumps({'output':str(out),'bytes':out.stat().st_size,'chapters':len(guides)},ensure_ascii=False))
