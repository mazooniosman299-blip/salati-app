package com.salati.prayer;

import android.app.DownloadManager;
import android.content.*;
import android.database.Cursor;
import android.net.Uri;
import android.media.MediaMetadataRetriever;
import android.os.Environment;
import android.webkit.WebResourceResponse;
import org.json.*;
import java.io.*;
import java.util.*;
import java.util.regex.*;

final class QuranDownloads {
 private static final String PREFS="salati_quran_downloads_v1";
 private static final String PREFIX="/quran-offline/";
 private static final String ORIGIN="https://appassets.androidplatform.net";
 private static String server(String reciter){
  switch(reciter){case "shatri":return "https://server11.mp3quran.net/shatri/";case "yasser":return "https://server11.mp3quran.net/yasser/";case "qatami":return "https://server6.mp3quran.net/qtm/";case "sudais":return "https://server11.mp3quran.net/sds/";case "afasy":return "https://server8.mp3quran.net/afs/";default:throw new IllegalArgumentException("reciter");}
 }
 private static String name(String reciter){switch(reciter){case "shatri":return "أبو بكر الشاطري";case "yasser":return "ياسر الدوسري";case "sudais":return "عبد الرحمن السديس";case "afasy":return "مشاري العفاسي";default:return "ناصر القطامي";}}
 private static String key(String reciter,int surah){server(reciter);if(surah<1||surah>114)throw new IllegalArgumentException("surah");return reciter+"-"+surah;}
 private static String filename(int surah){return String.format(Locale.ROOT,"%03d.mp3",surah);}
 private static SharedPreferences prefs(Context context){return context.getSharedPreferences(PREFS,Context.MODE_PRIVATE);}
 private static DownloadManager manager(Context context){DownloadManager manager=context.getSystemService(DownloadManager.class);if(manager==null)throw new IllegalStateException("downloads");return manager;}
 static File savedFile(Context context,String reciter,int surah){return file(context,reciter,surah);}
 private static File file(Context context,String reciter,int surah){
  key(reciter,surah);File base=context.getExternalFilesDir(Environment.DIRECTORY_MUSIC);
  if(base==null)throw new IllegalStateException("storage");
  return new File(new File(new File(base,"quran"),reciter),filename(surah));
 }
 private static File pendingFile(Context context,String reciter,int surah){
  key(reciter,surah);File base=context.getExternalFilesDir(Environment.DIRECTORY_MUSIC);
  if(base==null)throw new IllegalStateException("storage");
  return new File(new File(new File(base,"quran-pending"),reciter),filename(surah));
 }
 private static Map<Long,long[]> progress(DownloadManager manager,Collection<Long> ids){
  Map<Long,long[]> rows=new HashMap<>();if(ids.isEmpty())return rows;
  long[] values=new long[ids.size()];int i=0;for(long id:ids)values[i++]=id;
  try(Cursor cursor=manager.query(new DownloadManager.Query().setFilterById(values))){
   if(cursor==null)return rows;
   while(cursor.moveToNext())rows.put(cursor.getLong(cursor.getColumnIndexOrThrow(DownloadManager.COLUMN_ID)),new long[]{cursor.getLong(cursor.getColumnIndexOrThrow(DownloadManager.COLUMN_STATUS)),cursor.getLong(cursor.getColumnIndexOrThrow(DownloadManager.COLUMN_BYTES_DOWNLOADED_SO_FAR)),cursor.getLong(cursor.getColumnIndexOrThrow(DownloadManager.COLUMN_TOTAL_SIZE_BYTES)),cursor.getLong(cursor.getColumnIndexOrThrow(DownloadManager.COLUMN_REASON))});
  }
  return rows;
 }
 /** Decoder-level validation: a fake ID3 header or a truncated response
  * is not a playable Quran recording. No network or media playback occurs. */
 private static boolean decodesAsAudio(File file){
  if(!QuranAudioFiles.valid(file))return false;
  MediaMetadataRetriever reader=new MediaMetadataRetriever();
  try{
   reader.setDataSource(file.getAbsolutePath());
   String mime=reader.extractMetadata(MediaMetadataRetriever.METADATA_KEY_MIMETYPE);
   String duration=reader.extractMetadata(MediaMetadataRetriever.METADATA_KEY_DURATION);
   return mime!=null&&mime.startsWith("audio/")&&duration!=null&&Long.parseLong(duration)>500;
  }catch(RuntimeException error){return false;}
  finally{try{reader.release();}catch(RuntimeException ignored){}}
 }
 private static boolean ready(Context context,String reciter,int surah,SharedPreferences preferences,Map<Long,long[]> rows){
  String key=key(reciter,surah);long id=preferences.getLong(key,0);long[] row=rows.get(id);
  File saved=file(context,reciter,surah);
  String pinnedHash=preferences.getString(key+"-sha256","");
  // Existing saved recordings are checked against a digest across ALL bytes,
  // not against their extension, size, or only the opening MP3 header.
  boolean complete=QuranAudioFiles.valid(saved);
  if(complete&&!pinnedHash.isEmpty()){
   try{complete=pinnedHash.equals(QuranAudioFiles.sha256(saved));}
   catch(IOException error){complete=false;}
  }
  if(!complete&&saved.exists()){
   if(!saved.delete())return false;
   preferences.edit().remove(key+"-done").remove(key+"-sha256").apply();
   pinnedHash="";
  }
  if(!complete&&row!=null&&row[0]==DownloadManager.STATUS_SUCCESSFUL){
   File pending=pendingFile(context,reciter,surah);
   // DownloadManager can report a successful transfer whose saved bytes are
   // unexpectedly short. Never promote in that case.
   boolean matchedSize=row[2]<=0||pending.length()==row[2];
   complete=matchedSize&&QuranAudioFiles.promote(pending,saved);
  }
  if(!complete)return false;
  if(row!=null&&row[0]==DownloadManager.STATUS_SUCCESSFUL&&row[2]>0&&saved.length()!=row[2]){
   if(saved.exists())saved.delete();
   preferences.edit().remove(key+"-done").remove(key+"-sha256").apply();
   return false;
  }
  try{
   String actual=QuranAudioFiles.sha256(saved);
   if(!pinnedHash.isEmpty()&&!pinnedHash.equals(actual)){
    if(saved.exists())saved.delete();
    preferences.edit().remove(key+"-done").remove(key+"-sha256").apply();
    return false;
   }
   // Existing files from older versions get a decoder check on first upgrade.
   // The digest then becomes their permanent content-integrity reference.
   if(pinnedHash.isEmpty()&&!decodesAsAudio(saved)){
    if(saved.exists())saved.delete();
    preferences.edit().remove(key+"-done").remove(key+"-sha256").apply();
    return false;
   }
   if(pinnedHash.isEmpty()||!preferences.getBoolean(key+"-done",false)){
    if(!preferences.edit().putString(key+"-sha256",actual).putBoolean(key+"-done",true).commit())return false;
   }
  }catch(IOException error){return false;}
  if(row!=null&&row[0]==DownloadManager.STATUS_SUCCESSFUL)manager(context).remove(id);
  return true;
 }
 static synchronized void finish(Context context,long id){
  try{
   SharedPreferences preferences=prefs(context);
   for(Map.Entry<String,?> entry:preferences.getAll().entrySet()){
    if(!(entry.getValue() instanceof Long)||((Long)entry.getValue()).longValue()!=id)continue;
    Matcher match=Pattern.compile("^(shatri|yasser|qatami|sudais|afasy)-(\\d+)$").matcher(entry.getKey());
    if(match.matches())ready(context,match.group(1),Integer.parseInt(match.group(2)),preferences,progress(manager(context),Collections.singletonList(id)));
   }
  }catch(Exception ignored){}
 }
 static synchronized String status(Context context,String reciter){
  try{
   server(reciter);SharedPreferences preferences=prefs(context);DownloadManager manager=manager(context);List<Long> ids=new ArrayList<>();
   for(int surah=1;surah<=114;surah++){long id=preferences.getLong(key(reciter,surah),0);if(id>0)ids.add(id);}
   Map<Long,long[]> rows=progress(manager,ids);JSONArray entries=new JSONArray();
   for(int surah=1;surah<=114;surah++){
    String key=key(reciter,surah);long id=preferences.getLong(key,0);if(id==0)continue;
    long[] row=rows.get(id);JSONObject entry=new JSONObject().put("surah",surah);
    if(ready(context,reciter,surah,preferences,rows))entry.put("state","saved").put("bytes",file(context,reciter,surah).length());
    else if(row!=null&&(row[0]==DownloadManager.STATUS_PENDING||row[0]==DownloadManager.STATUS_PAUSED||row[0]==DownloadManager.STATUS_RUNNING))entry.put("state",row[0]==DownloadManager.STATUS_RUNNING?"downloading":"queued").put("bytes",Math.max(0,row[1])).put("total",Math.max(0,row[2]));
    else entry.put("state","failed").put("error",row!=null&&row[3]==DownloadManager.ERROR_INSUFFICIENT_SPACE?"space":"network");
    entries.put(entry);
   }
   return new JSONObject().put("entries",entries).toString();
  }catch(Exception error){return "{\"error\":\"storage\"}";}
 }
 static synchronized String download(Context context,String reciter,int selected){
  try{
   server(reciter);if(selected<0||selected>114)throw new IllegalArgumentException("surah");
   SharedPreferences preferences=prefs(context);DownloadManager manager=manager(context);
   List<Long> ids=new ArrayList<>();for(int surah=1;surah<=114;surah++){long id=preferences.getLong(key(reciter,surah),0);if(id>0)ids.add(id);}
   Map<Long,long[]> rows=progress(manager,ids);
   for(int surah=selected==0?1:selected;surah<=(selected==0?114:selected);surah++){
    String key=key(reciter,surah);long previous=preferences.getLong(key,0);long[] row=rows.get(previous);
    if(ready(context,reciter,surah,preferences,rows)||row!=null&&(row[0]==DownloadManager.STATUS_PENDING||row[0]==DownloadManager.STATUS_PAUSED||row[0]==DownloadManager.STATUS_RUNNING))continue;
    if(previous>0)manager.remove(previous);
    File destination=pendingFile(context,reciter,surah);if(destination.exists()&&!destination.delete())throw new IOException("storage");
    if(!destination.getParentFile().isDirectory()&&!destination.getParentFile().mkdirs())throw new IOException("storage");
    DownloadManager.Request request=new DownloadManager.Request(Uri.parse(server(reciter)+filename(surah)))
     .setTitle("صلاتي · "+name(reciter)+" · "+surah).setDescription("تنزيل السورة للاستماع بدون إنترنت")
     .setMimeType("audio/mpeg").setAllowedOverMetered(true).setAllowedOverRoaming(false)
     .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
     .setDestinationInExternalFilesDir(context,Environment.DIRECTORY_MUSIC,"quran-pending/"+reciter+"/"+filename(surah));
    long id=manager.enqueue(request);preferences.edit().putLong(key,id).putBoolean(key+"-done",false).remove(key+"-sha256").apply();
   }
   return "{\"ok\":true}";
  }catch(Exception error){return "{\"error\":\"storage\"}";}
 }
 private static String remove(Context context,String reciter,int selected,boolean keepSaved){
  try{
   server(reciter);if(selected<0||selected>114)throw new IllegalArgumentException("surah");
   SharedPreferences preferences=prefs(context);DownloadManager manager=manager(context);List<Long> ids=new ArrayList<>();
   for(int surah=1;surah<=114;surah++){long id=preferences.getLong(key(reciter,surah),0);if(id>0)ids.add(id);}
   Map<Long,long[]> rows=progress(manager,ids);SharedPreferences.Editor edit=preferences.edit();List<Long> remove=new ArrayList<>();
   for(int surah=selected==0?1:selected;surah<=(selected==0?114:selected);surah++){
    if(keepSaved&&ready(context,reciter,surah,preferences,rows))continue;
    String key=key(reciter,surah);long id=preferences.getLong(key,0);if(id>0)remove.add(id);
    edit.remove(key).remove(key+"-done").remove(key+"-sha256");
   }
   if(!remove.isEmpty()){long[] values=new long[remove.size()];for(int i=0;i<values.length;i++)values[i]=remove.get(i);manager.remove(values);}
   edit.apply();
   for(int surah=selected==0?1:selected;surah<=(selected==0?114:selected);surah++)if(!keepSaved||!ready(context,reciter,surah,preferences,rows)){
    File destination=file(context,reciter,surah);if(destination.exists()&&!destination.delete())throw new IOException("storage");
    File pending=pendingFile(context,reciter,surah);if(pending.exists()&&!pending.delete())throw new IOException("storage");
   }
   return "{\"ok\":true}";
  }catch(Exception error){return "{\"error\":\"storage\"}";}
 }
 static synchronized String cancel(Context context,String reciter){return remove(context,reciter,0,true);}
 static synchronized String delete(Context context,String reciter,int surah){return remove(context,reciter,surah,false);}
 static synchronized String localUrl(Context context,String reciter,int surah){
  try{
   SharedPreferences preferences=prefs(context);long id=preferences.getLong(key(reciter,surah),0);
   Map<Long,long[]> rows=preferences.getBoolean(key(reciter,surah)+"-done",false)?Collections.emptyMap():progress(manager(context),id>0?Collections.singletonList(id):Collections.emptyList());
   return ready(context,reciter,surah,preferences,rows)?ORIGIN+PREFIX+reciter+"/"+filename(surah):"";
  }catch(Exception error){return "";}
 }
 static WebResourceResponse response(Context context,Uri uri,Map<String,String> requestHeaders){
  try{
   Matcher match=Pattern.compile("^/quran-offline/(shatri|yasser|qatami|sudais|afasy)/(\\d{3})\\.mp3$").matcher(uri.getPath()==null?"":uri.getPath());
   if(!match.matches())return MainActivity.error();String reciter=match.group(1);int surah=Integer.parseInt(match.group(2));
   if(localUrl(context,reciter,surah).isEmpty())return MainActivity.error();
   File audio=file(context,reciter,surah);long size=audio.length();String header=null;
   for(Map.Entry<String,String> entry:requestHeaders.entrySet())if("range".equalsIgnoreCase(entry.getKey()))header=entry.getValue();
   Map<String,String> headers=new HashMap<>();headers.put("Accept-Ranges","bytes");headers.put("Access-Control-Allow-Origin",ORIGIN);headers.put("Cache-Control","no-store");
   QuranAudioRange range;
   try{range=QuranAudioRange.parse(header,size);}catch(IllegalArgumentException error){headers.put("Content-Range","bytes */"+size);return new WebResourceResponse("audio/mpeg",null,416,"Range Not Satisfiable",headers,new ByteArrayInputStream(new byte[0]));}
   headers.put("Content-Length",String.valueOf(range.length()));
   if(range.partial)headers.put("Content-Range","bytes "+range.start+"-"+range.end+"/"+size);
   return new WebResourceResponse("audio/mpeg",null,range.partial?206:200,range.partial?"Partial Content":"OK",headers,range.open(audio));
  }catch(Exception error){return MainActivity.error();}
 }
}
