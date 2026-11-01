package com.salati.prayer;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.os.SystemClock;
import android.view.Gravity;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.RemoteViews;

/** Debug-only real Android RemoteViews renderer, never included in release APK. */
public final class WidgetPreviewActivity extends Activity {
 private static int dp(Activity a,float value){return (int)(value*a.getResources().getDisplayMetrics().density+.5f);}
 @Override protected void onCreate(Bundle state){
  super.onCreate(state);
  getWindow().setStatusBarColor(Color.rgb(11,14,19));
  getWindow().setNavigationBarColor(Color.rgb(11,14,19));
  FrameLayout root=new FrameLayout(this);
  root.setBackgroundColor(Color.rgb(11,14,19));
  RemoteViews views=new RemoteViews(getPackageName(),R.layout.prayer_widget);
  views.setTextViewText(R.id.widget_location,"Mu... / مسقط");
  views.setTextViewText(R.id.widget_date,"1/11/2026");
  views.setTextViewText(R.id.widget_hijri,"هـ 1448/5/22");
  views.setTextViewText(R.id.widget_next_label,"الصلاة القادمة");
  views.setTextViewText(R.id.widget_next,"المغرب");
  views.setChronometerCountDown(R.id.widget_countdown,true);
  views.setChronometer(R.id.widget_countdown,SystemClock.elapsedRealtime()+6760000,null,true);
  int[] ids={R.id.widget_fajr,R.id.widget_sunrise,R.id.widget_dhuhr,R.id.widget_asr,R.id.widget_maghrib,R.id.widget_isha};
  String[] times={"4:55","6:13","11:55","3:08","5:33","6:44"};
  for(int i=0;i<ids.length;i++)views.setTextViewText(ids[i],times[i]);
  String active=getIntent().getStringExtra("prayer");
  if(active==null)active="maghrib";
  views.setTextViewText(R.id.widget_next,"asr".equals(active)?"العصر":"المغرب");
  PrayerWidget.applyUpcomingPrayerHighlight(views,active);
  View widget=views.apply(this,root);
  FrameLayout.LayoutParams p=new FrameLayout.LayoutParams(-1,dp(this,192),Gravity.TOP);
  p.leftMargin=dp(this,12);p.rightMargin=dp(this,12);p.topMargin=dp(this,72);
  root.addView(widget,p);
  setContentView(root);
 }
}
