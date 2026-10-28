const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),Module=require('node:module'),esbuild=require('esbuild');
function load(file){const m=new Module(file,module);m._compile(esbuild.buildSync({entryPoints:[file],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,file);return m.exports;}
(async()=>{
 const source=fs.readFileSync('app-source.js','utf8'),start=source.indexOf('let locationRequest;'),end=source.indexOf(";$('locate').onclick=useLocation;",start),{LocationIntent}=load('location-startup.js'),engine=load('prayer-engine.js'),location=load('location.js');
 for(const [method,madhab]of [['Karachi','Hanafi'],['Egyptian','Shafi'],['Auto','Hanafi']]){
  const state={lat:30.0444,lon:31.2357,zone:'Africa/Cairo',locationSet:true,locationMode:'auto',method,madhab,adjustments:{fajr:2},name:'Cairo'};
  const c={...location,state,locationIntent:new LocationIntent(),pendingLocationGeneration:0,locationBusy:false,$:()=>({disabled:false,textContent:''}),status(){},render(){},save(){},freshPosition:async()=>({coords:{latitude:state.lat,longitude:state.lon,accuracy:10},timestamp:Date.now()}),navigator:{geolocation:{}},regionalProfile:engine.regionalProfile,cities:load('cities.js').cities,WORLD_COUNTRIES:[],worldCountry:'',tr:a=>a};
  vm.createContext(c);vm.runInContext(source.slice(start,end+1),c);await c.useLocation();assert.equal(state.method,method,'GPS must preserve explicit calculation method');assert.equal(state.madhab,method==='Auto'?'Shafi':madhab);assert.equal(state.adjustments.fajr,2);
 }
 const {QiblaCompass}=load('compass.js');let permissionCalls=0;global.window={SalatiNative:{startCompass:()=>true,stopCompass(){}},addEventListener(){},removeEventListener(){}};
 const compass=new QiblaCompass(()=>({lat:30,lon:31}),()=>{});await compass.enable();assert(compass.enabled,'Native compass must work without browser orientation constructor');compass.disable();
 window.DeviceOrientationEvent={requestPermission:async()=>{permissionCalls++;return 'denied'}};await compass.enable();assert(compass.enabled);assert.equal(permissionCalls,0,'Native sensor must not request browser sensor permission');compass.disable();
 delete window.SalatiNative;window.isSecureContext=true;await compass.enable();assert.equal(compass.status,'denied');assert.equal(permissionCalls,1);compass.disable();delete window;
 console.log('PASS: GPS retains explicit calculation choices/offsets; native compass independent of browser sensor API; browser permission still enforced.');
})().catch(e=>{console.error(e);process.exitCode=1});
