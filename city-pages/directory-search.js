export function normalizeCitySearch(value){return value.normalize('NFKD').replace(/[\u064b-\u065f\u0670\u0640]/g,'').replace(/[أإآٱ]/g,'ا').toLocaleLowerCase().trim();}
export function matchesCitySearch(search,text){return normalizeCitySearch(text).includes(normalizeCitySearch(search));}
