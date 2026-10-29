require('./build-navigation.cjs');
require('./build-world-cities.cjs');
const fs=require('node:fs'),path=require('node:path');const root=path.resolve(__dirname,'..');const html=fs.readFileSync(path.join(root,'dist/index.html'),'utf8');const target=html.match(/src="(app(?:-v[\d.]+)?\.js)(?:\?[^"]*)?"/);if(!target)throw Error('Missing versioned app entry');const outfile=path.join(root,'dist',target[1]);require('esbuild').buildSync({entryPoints:[path.join(root,'app-source.js')],bundle:true,minify:true,outfile});if(target[1]!=='app.js')fs.copyFileSync(outfile,path.join(root,'dist/app.js'));console.log('Built '+target[1]);

// Version every app stylesheet with the entrypoint so browser caches cannot mix releases.
const version=target[1].match(/app-v([\d.]+)\.js/)[1];
let currentHtml=fs.readFileSync(path.join(root,'dist/index.html'),'utf8');
for(const name of ['style','light-theme','salati-design','reference-layout']){
 const filename=name+'-v'+version+'.css';
 fs.copyFileSync(path.join(root,'dist',name+'.css'),path.join(root,'dist',filename));
 const pattern=new RegExp('href="'+name+'(?:-v[\\d.]+)?\\.css"','g');
 currentHtml=currentHtml.replace(pattern,'href="'+filename+'"');
}
fs.writeFileSync(path.join(root,'dist/index.html'),currentHtml);

require('./build-city-pages.cjs');

// Permanent dark first paint on all first-party HTML pages, even before JS or styles load.
function forceDarkPages(directory){for(const entry of fs.readdirSync(directory,{withFileTypes:true})){if(entry.name==='downloads')continue;const file=path.join(directory,entry.name);if(entry.isDirectory())forceDarkPages(file);else if(entry.name.endsWith('.html')){let text=fs.readFileSync(file,'utf8');text=text.replace(/<body([^>]*)>/i,(_,attrs)=>{if(/class="/.test(attrs))attrs=attrs.replace(/class="([^"]*)"/,(_,classes)=>'class="'+[...new Set((classes+' dark').split(/\s+/))].join(' ')+'"');else attrs+=' class="dark"';return '<body'+attrs+'>';});if(!text.includes('html,body{background:#0B0E13'))text=text.replace(/<head>/i,'<head><style>html,body{background:#0B0E13;color:#FFFFFF;color-scheme:dark}</style>');fs.writeFileSync(file,text);}}}forceDarkPages(path.join(root,'dist'));
