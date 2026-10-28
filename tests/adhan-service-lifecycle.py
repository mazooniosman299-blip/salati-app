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
