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
 public final Map<String,Object> values=new HashMap<>();
 public Editor edit(){return new Editor();}
 public class Editor {
  public Editor putString(String key,String value){values.put(key,value);return this;}
  public Editor putBoolean(String key,boolean value){values.put(key,value);return this;}
  public void apply(){}
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
    'android/speech/tts/Voice.java': '''package android.speech.tts; import java.util.*;
public class Voice {
 private final Locale locale;private final boolean network;private final int quality,latency;private final Set<String> features;
 public Voice(String language,boolean network,int quality,int latency,String... features){this.locale=Locale.forLanguageTag(language);this.network=network;this.quality=quality;this.latency=latency;this.features=new HashSet<>(Arrays.asList(features));}
 public Locale getLocale(){return locale;}public boolean isNetworkConnectionRequired(){return network;}public Set<String> getFeatures(){return features;}public int getQuality(){return quality;}public int getLatency(){return latency;}
}''',
    'android/speech/tts/UtteranceProgressListener.java': '''package android.speech.tts;
public abstract class UtteranceProgressListener {public abstract void onStart(String id);public abstract void onDone(String id);public abstract void onError(String id);}''',
    'android/speech/tts/TextToSpeech.java': '''package android.speech.tts;
import android.content.Context;import android.media.AudioAttributes;import android.os.Bundle;import java.util.*;
public class TextToSpeech {
 public static final int SUCCESS=0,ERROR=-1,QUEUE_FLUSH=0;
 public static class Engine {public static final String KEY_FEATURE_NOT_INSTALLED="notInstalled",KEY_PARAM_VOLUME="volume";}
 public interface OnInitListener {void onInit(int status);}
 public static TextToSpeech latest;public static int nextResult=SUCCESS;
 public Set<Voice> voices=new LinkedHashSet<>();public Voice selected;public UtteranceProgressListener listener;public Bundle params;public AudioAttributes attributes;public float rate;public int spoken,stopped,shutdown;public String text;private final OnInitListener init;
 public TextToSpeech(Context context,OnInitListener init){this.init=init;latest=this;}
 public void initialized(int status){init.onInit(status);}
 public Set<Voice> getVoices(){return voices;}public int setVoice(Voice voice){selected=voice;return SUCCESS;}
 public void setAudioAttributes(AudioAttributes value){attributes=value;}public void setSpeechRate(float value){rate=value;}
 public void setOnUtteranceProgressListener(UtteranceProgressListener value){listener=value;}
 public int speak(String value,int queue,Bundle bundle,String id){spoken++;text=value;params=bundle;return nextResult;}
 public void stop(){stopped++;}public void shutdown(){shutdown++;}
}''',
    'com/salati/prayer/MainActivity.java': '''package com.salati.prayer;
import java.lang.ref.WeakReference;import android.os.*;
class MainActivity {static WeakReference<MainActivity> current=new WeakReference<>(null);final Handler main=new Handler(Looper.getMainLooper());void notifyStatus(){}}''',
    'com/salati/prayer/ArabicSpeechLifecycleTest.java': '''package com.salati.prayer;
import android.content.Context;import android.media.AudioAttributes;import android.os.Handler;import android.speech.tts.*;
public final class ArabicSpeechLifecycleTest {
 static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
 static void status(Context context,String expected){check(expected.equals(context.preferences.values.get("status")),"status should be "+expected+": "+context.preferences.values);}
 static Voice arabic(){return new Voice("ar-SA",false,400,100);}
 public static void main(String[] args){
  Context c=new Context();AudioAttributes attributes=new AudioAttributes();ArabicSpeech speech=new ArabicSpeech(c,attributes);int[] done={0};
  speech.speak("الصلاة خير من النوم",.35f,()->done[0]++);TextToSpeech engine=TextToSpeech.latest;
  Voice acceptable=arabic(),best=new Voice("ar-EG",false,500,80),slow=new Voice("ar-SA",false,500,200);
  engine.voices.add(acceptable);engine.voices.add(slow);engine.voices.add(best);engine.voices.add(new Voice("ar-SA",true,1000,0));engine.voices.add(new Voice("ar-SA",false,1000,0,TextToSpeech.Engine.KEY_FEATURE_NOT_INSTALLED));
  check(engine.spoken==0,"must await initialization");engine.initialized(TextToSpeech.SUCCESS);
  check(engine.spoken==1&&engine.selected==best,"select highest-quality installed offline Arabic, latency breaks tie");
  check(engine.attributes==attributes&&Math.abs(engine.rate-.92f)<.001,"speech keeps alarm attributes and expected rate");
  check(Math.abs(engine.params.values.get("volume")-.35f)<.001,"saved volume must reach TTS");check(done[0]==0,"adhan waits for speech completion");
  engine.listener.onDone("id");engine.listener.onDone("duplicate");engine.listener.onError("late");
  check(done[0]==1,"completion must resume adhan exactly once");check(engine.stopped==1&&engine.shutdown==1,"finished engine releases resources once");status(c,"ready");check(Handler.timers.isEmpty(),"finished speech removes timeout");
  // Each unusable voice category must continue adhan without a fake Arabic fallback.
  for(int kind=0;kind<4;kind++){
   final int[] count={0};speech.speak("reminder",1f,()->count[0]++);engine=TextToSpeech.latest;
   if(kind==1)engine.voices.add(new Voice("en-US",false,900,0));
   if(kind==2)engine.voices.add(new Voice("ar-SA",true,900,0));
   if(kind==3)engine.voices.add(new Voice("ar-SA",false,900,0,TextToSpeech.Engine.KEY_FEATURE_NOT_INSTALLED));
   engine.initialized(TextToSpeech.SUCCESS);check(count[0]==1&&engine.spoken==0,"unusable voices must not speak or block adhan: "+kind);status(c,"missing_arabic");
  }
  final int[] timed={0};speech.speak("wait",1f,()->timed[0]++);engine=TextToSpeech.latest;engine.voices.add(arabic());
  Handler.advance(7999);check(timed[0]==0,"deadline must allow initialization before eight seconds");Handler.advance(1);check(timed[0]==1,"initialization timeout resumes adhan");status(c,"timeout");engine.initialized(TextToSpeech.SUCCESS);check(engine.spoken==0&&timed[0]==1,"late initialization cannot restart timed-out speech");
  final int[] cancelled={0};speech.speak("cancel",1f,()->cancelled[0]++);engine=TextToSpeech.latest;engine.voices.add(arabic());speech.close();engine.initialized(TextToSpeech.SUCCESS);Handler.advance(9000);check(engine.spoken==0&&cancelled[0]==0,"closed pending init cannot speak or run continuation");
  speech.speak("cancel active",1f,()->cancelled[0]++);engine=TextToSpeech.latest;engine.voices.add(arabic());engine.initialized(TextToSpeech.SUCCESS);speech.close();engine.listener.onDone("late");check(cancelled[0]==0,"closed active speech ignores late completion");
  final int[] failed={0};speech.speak("error",2f,()->failed[0]++);engine=TextToSpeech.latest;engine.voices.add(arabic());engine.initialized(TextToSpeech.SUCCESS);check(engine.params.values.get("volume")==1f,"volume clamps to one");engine.listener.onError("id");check(failed[0]==1,"speech error must resume adhan");status(c,"error");
  TextToSpeech.nextResult=TextToSpeech.ERROR;speech.speak("rejected",-1f,()->failed[0]++);engine=TextToSpeech.latest;engine.voices.add(arabic());engine.initialized(TextToSpeech.SUCCESS);check(failed[0]==2&&engine.params.values.get("volume")==0f,"rejected speak resumes adhan and clamps volume to zero");status(c,"error");TextToSpeech.nextResult=TextToSpeech.SUCCESS;
  speech.speak("init error",1f,()->failed[0]++);engine=TextToSpeech.latest;engine.initialized(TextToSpeech.ERROR);check(failed[0]==3&&engine.spoken==0,"initialization error resumes adhan");status(c,"unavailable");
  final int[] speechTimeout={0};speech.speak("stalled",1f,()->speechTimeout[0]++);engine=TextToSpeech.latest;engine.voices.add(arabic());engine.initialized(TextToSpeech.SUCCESS);Handler.advance(8000);check(speechTimeout[0]==1&&engine.shutdown==1,"stalled utterance times out and resumes adhan");engine.listener.onDone("late");check(speechTimeout[0]==1,"late utterance completion cannot repeat continuation");check(Handler.timers.isEmpty(),"all terminal paths remove timers");
  System.out.println("PASS: actual ArabicSpeech local voice selection, volume, init/completion/error/timeout continuations, cancellation and late callbacks.");
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
