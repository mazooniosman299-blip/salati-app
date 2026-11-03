#!/usr/bin/env node
'use strict';
/** Counter-regression: parent Cloudflare build must not interrupt child CI gate. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const guard=require('../scripts/verify-publish-ci.cjs');
const build=fs.readFileSync(path.join(root,'scripts/build-cloudflare-pages.cjs'),'utf8');
const match=build.match(/\[path\.join\(root,'scripts\/verify-publish-ci\.cjs'\),sha\],\{([\s\S]*?)\}\);/);
assert(match,'Missing fail-closed exact-SHA publish guard process');
const attrs=match[1];
assert(/stdio\s*:\s*'inherit'/.test(attrs),'Deployment must expose child guard failure logs');
assert(/timeout\s*:\s*require\('\.\/verify-publish-ci\.cjs'\)\.MAX_WAIT_MS\s*\+\s*60\s*\*\s*1000/.test(attrs),
 'Cloudflare parent must wait longer than bounded mandatory CI attestation child');
assert.equal(guard.MAX_WAIT_MS,13*60*1000,'Review child max wait before changing deployment timeout');
assert(guard.MAX_WAIT_MS+60000>guard.MAX_WAIT_MS,'Parent expired before required CI proof could complete');
assert(/process\.env\.CF_PAGES_BRANCH==='production'/.test(build),'Nonproduction branch protection changed');
assert(/CF_PAGES_COMMIT_SHA/.test(build),'Exact Cloudflare commit identity removed');
assert(/require\('\.\/release-guard\.cjs'\)\.verifiedManifest\(\)/.test(build),'Original-key APK/website fingerprint contract removed');
assert(/scripts\/verify-publish-ci\.cjs/.test(build),'CI auth gate removed');
console.log('PASS Cloudflare build timeout > independent 13min exact-SHA CI wait; original-key/fingerprint checks remain mandatory');
