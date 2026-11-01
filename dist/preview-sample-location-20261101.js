/* PREVIEW APP ONLY. Real city-center demonstration data for the separate,
 * debug-signed app. Never infer the user's precise address or silently turn
 * on the background adhan. Change city in Settings for actual prayer times. */
(() => {
  if (!window.SalatiNative) return; // Do not alter public website or browser.
  try {
    const raw=localStorage.getItem('salati');
    const saved=raw?JSON.parse(raw):{};
    if (saved && saved.locationSet===true && Number.isFinite(saved.lat) && Number.isFinite(saved.lon)) return;
    if (saved && saved.salatiPreviewSampleAcknowledged === true) return;
    localStorage.setItem('salati',JSON.stringify({
      ...saved,
      lang:saved.lang==='en'?'en':'ar',
      lat:23.588,lon:58.3829,
      name:'مسقط (معاينة)',
      zone:'Asia/Muscat',
      zoneMode:'manual',
      locationSet:true,
      locationMode:'manual',
      method:'Oman',
      methodPreferenceVersion:1,
      audio:{...saved.audio,enabled:false},
      salatiPreviewSampleAcknowledged:true
    }));
  } catch (_) { /* Never block the original app if storage is restricted. */ }
})();
