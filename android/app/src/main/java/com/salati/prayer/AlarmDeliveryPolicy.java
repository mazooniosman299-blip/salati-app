package com.salati.prayer;
/** Reject obsolete, early or stale alarms without depending on the *current*
 * exact-alarm permission. Android may deliver an already scheduled inexact
 * wake-up after that permission is revoked. The saved event is validated by
 * PrayerSchedule.valid before we start any audio. */
public final class AlarmDeliveryPolicy {
 private AlarmDeliveryPolicy() {}
 // Exact alarms must be prompt. An inexact Doze fallback can be delivered
 // later by Android; allow up to 15 minutes, never beyond the next prayer.
 static final long EXACT_GRACE_MS=5*60*1000L;
 static final long INEXACT_GRACE_MS=15*60*1000L;
 static boolean mayPlay(boolean valid,boolean inexact,long scheduled,long now){
  return valid&&scheduled>0&&now>=scheduled-1000
    &&now-scheduled<=(inexact?INEXACT_GRACE_MS:EXACT_GRACE_MS);
 }
 static boolean preserveOnActivityResume(boolean valid,boolean inexact,
     long scheduled,long now,boolean alreadyDelivered){
  return !alreadyDelivered&&now>=scheduled&&mayPlay(valid,inexact,scheduled,now);
 }

 public static boolean mayPlay(boolean valid,long scheduled,long now){
  return valid && scheduled>0 && now>=scheduled-1000 && now-scheduled<=300000;
 }
 /** Never cancel a due PendingIntent during Activity resume. */
 public static boolean preserveOnActivityResume(boolean valid,
      long scheduled,long now,boolean alreadyDelivered){
  return !alreadyDelivered && now >= scheduled && mayPlay(valid,scheduled,now);
 }
}
