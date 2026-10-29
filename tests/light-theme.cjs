const assert=require('node:assert/strict'),fs=require('node:fs'),esbuild=require('esbuild');
const css=fs.readFileSync('dist/light-theme.css','utf8'),main=fs.readFileSync('dist/style.css','utf8');esbuild.transformSync(css,{loader:'css'});esbuild.transformSync(main,{loader:'css'});
const root=css.match(/:root\{([^}]+)\}/)[1],colors=Object.fromEntries([...root.matchAll(/--([a-z-]+):(#\w+)/g)].map(m=>[m[1],m[2]]));
assert.equal(colors.bg,'#ffffff');assert.equal(colors.card,'#ffffff');assert.equal(colors.ink,'#000000');assert.equal(colors.muted,'#000000');
const dark=Object.fromEntries([...css.match(/body\.dark\{([^}]+)\}/)[1].matchAll(/--([a-z-]+):(#\w+)/g)].map(m=>[m[1],m[2]]));assert.equal(dark.ink,'#ffffff');assert.equal(dark.muted,'#ffffff');
function luminance(hex){const values=hex.slice(1).match(/../g).map(s=>parseInt(s,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return .2126*values[0]+.7152*values[1]+.0722*values[2];}
function contrast(a,b){const values=[luminance(a),luminance(b)].sort((x,y)=>y-x);return (values[0]+.05)/(values[1]+.05);}
for(const background of [colors.bg,colors.card,'#ffffff']){assert(contrast(colors.ink,background)>=12);assert(contrast(colors.muted,background)>=7);assert(contrast(colors.line,background)>=3);}
assert(contrast('#000000','#ffffff')>=7);assert(contrast(colors.gold,colors.card)>=4.5);assert(contrast('#000000','#ffffff')>=4.5);
assert(!/(?:body:not\(\.dark\)|:root)\{[^}]*--(?:bg|card|ink|muted|line|gold):/.test(main),'Light-mode palette must not be overridden elsewhere');
assert(main.includes('font-family:SalatiCairo,Tahoma,Arial,sans-serif;font-size:17px;font-weight:700;font-synthesis:none'));
assert(main.includes('font-weight:200 1000'));assert(fs.statSync('dist/fonts/Cairo-Variable.ttf').size>0);assert(!css.includes('font-weight:400'));assert(!css.includes('SalatiArabic'));
assert(!/body\.dark\{[^}]*--/.test(main),'Theme palettes must be defined in one stylesheet');
assert.equal((main.match(/\.prayer\.active\{/g)||[]).length,1);assert(!css.includes('.prayer.active'));
assert(main.includes('.prayer.active{border:3px solid var(--prayer-highlight);background:var(--card)}'));
assert(contrast(colors['prayer-highlight'],colors.card)>=4.5);assert(contrast(dark['prayer-highlight'],dark.card)>=4.5);assert.notEqual(colors['prayer-highlight'],colors.gold);
assert(css.includes('.prayer-switches input[type=checkbox]:checked{background:var(--control-fill);border-color:var(--control-fill)}'));for(const theme of [colors,dark])assert(contrast(theme['control-ink'],theme['control-fill'])>=4.5,'Checked switches and filled controls must contrast with their actual foreground labels/thumbs');
assert(main.includes('grid-template-columns:minmax(0,1fr);align-items:start'));assert(main.includes('font-family:SalatiMadinahClassic,AmiriQuran,serif'));
assert(!main.includes('.verse-audio-dialog'));assert(!fs.readFileSync('quran-controller.js','utf8').includes('verseAudioPlay'));assert(/href="light-theme(?:-v[\d.]+)?\.css"/.test(fs.readFileSync('dist/index.html','utf8')));
console.log('PASS: single theme palette; bold Cairo UI in both themes; 21:1 light text contrast; prayer highlight contrast >=4.5:1 in both themes; Quran face/weight preserved; content-height cards and compact verse list retained.');
