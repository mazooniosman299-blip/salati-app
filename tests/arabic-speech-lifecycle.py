"""Compile actual ArabicSpeech with deterministic Android boundaries; no device-fidelity claim."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'android/content/Context.java': '''package android.content;
public class Context {
 public final SharedPreferences preferences=new SharedPreferences();
 public Context getApplicationContext(){return this;}
 public SharedPreferences getSharedPreferences(String name,int mode){return preferences;}
}''',
    'android/content/SharedPreferences.java': '''package android.content;
import java.util.*;
public class SharedPreferences {
 public boolean throwApply;public final Map<String,Object> values=new HashMap<>();
 public Editor edit(){return new Editor();}
 public class Editor {
  public Editor putString(String key,String value){values.put(key,value);return this;}
  public Editor putBoolean(String key,boolean value){values.put(key,value);return this;}
  public void apply(){if(throwApply)throw new IllegalStateException("preferences unavailable");}
 }
}''',
    'android/media/AudioAttributes.java': 'package android.media; public class AudioAttributes {}',
    'android/os/Looper.java': 'package android.os; public class Looper {public static Looper getMainLooper(){return new Looper();}}',
    'android/os/Bundle.java': '''package android.os; import java.util.*;
public class Bundle {public final Map<String,Float> values=new HashMap<>();public void putFloat(String key,float value){values.put(key,value);}}''',
    'android/os/Handler.java': '''package android.os; import java.util.*;
public class Handler {
 public static final Map<Runnable,Long> timers=new LinkedHashMap<>();public static long clock;
 public Handler(Looper looper){}
 public boolean post(Runnable task){task.run();return true;}
 public boolean postDelayed(Runnable task,long delay){timers.put(task,clock+delay);return true;}
 public void removeCallbacks(Runnable task){timers.remove(task);}
 public static void advance(long ms){clock+=ms;for(Map.Entry<Runnable,Long> entry:new ArrayList<>(timers.entrySet()))if(entry.getValue()<=clock){timers.remove(entry.getKey());entry.getKey().run();}}
}''',
    'com/salati/prayer/PcmAudioPlayer.java': '''package com.salati.prayer;
import android.content.Context;import android.media.AudioAttributes;
class PcmAudioPlayer {
 interface Listener {void complete();void error(Exception error);}
 static PcmAudioPlayer latest;static boolean throwPlay,throwConstructor,synchronousComplete;
 Listener listener;String path;AudioAttributes attributes;float volume;int stopped,played;
 PcmAudioPlayer(Context context){if(throwConstructor)throw new IllegalStateException("constructor failed");latest=this;}
 void play(String path,AudioAttributes attributes,float volume,Listener listener){this.path=path;this.attributes=attributes;this.volume=volume;this.listener=listener;played++;if(throwPlay)throw new IllegalStateException("missing asset");if(synchronousComplete)listener.complete();}
 void stop(){stopped++;}
}''',
    'com/salati/prayer/MainActivity.java': '''package com.salati.prayer;
import java.util.*;
class MainActivity {static boolean throwNotify;static final List<String> events=new ArrayList<>();static void notifyAnnouncement(String status){if(throwNotify)throw new IllegalStateException("WebView unavailable");events.add(status);}}''',
    'com/salati/prayer/ArabicSpeechLifecycleTest.java': '''package com.salati.prayer;
import android.content.Context;import android.media.AudioAttributes;import android.os.Handler;
public final class ArabicSpeechLifecycleTest {
 static final String FAJR="الصلاة خير من النوم";
 static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
 static void status(Context context,String expected){check(expected.equals(context.preferences.values.get("status")),"status should be "+expected+": "+context.preferences.values);check(expected.equals(MainActivity.events.get(MainActivity.events.size()-1)),"UI receives status "+expected);}
 public static void main(String[] args){
  Context c=new Context();AudioAttributes attributes=new AudioAttributes();ArabicSpeech speech=new ArabicSpeech(c,attributes);int[] done={0};
  speech.speak(FAJR,.35f,()->done[0]++);PcmAudioPlayer player=PcmAudioPlayer.latest;
  check(player.path.equals("www/audio/reminders/fajr-phrase.mp3"),"Fajr uses bundled phrase");check(player.attributes==attributes&&Math.abs(player.volume-.35f)<.001,"PCM inherits audio route and saved volume");
  status(c,"playing");check(MainActivity.events.get(0).equals("loading"),"loading precedes playing");check(done[0]==0,"adhan waits for clip completion");
  player.listener.complete();player.listener.complete();player.listener.error(new Exception("late"));
  check(done[0]==1&&player.stopped==1,"continuation and cleanup happen exactly once");status(c,"finished");check(Handler.timers.isEmpty(),"completion clears timeout");
  String[] keys={"fajr","dhuhr","asr","maghrib","isha"},names={"الفجر","الظهر","العصر","المغرب","العشاء"};
  for(int i=0;i<keys.length;i++){speech.speak("اقتربت صلاة "+names[i],1f,()->done[0]++);player=PcmAudioPlayer.latest;check(player.path.equals("www/audio/reminders/approach-"+keys[i]+".mp3"),"prayer maps to own recording: "+keys[i]);player.listener.complete();}
  final int[] old={0},replacement={0};speech.speak(FAJR,.5f,()->old[0]++);PcmAudioPlayer stale=PcmAudioPlayer.latest;speech.speak("اقتربت صلاة العصر",.7f,()->replacement[0]++);player=PcmAudioPlayer.latest;
  check(stale.stopped==1,"rapid replacement stops old clip");stale.listener.complete();stale.listener.error(new Exception("late"));check(old[0]==0&&replacement[0]==0,"stale callback cannot finish replacement");status(c,"playing");player.listener.complete();check(replacement[0]==1,"replacement continues exactly once");
  speech.speak(FAJR,1f,()->old[0]++);player=PcmAudioPlayer.latest;speech.close();player.listener.complete();player.listener.error(new Exception("late"));Handler.advance(9000);check(old[0]==0&&Handler.timers.isEmpty(),"explicit close suppresses callbacks and deadlines");
  final int[] timed={0};speech.speak(FAJR,1f,()->timed[0]++);player=PcmAudioPlayer.latest;Handler.advance(7999);check(timed[0]==0,"clip may run up to deadline");Handler.advance(1);check(timed[0]==1&&player.stopped==1,"timeout releases player and continues adhan");status(c,"error");player.listener.complete();check(timed[0]==1,"late completion after timeout is ignored");
  final int[] failed={0};speech.speak(FAJR,2f,()->failed[0]++);player=PcmAudioPlayer.latest;check(player.volume==1f,"volume clamps to one");player.listener.error(new Exception("decoder failure"));check(failed[0]==1,"decode error continues adhan");status(c,"error");
  PcmAudioPlayer.throwPlay=true;speech.speak(FAJR,.5f,()->failed[0]++);player=PcmAudioPlayer.latest;check(failed[0]==2&&player.volume==.5f&&player.stopped==1,"synchronous missing asset releases player and continues");status(c,"error");PcmAudioPlayer.throwPlay=false;
  PcmAudioPlayer.throwConstructor=true;speech.speak(FAJR,1f,()->failed[0]++);check(failed[0]==3,"constructor failure continues adhan");status(c,"error");PcmAudioPlayer.throwConstructor=false;
  for(String invalid:new String[]{null,"","arbitrary text","www/audio/other.mp3"}){PcmAudioPlayer previous=PcmAudioPlayer.latest;int before=failed[0];speech.speak(invalid,1f,()->failed[0]++);check(failed[0]==before+1&&PcmAudioPlayer.latest==previous,"unsupported text fails without arbitrary asset access");status(c,"error");}
  int before=failed[0];speech.speak(FAJR,Float.NaN,()->failed[0]++);check(failed[0]==before+1,"invalid volume fails without stuck playback");status(c,"error");
  for(float volume:new float[]{0f,-1f}){PcmAudioPlayer previous=PcmAudioPlayer.latest;int mutedBefore=failed[0];speech.speak(FAJR,volume,()->failed[0]++);check(failed[0]==mutedBefore+1&&PcmAudioPlayer.latest==previous,"muted setting never creates silent playback");status(c,"muted");check(Handler.timers.isEmpty(),"muted setting leaves no timeout");}
  c.preferences.throwApply=true;int persistenceBefore=failed[0];speech.speak(FAJR,.4f,()->failed[0]++);player=PcmAudioPlayer.latest;check(player.volume==.4f,"status persistence failure does not block audio");player.listener.complete();check(failed[0]==persistenceBefore+1,"status persistence failure does not block continuation");c.preferences.throwApply=false;
  MainActivity.throwNotify=true;int notificationBefore=failed[0];speech.speak(FAJR,1f,()->failed[0]++);player=PcmAudioPlayer.latest;player.listener.complete();check(failed[0]==notificationBefore+1,"UI event failure cannot block playback continuation");MainActivity.throwNotify=false;
  PcmAudioPlayer.synchronousComplete=true;speech.speak(FAJR,1f,()->failed[0]++);status(c,"finished");PcmAudioPlayer.synchronousComplete=false;check(Handler.timers.isEmpty(),"all terminal paths remove timeout");
  speech.speak(FAJR,1f,()->speech.speak("اقتربت صلاة المغرب",1f,()->replacement[0]++));PcmAudioPlayer first=PcmAudioPlayer.latest;first.listener.complete();player=PcmAudioPlayer.latest;check(player!=first,"completion may start a new clip");first.listener.error(new Exception("late"));status(c,"playing");player.listener.complete();check(replacement[0]==2,"nested replacement survives stale callback");check(Handler.timers.isEmpty(),"nested completion also removes timeout");
  ArabicSpeech oldService=new ArabicSpeech(c,attributes);oldService.speak(FAJR,1f,()->{});PcmAudioPlayer older=PcmAudioPlayer.latest;
  ArabicSpeech prelude=new ArabicSpeech(c,attributes);prelude.speak(FAJR,1f,()->{});PcmAudioPlayer newest=PcmAudioPlayer.latest;
  oldService.close();ArabicSpeech.recordCancellation(c);status(c,"playing");
  older.listener.complete();status(c,"playing");newest.listener.complete();status(c,"finished");
  ArabicSpeech.recordCancellation(c);status(c,"cancelled");
  System.out.println("PASS: actual bundled ArabicSpeech phrase mapping, route/volume, PCM completion/errors/timeout, rapid replacement, invalid input and stale callbacks.");
 }
}''',

}

with tempfile.TemporaryDirectory(prefix='salati-arabic-speech-') as directory:
    target = Path(directory)
    SOURCES['com/salati/prayer/ArabicSpeech.java'] = (ROOT / 'android/app/src/main/java/com/salati/prayer/ArabicSpeech.java').read_text()
    files = []
    for relative, contents in SOURCES.items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
        files.append(str(path))
    jdk = Path(os.environ['JAVA_HOME']) / 'bin' if os.environ.get('JAVA_HOME') else None
    javac = str(jdk / 'javac') if jdk else shutil.which('javac')
    java = str(jdk / 'java') if jdk else shutil.which('java')
    if not javac or not java:
        raise SystemExit('A host JDK is required; set JAVA_HOME to run this regression test.')
    subprocess.run([javac, '-d', str(target), *files], check=True)
    subprocess.run([java, '-cp', str(target), 'com.salati.prayer.ArabicSpeechLifecycleTest'], check=True)
