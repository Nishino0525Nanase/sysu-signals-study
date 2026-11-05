"""Rebuild the original-gain and unit-gain comparison for textbook 8.23."""
from pathlib import Path
import io,os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({'font.family':'Noto Sans CJK SC','axes.unicode_minus':False,'svg.fonttype':'none','font.size':11})
out=Path(__file__).resolve().parents[1]/'content/assets'
w=np.linspace(-1.6,1.6,2401);d=.3
triangle=lambda z:np.maximum(1-np.abs(z),0)
for gain,name in [(2,'oppenheim-o32-gain2.svg'),(1,'enhanced-e-o32-frequency-offset.svg')]:
    factor=gain/4;l=factor*triangle(w-d);r=factor*triangle(w+d);total=l+r
    fig,axes=plt.subplots(2,1,figsize=(10.5,6.5),sharex=True,constrained_layout=True)
    color=['#327767','#ac6d25']
    denominator='2' if gain==2 else '4'
    axes[0].plot(w,l,color=color[0],lw=2,label=rf'右移谱 $X(j(\omega-\Delta\omega))/{denominator}$')
    axes[0].plot(w,r,color=color[1],lw=2,label=rf'左移谱 $X(j(\omega+\Delta\omega))/{denominator}$')
    label='原题：图8.8低通增益为2' if gain==2 else '单位增益对照变式（原题增益为2）'
    axes[0].set_title('8.23｜'+label,loc='left');axes[0].set_ylabel('两份移频分量');axes[0].legend(frameon=False,fontsize=10)
    axes[1].plot(w,total,color=color[0],lw=2.5);axes[1].fill_between(w,total,color=color[0],alpha=.14)
    axes[1].set_ylabel('相加后的输出频谱');axes[1].set_xlabel(r'归一化角频率 $\omega/\omega_M$')
    plateau=gain*.35;axes[1].annotate(f'中央平台高 {plateau:g}',xy=(0,plateau),xytext=(.4,plateau*1.25),arrowprops={'arrowstyle':'->','color':color[0]})
    for ax in axes:ax.grid(alpha=.14);ax.set_xlim(-1.6,1.6);ax.set_ylim(-.02,gain*.54);ax.set_yticks([0,gain*.25,gain*.35,gain*.5]);ax.axhline(0,color='#798b85',lw=.7)
    axes[1].set_xticks([-1.3,-1,-.7,-.3,0,.3,.7,1,1.3])
    buffer=io.BytesIO();fig.savefig(buffer,format='svg');plt.close(fig)
    p=out/name;t=p.with_suffix('.svg.tmp');t.write_text('\n'.join(line.rstrip() for line in buffer.getvalue().decode().splitlines())+'\n');os.replace(t,p)
print('Rebuilt gain-2 original and gain-1 comparison with Chinese labels')
