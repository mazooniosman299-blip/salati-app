"""Production staging/state methods identify superseded starts without exposing stale queue state."""
from pathlib import Path
import os,subprocess,tempfile
source=Path('android/app/src/main/java/com/salati/prayer/QuranService.java').read_text()
def method(marker):
 start=source.index(marker);begin=source.index('{',start);depth=1;i=begin+1
 while depth:depth+=(source[i]=='{')-(source[i]=='}');i+=1
 return source[start:i]
methods='\n'.join(method(m) for m in ['static synchronized void stage(','static synchronized JSONObject take(','static String state()'])
code='''import java.util.*;
public class RequestStateTest {
 static String lastState="{}";static JSONObject pending;static volatile String requestedSession="";
 static class JSONObject {
  static Map<String,Map<String,String>> serialized=new HashMap<>();Map<String,String> values=new HashMap<>();
  JSONObject(){}JSONObject(String text){if(serialized.containsKey(text))values.putAll(serialized.get(text));else if(!text.equals("{}"))throw new IllegalArgumentException();}
  JSONObject put(String key,String value){values.put(key,value);return this;}String optString(String key){return values.getOrDefault(key,"");}
  public String toString(){String key="json"+serialized.size();serialized.put(key,new HashMap<>(values));return key;}
 }
'''+methods+'''
 public static void main(String[] args){
  lastState=new JSONObject().put("session","old").toString();stage(new JSONObject().put("session","A"));
  JSONObject value=new JSONObject(state());if(!value.optString("session").equals("old")||!value.optString("requestedSession").equals("A"))throw new AssertionError("Staged A must be identified separately from old active snapshot");
  take("A");value=new JSONObject(state());if(!value.optString("requestedSession").equals("A"))throw new AssertionError("A must stay pending until snapshot catches up, even after request was consumed");
  stage(new JSONObject().put("session","B"));take("B");lastState=new JSONObject().put("session","B").toString();value=new JSONObject(state());if(!value.optString("requestedSession").equals("B")||!value.optString("session").equals("B"))throw new AssertionError("Superseding request B must be identifiable after acknowledgement");
  System.out.println("PASS: production native state distinguishes staged/consumed requests from acknowledged playback across rapid supersession.");
 }
}'''
with tempfile.TemporaryDirectory(prefix='salati-request-state-') as d:
 p=Path(d)/'RequestStateTest.java';p.write_text(code);jdk=Path(os.environ['JAVA_HOME'])/'bin'
 subprocess.run([jdk/'javac',p],check=True);subprocess.run([jdk/'java','-cp',d,'RequestStateTest'],check=True)
