"""Execute production service branches with small Android-boundary fixtures, not device instrumentation."""
from pathlib import Path
import re,subprocess,tempfile,os
source=Path('android/app/src/main/java/com/salati/prayer/QuranService.java').read_text()
missing=re.search(r'if\(request==null\)\{(.*?)\}',source)[1].replace('return START_NOT_STICKY;','return;')
prepared=source.split('current.setOnPreparedListener(mp->{',1)[1].split('});',1)[0]
finish=re.search(r' void finish\(String result\)\{([^\n]+)\}',source)[1]
focus=Path('android/app/src/main/java/com/salati/prayer/AdhanService.java').read_text().split('void applyFocus(){',1)[1].split('\n void play',1)[0].rstrip().removesuffix('}')
code='''public class ServiceBranches {
 static class MediaPlayer {static final int SEEK_CLOSEST=3;boolean fail;int getDuration(){if(fail)throw new IllegalStateException("released");return 10;}void seekTo(long v,int mode){}void start(){}}
 static class Row {double optDouble(String key,double fallback){return fallback;}}
 static class Settings {double optDouble(String key,double fallback){return .25;}}
 static class Focus {float volume(float value){return value;}boolean paused;}
 static class Pcm {float volume;void setVolume(float v){volume=v;}void setPaused(boolean p){}}
 Row row=new Row();long ticket,generation;MediaPlayer player;Object rows;boolean ready,wantPlay;int duration;String status;boolean terminal,resumeOnGain;int startId=1;static final int STOP_FOREGROUND_REMOVE=1;int latestId=2;boolean stopped;int errors;
 void stopSelf(){stopped=true;}void stopSelf(int id){if(id==latestId)stopped=true;}
 void publish(){}void tick(){}void releaseWake(){}void releasePlayer(){}void abandonFocus(){}void stopForeground(int mode){}void finish(String result){errors++;'''+finish+'''}
 void missing(int id){'''+missing+'''}
 void prepared(MediaPlayer mp){'''+prepared+'''}
 static class Adhan {Pcm player=new Pcm(),prelude;Settings settings=new Settings();Focus focusState=new Focus();void applyFocus(){'''+focus+'''}}
 public static void main(String[] args){int failures=0;
 ServiceBranches s=new ServiceBranches();s.missing(1);if(s.stopped){System.err.println("Cancelled old start stopped a newer queued start");failures++;}
 s=new ServiceBranches();s.player=new MediaPlayer();s.player.fail=true;try{s.prepared(s.player);if(s.errors!=1){System.err.println("Prepared error not reported");failures++;}}catch(IllegalStateException e){System.err.println("Prepared callback leaked MediaPlayer error");failures++;}
 s=new ServiceBranches();s.finish("stopped");if(s.stopped){System.err.println("Old playback completion stopped newer queued start");failures++;}
 s=new ServiceBranches();MediaPlayer old=new MediaPlayer();old.fail=true;s.player=new MediaPlayer();s.prepared(old);if(s.errors!=0){System.err.println("Stale callback affected replacement");failures++;}
 Adhan a=new Adhan();a.applyFocus();if(Math.abs(a.player.volume-.25f)>.0001){System.err.println("Native playback ignored saved volume");failures++;}
 if(failures!=0)throw new AssertionError(failures+" service regressions");
 System.out.println("PASS: stale cancelled start, prepared errors, old-player callback rejection and native volume.");
 }
}'''
with tempfile.TemporaryDirectory(prefix='salati-service-') as d:
 p=Path(d)/'ServiceBranches.java';p.write_text(code);jdk=Path(os.environ['JAVA_HOME'])/'bin'
 subprocess.run([jdk/'javac',p],check=True);subprocess.run([jdk/'java','-cp',d,'ServiceBranches'],check=True)
