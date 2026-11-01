package com.salati.prayer;

import java.io.*;
import java.nio.file.*;
import java.util.*;

public final class QuranAudioRangeTest {
 static void check(boolean value){if(!value)throw new AssertionError();}
 public static void main(String[] args)throws Exception{
  byte[] bytes=new byte[4096];new Random(7).nextBytes(bytes);Path path=Files.createTempFile("salati-offline-range-",".mp3");
  try{
   Files.write(path,bytes);
   for(String header:new String[]{null,"bytes=0-","bytes=25-99","bytes=-37","bytes=4000-999999","bytes=0-0"}){
    QuranAudioRange range=QuranAudioRange.parse(header,bytes.length);
    try(InputStream input=range.open(path.toFile())){
     check(Arrays.equals(input.readAllBytes(),Arrays.copyOfRange(bytes,(int)range.start,(int)range.end+1)));
     check(input.read()==-1);check(input.read(new byte[1],0,0)==0);
    }
   }
   QuranAudioRange suffix=QuranAudioRange.parse("bytes=-99999",bytes.length);check(suffix.start==0&&suffix.end==4095);
   try(InputStream input=QuranAudioRange.parse("bytes=8-12",bytes.length).open(path.toFile())){
    check(input.skip(-5)==0);check(input.skip(999)==5);check(input.read()==-1);
   }
   for(String header:new String[]{"bytes=4096-","bytes=19-8","bytes=-0","bytes=-","items=1-2","bytes=0-1,3-4","bytes=9999999999999999999999-"}){
    boolean rejected=false;try{QuranAudioRange.parse(header,bytes.length);}catch(IllegalArgumentException error){rejected=true;}check(rejected);
   }
   boolean empty=false;try{QuranAudioRange.parse(null,0);}catch(IllegalArgumentException error){empty=true;}check(empty);
   check(!QuranAudioRange.parse(null,4096).partial);check(QuranAudioRange.parse("bytes=0-",4096).partial);
   Path root=Files.createTempDirectory("salati-quran-files-");
   try{
    File pending=root.resolve("pending/qatami/001.mp3").toFile(),saved=root.resolve("saved/qatami/001.mp3").toFile();
    check(pending.getParentFile().mkdirs());byte[] audio=new byte[2048];audio[0]=73;audio[1]=68;audio[2]=51;Files.write(pending.toPath(),audio);
    check(QuranAudioFiles.promote(pending,saved));check(!pending.exists());
    String expectedHash=QuranAudioFiles.sha256(saved);
    check(expectedHash.length()==64&&expectedHash.matches("[0-9a-f]{64}"));
    byte[] altered=Files.readAllBytes(saved.toPath());altered[900]^=73;
    Files.write(saved.toPath(),altered);
    check(!expectedHash.equals(QuranAudioFiles.sha256(saved))); // Same-size corruption detected
    Files.deleteIfExists(pending.toPath()); // Simulate DownloadManager removing its old download path.
    check(Files.readAllBytes(saved.toPath()).length==audio.length);check(QuranAudioFiles.valid(saved));
    check(QuranAudioFiles.promote(pending,saved)); // Recovery after interruption between rename and metadata update.
    check(saved.delete());Files.write(pending.toPath(),new byte[]{73,68,51});
    check(!QuranAudioFiles.promote(pending,saved));check(!saved.exists());
   }finally{try(java.util.stream.Stream<Path> files=Files.walk(root)){files.sorted(Comparator.reverseOrder()).forEach(file->{try{Files.delete(file);}catch(IOException error){throw new RuntimeException(error);}});}}
   System.out.println("Offline Android audio: full file, seeking ranges, suffixes, bounds and invalid ranges pass without network access.");
  }finally{Files.deleteIfExists(path);}
 }
}
