package com.salati.prayer;
import android.content.*;import android.media.AudioManager;
/** Changes only the alarm stream, and restores it unless the user changed it meanwhile. */
final class AlarmVolumeSession {
 private static final String PREF="salati_alarm_volume";
 static void begin(Context context,boolean enabled,boolean automatic,float appVolume){
  if(!enabled||!automatic||appVolume<=0)return;
  AudioManager audio=context.getSystemService(AudioManager.class);if(audio==null||audio.isVolumeFixed())return;
  try{
   int before=audio.getStreamVolume(AudioManager.STREAM_ALARM),maximum=audio.getStreamMaxVolume(AudioManager.STREAM_ALARM);
   boolean silent=audio.getRingerMode()!=AudioManager.RINGER_MODE_NORMAL;
   int target=AlarmVolumePolicy.target(enabled,automatic,silent,before,maximum,appVolume);if(target==before)return;
   SharedPreferences prefs=context.getSharedPreferences(PREF,0);
   if(!prefs.edit().putInt("before",before).putInt("applied",target).commit())return;
   try{audio.setStreamVolume(AudioManager.STREAM_ALARM,target,0);}catch(RuntimeException error){prefs.edit().clear().commit();}
  }catch(RuntimeException ignored){}
 }
 static void restore(Context context){
  SharedPreferences prefs=context.getSharedPreferences(PREF,0);if(!prefs.contains("before"))return;
  int before=prefs.getInt("before",0),applied=prefs.getInt("applied",-1);
  AudioManager audio=context.getSystemService(AudioManager.class);if(audio==null)return;
  try{if(AlarmVolumePolicy.restore(audio.getStreamVolume(AudioManager.STREAM_ALARM),applied))audio.setStreamVolume(AudioManager.STREAM_ALARM,before,0);}catch(RuntimeException ignored){return;}
  prefs.edit().clear().commit();
 }
}
