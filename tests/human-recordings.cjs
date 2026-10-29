// The release must use only the exact MP3 supplied/approved by the user.
const fs=require('node:fs'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const directory='dist/audio/reminders/',file='fajr-user-approved-1.0.103.mp3';
const manifest=JSON.parse(fs.readFileSync(directory+'verification.json','utf8'));
assert.deepEqual(fs.readdirSync(directory).filter(n=>n.endsWith('.mp3')),[file]);assert.equal(manifest.recordings.length,1);
const row=manifest.recordings[0];assert.equal(row.file,file);assert.equal(crypto.createHash('sha256').update(fs.readFileSync(directory+file)).digest('hex'),row.sha256);assert.equal(row.synthetic,false);assert(row.duration>19&&row.duration<20);assert(manifest.user_authorized_use_after_rights_disclosure);
assert.equal(row.redistribution_license_verified,false,'Do not invent a license for the user-provided recording');
assert(fs.readFileSync(directory+'SOURCES.md','utf8').includes('No documented redistribution permission'));
console.log('PASS: only the exact approved upload ships as a Fajr announcement; no approach clips, synthesis or invented redistribution license.');
