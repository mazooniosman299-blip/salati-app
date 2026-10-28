package com.salati.prayer;
/** Do not discard a briefly delayed wake-up; never replay an old prayer hours later. */
public final class AlarmDeliveryPolicy {
 private AlarmDeliveryPolicy() {}
 public static boolean mayPlay(boolean valid, boolean exactAllowed, long scheduled, long now) {
  return valid && exactAllowed && scheduled > 0 && now >= scheduled - 1000 && now - scheduled <= 300000;
 }
}
