package com.salati.prayer;
import android.app.DownloadManager;
import android.content.*;

public final class QuranDownloadReceiver extends BroadcastReceiver {
 @Override public void onReceive(Context context,Intent intent){
  if(!DownloadManager.ACTION_DOWNLOAD_COMPLETE.equals(intent.getAction()))return;
  long id=intent.getLongExtra(DownloadManager.EXTRA_DOWNLOAD_ID,-1);if(id<0)return;
  PendingResult pending=goAsync();Context app=context.getApplicationContext();
  new Thread(()->{try{QuranDownloads.finish(app,id);}finally{pending.finish();}},"salati-save-quran").start();
 }
}
