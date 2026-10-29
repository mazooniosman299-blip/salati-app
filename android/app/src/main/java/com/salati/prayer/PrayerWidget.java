package com.salati.prayer;
import android.app.*;import android.appwidget.*;import android.content.*;import android.graphics.Color;import android.os.Bundle;import android.widget.RemoteViews;import org.json.*;import java.text.*;import java.util.*;
public final class PrayerWidget extends AppWidgetProvider{
 static final String ACTION="com.salati.prayer.WIDGET_REFRESH";
 static final String ACTION_RECOVER="com.salati.prayer.WIDGET_RECOVER";
 static final long RECOVERY_INTERVAL=15*60*1000L;
 static String clock(long time,String zone){SimpleDateFormat f=new SimpleDateFormat("h:mm",Locale.US);f.setTimeZone(TimeZone.getTimeZone(zone));return f.format(new Date(time));}
 static String day(long now,String zone){SimpleDateFormat f=new SimpleDateFormat("yyyy-MM-dd",Locale.US);f.setTimeZone(TimeZone.getTimeZone(zone));return f.format(new Date(now));}
 static void updateAll(Context c){AppWidgetManager m=AppWidgetManager.getInstance(c);int[] ids=m.getAppWidgetIds(new ComponentName(c,PrayerWidget.class));for(int id:ids)update(c,m,id);if(ids.length>0)schedule(c);}
 static void update(Context c,AppWidgetManager manager,int id){RemoteViews views=new RemoteViews(c.getPackageName(),R.layout.prayer_widget);JSONObject config=PrayerSchedule.config(c);String zone=config.optString("zone",TimeZone.getDefault().getID());long now=System.currentTimeMillis();String today=day(now,zone);JSONArray days=config.optJSONArray("days");JSONObject found=null;JSONObject nextDay=null;if(days!=null)for(int i=0;i<days.length();i++){JSONObject d=days.optJSONObject(i);if(d==null)continue;if(today.equals(d.optString("date")))found=d;else if(d.optString("date").compareTo(today)>0&&(nextDay==null||d.optString("date").compareTo(nextDay.optString("date"))<0))nextDay=d;}

 views.setTextViewText(R.id.widget_location,config.optString("name","حدّد موقعك"));java.text.DateFormat localDate=new java.text.SimpleDateFormat("EEEE، d MMMM yyyy",new java.util.Locale("ar"));localDate.setTimeZone(TimeZone.getTimeZone(zone));views.setTextViewText(R.id.widget_date,localDate.format(new Date(now)));android.icu.text.DateFormat hijri=android.icu.text.DateFormat.getDateInstance(android.icu.text.DateFormat.LONG,new android.icu.util.ULocale("ar@calendar=islamic"));hijri.setTimeZone(android.icu.util.TimeZone.getTimeZone(zone));views.setTextViewText(R.id.widget_hijri,hijri.format(new Date(now)));
 boolean daylight=WidgetAppearancePolicy.isDay(now,zone,found==null?0:found.optLong("sunrise"),found==null?0:found.optLong("maghrib"));views.setImageViewResource(R.id.widget_scenery,R.drawable.widget_reference_mosque);views.setImageViewResource(R.id.widget_overlay,daylight?R.drawable.widget_overlay_day:R.drawable.widget_overlay_night);int primary=Color.WHITE,secondary=Color.WHITE;int[] primaryIds={R.id.widget_next,R.id.widget_countdown,R.id.widget_fajr,R.id.widget_sunrise,R.id.widget_dhuhr,R.id.widget_asr,R.id.widget_maghrib,R.id.widget_isha};for(int textId:primaryIds)views.setTextColor(textId,primary);int[] secondaryIds={R.id.widget_next_label,R.id.widget_label_fajr,R.id.widget_label_sunrise,R.id.widget_label_dhuhr,R.id.widget_label_asr,R.id.widget_label_maghrib,R.id.widget_label_isha};for(int textId:secondaryIds)views.setTextColor(textId,secondary);int[] captionIds={R.id.widget_next_label,R.id.widget_label_sunrise};for(int textId:captionIds)views.setTextColor(textId,Color.parseColor("#FFFFFF"));for(int dateId:new int[]{R.id.widget_location,R.id.widget_date,R.id.widget_hijri})views.setTextColor(dateId,Color.WHITE);Bundle size=manager.getAppWidgetOptions(id);int height=size.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_HEIGHT,110);boolean compact=height<220;float dateTextSize=dateTextSize(c,size,config.optString("name","حدّد موقعك"),localDate.format(new Date(now)),hijri.format(new Date(now)));views.setTextViewTextSize(R.id.widget_location,android.util.TypedValue.COMPLEX_UNIT_SP,17f);for(int dateId:new int[]{R.id.widget_date,R.id.widget_hijri})views.setTextViewTextSize(dateId,android.util.TypedValue.COMPLEX_UNIT_SP,dateTextSize);int inset=Math.round((compact?6:10)*c.getResources().getDisplayMetrics().density);views.setViewPadding(R.id.widget_card,inset,inset,inset,inset);views.setViewVisibility(R.id.widget_hijri,android.view.View.VISIBLE);views.setViewVisibility(R.id.widget_next_label,android.view.View.VISIBLE);
 String[] keys={"fajr","sunrise","dhuhr","asr","maghrib","isha"};int[] valueIds={R.id.widget_fajr,R.id.widget_sunrise,R.id.widget_dhuhr,R.id.widget_asr,R.id.widget_maghrib,R.id.widget_isha};for(int i=0;i<6;i++)views.setTextViewText(valueIds[i],found!=null&&found.optLong(keys[i])>0?clock(found.optLong(keys[i]),zone):"—");String upcomingKey="";String next="—";long nextTime=0;if(found!=null){for(String key:keys)if(!"sunrise".equals(key)&&found.optLong(key)>now){upcomingKey=key;next=AdhanService.prayerName(key);nextTime=found.optLong(key);break;}if(upcomingKey.isEmpty()&&nextDay!=null){upcomingKey="fajr";next="الفجر";nextTime=nextDay.optLong("fajr");}}views.setViewVisibility(R.id.widget_countdown_row,nextTime>now?android.view.View.VISIBLE:android.view.View.GONE);views.setChronometerCountDown(R.id.widget_countdown,true);views.setChronometer(R.id.widget_countdown,android.os.SystemClock.elapsedRealtime()+Math.max(0,nextTime-now),null,nextTime>now);views.setTextViewText(R.id.widget_next,next);int nextIcon="dhuhr".equals(upcomingKey)?R.drawable.ic_widget_dhuhr:"asr".equals(upcomingKey)?R.drawable.ic_widget_asr:"maghrib".equals(upcomingKey)?R.drawable.ic_widget_maghrib:"isha".equals(upcomingKey)?R.drawable.ic_widget_isha:R.drawable.ic_widget_sunrise;views.setImageViewResource(R.id.widget_next_icon,nextIcon);views.setViewVisibility(R.id.widget_next_icon,android.view.View.GONE);views.setTextViewText(R.id.widget_next_label,upcomingKey.isEmpty()?"افتح صلاتي لتحديث المواقيت":"الصلاة القادمة");int[] cellIds={R.id.widget_cell_fajr,R.id.widget_cell_sunrise,R.id.widget_cell_dhuhr,R.id.widget_cell_asr,R.id.widget_cell_maghrib,R.id.widget_cell_isha};for(int n=0;n<keys.length;n++)views.setInt(cellIds[n],"setBackgroundResource",keys[n].equals(upcomingKey)?R.drawable.widget_prayer_active:0);
 PendingIntent open=PendingIntent.getActivity(c,90,new Intent(c,MainActivity.class),PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);views.setOnClickPendingIntent(R.id.widget_root,open);manager.updateAppWidget(id,views);}
 // Preserve the large city label and fit smaller dates using actual font metrics.
 // Date wrapping and fallback-font spacing remain matched to the TextViews.
 static float dateTextSize(Context c,Bundle options,String city,String gregorian,String hijri){
  android.util.DisplayMetrics metrics=c.getResources().getDisplayMetrics();
  int height=options.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_HEIGHT,170),width=options.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_WIDTH,280);
  int inset=height<220?6:10;
  int available=Math.max(1,Math.round((height-2*inset-54-8)*metrics.density));
  int textWidth=Math.max(1,(int)Math.floor((width-2*inset)*1.1f/2.7f*metrics.density));
  android.text.TextPaint paint=new android.text.TextPaint(android.graphics.Paint.ANTI_ALIAS_FLAG);
  paint.setTypeface(android.graphics.Typeface.create("sans-serif-medium",android.graphics.Typeface.BOLD));
  paint.setTextSize(android.util.TypedValue.applyDimension(android.util.TypedValue.COMPLEX_UNIT_SP,17f,metrics));
  int cityWidth=Math.max(1,textWidth-Math.round(23*metrics.density));
  int cityHeight=Math.max(Math.round(22*metrics.density),placeLayout(city,paint,cityWidth,true).getHeight());
  paint.setTypeface(android.graphics.Typeface.create("sans-serif-medium",android.graphics.Typeface.NORMAL));
  for(float sp=12;sp>=8;sp-=.5f){
   paint.setTextSize(android.util.TypedValue.applyDimension(android.util.TypedValue.COMPLEX_UNIT_SP,sp,metrics));
   int textHeight=cityHeight+Math.round(7*metrics.density);
   for(String text:new String[]{gregorian,hijri}){
    android.text.StaticLayout layout=placeLayout(text,paint,textWidth,false);
    textHeight+=layout.getHeight();
   }
   if(textHeight<=available)return sp;
  }
  return 8;
 }
 // StaticLayout.Builder defaults to SIMPLE, matching the explicit TextView breakStrategy.
 static android.text.StaticLayout placeLayout(String text,android.text.TextPaint paint,int width,boolean singleLine){
  android.text.StaticLayout.Builder builder=android.text.StaticLayout.Builder.obtain(text,0,text.length(),paint,width).setIncludePad(false).setTextDirection(android.text.TextDirectionHeuristics.FIRSTSTRONG_RTL).setHyphenationFrequency(android.text.Layout.HYPHENATION_FREQUENCY_NONE);
  if(android.os.Build.VERSION.SDK_INT>=28)builder.setUseLineSpacingFromFallbacks(true);
  if(singleLine)builder.setMaxLines(1).setEllipsize(android.text.TextUtils.TruncateAt.END).setEllipsizedWidth(width);
  return builder.build();
 }
 static PendingIntent refreshIntent(Context c,int requestCode,String action){
  return PendingIntent.getBroadcast(c,requestCode,new Intent(c,PrayerWidget.class).setAction(action),PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
 }
 static void schedule(Context c){
  AlarmManager alarm=c.getSystemService(AlarmManager.class);
  if(alarm==null)return;
  JSONObject config=PrayerSchedule.config(c);
  String zone=config.optString("zone",TimeZone.getDefault().getID());
  long now=System.currentTimeMillis();
  JSONArray days=config.optJSONArray("days");
  JSONObject current=null;
  ArrayList<Long> events=new ArrayList<>();
  if(days!=null)for(int n=0;n<days.length();n++){
   JSONObject d=days.optJSONObject(n);if(d==null)continue;
   if(day(now,zone).equals(d.optString("date")))current=d;
   for(String key:new String[]{"fajr","sunrise","dhuhr","asr","maghrib","isha"})events.add(d.optLong(key));
  }
  long[] prayerTimes=new long[events.size()];for(int n=0;n<events.size();n++)prayerTimes[n]=events.get(n);
  long when=WidgetAppearancePolicy.nextRefresh(now,zone,current==null?0:current.optLong("sunrise"),current==null?0:current.optLong("maghrib"),prayerTimes);
  PendingIntent boundary=refreshIntent(c,91,ACTION);
  try{
   if(PrayerSchedule.exactAlarmsAllowed(c))alarm.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,when,boundary);
   else alarm.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,when,boundary);
  }catch(SecurityException denied){
   // Permission can be revoked between the capability check and scheduling.
   alarm.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,when,boundary);
  }
  // Independent recovery survives a late/missed boundary delivery. Each delivery
  // recomputes appearance and next prayer from the current instant, never equality.
  alarm.setInexactRepeating(AlarmManager.RTC_WAKEUP,now+RECOVERY_INTERVAL,RECOVERY_INTERVAL,refreshIntent(c,92,ACTION_RECOVER));
 }
 @Override public void onUpdate(Context c,AppWidgetManager m,int[] ids){updateAll(c);}
 @Override public void onReceive(Context c,Intent i){super.onReceive(c,i);if(ACTION.equals(i.getAction())||ACTION_RECOVER.equals(i.getAction())||Intent.ACTION_DATE_CHANGED.equals(i.getAction()))updateAll(c);}
 @Override public void onAppWidgetOptionsChanged(Context c,AppWidgetManager m,int id,Bundle options){updateAll(c);}
 @Override public void onDisabled(Context c){
  AlarmManager alarm=c.getSystemService(AlarmManager.class);
  for(int code:new int[]{91,92}){
   PendingIntent pending=refreshIntent(c,code,code==91?ACTION:ACTION_RECOVER);
   if(alarm!=null)alarm.cancel(pending);pending.cancel();
  }
 }
}
