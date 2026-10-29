"""Run the production focus handler against consecutive focus events and user intent."""
from pathlib import Path
import tempfile,subprocess,os
source=Path('android/app/src/main/java/com/salati/prayer/QuranService.java').read_text()
method=source.split(' void focusChanged(int change){',1)[1].split('\n',1)[0]
code='''public class FocusSequence {
 static class AudioManager {static final int AUDIOFOCUS_GAIN=1,AUDIOFOCUS_LOSS=-1,AUDIOFOCUS_LOSS_TRANSIENT=-2,AUDIOFOCUS_LOSS_TRANSIENT_CAN_DUCK=-3;}
 boolean wantPlay=true,resumeOnGain;int resumes;
 void pause(boolean user){if(user)resumeOnGain=false;wantPlay=false;}
 void resume(){resumes++;wantPlay=true;resumeOnGain=false;}
 void focusChanged(int change){'''+method+'''
 static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
 public static void main(String[] args){
  for(int first:new int[]{-2,-3})for(int second:new int[]{-2,-3}){
   FocusSequence q=new FocusSequence();q.focusChanged(first);q.focusChanged(second);q.focusChanged(1);
   check(q.wantPlay&&q.resumes==1,"repeated transient loss must preserve pending resume intent");
   q=new FocusSequence();q.focusChanged(first);q.pause(true);q.focusChanged(second);q.focusChanged(1);
   check(!q.wantPlay&&q.resumes==0,"explicit user pause during interruption must not resume");
   q=new FocusSequence();q.focusChanged(first);q.focusChanged(-1);q.focusChanged(1);
   check(!q.wantPlay&&q.resumes==0,"permanent focus loss cancels resume intent");
  }
  System.out.println("PASS: repeated transient focus events preserve intent; user pause and permanent loss suppress resume.");
 }
}'''
with tempfile.TemporaryDirectory(prefix='salati-focus-sequence-') as name:
 folder=Path(name);java=Path(os.environ['JAVA_HOME'])/'bin';(folder/'FocusSequence.java').write_text(code)
 subprocess.run([java/'javac',folder/'FocusSequence.java'],check=True)
 subprocess.run([java/'java','-cp',folder,'FocusSequence'],check=True)
