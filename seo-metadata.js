// A language switch does not create a separate indexable URL or hreflang target.
export const SEO_COPY = {
  ar: {
    title: 'صلاتي | مواقيت الصلاة والقرآن واتجاه القبلة',
    description: 'مواقيت الصلاة حسب موقعك ومدينتك حول العالم، مع القرآن الكريم والتلاوات واتجاه القبلة والأذكار. اختر طريقة الحساب المناسبة لبلدك مع صلاتي.'
  },
  en: {
    title: 'Salati | Worldwide Prayer Times, Quran & Qibla',
    description: 'Find prayer times for your location and city worldwide. Read the Quran, listen to recitations, find the Qibla and explore daily dhikr with Salati.'
  }
};
export function updateSeoMetadata(language, doc = document) {
  const copy = SEO_COPY[language] || SEO_COPY.ar;
  doc.title = copy.title;
  for (const [selector, value] of [
    ['meta[name="description"]', copy.description],
    ['meta[property="og:title"]', copy.title],
    ['meta[property="og:description"]', copy.description]
  ]) {
    const node = doc.querySelector(selector);
    if (node) node.content = value;
  }
}
