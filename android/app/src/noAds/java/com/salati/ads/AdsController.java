package com.salati.ads;
import android.app.Activity;import android.widget.LinearLayout;
/** The normal build contains no advertising SDK and performs no ad requests. */
public final class AdsController {
 public AdsController(Activity activity,LinearLayout root,Runnable onStatus){}
 public void start(){} public void setContext(String tab,boolean audio){} public void setNativePlayback(boolean audio){}
 public void resume(){} public void pause(){} public void destroy(){} public void showPrivacyOptions(){}
 public String diagnostics(){return "{}";}
 public boolean enabled(){return false;} public boolean privacyRequired(){return false;}
}
