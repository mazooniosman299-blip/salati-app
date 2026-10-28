package com.salati.prayer;

/** The service advances this queue without any Activity, WebView or JS callback. */
final class QuranPlaylist {
 final int[] groups;int index;boolean repeat,autoNext;
 QuranPlaylist(int[] groups,boolean repeat,boolean autoNext){
  if(groups.length==0||groups.length>7000)throw new IllegalArgumentException("queue");
  this.groups=groups.clone();for(int i=0;i<groups.length;i++)if(groups[i]<1||groups[i]>114||i>0&&groups[i]<groups[i-1])throw new IllegalArgumentException("surah");this.repeat=repeat;this.autoNext=autoNext;
 }
 boolean advance(){int next=index+1;if(next<groups.length&&groups[next]==groups[index]){index=next;return true;}if(repeat){while(index>0&&groups[index-1]==groups[index])index--;return true;}if(autoNext&&next<groups.length){index=next;return true;}return false;}
 boolean nextGroup(){int group=groups[index],next=index;while(next<groups.length&&groups[next]==group)next++;if(next==groups.length)return false;index=next;return true;}
 void previousGroup(boolean restart){int group=groups[index];while(index>0&&groups[index-1]==group)index--;if(!restart&&index>0){index--;group=groups[index];while(index>0&&groups[index-1]==group)index--;}}
}
