package com.salati.prayer;
/** Reject obsolete, early or stale alarms without depending on the *current*
 * exact-alarm permission. Android may deliver an already scheduled inexact
 * wake-up after that permission is revoked. The saved event is validated by
 * PrayerSchedule.valid before we start any audio. */
public final class AlarmDeliveryPolicy {
 private AlarmDeliveryPolicy() {}
 public static boolean mayPlay(boolean valid,long scheduled,long now){
  return valid && scheduled>0 && now>=scheduled-1000 && now-scheduled<=300000;
 }
 /** Never cancel a due PendingIntent during Activity resume. */
 public static boolean preserveOnActivityResume(boolean valid,
      long scheduled,long now,boolean alreadyDelivered){
  return !alreadyDelivered && now >= scheduled && mayPlay(valid,scheduled,now);
 }
}
