/* Concise contextual notes, keyed to the app's existing revision handbook.
 * Source scans, full tables and page references stay in the handbook reader. */
window.createLectureContext = function ({D, escape, md}) {
 const handbook = new Map((D.referenceHandbook?.cards || []).map(card => [card.id, card]));
 const notes = [
  {
   id: 'ct-scale', title: '时间尺度', referenceId: 'HF-05', chapters: ['4'],
   keywords: ['尺度','拓展','扩展','压缩','缩放','时间扩展','频谱变窄','平方sinc'],
   formula: '$$\\begin{gathered}x(at)\\longleftrightarrow\\\\\\frac{1}{|a|}X\\!\\left(j\\frac{\\omega}{a}\\right)\\end{gathered}$$',
   explanation: '当 $a\\ne0$，时间与频谱的宽度互逆变化；频谱高度还要除以 $|a|$。',
   hint: '$x(t/4)\\leftrightarrow4X(j4\\omega)$：带宽缩为 $1/4$，高度变为 $4$ 倍。求最高频率只看支撑边界。'
  },
  {
   id: 'ct-modulation', title: '余弦调制', referenceId: 'HF-05', chapters: ['4','8'],
   keywords: ['调制','混频','搬移','频移','载波','乘余弦','调制器'],
   formula: '$$x(t)\\cos\\omega_ct\\longleftrightarrow\\frac12\\big[X(j(\\omega-\\omega_c))+X(j(\\omega+\\omega_c))\\big].$$',
   explanation: '余弦拆成正、负频率的两个复指数，原谱向两侧各搬一次，每份乘 $1/2$。',
   hint: '先标每份谱的中心和边界，再算高度；发生重叠时相加。若乘的是 $2\\cos\\omega_ct$，两份系数各为 $1$。'
  },
  {
   id: 'ct-sampling', title: '冲激抽样', referenceId: 'HS-03', chapters: ['7'],
   keywords: ['抽样','采样','冲激串','周期门','门控','奈奎斯特','慢波','副本'],
   formula: '$$\\omega_s=\\frac{2\\pi}{T_s},\\qquad X_s(j\\omega)=\\frac1{T_s}\\sum_kX(j(\\omega-k\\omega_s)).$$',
   explanation: '单位冲激串抽样：原谱每隔 $\\omega_s$ 复制一次，每份高度乘 $1/T_s$。',
   hint: '间隔与高度分开看。周期矩形门控要先求级数系数 $c_k$，复制谱的权重是 $c_k$，不能照搬 $1/T_s$。'
  },
  {
   id: 'ct-shift', title: '时移与相位', referenceId: 'HF-05', chapters: ['4'],
   keywords: ['时移','延迟','相移','平移','线性相位'],
   formula: '$$x(t-t_0)\\longleftrightarrow e^{-j\\omega t_0}X(j\\omega).$$',
   explanation: '时间平移不改变幅度谱，只增加相位 $-\\omega t_0$。',
   hint: '先把 $x(at-b)$ 改写为 $x(a(t-b/a))$；真正的延迟是 $b/a$，再同时处理尺度因子。'
  },
  {
   id: 'ctfs', title: '连续傅里叶级数', referenceId: 'H13-03', chapters: ['3'],
   keywords: ['级数','周期门','矩形门','谐波','周期输入','傅里叶系数','周期函数'],
   formula: '$$a_k=\\frac1T\\int_{t_0}^{t_0+T}x(t)e^{-jk\\omega_0t}dt,\\qquad\\omega_0=\\frac{2\\pi}{T}.$$',
   explanation: '先选一个完整周期，再求系数；$a_0$ 就是一周期的平均值。',
   hint: '分析式有 $1/T$、负指数；综合式是 $\\sum_k a_ke^{jk\\omega_0t}$。脉宽与周期是两回事。'
  },
  {
   id: 'dtfs', title: '离散傅里叶级数', referenceId: 'H13-04', chapters: ['3','5'],
   keywords: ['DFS','离散级数','系数周期','N点','N周期','周期序列'],
   formula: '$$a_k=\\frac1N\\sum_{n=0}^{N-1}x[n]e^{-j2\\pi kn/N},\\qquad a_{k+N}=a_k.$$',
   explanation: '时间与系数都以 $N$ 为周期；每次求和只取连续 $N$ 项。',
   hint: '系数索引先按模 $N$ 折回。这里的级数系数等于未归一化 DFT 的 $1/N$，不能混用幅度。'
  },
  {
   id: 'energy', title: '能量 Parseval', referenceId: 'HF-08', chapters: ['4'],
   keywords: ['Parseval','能量','平方积分','卷积平方','模平方','频谱矩'],
   formula: '$$\\int_{-\\infty}^{\\infty}|x(t)|^2dt=\\frac1{2\\pi}\\int_{-\\infty}^{\\infty}|X(j\\omega)|^2d\\omega.$$',
   explanation: '在时域、频域中选更容易积分的一侧；频域换回能量时除以 $2\\pi$。',
   hint: '算的是模平方，不是频谱的几何面积。周期信号应改用平均功率的级数 Parseval 公式。'
  },
  {
   id: 'power', title: '周期平均功率', referenceId: 'H13-08', chapters: ['3'],
   keywords: ['平均功率','功率','单边','双边','功率谱'],
   formula: '$$P=\\frac1T\\int_{t_0}^{t_0+T}|x(t)|^2dt=\\sum_{k=-\\infty}^{\\infty}|a_k|^2.$$',
   explanation: '各个正交谐波的功率可以直接相加；直流项贡献 $|a_0|^2$。',
   hint: '实信号的正、负频率成对。若改成单边余弦形式，非零谐波幅度是双边系数模的两倍，功率对应 $A_k^2/2$。'
  },
  {
   id: 'ct-convolution', title: '连续卷积', referenceId: 'H13-02', chapters: ['2'],
   keywords: ['卷积','阶跃响应','冲激响应','零状态','支撑','重叠'],
   formula: '$$y_{zs}(t)=\\int_{-\\infty}^{\\infty}x(\\tau)h(t-\\tau)d\\tau.$$',
   explanation: '先固定输出时刻 $t$，找两个因子同时非零的 $\\tau$ 区间，再积分。',
   hint: '卷积给已知 LTI 系统的零状态响应。若有非零初态，全响应还要加零输入响应。'
  },
  {
   id: 'dt-convolution', title: '离散卷积', referenceId: 'H13-02', chapters: ['2'],
   keywords: ['离散卷积','序列卷积','右边指数','卷积求和','u[n','u[n−','u[n-'],
   formula: '$$y[n]=\\sum_{k=-\\infty}^{\\infty}x[k]h[n-k].$$',
   explanation: '先用阶跃条件联立出 $k$ 的上下限，再把指数代入求和。',
   hint: '闭区间 $L\\le k\\le U$ 一共 $U-L+1$ 项。替换 $n-k$ 时，指数与阶跃都要一起替换。'
  },
  {
   id: 'linearity', title: '线性与时不变', referenceId: 'H13-01', chapters: ['1'],
   keywords: ['线性','时不变','时变','性质','二变量核'],
   formula: '$$T\\{ax_1+bx_2\\}=aT\\{x_1\\}+bT\\{x_2\\}.$$',
   explanation: '线性比较输入幅值的叠加；时不变则比较“先延迟输入”和“求输出后再延迟”。',
   hint: '证明不成立，一个反例就够；证明成立要覆盖题目允许的全部输入。出现 $t$ 并不能直接否定线性。'
  },
  {
   id: 'causal-kernel', title: '因果：看未来输入', referenceId: 'H13-01', chapters: ['1'],
   keywords: ['因果','冲激响应核','二变量核','未来','h_tau','h_\\tau'],
   formula: '$$y(t)=\\int x(\\tau)K(t,\\tau)d\\tau,\\qquad\\tau>t\\Rightarrow K(t,\\tau)=0.$$',
   explanation: '一般线性系统的因果性，要检查未来时刻 $\\tau$ 的输入能否影响当前 $t$ 的输出。',
   hint: '只有已经确定是 LTI 系统时，才能把判据简化为单变量的 $h(t)=0$（$t<0$）。'
  },
  {
   id: 'dtft', title: 'DTFT：频率连续', referenceId: 'HD-01', chapters: ['5'],
   keywords: ['DTFT','幅频图','离散时间傅里叶','零点','频率响应'],
   formula: '$$X(e^{j\\omega})=\\sum_{n=-\\infty}^{\\infty}x[n]e^{-j\\omega n},\\qquad X(e^{j(\\omega+2\\pi)})=X(e^{j\\omega}).$$',
   explanation: '时间是离散的，频率变量仍连续；频谱以 $2\\pi$ 为周期。',
   hint: '先核对 $\\omega=0,\\pi$ 与零点，再判断整条幅频曲线。周期序列的 DTFT 是冲激线谱，不能直接当普通函数求和。'
  },
  {
   id: 'frequency-response', title: '频率响应', referenceId: 'HS-01', chapters: ['6'],
   keywords: ['幅频','相频','群时延','滤波','频率响应','稳态','电路'],
   formula: '$$Y(j\\omega)=H(j\\omega)X(j\\omega),\\qquad\\tau_g=-\\frac{d\\phi_H}{d\\omega}.$$',
   explanation: '模相乘、角相加；群时延是展开相位随频率的负斜率。',
   hint: '带单位阶跃开启的正弦输入还可能有暂态；只写正弦稳态不一定是全响应。'
  },
  {
   id: 'distortionless', title: '无失真传输', referenceId: 'HS-02', chapters: ['6'],
   keywords: ['无失真','全通','公共延迟'],
   formula: '$$H(j\\omega)=Ke^{-j\\omega t_0}\\quad\\text{在输入实际占据的频带成立}.$$',
   explanation: '所有频率共享同一个缩放系数 $K$ 和同一个延迟 $t_0$，波形才能整体保留。',
   hint: '全通只保证模不变；还要检查相位是否对应同一个时间延迟。'
  },
  {
   id: 'laplace-roc', title: '拉氏收敛域', referenceId: 'HL-01', chapters: ['9'],
   keywords: ['拉普拉斯','拉氏','s平面','ROC','极点','收敛域'],
   formula: '$$X(s)=\\int_{-\\infty}^{\\infty}x(t)e^{-st}dt.$$',
   explanation: '先标实际极点，再用因果或稳定条件选 ROC，最后为各项选左右边信号。',
   hint: '稳定要求 ROC 包含虚轴；有理因果系统的 ROC 在最右实际极点右侧。代数分式相同，ROC 不同，信号也可能不同。'
  },
  {
   id: 'z-roc', title: 'Z 收敛域', referenceId: 'HL-05', chapters: ['10'],
   keywords: ['Z变换','Z 变换','z平面','单位圆','ROC','极点','收敛域','逆Z'],
   formula: '$$\\frac1{1-az^{-1}}\\leftrightarrow\\begin{cases}a^nu[n],&|z|>|a|,\\\\-a^nu[-n-1],&|z|<|a|.\\end{cases}$$',
   explanation: '选了 ROC 才能确定左右边。稳定要求 ROC 包含整个单位圆。',
   hint: '左边项有负号，并且止于 $n=-1$。因果有理系统还须检查无穷远条件，不仅看 ROC 是圆外。'
  },
  {
   id: 'feedback', title: '反馈闭环', referenceId: 'HB-04', chapters: ['11'],
   keywords: ['反馈','闭环','回路','稳定区间'],
   formula: '$$e=x-Gy,\\quad y=He\\quad\\Rightarrow\\quad\\frac YX=\\frac H{1+HG}.$$',
   explanation: '先按求和节点列式，移项后得到闭环分母，避免把正、负反馈记反。',
   hint: '稳定判断针对闭环实际极点；外部传递函数约分可能隐藏内部模态。'
  },
  {
   id: 'orthogonal', title: '正交投影', referenceId: 'HM-09', chapters: ['S'],
   keywords: ['正交','最小误差','匹配滤波','最佳逼近','展开系数'],
   formula: '$$c_k=\\frac{\\langle x,g_k\\rangle}{\\|g_k\\|^2},\\qquad\\langle x,g\\rangle=\\int x(t)g^*(t)dt.$$',
   explanation: '最小误差时，残差与每个已选基函数正交。只有单位范数基才能直接把内积当系数。',
   hint: '正交不等于归一。复内积中的共轭、误差能量中的模平方都要保留。'
  }
 ];
 const byId = new Map(notes.map(note => [note.id, note]));
 function score(note, q) {
  const text = [q.title, q.summary, q.statement, q.firstStep].join(' ').toLowerCase();
  let value = note.chapters.some(chapter => (q.chapters || []).map(String).includes(chapter)) ? 5 : 0;
  for (const keyword of note.keywords) if (text.includes(keyword.toLowerCase())) value += keyword.length > 2 ? 7 : 3;
  if (handbook.get(note.referenceId)?.exampleIds?.includes(q.id)) value += 5;
  // Shared ROC vocabulary does not turn a Laplace question into a Z question.
  if (note.id === 'z-roc' && !(q.chapters || []).includes('10')) value = 0;
  if (note.id === 'laplace-roc' && !(q.chapters || []).includes('9')) value = 0;
  return value;
 }
 function cardsFor(q) {
  if (!q) return [];
  if (q.id === '2026-04') return ['ct-scale', 'ct-modulation', 'ct-sampling'].map(id => byId.get(id));
  return notes.map(note => ({note, score: score(note, q)})).filter(entry => entry.score > 0)
   .sort((a, b) => b.score - a.score).slice(0, 3).map(entry => entry.note);
 }
 function select(q, sectionTitle = '') {
  const cards = cardsFor(q), title = String(sectionTitle).toLowerCase();
  if (!title) return cards[0];
  const matches = cards.map(card => ({card, hits: card.keywords.reduce((n, word) => n + (title.includes(word.toLowerCase()) ? 1 : 0), 0)}));
  matches.sort((a, b) => b.hits - a.hits);
  return matches[0]?.card;
 }
 function body(card) {
  if (!card) return '<p>把已知条件与适用范围写在一起，再选用公式。</p>';
  const source = handbook.get(card.referenceId);
  return `<section class="lecture-context-note" data-context-note="${escape(card.id)}">${source ? `<button class="plain lecture-context-source" data-action="lecture-reference" data-card="${escape(card.referenceId)}">查看完整公式与原书对照</button>` : ''}<h3>${escape(card.title)}</h3><div class="lecture-context-formula">${md(card.formula)}</div><h4>怎么理解</h4><div class="lecture-context-explanation">${md(card.explanation)}</div><h4>记忆与检查</h4><div class="lecture-context-hint">${md(card.hint)}</div></section>`;
 }
 function renderCard(q, id) {
  return body(cardsFor(q).find(card => card.id === id) || byId.get(id) || select(q));
 }
 function render(q, sectionTitle = '') {
  const cards = cardsFor(q), active = select(q, sectionTitle);
  return `<h2>这一步用到</h2>${cards.length > 1 ? `<div class="lecture-context-tabs" role="group" aria-label="本题相关公式">${cards.map(card => `<button class="plain${card.id === active?.id ? ' selected' : ''}" data-action="lecture-context" data-context="${escape(card.id)}" aria-pressed="${card.id === active?.id}">${escape(card.title)}</button>`).join('')}</div>` : ''}<div data-context-body>${body(active)}</div><button class="plain lecture-full-reference" data-action="lecture-reference" data-chapter="${escape(q?.chapters?.[0] || '')}">打开公式速查</button>`;
 }
 return {cardsFor, select, render, renderCard};
};
