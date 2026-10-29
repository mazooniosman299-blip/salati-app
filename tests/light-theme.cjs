const assert=require('node:assert/strict'),fs=require('node:fs'),esbuild=require('esbuild');
const css=fs.readFileSync('dist/light-theme.css','utf8');esbuild.transformSync(css,{loader:'css'});
const root=css.match(/:root\{([^}]+)\}/)[1],tokens=Object.fromEntries([...root.matchAll(/--([\w-]+):([^;]+)/g)].map(m=>[m[1],m[2]]));
assert.equal(tokens.bg,'#0B0E13');assert.equal(tokens.card,'#15181D');assert.equal(tokens.ink,'#FFFFFF');assert.equal(tokens.muted,'#FFFFFF');assert.equal(tokens.line,'#32383F');assert.equal(tokens['surface-solid'],'#040509');
const html=fs.readFileSync('dist/index.html','utf8'),app=fs.readFileSync('app-source.js','utf8');assert(!html.includes('id="theme"'));assert(html.includes('<body class="dark">'));assert(!app.includes("$('theme')"));assert(!app.includes('state.dark=!state.dark'));assert(fs.readFileSync('settings-restore.js','utf8').includes('dark:true'));
for(const name of ['style','light-theme','salati-design','reference-layout'])assert(!fs.readFileSync('dist/'+name+'.css','utf8').includes('body:not(.dark)'));
assert(!fs.readFileSync('dist/public-page-theme.js','utf8').includes('prefers-color-scheme'));
assert(fs.readFileSync('dist/style.css','utf8').includes('font-family:SalatiMadinahClassic,AmiriQuran,serif'));
console.log('PASS: one permanent exact charcoal palette, no theme switch/system/light path, original Quran font preserved.');
