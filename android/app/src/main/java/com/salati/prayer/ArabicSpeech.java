package com.salati.prayer;

import android.content.Context;
import android.media.AudioAttributes;
import android.os.*;

/** Bounded local recordings. No installed speech engine or network is required. */
final class ArabicSpeech {
 static final String PREF="salati_announcement";
 private static ArabicSpeech owner;
 private final Context context;private final AudioAttributes attributes;private final Handler main=new Handler(Looper.getMainLooper());
 private PcmAudioPlayer player;private Runnable completion,timeout;private long generation;
 ArabicSpeech(Context context,AudioAttributes attributes){this.context=context.getApplicationContext();this.attributes=attributes;}
 static String asset(String text){
  if("الصلاة خير من النوم".equals(text))return "www/audio/reminders/fajr-phrase.mp3";
  String[] keys={"fajr","dhuhr","asr","maghrib","isha"};
  String[] names={"الفجر","الظهر","العصر","المغرب","العشاء"};
  for(int n=0;n<keys.length;n++)if(("اقتربت صلاة "+names[n]).equals(text))return "www/audio/reminders/approach-"+keys[n]+".mp3";
  return null;
 }
 void speak(String text,float volume,Runnable done){
  close();long ticket=generation;completion=done;owner=this;
  record(context,"loading");String path=asset(text);
  if(path==null||!Float.isFinite(volume)){finish(ticket,"error");return;}
  if(volume<=0){finish(ticket,"muted");return;}
  timeout=()->finish(ticket,"error");main.postDelayed(timeout,8000);
  try{
   PcmAudioPlayer current=new PcmAudioPlayer(context);player=current;
   current.play(path,attributes,Math.max(0,Math.min(1,volume)),new PcmAudioPlayer.Listener(){
    public void complete(){main.post(()->finish(ticket,"finished"));}
    public void error(Exception error){main.post(()->finish(ticket,"error"));}
   });
   if(ticket==generation&&owner==this)record(context,"playing");
  }catch(RuntimeException error){finish(ticket,"error");}
 }
 static void recordCancellation(Context context){if(owner==null)record(context,"cancelled");}
 static void record(Context context,String status){
  try{context.getSharedPreferences(PREF,0).edit().putString("status",status).apply();}catch(RuntimeException ignored){}
  try{MainActivity.notifyAnnouncement(status);}catch(RuntimeException ignored){}
 }
 private void finish(long ticket,String status){if(ticket!=generation)return;Runnable done=completion;boolean owns=owner==this;close();if(owns)record(context,status);if(done!=null)done.run();}
 void close(){if(owner==this)owner=null;generation++;completion=null;if(timeout!=null)main.removeCallbacks(timeout);timeout=null;PcmAudioPlayer old=player;player=null;if(old!=null)old.stop();}
}
