/* Full-book reader. The host owns routing, image zoom, caching, and publication. */
'use strict';
window.createTextbookReader = function ({ D, escape, heading }) {
 const book = D.textbookReader || {};
 const pages = (book.pages || []).filter(p => Number.isInteger(p.pdfPage) && p.pdfPage > 0 && p.path).slice().sort((a, b) => a.pdfPage - b.pdfPage);
 const pageByPdf = new Map(pages.map(p => [p.pdfPage, p]));
 const pageByPrint = new Map(pages.filter(p => Number.isInteger(p.printPage) && p.printPage > 0).map(p => [p.printPage, p]));
 const pageCount = Number(book.pdfPageCount) || pages.length;
 const maxPrint = Math.max(0, ...pageByPrint.keys());
 const storageKey = 'sysu-signals-textbook-last-page:' + (book.id || 'oppenheim-second-edition-cn');
 const toc = (book.toc || []).map((item, index) => ({ ...item, pdfPage: Number(item.pdfPage), level: Math.max(1, Math.min(10, Number(item.level) || 1)), index, children: [] })).filter(item => pageByPdf.has(item.pdfPage));
 const roots = [], stack = [];
 for (const item of toc) {
  while (stack.length && stack[stack.length - 1].level >= item.level) stack.pop();
  (stack.length ? stack[stack.length - 1].children : roots).push(item);
  stack.push(item);
 }
 let tocQuery = '', jumpMode = 'pdf', tocOpen = null, pendingTurn = null;
 const wide = () => typeof window.matchMedia === 'function' && window.matchMedia('(min-width:1480px)').matches;
 const normalize = value => String(value || '').normalize('NFKC').trim().toLowerCase().replace(/采样/g, '抽样');
 const integer = value => /^\d+$/.test(String(value || '').trim()) ? Number(String(value).trim()) : null;
 const hasPrint = page => Number.isInteger(page?.printPage) && page.printPage > 0;
 const pageLabel = page => hasPrint(page) ? `印刷书页 ${page.printPage} · PDF 第 ${page.pdfPage} 页` : `PDF 第 ${page.pdfPage} 页`;
 const href = page => '#book?pdf=' + page;
 function savedPage() {
  try { const value = integer(localStorage.getItem(storageKey)); return pageByPdf.has(value) ? value : null; } catch { return null; }
 }
 function rememberPage(value) { try { localStorage.setItem(storageKey, String(value)); } catch { /* Reading works when local storage is unavailable. */ } }
 function resolve(params) {
  const fallback = pageByPdf.get(savedPage()) || pages[0];
  if (params.has('pdf')) {
   const page = pageByPdf.get(integer(params.get('pdf')));
   return page ? { page } : { page: fallback, notice: `未找到这个 PDF 页码，请输入 1–${pageCount}。` };
  }
  if (params.has('print')) {
   const page = pageByPrint.get(integer(params.get('print')));
   return page ? { page } : { page: fallback, notice: '未找到这个印刷书页，请核对页码，或改用 PDF 页码跳转。' };
  }
  return { page: fallback, resumed: savedPage() !== null };
 }
 function currentEntry(pdfPage) {
  let entry;
  for (const item of toc) if (item.pdfPage <= pdfPage && (!entry || item.pdfPage >= entry.pdfPage)) entry = item;
  return entry;
 }
 function match(item, query) {
  const page = pageByPdf.get(item.pdfPage);
  const text = normalize(`${item.title} PDF ${item.pdfPage} ${hasPrint(page) ? '书页 ' + page.printPage : ''}`);
  return normalize(query).split(/\s+/).filter(Boolean).every(word => text.includes(word));
 }
 function containsCurrent(item, current) { return item.index === current?.index || item.children.some(child => containsCurrent(child, current)); }
 function filtered(item, query, includeAll = false) {
  const ownMatch = match(item, query), includeChildren = includeAll || ownMatch;
  const children = item.children.map(child => filtered(child, query, includeChildren)).filter(Boolean);
  return includeAll || ownMatch || children.length ? { item, children, ownMatch } : null;
 }
 function tocLink(item, current, label) {
  const page = pageByPdf.get(item.pdfPage), active = item.index === current?.index;
  return `<a class="book-toc-link ${active ? 'is-current' : ''}" href="${href(item.pdfPage)}" data-book-toc-page="${item.pdfPage}" ${active ? 'aria-current="page"' : ''}><span>${escape(label || item.title)}</span><small>${hasPrint(page) ? '书页 ' + page.printPage : 'PDF ' + item.pdfPage}</small></a>`;
 }
 function directory(query, pdfPage) {
  const current = currentEntry(pdfPage), searching = Boolean(normalize(query));
  const renderNode = (node, depth) => {
   const { item, children } = node;
   if (!item.children.length) return `<li>${tocLink(item, current)}</li>`;
   const open = searching || containsCurrent(item, current);
   return `<li><details class="book-toc-group book-toc-depth-${Math.min(depth, 3)}" ${open ? 'open' : ''}><summary><span>${escape(item.title)}</span><small>PDF ${item.pdfPage}</small></summary><div class="book-toc-children">${tocLink(item, current, '从本节开头读 →')}<ul>${children.map(child => renderNode(child, depth + 1)).join('')}</ul></div></details></li>`;
  };
  const list = roots.map(item => filtered(item, query)).filter(Boolean);
  return list.length ? `<ul class="book-toc-list">${list.map(node => renderNode(node, 0)).join('')}</ul>` : '<p class="book-toc-empty">没有匹配的目录。可试试“抽样”“傅里叶”或节号。</p>';
 }
 function paging(page, index, bottom = false) {
  const previous = pages[index - 1], next = pages[index + 1];
  const link = (value, label, turn) => value ? `<a class="book-page-link" data-book-turn="${turn}" href="${href(value.pdfPage)}">${label}</a>` : `<span class="book-page-link is-disabled" aria-disabled="true">${label}</span>`;
  return `<div class="book-paging ${bottom ? 'book-paging-bottom' : ''}" aria-label="原书翻页">${link(previous, '← 上一页', 'prev')}<span class="book-paging-position">${page.pdfPage} / ${pageCount}</span>${link(next, '下一页 →', 'next')}</div>`;
 }
 function jumpForm(page, suffix = '') {
  const id = 'book-jump-' + (suffix ? suffix + '-' : '');
  const value = jumpMode === 'print' ? (hasPrint(page) ? page.printPage : '') : page.pdfPage;
  return `<form class="book-jump-form" data-book-jump><label class="book-sr-only" for="${id}kind">页码类型</label><select id="${id}kind" data-book-jump-kind aria-label="页码类型"><option value="pdf" ${jumpMode === 'pdf' ? 'selected' : ''}>PDF 页</option><option value="print" ${jumpMode === 'print' ? 'selected' : ''}>印刷书页</option></select><label class="book-sr-only" for="${id}value">跳转页码</label><input id="${id}value" data-book-jump-value aria-label="跳转页码" type="number" inputmode="numeric" min="1" max="${jumpMode === 'print' ? maxPrint : pageCount}" step="1" value="${value}" placeholder="页码" required><button type="submit">跳转</button></form>`;
 }
 function dock(page, index) {
  const turn = (value, label, direction) => value ? `<a class="book-dock-turn" data-book-turn="${direction}" href="${href(value.pdfPage)}">${label}</a>` : `<span class="book-dock-turn is-disabled" aria-disabled="true">${label}</span>`;
  return `<div class="book-page-dock" role="navigation" aria-label="快捷翻页">${turn(pages[index - 1], '← 上一页', 'prev')}<details class="book-dock-menu"><summary aria-label="页码与跳转"><strong>${hasPrint(page) ? '书页 ' + page.printPage : 'PDF ' + page.pdfPage}</strong><small>${page.pdfPage} / ${pageCount} · 跳页⌃</small></summary><div class="book-dock-panel"><strong>跳到指定页</strong>${jumpForm(page, 'dock')}<p class="book-jump-feedback" data-book-jump-feedback role="status" hidden></p><button type="button" data-book-action="dock-toc">打开章节目录 ≡</button><small>电脑可按 ← / → 翻页</small></div></details>${turn(pages[index + 1], '下一页 →', 'next')}</div>`;
 }
 function downloadLink() {
  const download = book.download;
  if (!download?.path) return '';
  const size = download.bytes ? ` · ${(download.bytes / 1048576).toFixed(1)} MB` : '';
  return `<a class="book-download" href="${escape(download.path)}" target="_blank" rel="noopener">下载完整 PDF${size} ↗</a>`;
 }
 function render(params = new URLSearchParams()) {
  if (!pages.length) return heading('整本教材 / 原书阅读', '奥本海姆《信号与系统》第二版', '整本原书页面正在准备，请稍后重试。') + '<p><a class="button" href="#downloads">← 返回资料与安装</a></p>';
  const { page, notice, resumed } = resolve(params), index = pages.findIndex(p => p.pdfPage === page.pdfPage), entry = currentEntry(page.pdfPage);
  const open = tocOpen === null ? wide() : tocOpen;
  const isAndroid = new URLSearchParams(window.location.search).get('android') === '1';
  const modeNote = isAndroid ? 'App 已内置全书，翻页无需联网；下载完整 PDF 需联网。' : '网页逐页加载，读过的页面可缓存；完整 PDF 可另外下载。';
  return `<section class="textbook-reader" data-textbook-reader data-current-pdf="${page.pdfPage}">
   <div class="book-backline"><a href="#downloads">← 资料与安装</a><a class="book-download" href="#digest">先读原书精简版 →</a>${downloadLink()}</div>
   ${heading('整本教材 / 原书阅读', escape(book.title || '奥本海姆《信号与系统》第二版'), escape(modeNote))}
   <p class="book-reading-encouragement">这一页不必一次记住，先弄清一个公式为什么成立。看累了，也可以先休息一会儿。</p>
   <div class="book-page-heading"><div><strong>${escape(pageLabel(page))}</strong><span>${hasPrint(page) ? '按原书印刷页码标注' : '此页未标注正文印刷书页'}</span></div><span class="book-reading-location">${escape(entry?.title || '原书前置页')}${resumed ? '<small>接着上次阅读</small>' : ''}</span></div>
   ${notice ? `<p class="book-route-notice" role="status">${escape(notice)}</p>` : ''}
   <div class="book-read-controls">${paging(page, index)}${jumpForm(page)}<button type="button" class="book-toc-toggle" data-book-action="toggle-toc" aria-expanded="${open}" aria-controls="book-toc-shell">章节目录 ≡</button></div>
   <p class="book-jump-feedback" data-book-jump-feedback role="status" hidden></p>
   <div class="book-reading-layout"><div class="book-reading-content"><figure class="book-current-page"><p class="book-image-status" data-book-image-status role="status">正在载入本页…</p><button type="button" class="book-page-view" data-expand data-full="${escape(page.path)}" data-caption="${escape((book.title || '奥本海姆原书') + ' · ' + pageLabel(page))}" aria-label="放大${escape(pageLabel(page))}"><img data-book-page-image src="${escape(page.path)}" alt="${escape((book.title || '奥本海姆原书') + ' · ' + pageLabel(page))}" ${page.width > 0 ? `width="${Number(page.width)}"` : ''} ${page.height > 0 ? `height="${Number(page.height)}"` : ''} loading="eager" decoding="async" fetchpriority="high"><span class="book-zoom-hint">点开原图，查看局部公式与图形 ↗</span></button><button type="button" class="book-retry" data-book-action="retry-image" hidden>重新载入本页</button><figcaption>${escape(pageLabel(page))} · 共 ${pageCount} 个 PDF 页面</figcaption></figure>${paging(page, index, true)}</div>
   <aside class="book-directory" aria-label="整本教材目录"><details class="book-toc-shell" id="book-toc-shell" ${open ? 'open' : ''}><summary><span>章节目录</span><small>${toc.length} 个条目 · 可搜索</small></summary><div class="book-toc-content"><label class="book-sr-only" for="book-toc-search">搜索章节目录</label><input type="search" id="book-toc-search" placeholder="搜节号或关键词，如“7.3”“抽样”" value="${escape(tocQuery)}" autocomplete="off"><label class="book-sr-only" for="book-chapter-jump">快速选择章节</label><select id="book-chapter-jump" aria-label="快速选择章节"><option value="">快速选章…</option>${roots.map(item => `<option value="${item.pdfPage}">${escape(item.title)}</option>`).join('')}</select><p class="book-toc-count" data-book-toc-count>${tocQuery ? `${toc.filter(item => match(item, tocQuery)).length} 个标题或页码匹配` : `${toc.length} 个目录条目`}</p><div class="book-toc-results" data-book-toc-results>${directory(tocQuery, page.pdfPage)}</div></div></details></aside></div>
   <div class="book-quality-note"><strong>阅读提示</strong><p>按原书高清页面阅读。原件中已有的模糊不会凭空变清晰；小字和公式可点开局部放大。</p>${book.qualityNote ? `<details><summary>页面与页码说明</summary><p>${escape(book.qualityNote)}</p></details>` : ''}</div>
   ${dock(page, index)}
  </section>`;
 }
 function bind(rootElement) {
  const container = rootElement?.querySelector('[data-textbook-reader]');
  if (!container) return;
  const page = pageByPdf.get(Number(container.dataset.currentPdf));
  if (!page) return;
  rememberPage(page.pdfPage);
  const query = selector => container.querySelector(selector), shell = query('.book-toc-shell');
  const feedback = message => { container.querySelectorAll('[data-book-jump-feedback]').forEach(target => { target.textContent = message; target.hidden = !message; }); };
  const go = (type, value) => {
   const number = integer(value), target = (type === 'print' ? pageByPrint : pageByPdf).get(number);
   if (!target) { feedback(type === 'print' ? '未找到这个印刷书页。请核对书页，或切换到 PDF 页。' : `请输入 1–${pageCount} 范围内的 PDF 页码。`); return; }
   const hash = '#book?' + type + '=' + number;
   if (window.location.hash === hash) { feedback('已在这一页。'); query('.book-current-page').scrollIntoView({ block: 'start', behavior: 'smooth' }); }
   else { pendingTurn = 'jump'; window.location.hash = hash; }
  };
  const image = query('[data-book-page-image]'), status = query('[data-book-image-status]'), retry = query('.book-retry'), imageButton = query('.book-page-view');
  const loaded = () => { image.hidden = false; imageButton.disabled = false; status.hidden = true; retry.hidden = true; };
  const failed = () => { image.hidden = true; imageButton.disabled = true; status.hidden = false; status.textContent = '本页暂未载入，请重试。'; retry.hidden = false; };
  image.onload = loaded; image.onerror = failed;
  if (image.complete) { if (image.naturalWidth) loaded(); else failed(); }
  container.querySelectorAll('[data-book-jump]').forEach(form => {
   form.onsubmit = event => { event.preventDefault(); go(form.querySelector('[data-book-jump-kind]').value, form.querySelector('[data-book-jump-value]').value); };
   form.querySelector('[data-book-jump-kind]').onchange = event => {
   jumpMode = event.target.value;
   container.querySelectorAll('[data-book-jump]').forEach(target => {
    const input = target.querySelector('[data-book-jump-value]');
    target.querySelector('[data-book-jump-kind]').value = jumpMode;
    input.max = String(jumpMode === 'print' ? maxPrint : pageCount);
    input.value = jumpMode === 'print' ? (hasPrint(page) ? page.printPage : '') : page.pdfPage;
    input.placeholder = jumpMode === 'print' ? '印刷书页' : 'PDF 页码';
   });
   feedback('');
   };
  });
  query('#book-toc-search').oninput = event => {
   tocQuery = event.target.value;
   query('[data-book-toc-results]').innerHTML = directory(tocQuery, page.pdfPage);
   query('[data-book-toc-count]').textContent = normalize(tocQuery) ? `${toc.filter(item => match(item, tocQuery)).length} 个标题或页码匹配` : `${toc.length} 个目录条目`;
  };
  query('#book-chapter-jump').onchange = event => { if (event.target.value) { if (!wide()) { tocOpen = false; shell.open = false; } go('pdf', event.target.value); } };
  shell.ontoggle = () => { tocOpen = shell.open; query('[data-book-action="toggle-toc"]').setAttribute('aria-expanded', String(shell.open)); };
  container.onclick = event => {
   if (!event.ctrlKey && !event.metaKey && !event.altKey && !event.shiftKey && event.button === 0) {
    const turn = event.target.closest('a[data-book-turn]');
    if (turn) pendingTurn = turn.dataset.bookTurn;
   }
   const tocLink = event.target.closest('[data-book-toc-page]');
   if (tocLink) {
    if (!event.ctrlKey && !event.metaKey && !event.altKey && !event.shiftKey && event.button === 0 && Number(tocLink.dataset.bookTocPage) !== page.pdfPage) pendingTurn = 'jump';
    if (!wide()) { tocOpen = false; shell.open = false; }
    if (Number(tocLink.dataset.bookTocPage) === page.pdfPage && window.location.hash === tocLink.getAttribute('href')) { event.preventDefault(); query('.book-current-page').scrollIntoView({ block: 'start', behavior: 'smooth' }); }
    return;
   }
   const action = event.target.closest('[data-book-action]')?.dataset.bookAction;
   if (action === 'toggle-toc' || action === 'dock-toc') {
    shell.open = action === 'dock-toc' || !shell.open;
    tocOpen = shell.open;
    if (action === 'dock-toc') query('.book-dock-menu').open = false;
    if (shell.open) { shell.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); query('#book-toc-search').focus({ preventScroll: true }); }
   }
   if (action === 'retry-image') { status.hidden = false; status.textContent = '正在载入本页…'; retry.hidden = true; image.hidden = false; image.src = page.path; }
  };
  if (pendingTurn) {
   const turn = pendingTurn; pendingTurn = null;
   requestAnimationFrame(() => {
    if (!container.isConnected) return;
    query('.book-current-page').scrollIntoView({ block: 'start', behavior: 'instant' });
    query(turn === 'jump' ? '.book-dock-menu > summary' : '.book-page-dock a[data-book-turn="' + turn + '"]')?.focus({ preventScroll: true });
   });
  }
 }
 document.addEventListener('click', event => {
  const menu = document.querySelector('.book-dock-menu[open]');
  if (menu && !menu.contains(event.target)) menu.open = false;
 });
 window.addEventListener('keydown', event => {
  if (event.defaultPrevented || event.ctrlKey || event.metaKey || event.altKey || event.shiftKey || event.isComposing || !['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
  if (document.querySelector('dialog[open]') || event.target.closest('input,textarea,select,[contenteditable]:not([contenteditable="false"])') || !window.getSelection()?.isCollapsed) return;
  const target = document.querySelector('.book-page-dock a[data-book-turn="' + (event.key === 'ArrowLeft' ? 'prev' : 'next') + '"]');
  if (target) { event.preventDefault(); target.click(); }
 });
 return { render, bind };
};
