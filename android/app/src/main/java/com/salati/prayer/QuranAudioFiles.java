package com.salati.prayer;
import java.io.*;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashMap;
import java.util.Map;

final class QuranAudioFiles {
 static boolean valid(File file){
  if(!file.isFile()||file.length()<128)return false;
  try(InputStream input=new FileInputStream(file)){int a=input.read(),b=input.read(),c=input.read();return a==73&&b==68&&c==51||a==255&&(b&224)==224;}catch(IOException error){return false;}
 }
 /** Read the entire file; verify its stored digest on every later access,
  * including after an update. This detects same-size content corruption. */
 static String sha256(File file) throws IOException {
  try{
   MessageDigest digest=MessageDigest.getInstance("SHA-256");
   try(InputStream input=new BufferedInputStream(new FileInputStream(file))){
    byte[] bytes=new byte[32768];int count;
    while((count=input.read(bytes))!=-1)digest.update(bytes,0,count);
   }
   StringBuilder hex=new StringBuilder(64);
   for(byte value:digest.digest())hex.append(String.format(java.util.Locale.ROOT,"%02x",value&255));
   return hex.toString();
  }catch(NoSuchAlgorithmException error){throw new IllegalStateException("Missing SHA-256",error);}
 }
 // A media hash must not be recomputed for each HTTP Range / status refresh.
 // Metadata changes invalidate this in-memory cache, and the expiry forces
 // periodic full-file revalidation when an audio file is opened.
 private static final long RECHECK_NS=5L*60L*1000000000L;
 private static final Map<String,HashStamp> digestCache=new HashMap<>();
 private static final class HashStamp {
  final long size,modified,checked;final String hash;
  HashStamp(File f,String value,long at){size=f.length();modified=f.lastModified();hash=value;checked=at;}
 }
 static synchronized String cachedSha256(File file)throws IOException{
  String id=file.getAbsolutePath();long now=System.nanoTime();
  HashStamp entry=digestCache.get(id);
  if(entry!=null&&file.isFile()&&entry.size==file.length()
     &&entry.modified==file.lastModified()&&now-entry.checked>=0
     &&now-entry.checked<RECHECK_NS)return entry.hash;
  String result=sha256(file);
  digestCache.put(id,new HashStamp(file,result,now));
  return result;
 }
 static synchronized void invalidate(File file){digestCache.remove(file.getAbsolutePath());}
 static boolean promote(File pending,File saved){
  if(valid(saved))return true;
  if(!valid(pending))return false;
  invalidate(saved);
  if(!saved.getParentFile().isDirectory()&&!saved.getParentFile().mkdirs())return false;
  if(saved.exists()&&!saved.delete())return false;
  // Both directories are under the same app-specific Music directory. Rename
  // atomically, so DownloadManager cleanup only knows the obsolete pending path.
  return pending.renameTo(saved)&&valid(saved);
 }
}
