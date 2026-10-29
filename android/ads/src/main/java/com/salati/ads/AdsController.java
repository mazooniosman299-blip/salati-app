package com.salati.ads;

import android.app.Activity;
import android.graphics.Color;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.widget.LinearLayout;
import com.google.android.gms.ads.*;
import com.google.android.ump.*;

/** A failed ad integration is disabled for this session; devotional features remain available. */
public final class AdsController {
 private final Activity activity;
 private final LinearLayout root, container;
 private final Runnable onStatus;
 private final Handler main = new Handler(Looper.getMainLooper());
 private final AdInitialization initialization = new AdInitialization();
 private ConsentInformation consent;
 private AdView banner;
 private String tab = "";
 private boolean webAudio, nativeAudio, foreground, started, initializing, initialized, loaded, loading, destroyed;
 private volatile boolean disabled, privacyRequired;
 private boolean consentBusy;
 private long lastAttempt;
 private int bannerWidth;
 private final Runnable retry = () -> guard(() -> {
  if (!foreground || !"times".equals(tab) || webAudio || nativeAudio || consentBusy) return;
  if (consent != null && !consent.canRequestAds()) started = false;
  startInternal(); update();
 });
 private void retryLater() { main.removeCallbacks(retry); if (alive()) main.postDelayed(retry, 60000); }
 private void diagnostic(String stage, int code, String message) {
  Log.w("SalatiAds", stage + ": " + code + " " + message);
  try { activity.getSharedPreferences("salati_ads_diagnostics",0).edit().putString("stage",stage).putInt("code",code).putString("message",message).putLong("time",System.currentTimeMillis()).apply(); } catch (RuntimeException ignored) {}
  onStatus.run();
 }
 private final Runnable initializationTimeout = () -> fail(new IllegalStateException("Ad initialization timed out"));

 public AdsController(Activity activity, LinearLayout root, Runnable onStatus) {
  this.activity = activity; this.root = root; this.onStatus = onStatus;
  // Do not initialize UMP while MainActivity is still constructing the WebView.
  container = new LinearLayout(activity);
  container.setId(View.generateViewId());
  container.setContentDescription("إعلان / Advertisement");
  container.setOrientation(LinearLayout.VERTICAL);
  container.setGravity(Gravity.CENTER_HORIZONTAL);
  container.setBackgroundColor(Color.rgb(11, 14, 19));
  container.setPadding(0, dp(8), 0, 0);
  container.setVisibility(View.GONE);
  root.addView(container, new LinearLayout.LayoutParams(-1, -2));
  root.addOnLayoutChangeListener((v,l,t,r,b,ol,ot,or,ob) -> guard(() -> {
   if (r-l != or-ol && banner != null && widthDp() != bannerWidth) { destroyBanner(); update(); }
  }));
 }
 private int dp(int value) { return Math.round(value * activity.getResources().getDisplayMetrics().density); }
 private int widthDp() {
  int px = root.getWidth() - root.getPaddingLeft() - root.getPaddingRight();
  if (px <= 0) px = activity.getResources().getDisplayMetrics().widthPixels;
  return (int)(px / activity.getResources().getDisplayMetrics().density);
 }
 private boolean alive() { return !destroyed && !disabled && !activity.isFinishing() && !activity.isDestroyed(); }
 private void guard(Runnable action) {
  if (!alive()) return;
  try { action.run(); } catch (RuntimeException | LinkageError error) { fail(error); }
 }
 private void fail(Throwable error) {
  if (Looper.myLooper() != Looper.getMainLooper()) { main.post(() -> fail(error)); return; }
  if (destroyed || disabled) return;
  disabled = true; privacyRequired = false; consentBusy = false;
  initialization.cancel(); main.removeCallbacks(initializationTimeout); main.removeCallbacks(retry);
  container.setVisibility(View.GONE);
  // Local-only diagnostic: no device identifiers or network upload.
  Log.e("SalatiAds", "Advertising disabled after SDK failure", error);
  try { activity.getSharedPreferences("salati_ads_diagnostics", 0).edit()
    .putString("lastError", Log.getStackTraceString(error)).apply(); } catch (RuntimeException ignored) {}
  try { destroyBanner(); } catch (RuntimeException | LinkageError ignored) {}
  onStatus.run();
 }
 public String diagnostics() {
  android.content.SharedPreferences prefs=activity.getSharedPreferences("salati_ads_diagnostics",0);
  org.json.JSONObject result=new org.json.JSONObject();try{result.put("stage",disabled?"disabled":prefs.getString("stage","waiting"));result.put("code",prefs.getInt("code",-1));result.put("message",prefs.getString("message",""));result.put("loaded",loaded);result.put("production",!BuildConfig.TEST_ADS);}catch(org.json.JSONException ignored){}return result.toString();
 }
 public boolean enabled() { return !disabled; }
 public boolean privacyRequired() { return privacyRequired; }
 public void start() { guard(this::startInternal); }
 private void startInternal() {
  if (started || nativeAudio || webAudio || !foreground || !"times".equals(tab)) return;
  started = true; consentBusy = true;diagnostic("consent",0,"Checking consent");
  consent = UserMessagingPlatform.getConsentInformation(activity.getApplicationContext());
  consent.requestConsentInfoUpdate(activity, new ConsentRequestParameters.Builder().build(),
   () -> guard(() -> UserMessagingPlatform.loadAndShowConsentFormIfRequired(activity,
    error -> guard(() -> { consentBusy = false; if(error!=null){diagnostic("consent_form",error.getErrorCode(),error.getMessage());retryLater();} refreshPrivacy(); update(); }))),
   error -> guard(() -> { consentBusy = false; diagnostic("consent_update",error.getErrorCode(),error.getMessage());retryLater();refreshPrivacy(); update(); }));
  refreshPrivacy(); update();
 }
 private void refreshPrivacy() {
  privacyRequired = consent != null && consent.getPrivacyOptionsRequirementStatus() == ConsentInformation.PrivacyOptionsRequirementStatus.REQUIRED;
  onStatus.run();
 }
 private boolean eligible() {
  return alive() && !consentBusy && consent != null
    && AdVisibility.mayRequest(tab, webAudio || nativeAudio, foreground, consent.canRequestAds());
 }
 public void setContext(String tab, boolean audio) { guard(() -> { this.tab = tab; webAudio = audio; startInternal(); update();if(foreground&&"times".equals(tab)&&!audio&&consent!=null&&!consentBusy&&!consent.canRequestAds())retryLater(); }); }
 public void setNativePlayback(boolean audio) { guard(() -> { nativeAudio = audio; startInternal(); update(); }); }
 public void resume() { guard(() -> { foreground = true; startInternal(); update(); if(consent!=null&&!consent.canRequestAds())retryLater(); }); }
 public void pause() { guard(() -> { foreground = false; main.removeCallbacks(retry);update(); }); }
 private void update() {
  if (!alive()) return;
  if (!eligible()) { container.setVisibility(View.GONE); if (banner != null) banner.pause(); return; }
  if (!initialized) {
   if (initializing) return;
   initializing = true;diagnostic("initializing",0,"Initializing Google Mobile Ads");
   main.removeCallbacks(initializationTimeout);
   main.postDelayed(initializationTimeout, 45000);
   MobileAds.setRequestConfiguration(new RequestConfiguration.Builder().setMaxAdContentRating(RequestConfiguration.MAX_AD_CONTENT_RATING_G).build());
   initialization.start(task -> new Thread(task, "salati-ad-init").start(), activity::runOnUiThread,
    complete -> MobileAds.initialize(activity.getApplicationContext(), status -> complete.run()),
    () -> { if (alive()) { MobileAds.setAppMuted(true); MobileAds.setAppVolume(0f); } },
    () -> guard(() -> { main.removeCallbacks(initializationTimeout); initialized = true; initializing = false; update(); }), this::fail);
   return;
  }
  if (banner == null) {
   int width = widthDp(); if (width < 200) return;
   bannerWidth = width; banner = new AdView(activity);
   banner.setAdUnitId(BuildConfig.BANNER_ID);
   banner.setAdSize(AdSize.getCurrentOrientationAnchoredAdaptiveBannerAdSize(activity, width));
   container.addView(banner, new LinearLayout.LayoutParams(-2, -2));
   final AdView requestView = banner;
   banner.setAdListener(new AdListener() {
    @Override public void onAdLoaded() { guard(() -> { if (banner == requestView) { loaded = true; loading = false; main.removeCallbacks(retry);diagnostic("loaded",0,"Banner loaded");update(); } }); }
    @Override public void onAdFailedToLoad(LoadAdError error) { guard(() -> { if (banner == requestView) { loaded = false; loading = false; container.setVisibility(View.GONE);diagnostic("banner_load",error.getCode(),error.getMessage());retryLater(); } }); }
   });
  }
  if (loaded) { banner.resume(); container.setVisibility(View.VISIBLE); }
  else if (!loading && (lastAttempt == 0 || SystemClock.elapsedRealtime() - lastAttempt >= 60000)) {
   loading = true; lastAttempt = SystemClock.elapsedRealtime(); diagnostic("loading",0,"Requesting banner");banner.loadAd(new AdRequest.Builder().build());
  } else if (!loaded && !loading) {retryLater();}

 }
 public void showPrivacyOptions() { guard(() -> {
  if (!privacyRequired || consentBusy) return;
  consentBusy = true; container.setVisibility(View.GONE); if (banner != null) banner.pause();
  UserMessagingPlatform.showPrivacyOptionsForm(activity, error -> guard(() -> {
   consentBusy = false; destroyBanner(); refreshPrivacy(); update();
  }));
 }); }
 private void destroyBanner() {
  AdView old = banner; banner = null; loaded = false; loading = false; lastAttempt = 0;
  container.setVisibility(View.GONE);
  if (old != null) { container.removeView(old); old.destroy(); }
 }
 public void destroy() {
  destroyed = true; initialization.cancel(); main.removeCallbacks(initializationTimeout); main.removeCallbacks(retry);
  try { destroyBanner(); } catch (RuntimeException | LinkageError error) { Log.w("SalatiAds", "Ad cleanup failed", error); }
 }
}
