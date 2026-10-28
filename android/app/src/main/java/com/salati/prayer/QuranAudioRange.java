package com.salati.prayer;

import java.io.*;
import java.util.regex.*;

final class QuranAudioRange {
 final long start,end;
 final boolean partial;
 private QuranAudioRange(long start,long end,boolean partial){this.start=start;this.end=end;this.partial=partial;}
 long length(){return end-start+1;}
 static QuranAudioRange parse(String header,long length){
  if(length<=0)throw new IllegalArgumentException("Empty file");
  if(header==null||header.isEmpty())return new QuranAudioRange(0,length-1,false);
  Matcher match=Pattern.compile("bytes=(\\d*)-(\\d*)",Pattern.CASE_INSENSITIVE).matcher(header.trim());
  if(!match.matches()||match.group(1).isEmpty()&&match.group(2).isEmpty())throw new IllegalArgumentException("Invalid range");
  long start,end;
  if(match.group(1).isEmpty()){
   long suffix=Long.parseLong(match.group(2));if(suffix<=0)throw new IllegalArgumentException("Invalid suffix");
   start=Math.max(0,length-suffix);end=length-1;
  }else{
   start=Long.parseLong(match.group(1));end=match.group(2).isEmpty()?length-1:Math.min(length-1,Long.parseLong(match.group(2)));
  }
  if(start>=length||end<start)throw new IllegalArgumentException("Unsatisfied range");
  return new QuranAudioRange(start,end,true);
 }
 InputStream open(File file)throws IOException{
  FileInputStream input=new FileInputStream(file);
  try{input.getChannel().position(start);}catch(IOException error){input.close();throw error;}
  return new FilterInputStream(input){
   long remaining=length();
   @Override public int read()throws IOException{if(remaining==0)return -1;int value=in.read();if(value>=0)remaining--;return value;}
   @Override public int read(byte[] bytes,int offset,int count)throws IOException{if(count==0)return 0;if(remaining==0)return -1;int read=in.read(bytes,offset,(int)Math.min(count,remaining));if(read>0)remaining-=read;return read;}
   @Override public long skip(long count)throws IOException{long skipped=in.skip(Math.min(Math.max(0,count),remaining));remaining-=skipped;return skipped;}
   @Override public int available()throws IOException{return (int)Math.min(remaining,in.available());}
  };
 }
}
