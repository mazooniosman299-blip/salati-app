package com.salati.prayer;
public final class PlaybackWatchdogTest {
 static void check(boolean condition,String message){if(!condition)throw new AssertionError(message);}
 public static void main(String[] args){
  PlaybackWatchdog p=new PlaybackWatchdog(45000);
  check(!p.stalled(1000,0,true),"Start has grace period");
  check(!p.stalled(1000,44999,true),"Short buffering allowed");
  check(p.stalled(1000,45000,true),"Non-progressing playback must time out");
  p.reset();check(!p.stalled(1000,0,true),"Reset starts a new session");check(!p.stalled(1200,44000,true),"Real progress resets deadline");check(!p.stalled(1200,45000,true),"Old deadline cannot stop progressing audio");
  check(!p.stalled(1200,90000,false),"Paused playback never times out");check(!p.stalled(1200,150000,true),"Resume has full grace period");check(p.stalled(1200,195000,true),"Resume can still detect stall");
  p.reset();check(!p.stalled(1000,200000,true),"New track");check(!p.stalled(0,244000,true),"Seek/repeat resets deadline");
  System.out.println("PASS: Quran stalled-playback deadline, normal buffering, progress, pause/resume, seek/repeat and session reset.");
 }
}
