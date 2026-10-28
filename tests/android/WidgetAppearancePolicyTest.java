package com.salati.prayer;
import java.time.ZonedDateTime;
public final class WidgetAppearancePolicyTest {
 static long at(String date){return ZonedDateTime.parse(date).toInstant().toEpochMilli();}
 static void check(boolean actual,boolean expected,String message){if(actual!=expected)throw new AssertionError(message);}
 public static void main(String[] args){
  String zone="Asia/Riyadh";
  long rise=at("2026-10-28T06:12:00+03:00[Asia/Riyadh]"),set=at("2026-10-28T17:21:00+03:00[Asia/Riyadh]");
  check(WidgetAppearancePolicy.isDay(rise-1,zone,rise,set),false,"before sunrise is night");
  check(WidgetAppearancePolicy.isDay(rise,zone,rise,set),true,"sunrise starts day immediately");
  check(WidgetAppearancePolicy.isDay(set-1,zone,rise,set),true,"day lasts until maghrib");
  check(WidgetAppearancePolicy.isDay(set,zone,rise,set),false,"maghrib starts night immediately");
  long late=at("2026-10-28T23:30:00Z[UTC]");
  check(WidgetAppearancePolicy.isDay(late,"Pacific/Auckland",0,0),true,"fallback uses configured zone, not device/UTC");
  check(WidgetAppearancePolicy.isDay(at("2026-10-29T07:00:00+03:00[Asia/Riyadh]"),zone,rise,set),true,"stale dates use local fallback");
  check(WidgetAppearancePolicy.isDay(at("2026-10-28T07:00:00+03:00[Asia/Riyadh]"),zone,set,rise),true,"reversed boundaries use fallback");
  check(WidgetAppearancePolicy.isDay(at("2026-10-28T19:00:00+03:00[Asia/Riyadh]"),zone,0,0),false,"missing timings use night fallback");
  long now=at("2026-10-28T05:00:00+03:00[Asia/Riyadh]");
  if(WidgetAppearancePolicy.nextTransition(now,zone,rise,set)!=rise)throw new AssertionError("next transition is sunrise");
  if(WidgetAppearancePolicy.nextTransition(rise,zone,rise,set)!=set)throw new AssertionError("next transition is maghrib");
  if(WidgetAppearancePolicy.nextTransition(now,zone,0,0)!=at("2026-10-28T06:00:00+03:00[Asia/Riyadh]"))throw new AssertionError("fallback schedules sunrise without polling");
  long dst=at("2026-11-01T01:30:00-04:00[America/New_York]");
  if(WidgetAppearancePolicy.nextTransition(dst,"America/New_York",0,0)!=at("2026-11-01T06:00:00-05:00[America/New_York]"))throw new AssertionError("fallback respects DST change");
  System.out.println("PASS: widget sunrise/maghrib boundaries, configured zones, stale/missing/malformed timings and DST transitions.");
 }
}
