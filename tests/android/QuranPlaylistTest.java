package com.salati.prayer;
public final class QuranPlaylistTest {
 static void check(boolean value){if(!value)throw new AssertionError();}
 public static void main(String[] args){
  QuranPlaylist queue=new QuranPlaylist(new int[]{2,2,2,3,3,4},false,false);check(queue.advance()&&queue.index==1);check(queue.advance()&&queue.index==2);check(!queue.advance()&&queue.index==2);
  queue.repeat=true;check(queue.advance()&&queue.index==0);queue.repeat=false;queue.autoNext=true;for(int i=0;i<5;i++)check(queue.advance());check(queue.index==5&&!queue.advance());
  queue.previousGroup(false);check(queue.index==3);queue.previousGroup(true);check(queue.index==3);check(queue.nextGroup()&&queue.index==5);check(!queue.nextGroup());
  int[] groups=new int[6236];int n=0;for(int s=1;s<=114;s++){int count=s==114?6236-n:54;for(int a=0;a<count;a++)groups[n++]=s;}
  QuranPlaylist background=new QuranPlaylist(groups,false,true);int played=1;while(background.advance())played++;check(played==6236); // No WebView callback, timer or Activity participates.
  QuranPlaylist fullSurahs=new QuranPlaylist(new int[]{112,113,114},false,true);check(fullSurahs.advance()&&fullSurahs.index==1);fullSurahs.repeat=true;check(fullSurahs.advance()&&fullSurahs.index==1);fullSurahs.repeat=false;check(fullSurahs.advance()&&fullSurahs.index==2);check(!fullSurahs.advance());
  try{new QuranPlaylist(new int[]{2,1},false,false);throw new AssertionError();}catch(IllegalArgumentException expected){}
  System.out.println("PASS: native Quran queue advances 6236 cues without Activity/JS, retains verse and surah order, repeats the current surah, honors auto-next and supports skipping.");
 }
}
