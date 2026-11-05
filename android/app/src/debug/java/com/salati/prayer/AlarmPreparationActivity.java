package com.salati.prayer;

import android.app.Activity;
import android.os.Bundle;
import org.json.JSONArray;
import org.json.JSONObject;

/** Disposable-emulator fixture, compiled into DEBUG ONLY. Unlike finishing an
 * instrumentation session, normal Activity finish does not cancel app alarms. */
public final class AlarmPreparationActivity extends Activity {
 @Override protected void onCreate(Bundle saved){
  super.onCreate(saved);
  try{
   String prayer=getIntent().getStringExtra("prayer"),voice=getIntent().getStringExtra("voice");
   if(prayer==null||!prayer.matches("fajr|dhuhr|asr|maghrib|isha")||voice==null||!voice.matches("nufais|qatami|makkah|aqsa"))throw new IllegalArgumentException("Invalid test input");
   if(!PrayerSchedule.exactAlarmsAllowed(this))throw new IllegalStateException("Exact alarm test permission not granted");
   long at=System.currentTimeMillis()+12000;
   JSONObject data=new JSONObject().put("enabled",true).put("voice",voice).put("volume",.5).put("dua",false).put("silentMode",true)
    .put("events",new JSONArray().put(new JSONObject().put("prayer",prayer).put("time",at)).put(new JSONObject().put("prayer","isha").put("time",at+600000)))
    .put("days",new JSONArray());
   PrayerSchedule.sync(this,data.toString());
   // No test-only write or flush: the actual product must persist its metadata.
   JSONObject status=new JSONObject(PrayerSchedule.status(this));
   if(status.getLong("nextAlarmTime")!=at||!status.getString("nextAlarmPrayer").equals(prayer))throw new IllegalStateException("Alarm preparation did not persist");
   android.util.Log.i("SalatiAlarmTest","Prepared "+prayer+" at "+at);
  }catch(Exception error){android.util.Log.e("SalatiAlarmTest","Preparation failed",error);}
  finally{finishAndRemoveTask();}
 }
}
