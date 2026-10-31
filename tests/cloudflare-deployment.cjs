'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.join(__dirname,'..','dist');
const origin=process.env.SALATI_PUBLIC_ORIGIN||(()=>{const u=process.env.CF_PAGES_URL;if(!u)throw Error('Set SALATI_PUBLIC_ORIGIN for verification');const host=new URL(u).hostname.split('.');return 'https://'+host.slice(-3).join('.');})();
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const home=read('index.html'),map=read('sitemap.xml'),robots=read('robots.txt'),sw=read('sw.js'),header=read('_headers');
assert(home.includes('rel="canonical" href="'+origin+'/"'),'Homepage must point to new canonical URL');
assert(home.includes('property="og:url" content="'+origin+'/"'),'Social sharing URL must use Cloudflare hostname');
assert(map.includes('<loc>'+origin+'/</loc>'),'Sitemap homepage must point to deployed host');
assert(!map.includes('salati-world-prayer.sprytitan65.chatgpt.site'),'Old sitemap domain detected');
assert(robots.includes('Sitemap: '+origin+'/sitemap.xml'),'Robots must reference new sitemap');
assert(header.includes('/sw.js')&&header.includes('no-cache'),'Service worker updates must remain fresh');
for(const f of ['index.html','privacy.html','sitemap.xml','robots.txt']){
  assert(!read(f).includes('salati-world-prayer.sprytitan65.chatgpt.site'),f+' contains old host');
}
assert(sw.includes("salati-shell-v147"),'Offline cache revision must include latest verified PWA release');
for(const asset of ['manifest.json','app-v1.0.109.js','reference-layout-v1.0.109.css',
'light-theme-v1.0.109.css','images/mosque-reference-original.png',
'fonts/AmiriQuran-Regular.ttf','quran/data.json']){
  assert(fs.statSync(path.join(root,asset)).size>0,'Essential Salati asset missing: '+asset);
}
let urls=[...map.matchAll(/<loc>([^<]+)<\/loc>/g)].map(x=>x[1]);
assert(urls.length>=12,'City sitemap entries absent');
for(const url of urls){
  assert(url.startsWith(origin+'/'),'Sitemap contains foreign hostname: '+url);
  const rel=new URL(url).pathname.slice(1);
  assert(fs.existsSync(path.join(root,rel||'index.html')),'Sitemap page is missing: '+rel);
}
const out=read('ar/prayer-times/muscat.html');
assert(out.includes(origin+'/'),'Generated public city pages must point to Cloudflare hostname');
console.log('PASS: Cloudflare domain',origin,'sitemap routes',urls.length,'PWA assets and offline code, caching, canonical and privacy.');
