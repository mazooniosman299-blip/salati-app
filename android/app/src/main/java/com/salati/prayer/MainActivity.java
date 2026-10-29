package com.salati.prayer;
import com.salati.ads.AdsController;

import android.Manifest;import android.app.*;import android.appwidget.AppWidgetManager;import android.content.*;import android.content.pm.PackageManager;import android.graphics.Color;import android.hardware.*;import android.net.Uri;import android.os.*;import android.provider.Settings;import android.view.*;import android.webkit.*;import android.widget.*;import java.io.*;import java.util.*;

public final class MainActivity extends Activity implements SensorEventListener {
 static java.lang.ref.WeakReference<MainActivity> current=new java.lang.ref.WeakReference<>(null);
 static boolean nativeAdhanPlaying,nativeApproachPlaying;static volatile String playbackCode="inactive";
 static void notifyPlayback(String code){playbackCode=code;MainActivity activity=current.get();if(activity!=null)activity.main.post(()->{if(activity.web!=null)activity.web.evaluateJavascript("window.dispatchEvent(new CustomEvent('salati-native-playback',{detail:{code:"+org.json.JSONObject.quote(code)+"}}))",null);});}
 static void notifyQuran(String json){MainActivity activity=current.get();if(activity!=null)activity.main.post(()->{if(activity.resumed&&activity.web!=null)activity.web.evaluateJavascript("window.dispatchEvent(new CustomEvent('salati-native-quran',{detail:"+json+"}))",null);});}
 static void notifyAdhan(){nativeAdhanPlaying=true;MainActivity activity=current.get();if(activity!=null)activity.main.post(()->{if(activity.ads!=null)activity.ads.setNativePlayback(true);if(activity.web!=null)activity.web.evaluateJavascript("window.dispatchEvent(new Event('salati-native-adhan'))",null);});}
 static void notifyAdhanFinished(){nativeAdhanPlaying=false;MainActivity activity=current.get();if(activity!=null)activity.main.post(()->{if(activity.ads!=null)activity.ads.setNativePlayback(nativeAdhanPlaying||nativeApproachPlaying);});}
 static void notifyAnnouncement(String status){MainActivity activity=current.get();if(activity!=null)activity.main.post(()->{if(activity.web!=null)activity.web.evaluateJavascript("window.dispatchEvent(new CustomEvent('salati-native-announcement',{detail:{status:"+org.json.JSONObject.quote(status)+"}}))",null);});}
 static void notifyApproach(boolean playing){nativeApproachPlaying=playing;MainActivity activity=current.get();if(activity!=null)activity.main.post(()->{if(activity.ads!=null)activity.ads.setNativePlayback(nativeAdhanPlaying||nativeApproachPlaying);});}
 AdsController ads;
 static final String ORIGIN="https://appassets.androidplatform.net";WebView web;GeolocationPermissions.Callback geoCallback;String geoOrigin;SensorManager sensors;Sensor rotation;long lastSensor;boolean resumed,wantCompass,permissionPageReady;int activePermission;final Handler main=new Handler(Looper.getMainLooper());
 @Override public void onCreate(Bundle b){super.onCreate(b);if(AdhanService.active.get()==null)AlarmVolumeSession.restore(this);current=new java.lang.ref.WeakReference<>(this);getWindow().setStatusBarColor(getColor(R.color.salati_shell));getWindow().setNavigationBarColor(getColor(R.color.salati_shell));LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setBackgroundColor(getColor(R.color.salati_shell));root.setOnApplyWindowInsetsListener((v,in)->{v.setPadding(in.getSystemWindowInsetLeft(),in.getSystemWindowInsetTop(),in.getSystemWindowInsetRight(),in.getSystemWindowInsetBottom());return in;});web=new WebView(this);root.addView(web,new LinearLayout.LayoutParams(-1,0,1));setContentView(root);ads=new AdsController(this,root,()->notifyStatus());ads.setNativePlayback(nativeAdhanPlaying||nativeApproachPlaying);if(Build.VERSION.SDK_INT>=33)getOnBackInvokedDispatcher().registerOnBackInvokedCallback(android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT,this::handleBack);root.requestApplyInsets();web.setBackgroundColor(getColor(R.color.salati_shell));WebSettings s=web.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setGeolocationEnabled(true);s.setAllowFileAccess(false);s.setAllowContentAccess(false);s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);s.setMediaPlaybackRequiresUserGesture(true);s.setSupportMultipleWindows(false);sensors=(SensorManager)getSystemService(SENSOR_SERVICE);rotation=sensors.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR);web.addJavascriptInterface(new Bridge(),"SalatiNative");web.setWebViewClient(new WebViewClient(){
  @Override public WebResourceResponse shouldInterceptRequest(WebView v,WebResourceRequest r){Uri u=r.getUrl();if(!"appassets.androidplatform.net".equals(u.getHost()))return null;String p=u.getPath();if(p!=null&&p.startsWith("/quran-offline/"))return QuranDownloads.response(MainActivity.this,u,r.getRequestHeaders());if(p==null||!p.startsWith("/assets/www/")||p.contains(".."))return error();try{String asset=p.substring(8);InputStream in=getAssets().open(asset);String mime=mime(asset);Map<String,String> headers=new HashMap<>();headers.put("Access-Control-Allow-Origin",ORIGIN);headers.put("Cache-Control","no-cache");return new WebResourceResponse(mime,"UTF-8",200,"OK",headers,in);}catch(IOException e){return error();}}
  @Override public boolean shouldOverrideUrlLoading(WebView v,WebResourceRequest r){Uri u=r.getUrl();if(ORIGIN.equals(u.getScheme()+"://"+u.getHost())&&u.getPath()!=null&&u.getPath().startsWith("/assets/www/"))return false;openExternal(u);return true;}
  @Override public void onPageFinished(WebView v,String u){if(u.startsWith(ORIGIN+"/assets/www/")){notifyStatus();permissionPageReady=true;requestFirstNotificationPermission();}}
 });web.setWebChromeClient(new WebChromeClient(){@Override public void onGeolocationPermissionsShowPrompt(String origin,GeolocationPermissions.Callback callback){if(!origin.startsWith(ORIGIN)){callback.invoke(origin,false,false);return;}if(checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)==PackageManager.PERMISSION_GRANTED){callback.invoke(origin,true,false);return;}if(geoCallback!=null)geoCallback.invoke(geoOrigin,false,false);geoCallback=callback;geoOrigin=origin;requestLocationPermission();}});web.loadUrl(ORIGIN+"/assets/www/index.html");}
 boolean backPending;
 void finishBackNavigation(){if(isFinishing()||isDestroyed())return;if(web!=null&&web.canGoBack())web.goBack();else finish();}
 void handleBack(){
  if(backPending||isFinishing()||isDestroyed())return;
  if(web==null){finish();return;}
  backPending=true;
  try{web.evaluateJavascript("typeof window.salatiHandleBack==='function' && window.salatiHandleBack()",result->{backPending=false;if(!"true".equals(result))finishBackNavigation();});}
  catch(RuntimeException error){backPending=false;finishBackNavigation();}
 }
 // Legacy devices (API 26-32) use this entry point. API 33+ registers
 // OnBackInvokedDispatcher in onCreate, including Android 16 gestures.
 @android.annotation.SuppressLint("GestureBackNavigation")
 @Override public void onBackPressed(){handleBack();}
 static WebResourceResponse error(){return new WebResourceResponse("text/plain","UTF-8",404,"Not found",null,new ByteArrayInputStream(new byte[0]));}
 static String mime(String a){if(a.endsWith(".js"))return "application/javascript";if(a.endsWith(".json"))return "application/json";if(a.endsWith(".css"))return "text/css";if(a.endsWith(".html"))return "text/html";if(a.endsWith(".svg"))return "image/svg+xml";if(a.endsWith(".webp"))return "image/webp";if(a.endsWith(".png"))return "image/png";if(a.endsWith(".mp3"))return "audio/mpeg";if(a.endsWith(".ogg"))return "audio/ogg";if(a.endsWith(".ttf"))return "font/ttf";return "text/plain";}
 void openExternal(Uri u){if(!"https".equals(u.getScheme()))return;try{startActivity(new Intent(Intent.ACTION_VIEW,u).addCategory(Intent.CATEGORY_BROWSABLE));}catch(ActivityNotFoundException ignored){}}
 void notifyStatus(){if(web!=null)web.evaluateJavascript("window.dispatchEvent(new Event('salati-native-status'))",null);}
 boolean launchSettings(Intent intent){try{startActivity(intent);return true;}catch(RuntimeException error){return false;}}
 void appSettings(){if(!launchSettings(new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS,Uri.parse("package:"+getPackageName()))))Toast.makeText(this,"افتح إعدادات الهاتف ← التطبيقات ← صلاتي ← الأذونات",Toast.LENGTH_LONG).show();}
 void notificationSettings(){if(!launchSettings(new Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).putExtra(Settings.EXTRA_APP_PACKAGE,getPackageName())))appSettings();}
 void permissions(){requestBackgroundPermission();}
 void requestBackgroundPermission(){
  if(isFinishing()||isDestroyed())return;
  if(PrayerSchedule.exactAlarmsAllowed(this)){
   PrayerSchedule.scheduleNext(this,System.currentTimeMillis());
   Toast.makeText(this,"مسموح بالأذان في الخلفية",Toast.LENGTH_SHORT).show();
   notifyStatus();
  }else openExactSettings();
 }
 boolean notificationDecisionPending(){return Build.VERSION.SDK_INT>=33&&checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED&&!getPreferences(0).getBoolean("notificationDecisionRecorded",false);}
 void requestLocationPermission(){
  if(geoCallback==null||activePermission!=0||isFinishing()||isDestroyed())return;
  if(notificationDecisionPending()){requestFirstNotificationPermission();return;}
  activePermission=101;requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION,Manifest.permission.ACCESS_COARSE_LOCATION},101);
 }
 void requestFirstNotificationPermission(){
  if(!permissionPageReady||!resumed||activePermission!=0||isFinishing()||isDestroyed())return;
  if(!notificationDecisionPending()){requestLocationPermission();return;}
  activePermission=102;requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},102);
 }
 void requestNotificationPermission(){
  if(Build.VERSION.SDK_INT>=33&&checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED){
   boolean asked=getPreferences(0).getBoolean("notificationAsked",false);
   if(!asked||shouldShowRequestPermissionRationale(Manifest.permission.POST_NOTIFICATIONS)){getPreferences(0).edit().putBoolean("notificationAsked",true).apply();requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},102);return;}
  }
  if(PrayerSchedule.notificationsAllowed(this)){
   showNotificationConfirmation();
   return;
  }
  new AlertDialog.Builder(this)
   .setTitle("السماح بإشعارات صلاتي؟")
   .setMessage("يحتاج هاتفك إلى تفعيل الإشعارات من إعدادات النظام. اختر السماح لفتحها وتفعيلها.")
   .setItems(new String[]{"السماح","عدم السماح"},(dialog,which)->{if(which==0)notificationSettings();else notifyStatus();})
   .show();
 }
 void showNotificationConfirmation(){
  if(isFinishing()||isDestroyed())return;
  final Dialog dialog=new Dialog(this);dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
  float density=getResources().getDisplayMetrics().density;
  boolean dark=(getResources().getConfiguration().uiMode&android.content.res.Configuration.UI_MODE_NIGHT_MASK)==android.content.res.Configuration.UI_MODE_NIGHT_YES;
  int ink=getColor(dark?R.color.salati_ink_dark:R.color.salati_ink_light),surface=getColor(dark?R.color.salati_surface_dark:R.color.salati_surface_light);
  LinearLayout content=new LinearLayout(this);content.setOrientation(LinearLayout.VERTICAL);content.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);int pad=(int)(24*density);content.setPadding(pad,pad,pad,pad);
  android.graphics.drawable.GradientDrawable background=new android.graphics.drawable.GradientDrawable();background.setColor(surface);background.setCornerRadius(24*density);content.setBackground(background);
  TextView title=new TextView(this);title.setText("الإشعارات مفعّلة");title.setTextColor(ink);title.setTextSize(21);title.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);content.addView(title);
  TextView message=new TextView(this);message.setText("الإشعارات مسموحة بالفعل لتطبيق صلاتي.");message.setTextColor(ink);message.setTextSize(16);message.setLineSpacing(5*density,1);LinearLayout.LayoutParams textParams=new LinearLayout.LayoutParams(-1,-2);textParams.topMargin=(int)(12*density);textParams.bottomMargin=(int)(24*density);content.addView(message,textParams);
  Button close=new Button(this);close.setText("حسنًا");close.setTextSize(16);close.setTextColor(getColor(R.color.salati_action_ink));close.setAllCaps(false);android.graphics.drawable.GradientDrawable buttonBackground=new android.graphics.drawable.GradientDrawable();buttonBackground.setColor(getColor(R.color.salati_action));buttonBackground.setCornerRadius(14*density);close.setBackground(buttonBackground);content.addView(close,new LinearLayout.LayoutParams(-1,(int)(48*density)));close.setOnClickListener(v->{dialog.dismiss();notifyStatus();});
  dialog.setContentView(content);Window window=dialog.getWindow();if(window!=null){window.setBackgroundDrawable(new android.graphics.drawable.ColorDrawable(Color.TRANSPARENT));window.addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND);window.setDimAmount(.5f);}dialog.show();if(window!=null)window.setLayout(Math.min((int)(380*density),getResources().getDisplayMetrics().widthPixels-(int)(40*density)),-2);
 }
 void openExactSettings(){
  if(Build.VERSION.SDK_INT<31){notifyStatus();return;}
  if(!launchSettings(new Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM,Uri.parse("package:"+getPackageName())))&&!launchSettings(new Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM)))appSettings();
 }
 @Override public void onRequestPermissionsResult(int code,String[] p,int[] results){
  super.onRequestPermissionsResult(code,p,results);if(code==101||code==102)activePermission=0;
  if(code==101&&geoCallback!=null){boolean ok=checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION)==PackageManager.PERMISSION_GRANTED||checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)==PackageManager.PERMISSION_GRANTED;geoCallback.invoke(geoOrigin,ok,false);geoCallback=null;}
  if(code==102){if(results.length>0)getPreferences(0).edit().putBoolean("notificationDecisionRecorded",true).putBoolean("notificationAsked",true).apply();PrayerSchedule.scheduleNext(this,System.currentTimeMillis());notifyStatus();if(results.length>0)requestLocationPermission();}
  if(results.length>0)main.post(()->requestFirstNotificationPermission());
 }
 @Override protected void onResume(){super.onResume();current=new java.lang.ref.WeakReference<>(this);resumed=true;main.post(()->requestFirstNotificationPermission());if(ads!=null){ads.setNativePlayback(nativeAdhanPlaying||nativeApproachPlaying);ads.resume();}if(web!=null){web.onResume();web.evaluateJavascript("window.dispatchEvent(new Event(\"salati-native-resume\"))",null);}if(wantCompass&&rotation!=null)sensors.registerListener(this,rotation,SensorManager.SENSOR_DELAY_GAME);PrayerSchedule.scheduleNext(this,System.currentTimeMillis());PrayerWidget.updateAll(this);notifyStatus();}
 @Override protected void onPause(){resumed=false;if(ads!=null)ads.pause();sensors.unregisterListener(this);if(web!=null)web.onPause();super.onPause();}
 @Override protected void onDestroy(){if(ads!=null)ads.destroy();if(geoCallback!=null)geoCallback.invoke(geoOrigin,false,false);if(current.get()==this)current.clear();sensors.unregisterListener(this);if(web!=null){web.removeJavascriptInterface("SalatiNative");web.destroy();web=null;}super.onDestroy();}
 @Override public void onAccuracyChanged(Sensor s,int a){}
 @Override public void onSensorChanged(SensorEvent e){if(!resumed||web==null||SystemClock.elapsedRealtime()-lastSensor<80)return;lastSensor=SystemClock.elapsedRealtime();float[] r=new float[9],angles=new float[3];SensorManager.getRotationMatrixFromVector(r,e.values);SensorManager.getOrientation(r,angles);double heading=(Math.toDegrees(angles[0])+360)%360,beta=Math.toDegrees(angles[1]),gamma=Math.toDegrees(angles[2]);int accuracy=e.accuracy==SensorManager.SENSOR_STATUS_UNRELIABLE?60:10;String js="(()=>{const e=new Event('deviceorientationabsolute');Object.assign(e,{absolute:false,webkitCompassHeading:"+heading+",webkitCompassAccuracy:"+accuracy+",beta:"+beta+",gamma:"+gamma+"});window.dispatchEvent(e)})()";web.evaluateJavascript(js,null);}
 final class Bridge{
  @JavascriptInterface public String quranPlay(String json){return QuranService.start(MainActivity.this,json);}
  @JavascriptInterface public String quranState(){return QuranService.state();}
  @JavascriptInterface public String quranQueue(){return QuranService.queue();}
  @JavascriptInterface public void quranPause(String session){QuranService.command(session,"PAUSE",0,false,false);}
  @JavascriptInterface public void quranResume(String session){QuranService.command(session,"PLAY",0,false,false);}
  @JavascriptInterface public void quranStop(String session){QuranService.command(session,"STOP",0,false,false);}
  @JavascriptInterface public void quranSeek(String session,long ms){QuranService.command(session,"SEEK",ms,false,false);}
  @JavascriptInterface public void quranOptions(String session,boolean repeat,boolean autoNext){QuranService.command(session,"OPTIONS",0,repeat,autoNext);}
  @JavascriptInterface public String quranDownloadStatus(String reciter){return QuranDownloads.status(MainActivity.this,reciter);}
  @JavascriptInterface public String downloadQuran(String reciter,int surah){return QuranDownloads.download(MainActivity.this,reciter,surah);}
  @JavascriptInterface public String cancelQuranDownloads(String reciter){return QuranDownloads.cancel(MainActivity.this,reciter);}
  @JavascriptInterface public String deleteQuranDownload(String reciter,int surah){return QuranDownloads.delete(MainActivity.this,reciter,surah);}
  @JavascriptInterface public String quranOfflineUrl(String reciter,int surah){return QuranDownloads.localUrl(MainActivity.this,reciter,surah);}
  @JavascriptInterface public void setAdhanVolume(double volume){if(Double.isFinite(volume))main.post(()->AdhanService.volume(volume));}
  @JavascriptInterface public String audioState(){return playbackCode;}
  @JavascriptInterface public void previewAdhan(String kind,String voice,double volume){if(!("adhan".equals(kind)||"dua".equals(kind))||!voice.matches("nufais|qatami|makkah|aqsa")||!Double.isFinite(volume))return;main.post(()->{try{Intent intent=new Intent(MainActivity.this,AdhanService.class).putExtra("preview",true).putExtra("kind",kind).putExtra("voice",voice).putExtra("volume",Math.max(0,Math.min(1,volume))).putExtra("prayer","dhuhr");startForegroundService(intent);}catch(RuntimeException error){notifyPlayback("error");}});}
  @JavascriptInterface public String platform(){return "android";}
  @JavascriptInterface public void setAdContext(String tab,boolean playing){main.post(()->{if(ads!=null)ads.setContext(tab,playing);});}
  @JavascriptInterface public String adPrivacyStatus(){return "{\"enabled\":"+(ads!=null&&ads.enabled())+",\"privacyRequired\":"+(ads!=null&&ads.privacyRequired())+"}";}
  @JavascriptInterface public void showAdPrivacyOptions(){main.post(()->{if(ads!=null)ads.showPrivacyOptions();});}
  @JavascriptInterface public String status(){return PrayerSchedule.status(MainActivity.this);}
  @JavascriptInterface public String sync(String json){try{PrayerSchedule.sync(MainActivity.this,json);PrayerWidget.updateAll(MainActivity.this);return "ok";}catch(Exception e){return "invalid";}}
  @JavascriptInterface public void requestPermissions(){main.post(()->requestBackgroundPermission());}
  @JavascriptInterface public void requestNotifications(){main.post(()->requestNotificationPermission());}
  @JavascriptInterface public void requestBackgroundAdhan(){main.post(()->requestBackgroundPermission());}
  @JavascriptInterface public void stopAdhan(){main.post(()->{stopService(new Intent(MainActivity.this,AdhanService.class));if(stopService(new Intent(MainActivity.this,ApproachService.class)))ArabicSpeech.record(MainActivity.this,"cancelled");});}
  @JavascriptInterface public void stopAnnouncement(){main.post(()->{if(stopService(new Intent(MainActivity.this,ApproachService.class)))ArabicSpeech.record(MainActivity.this,"cancelled");});}
  @JavascriptInterface public void previewAnnouncement(String kind,String prayer){if(kind==null||prayer==null||!kind.matches("approach|fajr")||!prayer.matches("fajr|dhuhr|asr|maghrib|isha"))return;main.post(()->{try{startForegroundService(new Intent(MainActivity.this,ApproachService.class).putExtra("preview",true).putExtra("kind",kind).putExtra("prayer",prayer));}catch(RuntimeException error){ArabicSpeech.record(MainActivity.this,"error");}});}
  @JavascriptInterface public void openNotifications(){main.post(()->notificationSettings());}
  @JavascriptInterface public boolean startCompass(){if(rotation==null)return false;main.post(()->{wantCompass=true;if(resumed)sensors.registerListener(MainActivity.this,rotation,SensorManager.SENSOR_DELAY_GAME);});return true;}
  @JavascriptInterface public void stopCompass(){main.post(()->{wantCompass=false;sensors.unregisterListener(MainActivity.this);});}
  @JavascriptInterface public boolean pinWidget(){AppWidgetManager manager=getSystemService(AppWidgetManager.class);if(!manager.isRequestPinAppWidgetSupported())return false;main.post(()->manager.requestPinAppWidget(new ComponentName(MainActivity.this,PrayerWidget.class),null,null));return true;}
 }
}
