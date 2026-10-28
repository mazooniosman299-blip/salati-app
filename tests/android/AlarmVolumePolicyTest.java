package com.salati.prayer;
public final class AlarmVolumePolicyTest {
 static void check(boolean condition,String message){if(!condition)throw new AssertionError(message);}
 public static void main(String[] args){
  check(AlarmVolumePolicy.target(true,true,true,0,10,.8f)==6,"silent phone with muted alarm becomes audible");
  check(AlarmVolumePolicy.target(true,true,true,2,10,.8f)==6,"quiet alarm is raised in silent/vibrate mode");
  check(AlarmVolumePolicy.target(true,true,true,8,10,.8f)==8,"already loud alarm is preserved");
  check(AlarmVolumePolicy.target(true,true,false,3,10,.8f)==3,"normal nonzero alarm volume is preserved");
  check(AlarmVolumePolicy.target(true,true,false,0,10,.8f)==6,"zero alarm volume is raised when feature is enabled");
  check(AlarmVolumePolicy.target(false,true,true,0,10,.8f)==0,"disabled option changes nothing");
  check(AlarmVolumePolicy.target(true,false,true,0,10,.8f)==0,"manual preview changes nothing");
  check(AlarmVolumePolicy.target(true,true,true,0,10,0)==0,"explicit app mute is respected");
  check(AlarmVolumePolicy.target(true,true,true,0,0,.8f)==0,"fixed/zero maximum cannot be raised");
  check(AlarmVolumePolicy.restore(6,6),"unchanged temporary level is restored");
  check(!AlarmVolumePolicy.restore(4,6),"manual volume changes during adhan are retained");
  System.out.println("PASS: silent/normal modes, zero and high alarm volume, manual previews, disabled setting, app mute and restoration policy.");
 }
}
