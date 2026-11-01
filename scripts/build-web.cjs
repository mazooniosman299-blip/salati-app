require('./build-navigation.cjs');
require('./build-world-cities.cjs');
const fs=require('node:fs'),path=require('node:path');const root=path.resolve(__dirname,'..');const html=fs.readFileSync(path.join(root,'dist/index.html'),'utf8');const target=html.match(/src="(app(?:-v[\d.]+)?\.js)(?:\?[^"]*)?"/);if(!target)throw Error('Missing versioned app entry');const outfile=path.join(root,'dist',target[1]);require('esbuild').buildSync({entryPoints:[path.join(root,'app-source.js')],bundle:true,minify:true,outfile});if(target[1]!=='app.js')fs.copyFileSync(outfile,path.join(root,'dist/app.js'));console.log('Built '+target[1]);

// ONE canonical UI source after migration. The legacy versioned layout is
// supported only while bootstrapping older branches. Once salati-ui.css is
// linked, never generate -v*.css or add another stylesheet to the homepage.
const currentHtml=fs.readFileSync(path.join(root,'dist/index.html'),'utf8');
const canonicalLinked=currentHtml.includes('href="salati-ui.css"');
if(canonicalLinked){
 if(!fs.existsSync(path.join(root,'dist/salati-ui.css')))throw Error('Canonical salati-ui.css is missing');
 const linked=[...currentHtml.matchAll(/<link\\s+rel="stylesheet"\\s+href="([^"]+\\.css)"\\s*>/g)].map(m=>m[1]);
 if(linked.join('|')!=='salati-ui.css|/city-pages.css')throw Error('STOP: new CSS overlay was linked; edit salati-ui.css instead');
 console.log('Canonical Salati UI stylesheet enabled; no legacy versioned CSS generated.');
}else{
 // Legacy bootstrap only. Removed from production after canonical migration.
 const version=target[1].match(/app-v([\\d.]+)\\.js/)[1];
 let legacyHtml=currentHtml;
 for(const name of ['style','light-theme','salati-design','reference-layout']){
  const filename=name+'-v'+version+'.css';
  fs.copyFileSync(path.join(root,'dist',name+'.css'),path.join(root,'dist',filename));
  const pattern=new RegExp('href="'+name+'(?:-v[\\\\d.]+)?\\\\.css"','g');
  legacyHtml=legacyHtml.replace(pattern,'href="'+filename+'"');
 }
 fs.writeFileSync(path.join(root,'dist/index.html'),legacyHtml);
}
require('./build-city-pages.cjs');

// Permanent dark first paint on all first-party HTML pages, even before JS or styles load.
function forceDarkPages(directory){for(const entry of fs.readdirSync(directory,{withFileTypes:true})){if(entry.name==='downloads')continue;const file=path.join(directory,entry.name);if(entry.isDirectory())forceDarkPages(file);else if(entry.name.endsWith('.html')){let text=fs.readFileSync(file,'utf8');text=text.replace(/<body([^>]*)>/i,(_,attrs)=>{if(/class="/.test(attrs))attrs=attrs.replace(/class="([^"]*)"/,(_,classes)=>'class="'+[...new Set((classes+' dark').split(/\s+/))].join(' ')+'"');else attrs+=' class="dark"';return '<body'+attrs+'>';});if(!text.includes('html,body{background:#0B0E13'))text=text.replace(/<head>/i,'<head><style>html,body{background:#0B0E13;color:#FFFFFF;color-scheme:dark}</style>');fs.writeFileSync(file,text);}}}forceDarkPages(path.join(root,'dist'));
