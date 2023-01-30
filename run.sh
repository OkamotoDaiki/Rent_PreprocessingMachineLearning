#!/bin/sh

city="Chiyoda"
today="20230130"
input_URL="https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc=13101&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&srch_navi=1"
IO_fpathScraping="./data/raw/raw_"$city"_"$today".csv"
python3 ./script/scraping.py $IO_fpathScraping $input_URL
outputfpath_preprocessing="./result/preprocessing_"$city"_"$today".csv"
python3 ./script/preprocessing.py $IO_fpathScraping $outputfpath_preprocessing