package com.salati.prayer;
import android.app.*;import android.content.*;import android.media.*;import android.os.*;import org.json.JSONObject;
/** Explicit Fajr-phrase preview only. No scheduled pre-prayer announcements. */
public final class FajrPreviewService extends Service {
 private AudioManager manager;private AudioFocusRequest focus;private PowerManager.WakeLock wake;private ArabicSpeech speech;private final Handler handler=new Handler(Looper.getMainLooper());private int startId;private boolean terminal;private long generation;
 public IBinder onBind(Intent i){return null;}
 public int onStartCommand(Intent intent,int flags,int id){
  startId=id;boolean replacingOwnAudio=speech!=null;release();terminal=false;long ticket=generation;if(intent==null){finish("error");return START_NOT_STICKY;}
  if(!intent.getBooleanExtra("preview",false)||!"fajr".equals(intent.getStringExtra("kind"))||!"fajr".equals(intent.getStringExtra("prayer"))){finish("blocked");return START_NOT_STICKY;}
  JSONObject settings=PrayerSchedule.config(this);double volume=settings.optDouble("volume",1);
  if(!FajrAnnouncementPolicy.canPlay(PrayerSchedule.notificationsAllowed(this),getSystemService(NotificationManager.class).getCurrentInterruptionFilter(),volume)){finish(volume==0?"muted":"blocked");return START_NOT_STICKY;}
  manager=getSystemService(AudioManager.class);QuranService quran=QuranService.active;
  boolean busy=manager==null||AdhanService.active.get()!=null||quran!=null&&quran.wantPlay||!replacingOwnAudio&&manager.isMusicActive();
  try{
   NotificationChannel channel=new NotificationChannel("salati_fajr_phrase","عبارة الفجر",NotificationManager.IMPORTANCE_DEFAULT);channel.setSound(null,null);getSystemService(NotificationManager.class).createNotificationChannel(channel);
   String text="الصلاة خير من النوم";PendingIntent open=PendingIntent.getActivity(this,77,new Intent(this,MainActivity.class),PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
   startForeground(77,new Notification.Builder(this,"salati_fajr_phrase").setSmallIcon(R.drawable.ic_notification).setContentTitle(text).setContentText("استعد للصلاة").setContentIntent(open).setOnlyAlertOnce(true).setCategory(Notification.CATEGORY_REMINDER).setAutoCancel(true).setTimeoutAfter(60000).build());
   if(busy){finish("blocked");return START_NOT_STICKY;}MainActivity.notifyFajrPreview(true);wake=getSystemService(PowerManager.class).newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,"salati:fajr-preview");wake.acquire(35000);handler.postDelayed(()->{if(ticket==generation)finish("error");},33000);
   AudioAttributes attributes=new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_MEDIA).setContentType(AudioAttributes.CONTENT_TYPE_SPEECH).build();
   focus=new AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK).setAudioAttributes(attributes).setOnAudioFocusChangeListener(change->{if(ticket==generation&&change<0)finish("blocked");},handler).build();
   if(manager.requestAudioFocus(focus)!=AudioManager.AUDIOFOCUS_REQUEST_GRANTED){finish("blocked");return START_NOT_STICKY;}
   speech=new ArabicSpeech(this,attributes);speech.speak(text,(float)settings.optDouble("volume",1),()->{if(ticket==generation)finish(null);});
  }catch(RuntimeException error){android.util.Log.w("SalatiFajrPreview","Local announcement failed",error);finish("error");}return START_NOT_STICKY;
 }
 private void finish(String status){terminal=true;release();if(status!=null)ArabicSpeech.record(this,status);MainActivity.notifyFajrPreview(false);stopForeground(STOP_FOREGROUND_REMOVE);stopSelf(startId);}
 private void release(){generation++;handler.removeCallbacksAndMessages(null);if(speech!=null){speech.close();speech=null;}if(manager!=null&&focus!=null){manager.abandonAudioFocusRequest(focus);focus=null;}if(wake!=null&&wake.isHeld())wake.release();wake=null;}
 @Override public void onDestroy(){release();if(!terminal)ArabicSpeech.recordCancellation(this);MainActivity.notifyFajrPreview(false);stopForeground(STOP_FOREGROUND_REMOVE);super.onDestroy();}
}
