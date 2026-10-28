import manifest from './world-data/countries.json';
export const WORLD_COUNTRIES=manifest.countries;
export const WORLD_CITY_COUNT=manifest.cities;
export function countryOption(country,lang){const option=new Option(country[lang],country.code);option.dataset.search=country.search||[country.code,country.ar,country.en].join(' ');option.dataset.subtitle=country[lang==='ar'?'en':'ar'];return option;}
const validCode=code=>WORLD_COUNTRIES.some(c=>c.code===code);
export class WorldDirectory{
 constructor(fetcher=(...args)=>fetch(...args)){this.fetcher=fetcher;this.cache=new Map();this.pending=new Map();}
 async load(code){if(!validCode(code))throw Error('country');if(this.cache.has(code))return this.cache.get(code);if(this.pending.has(code))return this.pending.get(code);const request=this.fetcher('world-cities/'+code+'.json').then(r=>{if(!r.ok)throw Error('cities');return r.json();}).then(rows=>{if(!Array.isArray(rows)||rows.some(r=>!Array.isArray(r)||typeof r[0]!=='string'||!Number.isFinite(r[1])||!Number.isFinite(r[2])||Math.abs(r[1])>90||Math.abs(r[2])>180))throw Error('cities');this.cache.set(code,rows);return rows;}).finally(()=>this.pending.delete(code));this.pending.set(code,request);return request;}
}
export const cityLabel=row=>row[0]+(row[3]?' · '+row[3]:'');
