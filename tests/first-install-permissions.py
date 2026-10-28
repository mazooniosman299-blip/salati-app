"""Run actual activity permission sequencing with the Android dialog boundary substituted."""
from pathlib import Path
import subprocess,tempfile,os
s=Path('android/app/src/main/java/com/salati/prayer/MainActivity.java').read_text()
def method(marker):
 start=s.index(marker);body=s.index('{',start);depth=1;i=body+1
 while depth:
  depth+=(s[i]=='{')-(s[i]=='}');i+=1
 return s[start:i]
methods='\n'.join(method(m) for m in ['boolean notificationDecisionPending()','void requestLocationPermission()','void requestFirstNotificationPermission()','public void onRequestPermissionsResult('])
code='''import java.util.*;
class Base {public void onRequestPermissionsResult(int c,String[] p,int[] r){}}
public class PermissionSequenceTest extends Base {
 static class Build {static class VERSION {static int SDK_INT=36;}}
 static class Manifest {static class permission {static final String POST_NOTIFICATIONS="notification",ACCESS_FINE_LOCATION="fine",ACCESS_COARSE_LOCATION="coarse";}}
 static class PackageManager {static final int PERMISSION_GRANTED=0;}
 static class PrayerSchedule {static void scheduleNext(Object c,long t){}}
 class Prefs {boolean recorded;boolean getBoolean(String key,boolean fallback){return key.equals("notificationDecisionRecorded")?recorded:fallback;}Prefs edit(){return this;}Prefs putBoolean(String key,boolean value){if(key.equals("notificationDecisionRecorded"))recorded=value;return this;}void apply(){}}
 static class Handler {void post(Runnable run){run.run();}}
 static class Geo {void invoke(String origin,boolean allow,boolean retain){}}
 Prefs prefs=new Prefs();Handler main=new Handler();Geo geoCallback=new Geo();String geoOrigin="app";int activePermission;boolean permissionPageReady=true,resumed=true;ArrayList<Integer> requested=new ArrayList<>();
 boolean isFinishing(){return false;}boolean isDestroyed(){return false;}int checkSelfPermission(String key){return 1;}Prefs getPreferences(int mode){return prefs;}void notifyStatus(){}void requestPermissions(String[] p,int code){requested.add(code);}
'''+methods+'''
 public static void main(String[] args){
  for(int result:new int[]{0,1}){PermissionSequenceTest p=new PermissionSequenceTest();p.requestLocationPermission();p.requestFirstNotificationPermission();if(!p.requested.equals(Arrays.asList(102)))throw new AssertionError("First dialog must be notifications, without overlapping requests");p.onRequestPermissionsResult(102,new String[]{"notification"},new int[]{result});if(!p.requested.equals(Arrays.asList(102,101)))throw new AssertionError("Location must follow notification decision");}
  Build.VERSION.SDK_INT=32;PermissionSequenceTest old=new PermissionSequenceTest();old.requestFirstNotificationPermission();if(!old.requested.equals(Arrays.asList(101)))throw new AssertionError("Old Android must skip nonexistent notification runtime dialog");
  Build.VERSION.SDK_INT=36;PermissionSequenceTest waiting=new PermissionSequenceTest();waiting.permissionPageReady=false;waiting.requestLocationPermission();if(!waiting.requested.isEmpty())throw new AssertionError("Wait for page readiness");waiting.permissionPageReady=true;waiting.requestFirstNotificationPermission();if(!waiting.requested.equals(Arrays.asList(102)))throw new AssertionError("Start sequence after page ready");
  System.out.println("PASS: production first-install permission methods request notifications before location for allow/deny, no overlap, page readiness and pre-33 support.");
 }
}'''
with tempfile.TemporaryDirectory(prefix='salati-permissions-') as d:
 p=Path(d)/'PermissionSequenceTest.java';p.write_text(code);jdk=Path(os.environ['JAVA_HOME'])/'bin'
 subprocess.run([jdk/'javac',p],check=True);subprocess.run([jdk/'java','-cp',d,'PermissionSequenceTest'],check=True)
