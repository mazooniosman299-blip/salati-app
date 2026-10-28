package com.salati.prayer;

import android.content.Context;
import android.content.res.AssetFileDescriptor;
import android.media.*;
import android.os.*;
import java.nio.ByteBuffer;

/** Dedicated, buffered PCM output. No WebView playback or compressed-audio offload. */
final class PcmAudioPlayer {
 interface Listener { void complete(); void error(Exception error); }
 private final Context context;
 private final Handler main=new Handler(Looper.getMainLooper());
 private volatile boolean stopped,paused,playbackStarted;
 private final Object playbackLock=new Object();
 private volatile AudioTrack output;private volatile float level;
 PcmAudioPlayer(Context context){this.context=context.getApplicationContext();}
 void play(String asset,AudioAttributes attributes,float volume,Listener listener){
  level=volume;new Thread(()->decode(asset,attributes,volume,listener),"salati-pcm-audio").start();
 }
 void setVolume(float value){level=value;AudioTrack track=output;if(track!=null)try{track.setVolume(value);}catch(IllegalStateException ignored){}}
 void setPaused(boolean value){synchronized(playbackLock){if(stopped)return;paused=value;AudioTrack track=output;if(track!=null)try{if(value)track.pause();else if(playbackStarted)track.play();}catch(IllegalStateException ignored){}}}
 void stop(){synchronized(playbackLock){stopped=true;paused=true;AudioTrack track=output;if(track!=null)try{track.pause();}catch(IllegalStateException ignored){}}}
 private void startOutput(){synchronized(playbackLock){playbackStarted=true;if(!stopped&&!paused&&output!=null)output.play();}}
 private boolean waitForResume()throws InterruptedException{boolean waited=false;while(paused&&!stopped){waited=true;Thread.sleep(10);}return waited;}
 private MediaCodec decoder(MediaFormat format)throws Exception{
  String mime=format.getString(MediaFormat.KEY_MIME);
  // Prefer Android's software decoder; output is always buffered PCM through AudioTrack.
  for(MediaCodecInfo info:new MediaCodecList(MediaCodecList.REGULAR_CODECS).getCodecInfos()){
   if(info.isEncoder())continue;
   String name=info.getName();boolean software=Build.VERSION.SDK_INT>=29?info.isSoftwareOnly():(name.startsWith("OMX.google.")||name.startsWith("c2.android."));
   if(!software)continue;
   for(String type:info.getSupportedTypes())if(type.equalsIgnoreCase(mime))try{return MediaCodec.createByCodecName(name);}catch(Exception ignored){}
  }
  return MediaCodec.createDecoderByType(mime);
 }
 private void decode(String asset,AudioAttributes attributes,float volume,Listener listener){
  try{android.os.Process.setThreadPriority(android.os.Process.THREAD_PRIORITY_AUDIO);}catch(RuntimeException ignored){}
  MediaExtractor extractor=null;MediaCodec codec=null;AudioTrack track=null;Exception failure=null;
  try{
   extractor=new MediaExtractor();
   try(AssetFileDescriptor fd=context.getAssets().openFd(asset)){extractor.setDataSource(fd.getFileDescriptor(),fd.getStartOffset(),fd.getLength());}
   int stream=-1;for(int i=0;i<extractor.getTrackCount();i++)if(extractor.getTrackFormat(i).getString(MediaFormat.KEY_MIME).startsWith("audio/")){stream=i;break;}
   if(stream<0)throw new IllegalArgumentException("No audio track");extractor.selectTrack(stream);
   MediaFormat format=extractor.getTrackFormat(stream);format.setInteger(MediaFormat.KEY_PCM_ENCODING,AudioFormat.ENCODING_PCM_16BIT);
   codec=decoder(format);codec.configure(format,null,null,0);codec.start();
   MediaCodec.BufferInfo info=new MediaCodec.BufferInfo();boolean inputDone=false,outputDone=false,started=false;long bytesWritten=0;int frameBytes=0,prefillBytes=0;long lastProgress=SystemClock.elapsedRealtime();
   while(!stopped&&!outputDone){
    if(waitForResume())lastProgress=SystemClock.elapsedRealtime();if(stopped)break;
    if(SystemClock.elapsedRealtime()-lastProgress>15000)throw new IllegalStateException("Audio decoder stalled");
    if(!inputDone){int index=codec.dequeueInputBuffer(10000);if(index>=0){ByteBuffer input=codec.getInputBuffer(index);if(input==null)throw new IllegalStateException("Missing decoder input");input.clear();int size=extractor.readSampleData(input,0);if(size<0){codec.queueInputBuffer(index,0,0,0,MediaCodec.BUFFER_FLAG_END_OF_STREAM);inputDone=true;}else{codec.queueInputBuffer(index,0,size,extractor.getSampleTime(),0);extractor.advance();}}}
    int index=codec.dequeueOutputBuffer(info,10000);
    if(index==MediaCodec.INFO_OUTPUT_FORMAT_CHANGED){
     MediaFormat pcm=codec.getOutputFormat();int rate=pcm.getInteger(MediaFormat.KEY_SAMPLE_RATE),channels=pcm.getInteger(MediaFormat.KEY_CHANNEL_COUNT);
     if(channels!=1&&channels!=2)throw new IllegalArgumentException("Unsupported channel layout");
     int encoding=pcm.containsKey(MediaFormat.KEY_PCM_ENCODING)?pcm.getInteger(MediaFormat.KEY_PCM_ENCODING):AudioFormat.ENCODING_PCM_16BIT;
     if(encoding!=AudioFormat.ENCODING_PCM_16BIT&&encoding!=AudioFormat.ENCODING_PCM_FLOAT)throw new IllegalArgumentException("Unsupported PCM encoding");
     if(track!=null)throw new IllegalStateException("Unexpected audio format change");
     int mask=channels==1?AudioFormat.CHANNEL_OUT_MONO:AudioFormat.CHANNEL_OUT_STEREO;frameBytes=channels*(encoding==AudioFormat.ENCODING_PCM_FLOAT?4:2);
     int minimum=AudioTrack.getMinBufferSize(rate,mask,encoding);if(minimum<=0)throw new IllegalStateException("No PCM output");
     // Half a second of capacity; prefill a quarter second before starting playback.
     int capacity=Math.max(minimum*4,rate*frameBytes/2);capacity=((capacity+frameBytes-1)/frameBytes)*frameBytes;prefillBytes=rate*frameBytes/4;
     track=new AudioTrack.Builder().setAudioAttributes(attributes).setAudioFormat(new AudioFormat.Builder().setSampleRate(rate).setEncoding(encoding).setChannelMask(mask).build()).setPerformanceMode(AudioTrack.PERFORMANCE_MODE_NONE).setTransferMode(AudioTrack.MODE_STREAM).setBufferSizeInBytes(capacity).build();
     if(track.getState()!=AudioTrack.STATE_INITIALIZED)throw new IllegalStateException("PCM output initialization failed");
     output=track;track.setVolume(level);
    }else if(index>=0){
     lastProgress=SystemClock.elapsedRealtime();
     try{if(info.size>0&&(info.flags&MediaCodec.BUFFER_FLAG_CODEC_CONFIG)==0){
      if(track==null)throw new IllegalStateException("Missing output format");ByteBuffer pcm=codec.getOutputBuffer(index);pcm.position(info.offset);pcm.limit(info.offset+info.size);
      while(pcm.hasRemaining()&&!stopped){if(waitForResume())lastProgress=SystemClock.elapsedRealtime();if(stopped)break;int written=track.write(pcm,pcm.remaining(),AudioTrack.WRITE_NON_BLOCKING);if(written<0)throw new IllegalStateException("PCM write failed: "+written);bytesWritten+=written;if(written>0)lastProgress=SystemClock.elapsedRealtime();else if(SystemClock.elapsedRealtime()-lastProgress>15000)throw new IllegalStateException("PCM output stalled");if(!started&&bytesWritten>=prefillBytes){startOutput();started=true;}if(written==0)Thread.sleep(4);}
     }outputDone=(info.flags&MediaCodec.BUFFER_FLAG_END_OF_STREAM)!=0;}finally{codec.releaseOutputBuffer(index,false);}
    }
   }
   if(!stopped&&bytesWritten==0)throw new IllegalStateException("Empty decoded audio");
   if(!stopped&&track!=null&&bytesWritten>0){if(!started)startOutput();long frames=bytesWritten/frameBytes,lastHead=-1;lastProgress=SystemClock.elapsedRealtime();while(!stopped){if(waitForResume()){lastProgress=SystemClock.elapsedRealtime();lastHead=-1;}if(stopped)break;long head=Integer.toUnsignedLong(track.getPlaybackHeadPosition());if(head>=frames)break;if(head!=lastHead){lastHead=head;lastProgress=SystemClock.elapsedRealtime();}else if(SystemClock.elapsedRealtime()-lastProgress>15000)throw new IllegalStateException("Audio output stalled");Thread.sleep(10);}}
  }catch(Exception error){failure=error;}
  finally{output=null;if(track!=null){try{track.stop();}catch(IllegalStateException ignored){}try{track.release();}catch(RuntimeException ignored){}}if(codec!=null){try{codec.stop();}catch(IllegalStateException ignored){}try{codec.release();}catch(RuntimeException ignored){}}if(extractor!=null)try{extractor.release();}catch(RuntimeException ignored){}}
  final Exception error=failure;if(!stopped)main.post(()->{if(!stopped){if(error==null)listener.complete();else listener.error(error);}});
 }
}
