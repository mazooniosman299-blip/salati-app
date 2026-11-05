"""Run actual automatic alarm/focus branches; protect alarm audibility and calls.

Android15 cold/Doze integration RED proves focus-control denial is persistent,
not a foreground-state delay. Alarm output remains a separate platform usage.
"""
from pathlib import Path
import os,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'android/app/src/main/java/com/salati/prayer/AdhanService.java').read_text()
def extract(name):
 start=source.index(' void '+name+'(');opening=source.index('{',start);end=opening+1;depth=1
 while depth:
  depth+=(source[end]=='{')-(source[end]=='}');end+=1
 return source[start:end]
method=extract('requestPlaybackFocus')
if ' void monitorAlarmMode(' in source:method+='\n'+extract('monitorAlarmMode')
entry='requestPlaybackFocus(7,"fajr",0)' if 'int attempt' in method else 'requestPlaybackFocus(7,"fajr")'
code="""import java.util.*;
public class FocusStartupTest {
 static class Build {static class VERSION {static int SDK_INT=35;}}
 static class AudioManager {static final int AUDIOFOCUS_REQUEST_GRANTED=1,MODE_NORMAL=0;int calls,mode,modeReads;int[] results,modes;AudioManager(int... results){this.results=results;}int requestAudioFocus(Object request){return results[Math.min(calls++,results.length-1)];}int getMode(){return modes==null?mode:modes[Math.min(modeReads++,modes.length-1)];}}
 static class Handler {ArrayDeque<Runnable> tasks=new ArrayDeque<>();void postDelayed(Runnable r,long ms){tasks.add(r);}}
 static class PrayerSchedule {static void recordDelivery(Object c,String status,Object error){}}
 AudioManager manager;Object focus=new Object();Handler handler=new Handler();boolean preview,terminal;long generation=7;int starts;String finished;
 FocusStartupTest(int... results){manager=new AudioManager(results);}
 void finishPlayback(String code){finished=code;terminal=true;generation++;handler.tasks.clear();}
 void beginFocusedPlayback(long ticket,String prayer){check(ticket==generation,"Obsolete generation started");check(prayer.equals("fajr"),"Lost prayer context");starts++;}
 void tick(){if(!handler.tasks.isEmpty())handler.tasks.remove().run();}
 static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
 void start(){"""+entry+""";}
"""+method+"""
 public static void main(String[] args){
  FocusStartupTest cold=new FocusStartupTest(0);cold.start();for(int i=0;i<9;i++)cold.tick();check(cold.starts==1&&cold.finished==null,"Automatic Android15 alarm must remain audible when foreground-only focus CONTROL is denied");
  cold.manager.mode=2;cold.tick();check("stopped".equals(cold.finished)&&cold.handler.tasks.isEmpty(),"Call must stop alarm output and remove callbacks");cold.manager.mode=0;cold.tick();check(cold.starts==1,"Ended call must not restart a stopped alarm");
  FocusStartupTest startsRinging=new FocusStartupTest(0);startsRinging.manager.modes=new int[]{0,2};startsRinging.start();check(startsRinging.starts==0&&"stopped".equals(startsRinging.finished),"Call arriving between startup checks must prevent audio start");
  for(int mode:new int[]{1,2,3,4,5,6}){FocusStartupTest call=new FocusStartupTest(0);call.manager.mode=mode;call.start();for(int i=0;i<9;i++)call.tick();check(call.starts==0&&"blocked".equals(call.finished),"Never enter alarm-only output during phone/communication/ringing mode");}
  FocusStartupTest preview=new FocusStartupTest(0);preview.preview=true;preview.start();for(int i=0;i<9;i++)preview.tick();check(preview.starts==0&&"blocked".equals(preview.finished),"Preview remains media requiring granted focus");
  Build.VERSION.SDK_INT=34;FocusStartupTest legacy=new FocusStartupTest(0);legacy.start();for(int i=0;i<9;i++)legacy.tick();check(legacy.starts==0&&"blocked".equals(legacy.finished),"Legacy focus-denial behavior retained");Build.VERSION.SDK_INT=35;
  FocusStartupTest stopped=new FocusStartupTest(0);stopped.start();stopped.terminal=true;stopped.tick();check(stopped.starts==1&&stopped.handler.tasks.isEmpty(),"Stopped generation cannot schedule further checks");
  FocusStartupTest replaced=new FocusStartupTest(0);replaced.start();replaced.generation++;replaced.tick();check(replaced.starts==1&&replaced.handler.tasks.isEmpty(),"Old callback must not affect replacement");
  FocusStartupTest ready=new FocusStartupTest(1);ready.start();check(ready.starts==1&&ready.handler.tasks.isEmpty(),"Granted focus starts original output without extra watcher");
  System.out.println("PASS actual alarm focus/output branch: automatic35+ cold output, calls stop/block, preview/legacy rejection, stop/replacement and granted focus");
 }
}
"""
with tempfile.TemporaryDirectory(prefix='salati-focus-start-') as d:
 p=Path(d)/'FocusStartupTest.java';p.write_text(code);jdk=Path(os.environ['JAVA_HOME'])/'bin'
 log=Path(d)/'android/util/Log.java';log.parent.mkdir(parents=True);log.write_text('package android.util;public class Log {public static int i(String tag,String msg){return 0;}}')
 subprocess.run([jdk/'javac','-d',d,p,log],check=True);subprocess.run([jdk/'java','-cp',d,'FocusStartupTest'],check=True)
