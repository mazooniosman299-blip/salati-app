package com.salati.prayer;
public final class AudioFocusPolicyTest {
 static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
 public static void main(String[] args){
  AudioFocusPolicy p=new AudioFocusPolicy();p.change(-3);check(!p.stopped&&!p.paused&&p.volume(.8f)==.2f,"notification ducks without stopping");
  p.change(-3);check(p.volume(.8f)==.2f,"repeated notifications do not compound volume reduction");p.change(1);check(!p.paused&&!p.ducked&&p.volume(.8f)==.8f,"gain restores preferred volume");
  p.change(-2);check(p.paused&&!p.stopped,"temporary interruption preserves playback");p.change(-3);check(p.paused,"nested notification must not resume a paused call");p.change(1);check(!p.paused&&!p.stopped&&!p.ducked,"temporary interruption resumes on gain");
  p.change(-3);check(p.volume(.4f)==.1f,"live preference changes respect ducking");p.change(1);check(p.volume(.4f)==.4f,"gain restores updated preference");
  p.change(-1);p.change(1);check(p.stopped&&p.paused,"permanent loss must not auto-restart");
  System.out.println("PASS: notification duck/restore, repeated and nested interruptions, pause/resume, live volume and permanent focus loss.");
 }
}
