package com.salati.prayer;
import android.content.*;
/** Scheduled independently of the next prayer alarm, so a reminder cannot consume an adhan. */
public final class ApproachReceiver extends BroadcastReceiver {
 private static String lastRequested="";
 @Override public void onReceive(Context c,Intent i){
  long time=i.getLongExtra("time",0),prayerTime=i.getLongExtra("prayerTime",0),now=System.currentTimeMillis();String prayer=i.getStringExtra("prayer");
  boolean valid=PrayerSchedule.approachValid(c,time,prayerTime,prayer);PrayerSchedule.scheduleNextApproach(c,Math.max(time,now));
  if(!ApproachPolicy.mayPlay(valid,PrayerSchedule.exactAlarmsAllowed(c),time,prayerTime,now))return;
  String key=prayer+":"+time;SharedPreferences prefs=c.getSharedPreferences(PrayerSchedule.PREF,0);if(key.equals(lastRequested)||key.equals(prefs.getString("lastApproach","")))return;
  try{c.startForegroundService(new Intent(c,ApproachService.class).putExtra("prayer",prayer).putExtra("time",time).putExtra("prayerTime",prayerTime));lastRequested=key;prefs.edit().putString("lastApproach",key).commit();}catch(RuntimeException error){android.util.Log.w("SalatiApproach","Reminder service could not start",error);}
 }
}
