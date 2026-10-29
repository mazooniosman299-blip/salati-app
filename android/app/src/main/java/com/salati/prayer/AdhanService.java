package com.salati.prayer;
import android.app.*;import android.content.*;import android.media.*;import android.os.*;import org.json.JSONObject;
public final class AdhanService extends Service{
 static java.lang.ref.WeakReference<AdhanService> active=new java.lang.ref.WeakReference<>(null);
 @Override public void onCreate(){super.onCreate();AlarmVolumeSession.restore(this);active=new java.lang.ref.WeakReference<>(this);}
 static void volume(double value){AdhanService service=active.get();if(service==null)return;float level=(float)Math.max(0,Math.min(1,value));try{if(service.settings!=null)service.settings.put("volume",level);}catch(Exception ignored){}service.applyFocus();}
 PcmAudioPlayer player;ArabicSpeech prelude;String pendingRecording;AudioManager manager;AudioFocusRequest focus;PowerManager.WakeLock wake;Handler handler=new Handler(Looper.getMainLooper());JSONObject settings;boolean duaPlaying,preview,terminal;int startId;long generation;AudioAttributes attributes;AudioFocusPolicy focusState=new AudioFocusPolicy();
 public IBinder onBind(Intent i){return null;}
 static String prayerName(String p){switch(p==null?"":p){case "fajr":return "الفجر";case "dhuhr":return "الظهر";case "asr":return "العصر";case "maghrib":return "المغرب";case "isha":return "العشاء";default:return "الصلاة";}}
 Notification notice(String title){NotificationChannel channel=new NotificationChannel("salati_adhan","أذان الصلاة",NotificationManager.IMPORTANCE_LOW);channel.setSound(null,null);getSystemService(NotificationManager.class).createNotificationChannel(channel);PendingIntent open=PendingIntent.getActivity(this,0,new Intent(this,MainActivity.class),PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);PendingIntent stop=PendingIntent.getService(this,1,new Intent(this,AdhanService.class).setAction("STOP"),PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);return new Notification.Builder(this,"salati_adhan").setSmallIcon(com.salati.prayer.R.drawable.ic_notification).setContentTitle(title).setContentText("صلاتي · اضغط إيقاف لإنهاء الصوت").setContentIntent(open).setOngoing(true).setCategory(Notification.CATEGORY_ALARM).addAction(new Notification.Action.Builder(null,"إيقاف",stop).build()).build();}
 public int onStartCommand(Intent i,int flags,int id){
  startId=id;stopService(new Intent(this,FajrPreviewService.class));
  if(i==null||"STOP".equals(i.getAction())){finishPlayback("stopped");return START_NOT_STICKY;}
  release();focusState=new AudioFocusPolicy();terminal=false;settings=PrayerSchedule.config(this);preview=i.getBooleanExtra("preview",false);
  if(!preview&&!settings.optBoolean("enabled")){finishPlayback("stopped");return START_NOT_STICKY;}
  if(preview)try{settings.put("voice",i.getStringExtra("voice"));settings.put("volume",i.getDoubleExtra("volume",1.0));settings.put("dua",false);}catch(Exception ignored){}
  String prayer=i.getStringExtra("prayer");startForeground(71,notice(preview?"الاستماع للأذان والدعاء":"حان وقت صلاة "+prayerName(prayer)));
  MainActivity.notifyAdhan();MainActivity.notifyPlayback("loading");
  wake=getSystemService(PowerManager.class).newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,"salati:adhan");wake.acquire(600000);long ticket=generation;handler.postDelayed(()->{if(ticket==generation)finishPlayback("error");},600000);
  manager=getSystemService(AudioManager.class);attributes=new AudioAttributes.Builder().setUsage(preview?AudioAttributes.USAGE_MEDIA:AudioAttributes.USAGE_ALARM).setContentType(AudioAttributes.CONTENT_TYPE_SPEECH).build();
  focus=new AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN_TRANSIENT).setAudioAttributes(attributes).setWillPauseWhenDucked(false).setOnAudioFocusChangeListener(change->{if(ticket==generation)onAudioFocusChange(change);},handler).build();
  if(manager.requestAudioFocus(focus)!=AudioManager.AUDIOFOCUS_REQUEST_GRANTED){finishPlayback("blocked");return START_NOT_STICKY;}
  AlarmVolumeSession.begin(this,settings.optBoolean("silentMode",true),!preview,(float)settings.optDouble("volume",1.0));
  duaPlaying="dua".equals(i.getStringExtra("kind"));
  String voice=settings.optString("voice","nufais");if(!voice.matches("nufais|qatami|makkah|aqsa"))voice="nufais";
  String name=duaPlaying?"wasilah":"qatami".equals(voice)?"qatami-user-v2":voice;
  if(!preview&&"fajr".equals(prayer)&&settings.optBoolean("fajrAnnouncement",true)&&FajrAnnouncementPolicy.canPlay(PrayerSchedule.notificationsAllowed(this),getSystemService(NotificationManager.class).getCurrentInterruptionFilter(),settings.optDouble("volume",1))){
   pendingRecording=name;prelude=new ArabicSpeech(this,attributes);MainActivity.notifyPlayback("fajr");prelude.speak("الصلاة خير من النوم",(float)settings.optDouble("volume",1),()->{if(ticket!=generation)return;prelude=null;if(!focusState.paused&&pendingRecording!=null){String recording=pendingRecording;pendingRecording=null;play(recording);}});
  }else play(name);return START_NOT_STICKY;
 }
 void onAudioFocusChange(int change){focusState.change(change);if(focusState.stopped){finishPlayback("stopped");return;}if(prelude!=null&&focusState.paused){prelude.close();prelude=null;}if(!focusState.paused&&prelude==null&&pendingRecording!=null){String recording=pendingRecording;pendingRecording=null;play(recording);return;}applyFocus();}
 void applyFocus(){if(settings==null)return;float preferred=(float)Math.max(0,Math.min(1,settings.optDouble("volume",1.0)));if(prelude!=null)prelude.setVolume(focusState.volume(preferred));if(player!=null){player.setVolume(focusState.volume(preferred));player.setPaused(focusState.paused);}}
 void play(String name){
  if(player!=null)player.stop();
  String file="qatami-user-v2".equals(name)?"qatami-original-v4.ogg":name+("wasilah".equals(name)?"":"-clean-v3")+".mp3";
  float volume=focusState.volume((float)Math.max(0,Math.min(1,settings.optDouble("volume",1.0))));
  final PcmAudioPlayer current=new PcmAudioPlayer(this);player=current;current.setPaused(focusState.paused);
  if(!preview)PrayerSchedule.recordDelivery(this,"playing",null);
  MainActivity.notifyPlayback("wasilah".equals(name)?"dua":"fajr".equals(name)?"fajr":"adhan");
  current.play("www/audio/"+file,attributes,volume,new PcmAudioPlayer.Listener(){
   public void complete(){if(player!=current)return;if(!preview&&!duaPlaying&&settings.optBoolean("dua",true)&&PrayerSchedule.config(AdhanService.this).optBoolean("enabled")){duaPlaying=true;getSystemService(NotificationManager.class).notify(71,notice("دعاء الوسيلة"));play("wasilah");}else finishPlayback("finished");}
   public void error(Exception error){if(player!=current)return;android.util.Log.w("SalatiAudio","PCM playback failed",error);finishPlayback("error");}
  });
 }
 void finishPlayback(String code){if(!preview)PrayerSchedule.recordDelivery(this,code,null);terminal=true;release();MainActivity.notifyPlayback(code);stopForeground(STOP_FOREGROUND_REMOVE);stopSelf(startId);}
 void release(){generation++;if(prelude!=null){prelude.close();prelude=null;}pendingRecording=null;handler.removeCallbacksAndMessages(null);if(player!=null){player.stop();player=null;}AlarmVolumeSession.restore(this);if(manager!=null&&focus!=null){manager.abandonAudioFocusRequest(focus);focus=null;}if(wake!=null&&wake.isHeld())wake.release();wake=null;}
 public void onDestroy(){if(active.get()==this)active.clear();release();if(!terminal)MainActivity.notifyPlayback("stopped");MainActivity.notifyAdhanFinished();stopForeground(STOP_FOREGROUND_REMOVE);super.onDestroy();}
}
