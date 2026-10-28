const assert = require('node:assert/strict');
const Module = require('node:module');
const { buildSync } = require('esbuild');

const compiled = new Module(__filename, module);
compiled._compile(buildSync({
  entryPoints: ['audio-controller.js'], bundle: true, platform: 'node',
  format: 'cjs', write: false
}).outputFiles[0].text, __filename);
const { PrayerAudio, AUDIO_DEFAULTS, RECORDINGS } = compiled.exports;

class AudioContext {
  constructor() { this.state = 'running'; this.currentTime = 0; this.started = []; }
  resume() { return Promise.resolve(); }
  addEventListener() {}
  createGain() {
    return { connect() {}, gain: {
      value: 1, cancelScheduledValues() {}, setValueAtTime() {}, linearRampToValueAtTime() {}
    } };
  }
  createBufferSource() {
    const context = this;
    return { connect() {}, disconnect() {}, stop() {},
      start() { context.started.push(this.buffer.url); }
    };
  }
}

(async () => {
  const settings = { ...AUDIO_DEFAULTS, enabled: true, prayers: { ...AUDIO_DEFAULTS.prayers } };
  const storage = new Map();
  const audio = new PrayerAudio({
    getSettings: () => settings, onState() {}, Context: AudioContext,
    storage: { getItem: key => storage.get(key), setItem: (key, value) => storage.set(key, value) }
  });
  const loaded = [];
  audio.load = async url => { loaded.push(url); return { url }; };
  let time = Date.now();
  for (const voice of Object.keys(RECORDINGS)) {
    settings.voice = voice;
    loaded.length = 0;
    assert(await audio.arm());
    assert.deepEqual(loaded, [RECORDINGS[voice].url, 'audio/wasilah.mp3'],
      'Arming must cache the selected voice and dua without an unrelated Fajr recording');
    for (const prayer of ['fajr', 'dhuhr', 'asr', 'maghrib', 'isha']) {
      audio.stop(false);
      audio.ctx.started.length = 0;
      time += 60000;
      audio.previous = time - 1000;
      const schedule = [{ key: prayer, time: new Date(time) }];
      audio.tick(schedule, time, true);
      await Promise.resolve();
      await Promise.resolve();
      assert.deepEqual(audio.ctx.started, [RECORDINGS[voice].url], `${prayer} must honor ${voice}`);
      audio.source.onended();
      assert.deepEqual(audio.ctx.started, [RECORDINGS[voice].url, 'audio/wasilah.mp3']);
      audio.source.onended();
      assert.equal(audio.code, 'finished');
      audio.previous = time - 1000;
      audio.tick(schedule, time, true);
      await Promise.resolve();
      assert.equal(audio.ctx.started.length, 2, 'The same scheduled prayer must not replay');
    }
    audio.ctx.started.length = 0;
    assert(await audio.play('adhan', 'fajr', { followDua: false }));
    audio.source.onended();
    assert.deepEqual(audio.ctx.started, [RECORDINGS[voice].url], 'A preview must use the same recording');
  }
  audio.ctx.started.length = 0;
  assert(await audio.play('dua'));
  assert.deepEqual(audio.ctx.started, ['audio/wasilah.mp3']);
  audio.disable();
  console.log('Scheduled audio: all five prayers honor every selected voice, with matching previews, optional dua, caching and duplicate prevention.');
})().catch(error => { console.error(error); process.exitCode = 1; });
