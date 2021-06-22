# Hachidaishu classical Japanese poetic vocabulary dataset
## Hilofumi Yamamoto, Ph.D. (Tokyo Institute of Technology)
## Bor Hodošček, D.Engineering (Osaka University)

### Data offset

Example: \# 1 Kokinshu
```
01:000001:0001 A00 BG-01-1630-01-0100 02 年 年 とし 年 とし 
01:000001:0001 A10 BG-01-1911-03-1800 02 年 年 とし 年 とし 
01:000001:0002 A00 BG-08-0061-07-0100 61 の の の の の 
01:000001:0003 A00 BG-01-1770-01-0300 02 内 内 うち 内 うち 
01:000001:0004 A00 BG-08-0061-05-0100 61 に に に に に 
01:000001:0005 A00 BG-01-1624-02-0100 02 春 春 はる 春 はる 
01:000001:0006 A00 BG-08-0065-07-0100 65 は は は は は 
01:000001:0007 A00 BG-02-1527-01-0102 47 き 来 く 来 き 
01:000001:0008 A00 BG-03-1200-02-0900 74 に ぬ ぬ に に 
01:000001:0008 A10 BG-09-0010-01-0101 74 に ぬ ぬ に に 
01:000001:0008 A20 BG-09-0010-03-0200 74 に ぬ ぬ に に 
01:000001:0009 A00 BG-09-0010-04-0300 74 けり けり けり けり けり 
01:000001:0010 B00 BG-01-1950-14-0100 02 一とせ 一年 ひととせ 一年 ひととせ 
01:000001:0010 C00 BG-01-1950-01-0300 19 一 一 いち 一 いち 
01:000001:0010 C01 BG-01-1630-01-0100 02 年 年 とし 年 とし 
01:000001:0011 A00 BG-08-0061-10-0100 61 を を を を を 
01:000001:0012 A00 BG-01-1642-02-0100 02 こそ 去年 こぞ 去年 こぞ 
01:000001:0013 A00 BG-08-0061-04-0100 61 と と と と と 
01:000001:0014 A00 BG-08-0065-14-0100 65 や や や や や 
01:000001:0015 A00 BG-02-3120-01-0100 47 いは 言ふ いふ 言は いは 
01:000001:0016 A00 BG-03-3012-03-2600 74 ん む む む む 
01:000001:0016 A10 BG-09-0010-02-0102 74 ん む む む む 
01:000001:0017 B00 BG-01-1641-02-0100 02 ことし 今年 ことし 今年 ことし 
01:000001:0017 C00 BG-03-1000-01-0100 57 この この この この この 
01:000001:0017 C01 BG-01-1630-01-0100 02 年 年 とし 年 とし 
01:000001:0018 A00 BG-08-0061-04-0100 61 と と と と と 
01:000001:0019 A00 BG-08-0065-14-0100 65 や や や や や 
01:000001:0020 A00 BG-02-3120-01-0100 47 いは 言ふ いふ 言は いは 
01:000001:0021 A00 BG-03-3012-03-2600 74 ん む む む む 
01:000001:0021 A10 BG-09-0010-02-0102 74 ん む む む む 
``` 
### A line consists of 7 columns separated by spaces.
```
01:000001:0007 A00 BG-02-1527-01-0102 47 き 来 く 来 き 
```
- 1st column "01:000001:0007" consists of 3 fields: 1) anthology, 2) number of poem, and 3) serial ID of the token.
The anthology ID indicates respectively: 01..Kokinshu, 02..Gosenshu, 03..Shuishu, 04..Goshuishu, 05..Kin'yoshu, 06..Shikashu, 07..Senzaishu, and 08..Shinkokinshu.
- 2nd column indicates type of token: A type is a single token; B type is a compound token; C type is a breakdown of B type.
A00 indicates a single token; A01 indicates a single token and has another meaning; 
B00 indicates a compound token; B01 indicates a compound token which has another meaning;
C00 indicates the first element of the B00/B01.. breakdown; C01 indicates the second element of the B00/B01.. breakdown.
- 3rd column "BG-02-1527-01-0102": classification ID based on semantic categories according to Bunruigoihyo (Yamazaki et al. 2014).
- 4th column indicates a Chasen POS number.
- 5th column indicates surface form: a form appears in literary works.
- 6th column indicates lemma in kanji writing.
- 7th column indicates lemma in kana writing.
- 8th column indicates conjugated form in kanji writing form.
- 9th column indicates conjugated form in kana writing form.

## Notebook

Please see the [notebook](Hachidaishu_Vocabulary_Dataset_Examples.ipynb) provided in this repository for some examples on loading and analysing the dataset from Python.

## Reference

1. Yamamoto, Hilofumi (2007) 
  Thesaurus of Japanese Poetic Vocabulary Based on the Semantic Classifications Chart,
  The 13th Annual Symposium for Database of the Humanities, 
  1-8, 
  The Association for Database of the Humanities,
  Osaka.

1. Yamamoto, Hilofumi (2009) 
  Thesaurus for the Hachidaishu (ca. 905-1205) with the classification codes based on semantic principles,
  Nihongo no Kenkyu / Studies in the Japanese Language,
  46-52,
  Society for Japanese Linguistics,
  5, 1, 
  ISSN1349-5119.

1. Yamamoto, Hilofumi (2021)
  Hachidaishu vocabulary dataset,
  Zenodo,
  version 1.0.1,
  <https://doi.org/10.5281/zenodo.4744170>

1. Yamazaki, Makoto and Kashino, Wakako and Uchiyama, Kiyoko and Sunaoka, Kazuko, and Tajima, Ikudo and Yamamoto, Hilofumi and Han, Yoo-Sik and Seol, Geun-Su (2014)
  Bunruigoihyo zouhokaiteiban" e no anoteishion: kihongi no kettei (in Japanese),
  Keiryo Kokugo gakkai dai 58 kai taikai yokoshu,
  pp. 7--12.

1. [国文学研究資料館二十一代集](http://kotenseki.nijl.ac.jp/biblio/200007092)

1. [二十一代集 DOI: 10.20730/200007092](http://codh.rois.ac.jp/pmjt/book/200007092/): ROIS-DS人文学オープンデータ共同利用センター 新日本古典籍総合データベース（200007093）

<!--
@dataset{yamamoto_hilofumi_2021_4735848,
  author       = {Yamamoto, Hilofumi},
  title        = {Hachidaishu vocabulary dataset},
  month        = may,
  year         = 2021,
  publisher    = {Zenodo},
  version      = {1.0.0},
  doi          = {10.5281/zenodo.4735848},
  url          = {https://doi.org/10.5281/zenodo.4735848}
}

@Article{yamagen2009ae,
  author = 	 {Yamamoto, Hilofumi},
  title = 	 {Thesaurus for the Hachidaishu (ca.\,905--1205) with the classification codes based on semantic principles},
  journal =      {Nihongo no Kenkyu / {S}tudies in the Japanese Language},
  pages = 	 {46--52},
  OPTpublisher = {Society for Japanese Linguistics},
  year = 	 {2009},
  volume = 	 {5},
  number = 	 {1},
  OPTedition = 	 {ISSN1349-5119},
  OPTmonth = 	 {},
  OPTnote = 	 {},
  OPTannote = 	 {},
  OPTlocation =  {},
  OPTmemo = 	 {}
}

@InCollection{yamagen2007de,
  author = 	 {Yamamoto, Hilofumi},
  title = 	 {Thesaurus of Japanese Poetic Vocabulary Based on the Semantic
      Classifications Chart},
  year = 	 {2007},
  booktitle = 	 {The 13th Annual Symposium for Database of the Humanities}, 
  pages = 	 {1--8},
  publisher =    {The Association for Database of the Humanities},
  address = 	 {Osaka},
  OPTedition = 	 {},
  OPTmonth = 	 {2007.12},
  OPTmemo = 	 {}
}
-->
