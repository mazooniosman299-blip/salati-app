package com.salati.ads;
/** No ad views on devotional screens, during audio, without consent, or off screen. */
public final class AdVisibility {
 private AdVisibility() {}
 public static boolean mayRequest(String tab,boolean audio,boolean foreground,boolean consent){return "times".equals(tab)&&!audio&&foreground&&consent;}
 public static boolean mayShow(String tab,boolean audio,boolean foreground,boolean consent,boolean loaded){return loaded&&mayRequest(tab,audio,foreground,consent);}
}
