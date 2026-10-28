package com.salati.prayer;
/** The reminder is a separate, short delivery window and never replaces the actual adhan. */
final class ApproachPolicy {
 static int minutes(int value){return value==5||value==10||value==15?value:5;}
 static long at(long prayerTime,int lead){return prayerTime-(long)minutes(lead)*60000;}
 static boolean mayPlay(boolean valid,boolean exactAllowed,long scheduled,long prayerTime,long now){return valid&&exactAllowed&&scheduled>0&&prayerTime>now&&now>=scheduled-1000&&now-scheduled<=60000;}
}
