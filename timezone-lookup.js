import approximateLookup from 'tz-lookup';
import preciseRegions from './world-data/exact-timezone-regions.json';

// Exact, licensed source polygons for a reproduced24h island-zone error.
// Ordinary locations retain the existing lookup and its offline behavior.
function ringContains(ring,x,y){
 let inside=false;
 for(let i=0,j=ring.length-1;i<ring.length;j=i++){
  const [xi,yi]=ring[i],[xj,yj]=ring[j];
  const cross=(x-xi)*(yj-yi)-(y-yi)*(xj-xi);
  if(Math.abs(cross)<1e-12&&x>=Math.min(xi,xj)&&x<=Math.max(xi,xj)&&y>=Math.min(yi,yj)&&y<=Math.max(yi,yj))return true;
  if((yi>y)!==(yj>y)&&x<(xj-xi)*(y-yi)/(yj-yi)+xi)inside=!inside;
 }
 return inside;
}
function polygonContains(rings,x,y){return ringContains(rings[0],x,y)&&!rings.slice(1).some(r=>ringContains(r,x,y));}
const shapes=preciseRegions.features.map(f=>{
 const polygons=f.geometry.type==='MultiPolygon'?f.geometry.coordinates:[f.geometry.coordinates];
 const bounds=polygons.flat(2).reduce((b,p)=>({minX:Math.min(b.minX,p[0]),maxX:Math.max(b.maxX,p[0]),minY:Math.min(b.minY,p[1]),maxY:Math.max(b.maxY,p[1])}),{minX:Infinity,maxX:-Infinity,minY:Infinity,maxY:-Infinity});
 return {zone:f.properties.tzid,polygons,...bounds};
});
const cache=new Map();
export default function locationTimezone(lat,lon){
 // Preserve the existing validation; geographic refinement stays offline.
 const fallback=approximateLookup(lat,lon),key=lat+','+lon;
 if(cache.has(key))return cache.get(key);
 const zones=[];
 for(const s of shapes)if(lon>=s.minX&&lon<=s.maxX&&lat>=s.minY&&lat<=s.maxY&&s.polygons.some(p=>polygonContains(p,lon,lat)))zones.push(s.zone);
 // Keep an already valid local convention on a genuine overlapping boundary.
 const zone=zones.includes(fallback)?fallback:zones[0]||fallback;
 if(cache.size>=128)cache.delete(cache.keys().next().value);
 cache.set(key,zone);return zone;
}
