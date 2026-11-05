"""Exercise actual sync/scheduler methods against deterministic OS/clock boundaries.

Catches unconditional cancellation of a still-deliverable pending alarm during
WebView sync. The existing scheduler boundary fixture is reused, not its logic.
Actual Android AlarmManager/service delivery is tested separately on emulator.
"""
from pathlib import Path
import os, runpy, subprocess, tempfile

root=Path(__file__).resolve().parents[1]
fixture=runpy.run_path(str(root/'tests/legacy-reminder-migration.py'))
code=fixture['java_source'].split(' public static void main(String[] args){')[0]
code=code.replace('LegacyReminderMigrationTest','PendingAlarmResyncTest')
code=code.replace(' final Map<String,Object> data=new HashMap<>();',''' final Map<String,Object> data=new HashMap<>();
  static final Map<String,JSONObject> encoded=new HashMap<>();
  JSONObject(){}JSONObject(String json){data.putAll(encoded.get(json).data);}
  public String toString(){String key="json"+encoded.size();encoded.put(key,this);return key;}''')
code=code.replace('int length(){return values.size();}', 'JSONObject getJSONObject(int n){return values.get(n);}int length(){return values.size();}')
code=code.replace('final class Editor {','''final Map<String,Object> durable=new HashMap<>();final Context owner;SharedPreferences(Context owner){this.owner=owner;}
  long getLong(String k,long fallback){Object v=values.get(k);return v instanceof Number?((Number)v).longValue():fallback;}
  String getString(String k,String fallback){Object v=values.get(k);return v==null?fallback:v.toString();}
  final class Editor {''')
code=code.replace('boolean commit(){return true;}', 'boolean commit(){durable.clear();durable.putAll(values);return true;}')
code=code.replace('values.put(key,value);return this;}void apply()', 'values.put(key,value);if(key.equals("config"))owner.config=new JSONObject(value);return this;}void apply()')
code=code.replace('new SharedPreferences();','new SharedPreferences(this);')
code=code.replace('<T> T getSystemService','boolean stopService(Intent intent){return false;}<T> T getSystemService')
code=code.replace('static final class PrayerReceiver {}','static final class FajrPreviewService {}static final class AdhanService {}static final class PrayerReceiver {}')
# Model the OS replacement boundary and FLAG_UPDATE_CURRENT semantics rather
# than copying scheduler decisions. A fatal Error represents process death.
def change(old,new):
 global code
 assert old in code,('Boundary fixture changed',old)
 code=code.replace(old,new)
change('boolean allowed=true;', 'int crashPhase;boolean allowed=true;')
change('static void recordDelivery(Context c,String code,Throwable error){throw new AssertionError(code,error);}', 'static void recordDelivery(Context c,String code,Throwable error){if(error!=null)throw new AssertionError(code,error);c.prefs.values.put("deliveryStatus",code);}')
change('alarms.put(pending.request,info);operations.put(pending.request,pending);', 'if(crashPhase==1)throw new ProcessDeath();alarms.put(pending.request,info);operations.put(pending.request,pending);if(crashPhase==2)throw new ProcessDeath();')
change('inexactCalls++;alarms.put(pending.request,new AlarmClockInfo(at,null));operations.put(pending.request,pending);', 'if(crashPhase==1)throw new ProcessDeath();inexactCalls++;alarms.put(pending.request,new AlarmClockInfo(at,null));operations.put(pending.request,pending);if(crashPhase==2)throw new ProcessDeath();')
change('return new PendingIntent(request,intent,false,flags);', 'PendingIntent existing=c.alarm.operations.get(request);if(existing!=null){existing.intent.extras.clear();existing.intent.extras.putAll(intent.extras);return existing;}return new PendingIntent(request,intent,false,flags);')
change('  Intent(Context c,Class<?> target)', '  long getLongExtra(String key,long fallback){Object v=extras.get(key);return v instanceof Number?((Number)v).longValue():fallback;}String getStringExtra(String key){return (String)extras.get(key);}'+'\n  Intent(Context c,Class<?> target)')
change('boolean stopService(Intent intent)', 'int serviceStarts;void startForegroundService(Intent intent){serviceStarts++;}boolean stopService(Intent intent)')
receiver=(root/'android/app/src/main/java/com/salati/prayer/PrayerReceiver.java').read_text()
start=receiver.index(' public void onReceive(');opening=receiver.index('{',start);end=opening+1;depth=1
while depth:
 depth+=(receiver[end]=='{')-(receiver[end]=='}');end+=1
change('static final class PrayerReceiver {}','static final class ProcessDeath extends Error {}static final class PrayerWidget {static void updateAll(Context c){}}static final class PrayerReceiver {'+receiver[start:end]+'}')
extra='\n'.join(fixture['method'](n) for n in ['sync','pendingDueOnResume','laterEventAlreadyDue'])
code=code.replace('\n }\n static void check', '\n'+extra+'\n }\n static void check')
code=code.replace(' static final class JSONObject {',''' static final class System {
  static long now=1800000000000L;static long currentTimeMillis(){return now;}
  static final java.io.PrintStream out=java.lang.System.out;
 }
 static final class JSONObject {''')
code+='''
 static Context pending(String prayer,long delay,boolean inexact){
  Context c=new Context();long at=System.now-delay;
  c.config=new JSONObject().put("enabled",true).put("events",new JSONArray().add(event(at,prayer)).add(event(System.now+3600000,"isha"))).put("days",new JSONArray());
  c.prefs.values.put("nextAlarmTime",at);c.prefs.values.put("nextAlarmPrayer",prayer);c.prefs.values.put("nextAlarmMode",inexact?"inexact":"exact");
  c.alarm.allowed=!inexact;
  PendingIntent pi=PrayerSchedule.pending(c,at,prayer);
  if(inexact)c.alarm.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,at,pi);else c.alarm.setAlarmClock(new AlarmManager.AlarmClockInfo(at,null),pi);
  c.prefs.durable.putAll(c.prefs.values);
  return c;
 }
 public static void main(String[] args)throws Exception{
  long originalNow=System.now;Context cold=new Context();
  cold.config=new JSONObject().put("enabled",true).put("events",new JSONArray().add(event(originalNow+1000,"fajr")).add(event(originalNow+3600000,"dhuhr"))).put("days",new JSONArray());
  PrayerSchedule.sync(cold,cold.config.toString());
  cold.prefs.values.clear();cold.prefs.values.putAll(cold.prefs.durable);System.now+=21000;
  check(PrayerSchedule.pendingDueOnResume(cold,System.now),"Confirmed alarm metadata must survive immediate process death before asynchronous disk work");System.now=originalNow;
  for(boolean inexact:new boolean[]{false,true}){
   Context early=pending("fajr",-120000,inexact);long future=(Long)early.prefs.values.get("nextAlarmTime");
   Intent intent=new Intent(early,PrayerReceiver.class).putExtra("time",future).putExtra("prayer","fajr");
   new PrayerReceiver().onReceive(early,intent);
   same(at(early,5101),future,"Rejected early callback must rearm, never skip the actual upcoming prayer");
   check(early.serviceStarts==0,"Early callback must not start audio");
   for(int phase:new int[]{1,2}){
    Context sameEvent=pending("fajr",-60000,inexact);long due=(Long)sameEvent.prefs.values.get("nextAlarmTime");sameEvent.alarm.crashPhase=phase;
    try{PrayerSchedule.scheduleNext(sameEvent,System.now);throw new AssertionError("Fault injection missing");}catch(ProcessDeath expected){}
    same(at(sameEvent,5101),due,"Same-event resync lost OSalarm during process death; phase="+phase);
   }
   Context changed=pending("fajr",-60000,inexact);long oldDue=(Long)changed.prefs.values.get("nextAlarmTime"),futureDue=oldDue+60000;
   changed.config.put("events",new JSONArray().add(event(futureDue,"fajr")).add(event(System.now+3600000,"isha")));changed.alarm.crashPhase=1;
   try{PrayerSchedule.scheduleNext(changed,System.now);throw new AssertionError("Fault injection missing");}catch(ProcessDeath expected){}
   same(at(changed,5101),oldDue,"Interrupted changed-time replacement must retain prior OSwake-up");
   PendingIntent oldWake=changed.alarm.operations.get(5101);check(((Long)oldWake.intent.extras.get("time"))==futureDue,"Model real UPDATE_CURRENT extras alias");
   changed.alarm.crashPhase=0;System.now=oldDue;new PrayerReceiver().onReceive(changed,oldWake.intent);System.now=originalNow;
   same(at(changed,5101),futureDue,"Old wake with updated future extras must rearm the new prayer");check(changed.serviceStarts==0,"Interrupted replacement must not play the new prayer early");
  }
  for(boolean previousInexact:new boolean[]{false,true})for(int phase:new int[]{1,2}){
   Context transition=pending("fajr",-60000,previousInexact);long due=(Long)transition.prefs.values.get("nextAlarmTime");
   transition.alarm.allowed=previousInexact;transition.alarm.crashPhase=phase;
   try{PrayerSchedule.scheduleNext(transition,System.now);throw new AssertionError("Cross-mode fault injection missing");}catch(ProcessDeath expected){}
   transition.prefs.values.clear();transition.prefs.values.putAll(transition.prefs.durable);transition.alarm.crashPhase=0;System.now=due+600000;
   new PrayerReceiver().onReceive(transition,new Intent(transition,PrayerReceiver.class).putExtra("time",due).putExtra("prayer","fajr"));System.now=originalNow;
   check(transition.serviceStarts==0,"Interrupted cross-mode replacement must never inherit ambiguous30min grace; oldInexact="+previousInexact+" phase="+phase);
  }
  Context confirmedInexact=pending("fajr",-60000,true);long dueInexact=(Long)confirmedInexact.prefs.values.get("nextAlarmTime");PrayerSchedule.scheduleNext(confirmedInexact,System.now);
  confirmedInexact.prefs.values.clear();confirmedInexact.prefs.values.putAll(confirmedInexact.prefs.durable);System.now=dueInexact+600000;
  new PrayerReceiver().onReceive(confirmedInexact,new Intent(confirmedInexact,PrayerReceiver.class).putExtra("time",dueInexact).putExtra("prayer","fajr"));System.now=originalNow;
  check(confirmedInexact.serviceStarts==1,"Confirmed inexact alarm retains existing30min delivery grace");
  for(String prayer:new String[]{"fajr","dhuhr","asr","maghrib","isha"}){
   for(boolean inexact:new boolean[]{false,true}){
    Context c=pending(prayer,inexact?600000:20000,inexact);long due=(Long)c.prefs.values.get("nextAlarmTime");
    PrayerSchedule.sync(c,c.config.toString());
    same(at(c,5101),due,prayer+": sync cancels the undelivered due alarm");
    check(PrayerSchedule.valid(c,due,prayer),"Receiver must still validate the synchronized event");
    check(AlarmDeliveryPolicy.mayPlay(true,inexact,due,System.now),"Pending event remains inside existing grace");
    c.prefs.values.put("last",prayer+due);PrayerSchedule.sync(c,c.config.toString());
    same(at(c,5101),System.now+3600000,"Delivered alarm must advance, not repeat");
   }
   Context disabled=pending(prayer,20000,false);disabled.config.put("enabled",false);PrayerSchedule.sync(disabled,disabled.config.toString());same(at(disabled,5101),0,"Global disable cancels pending alarm");
   Context excluded=pending(prayer,20000,false);excluded.config.put("events",new JSONArray().add(event(System.now+3600000,"isha")));PrayerSchedule.sync(excluded,excluded.config.toString());same(at(excluded,5101),System.now+3600000,"Disabled prayer or changed timestamp is not preserved");
  }
  for(boolean inexact:new boolean[]{false,true}){
   Context expired=pending("fajr",inexact?1800001:300001,inexact);PrayerSchedule.sync(expired,expired.config.toString());same(at(expired,5101),System.now+3600000,"Expired alarm must not be revived");
  }
  Context revoked=pending("fajr",20000,false);revoked.alarm.allowed=false;PrayerSchedule.sync(revoked,revoked.config.toString());same(at(revoked,5101),System.now+3600000,"Revoked exact alarm is not falsely preserved");
  System.out.println("PASS actual scheduler/receiver: process-death replacement and early callbacks, all5 prayers, exact/inexact, delivered/disabled/changed/expired/revoked safety");
 }
}
'''
with tempfile.TemporaryDirectory(prefix='salati-pending-sync-') as d:
 target=Path(d);test=target/'PendingAlarmResyncTest.java';test.write_text(code)
 log=target/'android/util/Log.java';log.parent.mkdir(parents=True);log.write_text('package android.util;public class Log {public static int w(String t,String s,Throwable e){return 0;}}')
 jdk=Path(os.environ['JAVA_HOME'])/'bin'
 subprocess.run([jdk/'javac','-d',target,test,log,root/'android/app/src/main/java/com/salati/prayer/AlarmDeliveryPolicy.java'],check=True)
 subprocess.run([jdk/'java','-cp',target,'com.salati.prayer.PendingAlarmResyncTest'],check=True)
