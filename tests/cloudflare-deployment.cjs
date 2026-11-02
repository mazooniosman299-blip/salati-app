'use strict';
// This separate web-only preview must not masquerade as a signed Android release.
if(process.env.CF_PAGES_BRANCH==='preview/salati-madinah-reader-review-20261102'){
 const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');const root=path.resolve(__dirname,'..');const read=p=>fs.readFileSync(path.join(root,p),'utf8');const page=read('dist/index.html'),ui=read('dist/salati-ui.css'),js=read('dist/app-v1.0.109.js'),headers=read('dist/_headers');
 assert(page.includes('id="mushafPlayerSlot"')&&page.includes('id="qVerses"'),'Missing Quran/player');assert(page.indexOf('id="qSheet"')<page.indexOf('id="mushafPlayerSlot"')&&page.indexOf('id="mushafPlayerSlot"')<page.indexOf('</article>'),'Audio player must be INSIDE the Quran reading frame');assert(ui.includes('.quran-madinah-plate'),'Madinah print stylesheet missing');
 assert(ui.includes('top:50%;left:50%'),'Madinah player must be centered on page');
 assert(js.includes('files.quran.app/hafs/madani/width_1024/page'),'Original printed Madani layout must be in bundled JS');assert(js.includes('cdn.quran.ws/svg/pages/v1.1.1/hafs-kfqc'),'Actual Madinah/KFQC SVG viewer absent');assert(!page.includes('href="/downloads/salati-'),'Old APK offered on preview');assert(headers.includes('noindex, nofollow'),'Preview index protection missing');assert(read('dist/robots.txt').includes('Disallow: /'),'Preview must not be indexed');console.log('PASS web-only Madinah Mushaf preview: printed plates, player with Quran, no old APK, noindex');process.exit(0);
}

const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.join(__dirname,'..'),dist=path.join(root,'dist');
const origin=process.env.SALATI_PUBLIC_ORIGIN||(()=>{
  const u=process.env.CF_PAGES_URL;
  if(!u)throw Error('Set SALATI_PUBLIC_ORIGIN for verification');
  const host=new URL(u).hostname.split('.');
  return 'https://'+host.slice(-3).join('.');
})();
const read=p=>fs.readFileSync(path.join(dist,p),'utf8');
const home=read('index.html'),map=read('sitemap.xml'),robots=read('robots.txt');
const sw=read('sw.js'),header=read('_headers');
const pointer=JSON.parse(fs.readFileSync(path.join(root,'apk-release-parts/current.json'),'utf8'));
assert(/^1\.0\.\d+$/.test(pointer.version),'Invalid current verified release pointer');
const version=pointer.version;
const versionNumber=Number(version.split('.').pop());
const folder=path.join(root,'apk-release-parts','v'+version);
const manifest=JSON.parse(fs.readFileSync(path.join(folder,'manifest.json'),'utf8'));
assert(manifest.version===version && manifest.versionCode===versionNumber+1,
 'Android release identity/versionCode does not match public version');
assert(manifest.applicationId==='com.salati.prayer');
assert(manifest.certificateSha256==='559dec66ab13e86be17c661732f1d2b1751a63261ed7d7d353b857f693cf056e');
assert(home.includes('rel="canonical" href="'+origin+'/"'),'Incorrect homepage canonical URL');
assert(home.includes('property="og:url" content="'+origin+'/"'),'Social sharing URL must use Cloudflare hostname');
assert(map.includes('<loc>'+origin+'/</loc>'),'Sitemap homepage must point to deployed host');
assert(!map.includes('salati-world-prayer.sprytitan65.chatgpt.site'),'Old sitemap domain detected');
assert(robots.includes('Sitemap: '+origin+'/sitemap.xml'),'Robots must reference new sitemap');
assert(header.includes('/sw.js') && header.includes('no-cache'),'Service worker must not be permanently cached');
for(const name of ['index.html','privacy.html','sitemap.xml','robots.txt']){
 assert(!read(name).includes('salati-world-prayer.sprytitan65.chatgpt.site'),name+' contains old canonical host');
}
const swVersion=sw.match(/salati-shell-v(\d+)/);
assert(swVersion && Number(swVersion[1])>=179,'Offline cache revision is too old for current release');
assert(sw.includes('./salati-ui.css'),'Offline app shell must include canonical CSS');
for(const asset of ['manifest.json','app-v1.0.109.js','salati-ui.css',
 'quran-mushaf-markers-20261101.js','images/mosque-reference-original.png',
 'fonts/AmiriQuran-Regular.ttf','quran/data.json']){
 assert(fs.statSync(path.join(dist,asset)).size>0,'Missing current app asset: '+asset);
}
const styles=read('salati-ui.css');
assert(styles.startsWith('@layer salati-base,salati-priority;'),'CSS cascade layers not preserved');
assert(!styles.includes('!important'),'CSS priority flags unexpectedly restored');
const urls=[...map.matchAll(/<loc>([^<]+)<\/loc>/g)].map(x=>x[1]);
assert(urls.length>=12,'City sitemap entries absent');
for(const url of urls){
 assert(url.startsWith(origin+'/'),'Foreign sitemap hostname: '+url);
 const rel=new URL(url).pathname.slice(1);
 assert(fs.existsSync(path.join(dist,rel||'index.html')),'Sitemap page missing: '+rel);
}
const apkName='salati-'+version+'.apk',apkUrl='/downloads/'+apkName;
assert(home.includes('href="'+apkUrl+'"'),'Website APK link points to stale version');
assert(home.includes('class="app-version">v'+version+'</small>'),'Website version label is stale');
assert(header.includes('Content-Disposition: attachment; filename="'+apkName+'"'),
 'APK must be served as a downloaded Android archive');
const apkPath=path.join(dist,'downloads',apkName);
assert(fs.existsSync(apkPath),'Cloudflare bundle missing exact signed release APK');
const hash=crypto.createHash('sha256');let total=0;
for(let i=0;i<manifest.partCount;i++){
 const chunk=fs.readFileSync(path.join(folder,'part'+String(i).padStart(2,'0')+'.bin'));
 hash.update(chunk);total+=chunk.length;
}
assert(total===manifest.size && hash.digest('hex')===manifest.sha256,
 'Original-key signed APK chunks do not match verified release manifest');
const signed=fs.readFileSync(apkPath);
assert(signed.length===manifest.size,'Hosted APK size mismatch');
assert(crypto.createHash('sha256').update(signed).digest('hex')===manifest.sha256,
 'Hosted APK SHA-256 differs from verified original-key release');
assert(read('ar/prayer-times/muscat.html').includes(origin+'/'),
 'Generated Arabic prayer-time pages must use correct Cloudflare origin');
console.log('PASS Cloudflare release '+version+'; Android code '+manifest.versionCode+
 ', original certificate, bytes/SHA256, zero-!important CSS, PWA '+swVersion[1]+
 ', SEO routes '+urls.length+', site '+origin);
