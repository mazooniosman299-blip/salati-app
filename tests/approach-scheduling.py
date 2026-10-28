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

methods = '\n'.join(method(name) for name in ['pending', 'scheduleNext', 'approachPending', 'scheduleNextApproach', 'approachValid', 'valid'])
java_source = '''package com.salati.prayer;
import java.util.*;
public final class ApproachSchedulingTest {
 static final class JSONObject {
  final Map<String,Object> data=new HashMap<>();
  JSONObject put(String key,Object value){data.put(key,value);return this;}
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
  JSONObject config;final AlarmManager alarm=new AlarmManager();final SharedPreferences prefs=new SharedPreferences();
  <T> T getSystemService(Class<T> type){return type.cast(alarm);}SharedPreferences getSharedPreferences(String name,int mode){return prefs;}
 }
 static final class Intent {
  String action;final Map<String,Object> extras=new HashMap<>();final Class<?> target;
  Intent(Context c,Class<?> target){this.target=target;}Intent setAction(String action){this.action=action;return this;}
  Intent putExtra(String key,long value){extras.put(key,value);return this;}Intent putExtra(String key,String value){extras.put(key,value);return this;}
 }
 static final class PendingIntent {
  static final int FLAG_UPDATE_CURRENT=1,FLAG_IMMUTABLE=2;final int request;final Intent intent;final boolean activity;
  PendingIntent(int request,Intent intent,boolean activity,int flags){check((flags&FLAG_IMMUTABLE)!=0,"PendingIntent must remain immutable");this.request=request;this.intent=intent;this.activity=activity;}
  static PendingIntent getBroadcast(Context c,int request,Intent intent,int flags){return new PendingIntent(request,intent,false,flags);}
  static PendingIntent getActivity(Context c,int request,Intent intent,int flags){return new PendingIntent(request,intent,true,flags);}
 }
 static final class AlarmManager {
  boolean allowed=true;final Map<Integer,AlarmClockInfo> alarms=new HashMap<>();final Map<Integer,PendingIntent> operations=new HashMap<>();
  static final class AlarmClockInfo {final long at;final PendingIntent open;AlarmClockInfo(long at,PendingIntent open){this.at=at;this.open=open;}}
  void cancel(PendingIntent pending){alarms.remove(pending.request);operations.remove(pending.request);}
  void setAlarmClock(AlarmClockInfo info,PendingIntent pending){alarms.put(pending.request,info);operations.put(pending.request,pending);}
 }
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
  PrayerSchedule.scheduleNext(c,now);
  same(at(c,5101),first,"next adhan keeps original prayer time");same(at(c,5103),first-5*60000,"default reminder lead is five minutes");
  check(c.alarm.operations.size()==2,"adhan and reminder must have independent registrations");
  check(c.alarm.operations.get(5101).intent.target==PrayerReceiver.class&&c.alarm.operations.get(5103).intent.target==ApproachReceiver.class,"alarms have separate receivers");
  check(c.alarm.alarms.get(5101).open.request==5102&&c.alarm.alarms.get(5103).open.request==5104,"separate alarm presentation intents");
  same((Long)c.alarm.operations.get(5103).intent.extras.get("prayerTime"),first,"reminder retains actual prayer time");
  check("com.salati.prayer.APPROACH".equals(c.alarm.operations.get(5103).intent.action),"reminder action");
  for(int lead:new int[]{5,10,15}){
   c.config.put("approachMinutes",lead);PrayerSchedule.scheduleNext(c,now);
   same(at(c,5103),first-lead*60000L,"selected lead must schedule independently");same(at(c,5101),first,"lead never shifts actual adhan");
   check(PrayerSchedule.approachValid(c,at(c,5103),first,"dhuhr"),"fresh reminder is valid");
   same((Long)c.prefs.values.get("nextApproachTime"),at(c,5103),"persist next approach");same((Long)c.prefs.values.get("nextAlarmTime"),first,"persist next adhan");
  }
  c.config.put("approachMinutes",7);PrayerSchedule.scheduleNext(c,now);same(at(c,5103),first-5*60000,"unsupported lead falls back to five");
  c.config.put("approachMinutes",5);long reminder=first-5*60000;
  PrayerSchedule.scheduleNextApproach(c,reminder+1);
  same(at(c,5103),second-5*60000,"delivered reminder advances only reminder registration");same(at(c,5101),first,"rescheduling approach cannot consume next adhan");check(PrayerSchedule.valid(c,first,"dhuhr"),"approach does not consume event validity");
  c.config.put("approachEnabled",false);PrayerSchedule.scheduleNext(c,now);same(at(c,5103),0,"disabled reminders cancel reminder alarm");same(at(c,5101),first,"disabling reminders preserves adhan");check(!c.prefs.values.containsKey("nextApproachTime"),"clear disabled reminder metadata");check(!PrayerSchedule.approachValid(c,reminder,first,"dhuhr"),"disabled reminder rejects old intent");
  c.config.put("approachEnabled",true);c.config.put("approachMinutes",10);check(!PrayerSchedule.approachValid(c,reminder,first,"dhuhr"),"lead settings change invalidates old reminder");check(PrayerSchedule.approachValid(c,first-10*60000,first,"dhuhr"),"new lead validates");
  check(!PrayerSchedule.approachValid(c,first-10*60000,first,"fajr"),"mismatched prayer intent invalid");
  c.config.put("events",new JSONArray().add(event(second,"asr")));check(!PrayerSchedule.approachValid(c,first-10*60000,first,"dhuhr"),"changed schedule invalidates removed prayer");
  long soon=now+2*60000;c.config.put("events",new JSONArray().add(event(soon,"fajr")).add(event(first,"dhuhr")));c.config.put("approachMinutes",5);PrayerSchedule.scheduleNext(c,now);
  same(at(c,5101),soon,"upcoming prayer remains eligible after reminder time passed");same(at(c,5103),first-5*60000,"past reminder skips to next future reminder");
  c.config.put("enabled",false);PrayerSchedule.scheduleNext(c,now);same(at(c,5101),0,"disabling adhan clears actual alarm");same(at(c,5103),0,"disabling adhan also clears reminders");check(!c.prefs.values.containsKey("nextAlarmTime")&&!c.prefs.values.containsKey("nextApproachTime"),"disabled scheduling clears next metadata");check(!PrayerSchedule.approachValid(c,first-5*60000,first,"dhuhr"),"disabled adhan invalidates old approach");
  c.config.put("enabled",true);c.alarm.allowed=false;PrayerSchedule.scheduleNext(c,now);check(c.alarm.alarms.isEmpty(),"missing exact-alarm permission leaves both unscheduled");
  System.out.println("PASS: actual scheduler methods preserve independent 5101/5103 alarms, lead defaults/options, disabling, reminder rescheduling, past-window skipping and stale-intent validation.");
 }
}
'''

with tempfile.TemporaryDirectory(prefix='salati-approach-scheduling-') as directory:
    target = Path(directory)
    test = target / 'ApproachSchedulingTest.java'
    test.write_text(java_source)
    policy = target / 'ApproachPolicy.java'
    policy.write_text((ROOT / 'android/app/src/main/java/com/salati/prayer/ApproachPolicy.java').read_text())
    log = target / 'android/util/Log.java'
    log.parent.mkdir(parents=True)
    log.write_text('package android.util; public class Log {public static int w(String tag,String text,Throwable error){throw new AssertionError(text,error);}}')
    jdk = Path(os.environ['JAVA_HOME']) / 'bin' if os.environ.get('JAVA_HOME') else None
    javac = str(jdk / 'javac') if jdk else shutil.which('javac')
    java = str(jdk / 'java') if jdk else shutil.which('java')
    if not javac or not java:
        raise SystemExit('A host JDK is required; set JAVA_HOME to run this regression test.')
    subprocess.run([javac, '-d', str(target), str(test), str(policy), str(log)], check=True)
    subprocess.run([java, '-cp', str(target), 'com.salati.prayer.ApproachSchedulingTest'], check=True)
