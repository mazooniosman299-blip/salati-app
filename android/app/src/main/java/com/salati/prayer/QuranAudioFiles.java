package com.salati.prayer;
import java.io.*;

final class QuranAudioFiles {
 static boolean valid(File file){
  if(!file.isFile()||file.length()<128)return false;
  try(InputStream input=new FileInputStream(file)){int a=input.read(),b=input.read(),c=input.read();return a==73&&b==68&&c==51||a==255&&(b&224)==224;}catch(IOException error){return false;}
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
