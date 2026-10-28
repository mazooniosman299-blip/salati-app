package com.salati.prayer;
final class AlarmVolumePolicy {
 static int target(boolean enabled,boolean automatic,boolean silent,int current,int maximum,float appVolume){
  if(!enabled||!automatic||appVolume<=0||maximum<=0||current<0||(!silent&&current>0))return current;
  return Math.max(current,Math.min(maximum,Math.max(1,(int)Math.ceil(maximum*.6))));
 }
 static boolean restore(int current,int applied){return current==applied;}
}
