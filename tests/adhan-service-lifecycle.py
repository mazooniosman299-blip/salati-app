"""Run actual service terminal/listener branches with Android lifecycle boundaries substituted."""
from pathlib import Path
import re,subprocess,tempfile,os
source=Path('android/app/src/main/java/com/salati/prayer/AdhanService.java').read_text()
finish=re.search(r' void finishPlayback\(String code\)\{([^\n]+)\}',source)[1]
focus=re.search(r'setOnAudioFocusChangeListener\(change->\{(.*?)\},handler\)',source)
focus=focus[1] if focus else 'onAudioFocusChange(change);'
timeout=re.search(r'handler.postDelayed\(\(\)->\{(.*?)\},600000\)',source)
timeout=timeout[1] if timeout else 'stopSelf();'
code='''public class AdhanBranches {
 boolean preview=true,terminal,stopped;int latestId=2,startId=1,cleanup,focusChanges;long generation=2;
 static final int STOP_FOREGROUND_REMOVE=1;
 static class MainActivity {static void notifyPlayback(String code){}}
 static class PrayerSchedule {static void recordDelivery(Object c,String code,Object error){}}
 void stopSelf(){stopped=true;}void stopSelf(int id){if(id==latestId)stopped=true;}
 void release(){cleanup++;generation++;}void stopForeground(int flags){}void onAudioFocusChange(int change){focusChanges++;}
 void finishPlayback(String code){'''+finish+'''}
 void deliverFocus(long ticket,int change){'''+focus+'''}
 void deliverTimeout(long ticket){'''+timeout+'''}
 public static void main(String[] args){
  AdhanBranches old=new AdhanBranches();old.finishPlayback("finished");if(old.stopped)throw new AssertionError("Old playback stops newer queued request");if(old.cleanup!=1)throw new AssertionError("Terminal playback must release audio/focus/wake immediately");
  AdhanBranches current=new AdhanBranches();current.startId=2;current.finishPlayback("stopped");if(!current.stopped)throw new AssertionError("Current request must stop normally");
  AdhanBranches replaced=new AdhanBranches();replaced.deliverFocus(1,-1);replaced.deliverTimeout(1);if(replaced.focusChanges!=0||replaced.stopped||replaced.cleanup!=0)throw new AssertionError("Old focus/timeout affects replacement");
  replaced.deliverFocus(2,1);if(replaced.focusChanges!=1)throw new AssertionError("Current focus callback lost");
  replaced.startId=2;replaced.deliverTimeout(2);if(!replaced.stopped||replaced.cleanup!=1)throw new AssertionError("Current timeout must clean up and stop");
  System.out.println("PASS: adhan start-ID isolation, immediate terminal cleanup, obsolete focus/timeout ignored and current callbacks retained.");
 }
}'''
with tempfile.TemporaryDirectory(prefix='salati-adhan-') as d:
 p=Path(d)/'AdhanBranches.java';p.write_text(code);jdk=Path(os.environ['JAVA_HOME'])/'bin'
 subprocess.run([jdk/'javac',p],check=True);subprocess.run([jdk/'java','-cp',d,'AdhanBranches'],check=True)

# Exercise actual prelude/main-player focus methods with deterministic PCM boundaries.
apply_focus=re.search(r' void applyFocus\(\)\{([^\n]+)\}',source)[1]
change_focus=re.search(r' void onAudioFocusChange\(int change\)\{([^\n]+)\}',source)[1]
focus_code='''package com.salati.prayer;
public class AdhanFocusBranches {
 static class Pcm {float volume;boolean paused;int changes,closed;void setVolume(float v){volume=v;changes++;}void setPaused(boolean p){paused=p;}void close(){closed++;}}
 static class Settings {double preferred=.8;double optDouble(String key,double fallback){return preferred;}}
 Pcm player,prelude;Settings settings=new Settings();AudioFocusPolicy focusState=new AudioFocusPolicy();String pendingRecording="recording";String recording;int plays;boolean finished;
 void finishPlayback(String code){finished=true;}void play(String name){recording=name;plays++;player=new Pcm();player.setVolume(focusState.volume((float)settings.preferred));player.setPaused(focusState.paused);}
 void applyFocus(){'''+apply_focus+'''}
 void onAudioFocusChange(int change){'''+change_focus+'''}
 static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
 static void near(float actual,float expected,String message){check(Math.abs(actual-expected)<.0001,message+": "+actual);}
 public static void main(String[] args){
  AdhanFocusBranches service=new AdhanFocusBranches();service.prelude=new Pcm();Pcm prelude=service.prelude;
  service.applyFocus();near(prelude.volume,.8f,"prelude volume updates with no main player");
  service.onAudioFocusChange(-3);near(prelude.volume,.2f,"CAN_DUCK affects prelude");check(prelude.closed==0&&!service.focusState.paused,"ducking keeps current phrase active");
  service.settings.preferred=.6;service.applyFocus();near(prelude.volume,.15f,"live user volume respects active ducking");
  service.onAudioFocusChange(1);near(prelude.volume,.6f,"focus gain restores updated user volume");
  service.settings.preferred=.35;service.applyFocus();near(prelude.volume,.35f,"live user volume reaches prelude");
  service.player=new Pcm();service.onAudioFocusChange(-3);near(prelude.volume,.0875f,"prelude and main output both receive focus volume");near(service.player.volume,.0875f,"main output volume is preserved");check(!service.player.paused,"ducking keeps main output active");
  service.onAudioFocusChange(-2);check(prelude.closed==1&&service.prelude==null,"transient focus loss closes prelude exactly once");check("recording".equals(service.pendingRecording)&&service.player.paused,"transient loss preserves pending adhan and pauses main output");
  service.onAudioFocusChange(1);check(service.plays==1&&service.pendingRecording==null&&"recording".equals(service.recording),"focus gain continues pending adhan exactly once");near(service.player.volume,.35f,"continued adhan respects live user volume");service.onAudioFocusChange(1);check(service.plays==1,"duplicate gain does not restart recording");
  service.onAudioFocusChange(-1);check(service.finished,"permanent focus loss preserves terminal cleanup path");
  AdhanFocusBranches unavailable=new AdhanFocusBranches();unavailable.prelude=new Pcm();unavailable.settings=null;unavailable.applyFocus();check(unavailable.prelude.changes==0,"missing settings is safe");
  System.out.println("PASS: actual adhan prelude/main PCM duck/restore, live volume, transient-close/pending continuation and permanent focus loss.");
 }
}'''
with tempfile.TemporaryDirectory(prefix='salati-prelude-focus-') as d:
 target=Path(d);test=target/'AdhanFocusBranches.java';test.write_text(focus_code)
 policy=Path('android/app/src/main/java/com/salati/prayer/AudioFocusPolicy.java')
 subprocess.run([jdk/'javac','-d',target,test,policy],check=True)
 subprocess.run([jdk/'java','-cp',target,'com.salati.prayer.AdhanFocusBranches'],check=True)
