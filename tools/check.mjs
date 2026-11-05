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
const qs=d.exams.flatMap(e=>e.questions),drills=d.training;
assert.equal(qs.length,243);assert.equal(new Set(qs.map(q=>q.id)).size,243);assert.equal(drills.length,32);assert.equal(d.oppenheim.length,40);
let errors=[],mathCount=0,figureCount=0;
for(const q of [...qs,...drills]){
 for(const field of ['statement','firstStep','solution','answer']){
  assert.equal(typeof q[field],'string',q.id+' '+field);
  for(const match of q[field].matchAll(/\$\$([\s\S]*?)\$\$|(?<!\\)\$([^$\n]+)\$|\\\[([\s\S]*?)\\\]|\\\(([\s\S]*?)\\\)/g)){
   const tex=match[1]??match[2]??match[3]??match[4];mathCount++;
   try{katex.renderToString(tex,{throwOnError:true,strict:'ignore',macros:{'\\sinc':'\\operatorname{sinc}','\\sgn':'\\operatorname{sgn}','\\rect':'\\operatorname{rect}','\\Sa':'\\operatorname{Sa}'}});}catch(e){errors.push({id:q.id,field,tex,error:e.message});}
  }
 }
 for(const f of q.figures||[]){let name=typeof f==='string'?f:f.path||f.file||f.src;assert.ok(name,q.id);await fs.access(path.join(root,'dist/assets',path.basename(name)));figureCount++;}
 if(!q.training)for(const p of q.sourcePages||[])await fs.access(path.join(root,`dist/sources/${q.year}_${p}.webp`));
}
for(const c of d.chapters){let list=qs.filter(q=>q.chapters.includes(c.chapter));assert.equal(list.length,c.count,c.chapter);assert.equal(new Set(list.map(q=>q.year)).size,c.year_count,c.chapter);}
await fs.writeFile(path.join(root,'content/math-check.json'),JSON.stringify(errors,null,2));
console.log(JSON.stringify({questions:qs.length,training:drills.length,formulaExpressions:mathCount,figureReferences:figureCount,formulaErrors:errors.length,examples:errors.slice(0,12)}));
if(errors.length)process.exitCode=1;
