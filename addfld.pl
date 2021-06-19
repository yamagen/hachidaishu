#!/usr/bin/perl
undef %hachidai; 
undef %nijuichidai; 
undef %data; 
while (<>)  {
  chomp;
  print $_."\n";
  $nijuichidai{$_} = 1;
}

open(F,"./hachidai.db");
while (<F>) {
  chomp;
  print $_."\n";
  $hachidai{$_} = 1;
}
close(F);
