"""Export the same source-backed, colored revision cards used by the app."""
from pathlib import Path
import json,re,subprocess,os,io
from PIL import Image
import fitz

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'android/build/reference-handbook'
BUILD.mkdir(parents=True,exist_ok=True)
data=json.loads((ROOT/'content/reference-handbook.json').read_text())
references=json.loads((ROOT/'content/textbook-links.json').read_text())
originals={c['id']:c for c in references.get('handbookCards',[])}
concepts={c['id']:c for c in references['concepts']}
categories={'definition':('定义','1F5D9B'),'formula':('公式','6C41A5'),'property':('性质','087B7E'),'table':('变换表','946009'),'common':('常规解法','317247'),'special':('特殊技巧','AE3864')}
parts=['''---
title: "中大信号研习室"
subtitle: "教材原图 · 公式与方法速查"
author: "定义 / 傅里叶级数 / 变换表 / 性质 / 真题方法"
lang: zh-CN
toc-title: "速查目录"
---

\\newpage

# 阅读方式

每张卡保留上传中文版第二版的真实摘图，分别标出中文书页和PDF页。图下的公式、理解提示、记忆提示与方法路线由本项目独立整理，便于复习与迁移。

颜色同时配合文字标签：蓝色为定义，紫色为公式，青色为性质，金色为变换表，绿色为常规解法，玫红色为特殊技巧。适用条件与易错点单独标出。

原书截图保持原文；清晰排版的公式便于手机查阅。公式必须连同适用条件使用，特别留意连续与离散频率、双边与单边变换、冲激的分布含义及收敛域。

每卡末尾的题号链接可打开网页中的详细答案与多方法对照。离线APK也内置全部卡片与原图。

个人备考整理，非中山大学官方教材或官方答案。
''',data.get('notation','')]

def field(value):
    return '\n'.join('- '+s for s in value) if isinstance(value,list) else str(value or '')

def aid(title,value,color):
    if not value:return ''
    return '\\colorlet{aidcolor}{'+color+'}\n\n## '+title+'\n\n'+field(value)

def original_image(f):
    source=ROOT/'content'/f['path'];target=BUILD/(source.stem+'.png')
    buffer=io.BytesIO();Image.open(source).save(buffer,format='PNG');data=buffer.getvalue()
    Image.open(io.BytesIO(data)).verify()
    temporary=target.with_suffix('.png.tmp');temporary.write_bytes(data);os.replace(temporary,target)
    assert target.read_bytes()==data,'Original excerpt PNG write failed: '+str(target)
    caption=f"教材原文：{f['caption']}；中文书页{f['printPage']} / PDF第{f['pdfPage']}页"
    return f'![{caption}]({target}){{width=100% height=0.68\\textheight keepaspectratio=true}}'

for c in data['cards']:
    label,color=categories[c['category']]
    parts.extend(['\\newpage',f'\\definecolor{{cardcolor}}{{HTML}}{{{color}}}',f"# {c['title']}",f"**{label} · {'补充专题' if str(c['chapter'])=='S' else '第'+str(c['chapter'])+'章'} · {c['id']}**"])
    refs=[r for r in [originals.get(c['id']),*[concepts.get(i) for i in c.get('conceptIds',[])]] if r]
    for r in refs:
        parts.extend(['\\colorlet{aidcolor}{sourcegray}','## 教材原文摘图',r.get('section',c.get('section','教材相关基础'))])
        parts.extend(original_image(f) for f in r.get('excerpts',[]))
    parts.append(aid('关键关系' if c['category'] in ['common','special'] else '清晰公式 · 对照原文',c.get('formula'),'formulapurple'))
    for f in c.get('diagramPaths',[]):
        source=ROOT/'dist/assets'/Path(f).name;target=BUILD/(source.stem+'.pdf')
        if source.suffix=='.svg':
            subprocess.run(['inkscape',str(source),'--export-type=pdf','--export-text-to-path','--export-filename='+str(target)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        else:target=source
        parts.append(f'![中文辅助图：独立绘制，用于理解原书公式]({target}){{width=100% height=0.65\\textheight keepaspectratio=true}}')
    parts.extend([aid('逐步路线' if c['category'] in ['common','special'] else '怎么理解',c.get('explanation'),'definitionblue'),aid('第一步怎么想到' if c['category'] in ['common','special'] else '记忆提示',c.get('memory'),'methodgreen'),aid('适用条件',c.get('conditions'),'propertyteal'),aid('易错提醒',c.get('pitfalls'),'warningorange')])
    links=[]
    for i in c.get('exampleIds',[]):
        route=f'practice?kind=book&question={i}' if i.startswith('O') else f'papers?year={i[:4]}&question={i}&focus=methods'
        links.append(f'[{i}](https://nishino0525nanase.github.io/sysu-signals-study/#{route})')
    parts.extend([aid('对应例题',' · '.join(links),'methodgreen')])

markdown='\n\n'.join(parts)
# Pandoc math uses ASCII TeX rather than typographical subscripts.
markdown=markdown.replace('－','-').replace('‑','-')
subtable=str.maketrans('₀₁₂₃₄₅₆₇₈₉ₖ','0123456789k')
suptable=str.maketrans({'⁻':'-','⁺':'+','ᵗ':'t','ⁿ':'n','²':'2','³':'3'})
def normalize(t,math):
    def wrap(tex):return tex if math else '$'+tex+'$'
    t=re.sub(r'([A-Za-zα-ωΑ-Ω0-9]+)([₀₁₂₃₄₅₆₇₈₉ₖ]+)',lambda m:wrap(m[1]+'_{'+m[2].translate(subtable)+'}'),t)
    return re.sub(r'([A-Za-zα-ωΑ-Ω0-9]+|\([^()\n]+\))([⁻⁺ᵗⁿ²³]+)',lambda m:wrap(m[1]+'^{'+m[2].translate(suptable)+'}'),t)
markdown=''.join(normalize(t,t.startswith('$')) for t in re.split(r'(\$\$[\s\S]*?\$\$|\$[^$\n]+\$)',markdown))
md=BUILD/'reference-handbook.md';md.write_text(markdown)
header=BUILD/'header.tex';header.write_text(r'''
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{float}
\floatplacement{figure}{H}
\raggedbottom
\definecolor{cardcolor}{HTML}{285D50}
\definecolor{aidcolor}{HTML}{285D50}
\definecolor{sourcegray}{HTML}{45545E}
\definecolor{formulapurple}{HTML}{6C41A5}
\definecolor{definitionblue}{HTML}{1F5D9B}
\definecolor{methodgreen}{HTML}{317247}
\definecolor{propertyteal}{HTML}{087B7E}
\definecolor{warningorange}{HTML}{A64B1E}
\XeTeXlinebreaklocale "zh"
\XeTeXlinebreakskip=0pt plus 1pt
\setlength{\emergencystretch}{4em}
\setlength{\parskip}{5pt}
\allowdisplaybreaks
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small 中大信号研习室}
\fancyhead[R]{\small 公式与方法速查}
\fancyfoot[C]{\small\thepage}
\setlength{\headheight}{15pt}
\titleformat{\section}{\Large\bfseries\color{cardcolor}}{}{0em}{}[\color{cardcolor}\titlerule]
\titleformat{\subsection}{\large\bfseries\color{aidcolor}}{}{0em}{}
\providecommand{\sinc}{\operatorname{sinc}}
\providecommand{\Sa}{\operatorname{Sa}}
\providecommand{\rect}{\operatorname{rect}}
\providecommand{\sgn}{\operatorname{sgn}}
''')
out=ROOT/'dist/downloads/reference-handbook.pdf';tmp=BUILD/'reference-handbook.pdf'
for png in BUILD.glob('*.png'):
    with Image.open(png) as picture:picture.verify()
subprocess.run(['pandoc',str(md),'--standalone','--toc','--toc-depth=1','--pdf-engine=xelatex','--include-in-header='+str(header),'-V','documentclass=article','-V','fontsize=11pt','-V','papersize=a4','-V','geometry:top=25mm,bottom=23mm,left=21mm,right=21mm','-V','mainfont=Noto Serif CJK SC','-V','sansfont=Noto Sans CJK SC','-V','monofont=DejaVu Sans Mono','-V','linestretch=1.2','-V','colorlinks=true','-V','linkcolor=definitionblue','-o',str(tmp)],check=True)
with fitz.open(tmp) as document:assert len(document)>=len(data['cards']),'Incomplete handbook PDF'
temporary=out.with_suffix('.pdf.tmp');temporary.write_bytes(tmp.read_bytes());os.replace(temporary,out)
print(json.dumps({'output':str(out),'bytes':out.stat().st_size,'cards':len(data['cards'])},ensure_ascii=False))
