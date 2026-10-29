"""Exercise production Activity lifecycle methods through a two-window callback handoff."""
from pathlib import Path
import os,subprocess,tempfile
s=Path('android/app/src/main/java/com/salati/prayer/MainActivity.java').read_text()
def method(marker):
 start=s.index(marker);begin=s.index('{',start);depth=1;i=begin+1
 while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
 return s[start:i]
code='''import java.lang.ref.WeakReference;
class Base {protected void onResume(){}protected void onDestroy(){}}
public class ActivityOwnerTest extends Base {
 static WeakReference<ActivityOwnerTest> current=new WeakReference<>(null);
 static boolean nativeAdhanPlaying,nativeApproachPlaying;boolean resumed,wantCompass;Object rotation;Handler main=new Handler();Ads ads;Web web=new Web();Sensors sensors=new Sensors();Geo geoCallback;String geoOrigin;
 static class Handler {void post(Runnable r){r.run();}}
 static class Ads {boolean playing;void setNativePlayback(boolean value){playing=value;}void resume(){}void destroy(){}}
 static class Web {void onResume(){}void evaluateJavascript(String s,Object callback){}void removeJavascriptInterface(String s){}void destroy(){}}
 static class Sensors {void registerListener(Object a,Object b,int c){}void unregisterListener(Object a){}}
 static class SensorManager {static final int SENSOR_DELAY_GAME=1;}
 static class PrayerSchedule {static void scheduleNext(Object c,long n){}}
 static class PrayerWidget {static void updateAll(Object c){}}
 static class Geo {void invoke(String origin,boolean allow,boolean retain){}}
 void requestFirstNotificationPermission(){}void notifyStatus(){}
'''+method('protected void onResume()')+'\n'+method('protected void onDestroy()')+'''
 public static void main(String[] args){
  ActivityOwnerTest a=new ActivityOwnerTest(),b=new ActivityOwnerTest();a.ads=new Ads();current=new WeakReference<>(a);a.onResume();current=new WeakReference<>(b);b.onResume();b.onDestroy();nativeAdhanPlaying=true;a.onResume();if(!a.ads.playing)throw new AssertionError("Returning Activity must suppress ads during native audio started under another Activity");
  if(current.get()!=a)throw new AssertionError("Returning to older Activity must restore native callback destination");
  ActivityOwnerTest c=new ActivityOwnerTest();c.onResume();a.onDestroy();if(current.get()!=c)throw new AssertionError("Destroying an old Activity must not clear current owner");
  System.out.println("PASS: production onResume/onDestroy restore native callback ownership across Activity returns and preserve newer owner.");
 }
}'''
with tempfile.TemporaryDirectory(prefix='salati-activity-owner-') as d:
 p=Path(d)/'ActivityOwnerTest.java';p.write_text(code);jdk=Path(os.environ['JAVA_HOME'])/'bin'
 subprocess.run([jdk/'javac',p],check=True);subprocess.run([jdk/'java','-cp',d,'ActivityOwnerTest'],check=True)
