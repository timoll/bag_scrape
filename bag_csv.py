import csv
import sys
import pandas as pd
import requests
import io
import argparse

cases_link='https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-datengrundlage-lagebericht.xlsx.download.xlsx/200325_Datengrundlage_Grafiken_COVID-19-Bericht.xlsx'

tests_link='https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-basisdaten-labortests.xlsx.download.xlsx/Dashboard_3_COVID19_labtests_positivity.xlsx'

parser = argparse.ArgumentParser(description='get daily new cases')

parser.add_argument('-d', '--delete', metavar='N', type=int, help="delete first N lines") 
parser.add_argument('-i', '--index', help="output index", action="store_true")

args = parser.parse_args()


cases_excel=requests.get(cases_link).content
tests_excel=requests.get(tests_link).content
cases_df=pd.ExcelFile(cases_excel).parse(skiprows=6).set_index("Datum")
tests_df=pd.ExcelFile(tests_excel).parse()


tests_df=tests_df.groupby(by=['Datum','Outcome_tests']).sum()
tests_df=tests_df.unstack(level=-1)
result=pd.concat([cases_df["Fallzahlen pro Tag"], tests_df], axis=1, sort=False)
print(result.to_csv(index=args.index, header=args.index)) 

