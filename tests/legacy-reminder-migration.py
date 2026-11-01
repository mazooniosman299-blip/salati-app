"""Run production scheduler methods with deterministic alarm/JSON boundaries on the host JDK."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'android/app/src/main/java/com/salati/prayer/PrayerSchedule.java').read_text()

def method(name):
    """Extract complete production methods, without reimplementing their decisions."""
    match = re.search(r'\b(?:void|boolean|PendingIntent)\s+' + re.escape(name) + r'\(', source)
    if not match:
        raise AssertionError('Production method missing: ' + name)
    start = source.rfind('\n', 0, match.start()) + 1
    opening = source.index('{', match.end())
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]

methods = '\n'.join(method(name) for name in ['pending', 'scheduleNext', 'cancelLegacyApproach', 'valid'])
java_source = '''package com.salati.prayer;
import java.util.*;
public final class LegacyReminderMigrationTest {
 static final class JSONObject {
  final Map<String,Object> data=new HashMap<>();
  JSONObject put(String key,Object value){data.put(key,value);return this;}Object remove(String key){return data.remove(key);}
  JSONArray optJSONArray(String key){return (JSONArray)data.get(key);}
  boolean optBoolean(String key){return optBoolean(key,false);}boolean optBoolean(String key,boolean fallback){Object value=data.get(key);return value instanceof Boolean?(Boolean)value:fallback;}
  int optInt(String key,int fallback){Object value=data.get(key);return value instanceof Number?((Number)value).intValue():fallback;}
  long optLong(String key){Object value=data.get(key);return value instanceof Number?((Number)value).longValue():0;}
  String optString(String key){Object value=data.get(key);return value==null?"":value.toString();}
 }
 static final class JSONArray {
  final List<JSONObject> values=new ArrayList<>();JSONArray add(JSONObject value){values.add(value);return this;}
  int length(){return values.size();}JSONObject optJSONObject(int index){return values.get(index);}
 }
 static final class SharedPreferences {
  final Map<String,Object> values=new HashMap<>();Editor edit(){return new Editor();}
  final class Editor {Editor remove(String key){values.remove(key);return this;}Editor putLong(String key,long value){values.put(key,value);return this;}Editor putString(String key,String value){values.put(key,value);return this;}void apply(){}}
 }
 static final class Context {
  JSONObject config;PendingIntent legacy;final AlarmManager alarm=new AlarmManager();final NotificationManager notifications=new NotificationManager();final SharedPreferences prefs=new SharedPreferences();
  <T> T getSystemService(Class<T> type){return type.cast(type==AlarmManager.class?alarm:notifications);}SharedPreferences getSharedPreferences(String name,int mode){return prefs;}
 }
 static final class Intent {
  String action;final Map<String,Object> extras=new HashMap<>();final Class<?> target;
  Intent(Context c,Class<?> target){this.target=target;}Intent setAction(String action){this.action=action;return this;}
  Intent putExtra(String key,long value){extras.put(key,value);return this;}Intent putExtra(String key,String value){extras.put(key,value);return this;}
 }
 static final class PendingIntent {
  static final int FLAG_UPDATE_CURRENT=1,FLAG_IMMUTABLE=2,FLAG_NO_CREATE=4;final int request;final Intent intent;final boolean activity;boolean canceled;void cancel(){canceled=true;}
  PendingIntent(int request,Intent intent,boolean activity,int flags){check((flags&FLAG_IMMUTABLE)!=0,"PendingIntent must remain immutable");this.request=request;this.intent=intent;this.activity=activity;}
  static PendingIntent getBroadcast(Context c,int request,Intent intent,int flags){if((flags&FLAG_NO_CREATE)!=0)return c.legacy==null||c.legacy.canceled?null:c.legacy;return new PendingIntent(request,intent,false,flags);}
  static PendingIntent getActivity(Context c,int request,Intent intent,int flags){return new PendingIntent(request,intent,true,flags);}
 }
 static final class AlarmManager {
  boolean allowed=true;final Map<Integer,AlarmClockInfo> alarms=new HashMap<>();final Map<Integer,PendingIntent> operations=new HashMap<>();
  static final class AlarmClockInfo {final long at;final PendingIntent open;AlarmClockInfo(long at,PendingIntent open){this.at=at;this.open=open;}}
  void cancel(PendingIntent pending){alarms.remove(pending.request);operations.remove(pending.request);}
  static final int RTC_WAKEUP=0;
  int inexactCalls;
  void setAlarmClock(AlarmClockInfo info,PendingIntent pending){alarms.put(pending.request,info);operations.put(pending.request,pending);}
  void setAndAllowWhileIdle(int type,long at,PendingIntent pending){check(type==RTC_WAKEUP,"must wake from RTC time");inexactCalls++;alarms.put(pending.request,new AlarmClockInfo(at,null));operations.put(pending.request,pending);}
 }
 static final class NotificationManager {int canceled;String deleted;void cancel(int id){canceled=id;}void deleteNotificationChannel(String name){deleted=name;}}
 static final class PrayerReceiver {}static final class ApproachReceiver {}static final class MainActivity {}
 static final class PrayerSchedule {
  static final String PREF="salati_background";static final int REQUEST=5101;
  static JSONObject config(Context c){return c.config;}static boolean exactAlarmsAllowed(Context c){return c.alarm.allowed;}
  static void recordDelivery(Context c,String code,Throwable error){throw new AssertionError(code,error);}
''' + methods + '''
 }
 static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
 static JSONObject event(long time,String prayer){return new JSONObject().put("time",time).put("prayer",prayer);}
 static long at(Context c,int request){AlarmManager.AlarmClockInfo alarm=c.alarm.alarms.get(request);return alarm==null?0:alarm.at;}
 static void same(long actual,long expected,String message){check(actual==expected,message+": "+actual+" != "+expected);}
 public static void main(String[] args){
  long now=System.currentTimeMillis(),first=now+40*60000,second=now+70*60000;Context c=new Context();
  JSONArray events=new JSONArray().add(event(second,"asr")).add(event(first,"dhuhr"));
  c.config=new JSONObject().put("enabled",true).put("events",events);
  c.config.put("approachEnabled",true).put("approachMinutes",15).put("fajrAnnouncement",false).put("volume",.35);
  c.legacy=new PendingIntent(5103,new Intent(c,ApproachReceiver.class).setAction("com.salati.prayer.APPROACH"),false,PendingIntent.FLAG_IMMUTABLE);
  c.alarm.setAlarmClock(new AlarmManager.AlarmClockInfo(first-300000,null),c.legacy);
  c.prefs.values.put("nextApproachTime",first-300000);c.prefs.values.put("lastApproach","old");
  PrayerSchedule.scheduleNext(c,now);
  check(c.legacy.canceled,"Previously registered request5103 must be canceled");
  same(at(c,5103),0,"Removed approach alarm must not be rescheduled");same(at(c,5101),first,"Actual next prayer unchanged");
  check(!c.config.data.containsKey("approachEnabled")&&!c.config.data.containsKey("approachMinutes"),"Drop obsolete saved keys");
  check(!c.prefs.values.containsKey("nextApproachTime")&&!c.prefs.values.containsKey("lastApproach"),"Clear legacy delivery state");
  check(!c.config.optBoolean("fajrAnnouncement")&&c.config.data.get("volume").equals(.35),"Preserve Fajr opt-out and volume");
  check(c.notifications.canceled==76&&"salati_approach".equals(c.notifications.deleted),"Remove only obsolete notification/channel");
  PrayerSchedule.scheduleNext(c,now);check(c.alarm.operations.size()==1,"Idempotent migration never creates a new approach alarm");
  c.alarm.allowed=false;PrayerSchedule.scheduleNext(c,now);
  same(at(c,5101),first,"Revoked exact permission must schedule an inexact fallback");
  check(c.alarm.inexactCalls==1,"Fallback was not used");
  check("inexact".equals(c.prefs.values.get("nextAlarmMode")),"Fallback status must be visible");
  c.alarm.allowed=true;PrayerSchedule.scheduleNext(c,now);
  check("exact".equals(c.prefs.values.get("nextAlarmMode")),"Restored permission returns to accurate alarms");
  c.alarm.allowed=true;c.config.put("enabled",false);PrayerSchedule.scheduleNext(c,now);same(at(c,5101),0,"Disabled user setting stays disabled");
  System.out.println("PASS: production upgrade cancels old5103 alarm and metadata, preserves real adhan/settings, never recreates approach reminders.");
 }
}
'''

with tempfile.TemporaryDirectory(prefix='salati-legacy-reminder-') as directory:
    target = Path(directory)
    test = target / 'LegacyReminderMigrationTest.java'
    test.write_text(java_source)
    log = target / 'android/util/Log.java'
    log.parent.mkdir(parents=True)
    log.write_text('package android.util; public class Log {public static int w(String tag,String text,Throwable error){throw new AssertionError(text,error);}}')
    jdk = Path(os.environ['JAVA_HOME']) / 'bin' if os.environ.get('JAVA_HOME') else None
    javac = str(jdk / 'javac') if jdk else shutil.which('javac')
    java = str(jdk / 'java') if jdk else shutil.which('java')
    if not javac or not java:
        raise SystemExit('A host JDK is required; set JAVA_HOME to run this regression test.')
    subprocess.run([javac, '-d', str(target), str(test), str(log)], check=True)
    subprocess.run([java, '-cp', str(target), 'com.salati.prayer.LegacyReminderMigrationTest'], check=True)
