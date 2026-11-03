#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const manifest=JSON.parse(read('docs/requests/ACTIVE_CHANGE.json'));
const current=JSON.parse(read('apk-release-parts/current.json'));
const release=JSON.parse(read('apk-release-parts/v'+current.version+'/manifest.json'));
const html=read('dist/index.html');
const agent=read('AGENTS.md');
const design=read('docs/CURRENT_APPROVED_DESIGN.md');
const map=read('docs/ACTUAL_SOURCE_MAP.md');
const conflicts=read('docs/INSTRUCTION_CONFLICTS.md');
const report=read('docs/ROOT_CAUSE_AUDIT_20261103.md');
assert.equal(current.version,release.version,'release manifest version mismatch');
assert.equal(release.applicationId,'com.salati.prayer');
assert.equal(release.certificateSha256,'559dec66ab13e86be17c661732f1d2b1751a63261ed7d7d353b857f693cf056e');
assert(read('README.md').slice(0,450).includes(current.version),'README banner stale versus release manifest');
for(const doc of ['CURRENT_APPROVED_DESIGN.md','ACTUAL_SOURCE_MAP.md','INSTRUCTION_CONFLICTS.md']) {
  assert(agent.includes(doc),'AGENTS missing direct source-of-truth guide: '+doc);
}
assert(agent.includes('production')&&agent.includes('git diff')&&agent.includes('original'),'Missing core implementation guardrails');
assert(design.includes('Unresolved')&&design.includes('PR #35')&&design.includes('PR #36'),'Current design hides outstanding conflicts');
assert(conflicts.includes('preview-four-ui-changes-browser.py'),'Preview/production collision not documented');
assert(map.includes('app-source.js')&&map.includes('quran-controller.js')&&map.includes('PrayerWidget.java'),'Active source ownership missing');
assert(map.includes('salati-ui.css')&&html.includes('href="salati-ui.css"'),'Canonical CSS source mismatch');
for(const id of ['times','mushaf','qibla','dhikr','tasbih','settings','qTransport','qSeek','mushafPlayerSlot']) {
 assert(html.includes('id="'+id+'"'),'Missing live component id '+id);
}
const rows=report.split('\n').filter(line=>/^\|\s*(?:[1-9]|1\d|20)\s*\|/.test(line));
assert.equal(rows.length,20,'20-risk audit missing row(s)');
assert(read('docs/requests/SALATI-20261103-ROOT-CONTROL.md').includes(manifest.original_verbatim_excerpt),'Original user wording must be copied verbatim into acceptance record');
assert(['governance','infrastructure'].includes(manifest.release_mode),'This no-UI-change PR must declare governance/infrastructure mode');
assert.equal(manifest.visual_change,false,'Governance PR must not claim UI change');
assert.equal(manifest.android_release,false,'Governance PR must not claim Android release');
const {validateScope,requiresWebVisualDiff}=require('../scripts/verify-change-scope.cjs');
assert(requiresWebVisualDiff(['glass-navigation.js','choice-picker.js','dist/salati-ui.css']),'Imported UI modules must not bypass runtime visual comparison');
assert(!requiresWebVisualDiff(['AGENTS.md','docs/ACTUAL_SOURCE_MAP.md']),'Governance-only documentation should not trigger UI diff');
assert(requiresWebVisualDiff(['dist/images/new-reference.jpeg','dist/fonts/reader.woff2','dist/reader.html','dist/quran/page.avif']),'Images, web fonts and HTML under dist must trigger a real visual diff');
const permitted=['AGENTS.md','README.md','docs/requests/ACTIVE_CHANGE.json','docs/ROOT_CAUSE_AUDIT_20261103.md','scripts/verify-change-scope.cjs','tests/agent-governance-contract.cjs','.github/workflows/salati-agent-governance.yml'];
const fixture={...manifest,release_mode:'governance',allowed_paths:[...new Set([...manifest.allowed_paths,...permitted])]};
assert.equal(validateScope(permitted,fixture),permitted.length);
for(const forbidden of ['dist/index.html','dist/salati-ui.css','android/app/src/main/java/com/salati/prayer/MainActivity.java','quran-controller.js','other-file.txt']){
 assert.throws(()=>validateScope([...permitted,forbidden],fixture),/OUT-OF-SCOPE/,'Unexpected change slipped through: '+forbidden);
}
assert.throws(()=>validateScope(permitted,{...manifest,base_branch:'main'}),/production/);
assert.throws(()=>validateScope(permitted,{...manifest,allowed_paths:[]}),/Empty/);
const more={...fixture,allowed_paths:[...fixture.allowed_paths,'dist/index.html']};
assert.throws(()=>validateScope([...permitted,'dist/index.html'],more),/Governance changes|Infrastructure request/);
const preview={...more,release_mode:'preview'};
assert.equal(validateScope([...permitted,'dist/index.html'],preview),permitted.length+1);
const prod={...more,release_mode:'production'};
assert.throws(()=>validateScope([...permitted,'dist/index.html'],prod,{releaseVerifier:()=>{throw new Error('independent signed proof unavailable')}}),/independent signed proof unavailable/,'Production runtime modification must not pass without independent original-key verification');
let proofCalled=false;
assert.throws(()=>validateScope([...permitted,'dist/index.html'],{...prod,original_key_signing_verified:true,website_apk_fingerprint_verified:true},{releaseVerifier:()=>{proofCalled=true;throw new Error('independent original-key proof unavailable')}}),/independent original-key proof unavailable/,'Editable JSON booleans cannot bypass independent signer inspection');
assert(proofCalled,'Signer proof verifier was bypassed');
assert.equal(validateScope([...permitted,'dist/index.html'],prod,{releaseVerifier:()=>{}}),permitted.length+1,'Only externally verified callback can certify release');
const build={...fixture,allowed_paths:[...fixture.allowed_paths,'scripts/release-guard.cjs']};
assert.throws(()=>validateScope([...permitted,'scripts/release-guard.cjs'],build),/Governance changes cannot mutate/,'Build/sign guard is runtime critical');
const uiAllowed={...fixture,allowed_paths:[...fixture.allowed_paths,'glass-navigation.js']};
assert.throws(()=>validateScope([...permitted,'glass-navigation.js'],uiAllowed),/Governance changes cannot mutate/,'Additional imported UI sources must not be allowed by governance mode');
const missingTarget={...fixture,visual_change:true,allowed_paths:[...fixture.allowed_paths,'dist/salati-ui.css'],visual_allowed_regions:[{selector:'#qTransport',tab:'mushaf',language:'both'}],release_mode:'preview'};
assert.throws(()=>validateScope([...permitted,'dist/salati-ui.css'],missingTarget),/before\/after\/preserve/,'Vague visual selector must be rejected');
const specificTarget={...missingTarget,visual_allowed_regions:[{selector:'#qTransport',tab:'mushaf',language:'both',before:'charcoal button',after:'blue button',preserve:['size','position','Quran text','navigation']}]};
assert.equal(validateScope([...permitted,'dist/salati-ui.css'],specificTarget),permitted.length+1,'Fully specified preview request should be permitted, but never published');
assert.throws(()=>validateScope(permitted,{...specificTarget,allowed_paths:fixture.allowed_paths}),/no visual-capable/, 'Visual completion cannot be claimed from documentation-only modifications');
const infraSmoke={...manifest,release_mode:'infrastructure',visual_change:false,android_release:false,allowed_paths:[...new Set([...manifest.allowed_paths,'scripts/verify-publish-ci.cjs','package.json','tests/publish-ci-wait.cjs'])]};
const infraFiles=['scripts/verify-publish-ci.cjs','package.json','tests/publish-ci-wait.cjs','docs/requests/ACTIVE_CHANGE.json'];
assert.equal(validateScope(infraFiles,infraSmoke),infraFiles.length,'CI scheduling can be repaired without modifying signed app');
assert.throws(()=>validateScope([...infraFiles,'dist/index.html'],{...infraSmoke,allowed_paths:[...infraSmoke.allowed_paths,'dist/index.html']}),/Infrastructure request cannot edit app/);
const manifestReference=JSON.parse(read('design-references/APPROVED_REFERENCE_REGISTRY.json'));
assert(manifestReference.references.some(x=>x.id==='mosque-original'&&x.status==='verified-user-asset'));
assert(manifestReference.references.some(x=>x.id==='printed-mushaf-final'&&x.status==='unresolved'));

const verbatim=read('docs/requests/ORIGINAL_FULL_PROMPT_20261103.md');
assert(verbatim.includes('## المشكلة 1: غياب تعليمات موحدة لـChatGPT')&&verbatim.includes('## المشكلة 20: غياب سجل نهائي لتنفيذ الطلبات وقبولها'),'Original 20-point user request is incomplete');
assert(agent.includes('ORIGINAL_FULL_PROMPT_20261103.md'),'AGENTS no longer requires whole original user mandate');
require('../scripts/verify-request-status.cjs');
console.log('PASS agent governance: 20 risks, source ownership, conflicting PRs, original release identity, additional negative cases; no visual match asserted');
