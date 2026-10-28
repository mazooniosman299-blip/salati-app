package com.salati.prayer;
import android.app.*;import android.content.*;import android.media.*;import android.os.*;import org.json.JSONObject;
/** Short spoken reminder. Existing audio wins, and the real adhan always preempts this service. */
public final class ApproachService extends Service {
 private AudioManager manager;private AudioFocusRequest focus;private PowerManager.WakeLock wake;private ArabicSpeech speech;private final Handler handler=new Handler(Looper.getMainLooper());private int startId;private boolean previewMode;private long generation;
 public IBinder onBind(Intent i){return null;}
 public int onStartCommand(Intent intent,int flags,int id){
  startId=id;release();long ticket=generation;if(intent==null){finish();return START_NOT_STICKY;}
  boolean preview=intent.getBooleanExtra("preview",false);previewMode=preview;long at=intent.getLongExtra("time",0),prayerTime=intent.getLongExtra("prayerTime",0);String prayer=intent.getStringExtra("prayer");
  if(!preview&&!ApproachPolicy.mayPlay(PrayerSchedule.approachValid(this,at,prayerTime,prayer),PrayerSchedule.exactAlarmsAllowed(this),at,prayerTime,System.currentTimeMillis())){finish();return START_NOT_STICKY;}
  manager=getSystemService(AudioManager.class);QuranService quran=QuranService.active;
  boolean busy=manager==null||AdhanService.active.get()!=null||quran!=null&&quran.wantPlay||manager.isMusicActive();
  try{
   NotificationChannel channel=new NotificationChannel("salati_approach","اقتراب الصلاة",NotificationManager.IMPORTANCE_DEFAULT);channel.setSound(null,null);getSystemService(NotificationManager.class).createNotificationChannel(channel);
   String text=preview&&"fajr".equals(intent.getStringExtra("kind"))?"الصلاة خير من النوم":"اقتربت صلاة "+AdhanService.prayerName(prayer);PendingIntent open=PendingIntent.getActivity(this,76,new Intent(this,MainActivity.class),PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
   startForeground(76,new Notification.Builder(this,"salati_approach").setSmallIcon(R.drawable.ic_notification).setContentTitle(text).setContentText("استعد للصلاة").setContentIntent(open).setOnlyAlertOnce(true).setCategory(Notification.CATEGORY_REMINDER).setAutoCancel(true).setTimeoutAfter(60000).build());
   if(busy){finish();return START_NOT_STICKY;}MainActivity.notifyApproach(true);wake=getSystemService(PowerManager.class).newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,"salati:approach");wake.acquire(12000);handler.postDelayed(()->{if(ticket==generation)finish();},11000);
   AudioAttributes attributes=new AudioAttributes.Builder().setUsage(preview?AudioAttributes.USAGE_MEDIA:AudioAttributes.USAGE_NOTIFICATION_EVENT).setContentType(AudioAttributes.CONTENT_TYPE_SPEECH).build();
   focus=new AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK).setAudioAttributes(attributes).setOnAudioFocusChangeListener(change->{if(ticket==generation&&change<0)finish();},handler).build();
   if(manager.requestAudioFocus(focus)!=AudioManager.AUDIOFOCUS_REQUEST_GRANTED){finish();return START_NOT_STICKY;}
   JSONObject settings=PrayerSchedule.config(this);speech=new ArabicSpeech(this,attributes);speech.speak(text,(float)settings.optDouble("volume",1),()->{if(ticket==generation)finish();});
  }catch(RuntimeException error){finish();}return START_NOT_STICKY;
 }
 private int notificationMode(){JSONObject config=PrayerSchedule.config(this);return previewMode||!config.optBoolean("enabled")||!config.optBoolean("approachEnabled",true)?STOP_FOREGROUND_REMOVE:STOP_FOREGROUND_DETACH;}
 private void finish(){release();MainActivity.notifyApproach(false);stopForeground(notificationMode());stopSelf(startId);}
 private void release(){generation++;handler.removeCallbacksAndMessages(null);if(speech!=null){speech.close();speech=null;}if(manager!=null&&focus!=null){manager.abandonAudioFocusRequest(focus);focus=null;}if(wake!=null&&wake.isHeld())wake.release();wake=null;}
 @Override public void onDestroy(){release();MainActivity.notifyApproach(false);stopForeground(notificationMode());super.onDestroy();}
}
