// Protect the two user-approved recorded excerpts against accidental synthetic substitution.
// These hashes identify reviewed source bytes; this is not an automatic human-voice detector.
const fs=require('node:fs'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const approved={
 'approach-hayya-human-v1.mp3':'9a1bf07368cab2926ce4328bbfb662efdb52c4543152338d3b5edd3bcb40ff26',
 'fajr-phrase-human-v1.mp3':'adabd1e6d8435dea1c5081040e6af2a56f0173c1a4106a101144aeaee6e2c6a4'
};
const directory='dist/audio/reminders/';
assert.deepEqual(fs.readdirSync(directory).filter(name=>name.endsWith('.mp3')).sort(),Object.keys(approved).sort());
for(const [file,sha] of Object.entries(approved))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(directory+file)).digest('hex'),sha,file+' must be the reviewed recorded excerpt');
for(const file of ['generate_sources.py','prepare_audio.py'])assert(!fs.existsSync(directory+file),'rejected synthesis tooling must not ship');
const manifest=JSON.parse(fs.readFileSync(directory+'verification.json','utf8'));
assert.equal(manifest.recordings.length,2);for(const row of manifest.recordings){assert.equal(row.sha256,approved[row.file]);assert.equal(row.synthetic,false);assert(row.duration_seconds<25,'recordings fit inside the bounded30second controller window');}
const sources=fs.readFileSync(directory+'SOURCES.md','utf8');assert(sources.includes('https://soundcloud.com/r-da-wakrim/2014-1'));assert(sources.includes('63.5–74.3'));
console.log('PASS: only the two reviewed real-recording excerpts ship; original hashes, complete-phrase durations and source provenance retained.');
