from pathlib import Path
import re,subprocess,tempfile,os
# Compile the actual production method; only Android/JSON boundary types are replaced.
s=Path('android/app/src/main/java/com/salati/prayer/QuranService.java').read_text();method=re.search(r' static String queue\(\)\{[^\n]+',s)[0]
code='''import java.util.concurrent.atomic.AtomicReference;
import java.util.concurrent.CountDownLatch;
public class QuranService {
 static volatile QuranService active;volatile JSONArray rows;
 static class JSONArray {public String toString(){return "[]";}}
'''+method+'''
 public static void main(String[] args)throws Exception{
  QuranService service=new QuranService();active=service;JSONArray ready=new JSONArray();AtomicReference<Throwable> error=new AtomicReference<>();
  CountDownLatch start=new CountDownLatch(1);long[] reads={0};
  Thread writer=new Thread(()->{try{start.await();for(int i=0;i<2000000;i++){service.rows=ready;active=service;service.rows=null;active=null;}}catch(Throwable e){error.set(e);}});
  Thread reader=new Thread(()->{try{start.await();for(int i=0;i<1000000;i++){String value=queue();if(!"[]".equals(value))throw new AssertionError("Invalid queue snapshot");reads[0]++;}}catch(Throwable e){error.set(e);}});
  writer.start();reader.start();start.countDown();writer.join();reader.join();if(reads[0]!=1000000)throw new AssertionError("Reader did not complete");if(error.get()!=null)throw new AssertionError("Queue snapshot raced with start/stop",error.get());
 }
}'''
with tempfile.TemporaryDirectory(prefix='salati-queue-') as d:
 p=Path(d)/'QuranService.java';p.write_text(code);jdk=Path(os.environ['JAVA_HOME'])/'bin'
 subprocess.run([jdk/'javac',p],check=True)
 r=subprocess.run([jdk/'java','-Xint','-cp',d,'QuranService'],capture_output=True,text=True);print(r.stderr if r.returncode else 'PASS: native queue snapshots survive concurrent session replacement.');raise SystemExit(r.returncode)
