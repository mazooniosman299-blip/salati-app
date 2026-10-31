package com.salati.prayer;
/** Do not discard a briefly delayed wake-up; never replay an old prayer hours later. */
public final class AlarmDeliveryPolicy {
 private AlarmDeliveryPolicy() {}
 public static boolean mayPlay(boolean valid, boolean exactAllowed, long scheduled, long now) {
  return valid && exactAllowed && scheduled > 0 && now >= scheduled - 1000 && now - scheduled <= 300000;
 }
 /** A queued, slightly overdue alarm must not be cancelled when the Activity resumes.
  * Boot/package/time changes still reschedule through RestoreReceiver. */
 public static boolean preserveOnActivityResume(boolean valid,boolean exactAllowed,
     long scheduled,long now,boolean alreadyDelivered){
  return !alreadyDelivered && now >= scheduled && mayPlay(valid,exactAllowed,scheduled,now);
 }
}
