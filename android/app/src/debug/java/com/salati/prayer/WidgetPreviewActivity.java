package com.salati.prayer;
import android.app.Activity;
import android.appwidget.AppWidgetManager;
import android.graphics.Color;
import android.os.Bundle;
import android.os.SystemClock;
import android.view.Gravity;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.RemoteViews;

/** Debug-only render of the actual widget RemoteViews; never packaged in release. */
public final class WidgetPreviewActivity extends Activity {
 @Override public void onCreate(Bundle state){
  super.onCreate(state);
  getWindow().setStatusBarColor(Color.rgb(7,11,16));
  getWindow().setNavigationBarColor(Color.rgb(7,11,16));
  FrameLayout stage=new FrameLayout(this);
  stage.setBackgroundColor(Color.rgb(9,15,23));
  setContentView(stage);
  RemoteViews views=new RemoteViews(getPackageName(),R.layout.prayer_widget);
  views.setImageViewResource(R.id.widget_scenery,R.drawable.widget_reference_mosque);
  views.setImageViewResource(R.id.widget_overlay,R.drawable.widget_overlay_night);
  views.setTextViewText(R.id.widget_location,"Mu... / مسقط");
  views.setTextViewText(R.id.widget_date,"1/11/2026");
  views.setTextViewText(R.id.widget_hijri,"هـ 1448/5/22");
  views.setTextViewText(R.id.widget_next_label,"الصلاة القادمة");
  views.setTextViewText(R.id.widget_next,"المغرب");
  views.setChronometerCountDown(R.id.widget_countdown,true);
  views.setChronometer(R.id.widget_countdown,SystemClock.elapsedRealtime()+6760000,null,true);
  String[] names={"fajr","sunrise","dhuhr","asr","maghrib","isha"};
  String[] times={"4:55","6:13","11:55","3:08","5:33","6:44"};
  int[] ids={R.id.widget_fajr,R.id.widget_sunrise,R.id.widget_dhuhr,R.id.widget_asr,R.id.widget_maghrib,R.id.widget_isha};
  int active=getIntent().getIntExtra("active",4); // 4 = maghrib, 2 = dhuhr
  for(int i=0;i<ids.length;i++){
    views.setTextViewText(ids[i],times[i]);
    views.setInt(ids[i],"setBackgroundResource",i==active?R.drawable.widget_prayer_active:0);
  }
  View widget=views.apply(this,stage);
  int dpWidth=(int)(getResources().getDisplayMetrics().widthPixels/getResources().getDisplayMetrics().density);
  float d=getResources().getDisplayMetrics().density;
  FrameLayout.LayoutParams frame=new FrameLayout.LayoutParams(-1,Math.round(205*d),Gravity.TOP);
  frame.leftMargin=Math.round(10*d);
  frame.rightMargin=Math.round(10*d);
  frame.topMargin=Math.round(30*d);
  stage.addView(widget,frame);
 }
}
