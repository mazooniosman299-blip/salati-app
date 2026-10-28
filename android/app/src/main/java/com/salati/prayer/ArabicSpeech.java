package com.salati.prayer;

import android.content.Context;
import android.media.AudioAttributes;
import android.os.*;
import android.speech.tts.*;
import java.util.*;

/** Bounded, cancellable speech using an installed Arabic voice; never requests a network voice. */
final class ArabicSpeech {
 static final String PREF="salati_speech";
 private final Context context;private final AudioAttributes attributes;private final Handler main=new Handler(Looper.getMainLooper());
 private TextToSpeech engine;private Runnable completion,timeout;private long generation;
 ArabicSpeech(Context context,AudioAttributes attributes){this.context=context.getApplicationContext();this.attributes=attributes;}
 void speak(String text,float volume,Runnable done){
  close();long ticket=generation;completion=done;timeout=()->finish(ticket,"timeout");main.postDelayed(timeout,8000);
  try{engine=new TextToSpeech(context,status->main.post(()->{
   if(ticket!=generation)return;
   try{
    if(status!=TextToSpeech.SUCCESS||engine==null){finish(ticket,"unavailable");return;}
    Set<Voice> voices=engine.getVoices();Voice selected=voices==null?null:voices.stream().filter(v->"ar".equals(v.getLocale().getLanguage())&&!v.isNetworkConnectionRequired()&&!v.getFeatures().contains(TextToSpeech.Engine.KEY_FEATURE_NOT_INSTALLED)).max(Comparator.comparingInt(Voice::getQuality).thenComparingInt(v->-v.getLatency())).orElse(null);
    if(selected==null||engine.setVoice(selected)!=TextToSpeech.SUCCESS){finish(ticket,"missing_arabic");return;}
    engine.setAudioAttributes(attributes);engine.setSpeechRate(.92f);
    engine.setOnUtteranceProgressListener(new UtteranceProgressListener(){public void onStart(String id){}public void onDone(String id){main.post(()->finish(ticket,"ready"));}public void onError(String id){main.post(()->finish(ticket,"error"));}});
    record("ready");Bundle params=new Bundle();params.putFloat(TextToSpeech.Engine.KEY_PARAM_VOLUME,Math.max(0,Math.min(1,volume)));
    if(engine.speak(text,TextToSpeech.QUEUE_FLUSH,params,"salati-"+ticket)!=TextToSpeech.SUCCESS)finish(ticket,"error");
   }catch(RuntimeException error){finish(ticket,"error");}
  }));}catch(RuntimeException error){finish(ticket,"unavailable");}
 }
 private void record(String status){try{context.getSharedPreferences(PREF,0).edit().putString("status",status).putBoolean("ready","ready".equals(status)).apply();MainActivity activity=MainActivity.current.get();if(activity!=null)activity.main.post(activity::notifyStatus);}catch(RuntimeException ignored){}}
 private void finish(long ticket,String status){if(ticket!=generation)return;Runnable done=completion;record(status);close();if(done!=null)done.run();}
 void close(){generation++;completion=null;if(timeout!=null)main.removeCallbacks(timeout);timeout=null;TextToSpeech old=engine;engine=null;if(old!=null){try{old.stop();}catch(RuntimeException ignored){}try{old.shutdown();}catch(RuntimeException ignored){}}}
}
