"""A short, source-checked reading guide, using the same text as the web app."""
from pathlib import Path
import json,re,subprocess,os
import fitz

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'android/build/textbook-condensed';BUILD.mkdir(parents=True,exist_ok=True)
data=json.loads((ROOT/'content/textbook-condensed.json').read_text())
parts=['''---
title: "奥本海姆《信号与系统》"
subtitle: "原书精读 · 中大备考精简版"
author: "中大信号研习室"
lang: zh-CN
toc-title: "提要目录"
---

\\newpage

# 先把主线读清楚

这份讲义按上传中文版第二版的11章正文、典型例题与章末小结逐页核对后整理，附正交投影补充。每章围绕核心概念、适用条件、题目第一步、小例子和易错点展开。它用于串起主线；完整原书、长表与逐题推导由文末链接按需回看。

''',data.get('readingAdvice',''),r'''
**连续与离散先分清。** 连续信号用$t$，连续角频率单位是rad/s；离散序列用$n$，数字角频率单位是rad/样本。同一个字母$\omega$在原书不同章可以有不同单位。采样连接两者时，先写$\Omega=\omega T_s$。

**变换式必须连同条件记。** 连续傅里叶逆变换有$1/(2\pi)$；级数系数分析有$1/T$或$1/N$；拉普拉斯与Z变换必须带收敛域。原点冲激、非零初态、复内积共轭与有限/无限回波，均不能因简写而删除。

**读完一章，就用章末两道题验证。** 先自己写第一步，再打开题内完整解析。书页指书上印刷页，PDF页包含前置页；正文均分别标明。

完整网页：https://nishino0525nanase.github.io/sysu-signals-study/#digest

个人备考整理，非学校官方答案；各章文字为独立归纳。
''']

def aid(title,value,color):
    if not value:return ''
    text='\n'.join('- '+v for v in value) if isinstance(value,list) else str(value)
    return '\\colorlet{aidcolor}{'+color+'}\n\n## '+title+'\n\n'+text

for c in data['chapters']:
    label='补充专题' if c['chapter']=='S' else '第'+c['chapter']+'章'
    parts.extend(['\\Needspace{9\\baselineskip}',f"# {label}　{c['title']}",f"**主线：** {c['coreIdea']}",aid('抓住这几条','','definitionblue')])
    for e in c['essentials']:
        parts.extend(['\\colorlet{aidcolor}{definitionblue}',f"## {e['title']}",e['explanation']])
        if e.get('formula'):parts.extend(['\\begingroup\\color{formulapurple}',e['formula'],'\\endgroup'])
    parts.append(aid('看到题目，先做什么','\n\n'.join('**'+s['trigger']+'：** '+s['action']for s in c['firstSteps']),'methodgreen'))
    parts.append(aid(c['miniExample']['title'],c['miniExample']['body'],'studygold'))
    parts.append(aid('这两处最容易混',c['pitfalls'],'warningorange'))
    parts.append('\\Needspace{6\\baselineskip}')
    parts.append(aid('检查是否理解',c['selfCheck']['question']+'\n\n**答案与理由：** '+c['selfCheck']['answer'],'propertyteal'))
    links=[]
    for i in c['examIds']:
        route=f'practice?kind=book&question={i}'if i.startswith('O')else f'papers?year={i[:4]}&question={i}'
        links.append(f'[{i}](https://nishino0525nanase.github.io/sysu-signals-study/#{route})')
    sources='；'.join(f"{s['label']}：书页{s['printFrom']}–{s['printTo']} / PDF{s['pdfFrom']}–{s['pdfTo']}" for s in c['sourceSpans'])
    parts.extend(['**用真题检验：** '+' · '.join(links),'\\begingroup\\small','**原书依据：** '+sources+'。','**按需回看：** '+'；'.join(f"[{b['label']}](https://nishino0525nanase.github.io/sysu-signals-study/#book?pdf={b['pdfPage']})"for b in c['bookLinks'])+'。','\\endgroup'])

parts.extend(['\\newpage',r'''
# 附录一　先记母谱，再用性质生成

以下为本项目独立归纳；完整原表可从网页“公式速查”查阅。记号采用$\mathrm{Sa}(v)=\sin v/v$，端点按适当极限或分布意义解释。

## 连续傅里叶：零频面积和逆式系数先对齐

$$X(j\omega)=\int x(t)e^{-j\omega t}dt,\qquad x(t)=\frac1{2\pi}\int X(j\omega)e^{j\omega t}d\omega.$$

|时域母型|频域|先检查|
|---|---|---|
|$\delta(t)$|$1$|冲激面积为1|
|$1$|$2\pi\delta(\omega)$|按分布理解|
|$e^{-at}u(t)$|$1/(a+j\omega)$|$\Re a>0$|
|$\mathbf1_{\{\lvert t\rvert<T_1\}}$|$2\sin(\omega T_1)/\omega$|零频补值$2T_1$|
|$\sin(Wt)/(\pi t)$|$\mathbf1_{\{\lvert\omega\rvert<W\}}$|$W>0$；时域原点补$W/\pi$|
|$\cos(\omega_0t)$|$\pi[\delta(\omega-\omega_0)+\delta(\omega+\omega_0)]$|谱线画面积|
|$u(t)$|$\operatorname{PV}\frac1{j\omega}+\pi\delta(\omega)$|不能漏零频冲激|

**性质选路：** 时移乘负相位，调制搬频谱；时间压缩，频谱展宽且幅度除$|a|$。时域卷积变乘积，时域相乘变频域卷积并乘$1/(2\pi)$。对偶同时带$2\pi$和反转。能量满足$\int|x|^2dt=(1/2\pi)\int|X|^2d\omega$。

## 离散傅里叶：频率连续，频谱按2π重复

$$X(e^{j\Omega})=\sum_nx[n]e^{-j\Omega n},\quad x[n]=\frac1{2\pi}\int_{-\pi}^{\pi}X(e^{j\Omega})e^{j\Omega n}d\Omega.$$

|序列母型|DTFT|先检查|
|---|---|---|
|$\delta[n]$|$1$|整数索引|
|$1$|$2\pi\sum_k\delta(\Omega-2\pi k)$|周期分布|
|$a^nu[n]$|$1/(1-ae^{-j\Omega})$|$\lvert a\rvert<1$|
|$x[n]=1$于$0\le n<L$，其他0|$e^{-j\Omega(L-1)/2}\sin(L\Omega/2)/\sin(\Omega/2)$|$L$是样本数；$2\pi k$处补$L$|

**系数不要混：** 采用未归一化正向DFT时，$X_{\rm DFT}[k]=N a_k$，这里$a_k$是N周期DFS系数；周期序列的DTFT谱线面积是$2\pi a_k$。DFT关系为本项目补充归纳，不冒称原书另有DFT专章。

## 拉普拉斯与Z：同一个分式可以有不同信号

$$\frac1{s-a}\leftrightarrow\begin{cases}e^{at}u(t),&\Re s>\Re a,\\-e^{at}u(-t),&\Re s<\Re a;\end{cases}$$
$$\frac1{1-az^{-1}}\leftrightarrow\begin{cases}a^nu[n],&|z|>|a|,\\-a^nu[-n-1],&|z|<|a|,\end{cases}\qquad a\ne0.$$

**稳定与频响：** 双边ROC含虚轴或单位圆时，可以安全取相应傅里叶变换。适当有理因果系统的极点须分别在开左半平面或单位圆内，才BIBO稳定；约分后的外部稳定不自动保证内部模态稳定。单边变换必须带原题给定初态。
'''])

parts.extend(['\\Needspace{12\\baselineskip}','# 附录二　三张图串起时频与系统'])
figures=[('handbook-ctft-rect-sinc.svg','矩形与Sa：时域宽度、零频面积与零点位置一起记'),('handbook-sampling-spectra.svg','抽样复制：先画边缘，再叠加幅值；重叠部分相加'),('handbook-roc-compare.svg','相同代数式的不同ROC：稳定与因果要分开判断')]
for name,caption in figures:
    source=ROOT/'content/assets'/name;dest=BUILD/(source.stem+'.pdf')
    subprocess.run(['inkscape',str(source),'--export-type=pdf','--export-text-to-path','--export-filename='+str(dest)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    parts.extend([f'## {caption}',f'![中文图解 · 本项目独立绘制]({dest}){{width=100% height=0.43\\textheight keepaspectratio=true}}'])

parts.extend(['\\newpage',r'''
# 附录三　真题第一步清单

|题面触发|第一步|写完后检查|
|---|---|---|
|判断线性、时不变、因果等|每项独立代定义；时不变画两条延时路径|反例输入是否合法、是否覆盖全时间|
|卷积含阶跃、门函数|先把两段支撑相交，得到积分或求和区间|首个非零点、离散项数|
|求复杂波形频谱|先识母谱；折线/跳跃可先求分布导数|尺度、相位、零频冲激|
|周期输入通过LTI|先定共同频率网格，再逐根乘频响|级数系数与冲激面积、采样归一化|
|多级抽样、调制、恢复|按每一级列关系，标副本中心与边缘|幅度是相加、低通增益是否遗漏|
|题给非零初态或同初态实验|先拆零输入/零状态；同初态相减消初态项|初态只加一次，左右初值不混|
|逆拉氏/Z变换|先因式分解与ROC，再给各项选左右边|分子z与1、原点与无穷远|
|反馈结构或参数稳定|给内部量命名，按求和节点消元|边界、约分与内部模态|
|最小误差、正交展开|先写残差与所选基正交|基是否归一、复内积是否共轭|

**作答顺序：** 定义与条件 → 选择域/母型 → 列第一条关键式 → 推导 → 用边界、首样值、能量或数量级核对。独立解法、等价视角与核验法在题内分别标注，不必为“多一种方法”重复同一推导。

**对应工具：**

- 精读与题目互链：https://nishino0525nanase.github.io/sysu-signals-study/#digest
- 原书与完整目录：https://nishino0525nanase.github.io/sysu-signals-study/#book
- 原书变换表与方法卡：https://nishino0525nanase.github.io/sysu-signals-study/#reference
'''])

markdown='\n\n'.join(parts).replace('‑','-').replace('－','-')
subtable=str.maketrans('₀₁₂₃₄₅₆₇₈₉ₖ','0123456789k');suptable=str.maketrans({'⁻':'-','⁺':'+','ᵗ':'t','ⁿ':'n','²':'2','³':'3'})
def normalize(t,math):
    def wrap(tex):return tex if math else '$'+tex+'$'
    t=re.sub(r'([A-Za-zα-ωΑ-Ω0-9]+)([₀₁₂₃₄₅₆₇₈₉ₖ]+)',lambda m:wrap(m[1]+'_{'+m[2].translate(subtable)+'}'),t)
    return re.sub(r'([A-Za-zα-ωΑ-Ω0-9]+|\([^()\n]+\))([⁻⁺ᵗⁿ²³]+)',lambda m:wrap(m[1]+'^{'+m[2].translate(suptable)+'}'),t)
markdown=''.join(normalize(t,t.startswith('$'))for t in re.split(r'(\$\$[\s\S]*?\$\$|\$[^$\n]+\$)',markdown))
mdfile=BUILD/'textbook-condensed.md';mdfile.write_text(markdown)
header=BUILD/'header.tex';header.write_text(r'''
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{needspace}
\usepackage{float}
\floatplacement{figure}{H}
\raggedbottom
\definecolor{studygreen}{HTML}{285D50}
\definecolor{definitionblue}{HTML}{1F5D9B}
\definecolor{formulapurple}{HTML}{6C41A5}
\definecolor{methodgreen}{HTML}{317247}
\definecolor{propertyteal}{HTML}{087B7E}
\definecolor{warningorange}{HTML}{A64B1E}
\definecolor{studygold}{HTML}{946009}
\colorlet{aidcolor}{definitionblue}
\XeTeXlinebreaklocale "zh"
\XeTeXlinebreakskip=0pt plus 1pt
\setlength{\emergencystretch}{4em}
\setlength{\parskip}{4pt}
\allowdisplaybreaks
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\color{studygreen}中大信号研习室}
\fancyhead[R]{\small 原书精读精简版}
\fancyfoot[C]{\small\thepage}
\setlength{\headheight}{15pt}
\titleformat{\section}{\Large\bfseries\color{studygreen}}{}{0em}{}
\titleformat{\subsection}{\normalsize\bfseries\color{aidcolor}}{}{0em}{}
\titlespacing*{\section}{0pt}{18pt}{10pt}
\titlespacing*{\subsection}{0pt}{10pt}{5pt}
\providecommand{\sinc}{\operatorname{sinc}}
\providecommand{\Sa}{\operatorname{Sa}}
\providecommand{\rect}{\operatorname{rect}}
\providecommand{\sgn}{\operatorname{sgn}}
''')
temporary=BUILD/'textbook-condensed.pdf';output=ROOT/'dist/downloads/textbook-condensed.pdf'
subprocess.run(['pandoc',str(mdfile),'--standalone','--toc','--toc-depth=1','--pdf-engine=xelatex','--include-in-header='+str(header),'-V','documentclass=article','-V','fontsize=12pt','-V','papersize=a4','-V','geometry:top=23mm,bottom=22mm,left=20mm,right=20mm','-V','mainfont=Noto Serif CJK SC','-V','sansfont=Noto Sans CJK SC','-V','monofont=DejaVu Sans Mono','-V','linestretch=1.16','-V','colorlinks=true','-V','linkcolor=studygreen','-o',str(temporary)],check=True)
with fitz.open(temporary)as document:count=len(document);assert count>=12
destination=output.with_suffix('.pdf.tmp');destination.write_bytes(temporary.read_bytes());os.replace(destination,output)
print(json.dumps({'output':str(output),'pages':count,'bytes':output.stat().st_size,'chapters':len(data['chapters'])},ensure_ascii=False))
