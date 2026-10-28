package com.salati.ads;
public final class AdVisibilityTest {
 public static void main(String[] args){
  int count=0;for(String tab:new String[]{"times","mushaf","qibla","settings","dhikr","dialog","setup","background",""})for(boolean audio:new boolean[]{false,true})for(boolean foreground:new boolean[]{false,true})for(boolean consent:new boolean[]{false,true})for(boolean loaded:new boolean[]{false,true}){
   boolean allowed=tab.equals("times")&&!audio&&foreground&&consent;
   if(AdVisibility.mayRequest(tab,audio,foreground,consent)!=allowed||AdVisibility.mayShow(tab,audio,foreground,consent,loaded)!=(allowed&&loaded))throw new AssertionError(tab);count++;
  }
  System.out.println("PASS: "+count+" banner visibility/request cases cover Quran, qibla, settings, dialogs, setup, background, audio and consent.");
 }
}
