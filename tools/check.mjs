import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=await fs.readFile(path.join(root,'dist/data.js'),'utf8');
const d=JSON.parse(source.slice(source.indexOf('=')+1).trim().replace(/;$/,''));
const context={module:{exports:{}},exports:{},console};context.exports=context.module.exports;
vm.runInNewContext(await fs.readFile(path.join(root,'dist/vendor/katex.min.js'),'utf8'),context);
const katex=context.module.exports;
const qs=d.exams.flatMap(e=>e.questions),drills=d.training,book=d.oppenheim;
const sources=d.resources||[],methods=d.alternativeMethods||[],guides=d.studyGuides||[];
const examMethods=d.examMethods||[];
const references=d.textbookReferences||{},bookOriginals=references.exercises||[],bookConcepts=references.concepts||[];
const handbook=d.referenceHandbook?.cards||[];
const textbookReader=d.textbookReader;
assert.equal(textbookReader?.pages?.length,628,'The complete uploaded book has 628 PDF pages');
assert.equal(textbookReader.pdfPageCount,628);
assert.equal(textbookReader.toc.length,302,'Preserve all original book bookmarks');
assert.equal(new Set(textbookReader.pages.map(p=>p.pdfPage)).size,628);
for(let i=0;i<textbookReader.pages.length;i++){
 const p=textbookReader.pages[i];assert.equal(p.pdfPage,i+1,'Book pages must remain in source order');
 assert.ok(p.width>0&&p.height>0&&p.path.startsWith('references/textbook/'),'Invalid book image '+p.pdfPage);
 assert.ok((await fs.stat(path.join(root,'dist',p.path))).size>100,'Missing book image '+p.pdfPage);
 if(p.printPage!==null)assert.equal(p.printPage,p.pdfPage-22,'Incorrect printed page '+p.pdfPage);
}
assert.equal(textbookReader.pages[0].printPage,null,'Cover is not printed page -21');
assert.equal(textbookReader.pages.at(-1).printPage,null,'File-information leaf has no book page');
for(const t of textbookReader.toc)assert.ok(t.title&&t.pdfPage>=1&&t.pdfPage<=628,'Invalid original bookmark');
assert.equal(new URL(textbookReader.download.path).protocol,'https:');
const serviceWorker=await fs.readFile(path.join(root,'dist/sw.js'),'utf8');
const precacheMatch=serviceWorker.match(/const ASSETS=(\[[\s\S]*?\]);self/);
assert.ok(precacheMatch,'Missing offline asset list');
assert.ok(!JSON.parse(precacheMatch[1]).some(p=>p.startsWith('references/textbook/')),'Do not preload the entire textbook on website install');
assert.equal(qs.length,243);assert.equal(new Set(qs.map(q=>q.id)).size,243);assert.equal(drills.length,32);assert.equal(d.oppenheim.length,40);
assert.equal(new Set([...qs,...drills,...book].map(q=>q.id)).size,315);
const questionIds=new Set([...qs,...drills,...book].map(q=>q.id));
const condensed=d.textbookCondensed;
assert.equal(condensed?.chapters?.length,12,'The brief needs all 11 original chapters and the labeled supplement');
assert.equal(new Set(condensed.chapters.map(c=>c.chapter)).size,12,'Duplicate condensed chapter');
assert.equal(new Set(condensed.auditedBodyPdfPages).size,401,'Check all chapter body and summary pages');
for(const c of condensed.chapters){
 assert.ok(c.title&&c.coreIdea&&c.readAudit?.bodyPdfPages?.length,c.id+' missing source reading record');
 assert.ok(c.essentials.length>=3&&c.essentials.length<=4,c.id+' should stay concise');
 assert.ok(c.firstSteps.length<=3&&c.firstSteps.length>0&&c.pitfalls.length===2,c.id+' invalid brief structure');
 assert.ok(c.miniExample?.body&&c.selfCheck?.question&&c.selfCheck?.answer,c.id+' missing usable example/check');
 for(const id of c.examIds)assert.ok(questionIds.has(id),c.id+' unknown example '+id);
 for(const b of c.bookLinks)assert.ok(b.pdfPage>=1&&b.pdfPage<=628,c.id+' invalid book link');
 for(const s of c.sourceSpans)assert.ok(s.pdfFrom===s.printFrom+22&&s.pdfTo===s.printTo+22,c.id+' incorrect source page mapping');
 const visible=JSON.stringify({coreIdea:c.coreIdea,essentials:c.essentials,firstSteps:c.firstSteps,miniExample:c.miniExample,pitfalls:c.pitfalls,selfCheck:c.selfCheck});
 assert.ok((visible.match(/[\u4e00-\u9fff]/g)||[]).length<=1200,c.id+' is too long for the brief');
 assert.ok(!/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(visible),c.id+' bad text control character');
}
assert.equal(bookOriginals.length,40,'Each selected exercise needs its actual original');
assert.equal(new Set(bookOriginals.map(b=>b.id)).size,40);
const coveredConcepts=new Set(bookConcepts.flatMap(c=>c.topicCodes));
for(const t of d.topics)assert.ok(coveredConcepts.has(t.code),'Missing textbook basis for '+t.code);
for(const r of [...bookOriginals,...bookConcepts,...(references.relationExcerpts||[]),...(references.handbookCards||[])]){
 assert.ok(r.excerpts?.length,r.id+' missing original image');
 for(const f of r.excerpts){
  assert.ok(f.pdfPage>0&&f.pdfPage<=references.book.pdfPages,r.id+' invalid PDF page');
  assert.ok(f.width>0&&f.height>0,r.id+' invalid image dimensions');
  for(const pathName of [f.path,f.thumb])assert.ok((await fs.stat(path.join(root,'dist',pathName))).size>100,r.id+' missing/empty original image');
 }
}
assert.ok(handbook.length>=40,'Formula and method handbook must be substantive');
assert.equal(new Set(handbook.map(c=>c.id)).size,handbook.length,'Duplicate handbook IDs');
for(const kind of ['definition','formula','property','table','common','special'])assert.ok(handbook.some(c=>c.category===kind),'Missing handbook category '+kind);
for(const chapter of ['3','4','5','9','10'])assert.ok(handbook.some(c=>c.category==='table'&&String(c.chapter)===chapter),'Missing original transform/property table '+chapter);
for(const c of handbook){
 assert.ok(c.title&&c.formula&&c.explanation&&c.memory&&c.conditions&&c.pitfalls,c.id+' incomplete revision aid');
 assert.ok(['definition','formula','property','table','common','special'].includes(c.category),c.id+' unknown category');
 assert.ok(c.exampleIds?.length,c.id+' missing worked example');
 for(const id of c.exampleIds)assert.ok(questionIds.has(id),c.id+' unknown example '+id);
 const refs=[...(references.handbookCards||[]).filter(r=>r.id===c.id),...(c.conceptIds||[]).map(id=>bookConcepts.find(r=>r.id===id))];
 assert.ok(refs.length&&refs.every(r=>r?.excerpts?.length),c.id+' missing authentic original basis');
 for(const p of c.diagramPaths||[])assert.ok((await fs.stat(path.join(root,'dist/assets',path.basename(p)))).size>100,c.id+' missing diagram');
}
for(const r of references.relations||[]){
 assert.ok(questionIds.has(r.questionId),'Unknown matching question '+r.questionId);
 assert.ok(['同题','结构相似','同知识点'].includes(r.kind),'Unclassified textbook match');
 assert.ok(r.explanation&&r.scope&&r.confidence==='verified','Unverified textbook match '+r.questionId);
 if(r.exerciseId)assert.ok(bookOriginals.some(b=>b.id===r.exerciseId),'Unknown matched textbook exercise');
 else assert.ok((references.relationExcerpts||[]).some(b=>b.id===r.excerptId),'Missing source crop for extra matched exercise');
}
const sourceIds=new Set(sources.map(r=>r.id));
const examIds=new Set(qs.map(q=>q.id)),methodIds=new Map(methods.map(m=>[m.id,m]));
assert.equal(examMethods.length,qs.length,'Every visible exam group needs a method synthesis');
assert.equal(new Set(examMethods.map(m=>m.targetId)).size,qs.length,'Method synthesis must map each exam once');
for(const m of examMethods){
 const scan=value=>{if(typeof value==='string')assert.ok(!/[\x00-\x09\x0B-\x1F]/.test(value),m.targetId+' contains an accidental control character');else if(Array.isArray(value))value.forEach(scan);else if(value&&typeof value==='object')Object.values(value).forEach(scan);};scan(m);
 assert.ok(examIds.has(m.targetId),m.targetId+' unknown exam');
 assert.ok(m.scope&&m.comparison&&m.recommended?.title&&m.recommended.why,m.targetId+' missing question-specific guidance');
 assert.ok(m.recommended.steps?.length>=3,m.targetId+' needs concrete recommended steps');
 assert.ok((m.alternatives?.length||0)+(m.existingMethodIds?.length||0)>0,m.targetId+' needs another perspective or check');
 for(const a of m.alternatives||[]){
  assert.ok(['另一解法','等价视角','核验法'].includes(a.kind),m.targetId+' unclassified alternative');
  assert.ok(a.title&&a.whenToUse&&a.steps?.length>=3,m.targetId+' incomplete alternative');
 }
 for(const id of m.existingMethodIds||[])assert.ok(methodIds.get(id)?.targetIds.includes(m.targetId),m.targetId+' mismatched existing method '+id);
 for(const id of m.sourceIds||[])assert.ok(sourceIds.has(id),m.targetId+' unknown source '+id);
}
assert.equal(sourceIds.size,sources.length,'Duplicate course source IDs');
for(const source of sources){
 assert.ok(source.title&&source.evidenceLevel,source.id+' missing provenance');
 assert.equal(new URL(source.url).protocol,'https:',source.id+' unsafe source URL');
 for(const id of source.targetIds||[])assert.ok(questionIds.has(id),source.id+' unknown target '+id);
}
for(const method of methods){
 assert.ok(method.title&&method.derivation?.length>150,method.id+' needs a worked alternative');
 assert.ok(method.targetIds?.length&&method.sourceIds?.length,method.id+' needs question/source mapping');
 for(const id of method.targetIds)assert.ok(questionIds.has(id),method.id+' unknown question '+id);
 for(const id of method.sourceIds)assert.ok(sourceIds.has(id),method.id+' unknown source '+id);
}
assert.equal(guides.length,12,'12 chapter digests must be available offline');
assert.equal(new Set(guides.map(g=>g.id)).size,guides.length);
for(const g of guides){
 assert.ok(g.title&&g.summary&&g.body.length>1800,g.id+' needs a self-contained lesson');
 assert.ok(g.quickTakeaways.length>=3&&g.selfCheck.length>=2&&g.pitfalls.length>=3,g.id+' needs takeaways and checks');
 for(const id of g.practiceIds)assert.ok(questionIds.has(id),g.id+' unknown practice '+id);
 for(const id of g.sourceIds)assert.ok(sourceIds.has(id),g.id+' unknown source '+id);
}
for(const q of [...drills,...book]){assert.ok(q.solution.length>300,q.id+' needs a worked solution');assert.ok(!/^(最终表达式|各问具体表达式).*(见|推导)/.test(q.answer),q.id+' needs a concrete answer');}
assert.ok(!(await fs.readFile(path.join(root,'dist/app.js'),'utf8')).includes("replace(/\\$|\\\\[a-zA-Z]+/g"),'Preview must preserve TeX commands');
let errors=[],mathCount=0,figureCount=0;
const handbookChecks=handbook.map(c=>({id:c.id,statement:c.formula,firstStep:c.memory,solution:c.explanation+'\n'+(Array.isArray(c.conditions)?c.conditions.join('\n'):c.conditions),answer:Array.isArray(c.pitfalls)?c.pitfalls.join('\n'):c.pitfalls,training:true,figures:(c.diagramPaths||[]).map(path=>({path}))}));
const condensedChecks=condensed.chapters.map(c=>({id:c.id,statement:c.coreIdea,firstStep:c.firstSteps.map(s=>s.trigger+'\n'+s.action).join('\n'),solution:c.essentials.map(e=>e.title+'\n'+e.explanation+'\n'+e.formula).join('\n'),answer:c.miniExample.title+'\n'+c.miniExample.body+'\n'+c.pitfalls.join('\n')+'\n'+c.selfCheck.question+'\n'+c.selfCheck.answer,training:true}));
for(const q of [...condensedChecks,...handbookChecks,{id:"handbook-notation",statement:d.referenceHandbook.notation,firstStep:"",solution:"",answer:"",training:true},...qs,...drills,...book,...methods.map(m=>({id:m.id,statement:m.why||'',firstStep:m.whenToUse||'',solution:m.derivation,answer:m.check||'',training:true})),...guides.map(g=>({id:g.id,statement:g.summary,firstStep:g.quickTakeaways.join('\n'),solution:g.body,answer:g.selfCheck.join('\n'),pitfalls:g.pitfalls,training:true})),...examMethods.map(m=>({id:m.targetId+'-methods',statement:m.scope,firstStep:m.recommended.why,solution:m.recommended.steps.join('\n')+'\n'+(m.alternatives||[]).map(a=>a.whenToUse+'\n'+a.steps.join('\n')).join('\n'),answer:m.comparison,training:true})),...bookConcepts.map(c=>({id:c.id,statement:c.summary,firstStep:c.coverageNote||'',solution:'',answer:'',training:true})),...(references.relations||[]).map((r,i)=>({id:'book-relation-'+i,statement:r.scope,firstStep:'',solution:r.explanation,answer:'',training:true}))]){
 for(const field of ['statement','firstStep','solution','answer',...(q.pitfalls||[]).map((_,i)=>'pitfall'+i)]){
  const value=field.startsWith('pitfall')?q.pitfalls[+field.slice(7)]:q[field];
  assert.equal(typeof value,'string',q.id+' '+field);
  for(const match of value.matchAll(/\$\$([\s\S]*?)\$\$|(?<!\\)\$([^$\n]+)\$|\\\[([\s\S]*?)\\\]|\\\(([\s\S]*?)\\\)/g)){
   const tex=match[1]??match[2]??match[3]??match[4];mathCount++;
   try{katex.renderToString(tex,{throwOnError:true,strict:'ignore',macros:{'\\sinc':'\\operatorname{sinc}','\\sgn':'\\operatorname{sgn}','\\rect':'\\operatorname{rect}','\\Sa':'\\operatorname{Sa}'}});}catch(e){errors.push({id:q.id,field,tex,error:e.message});}
  }
 }
 for(const f of q.figures||[]){let name=typeof f==='string'?f:f.path||f.file||f.src;assert.ok(name,q.id);await fs.access(path.join(root,'dist/assets',path.basename(name)));figureCount++;}
 if(!q.training&&!q.textbook)for(const p of q.sourcePages||[])for(const suffix of ['','-thumb'])assert.ok((await fs.stat(path.join(root,`dist/sources/${q.year}_${p}${suffix}.webp`))).size>100,'Empty original page '+q.year+' '+p);
}
for(const c of d.chapters){let list=qs.filter(q=>q.chapters.includes(c.chapter));assert.equal(list.length,c.count,c.chapter);assert.equal(new Set(list.map(q=>q.year)).size,c.year_count,c.chapter);}
await fs.writeFile(path.join(root,'content/math-check.json'),JSON.stringify(errors,null,2));
console.log(JSON.stringify({condensedChapters:condensed.chapters.length,condensedBodyPages:condensed.auditedBodyPdfPages.length,handbookCards:handbook.length,handbookTables:handbook.filter(c=>c.category==='table').length,questions:qs.length,examMethodSyntheses:examMethods.length,training:drills.length,textbookGroups:book.length,textbookOriginals:bookOriginals.length,conceptCards:bookConcepts.length,topicCoverage:coveredConcepts.size,textbookRelations:references.relations?.length,alternativeMethods:methods.length,courseDigests:guides.length,courseSources:sources.length,formulaExpressions:mathCount,figureReferences:figureCount,formulaErrors:errors.length,examples:errors.slice(0,12)}));
if(errors.length)process.exitCode=1;
