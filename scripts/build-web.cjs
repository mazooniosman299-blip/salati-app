require('./build-world-cities.cjs');
const fs=require('node:fs'),path=require('node:path');const root=path.resolve(__dirname,'..');const html=fs.readFileSync(path.join(root,'dist/index.html'),'utf8');const target=html.match(/src="(app(?:-v[\d.]+)?\.js)(?:\?[^"]*)?"/);if(!target)throw Error('Missing versioned app entry');const outfile=path.join(root,'dist',target[1]);require('esbuild').buildSync({entryPoints:[path.join(root,'app-source.js')],bundle:true,minify:true,outfile});if(target[1]!=='app.js')fs.copyFileSync(outfile,path.join(root,'dist/app.js'));console.log('Built '+target[1]);

require('./build-city-pages.cjs');
