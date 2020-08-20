#!/bin/bash
OLD_PATH=out/report_date/$(date -I -d "yesterday");
NEW_PATH=out/report_date/$(date -I);
DIFF_PATH=$NEW_PATH/diff;
CURRENT_DIR=$(pwd)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

while getopts o:n:d: opt
do
   case $opt in
       o) OLD_PATH=$OPTARG;;
       n) NEW_PATH=$OPTARG;DIFF_PATH=$NEW_PATH/diff;;
       d) DIFF_PATH=$OPTARG;;
   esac
done

find $OLD_PATH -mindepth 1 -path $OLD_PATH/diff  -prune -o  -type d -printf '%P\n' | while read folders; 
do
    mkdir -p "$DIFF_PATH/${folders}";
done

find $OLD_PATH -path $OLD_PATH/diff -prune -o -name "*.csv" -printf '%P\n' | while read file_path; 
do 
    python $SCRIPT_DIR/diff.py "${OLD_PATH}/${file_path}" "${NEW_PATH}/${file_path}" > "${DIFF_PATH}/${file_path}"
    file_sum_path=${file_path//.csv/_sum.csv}
    python $SCRIPT_DIR/diff.py "${OLD_PATH}/${file_path}" "${NEW_PATH}/${file_path}" --sum  > "${DIFF_PATH}/${file_sum_path}"
done
