"""Actual startup-focus branch with deterministic OS denial/handler boundaries.

The original cold-process Android15 regression failed with deliveryStatus
blocked and HardeningEnforcer OP_TAKE_AUDIO_FOCUS denial at procState4. These
cases additionally protect cancellation and permanent focus denial behavior.
"""
from pathlib import Path
import os,subprocess,tempfile,re
root=Path(__file__).resolve().parents[1]
source=(root/'android/app/src/main/java/com/salati/prayer/AdhanService.java').read_text()
start=source.index(' void requestPlaybackFocus(');opening=source.index('{',start);end=opening+1;depth=1
while depth:
 depth+=(source[end]=='{')-(source[end]=='}');end+=1
method=source[start:end]
code='''import java.util.*;
public class FocusStartupTest {
 static class AudioManager {static final int AUDIOFOCUS_REQUEST_GRANTED=1;int calls;int[] results;AudioManager(int... results){this.results=results;}int requestAudioFocus(Object request){return results[Math.min(calls++,results.length-1)];}}
 static class Handler {ArrayDeque<Runnable> tasks=new ArrayDeque<>();void postDelayed(Runnable r,long ms){check(ms==250,"Bounded foreground-state retry delay");tasks.add(r);}}
 static class PrayerSchedule {static void recordDelivery(Object c,String status,Object error){check(status.equals("waiting_audio_focus"),"Startup diagnosis stays explicit");}}
 AudioManager manager;Object focus=new Object();Handler handler=new Handler();boolean preview,terminal;long generation=7;int starts;String finished;
 FocusStartupTest(int... results){manager=new AudioManager(results);}
 void finishPlayback(String code){finished=code;terminal=true;generation++;handler.tasks.clear();}
 void beginFocusedPlayback(long ticket,String prayer){check(ticket==generation,"Obsolete generation started");check(prayer.equals("fajr"),"Lost prayer context");starts++;}
 void drain(){int n=0;while(!handler.tasks.isEmpty()){check(n++<20,"Unbounded retry");handler.tasks.remove().run();}}
 static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
'''+method+'''
 public static void main(String[] args){
  FocusStartupTest cold=new FocusStartupTest(0,0,1);cold.requestPlaybackFocus(7,"fajr",0);check(cold.starts==0&&cold.finished==null,"Do not play before audio focus is granted");cold.drain();check(cold.starts==1&&cold.manager.calls==3&&cold.finished==null,"Cold eligibility transition must recover once");
  FocusStartupTest denied=new FocusStartupTest(0);denied.requestPlaybackFocus(7,"fajr",0);denied.drain();check(denied.starts==0&&"blocked".equals(denied.finished)&&denied.manager.calls==9,"Persistent denial must terminate, never bypass policy");
  FocusStartupTest stopped=new FocusStartupTest(0,1);stopped.requestPlaybackFocus(7,"fajr",0);stopped.terminal=true;stopped.drain();check(stopped.starts==0&&stopped.manager.calls==1,"Stop during pending retry must not restart");
  FocusStartupTest replaced=new FocusStartupTest(0,1);replaced.requestPlaybackFocus(7,"fajr",0);replaced.generation++;replaced.drain();check(replaced.starts==0&&replaced.manager.calls==1,"Old callback must not affect replacement");
  FocusStartupTest preview=new FocusStartupTest(0,1);preview.preview=true;preview.requestPlaybackFocus(7,"fajr",0);preview.drain();check(preview.starts==0&&preview.manager.calls==1&&"blocked".equals(preview.finished),"Manual preview preserves immediate rejection");
  FocusStartupTest ready=new FocusStartupTest(1);ready.requestPlaybackFocus(7,"fajr",0);check(ready.starts==1&&ready.handler.tasks.isEmpty(),"Already-ready output starts without delay");
  System.out.println("PASS actual startup focus branch: cold denial/grant, permanent denial, stop/replacement, preview and already-ready behavior");
 }
}
'''
with tempfile.TemporaryDirectory(prefix='salati-focus-start-') as d:
 p=Path(d)/'FocusStartupTest.java';p.write_text(code);jdk=Path(os.environ['JAVA_HOME'])/'bin'
 subprocess.run([jdk/'javac',p],check=True);subprocess.run([jdk/'java','-cp',d,'FocusStartupTest'],check=True)
