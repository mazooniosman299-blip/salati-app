/**
 * Salati: printed Madinah Mushaf (Hafs, King Fahd Complex, V4 1441H).
 * This is publisher plate artwork, NOT re-typeset Quranic text.
 *
 * Immutable 604-page version: https://cdn.quran.ws/svg/pages/v1.1.1/
 * Source: https://github.com/quran-ws/quran-svg
 * License: KFGQPC free digital use; verse polygons CC BY 4.0.
 * Keep original Salati text reader as offline/network-failure fallback.
 *
 * Never fetch `latest`, change the edition, modify diacritics, or silently
 * accept a page whose ayah set differs from our own trusted Quran JSON.
 */
export const PRINTED_MUSHAF = Object.freeze({
  edition: 'hafs-kfqc',
  version: 'v1.1.1',
  pages: 604,
  publisher: 'King Fahd Glorious Quran Printing Complex',
  base: 'https://cdn.quran.ws/svg/pages/v1.1.1/hafs-kfqc/'
});
const svgNS = 'http://www.w3.org/2000/svg';
const allowedElements = new Set(['svg','g','path','defs','clipPath','rect','circle','ellipse','line','polygon','polyline','title','desc']);
const safeNames = /^(?:xmlns(?::[\w-]+)?|version|viewBox|xml:space|transform|id|class|fill|fill-opacity|stroke|stroke-width|stroke-linecap|stroke-linejoin|stroke-dasharray|fill-rule|opacity|clip-path|ayah:x|ayah:y|d|x|y|width|height|cx|cy|r|rx|ry|x1|x2|y1|y2|points|number|surah|ayah)$/;
const pending = new WeakMap();
export const PRINTED_MUSHAF_SOURCE = 'https://github.com/quran-ws/quran-svg/tree/9fc0c87/mushafs/hafs/kfqc/svg';

function asMarkup(source, pageNumber, originalVerses) {
  if (source.length < 10000 || source.length > 2400000) throw new Error('Invalid printed Quran SVG payload size');
  const parsed = new DOMParser().parseFromString(source, 'image/svg+xml');
  if (parsed.querySelector('parsererror')) throw new Error('Invalid printed Quran SVG XML');
  const svg = parsed.documentElement;
  if (svg?.namespaceURI !== svgNS || svg.localName !== 'svg') throw new Error('Not a Quran SVG page');

  // All visible publisher artwork is kept byte-for-byte in vector geometry;
  // only untrusted markup or executable attributes are rejected.
  for (const el of [svg, ...svg.querySelectorAll('*')]) {
    if (!allowedElements.has(el.localName)) throw new Error('Unrecognised Quran SVG element');
    for (const attr of el.attributes) {
      const namespace = attr.name === 'xmlns' || attr.name === 'xmlns:ayah';
      if (!safeNames.test(attr.name) || (namespace ? !['http://www.w3.org/2000/svg','https://quranpedia.net'].includes(attr.value) : /(?:javascript:|https?:|data:|expression\s*\()/i.test(attr.value))) {
        throw new Error('Unsafe Quran SVG attribute');
      }
    }
  }
  const polygons = [...svg.querySelectorAll('path.ayahPolygon[surah][ayah]')];
  const wanted = new Set(originalVerses.map(v => v.s + ':' + v.a));
  const available = new Set(polygons.map(el => el.getAttribute('surah') + ':' + el.getAttribute('ayah')));
  if (!wanted.size || polygons.length !== wanted.size ||
      available.size !== wanted.size || [...wanted].some(ayah => !available.has(ayah))) {
    throw new Error('Publisher page verses do not match Salati Quran data');
  }
  svg.classList.add('salati-publisher-plate');
  svg.removeAttribute('width');
  svg.removeAttribute('height');
  // Group rather than role=img: nested verse buttons stay accessible.
  const arabic = document.documentElement.lang !== 'en';
  svg.setAttribute('role', 'group');
  svg.setAttribute('aria-label', arabic ? 'صفحة ' + pageNumber + ' من مصحف المدينة النبوية' : 'Madinah Mushaf, page ' + pageNumber);
  for (const el of svg.querySelectorAll('#content,#ayah_markers')) el.style.pointerEvents = 'none';
  for (const el of polygons) {
    const key = el.getAttribute('surah') + ':' + el.getAttribute('ayah');
    el.setAttribute('data-ayah', key); // Same event contract as Salati text view.
    el.setAttribute('tabindex','0');
    el.setAttribute('role','button');
    el.setAttribute('aria-label',arabic ? 'الآية ' + el.getAttribute('ayah') + '، استماع' : 'Verse ' + el.getAttribute('ayah') + ', listen');
    el.style.pointerEvents = 'all';
    el.style.cursor = 'pointer';
  }
  return document.importNode(svg, true);
}

/**
 * Replaces the layout-dependent HTML DISPLAY only; all original Quran data,
 * playback, page/surah navigation, bookmarks and reciter state remain intact.
 * On any failure, the original text page stays readable.
 */
export async function mountPrintedMushaf(pageElement, pageNumber, originalVerses) {
  if (!pageElement || pageNumber < 1 || pageNumber > PRINTED_MUSHAF.pages || !originalVerses?.length) return false;
  // Node unit-test DOMs and offline sessions use the trusted text reader;
  // do not start irrelevant network timeouts in synthetic test environments.
  if (typeof DOMParser !== 'function' || typeof document === 'undefined' || typeof document.importNode !== 'function' ||
      (typeof navigator !== 'undefined' && navigator.onLine === false)) return false;
  if (pending.has(pageElement)) return pending.get(pageElement);
  const job = (async () => {
    const controller = new AbortController();
    const cancel = setTimeout(() => controller.abort(), 12000);
    try {
      const url = PRINTED_MUSHAF.base + String(pageNumber).padStart(3,'0') + '.svg';
      const response = await fetch(url, {signal:controller.signal, mode:'cors', credentials:'omit', cache:'force-cache'});
      if (!response.ok) throw new Error('Publisher page unavailable');
      const source = await response.text();
      const svg = asMarkup(source, pageNumber, originalVerses);
      if (!pageElement.isConnected || pageElement.dataset.readingPage !== String(pageNumber)) return false;
      const footer = pageElement.querySelector('.reading-page-number');
      if (!footer) return false;
      pageElement.replaceChildren(svg,footer);
      pageElement.classList.add('salati-printed-page');
      pageElement.dataset.plateEdition = PRINTED_MUSHAF.edition;
      // Opening spread viewBoxes are NOT tight. Fit the printed ink only for
      // 1 & 2: otherwise the viewer shows a huge white/blank space.
      if (pageNumber <= 2) requestAnimationFrame(() => {
        if (!svg.isConnected) return;
        try {
          const rect = svg.getBBox();
          if (rect.width > 0 && rect.height > 0) {
            const pad = Math.max(rect.width,rect.height) * .035;
            svg.setAttribute('viewBox', [rect.x-pad,rect.y-pad,rect.width+2*pad,rect.height+2*pad].join(' '));
          }
        } catch { /* retain publisher viewBox rather than crop manually */ }
      });
      return true;
    } catch (error) {
      // No generated substitute, no empty rectangle, and no mutated ayat.
      pageElement.dataset.plateUnavailable = 'true';
      console.warn('Salati: authentic Mushaf plate unavailable; retaining verified text page.', pageNumber, error?.message);
      return false;
    } finally { clearTimeout(cancel); }
  })();
  pending.set(pageElement,job);
  return job;
}
