export function fullSurahUrl(reciter,surah){return reciter.surahs.includes(Number(surah))?(reciter.surahUrls?.[surah]||reciter.server+String(surah).padStart(3,'0')+'.mp3'):null;}
