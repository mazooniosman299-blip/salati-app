package com.salati.prayer;
public final class AlarmDeliveryPolicyTest {
 static void check(boolean value){if(!value)throw new AssertionError();}
 public static void main(String[] args){
  long at=1800000000000L;
  check(AlarmDeliveryPolicy.mayPlay(true,true,at,at));
  check(AlarmDeliveryPolicy.mayPlay(true,true,at,at+90001));
  check(AlarmDeliveryPolicy.mayPlay(true,true,at,at+300000));
  check(!AlarmDeliveryPolicy.mayPlay(true,true,at,at+300001));
  check(!AlarmDeliveryPolicy.mayPlay(true,true,at,at-1001));
  check(!AlarmDeliveryPolicy.mayPlay(false,true,at,at));
  check(!AlarmDeliveryPolicy.mayPlay(true,false,at,at));
  check(!AlarmDeliveryPolicy.mayPlay(true,true,0,0));
  System.out.println("PASS: on-time and briefly delayed wake-ups play; stale, early, disabled/obsolete and unauthorized alarms are rejected.");
 }
}
