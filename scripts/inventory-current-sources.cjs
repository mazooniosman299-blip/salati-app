#!/usr/bin/env node
'use strict';
/** Inventory real loaded shell, CSS and esbuild upstream import graph. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {execFileSync}=require('node:child_process');
const ROOT=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(ROOT,'dist/index.html'),'utf8');
const links=[...html.matchAll(/<link\b[^>]*\brel=["']stylesheet["'][^>]*\bhref=["']([^"']+)["']/ig)].map(x=>x[1]);
const scripts=[...html.matchAll(/<script\b[^>]*\bsrc=["']([^"']+)["']/ig)].map(x=>x[1]);
assert.deepEqual(links,['salati-ui.css'],'Active project must load only canonical CSS');
assert(scripts.some(x=>/^app(?:-v[\d.]+)?\.js$/.test(x)),'Missing actual esbuild application bundle');
assert(scripts.every(x=>fs.existsSync(path.join(ROOT,'dist',x.split('?')[0]))),'Linked runtime JavaScript is absent');
const active=new Set(),missing=[],edges=[];
function crawl(file) {
 const abs=path.resolve(ROOT,file);
 if(active.has(file))return;
 active.add(file);
 assert(abs.startsWith(ROOT+path.sep),'JS module escaped repository: '+file);
 if(!fs.existsSync(abs)){missing.push(file);return;}
 const content=fs.readFileSync(abs,'utf8');
 const pattern=/(?:import|export)\s*(?:[^;\n]*?\sfrom\s*)?["'](\.[^"']+)["']|import\(\s*["'](\.[^"']+)["']\s*\)/g;
 for(const m of content.matchAll(pattern)){
  const target=m[1]||m[2];
  let absolute=path.resolve(path.dirname(abs),target);
  if(!path.extname(absolute))absolute+='.js';
  const rel=path.relative(ROOT,absolute).replace(/\\/g,'/');
  edges.push({from:file,to:rel});
  crawl(rel);
 }
}
crawl('app-source.js');
assert.equal(missing.length,0,'Missing actual application upstream imports '+missing.join(', '));
const tracked=execFileSync('git',['ls-files','-z'],{cwd:ROOT,encoding:'utf8'}).split('\0').filter(Boolean);
const classif={active_upstream_js:[],active_shell_css:[],generated_runtime:[],native_android:[],historical_or_preview:[],tests:[],documentation:[],other:[]};
const runtime=new Set(['dist/index.html','dist/salati-ui.css',...scripts.map(x=>'dist/'+x),...active]);
for(const file of tracked){
 if(active.has(file))classif.active_upstream_js.push(file);
 else if(file==='dist/index.html'||file==='dist/salati-ui.css')classif.active_shell_css.push(file);
 else if(scripts.map(s=>'dist/'+s).includes(file))classif.generated_runtime.push(file);
 else if(file.startsWith('android/'))classif.native_android.push(file);
 else if(file.startsWith('tests/'))classif.tests.push(file);
 else if(/^(?:docs\/|design-references\/)/.test(file)||/^(?:README|AGENTS|design-qa)\.md$/.test(file))classif.documentation.push(file);
 else if(/(?:-v1\.0\.\d+|preview-|reference-layout|light-theme|design-restoration)/.test(file))classif.historical_or_preview.push(file);
 else classif.other.push(file);
}
const result={
 inspected_commit:execFileSync('git',['rev-parse','HEAD'],{cwd:ROOT,encoding:'utf8'}).trim(),
 linked_css:links,linked_scripts:scripts,source_entry:'app-source.js',
 source_graph_count:active.size,import_edges:edges,
 release_version:JSON.parse(fs.readFileSync(path.join(ROOT,'apk-release-parts/current.json'),'utf8')).version,
 verified_source_files:[...active].sort(),
 inventory_totals:Object.fromEntries(Object.entries(classif).map(([k,v])=>[k,v.length])),
 files_by_category:classif,
 disclaimer:'Static imports and linked assets are verified; conditional DOM regeneration, browser behavior and visual parity require runtime tests.'
};
const out=path.join(ROOT,'reports/active-source-map.json');
fs.mkdirSync(path.dirname(out),{recursive:true});
fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');
console.log('PASS active source graph',result.source_graph_count,'upstream modules,',edges.length,'relative edges,',
 tracked.length,'tracked files; direct linked assets exist. No visual parity claim.');
