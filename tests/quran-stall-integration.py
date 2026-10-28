"""Execute the actual native progress callback with a deterministic clock/player boundary."""
from pathlib import Path
import subprocess,tempfile,os
source=Path('android/app/src/main/java/com/salati/prayer/QuranService.java').read_text()
body=source.split('progressTick=()->{',1)[1].split('};handler.postDelayed(progressTick',1)[0]
code='''package com.salati.prayer;
public class StallCallbackTest {
 static class SystemClock {static long now;static long elapsedRealtime(){return now;}}
 static class Player {int position=1000;int getCurrentPosition(){return position;}}
 static class Row {double optDouble(String key,double fallback){return fallback;}}
 static class Rows {Row getJSONObject(int index){return new Row();}}
 static class Playlist {int index;}
 Player player=new Player();Rows rows=new Rows();Playlist playlist=new Playlist();PlaybackWatchdog watchdog=new PlaybackWatchdog(45000);boolean ready=true,wantPlay=true;long generation;int position,errors;String lastState;Runnable progressTick;
 void holdWake(){}Object snapshot(){return "{}";}void advance(){}void finish(String error){errors++;wantPlay=false;ready=false;generation++;}
 void tick(){long ticket=generation;progressTick=()->{'''+body+'''};}
 public static void main(String[] args){StallCallbackTest p=new StallCallbackTest();p.tick();p.progressTick.run();SystemClock.now=44999;p.progressTick.run();if(p.errors!=0)throw new AssertionError("Normal buffering rejected");SystemClock.now=45000;p.progressTick.run();if(p.errors!=1)throw new AssertionError("Native callback never terminates stalled playback");System.out.println("PASS: actual QuranService progress callback reports/stops a 45-second stall.");}
}'''
with tempfile.TemporaryDirectory(prefix='salati-stall-') as d:
 p=Path(d)/'StallCallbackTest.java';p.write_text(code);jdk=Path(os.environ['JAVA_HOME'])/'bin'
 subprocess.run([jdk/'javac','-d',d,'android/app/src/main/java/com/salati/prayer/PlaybackWatchdog.java',p],check=True);subprocess.run([jdk/'java','-cp',d,'com.salati.prayer.StallCallbackTest'],check=True)
