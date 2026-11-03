#!/usr/bin/env node
'use strict';
/** Immutable reviewed Hafs Quran source contract: no rewriting scripture to satisfy UI. */
const assert=require('node:assert/strict'),crypto=require('node:crypto'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const file=path.join(root,'dist/quran/data.json');
const bytes=fs.readFileSync(file);
const sha=crypto.createHash('sha256').update(bytes).digest('hex');
const approved='cb2be527751f8671b89595a0d81cc059c3db894c213772200bcf9a01dc5096e5';
assert.equal(sha,approved,'Quran source bytes changed: require verified publisher source, owner review, and a new provenance record before editing any ayah');
const q=JSON.parse(bytes.toString('utf8'));
assert.equal(q.surahs.length,114,'114 surahs required');
assert.equal(q.pages.length,604,'604 Hafs source pages required');
const verses=q.pages.flat(),seen=new Set(),count=new Map();
assert.equal(verses.length,6236,'6236 unique Quran verses required');
for(const verse of verses){
 assert(Number.isInteger(verse.s)&&verse.s>=1&&verse.s<=114,'Wrong surah ID');
 assert(Number.isInteger(verse.a)&&verse.a>=1,'Wrong ayah number');
 assert(typeof verse.t==='string'&&verse.t.trim().length>0,'Empty Quran verse');
 const key=verse.s+':'+verse.a;
 assert(!seen.has(key),'Duplicate verse '+key);
 seen.add(key);count.set(verse.s,(count.get(verse.s)||0)+1);
}
for(const s of q.surahs)assert.equal(count.get(s.id),s.total_verses,'Surah ayah count changed: '+s.id);
console.log('PASS immutable Quran text SHA-256',sha,'surahs=114, pages=604, ayahs=6236, no duplicate/missing verse, source text unaltered');
