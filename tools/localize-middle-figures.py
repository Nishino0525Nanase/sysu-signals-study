"""Rebuild 2017–2019 original plots with Chinese text, then localize 2020–2022 SVG labels.

Curves, coordinates, and mathematical parameters follow the reviewed original assets.
Requires matplotlib, numpy, lxml, fontconfig, and Noto Sans CJK SC.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import subprocess
font_manager.fontManager.addfont(subprocess.check_output(['fc-match','Noto Sans CJK SC','-f','%{file}']).decode())
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'content/assets'
import io, os
from lxml import etree

def save_svg(fig, name):
    buffer=io.StringIO()
    fig.savefig(buffer,format='svg',bbox_inches='tight')
    payload=buffer.getvalue().encode('utf-8')
    etree.fromstring(payload)
    destination=P/name
    temporary=destination.with_name(destination.name+'.partial')
    temporary.write_bytes(payload)
    os.replace(temporary,destination)
    etree.parse(str(destination))

plt.rcParams.update({'font.family':'Noto Sans CJK SC','font.size':11,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#fffdf8','axes.facecolor':'#fffdf8','axes.prop_cycle':plt.cycler(color=['#126b77','#cb6542','#6354a3'])})
def finish(fig,name):
 
 for axis in fig.axes:
  if len(axis.get_xticks())>10:axis.tick_params(axis='x',labelrotation=40)
 fig.tight_layout(pad=1.7);save_svg(fig,name);plt.close(fig)
def base(ax,title,xlabel=r'归一化角频率 $\omega/\pi$'):
 ax.set_title(title,loc='left',fontweight='bold',fontsize=12);ax.axhline(0,c='#999',lw=.65);ax.axvline(0,c='#aaa',lw=.65);ax.set_xlabel(xlabel);ax.grid(alpha=.15)
def stems(ax,x,y,color='#126b77',label=None):
 ax.vlines(x,0,y,color=color,lw=2,label=label);ax.plot(x,y,'^',ms=6,color=color)

t=np.linspace(-.4,2.5,1400)
fig,axs=plt.subplots(3,1,figsize=(9,7.8))
base(axs[0],r'$h(t)=u(t)-u(t-1)$','时间 $t$');axs[0].plot([-.4,0,0,1,1,2.5],[0,0,1,1,0,0]);axs[0].set_xticks([0,1,2]);axs[0].set_yticks([0,1])
base(axs[1],r'$s(t)=t\ (0<t<1),\quad s(t)=1\ (t\geq1)$','时间 $t$');axs[1].plot(t,np.clip(t,0,1));axs[1].set_xticks([0,1,2]);axs[1].set_yticks([0,1])
y=np.where((t>=0)&(t<=1),(1-np.cos(np.pi*t))/np.pi,np.where((t>1)&(t<=2),(1+np.cos(np.pi*(t-1)))/np.pi,0))
base(axs[2],r'$y_1(t)$: 有限半正弦通过宽度为1的积分窗口','时间 $t$');axs[2].plot(t,y);axs[2].set_xticks([0,1,2]);axs[2].set_yticks([0,2/np.pi],[r'$0$',r'$2/\pi$']);finish(fig,'2017_q3_waveforms.svg')

v=np.linspace(-8*np.pi,8*np.pi,10001);d=np.pi*np.pi-v*v;X=np.divide(2*np.pi*np.cos(v/2),d,out=np.full_like(v,.5),where=np.abs(d)>1e-8)
fig,axs=plt.subplots(3,1,figsize=(10,8),sharex=True)
for ax in axs:base(ax,'',r'归一化角频率 $\omega\tau/\pi$');ax.set_xticks(np.arange(-8,9))
axs[0].set_title('保留正负号的实数频谱',loc='left',fontweight='bold');axs[0].plot(v/np.pi,X);axs[0].set_ylabel(r'$X/\tau$');axs[0].scatter([-1,1],[.5,.5],c='#cb6542',zorder=5);axs[0].annotate(r'$X(\pm\pi/\tau)=\tau/2$',(1,.5),(2,.5),arrowprops={'arrowstyle':'->'})
axs[1].set_title('幅度',loc='left',fontweight='bold');axs[1].plot(v/np.pi,abs(X));axs[1].set_ylabel(r'$|X|/\tau$')
phase=np.where(X>=0,0,np.pi);phase[np.abs(X)<1e-5]=np.nan
axs[2].set_title('相位（真实零点处无定义）',loc='left',fontweight='bold');axs[2].plot(v/np.pi,phase);axs[2].set_yticks([0,np.pi],['0',r'$\pi$']);finish(fig,'2017_q4_spectrum.svg')

w=np.linspace(-3,3,6001);band=(abs(w)>1.75)&(abs(w)<2.25)
fig,axs=plt.subplots(4,1,figsize=(10,10),sharex=True)
base(axs[0],r'$|H|$: 两个通带，通带增益为1');axs[0].plot(w,band*1.);axs[0].set_yticks([0,1])
phase=np.full_like(w,np.nan);phase[(w>1.75)&(w<2.25)]=-np.pi*(w[(w>1.75)&(w<2.25)]-2)/2;phase[(w>-2.25)&(w<-1.75)]=-np.pi*(w[(w>-2.25)&(w<-1.75)]+2)/2
base(axs[1],r'$\arg H$: 相对各通带中心的延时为 $1/2$');axs[1].plot(w,phase);axs[1].set_yticks([-np.pi/8,0,np.pi/8],[r'$-\pi/8$','0',r'$\pi/8$'])
base(axs[2],r'第（3）问： $X(j\omega)$');axs[2].plot(w,.5*((abs(w-2)<.5)|(abs(w+2)<.5)));axs[2].set_yticks([0,.5])
base(axs[3],r'第（4）问： $\operatorname{Im}Y(j\omega)=-\frac{1}{2}\operatorname{sgn}\omega$，适用范围 $|\omega|<\pi/2$');axs[3].plot(w,np.where(abs(w)<.5,-.5*np.sign(w),0));axs[3].set_yticks([-.5,0,.5]);axs[3].set_xticks([-2.5,-2.25,-2,-1.75,-1.5,-.5,0,.5,1.5,1.75,2,2.25,2.5]);finish(fig,'2017_q5_sampling.svg')

w=np.linspace(-np.pi,np.pi,1500)
fig,ax=plt.subplots(figsize=(9,4));base(ax,r'幅频响应：$|H_1(e^{j\omega})|=(5/4-\cos\omega)^{-1/2}$');ax.plot(w/np.pi,1/np.sqrt(1.25-np.cos(w)));ax.set_xticks([-1,-.5,0,.5,1]);ax.set_yticks([2/3,1,2],[r'$2/3$','1','2']);finish(fig,'2017_q7_magnitude.svg')

def poles(ax,ps,zs,title,lim):
 base(ax,title,r'实部 $\operatorname{Re}s$');ax.set_ylabel(r'虚部 $\operatorname{Im}s$');ax.scatter([complex(p).real for p in ps],[complex(p).imag for p in ps],marker='x',s=100,lw=2,label='极点');ax.scatter([complex(z).real for z in zs],[complex(z).imag for z in zs],facecolors='none',edgecolors='#cb6542',s=100,lw=2,label='零点');ax.set_xlim(*lim);ax.legend();ax.set_ylim(-2,2)
fig,ax=plt.subplots(figsize=(8,4));poles(ax,[-2,2],[1.5],'因果系统：存在一个右半平面极点',(-3,3));ax.set_xticks([-2,0,1.5,2]);finish(fig,'2017_q8_poles.svg')

fig,axs=plt.subplots(6,1,figsize=(11,14))
for ax in axs:ax.set_xlim(-6,6);ax.set_xticks(np.arange(-6,7));ax.set_ylim(-1.35,2.6);base(ax,'',r'角频率 $\omega$（弧度/秒）')
axs[0].set_title(r'$F_1$: 冲激虚部权重除以 $\pi$',loc='left');stems(axs[0],[-1,1],[-1,1]);axs[0].set_ylabel(r'$\operatorname{Im} F_1/\pi$')
axs[1].set_title(r'$Y_1$: 冲激实部权重除以 $\pi$',loc='left');stems(axs[1],[-5,-3,3,5],[.5]*4)
axs[2].set_title(r'$Y_2$: 冲激实部权重除以 $\pi$',loc='left');stems(axs[2],[-5,-3,3,5],[.5,-.5,-.5,.5])
axs[3].set_title(r'$Y$: 冲激实部权重除以 $\pi$',loc='left');stems(axs[3],[-5,5],[1,1])
axs[4].set_title(r'$Y_s$: 实际冲激权重， $\omega_s=4$',loc='left');stems(axs[4],[-5,-3,-1,1,3,5],[2]*6)
axs[5].set_title(r'$Z$: 冲激实部权重除以 $\pi$',loc='left');stems(axs[5],[-1,1],[1,1]);axs[5].axvspan(-2,2,color='#126b77',alpha=.08);finish(fig,'2018_q3_spectra.svg')

fig,ax=plt.subplots(figsize=(10,4.5));base(ax,'两次交替调制使幅频响应平移 '+r'$\pi$');ax.plot(w/np.pi,1/np.sqrt(1.25-np.cos(w)),label=r'$|H_1|$：低通');ax.plot(w/np.pi,1/np.sqrt(1.25+np.cos(w)),label=r'$|H|$：高通');ax.set_xticks([-1,-.5,0,.5,1]);ax.set_yticks([2/3,1,2],[r'$2/3$','1','2']);ax.legend();finish(fig,'2018_q6_magnitude.svg')

fig,axs=plt.subplots(2,1,figsize=(10,8));a=axs[0];base(a,r'$|H(j\omega)|=10\sqrt{1+\omega^2}/|10000-\omega^2|$',r'$\omega$');
for lo,hi in [(-250,-100.05),(-99.95,99.95),(100.05,250)]:
 v=np.linspace(lo,hi,1800);a.semilogy(v,10*np.sqrt(1+v*v)/abs(10000-v*v),c='#126b77')
for x in [-100,100]:a.axvline(x,c='#cb6542',ls='--')
a.set_ylim(7e-4,1e2);a.set_xticks([-200,-100,0,100,200]);a.text(105,10,'无界共振',c='#cb6542');a=axs[1];t=np.linspace(0,.2,1800);base(a,'阶跃响应：持续振荡',r'时间 $t$（秒）');a.plot(t,.001*(1-np.cos(100*t))+.1*np.sin(100*t));finish(fig,'2018_q8_response.svg')

# 2019 Q6 continuous spectra and impulses are shown independently.
v=np.linspace(-180,180,18001)
def B(x):return 2*np.maximum(1-abs(x)/40,0)
x2=.5*(B(v-40)+B(v+40));x3=x2*(abs(v)<=60);r=(v+50)%100-50;q=np.where(abs(r)<40,abs(r)/40,1.5);g=np.where(abs(v)<=140,1,np.maximum((160-abs(v))/20,0))
fig,axs=plt.subplots(7,1,figsize=(13,18),sharex=True)
for ax in axs:base(ax,'',r'角频率 $\omega$（弧度/秒）');ax.set_xticks([-160,-140,-100,-80,-60,-50,-40,0,40,50,60,80,100,140,160]);ax.set_xlim(-180,180)
axs[0].set_title(r'$X_1$: 连续部分 $B$；原点冲激权重为 $2\pi$',loc='left');axs[0].plot(v,B(v));stems(axs[0],[0],[2.4],'#cb6542');axs[0].text(3,2.3,r'$2\pi\delta(\omega)$');axs[0].set_yticks([0,1,2]);axs[0].set_ylim(0,2.7)
axs[1].set_title(r'$X_2$: 连续部分；$\pm40$ 处冲激权重为 $\pi$',loc='left');axs[1].plot(v,x2);stems(axs[1],[-40,40],[1.3,1.3],'#cb6542');axs[1].set_yticks([0,.5,1]);axs[1].set_ylim(0,1.6)
axs[2].set_title(r'$X_3$: 在 $\pm60$ 处截断；冲激权重仍为 $\pi$',loc='left');axs[2].plot(v,x3);stems(axs[2],[-40,40],[1.3,1.3],'#cb6542');axs[2].set_yticks([0,.5,1]);axs[2].set_ylim(0,1.6)
axs[3].set_title(r'$X_4$ 连续部分除以 $50/\pi$：重叠副本相加为 $q$',loc='left');axs[3].plot(v,q);axs[3].set_yticks([0,1,1.5]);axs[3].set_ylim(0,1.8)
a=sorted(set([100*k+s for k in range(-3,4) for s in [-40,40] if -180<100*k+s<180]));axs[4].set_title(r'$X_4$ 各冲激权重均为50',loc='left');stems(axs[4],a,[50]*len(a));axs[4].set_yticks([0,50]);axs[4].set_ylim(0,65)
axs[5].set_title(r'$Y$ 连续部分除以 $50/\pi$： $g(\omega)q(\omega)$',loc='left');axs[5].plot(v,g*q);axs[5].plot(v,g,'--',c='#cb6542',label=r'$g=H_2$');axs[5].legend();axs[5].set_yticks([0,1,1.5]);axs[5].set_ylim(0,1.8)
axs[6].set_title(r'$Y$ 冲激：保留 $\pm40,\pm60,\pm140$，滤除 $\pm160$',loc='left');stems(axs[6],[-140,-60,-40,40,60,140],[50]*6);axs[6].set_yticks([0,50]);axs[6].set_ylim(0,65);finish(fig,'2019_q6_spectra.svg')

A=2*np.sqrt(2)/np.pi;C=A/5
fig,axs=plt.subplots(3,1,figsize=(11,9))
for ax in axs:base(ax,'',r'归一化角频率 / $\pi$');ax.set_xticks([-1.5,-1.25,-1,-.75,-.25,0,.25,.75,1,1.25,1.5]);ax.set_xlim(-1.55,1.55);ax.set_ylim(-.9,3.4)
axs[0].set_title(r'$X_1$: 实际傅里叶冲激系数；横坐标 $\Omega T/\pi$',loc='left');stems(axs[0],[-.25,.25],[np.pi*A]*2,label='实部权重');stems(axs[0],[-1.25,1.25],[-np.pi*C,np.pi*C],'#cb6542',label='虚部权重');axs[0].legend()
axs[1].set_title(r'$X_3(e^{j\omega})$: 一个周期；横坐标 $\omega/\pi$',loc='left');stems(axs[1],[-.25,.25],[np.pi*A]*2,label='实部权重');stems(axs[1],[-.75,.75],[np.pi*C,-np.pi*C],'#cb6542',label='虚部权重');axs[1].axvline(-1,c='#777',ls='--');axs[1].axvline(1,c='#777',ls='--');axs[1].legend()
axs[2].set_title(r'$X_5$: 增益 $T$ 恢复冲激系数；横坐标 $\Omega T/\pi$',loc='left');stems(axs[2],[-.25,.25],[np.pi*A]*2,label='实部权重');stems(axs[2],[-.75,.75],[np.pi*C,-np.pi*C],'#cb6542',label='虚部权重');axs[2].legend();finish(fig,'2019_q8_aliasing.svg')

fig,ax=plt.subplots(figsize=(9,4.5));poles(ax,[-1],[1],r'全通情形 $a=b=1$: $H(s)=(1-s)/(1+s)$',(-2.1,2.1));ax.set_xticks([-1,0,1]);ax.set_ylim(-1,1);finish(fig,'2019_q9_poles.svg')

# Direct-form realization for 2019 Q10, also including its pole-zero map.
fig,axs=plt.subplots(2,1,figsize=(12,9));ax=axs[0];ax.set_xlim(0,12);ax.set_ylim(-2.5,2);ax.axis('off');ax.set_title(r'直接Ⅱ型： $\dot v_1=x-5v_1-6v_2$, $\dot v_2=v_1$, $y=2v_1+v_2$',loc='left',fontweight='bold')
def arrow(a,b,label=None):
 ax.add_patch(FancyArrowPatch(a,b,arrowstyle='->',mutation_scale=12,color='#126b77',lw=1.7));
 if label:ax.text((a[0]+b[0])/2,(a[1]+b[1])/2+.13,label,ha='center')
def box(x,y,text):ax.add_patch(Rectangle((x,y),1.2,.75,fill=False,ec='#126b77',lw=1.8));ax.text(x+.6,y+.375,text,ha='center',va='center',fontsize=13)
ax.add_patch(Circle((2,.5),.22,fill=False,ec='#126b77',lw=1.8));ax.text(2,.5,'+',ha='center',va='center');arrow((.1,.5),(1.78,.5),'$x$');box(3,.125,r'$1/s$');arrow((2.22,.5),(3,.5));box(5.5,.125,r'$1/s$');arrow((4.2,.5),(5.5,.5),r'$v_1$');arrow((6.7,.5),(8,.5),r'$v_2$');ax.plot([4.8,4.8],[.5,-1],c='#126b77');ax.plot([4.8,1.6],[-1,-1],c='#126b77');arrow((1.6,-1),(1.87,.37));ax.text(3.4,-.9,'$-5$',ha='center');ax.plot([7.4,7.4],[.5,-2],c='#126b77');ax.plot([7.4,2],[-2,-2],c='#126b77');arrow((2,-2),(2,.28));ax.text(5,-1.9,'$-6$',ha='center');ax.add_patch(Circle((10,.5),.22,fill=False,ec='#126b77',lw=1.8));ax.text(10,.5,'+',ha='center',va='center');arrow((8,.5),(9.78,.5),'1');ax.plot([4.8,4.8],[.5,1.5],c='#126b77');ax.plot([4.8,10],[1.5,1.5],c='#126b77');arrow((10,1.5),(10,.72));ax.text(7,1.6,'2');arrow((10.22,.5),(11.8,.5),'$y$');poles(axs[1],[-2,-3],[-.5],'稳定因果系统：极点为−2、−3；零点为−1/2',(-4,1));axs[1].set_xticks([-3,-2,-.5,0]);finish(fig,'2019_q10_realization.svg')
print('Created',len(list(P.glob('2017*.svg')))+len(list(P.glob('2018*.svg')))+len(list(P.glob('2019*.svg'))),'figures')

def diagram(name,title,unit,feedback,feedforward,extra=None):
 fig,ax=plt.subplots(figsize=(12,6));ax.set_xlim(-.3,12);ax.set_ylim(-2.8,2.6);ax.axis('off');ax.set_title(title,loc='left',fontweight='bold',pad=10)
 def arrow(a,b):ax.add_patch(FancyArrowPatch(a,b,arrowstyle='->',mutation_scale=13,lw=1.8,color='#126b77'))
 def line(xs,ys):ax.plot(xs,ys,c='#126b77',lw=1.8)
 def summ(x,y):ax.add_patch(Circle((x,y),.19,fill=False,ec='#126b77',lw=1.7));ax.text(x,y,'+',ha='center',va='center',fontsize=14)
 def box(x,y,label):ax.add_patch(Rectangle((x,y),1.2,.7,fill=False,ec='#126b77',lw=1.8));ax.text(x+.6,y+.35,label,ha='center',va='center',fontsize=15)
 summ(2,0);arrow((0,0),(1.81,0));ax.text(.6,.16,'$x$',fontsize=14);arrow((2.19,0),(3,0));box(3,-.35,unit);arrow((4.2,0),(5.5,0));box(5.5,-.35,unit);arrow((6.7,0),(7.7,0));ax.text(2.55,.2,'$w$' if 'z' in unit else r'$\ddot q$',fontsize=13);ax.text(4.65,.2,'$w_1$' if 'z' in unit else '$v_1$',fontsize=13);ax.text(7,.2,'$w_2$' if 'z' in unit else '$v_2$',fontsize=13)
 line([4.7,4.7,1.65],[0,-1,-1]);arrow((1.65,-1),(1.87,-.13));ax.text(3.4,-.85,feedback[0],fontsize=14)
 line([7.2,7.2,2.05],[0,-2,-2]);arrow((2.05,-2),(2.01,-.19));ax.text(4.7,-1.85,feedback[1],fontsize=14)
 summ(10,0)
 # Independent output taps routed at three different vertical levels.
 if feedforward[0]!='0':
  line([2.6,2.6,10],[0,1.9,1.9]);arrow((10,1.9),(10,.19));ax.text(7.4,2.02,feedforward[0],fontsize=14)
 if feedforward[1]!='0':
  line([4.7,4.7,9],[0,1.05,1.05]);arrow((9,1.05),(9.88,.13));ax.text(6.8,1.18,feedforward[1],fontsize=14)
 if feedforward[2]!='0':
  arrow((7.7,0),(9.81,0));ax.text(8.5,.15,feedforward[2],fontsize=14)
 arrow((10.19,0),(11.8,0));ax.text(11,.16,'$y$',fontsize=14)
 if extra:fig.text(.12,.02,extra,fontsize=13)
 fig.tight_layout();save_svg(fig,name);plt.close(fig)
diagram('2018_q5_realization.svg','2018年第五题：最少两级延时的直接Ⅱ型',r'$z^{-1}$',['7','−10'],['6','−33','39'])
diagram('2019_q7_realization.svg','2019年第七题：最少两级延时的直接Ⅱ型',r'$z^{-1}$',[r'$7/12$',r'$-1/12$'],['−1',r'$5/12$','0'])
diagram('2018_q8_realization.svg',r'2018年第八题： $H(s)=10(s+1)/(s^2+10000)$',r'$1/s$',['0','−10000'],['0','10','10'],r'极点为 $s=\pm j100$，零点为 $s=-1$。无阻尼，故不满足有界输入有界输出稳定。')

# Later assets use editable SVG text, so geometry and paths stay byte-for-byte identical.
from lxml import etree
TRANSLATIONS = {
 '2020 Q10 · two-integrator realization':'2020年第十题：两积分器实现',
 'amplitude':'幅度',
 '2020 Q2 · step combination':'2020年第二题：阶跃信号组合',
 'a>b · two poles and two zeros before any cancellation':'a>b：约分前有两个极点和两个零点',
 'a<b · two poles and two zeros before any cancellation':'a<b：约分前有两个极点和两个零点',
 'a=b=τ · reduced allpass H(s)=(sτ−1)/(sτ+1)':'a=b=τ：约分后的全通系统 H(s)=(sτ−1)/(sτ+1)',
 '2020 Q3 · a=r₁C₂, b=r₂C₁; ○ zeros, × poles':'2020年第三题：a=r₁C₂，b=r₂C₁；○表示零点，×表示极点',
 'Symbolic real-axis order (spacing schematic)':'实轴上的符号次序（间距为示意）',
 '2020 Q7 · 4(1−cos 2t)/(πt)':'2020年第七题：4(1−cos 2t)/(πt)',
 'ω (rad/s)':'角频率 ω（弧度/秒）',
 'Cosine amplitudes':'余弦分量的幅度',
 'Two-sided |cₖ|':'双边复指数系数幅度 |cₖ|',
 'phase / π':'相位 / π',
 'Cosine phases':'余弦分量的相位',
 'Two-sided arg cₖ':'双边复指数系数相位 arg cₖ',
 'ν = ω/(2π) (Hz)':'频率 ν=ω/(2π)（赫兹）',
 '2020 Q9 · Ts=12.5 ms, fs=80 Hz: copies':'2020年第九题：Ts=12.5毫秒，fs=80赫兹的谱副本',
 'Summed sampled spectrum':'相加后的抽样频谱',
 'baseband overlap':'基带发生重叠',
 '2021 Q10 · direct form II: two delays':'2021年第十题：两级延时的直接Ⅱ型',
 'Re(z)':'实部 Re(z)',
 'Im(z)':'虚部 Im(z)',
 '2021 Q10 · ○ zero, × poles':'2021年第十题：○表示零点，×表示极点',
 'Magnitude':'幅度',
 'Principal phase':'主值相位',
 'Ts × spectrum':'频谱 × Ts',
 '2021 Q6 · a=π/Ts=3ωm: all odd-center copies':'2021年第六题：a=π/Ts=3ωm，奇数倍中心的全部副本',
 'Bandpass a<|ω|<3a cuts copies through their centers':'带通 a<|ω|<3a 从副本中心切开',
 '2021 Q7 · triangular gate spectral weights (FT weights = 2πcₖ)':'2021年第七题：三角门频谱权重（傅里叶变换权重=2πcₖ）',
 'ω/ωm (critical case Ω=2ωm)':'ω/ωm（临界情形 Ω=2ωm）',
 'Fs / τ':'抽样谱 Fs / τ',
 'Critical bandwidth: copied rectangles in [−4ωm,4ωm]':'临界带宽：[−4ωm,4ωm]内的矩形副本',
 'Re(s)T':'实部 Re(s)T',
 'Im(s)T':'虚部 Im(s)T',
 '2021 Q9 · zeros, α=0.6; no finite poles':'2021年第九题：α=0.6时的零点；无有限极点',
 'Finite direct path + one echo':'直接路径加一次有限回波',
 '2022 Q10 · generic causal: ROC |z|>3':'2022年第十题：一般因果实现，收敛域 |z|>3',
 'cancelled at 3':'在3处相消',
 'k=−1/3: reduced ROC |z|>1/3':'k=−1/3：约分后收敛域 |z|>1/3',
 '2022 Q3 · original x(t)':'2022年第三题：原信号 x(t)',
 'δ(t−1), weight 1':'δ(t−1)，权重为1',
 'x(−3t+3): regular part + unit impulse':'x(−3t+3)：普通函数部分加单位冲激',
 'impulse weight × Ts/π':'冲激权重 × Ts/π',
 '2022 Q6 · sampled spectrum; lowpass |ω|<5 units':'2022年第六题：抽样谱；低通范围为 |ω|<5（图示单位）',
 'Output: DC + difference frequency, period 11T':'输出：直流加差频，周期为11T',
 'Inverse FT of Re F = even part [f(t)+f(−t)]/2':'频谱实部的傅里叶逆变换=偶部 [f(t)+f(−t)]/2',
 '2022 Q9 · one-integrator highpass realization':'2022年第九题：单积分器高通实现',
 '2022 Q7 · f(t)':'2022年第七题：f(t)',
 '2022 Q9 · first-order highpass, H(s)=s/(s+1)':'2022年第九题：一阶高通，H(s)=s/(s+1)',
}
for year in [2020,2021,2022]:
 for file in sorted(P.glob(str(year)+'*.svg')):
  doc=etree.parse(str(file))
  for node in doc.iter():
   if node.text:
    node.text=TRANSLATIONS.get(node.text,node.text)
   for key,value in list(node.attrib.items()):
    if key=='style' and 'DejaVu Sans' in value:
     node.set(key,value.replace('DejaVu Sans','Noto Sans CJK SC'))
  payload=etree.tostring(doc,xml_declaration=True,encoding='utf-8').decode()
  payload=payload.replace('DejaVu Sans','Noto Sans CJK SC')
  temporary=file.with_name(file.name+'.partial');temporary.write_text(payload);os.replace(temporary,file)
print('Chinese figure localization complete for 2017–2022.')

for year in range(2017,2023):
 for file in P.glob(str(year)+'*.svg'):etree.parse(str(file))
print('All 32 SVG files are well-formed XML.')
