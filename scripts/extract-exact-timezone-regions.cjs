'use strict';
// Reproduction tool only; geobuf/pbf and the75MB reference are NOT app dependencies.
// NODE_PATH=<dev-decoder>/node_modules node scripts/extract-exact-timezone-regions.cjs <geo-tz8.1.11/package> <audit.json>
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{decode}=require('geobuf'),Pbf=require('pbf');
const [reference,auditPath]=process.argv.slice(2);if(!reference||!auditPath)throw Error('Supply the pinned geo-tz8.1.11 package directory and audited points');
const root=path.resolve(__dirname,'..'),dataFile=path.join(reference,'data/timezones.geojson.geo.dat'),indexFile=path.join(reference,'data/timezones.geojson.index.json'),index=JSON.parse(fs.readFileSync(indexFile));
const fd=fs.openSync(dataFile,'r'),features=[],sourceCells=[],used=new Set();
function children(b){const x=(b.left+b.right)/2,y=(b.top+b.bottom)/2;return {a:{left:x,right:b.right,bottom:y,top:b.top},b:{left:b.left,right:x,bottom:y,top:b.top},c:{left:b.left,right:x,bottom:b.bottom,top:y},d:{left:x,right:b.right,bottom:b.bottom,top:y}};}
const world={left:-179.9999,right:179.9999,bottom:-89.9999,top:89.9999};
function add(node,b,key,onlyZone){
 const unique=key+':'+(onlyZone||'all');if(used.has(unique))return;used.add(unique);
 if(Array.isArray(node)){
  if(node.length!==1||onlyZone&&!node.some(i=>index.timezones[i]===onlyZone))return;
  features.push({type:'Feature',properties:{tzid:index.timezones[node[0]]},geometry:{type:'Polygon',coordinates:[[[b.left,b.bottom],[b.right,b.bottom],[b.right,b.top],[b.left,b.top],[b.left,b.bottom]]]}});
  sourceCells.push({key,exactCell:true,zone:index.timezones[node[0]],bounds:b});return;
 }
 const bytes=Buffer.alloc(node.len);fs.readSync(fd,bytes,0,node.len,node.pos);const fc=decode(new Pbf(bytes));const chosen=fc.features.filter(f=>!onlyZone||f.properties.tzid===onlyZone);
 if(chosen.length){features.push(...chosen);sourceCells.push({key,pos:node.pos,len:node.len,filter:onlyZone||null});}
}
function leaf(lat,lon){let node=index.lookup,b=world,key='';while(node&&!Array.isArray(node)&&!(node.pos>=0&&node.len)){const c=children(b),x=(b.left+b.right)/2,y=(b.top+b.bottom)/2,k=lat>=y?(lon>=x?'a':'b'):(lon<x?'c':'d');node=node[k];b=c[k];key+=k;}if(node)add(node,b,key);}
for(const p of JSON.parse(fs.readFileSync(auditPath)).mismatches)leaf(p.lat,p.lon);
function zoneRegion(zone,bounds){function visit(node,b,key){if(!node||b.right<bounds.left||b.left>bounds.right||b.top<bounds.bottom||b.bottom>bounds.top)return;if(Array.isArray(node)||node.pos>=0&&node.len){add(node,b,key,zone);return;}for(const [k,c] of Object.entries(children(b)))visit(node[k],c,key+k);}visit(index.lookup,world,'');}
// Complete original territorial-water geometry for the two observed date-line island errors.
zoneRegion('Pacific/Fakaofo',{left:-174,right:-170,bottom:-11,top:-7});
zoneRegion('Pacific/Pago_Pago',{left:-173,right:-168,bottom:-16,top:-10});
fs.closeSync(fd);
const serialized=JSON.stringify({type:'FeatureCollection',features})+'\n',output=path.join(root,'world-data/exact-timezone-regions.json');fs.writeFileSync(output,serialized);
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const meta={sourcePackage:'geo-tz@8.1.11',upstream:'https://github.com/evansiroky/node-geo-tz',boundarySource:'https://github.com/evansiroky/timezone-boundary-builder',dataLicense:'ODbL1.0, OpenStreetMap contributors; included under dist/licenses',originalDataSha256:hash(fs.readFileSync(dataFile)),indexSha256:hash(fs.readFileSync(indexFile)),sha256:hash(serialized),featureCount:features.length,bytes:Buffer.byteLength(serialized),sourceCells,method:'Original exact source polygon regions for observed lookup mismatches; source quadtree uniform-cell rectangles where applicable. No guessed coordinate radii, invented UTC offsets, online lookup or geo-tz production dependency. Complete source Tokelau/American Samoa territorial geometry retained.'};
fs.writeFileSync(path.join(root,'world-data/exact-timezone-regions-SOURCES.json'),JSON.stringify(meta,null,2)+'\n');console.log('Extracted precise source regions',meta.featureCount,'features',meta.bytes,'bytes',meta.sha256);
