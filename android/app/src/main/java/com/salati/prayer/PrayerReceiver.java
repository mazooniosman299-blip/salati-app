package com.salati.prayer;
import android.content.*;
/** Delivered from Android's alarm clock; playback uses only the saved local schedule/assets. */
public final class PrayerReceiver extends BroadcastReceiver {
 public void onReceive(Context c,Intent i){
  long time=i.getLongExtra("time",0),now=System.currentTimeMillis();String prayer=i.getStringExtra("prayer");
  SharedPreferences saved=c.getSharedPreferences(PrayerSchedule.PREF,0);
  // Save the delivered alarm's mode BEFORE scheduling the next event.
  boolean inexact="inexact".equals(saved.getString("nextAlarmMode",""));
  boolean valid=PrayerSchedule.valid(c,time,prayer)&&!PrayerSchedule.laterEventAlreadyDue(c,time,now);
  boolean playable=AlarmDeliveryPolicy.mayPlay(valid,inexact,time,now);
  // UPDATE_CURRENT can change an older wake-up's extras before its OS time
  // is replaced. Rejected early callbacks must rearm the future prayer,
  // rather than advancing past a prayer that has not actually been played.
  PrayerSchedule.scheduleNext(c,playable?Math.max(time,now):now);
  if(!playable){
   PrayerSchedule.recordDelivery(c,valid?"late_alarm_skipped":"obsolete_alarm",null);PrayerWidget.updateAll(c);return;
  }
  String key=prayer+time;
  if(key.equals(saved.getString("last","")))return;
  try{
   c.startForegroundService(new Intent(c,AdhanService.class).putExtra("prayer",prayer));
   saved.edit().putString("last",key).commit();PrayerSchedule.recordDelivery(c,"service_requested",null);
  }catch(RuntimeException error){PrayerSchedule.recordDelivery(c,"service_start_failed",error);}
  PrayerWidget.updateAll(c);
 }
}
