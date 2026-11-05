import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>fs.readFile(path.join(root,p),'utf8').then(JSON.parse);
const catalog=await read('content/catalog.json'), statistics=await read('content/statistics.json');
const learning=await read('content/resources.json');
const guides=await read('content/study-guides.json');
const examMethods=await read('content/exam-methods.json');
const textbookReferences=await read('content/textbook-links.json');
const referenceHandbook=await read('content/reference-handbook.json');
const topics=new Map(statistics.topics.map(t=>[t.code,t]));
const exams=[];
for(let year=2008;year<=2026;year++){
 const exam=await read(`content/${year}.json`);
 const rows=statistics.index.filter(r=>r.year===year);
 if(exam.questions.length!==rows.length)throw Error(`Year ${year}: index mismatch`);
 const refs=new Map(rows.map(r=>[r.question,r]));
 for(let i=0;i<exam.questions.length;i++){
  const q=exam.questions[i], r=refs.get(q.ref);
  if(!r)throw Error(`Unknown question ${year} ${q.ref}`);
  for(const key of ['title','statement','solution','firstStep','answer'])if(!q[key])throw Error(`Empty ${key}: ${year} ${q.ref}`);
  Object.assign(q,{id:`${year}-${String(i+1).padStart(2,'0')}`,year,order:i,codes:r.codes,summary:r.summary,chapters:[...new Set(r.codes.map(c=>topics.get(c).chapter))]});
 }
 if(year===2025)exam.note='现有资料第2、3页重复，未见第4、5题。仅讲解8个可见题组，不补造缺题。';
 if(year===2021)exam.note='整理版题号由七跳至九，按9个可见题组讲解。回波题为直接路径加一次回波。';
 if(year===2026)exam.note='前两PDF页为题面，后附机构解析。本文独立推导，复数内积等条件区别在题内说明。';
 exams.push(exam);
}
await fs.mkdir(path.join(root,'dist/assets'),{recursive:true});
for(const name of await fs.readdir(path.join(root,'content/assets'))){
 if(!['.svg','.png','.jpg','.webp'].includes(path.extname(name))||/\.tmp\.|\.cn-tmp$/.test(name))continue;
 const destination=path.join(root,'dist/assets',name),temporary=destination+'.tmp';
 await fs.writeFile(temporary,await fs.readFile(path.join(root,'content/assets',name)));
 await fs.rename(temporary,destination);
}
const referenceFiles=new Set(['exercises','concepts','relationExcerpts','handbookCards'].flatMap(k=>(textbookReferences[k]||[]).flatMap(e=>e.excerpts.flatMap(f=>[f.path,f.thumb]))));
for(const relativeFile of referenceFiles){
 const file=path.join(root,'content',relativeFile);
 const relative=path.relative(path.join(root,'content/references'),file),destination=path.join(root,'dist/references',relative);
 await fs.mkdir(path.dirname(destination),{recursive:true});await fs.writeFile(destination+'.tmp',await fs.readFile(file));await fs.rename(destination+'.tmp',destination);
}
const data={...catalog,chapters:statistics.chapters,topics:statistics.topics,exams,resources:learning.sources,alternativeMethods:learning.methods,studyGuides:guides.guides,examMethods:examMethods.entries,textbookReferences,referenceHandbook};
const compiled=path.join(root,'dist/data.js');
await fs.writeFile(compiled+'.tmp','window.SIGNAL_DATA='+JSON.stringify(data)+';\n');
await fs.rename(compiled+'.tmp',compiled);
async function walk(dir){let result=[];for(const e of await fs.readdir(dir,{withFileTypes:true})){let p=path.join(dir,e.name);if(e.isDirectory())result.push(...await walk(p));else result.push(p);}return result;}
const files=await walk(path.join(root,'dist'));
const assets=files.filter(p=>!p.endsWith('.apk')&&!p.endsWith('.apk.sha256')&&!p.endsWith('/sw.js')&&!/\.tmp(?:\.|$)|\.cn-tmp$/.test(p)).map(p=>path.relative(path.join(root,'dist'),p).split(path.sep).join('/'));
const digest=crypto.createHash('sha256');
for(const asset of [...assets].sort()){
 digest.update(asset).update(await fs.readFile(path.join(root,'dist',asset)));
}
const hash=digest.digest('hex').slice(0,12);
await fs.writeFile(path.join(root,'dist/sw.js'),`const CACHE='signal-atlas-${hash}';const ASSETS=${JSON.stringify(['./',...assets])};self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting())));self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('signal-atlas-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));self.addEventListener('fetch',e=>{if(e.request.method!=='GET'||new URL(e.request.url).origin!==location.origin||e.request.url.endsWith('.apk'))return;e.respondWith(fetch(e.request).then(r=>{if(r.ok){let copy=r.clone();caches.open(CACHE).then(c=>c.put(e.request,copy));}return r;}).catch(()=>caches.match(e.request)));});`);
console.log(JSON.stringify({years:exams.length,questions:exams.flatMap(e=>e.questions).length,training:data.training.length,assets:assets.length}));
