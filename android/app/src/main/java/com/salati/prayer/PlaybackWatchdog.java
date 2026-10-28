package com.salati.prayer;
/** Detect lack of media-position progress, independent of recording silence or track length. */
final class PlaybackWatchdog {
 private final long timeout;private long position,lastProgress;private boolean observed;
 PlaybackWatchdog(long timeout){if(timeout<=0)throw new IllegalArgumentException("timeout");this.timeout=timeout;}
 void reset(){observed=false;}
 boolean stalled(long current,long now,boolean playing){
  if(!playing){reset();return false;}
  if(!observed||current!=position||now<lastProgress){observed=true;position=current;lastProgress=now;return false;}
  return now-lastProgress>=timeout;
 }
}
