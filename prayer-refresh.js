/** Reconcile local date and calendars on foreground/resume, network recovery and while open. */
export function setupPrayerRefresh({wake,document:doc=globalThis.document,window:win=globalThis.window,setInterval:every=globalThis.setInterval,clearInterval:cancel=globalThis.clearInterval}){
 const visible=()=>doc.visibilityState!=='hidden';
 const run=retryFailed=>{if(visible())wake({retryFailed})};
 const foreground=()=>run(false),online=()=>run(true);
 doc.addEventListener('visibilitychange',foreground);
 for(const name of ['pageshow','salati-native-resume'])win.addEventListener(name,foreground);
 win.addEventListener('online',online);
 const timer=every(foreground,60000);
 return ()=>{cancel(timer);doc.removeEventListener('visibilitychange',foreground);for(const name of ['pageshow','salati-native-resume'])win.removeEventListener(name,foreground);win.removeEventListener('online',online)};
}
