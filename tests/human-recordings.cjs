const fs=require('node:fs'),assert=require('node:assert/strict');
const folder='dist/audio/reminders/';
const source=fs.readFileSync('prayer-announcements.js','utf8');
const manifest=JSON.parse(fs.readFileSync(folder+'verification.json','utf8'));
assert.deepEqual(fs.readdirSync(folder).filter(n=>n.endsWith('.mp3')),[],
 'No Fajr recording with unverified redistribution rights may ship');
assert(!source.includes('fajr-user-approved-1.0.103.mp3'));
assert(source.includes('speechSynthesis')&&source.includes('الصلاة خير من النوم'));
assert.equal(manifest.redistribution_license_verified,false);
assert.equal(manifest.distributed_recordings,0);
console.log('PASS: Fajr speech uses device TTS, unlicensed file not distributed.');
