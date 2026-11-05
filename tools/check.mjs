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
assert.equal(qs.length,243);assert.equal(new Set(qs.map(q=>q.id)).size,243);assert.equal(drills.length,32);assert.equal(d.oppenheim.length,40);
assert.equal(new Set([...qs,...drills,...book].map(q=>q.id)).size,315);
const questionIds=new Set([...qs,...drills,...book].map(q=>q.id));
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
for(const q of [...qs,...drills,...book,...methods.map(m=>({id:m.id,statement:m.why||'',firstStep:m.whenToUse||'',solution:m.derivation,answer:m.check||'',training:true})),...guides.map(g=>({id:g.id,statement:g.summary,firstStep:g.quickTakeaways.join('\n'),solution:g.body,answer:g.selfCheck.join('\n'),pitfalls:g.pitfalls,training:true})),...examMethods.map(m=>({id:m.targetId+'-methods',statement:m.scope,firstStep:m.recommended.why,solution:m.recommended.steps.join('\n')+'\n'+(m.alternatives||[]).map(a=>a.whenToUse+'\n'+a.steps.join('\n')).join('\n'),answer:m.comparison,training:true}))]){
 for(const field of ['statement','firstStep','solution','answer',...(q.pitfalls||[]).map((_,i)=>'pitfall'+i)]){
  const value=field.startsWith('pitfall')?q.pitfalls[+field.slice(7)]:q[field];
  assert.equal(typeof value,'string',q.id+' '+field);
  for(const match of value.matchAll(/\$\$([\s\S]*?)\$\$|(?<!\\)\$([^$\n]+)\$|\\\[([\s\S]*?)\\\]|\\\(([\s\S]*?)\\\)/g)){
   const tex=match[1]??match[2]??match[3]??match[4];mathCount++;
   try{katex.renderToString(tex,{throwOnError:true,strict:'ignore',macros:{'\\sinc':'\\operatorname{sinc}','\\sgn':'\\operatorname{sgn}','\\rect':'\\operatorname{rect}','\\Sa':'\\operatorname{Sa}'}});}catch(e){errors.push({id:q.id,field,tex,error:e.message});}
  }
 }
 for(const f of q.figures||[]){let name=typeof f==='string'?f:f.path||f.file||f.src;assert.ok(name,q.id);await fs.access(path.join(root,'dist/assets',path.basename(name)));figureCount++;}
 if(!q.training&&!q.textbook)for(const p of q.sourcePages||[])await fs.access(path.join(root,`dist/sources/${q.year}_${p}.webp`));
}
for(const c of d.chapters){let list=qs.filter(q=>q.chapters.includes(c.chapter));assert.equal(list.length,c.count,c.chapter);assert.equal(new Set(list.map(q=>q.year)).size,c.year_count,c.chapter);}
await fs.writeFile(path.join(root,'content/math-check.json'),JSON.stringify(errors,null,2));
console.log(JSON.stringify({questions:qs.length,examMethodSyntheses:examMethods.length,newIndependentAlternatives:examMethods.reduce((n,m)=>n+(m.alternatives||[]).filter(a=>a.kind==='另一解法').length,0),training:drills.length,textbookGroups:book.length,alternativeMethods:methods.length,courseDigests:guides.length,courseSources:sources.length,formulaExpressions:mathCount,figureReferences:figureCount,formulaErrors:errors.length,examples:errors.slice(0,12)}));
if(errors.length)process.exitCode=1;
