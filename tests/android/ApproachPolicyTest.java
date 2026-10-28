package com.salati.prayer;
public final class ApproachPolicyTest {
 static void check(boolean yes,String label){if(!yes)throw new AssertionError(label);}
 public static void main(String[] args){long prayer=2000000;
  for(int lead:new int[]{5,10,15}){long at=ApproachPolicy.at(prayer,lead);check(at==prayer-lead*60000L,"Selected lead time");check(ApproachPolicy.mayPlay(true,true,at,prayer,at),"On-time delivery");check(ApproachPolicy.mayPlay(true,true,at,prayer,at+59999),"Brief OS delivery delay");check(!ApproachPolicy.mayPlay(true,true,at,prayer,at+60001),"Stale reminder rejected");check(!ApproachPolicy.mayPlay(false,true,at,prayer,at),"Changed/disabled settings reject old alarm");check(!ApproachPolicy.mayPlay(true,false,at,prayer,at),"Exact permission required");check(!ApproachPolicy.mayPlay(true,true,at,prayer,at-1001),"Early alarm rejected");check(!ApproachPolicy.mayPlay(true,true,at,prayer,prayer),"Never announce approach at actual adhan");}
  for(int bad:new int[]{-1,0,1,30,999})check(ApproachPolicy.minutes(bad)==5,"Invalid lead defaults to5");
  System.out.println("PASS:5/10/15-minute lead, bounded delivery, invalid/stale/early/disabled reminders, permission and actual-adhan boundary.");
 }
}
