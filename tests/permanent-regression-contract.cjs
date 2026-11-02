#!/usr/bin/env node
'use strict';

/**
 * Blocking release contract for Salati. Intentionally fast and dependency-free:
 * this executes inside Cloudflare Pages builds as well as GitHub Actions.
 * Real-browser and native-device tests run in the companion CI workflow.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const read = p => fs.readFileSync(path.join(root, p), 'utf8');
const release = JSON.parse(read('apk-release-parts/current.json'));
assert.match(release.version, /^1\.0\.\d+$/, 'Unrecognised current APK version');
const manifest = JSON.parse(read('apk-release-parts/v' + release.version + '/manifest.json'));

function validate(html, css, worker, current, signed) {
  const cssLinks = [...html.matchAll(/<link\b[^>]*\brel=["']stylesheet["'][^>]*>/gi)]
    .map(m => m[0].match(/\bhref=["']([^"']+)["']/i)?.[1]);
  assert.deepEqual(cssLinks, ['salati-ui.css'], 'Multiple/stale app CSS layers returned');
  assert(!/!\s*important\b/i.test(css), 'Force-priority CSS was reintroduced');
  assert(!/preview-sample-location|light-theme-v|active-reference-nav-20261101\.css/i.test(html),
    'Retired preview/light-theme code returned');
  for (const marker of ['nav-icon-button.active', '#prayers', '#mushafPlayerSlot']) {
    assert(css.includes(marker), 'Approved dark UI component missing: ' + marker);
  }
  for (const id of ['qVerses', 'mushafPlayerSlot']) {
    assert(html.includes('id="' + id + '"'), 'Quran reader component missing: ' + id);
  }
  assert(worker.includes("'./salati-ui.css'"), 'Offline cache excludes the canonical stylesheet');
  assert.equal(signed.version, current.version, 'Website and APK release versions differ');
  assert.equal(signed.filename, 'salati-' + current.version + '.apk', 'Wrong signed APK filename');
  assert.equal(signed.applicationId, 'com.salati.prayer', 'Unexpected Android package');
  assert.equal(signed.certificateSha256,
    '559dec66ab13e86be17c661732f1d2b1751a63261ed7d7d353b857f693cf056e',
    'Original Android signing certificate changed');
  assert(html.includes('href="/downloads/' + signed.filename + '"'),
    'Website download link does not reference the verified signed APK');
  assert(html.includes('class="app-version">v' + current.version + '</small>'),
    'Displayed website version is stale');
}
const html = read('dist/index.html');
const css = read('dist/salati-ui.css');
const worker = read('dist/sw.js');
validate(html, css, worker, release, manifest);

// Negative/mutation smoke tests: the gate itself must demonstrate that it
// actually REJECTS earlier Salati regressions instead of always printing PASS.
const mustReject = (label, mutate) => {
  const v = [html, css, worker, release, manifest];
  const broken = mutate(v);
  assert.throws(() => validate(...broken), undefined, 'Gate missed mutation: ' + label);
};
mustReject('CSS priority', v => { v[1] += '\n.x{color:red!important}'; return v; });
mustReject('second CSS layer', v => { v[0] = v[0].replace('href="salati-ui.css"', 'href="salati-ui.css"><link rel="stylesheet" href="legacy.css"'); return v; });
mustReject('old APK version link', v => { v[0] = v[0].replace('href="/downloads/' + manifest.filename + '"', 'href="/downloads/salati-1.0.0.apk"'); return v; });
mustReject('wrong certificate', v => { v[4] = {...manifest, certificateSha256: '0'.repeat(64)}; return v; });
mustReject('no Quran section', v => { v[0] = v[0].replace('id="qVerses"', 'id="missingReader"'); return v; });
console.log('PASS permanent Salati contract: dark CSS, Quran, offline cache, signed APK/version, and 5 tested failure injections');
