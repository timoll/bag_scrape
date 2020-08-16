import csv
import sys 
import pandas as pd
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('file1', metavar='F1', type=argparse.FileType('r', encoding='UTF-8'))
parser.add_argument('file2', metavar='F2', type=argparse.FileType('r', encoding='UTF-8'))
parser.add_argument('--sum', dest='sum', action='store_const',
                    const=True, default=False,
                    help='sum columns')

args=parser.parse_args()

df1=pd.read_csv(args.file1, index_col='date')
df2=pd.read_csv(args.file2, index_col='date')


df=df1.subtract(df2, fill_value=0)
if args.sum :
    print(pd.DataFrame(df.sum(axis=0)).T.to_csv(index=False))
else :
    print(df.to_csv())

args.file1.close()
args.file2.close()
