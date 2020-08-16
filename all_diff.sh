#!/bin/bash
cd out/report_date/$(date -I -d "yesterday");
find . -mindepth 1 -path ./diff  -prune -o  -type d -print | while read folders; 
do
    mkdir -p "../$(date -I)/diff/${folders}";
done

find . -path ./diff -prune -o -name "*.csv" -print | while read file_path; 
do 
    python ../../../diff.py "${file_path}" "../$(date -I)/${file_path}" > "../$(date -I)/diff/${file_path}"
    python ../../../diff.py "${file_path}" "../$(date -I)/${file_path}" --sum > "../$(date -I)/diff/${file_path}.sum.csv"
done
