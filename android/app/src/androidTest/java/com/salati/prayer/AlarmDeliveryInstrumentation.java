package com.salati.prayer;

import android.app.Instrumentation;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import org.json.JSONArray;
import org.json.JSONObject;

/** Test-only runner: installs an actual near-future alarm, then exits so Android
 * must wake a cold background process. No test hook enters the production APK. */
public final class AlarmDeliveryInstrumentation extends Instrumentation {
 private Bundle arguments;
 @Override public void onCreate(Bundle args){super.onCreate(args);arguments=args;start();}
 @Override public void onStart(){
  Bundle result=new Bundle();
  try{
   Context c=getTargetContext();
   String prayer=arguments.getString("prayer","fajr");
   if(!prayer.matches("fajr|dhuhr|asr|maghrib|isha"))throw new AssertionError("Invalid test prayer");
   if(!PrayerSchedule.exactAlarmsAllowed(c))throw new AssertionError("Exact alarm test requires granted OS permission");
   c.stopService(new Intent(c,AdhanService.class));
   c.getSharedPreferences(PrayerSchedule.PREF,0).edit().clear().commit();
   long at=System.currentTimeMillis()+12000;
   JSONObject data=new JSONObject().put("enabled",true).put("voice",arguments.getString("voice","nufais")).put("volume",.5).put("dua",false).put("silentMode",true)
    .put("events",new JSONArray().put(new JSONObject().put("prayer",prayer).put("time",at)).put(new JSONObject().put("prayer","isha").put("time",at+600000)))
    .put("days",new JSONArray());
   PrayerSchedule.sync(c,data.toString());
   JSONObject state=new JSONObject(PrayerSchedule.status(c));
   if(state.getLong("nextAlarmTime")!=at||!state.getString("nextAlarmPrayer").equals(prayer)||!state.getString("nextAlarmMode").equals("exact"))throw new AssertionError("Actual AlarmManager schedule not confirmed: "+state);
   result.putString("scheduledPrayer",prayer);result.putLong("scheduledTime",at);
   result.putString("stream","Prepared real cold-process screen-off alarm; shell verifies delivery and actual AudioTrack after runner exits");
   finish(-1,result);
  }catch(Throwable error){result.putString("stream",android.util.Log.getStackTraceString(error));finish(0,result);}
 }
}
