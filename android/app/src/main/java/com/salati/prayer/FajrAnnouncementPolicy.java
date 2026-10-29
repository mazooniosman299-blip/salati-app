package com.salati.prayer;
import android.app.NotificationManager;
/** Uses named SDK constants and the platform audio policy, never a DND bypass. */
final class FajrAnnouncementPolicy {
 static boolean canPlay(boolean notificationsAllowed,int filter,double volume){
  if(!notificationsAllowed||!Double.isFinite(volume)||volume<=0)return false;
  return filter==NotificationManager.INTERRUPTION_FILTER_ALL
   ||filter==NotificationManager.INTERRUPTION_FILTER_PRIORITY
   ||filter==NotificationManager.INTERRUPTION_FILTER_ALARMS;
 }
}
