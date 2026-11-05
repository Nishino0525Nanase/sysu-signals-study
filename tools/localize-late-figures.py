"""Rebuild recent-year and selected textbook figures using Chinese annotations.
The original mathematical curves and structural connections are preserved.
Requires NumPy, Matplotlib and the Noto Sans CJK SC font.
"""
from pathlib import Path
import re
import os
import io
import xml.etree.ElementTree as ET
ASSETS = Path(__file__).resolve().parents[1] / 'content/assets'
ASSETS.mkdir(parents=True, exist_ok=True)

def atomic_savefig(fig, path, **options):
    """Render in memory, validate the finished document, then atomically publish."""
    from PIL import Image
    path=Path(path)
    fmt=options.pop('format', path.suffix.lstrip('.'))
    buffer=io.BytesIO()
    type(fig).savefig(fig, buffer, format=fmt, **options)
    data=buffer.getvalue()
    if fmt=='svg':
        ET.fromstring(data)
    else:
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
    temp=path.with_name(path.name+'.cn-tmp')
    temp.write_bytes(data)
    os.replace(temp,path)


def draw_recent():
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from pathlib import Path
    D=ASSETS
    plt.rcParams.update({'font.family':['Noto Sans CJK SC','DejaVu Sans'],'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#64748b','axes.labelcolor':'#334155','text.color':'#172554','xtick.color':'#475569','ytick.color':'#475569','axes.grid':True,'grid.color':'#e2e8f0','grid.alpha':.8,'svg.fonttype':'path','figure.facecolor':'#ffffff','axes.facecolor':'#ffffff','savefig.bbox':'tight'})
    C=['#176BCE','#EA7C36','#7C3AED','#0F9C92','#CE3F69']
    tri=lambda x:np.maximum(1-np.abs(x),0)
    def setup(ax,title,xlabel=r'角频率 $\omega$（弧度/秒）',ylabel='频谱幅值'):
     ax.set_title(title,loc='left',fontweight='bold',pad=13);ax.set_xlabel(xlabel);ax.set_ylabel(ylabel);ax.axhline(0,color='#64748b',lw=.8);ax.grid(True)
    def save(fig,name):
     atomic_savefig(fig, D/name,format='svg');plt.close(fig)
    # 2026 matching, exact functions
    w=np.linspace(-np.pi,np.pi,6001);z=np.exp(1j*w);X=1+z**-1+z**-2
    Hs=[(z**3-1)/(z**3-.5),z**3/(z**3-.5),(z**3-z**2+z)/(z**3-.5),1+z,1-z+z**2-z**3]
    f,axs=plt.subplots(2,3,figsize=(12,6.7),constrained_layout=True)
    for i,(ax,H,g) in enumerate(zip(axs.flat,Hs,[5,4,6,1,3])):
     ax.plot(w/np.pi,np.abs(X*H),color=C[i%5],lw=2);setup(ax,f'2026年第二题：系统H{i+1}对应原图{g}',r'归一化角频率 $\omega/\pi$',r'输出幅度 $|Y_i(e^{j\omega})|$');ax.set_xticks([-1,-2/3,0,2/3,1],['−1','−2/3','0','2/3','1']);ax.set_xlim(-1,1);ax.set_ylim(-.15,6.4)
    axs.flat[-1].axis('off');axs.flat[-1].text(.05,.7,'全部曲线由五个系统函数\n在单位圆上直接计算得到。\n\n原题图2为多余选项。',transform=axs.flat[-1].transAxes,fontsize=13)
    save(f,'2026_q2_magnitudes.svg')
    # 2026 scaling and gates
    w=np.linspace(-8,8,10001);X0=2*tri(w/2);Xs=8*tri(2*w)
    G=lambda w:8*(tri(2*(w-1))+tri(2*(w+1)))+4*(tri(2*(w-2))+tri(2*(w+2)))
    y1=20/3*(tri(2*(w-1))+tri(2*(w+1)));y2=np.where((abs(w)>1.5)&(abs(w)<2),20/np.pi*(abs(w)-1.5),0)
    f,axs=plt.subplots(5,1,figsize=(11,13),constrained_layout=True)
    vals=[X0,Xs,G(w),y1,y2];titles=['输入频谱：X₀ = 2Λ(ω/2)','两支路均作时间扩展：X₁ = X₂ = 8Λ(2ω)','混频后：g = 2x₁ cos(t) + x₂ cos(2t)','门控支路：Y₁，通带 |ω| < 1.5','冲激抽样支路：Y₂，通带 1.5 < |ω| < 2']
    for ax,v,title in zip(axs,vals,titles):ax.plot(w,v,lw=2,color=C[0]);setup(ax,'2026年第四题｜'+title);ax.set_xlim(-3.1,3.1);ax.set_xticks([-3,-2.5,-2,-1.5,-1,-.5,0,.5,1,1.5,2,2.5,3])
    axs[3].set_ylim(-.3,7.3);axs[4].set_ylim(-.2,3.6)
    save(f,'2026_q4_spectra.svg')
    # 2026 slow wave
    T=1.;delta=.1;Ts=T+delta;tt=np.linspace(0,22,6000);xx=lambda t:.3+np.cos(2*np.pi*t/T);slow=lambda t:(.3+np.cos(2*np.pi*delta*t/(T*Ts)))/Ts
    f,axs=plt.subplots(2,1,figsize=(11,6.4),constrained_layout=True)
    t1=np.linspace(0,3.3,2000);axs[0].plot(t1,xx(t1),color=C[0],lw=1.8);setup(axs[0],'2026年第七题｜原波形：T = 1，Δ = 0.1','时间 t','输入 x(t)');axs[0].set_xlim(0,3.3)
    axs[1].plot(tt,slow(tt),color=C[3],lw=2.3,label=r'慢波 $y(t)=x(\Delta t/T_s)/T_s$');tn=np.arange(21)*Ts;axs[1].scatter(tn,xx(tn)/Ts,color=C[1],s=20,label=r'抽样值 $x(nT_s)/T_s$');setup(axs[1],'重构慢波：周期为11，时间轴放大11倍','时间 t','输出 y(t)');axs[1].legend(loc='upper right');axs[1].set_xlim(0,22)
    save(f,'2026_q7_slowwave.svg')
    #2023 SSB normalized illustrative parabola as source sketch
    w=np.linspace(-6.5,6.5,7000);m=1.;w0=4.;G=lambda v:np.where(abs(v)<=1,1-v*v,0)
    orig=G(w);dsb=.5*(G(w-w0)+G(w+w0));ssb=G(w-w0)*(w<w0)+G(w+w0)*(w>-w0)
    f,axs=plt.subplots(3,1,figsize=(10,8),constrained_layout=True)
    for ax,v,title in zip(axs,[orig,dsb,ssb],['归一化原谱包络示意：ωₘ = 1','仅取上支路：双边带频谱','希尔伯特支路相加：仅保留下边带']):ax.plot(w,v,color=C[0],lw=2);ax.fill_between(w,0,v,color=C[0],alpha=.1);setup(ax,'2023年第五题｜'+title);ax.set_xlim(-6,6);ax.set_ylim(-.05,1.15);ax.set_xticks([-5,-4,-3,-1,0,1,3,4,5])
    save(f,'2023_q5_ssb.svg')
    #2023 sampling exact
    w=np.linspace(-10,8,10000);X=lambda v:np.pi*tri((v+2)/2)
    f,axs=plt.subplots(3,1,figsize=(11,8.5),constrained_layout=True)
    axs[0].plot(w,X(w),lw=2,color=C[0]);setup(axs[0],'2023年第六题｜复输入频谱：支撑区间为[-4, 0]');axs[0].set_ylim(-.1,3.5)
    Tsamp=np.pi/2;ws=4
    for k in range(-3,4):axs[1].plot(w,X(w-k*ws)/Tsamp,lw=1.8,color=C[0] if k==0 else '#94a3b8',label='原频谱副本' if k==0 else None)
    setup(axs[1],'无混叠的最大抽样间隔：T = π/2，ωₛ = 4');axs[1].set_ylim(-.1,2.3)
    R=4*np.abs(np.sinc(2*w/np.pi));axs[2].plot(w,R,lw=2,color=C[1]);setup(axs[2],'宽度为4的保持器：零点使直接逆系统的增益无界',ylabel=r'幅度 $|R(\omega)|$');zeroidx=np.array([k for k in range(-6,7) if k!=0]);axs[2].scatter(zeroidx*np.pi/2,np.zeros(len(zeroidx)),s=15,color=C[4])
    for ax in axs:ax.set_xlim(-10,8);ax.set_xticks(np.arange(-10,9,2))
    save(f,'2023_q6_sampling.svg')
    #2023 response exact
    w=np.linspace(0,15,2500);mag=2/np.sqrt(w*w+4);phase=np.pi-2*np.arctan(w)-np.arctan(w/2)
    f,axs=plt.subplots(1,2,figsize=(11,4),constrained_layout=True)
    axs[0].plot(w,mag,color=C[0],lw=2);setup(axs[0],'2023年第八题｜低通幅频特性',ylabel=r'幅度 $|H(j\omega)|$');axs[0].axvline(2,color=C[1],ls='--');axs[0].scatter([2],[1/np.sqrt(2)],color=C[1]);axs[1].plot(w,phase,color=C[3],lw=2);setup(axs[1],'连续展开的相频特性',ylabel='相位（弧度）');axs[1].set_yticks([-np.pi/2,0,np.pi/2,np.pi],['−π/2','0','π/2','π'])
    save(f,'2023_q8_response.svg')
    #2024 finite h and step
    t=np.linspace(-1,4,2500);h=np.where((t>=0)&(t<=2),np.sin(np.pi*t/2),0);g=np.where(t<0,0,np.where(t<=2,2/np.pi*(1-np.cos(np.pi*t/2)),4/np.pi));ys=2*g-4/np.pi
    f,axs=plt.subplots(3,1,figsize=(10,8.2),constrained_layout=True)
    for ax,v,title,lab in zip(axs,[h,g,ys],['冲激响应：支撑区间为[0, 2]','阶跃响应：最终平台为4/π','符号函数输入的响应：两端平台为±4/π'],['h(t)','g(t)','y(t)']):ax.plot(t,v,color=C[0],lw=2);setup(ax,'2024年第一题｜'+title,'时间 t',lab);ax.set_xlim(-1,4);ax.set_xticks([-1,0,1,2,3,4])
    save(f,'2024_q1_step.svg')
    #2024 gate exact
    w=np.linspace(-27,27,10001);v=.5*tri(w/2)
    f,ax=plt.subplots(figsize=(12,4),constrained_layout=True)
    for k in [-3,-1,0,1,3]:
     ck=.5 if k==0 else np.sin(k*np.pi/2)/(k*np.pi);ax.plot(w,ck*tri((w-8*k)/2),lw=2,color=C[0] if ck>=0 else C[4])
    setup(ax,'2024年第四题｜门控后的带符号频谱（保留负副本）');ax.set_xticks([-26,-24,-22,-18,-16,-14,-10,-8,-6,-2,0,2,6,8,10,14,16,18,22,24,26]);ax.set_xlim(-26,26);ax.set_ylim(-.17,.57)
    save(f,'2024_q4_gated_spectrum.svg')
    #2024 formal mag
    f,ax=plt.subplots(figsize=(10,4.2),constrained_layout=True)
    for w in [np.linspace(0,999.5,2000),np.linspace(1000.5,3000,3000)]:ax.semilogy(w,2*np.sqrt(1+w*w)/np.abs(1e6-w*w),color=C[0],lw=2)
    ax.axvline(1000,color=C[4],ls='--',label='角频率1000弧度/秒处的极点');setup(ax,'2024年第八题｜形式幅值：普通傅里叶频率响应不存在',ylabel='形式幅值（对数刻度）');ax.legend();ax.set_xlim(0,3000)
    save(f,'2024_q8_formal_magnitude.svg')
    #2025 overlap waveform
    t=np.linspace(-1,8,6000);a=np.maximum(0,t-4);b=np.minimum(2,t);y=np.where(b>a,3*np.exp(-3*t)*(np.exp(b)-np.exp(a)),0);x=np.where((t>=0)&(t<2),3*np.exp(-2*t),0)
    f,axs=plt.subplots(2,1,figsize=(11,6.5),constrained_layout=True)
    axs[0].plot(t,x,color=C[1],lw=2);setup(axs[0],'2025年第一题｜截断指数输入','时间 t','输入 x(t)');axs[1].plot(t,y,color=C[0],lw=2);setup(axs[1],'输出：重叠区间在t = 0、2、4、6处改变；y(7) = 0','时间 t','输出 y(t)');axs[1].scatter([7],[0],color=C[4],s=40)
    for ax in axs:ax.set_xlim(-1,8);ax.set_xticks([-1,0,1,2,3,4,5,6,7,8])
    save(f,'2025_q1_waveform.svg')
    #2025 normalized sampling
    w=np.linspace(-10,10,8000);w0=4.;B=1.;original=tri((w-w0)/B)+tri((w+w0)/B);base=tri(w/B);ws=4.;Tsample=2*np.pi/ws
    sample=sum(tri((w-k*ws)/B)/Tsample for k in range(-4,5))
    f,axs=plt.subplots(3,1,figsize=(11,8.3),constrained_layout=True)
    for ax,v,title in zip(axs,[original,base,sample],['归一化示例：B = 1，ω₀ = 4','余弦混频与单位增益低通之后','冲激抽样：ωₛ = 4，T = π/2，峰值为1/T']):ax.plot(w,v,color=C[0],lw=2);setup(ax,'2025年第六题｜'+title);ax.set_xlim(-10,10);ax.set_xticks(np.arange(-10,11,1))
    save(f,'2025_q6_sampling.svg')
    #2025 pole-zero
    f,ax=plt.subplots(figsize=(7,5),constrained_layout=True);theta=np.linspace(0,2*np.pi,1000);ax.plot(np.cos(theta),np.sin(theta),'--',color='#94a3b8',label='单位圆');ax.scatter([0],[0],facecolors='none',edgecolors=C[0],s=150,lw=2,label='原点处二重零点');ax.text(.08,.1,'×2',color=C[0]);ax.scatter([.5,2],[0,0],marker='x',s=130,lw=2,color=C[4],label='极点：0.5与2');ax.axvline(0,color='#64748b',lw=.8);setup(ax,'2025年第九题｜因果实现的收敛域：|z| > 2','实部 Re(z)','虚部 Im(z)');ax.set_aspect('equal');ax.set_xlim(-1.3,2.6);ax.set_ylim(-1.4,1.5);ax.legend(loc='upper left',fontsize=9)
    save(f,'2025_q9_poles.svg')
    print('Created',len(list(D.glob('202[3-6]*.svg'))),'recent-year figures')
    #2024 odd pi line spectrum
    f,ax=plt.subplots(figsize=(10,4.2),constrained_layout=True)
    ww=np.arange(-5,6,2)*np.pi
    for wi in ww:ax.annotate('',xy=(wi,2*np.pi/3),xytext=(wi,0),arrowprops=dict(arrowstyle='-|>',color=C[0],lw=2,mutation_scale=15))
    setup(ax,'2024年第六题｜输出线谱：π的奇数倍处冲激权值为2π/3',r'离散角频率 $\Omega$（弧度/样本）','冲激权值');ax.set_xlim(-5.7*np.pi,5.7*np.pi);ax.set_ylim(-.1,2.8);ax.set_xticks(np.arange(-5,6)*np.pi,['−5π','−4π','−3π','−2π','−π','0','π','2π','3π','4π','5π']);ax.set_yticks([0,2*np.pi/3],['0','2π/3'])
    save(f,'2024_q6_line_spectrum.svg')
    #2024 two-integrator realization
    from matplotlib.patches import Rectangle,Circle
    f,ax=plt.subplots(figsize=(11,5),constrained_layout=True);ax.set_xlim(0,11);ax.set_ylim(0,5);ax.axis('off')
    def arrow(x1,y1,x2,y2,label=None,dy=.15):
     ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='-|>',lw=1.7,color='#176BCE',mutation_scale=13))
     if label:ax.text((x1+x2)/2,(y1+y2)/2+dy,label,ha='center',va='bottom',fontsize=12)
    def box(x,y,text):
     ax.add_patch(Rectangle((x-.55,y-.35),1.1,.7,facecolor='#eff6ff',edgecolor='#176BCE',lw=1.5));ax.text(x,y,text,ha='center',va='center',fontsize=16)
    ax.text(.2,4.7,'2024年第八题｜最小实现：两个积分器',ha='left',fontweight='bold',fontsize=15)
    ax.add_patch(Circle((2,3.4),.26,facecolor='white',edgecolor='#176BCE',lw=1.5));ax.text(2,3.4,'Σ',ha='center',va='center',fontsize=17)
    box(4.2,3.4,r'$1/s$');box(7.3,3.4,r'$1/s$');box(4.9,1.3,r'$-10^6$');box(9.4,2.1,r'$2(v_1+v_2)$')
    arrow(.3,3.4,1.73,3.4,r'$x$');arrow(2.26,3.4,3.65,3.4,r'$\dot v_2$');arrow(4.75,3.4,6.75,3.4,r'$v_2$');arrow(7.85,3.4,8.5,3.4,r'$v_1$')
    ax.plot([8.3,8.3,5.45],[3.4,1.3,1.3],color='#176BCE',lw=1.7);arrow(4.35,1.3,2,1.3);arrow(2,1.3,2,3.14)
    ax.plot([5.6,5.6,8.85],[3.4,2.1,2.1],color='#176BCE',lw=1.7);ax.plot([8.3,8.3,9.4],[3.4,3,3],color='#176BCE',lw=1.7);arrow(9.4,3,9.4,2.45);arrow(9.95,2.1,10.8,2.1,r'$y$')
    ax.text(.4,.35,r'$\dot v_1=v_2,\quad\dot v_2=x-10^6v_1,\quad y=2v_1+2v_2$',fontsize=15)
    save(f,'2024_q8_realization.svg')


def draw_enhanced_a():
    from pathlib import Path
    import json, numpy as np, matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from xml.sax.saxutils import escape
    a=ASSETS
    plt.rcParams.update({'font.family':['Noto Sans CJK SC','DejaVu Sans'],'svg.fonttype':'path','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.prop_cycle':plt.cycler(color=['#327767','#a66b27'])})
    t=np.linspace(-3,8,1400)
    fig,axs=plt.subplots(3,1,figsize=(9,9),constrained_layout=True)
    y=np.where(t>=0,np.exp(-t)-np.exp(-2*t),0)
    axs[0].plot(t,y,label='a=1, b=2');axs[0].plot(t,np.where(t>=0,t*np.exp(-t),0),'--',label='a=b=1');axs[0].legend();axs[0].set_title('2.22(a)：右边指数卷积（参数示例）')
    y=np.select([t<=1,t<=3,t<=6],[.5*np.exp(2*t)*(1-2*np.exp(-4)+np.exp(-10)),.5*np.exp(2)-np.exp(2*(t-2))+.5*np.exp(2*(t-5)),-.5*np.exp(2)+.5*np.exp(2*(t-5))],default=0)
    axs[1].plot(t,y);axs[1].set_title('2.22(b)：左边冲激响应产生非因果输出');axs[1].set_xticks([-3,0,1,3,6,8]);
    y=np.select([(t>1)&(t<3),(t>=3)&(t<5)],[2/np.pi*(1-np.cos(np.pi*(t-1))),2/np.pi*(np.cos(np.pi*(t-3))-1)],default=0)
    axs[2].plot(t,y);axs[2].scatter([1,2,3,4,5],[0,4/np.pi,0,-4/np.pi,0],color='#a66b27');axs[2].set_title('2.22(c)：单周期正弦与延时矩形的卷积');axs[2].set_xticks([0,1,2,3,4,5,6]);
    for ax in axs:ax.axhline(0,c='#667a73',lw=.7);ax.grid(alpha=.18);ax.set_xlabel('时间 t');ax.set_ylabel('输出 y(t)')
    atomic_savefig(fig, a/'enhanced-a-2-22.svg');plt.close(fig)
    t=np.linspace(-2,9,1000);y=np.select([t<1,t<4],[np.zeros_like(t),1-np.exp(-(t-1))],default=(1-np.exp(-3))*np.exp(-(t-4)))
    fig,ax=plt.subplots(figsize=(9,3.6),constrained_layout=True);ax.plot(t,y,label='输出 y(t)');ax.plot([-1,-1,2,2], [0,1,1,0],'--',alpha=.55,label='输入 x(t)');ax.axhline(0,c='#667a73',lw=.7);ax.scatter([1,4],[0,1-np.exp(-3)]);ax.set_xticks([-1,0,1,2,4,6,8]);ax.set_xlabel('时间 t');ax.set_ylabel('信号幅度');ax.set_title('2.40：输入支撑为[-1, 2]，冲激响应延时2');ax.grid(alpha=.2);ax.legend();atomic_savefig(fig, a/'enhanced-a-2-40.svg');plt.close(fig)


def draw_enhanced_c():
    from pathlib import Path
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    root=ASSETS
    plt.rcParams.update({'font.family':['Noto Sans CJK SC','DejaVu Sans'],'svg.fonttype':'path','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    w=np.linspace(-7,7,2801)
    L=lambda c:np.maximum(1-abs(w-c),0)
    arr=[.5*(L(.5)+L(-.5)),.5*(L(1)+L(-1)),.5*(L(2)+L(-2)),.25*(L(1)+L(-1)-L(3)-L(-3)),.5*(L(2)+L(-2)-L(1)-L(-1)),sum(L(2*n) for n in range(-5,6))/np.pi,np.ones_like(w)/(2*np.pi),np.ones_like(w)/(2*np.pi),sum(L(2*n+1) for n in range(-5,6))/(2*np.pi),L(0)/3+sum(np.sin(n*np.pi/3)/(n*np.pi)*L(2*n) for n in range(-5,6) if n)]
    titles=['(i) 乘以 cos(t/2)','(ii) 乘以 cos(t)','(iii) 乘以 cos(2t)','(iv) 乘以 sin(t)sin(2t)','(v) 乘以 cos(2t)−cos(t)','(vi) 冲激串：周期 T = π','(vii) 冲激串：周期 T = 2π','(viii) 冲激串：周期 T = 4π','(ix) 两个冲激串之差','(x) 周期方波：占空比为1/3']
    fig,axs=plt.subplots(5,2,figsize=(10,13),constrained_layout=True)
    for ax,y,title in zip(axs.ravel(),arr,titles):
     ax.axhline(0,color='#82908a',lw=.7);ax.axvline(0,color='#82908a',lw=.7);ax.plot(w,y,color='#246c5c',lw=1.8);ax.set_title(title,loc='left',fontsize=11);ax.set_xlim(-7,7);ax.set_xticks(range(-6,7,2));ax.set_xlabel('角频率 ω（弧度/秒）');ax.set_ylabel('输出频谱 Y(jω)');ax.grid(alpha=.15);ax.set_ylim(min(-.05,float(min(y))-.05),max(.4,float(max(y))+.08))
    atomic_savefig(fig, root/'enhanced-c-o16-spectra.svg',bbox_inches='tight');plt.close(fig)
    t=np.linspace(-8,12,3000)
    x=np.cos(t/np.sqrt(3))+np.cos(t)+np.cos(np.sqrt(3)*t)
    y=np.cos(t/np.sqrt(3)-np.pi/3)+np.cos(t-np.pi/2)+np.cos(np.sqrt(3)*t-2*np.pi/3)
    fig,axs=plt.subplots(2,1,figsize=(10,6),sharex=True,constrained_layout=True)
    for ax,z,title,c in zip(axs,[x,y],['输入 x(t)','输出 y(t)，a=1'],['#246c5c','#b27428']):
     ax.plot(t,z,c,lw=1.8);ax.axhline(0,c='#82908a',lw=.7);ax.axvline(0,c='#82908a',lw=.7);ax.set_ylim(-3.3,3.3);ax.grid(alpha=.15);ax.set_ylabel(title)
    axs[1].set_xlabel('时间 t');atomic_savefig(fig, root/'enhanced-c-o18-waveforms.svg',bbox_inches='tight');plt.close(fig)
    print('2 figures saved')


def draw_enhanced_e():
    from pathlib import Path
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out=ASSETS
    plt.rcParams.update({'font.family':['Noto Sans CJK SC','DejaVu Sans'],'svg.fonttype':'path','axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#243a3b','text.color':'#243a3b','axes.edgecolor':'#9aada4','font.size':11,'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white'})
    green='#327767';amber='#b57632';red='#ab5d4d';gray='#c6cfcb'
    a=3.;wm=1.;w=np.linspace(-11,11,8801)
    def G(z):return np.where(np.abs(z)<=1,1-.8*z*z,0)
    orig=G(w);copies=sum(G(w-(2*k+1)*a) for k in range(-3,3)); y=np.where((np.abs(w)>a)&(np.abs(w)<3*a),copies,0)
    fig,axs=plt.subplots(3,1,figsize=(11,8),sharex=True,constrained_layout=True)
    axs[0].plot(w,orig,color=green,lw=2);axs[0].fill_between(w,orig,color=green,alpha=.15)
    axs[0].set_ylabel(r'原频谱 $X(j\omega)$');axs[0].set_title(r'O29 / 7.23：频谱副本的位置与半边谱的选择 ($\omega_M=1,\ a=\pi/\Delta=3$)',loc='left',fontsize=12)
    axs[0].text(1.6,.73,'包络示意图：原书只给出支撑区间，\n未指定曲线的解析表达式。',fontsize=10)
    axs[1].plot(w,copies,color=green,lw=1.8);axs[1].fill_between(w,copies,color=green,alpha=.1);axs[1].set_ylabel(r'抽样谱 $\Delta X_p(j\omega)$')
    for cen in [-9,-3,3,9]:
     axs[1].axvline(cen,color=gray,lw=.7,ls=':');axs[1].text(cen,1.08,rf'${int(cen/3)}a$',ha='center',fontsize=10)
    axs[2].axvspan(3,9,color=green,alpha=.06);axs[2].axvspan(-9,-3,color=green,alpha=.06)
    axs[2].plot(w,copies,color=gray,lw=1.3,ls='--');axs[2].plot(w,y,color=amber,lw=2.3);axs[2].fill_between(w,y,color=amber,alpha=.2);axs[2].set_ylabel(r'滤波后谱 $\Delta Y(j\omega)$');axs[2].set_xlabel(r'归一化角频率 $\omega/\omega_M$')
    axs[2].annotate('右半边',xy=(3.45,.84),xytext=(4.9,1.02),arrowprops={'arrowstyle':'->','color':amber},color=amber,fontsize=10)
    axs[2].annotate('左半边',xy=(8.55,.84),xytext=(6.6,1.02),arrowprops={'arrowstyle':'->','color':amber},color=amber,fontsize=10)
    for ax in axs:
     ax.set_ylim(-.05,1.28);ax.set_xlim(-11,11);ax.set_yticks([0,1]);ax.grid(axis='y',alpha=.15)
     ax.axhline(0,color=gray,lw=.7)
    axs[2].set_xticks([-10,-9,-8,-4,-3,-2,-1,0,1,2,3,4,8,9,10]);
    atomic_savefig(fig, out/'enhanced-e-o29-halfbands.svg');plt.close(fig)
    
    w=np.linspace(-1.6,1.6,2201);delta=.3
    tri=lambda z:np.maximum(1-np.abs(z),0)
    l=tri(w-delta)/4;r=tri(w+delta)/4;s=l+r
    fig,axs=plt.subplots(2,1,figsize=(10.5,6.5),sharex=True,constrained_layout=True)
    axs[0].plot(w,l,color=green,lw=2,label=r'右移分量 $X(j(\omega-\Delta\omega))/4$');axs[0].plot(w,r,color=amber,lw=2,label=r'左移分量 $X(j(\omega+\Delta\omega))/4$');axs[0].set_ylabel('移频分量');axs[0].legend(frameon=False,fontsize=10);axs[0].set_title(r'O32单位增益变式（原题增益2）：两份移频谱相加 ($\omega_M=1,\ |\Delta\omega|=0.3$)',loc='left',fontsize=12)
    axs[1].plot(w,s,color=green,lw=2.5);axs[1].fill_between(w,s,color=green,alpha=.17);axs[1].set_ylabel(r'输出频谱 $X_{out}(j\omega)$');axs[1].set_xlabel(r'归一化角频率 $\omega/\omega_M$')
    axs[1].annotate(r'中央平台： $\frac{1}{2}(1-d/\omega_M)=0.35$',xy=(0,.35),xytext=(.37,.48),arrowprops={'arrowstyle':'->','color':green},fontsize=10)
    for ax in axs:
     ax.grid(alpha=.14);ax.set_xlim(-1.6,1.6);ax.set_ylim(-.02,.54);ax.set_yticks([0,.25,.35,.5]);ax.axhline(0,color=gray,lw=.7)
    axs[1].set_xticks([-1.3,-1,-.7,-.3,0,.3,.7,1,1.3]);
    atomic_savefig(fig, out/'enhanced-e-o32-frequency-offset.svg');plt.close(fig)
    print('created 2 SVGs')


def draw_training():
    from pathlib import Path
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle, Arc
    
    out=ASSETS
    plt.rcParams.update({'font.family':['Noto Sans CJK SC','DejaVu Sans'],'font.size':11,'mathtext.fontset':'dejavusans'})
    blue='#215b76';orange='#c47d39'
    
    def spectrum(name,centres,half,height,lims):
        w=np.linspace(*lims,5001)
        fig,axs=plt.subplots(2,1,figsize=(7.3,3.5),sharex=True,layout='constrained')
        for ax in axs:
            ax.axhline(0,color='#454c54',lw=.8);ax.axvline(0,color='#abb4ba',lw=.7)
            ax.spines[['top','right','left']].set_visible(False)
            ax.set_ylim(-height*.12,height*1.35);ax.set_yticks([0,height],['0',rf'${height:.3f}$'])
            ax.grid(axis='x',alpha=.15)
        ys=np.zeros_like(w)
        for c in centres:ys+=height*np.maximum(1-np.abs(w-c)/half,0)
        axs[0].plot(w,ys,color=blue,lw=1.8);axs[0].set_ylabel(r'抽样谱 $X_p(j\omega)$')
        keep=np.zeros_like(w)
        for c in [-centres[centres>0][0],centres[centres>0][0]]:keep+=height*np.maximum(1-np.abs(w-c)/half,0)
        axs[1].plot(w,keep,color=orange,lw=1.8);axs[1].set_ylabel(r'输出谱 $Y(j\omega)$')
        axs[1].set_xlabel(r'角频率 $\omega$（弧度/秒）');axs[1].set_xlim(lims)
        ticks=sorted(set([0]+[float(c+d) for c in centres for d in [-half,0,half] if lims[0]<=c+d<=lims[1]]))
        axs[1].set_xticks(ticks)
        atomic_savefig(fig, out/('training_'+name),dpi=220);plt.close(fig)
    
    spectrum('mock_sampling.png',np.array([-9,-3,3,9]),1,3/np.pi,(-10,10))
    spectrum('exercise_sampling.png',np.array([-15,-5,5,15]),2,5/np.pi,(-12,12))
    
    fig,ax=plt.subplots(figsize=(7.2,1.9));ax.set_aspect('equal');ax.set_xlim(0,9);ax.set_ylim(-.2,2.1);ax.axis('off')
    def arrow(x1,y1,x2,y2):ax.annotate('',(x2,y2),(x1,y1),arrowprops={'arrowstyle':'->','lw':1.5,'color':blue})
    ax.add_patch(Circle((2,1.25),.25,fill=False,color=blue,lw=1.5));ax.text(2,1.25,'+',ha='center',va='center',fontsize=15)
    arrow(.3,1.25,1.75,1.25);ax.text(.25,1.5,r'输入 $x(t)$')
    for x,w,label in [(3,.8,r'$k$'),(4.8,1.6,r'$G(s)$')]:
        ax.add_patch(Rectangle((x,.87),w,.76,fill=False,color=blue,lw=1.5));ax.text(x+w/2,1.25,label,ha='center',va='center',fontsize=14)
    arrow(2.25,1.25,3,1.25);arrow(3.8,1.25,4.8,1.25);arrow(6.4,1.25,8.5,1.25);ax.text(8.2,1.55,r'输出 $y(t)$')
    ax.plot([7.4,7.4,2],[1.25,.05,.05],color=blue,lw=1.5);arrow(2,.05,2,1);ax.text(2.25,.5,'+',fontsize=14)
    fig.tight_layout(pad=.2);atomic_savefig(fig, out/'training_feedback.png',dpi=220);plt.close(fig)
    
    fig,ax=plt.subplots(figsize=(7.2,2.4));ax.set_aspect('equal');ax.set_xlim(0,8);ax.set_ylim(-.4,2.5);ax.axis('off')
    ax.plot([.6,1.5],[1.9,1.9],color=blue,lw=1.5)
    xs=np.linspace(1.5,2.7,13);ys=1.9+.15*np.array([0,1,-1,1,-1,1,-1,1,-1,1,-1,1,0]);ax.plot(xs,ys,color=blue,lw=1.5)
    ax.plot([2.7,3.4],[1.9,1.9],color=blue,lw=1.5)
    for i in range(4):ax.add_patch(Arc((3.6+i*.4,1.9),.4,.5,theta1=0,theta2=180,color=blue,lw=1.5))
    ax.plot([5,6.6,6.6],[1.9,1.9,1.1],color=blue,lw=1.5)
    ax.plot([6.2,7],[1.1,1.1],color=blue,lw=1.5);ax.plot([6.2,7],[.85,.85],color=blue,lw=1.5)
    ax.plot([6.6,6.6,.6],[.85,0,0],color=blue,lw=1.5)
    ax.text(1.7,2.18,r'$R=2\,\Omega$');ax.text(3.55,2.25,r'$L=1$ 亨利');ax.text(6.95,.9,r'$C=\frac{1}{2}$ 法拉')
    ax.text(.2,.95,r'$x(t)$',ha='center');ax.text(.5,1.7,'+');ax.text(.5,.1,'−');ax.text(5.9,.9,r'$y(t)$',ha='right')
    fig.tight_layout(pad=.2);atomic_savefig(fig, out/'training_rlc.png',dpi=220);plt.close(fig)


def localize_preserved_blocks():
    """Change visible labels only; never regenerate the corrected wiring."""
    replacements = {
        '2.60(c): S1, two integrators and three feedforward taps': '2.60(c)：子系统S₁，两个积分器与三条前馈支路',
        '2.60(d): S2, feedback from two integrated output states': '2.60(d)：子系统S₂，由两个积分状态反馈',
        '2.60(e,f): two cascade orders (4 integrators before sharing)': '2.60(e、f)：两种串联次序（共用前共四个积分器）',
        '2.60(g): Direct Form II, one shared two-integrator chain': '2.60(g)：直接Ⅱ型，共用一条双积分器链',
        'S1: 2 integrators': 'S₁：两个积分器',
        'S2: 2 integrators': 'S₂：两个积分器',
    }
    for name in ['enhanced-a-2-60-blocks.svg', 'enhanced-f-o39-structures.svg']:
        p=ASSETS/name
        s=p.read_text()
        for old,new in replacements.items():
            s=s.replace(old,new)
        s=s.replace('font-family="Arial,sans-serif"', 'font-family="Noto Sans CJK SC,Microsoft YaHei,sans-serif"')
        s=s.replace('直接II型','直接Ⅱ型')
        ET.fromstring(s)
        temp=p.with_name(p.name+'.cn-tmp')
        temp.write_text(s)
        os.replace(temp,p)


if __name__ == '__main__':
    import matplotlib as mpl
    import matplotlib.font_manager as font_manager
    # Refuse to produce missing-glyph boxes on a machine without the Chinese font.
    font_manager.findfont('Noto Sans CJK SC', fallback_to_default=False)
    for draw in [draw_recent, draw_enhanced_a, draw_enhanced_c, draw_enhanced_e, draw_training]:
        draw()
    localize_preserved_blocks()
    print('已重绘2023—2026年、课后增强图与4幅训练图；框图接线保持不变。')
