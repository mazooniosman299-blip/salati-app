const $=id=>document.getElementById(id);
export class QuranDownloadControls{
 constructor({offline,getReciter,getSurah,getLang,beforeRemove}){
  Object.assign(this,{offline,getReciter,getSurah,getLang,beforeRemove});this.serial=0;this.message='';
  $('qDownloadSurah').onclick=()=>this.act(()=>offline.download(getReciter(),getSurah()));
  $('qDownloadAll').onclick=()=>{
   $('qDownloadConfirmTitle').textContent=this.tr('تنزيل المصحف كاملًا؟','Download the full Quran?');
   $('qDownloadConfirmText').textContent=this.tr('سيتم تنزيل السور الـ١١٤ بصوت '+getReciter().ar+'. قد تحتاج مساحة كبيرة وتستهلك بيانات الإنترنت.','Download all 114 surahs by '+getReciter().en+'. This can use substantial storage and mobile data.');
   this.confirmReciter=getReciter();$('qDownloadConfirm').showModal();
  };
  $('qDownloadConfirmYes').onclick=()=>{$('qDownloadConfirm').close();this.act(()=>offline.download(this.confirmReciter));};
  $('qDownloadConfirmNo').onclick=()=>$('qDownloadConfirm').close();
  $('qDownloadCancel').onclick=()=>this.act(()=>offline.cancel(getReciter()));
  $('qDownloadDelete').onclick=()=>this.act(async()=>{beforeRemove();await offline.remove(getReciter(),getSurah());});
  $('qDownloadDeleteAll').onclick=()=>{
   $('qDownloadDeleteConfirm').showModal();
  };
  $('qDownloadDeleteYes').onclick=()=>{$('qDownloadDeleteConfirm').close();this.act(async()=>{beforeRemove();await offline.remove(getReciter());});};
  $('qDownloadDeleteNo').onclick=()=>$('qDownloadDeleteConfirm').close();
  // The previous 2-second loop triggered SHA and DownloadManager scans
  // even when nothing was downloading. Poll 15s for active transfers and
  // 60s for idle libraries; never poll a hidden page or background tab.
  this.lastPoll=0;this.activeTransfers=false;
  const refresh=(force=false)=>{
   if(document.hidden||$('mushaf').hidden)return;
   const now=Date.now(),minimum=this.activeTransfers?15000:60000;
   if(!force&&now-this.lastPoll<minimum)return;
   this.lastPoll=now;this.refresh();
  };
  this.timer=setInterval(()=>refresh(),15000);
  document.addEventListener('visibilitychange',()=>refresh(true));
  window.addEventListener('online',()=>refresh(true));
 }
 tr(ar,en){return this.getLang()==='ar'?ar:en;}
 async act(action){
  this.message='';
  try{await action();}catch(error){this.message=error.message==='space'?this.tr('المساحة غير كافية. احذف بعض التنزيلات ثم حاول مجددًا.','Not enough storage. Remove some downloads and retry.'):this.tr('تعذر بدء التنزيل. تحقق من الإنترنت والمساحة المتاحة.','Could not start the download. Check your connection and free storage.');}
  this.refresh();
 }
 async refresh(){
  const serial=++this.serial,reciter=this.getReciter(),surah=this.getSurah();
  try{
   const rows=await this.offline.list(reciter);if(serial!==this.serial)return;
   const saved=rows.filter(row=>row.state==='saved'),active=rows.filter(row=>['queued','downloading'].includes(row.state));
   this.activeTransfers=active.length>0;
   const current=rows.find(row=>row.surah===surah),busy=current&&['queued','downloading'].includes(current.state);
   $('qDownloadSurah').disabled=!this.offline.available||busy||current?.state==='saved';
   $('qDownloadAll').disabled=!this.offline.available||saved.length===reciter.surahs.length||active.length>0;
   $('qDownloadCancel').hidden=!active.length;
   $('qDownloadDelete').hidden=current?.state!=='saved';
   $('qDownloadDeleteAll').hidden=!saved.length;
   let status=current?.state==='saved'?this.tr('هذه السورة محفوظة بدون إنترنت.','This surah is saved for offline listening.'):this.tr('هذه السورة غير منزّلة.','This surah has not been downloaded.');
   if(saved.length)status+=' '+this.tr('المحفوظ بصوت هذا القارئ: '+saved.length+' / '+reciter.surahs.length+'.','Saved for this reciter: '+saved.length+' / '+reciter.surahs.length+'.');
   if(active.length){const downloading=active.find(row=>row.state==='downloading'),progress=downloading?.total>0?' '+Math.min(100,Math.floor(downloading.bytes/downloading.total*100))+'%':'';status+=' '+this.tr('جارٍ التنزيل'+progress+' · المتبقي '+active.length+'.','Downloading'+progress+' · '+active.length+' remaining.');}
   const failed=rows.filter(row=>row.state==='failed');
   if(failed.length)status+=' '+(failed.some(row=>row.error==='space')?this.tr('المساحة غير كافية.','Not enough storage.'):this.tr('تعذر تنزيل '+failed.length+' سورة. اتصل بالإنترنت وأعد التنزيل.','Could not download '+failed.length+' surah(s). Reconnect and retry.'));
   $('qDownloadStatus').textContent=this.message||status;
  }catch{$('qDownloadStatus').textContent=this.tr('تعذر قراءة التنزيلات المحفوظة.','Could not read saved downloads.');}
 }
}
