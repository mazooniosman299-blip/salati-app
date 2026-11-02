#!/usr/bin/env node
'use strict';
// Rebuild the existing Salati app, never generate a replacement landing page.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),dist=path.join(root,'dist');
const OLD=/https:\/\/salati-world-prayer\.(?:sprytitan65|mazenosman968)\.chatgpt\.site/gi;
const maxAssetBytes=25*1024*1024;
function canonicalOrigin(){
  const explicit=process.env.SALATI_PUBLIC_ORIGIN?.trim();
  const value=explicit||process.env.CF_PAGES_URL?.trim();
  if(!value)throw Error('Missing SALATI_PUBLIC_ORIGIN or CF_PAGES_URL. Refusing to publish old SEO hostnames.');
  const parsed=new URL(value);
  if(parsed.protocol!=='https:'||parsed.username||parsed.password||parsed.search||parsed.hash||
     (parsed.pathname&&parsed.pathname!=='/'))throw Error('Public origin must be an HTTPS site root');
  let hostname=parsed.hostname.toLowerCase();
  if(!explicit&&hostname.endsWith('.pages.dev')){
    const labels=hostname.split('.');
    if(labels.length<3)throw Error('Invalid Cloudflare Pages URL: '+hostname);
    hostname=labels.slice(-3).join('.'); // hash.project.pages.dev -> project.pages.dev
  }
  if(!/^[a-z0-9.-]+$/.test(hostname))throw Error('Unsafe public hostname');
  return 'https://'+hostname+(parsed.port?':'+parsed.port:'');
}
const origin=canonicalOrigin();
/* Require an exact-SHA successful GitHub Actions attestation on all public
   Cloudflare Pages production builds. Preview/local builds remain isolated. */
if(process.env.CF_PAGES_BRANCH==='production') {
  const sha=process.env.CF_PAGES_COMMIT_SHA||'';
  if(!/^[a-f0-9]{40}$/i.test(sha))throw Error('BLOCK PRODUCTION: missing or invalid Cloudflare Pages commit SHA');
  require('node:child_process').execFileSync(process.execPath,
    [path.join(root,'scripts/verify-publish-ci.cjs'),sha],{cwd:root,stdio:'inherit',timeout:30000});
}

if(process.env.SALATI_WEB_ALREADY_BUILT!=='1')require('./build-web.cjs');
/*
 * Enforce regression checks inside the deployment build itself, not merely
 * optional GitHub CI. A direct production push must fail closed if either
 * the approved core contracts or any existing JavaScript regression fails.
 * Real Chromium and Android screenshot tests remain required CI checks.
 */
const {execFileSync}=require('node:child_process');
execFileSync(process.execPath,[path.join(root,'tests/permanent-regression-contract.cjs')],{cwd:root,stdio:'inherit'});
execFileSync('npm',['test'],{cwd:root,stdio:'inherit'});
// Release CI builds once, computes its fingerprint and reuses that identical
// output here. Rebuilding again would mutate generated HTML and invalidate
// the signed build's exact-source proof.

// Publish ONLY the signed APK whose version and full web-asset fingerprint
// match this exact website build. The release guard fails deployment otherwise.
// The original private signing key never leaves secure local signing.
const crypto=require('node:crypto');
// Preview-only route. NEVER run on production. No signed APK is distributed
// when the Quran/UI changes are still awaiting user acceptance.
if(process.env.CF_PAGES_BRANCH==='preview/salati-madinah-reader-review-20261102'){
 const homePath=path.join(dist,'index.html');
 let html=fs.readFileSync(homePath,'utf8');
 const apkLink=/<a class="primary apk-download"[^>]*>[\s\S]*?<\/a>/;
 if(!apkLink.test(html))throw Error('Preview must explicitly suppress APK download');
 html=html.replace(apkLink,'<p class="note" id="previewApkNotice">هذه معاينة للموقع فقط؛ تحميل APK يبقى من النسخة الرسمية بعد الموافقة والاختبار.</p>');
 html=html.replace('<head>','<head><meta name="robots" content="noindex,nofollow">');
 fs.writeFileSync(homePath,html);
 fs.rmSync(path.join(dist,'downloads','salati-1.0.123.apk'),{force:true});
 fs.writeFileSync(path.join(dist,'robots.txt'),'User-agent: *\nDisallow: /\n');
 const hashes=new Set();
 const digest=source=>"'sha256-"+crypto.createHash('sha256').update(source).digest('base64')+"'";
 const walk=directory=>{for(const ent of fs.readdirSync(directory,{withFileTypes:true})){const full=path.join(directory,ent.name);if(ent.isDirectory()){if(ent.name!=='downloads')walk(full);continue;}if(!ent.name.endsWith('.html'))continue;const source=fs.readFileSync(full,'utf8');for(const m of source.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)){if(/\bsrc\s*=/.test(m[1])||/application\/ld\+json/.test(m[1])||!m[2].trim())continue;hashes.add(digest(m[2]));}}};
 walk(dist);
 const policy=["default-src 'self'","base-uri 'self'","object-src 'none'","frame-ancestors 'none'","script-src 'self' "+[...hashes].join(' '),"style-src 'self' 'unsafe-inline'","img-src 'self' data: blob: https:","font-src 'self' data:","connect-src 'self' https:","media-src 'self' blob: https:","worker-src 'self' blob:","manifest-src 'self'"].join('; ');
 fs.writeFileSync(path.join(dist,'_headers'), '/*\n  Content-Security-Policy: '+policy+'\n  X-Robots-Tag: noindex, nofollow\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n\n/sw.js\n  Cache-Control: no-store\n');
 console.log('PASS: isolated Madinah Quran web-only preview; no APK, production release guard unchanged.');
 process.exit(0);
}
const signedRelease=require('./release-guard.cjs').verifiedManifest();
const releaseParts=path.join(root,'apk-release-parts','v'+signedRelease.version);
const signedPath=path.join(dist,'downloads',signedRelease.filename);
const tempPath=signedPath+'.pending';
let signedSize=0;
const releaseHash=crypto.createHash('sha256');
try{
  const fd=fs.openSync(tempPath,'w');
  try{
    for(let i=0;i<signedRelease.partCount;i++){
      const part=fs.readFileSync(path.join(releaseParts,'part'+String(i).padStart(2,'0')+'.bin'));
      fs.writeSync(fd,part);signedSize+=part.length;releaseHash.update(part);
    }
  }finally{fs.closeSync(fd);}
  if(signedSize!==signedRelease.size||releaseHash.digest('hex')!==signedRelease.sha256)
    throw Error('Signed APK checksum or size does not match immutable release manifest');
  if(signedSize>maxAssetBytes)throw Error('APK exceeds Cloudflare Pages single-asset cap');
  fs.renameSync(tempPath,signedPath);
}catch(e){fs.rmSync(tempPath,{force:true});throw e;}
console.log('Locally hosted verified signed APK:',signedRelease.filename,signedSize,'bytes');
let edits=0,files=0;const extensions=new Set(['.html','.xml','.txt','.json']);
function visit(dir){
  for(const entry of fs.readdirSync(dir,{withFileTypes:true})){
    const full=path.join(dir,entry.name);
    if(entry.isDirectory()){visit(full);continue;}
    files++;
    if(fs.statSync(full).size>maxAssetBytes)
      throw Error('Cloudflare Pages 25 MiB/file cap exceeded: '+path.relative(dist,full));
    if(!extensions.has(path.extname(entry.name).toLowerCase()))continue;
    const before=fs.readFileSync(full,'utf8'),matches=before.match(OLD);
    if(matches){edits+=matches.length;fs.writeFileSync(full,before.replace(OLD,origin),'utf8');}
  }
}
visit(dist);
if(edits<10)throw Error('Expected old production links missing; inspect SEO generation before publishing.');
const sitemap=fs.readFileSync(path.join(dist,'sitemap.xml'),'utf8');
if(!sitemap.includes('<loc>'+origin+'/</loc>')||sitemap.includes('.chatgpt.site'))
  throw Error('Generated sitemap is not bound to the new site');
const home=fs.readFileSync(path.join(dist,'index.html'),'utf8');
if(!home.includes('rel="canonical" href="'+origin+'/"'))throw Error('Homepage canonical missing');
fs.writeFileSync(path.join(dist,'robots.txt'),'User-agent: *\nAllow: /\n\nSitemap: '+origin+'/sitemap.xml\n');
// Generate CSP hashes for executable inline scripts across ALL generated pages.
// No unsafe-inline JS and no third-party script origins; styles still need
// unsafe-inline because the existing interface uses inline style attributes.
const inlineHashes=new Set();
function collectScriptHashes(dir){
 for(const item of fs.readdirSync(dir,{withFileTypes:true})){
  const full=path.join(dir,item.name);
  if(item.isDirectory()){collectScriptHashes(full);continue;}
  if(!item.name.endsWith('.html'))continue;
  const html=fs.readFileSync(full,'utf8');
  for(const match of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)){
   const attrs=match[1],content=match[2];
   if(/\bsrc\s*=/.test(attrs)||/\btype\s*=\s*["']application\/ld\+json["']/i.test(attrs)||!content.trim())continue;
   inlineHashes.add("'sha256-"+crypto.createHash('sha256').update(content).digest('base64')+"'");
  }
 }
}
collectScriptHashes(dist);
const securityPolicy=[
 "default-src 'self'",
 "base-uri 'self'",
 "object-src 'none'",
 "frame-ancestors 'none'",
 "form-action 'self'",
 "script-src 'self' "+[...inlineHashes].join(' '),
 "style-src 'self' 'unsafe-inline'",
 "font-src 'self' data:",
 "img-src 'self' data: blob: https:",
 "connect-src 'self' https:",
 "media-src 'self' blob: https:",
 "worker-src 'self' blob:",
 "manifest-src 'self'",
 "upgrade-insecure-requests"
].join('; ');
fs.writeFileSync(path.join(dist,'_headers'),[
'/*',
'  Content-Security-Policy: '+securityPolicy,
'  X-Content-Type-Options: nosniff',
'  Referrer-Policy: strict-origin-when-cross-origin',
'',
'/sw.js','  Cache-Control: no-cache, max-age=0, must-revalidate','',
'/*.html','  Cache-Control: no-cache, max-age=0, must-revalidate','',
'/sitemap.xml','  Cache-Control: no-cache, max-age=0, must-revalidate','',
'/robots.txt','  Cache-Control: no-cache, max-age=0, must-revalidate','',
'/downloads/'+signedRelease.filename,
'  Content-Type: application/vnd.android.package-archive',
'  Content-Disposition: attachment; filename="'+signedRelease.filename+'"',
'  X-Content-Type-Options: nosniff',
'  Cache-Control: public, max-age=3600',''
].join('\n'));
if(fs.statSync(path.join(dist,'index.html')).size===0)throw Error('Empty homepage');
console.log('Cloudflare Pages ready:',origin,'files:',files,'SEO URLs rewritten:',edits);
