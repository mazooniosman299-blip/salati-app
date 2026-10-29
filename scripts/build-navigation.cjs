const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),library=path.join(root,'node_modules/@phosphor-icons/core');
const icons={times:'clock',mushaf:'book-open',qibla:'compass',dhikr:'heart',tasbih:'circle-dashed',settings:'gear-six'};
const symbols=Object.entries(icons).map(([id,name])=>{
 const source=fs.readFileSync(path.join(library,'assets/regular',name+'.svg'),'utf8');
 const body=source.replace(/^.*?<svg[^>]*>/s,'').replace(/<\/svg>\s*$/,'');
 return `<symbol id="${id}" viewBox="0 0 256 256" fill="currentColor" stroke="none">${body}</symbol>`;
});
fs.writeFileSync(path.join(root,'dist/icons/navigation.svg'),'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">\n<!-- Phosphor Icons regular: MIT; see PHOSPHOR-LICENSE.txt. -->\n'+symbols.join('\n')+'\n</svg>\n');
fs.writeFileSync(path.join(root,'dist/icons/PHOSPHOR-LICENSE.txt'),fs.readFileSync(path.join(library,'LICENSE'),'utf8').replace(/\r\n/g,'\n'));
fs.mkdirSync(path.join(root,'dist/licenses'),{recursive:true});
fs.writeFileSync(path.join(root,'dist/licenses/MOTION-LICENSES.txt'),['motion','motion-dom','motion-utils','framer-motion'].map(name=>name+'\n'+fs.readFileSync(path.join(root,'node_modules',name,'LICENSE.md'),'utf8')).join('\n\n'));
console.log('Built six local Phosphor navigation icons.');

fs.copyFileSync(path.join(library,'assets/fill/map-pin-fill.svg'),path.join(root,'dist/icons/location-fill.svg'));
