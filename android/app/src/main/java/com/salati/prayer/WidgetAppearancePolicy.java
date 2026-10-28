package com.salati.prayer;

import java.util.Calendar;
import java.util.TimeZone;

/** The widget follows the saved location's sun, independently of device theme. */
public final class WidgetAppearancePolicy {
 private WidgetAppearancePolicy() {}
 private static Calendar local(long now,String zone){Calendar c=Calendar.getInstance(TimeZone.getTimeZone(zone));c.setTimeInMillis(now);return c;}
 private static boolean sameDay(long a,long b,String zone){Calendar x=local(a,zone),y=local(b,zone);return x.get(Calendar.ERA)==y.get(Calendar.ERA)&&x.get(Calendar.YEAR)==y.get(Calendar.YEAR)&&x.get(Calendar.DAY_OF_YEAR)==y.get(Calendar.DAY_OF_YEAR);}
 private static boolean valid(long now,String zone,long sunrise,long maghrib){return sunrise>0&&maghrib>sunrise&&sameDay(now,sunrise,zone)&&sameDay(now,maghrib,zone);}
 public static boolean isDay(long now,String zone,long sunrise,long maghrib){if(valid(now,zone,sunrise,maghrib))return now>=sunrise&&now<maghrib;int hour=local(now,zone).get(Calendar.HOUR_OF_DAY);return hour>=6&&hour<18;}
 public static long nextTransition(long now,String zone,long sunrise,long maghrib){
  if(valid(now,zone,sunrise,maghrib)){if(now<sunrise)return sunrise;if(now<maghrib)return maghrib;}
  Calendar next=local(now,zone);int hour=next.get(Calendar.HOUR_OF_DAY);if(hour>=18)next.add(Calendar.DAY_OF_MONTH,1);next.set(Calendar.HOUR_OF_DAY,hour<6||hour>=18?6:18);next.set(Calendar.MINUTE,0);next.set(Calendar.SECOND,0);next.set(Calendar.MILLISECOND,0);return next.getTimeInMillis();
 }
}
