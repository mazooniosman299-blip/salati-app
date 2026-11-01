package com.salati.prayer;
public final class AlarmDeliveryPolicyTest {
 static void check(boolean value){if(!value)throw new AssertionError();}
 public static void main(String[] args){
  long at=1800000000000L;
  check(AlarmDeliveryPolicy.mayPlay(true,true,at,at));
  check(AlarmDeliveryPolicy.mayPlay(true,false,at,at+300000));
  check(!AlarmDeliveryPolicy.mayPlay(true,false,at,at+300001));
  check(AlarmDeliveryPolicy.mayPlay(true,true,at,at+600000));
  check(AlarmDeliveryPolicy.mayPlay(true,true,at,at+900000));
  check(AlarmDeliveryPolicy.mayPlay(true,true,at,at+900001));
  check(AlarmDeliveryPolicy.mayPlay(true,true,at,at+1800000));
  check(!AlarmDeliveryPolicy.mayPlay(true,true,at,at+1800001));
  check(!AlarmDeliveryPolicy.mayPlay(false,true,at,at+1200000));
  check(!AlarmDeliveryPolicy.mayPlay(false,true,at,at+600000));
  check(AlarmDeliveryPolicy.preserveOnActivityResume(true,true,at,at+600000,false));
  check(!AlarmDeliveryPolicy.preserveOnActivityResume(true,true,at,at+600000,true));
  check(AlarmDeliveryPolicy.mayPlay(true,at,at));
  check(AlarmDeliveryPolicy.mayPlay(true,at,at+90001));
  check(AlarmDeliveryPolicy.mayPlay(true,at,at+300000));
  check(!AlarmDeliveryPolicy.mayPlay(true,at,at+300001));
  check(!AlarmDeliveryPolicy.mayPlay(true,at,at-1001));
  check(!AlarmDeliveryPolicy.mayPlay(false,at,at));
  check(!AlarmDeliveryPolicy.mayPlay(true,0,0));
  check(AlarmDeliveryPolicy.preserveOnActivityResume(true,at,at,false));
  check(AlarmDeliveryPolicy.preserveOnActivityResume(true,at,at+120000,false));
  check(AlarmDeliveryPolicy.preserveOnActivityResume(true,at,at+300000,false));
  check(!AlarmDeliveryPolicy.preserveOnActivityResume(true,at,at+300001,false));
  check(!AlarmDeliveryPolicy.preserveOnActivityResume(true,at,at-1,false));
  check(!AlarmDeliveryPolicy.preserveOnActivityResume(true,at,at+2000,true));
  check(!AlarmDeliveryPolicy.preserveOnActivityResume(false,at,at+2000,false));
  System.out.println("PASS: verified stored events play during short grace period even in inexact fallback; reject stale, early and duplicate deliveries.");
 }
}
