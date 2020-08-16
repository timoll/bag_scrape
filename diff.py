import csv
import sys 
import pandas as pd
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('old_file', metavar='OLD', type=argparse.FileType('r', encoding='UTF-8'), help="csv-file with the older data")
parser.add_argument('new_file', metavar='NEW', type=argparse.FileType('r', encoding='UTF-8'), help="csv-file with the newer data")
parser.add_argument('--sum', dest='sum', action='store_const',
                    const=True, default=False,
                    help='sum columns')

args=parser.parse_args()

df1=pd.read_csv(args.old_file, index_col=0)
df2=pd.read_csv(args.new_file, index_col=0)


df=df2.subtract(df1, fill_value=0)
if args.sum :
    print(pd.DataFrame(df.sum(axis=0)).T.to_csv(index=False))
else :
    print(df.to_csv())

args.old_file.close()
args.new_file.close()
