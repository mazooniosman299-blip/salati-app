// Protect the six user-approved recorded excerpts against accidental synthetic substitution.
// These hashes identify reviewed source bytes; this is not an automatic human-voice detector.
const fs=require('node:fs'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const approved={
 "approach-fajr-human-v2.mp3": "79fbe09f8bb15d23338ddf4c0456e9ea856bdd33cf40405350d5379b4fb79c2b",
 "approach-dhuhr-human-v2.mp3": "63a73813e8a46d6d7b3b161b16c5bb96272c0f40387d56a215cc277d7aa8a1e6",
 "approach-asr-human-v2.mp3": "32ebf2d3ea63e26a3ce2d1a910c80685dd90e88f025140b608432ef26705b860",
 "approach-maghrib-human-v2.mp3": "8b8b175c8e2cd4857a71943fa0c52bc4892d42d4aa3e16cce0b58222425cb183",
 "approach-isha-human-v2.mp3": "6d7d02e101d40422bbb72a78d2deeeb5c1ea4ff8a76ad77708c12d3bfbf41746",
 "fajr-phrase-single-human-v2.mp3": "c6e8d705ccef1add81cd667e8fa15f5bfecf4eadc41d675471395e9f2f43b93a"
};
const directory='dist/audio/reminders/';
assert.deepEqual(fs.readdirSync(directory).filter(name=>name.endsWith('.mp3')).sort(),Object.keys(approved).sort());
for(const [file,sha] of Object.entries(approved))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(directory+file)).digest('hex'),sha,file+' must be the reviewed recorded excerpt');
for(const file of ['generate_sources.py','prepare_audio.py'])assert(!fs.existsSync(directory+file),'rejected synthesis tooling must not ship');
const manifest=JSON.parse(fs.readFileSync(directory+'verification.json','utf8'));
assert.equal(manifest.recordings.length,6);for(const row of manifest.recordings){assert.equal(row.sha256,approved[row.file]);assert.equal(row.synthetic,false);assert(row.duration<25,'recordings fit inside the bounded30second controller window');}
const sources=fs.readFileSync(directory+'SOURCES.md','utf8');assert(sources.includes('https://soundcloud.com/ramy-elshiekh-228503388/2dof6bkyfcuy'));assert(sources.includes('214.2–228.2'));
console.log('PASS: only the six reviewed real-recording excerpts ship; original hashes, complete-phrase durations and source provenance retained.');
