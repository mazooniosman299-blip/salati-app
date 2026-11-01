package com.salati.prayer;
import java.io.*;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

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
 static boolean promote(File pending,File saved){
  if(valid(saved))return true;
  if(!valid(pending))return false;
  if(!saved.getParentFile().isDirectory()&&!saved.getParentFile().mkdirs())return false;
  if(saved.exists()&&!saved.delete())return false;
  // Both directories are under the same app-specific Music directory. Rename
  // atomically, so DownloadManager cleanup only knows the obsolete pending path.
  return pending.renameTo(saved)&&valid(saved);
 }
}
