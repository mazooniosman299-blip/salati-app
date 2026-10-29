package com.salati.prayer;
import android.content.*;
/** Upgrade tombstone: old request5103 deliveries can only cancel their legacy alarm. */
public final class ApproachReceiver extends BroadcastReceiver {
 @Override public void onReceive(Context c,Intent i){PrayerSchedule.cancelLegacyApproach(c);}
}
