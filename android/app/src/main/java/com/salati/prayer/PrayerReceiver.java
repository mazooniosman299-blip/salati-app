package com.salati.prayer;
import android.content.*;
/** Delivered from Android's alarm clock; playback uses only the saved local schedule/assets. */
public final class PrayerReceiver extends BroadcastReceiver {
 public void onReceive(Context c,Intent i){
  long time=i.getLongExtra("time",0),now=System.currentTimeMillis();String prayer=i.getStringExtra("prayer");
  boolean valid=PrayerSchedule.valid(c,time,prayer);
  PrayerSchedule.scheduleNext(c,Math.max(time,now));
  if(!AlarmDeliveryPolicy.mayPlay(valid,PrayerSchedule.exactAlarmsAllowed(c),time,now)){
   PrayerSchedule.recordDelivery(c,valid?"delivery_outside_window":"obsolete_alarm",null);PrayerWidget.updateAll(c);return;
  }
  String key=prayer+time;SharedPreferences saved=c.getSharedPreferences(PrayerSchedule.PREF,0);
  if(key.equals(saved.getString("last","")))return;
  try{
   c.startForegroundService(new Intent(c,AdhanService.class).putExtra("prayer",prayer));
   saved.edit().putString("last",key).commit();PrayerSchedule.recordDelivery(c,"service_requested",null);
  }catch(RuntimeException error){PrayerSchedule.recordDelivery(c,"service_start_failed",error);}
  PrayerWidget.updateAll(c);
 }
}
