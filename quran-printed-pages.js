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

/**
 * Reader engine lifecycle, deliberately independent of the visual theme.
 * Mount only leaves near the scrolling viewport, and release SVG path trees
 * after they leave it. Restore ORIGINAL trusted Quran text when released.
 * All page geometry is derived from the actual publisher artwork.
 */
const leaves = new WeakMap();

function originalInkFit(svg, pageNumber) {
  if (!svg.isConnected) return false;
  try {
    const b = svg.getBBox();
    const v = svg.viewBox.baseVal;
    if (![b.x,b.y,b.width,b.height].every(Number.isFinite) ||
        b.width < 40 || b.height < 60 || !v.width || !v.height) return false;
    // Do not stretch/clip glyphs. The external viewBox may contain unused area.
    const margin = Math.max(b.width,b.height) * (pageNumber <= 2 ? .035 : .015);
    const rect = [b.x-margin,b.y-margin,b.width+2*margin,b.height+2*margin];
    if (rect[2] <= 0 || rect[3] <= 0 || rect[2] > 700 || rect[3] > 1000) return false;
    svg.setAttribute('viewBox',rect.join(' '));
    svg.setAttribute('preserveAspectRatio','xMidYMin meet');
    return true;
  } catch {
    return false; // Android SVG implementations may lack getBBox.
  }
}

function releasePlate(state) {
  if (!state.plate || !state.page.isConnected) return;
  const box = state.page.getBoundingClientRect();
  // Preserve scroll height while this page is outside the reader viewport.
  if (box.height > 100 && box.height < 2200)
    state.page.style.minHeight = Math.ceil(box.height) + 'px';
  state.inkObserver?.disconnect();
  state.inkObserver = null;
  state.page.replaceChildren(...state.fallback.childNodes,state.footer);
  state.fallback = null;
  state.plate = null;
  state.page.classList.remove('salati-printed-page');
  delete state.page.dataset.plateEdition;
}

async function loadPlate(state) {
  if (state.busy || state.plate || !state.near || state.disposed) return false;
  const page = state.page;
  const token = ++state.generation;
  const controller = new AbortController();
  state.abort = controller;
  state.busy = true;
  const limit = setTimeout(() => controller.abort(), 12000);
  try {
    const url = PRINTED_MUSHAF.base + String(state.pageNumber).padStart(3,'0') + '.svg';
    const response = await fetch(url,{signal:controller.signal,mode:'cors',credentials:'omit',cache:'force-cache'});
    if (!response.ok) throw new Error('Publisher page unavailable');
    const source = await response.text();
    const svg = asMarkup(source,state.pageNumber,state.verses);
    if (state.disposed || !state.near || state.generation !== token ||
        !page.isConnected || page.dataset.readingPage !== String(state.pageNumber)) return false;
    // Save all authored fallback nodes (and the original verse click targets).
    const fallback = document.createDocumentFragment();
    for (const node of Array.from(page.childNodes)) if (node !== state.footer) fallback.appendChild(node);
    page.replaceChildren(svg,state.footer);
    state.fallback = fallback;
    state.plate = svg;
    state.page.style.minHeight = '';
    page.classList.add('salati-printed-page');
    page.dataset.plateEdition = PRINTED_MUSHAF.edition;
    delete page.dataset.plateUnavailable;
    // getBBox() is only dependable when this leaf becomes visible.
    if (typeof IntersectionObserver === 'function') {
      state.inkObserver = new IntersectionObserver(entries => {
        if (entries.some(e => e.isIntersecting)) {
          if (originalInkFit(svg,state.pageNumber)) state.inkObserver?.disconnect();
        }
      },{root:document.getElementById('qVerses'),rootMargin:'0px'});
      state.inkObserver.observe(svg);
    }
    requestAnimationFrame(() => {
      if (svg.isConnected && svg.getBoundingClientRect().height > 1)
        originalInkFit(svg,state.pageNumber);
    });
    return true;
  } catch (error) {
    if (!state.disposed && state.near) {
      state.page.dataset.plateUnavailable = 'true';
      console.warn('Salati: authentic Mushaf plate unavailable; retaining verified text page.',state.pageNumber,error?.message);
    }
    return false;
  } finally {
    clearTimeout(limit);
    state.busy = false;
    state.abort = null;
    // Rapid scrolling can abort a prefetch and re-enter before its promise
    // settles. Retry the CURRENT viewport generation, never a stale page.
    if (state.near && !state.plate && !state.disposed && state.generation !== token)
      queueMicrotask(() => { if (state.near && !state.busy) void loadPlate(state); });
  }
}

export function disposePrintedMushaf(pageElement) {
  const state = leaves.get(pageElement);
  if (!state) return;
  state.disposed = true;
  ++state.generation;
  state.abort?.abort();
  state.nearObserver?.disconnect();
  state.inkObserver?.disconnect();
  // Container is about to be cleared, so releasing the SVG is not needed.
  state.fallback = null;
  leaves.delete(pageElement);
}

export function mountPrintedMushaf(pageElement,pageNumber,originalVerses) {
  if (!pageElement || pageNumber < 1 || pageNumber > PRINTED_MUSHAF.pages || !originalVerses?.length) return false;
  // Never start network fetches in minimal test DOMs or offline sessions.
  if (typeof DOMParser !== 'function' || typeof document === 'undefined' ||
      typeof document.importNode !== 'function' ||
      (typeof navigator !== 'undefined' && navigator.onLine === false)) return false;
  if (leaves.has(pageElement)) return true;
  const state = {
    page:pageElement,pageNumber,verses:originalVerses,
    footer:pageElement.querySelector('.reading-page-number'),
    fallback:null,plate:null,busy:false,abort:null,near:false,
    nearObserver:null,inkObserver:null,generation:0,disposed:false
  };
  if (!state.footer) return false;
  leaves.set(pageElement,state);
  if (typeof IntersectionObserver !== 'function') {
    state.near = true;
    void loadPlate(state);
    return true;
  }
  // Near viewport = network/mount; away = restore text and discard heavy paths.
  // This prevents hundreds of 200-600KB SVG DOM trees building up on phones.
  state.nearObserver = new IntersectionObserver(entries => {
    if (state.disposed || !pageElement.isConnected) {
      disposePrintedMushaf(pageElement);
      return;
    }
    if (entries.some(e=>e.isIntersecting)) {
      state.near=true;
      void loadPlate(state);
    } else {
      state.near=false;
      ++state.generation;
      state.abort?.abort();
      releasePlate(state);
    }
  },{root:document.getElementById('qVerses'),rootMargin:'900px 0px'});
  state.nearObserver.observe(pageElement);
  return true;
}
