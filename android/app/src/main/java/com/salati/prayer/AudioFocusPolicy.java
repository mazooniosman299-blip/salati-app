package com.salati.prayer;

/** Android audio-focus values; independent of the framework for sequence tests. */
final class AudioFocusPolicy {
 boolean paused,ducked,stopped;
 void change(int focus){
  if(stopped)return;
  switch(focus){
   case 1:paused=false;ducked=false;break; // AUDIOFOCUS_GAIN
   case -3:ducked=true;break; // LOSS_TRANSIENT_CAN_DUCK: keep the current position playing.
   case -2:paused=true;ducked=false;break; // LOSS_TRANSIENT: retain buffered audio for resume.
   case -1:stopped=true;paused=true;ducked=false;break; // Permanent loss.
   default:break;
  }
 }
 float volume(float preferred){return preferred*(ducked?.25f:1f);}
}
