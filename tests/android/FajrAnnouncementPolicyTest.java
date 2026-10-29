package com.salati.prayer;
import android.app.NotificationManager;
public final class FajrAnnouncementPolicyTest {
 static void check(boolean yes,String name){if(!yes)throw new AssertionError(name);}
 public static void main(String[] args){
  for(int allowed:new int[]{NotificationManager.INTERRUPTION_FILTER_ALL,NotificationManager.INTERRUPTION_FILTER_PRIORITY,NotificationManager.INTERRUPTION_FILTER_ALARMS})check(FajrAnnouncementPolicy.canPlay(true,allowed,.35),"OS handles allowed interruption modes");
  for(int denied:new int[]{NotificationManager.INTERRUPTION_FILTER_UNKNOWN,NotificationManager.INTERRUPTION_FILTER_NONE,-1,99})check(!FajrAnnouncementPolicy.canPlay(true,denied,1),"Unknown/total silence cannot start phrase");
  check(!FajrAnnouncementPolicy.canPlay(false,1,1),"Notification permission denied");
  for(double volume:new double[]{0,-1,Double.NaN,Double.POSITIVE_INFINITY,Double.NEGATIVE_INFINITY})check(!FajrAnnouncementPolicy.canPlay(true,1,volume),"Muted/invalid user volume");
  check(FajrAnnouncementPolicy.canPlay(true,1,.01),"Low positive user volume stays allowed");
  System.out.println("PASS: Fajr notification/DND modes and finite user-volume boundaries; platform routing never bypassed.");
 }
}
