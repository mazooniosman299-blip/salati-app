import {matchesCitySearch} from './directory-search.js';
const input=document.getElementById('city-search'),cards=[...document.querySelectorAll('[data-city-search]')];
input.addEventListener('input',()=>{
 let count=0;for(const card of cards){card.hidden=!matchesCitySearch(input.value,card.dataset.citySearch);if(!card.hidden)count++;}
 for(const group of document.querySelectorAll('[data-country-group]'))group.hidden=![...group.querySelectorAll('[data-city-search]')].some(card=>!card.hidden);
 document.getElementById('city-search-status').textContent=document.documentElement.lang==='ar'?'المدن المعروضة: '+new Intl.NumberFormat('ar').format(count):'Cities shown: '+count;
});
