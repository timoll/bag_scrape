import csv
import sys
import pandas as pd
import requests
import io
import argparse
import matplotlib.pyplot as plt
all_link='https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-basisdaten-fallzahlen.xlsx.download.xlsx/Dashboards_1&2_COVID19_swiss_data_pv.xlsx'


parser = argparse.ArgumentParser(description='get daily new cases')

parser.add_argument('-c', '--canton', help="results for a canton") 
args = parser.parse_args()


excel_all=requests.get(all_link).content
cases_df=pd.ExcelFile(excel_all).parse().set_index("fall_dt")
deaths_df=pd.ExcelFile(excel_all).parse().set_index("pttoddat")

cases_df=cases_df[cases_df.index.notnull()]
deaths_df=deaths_df[deaths_df.index.notnull()]

cases_df.reset_index(inplace=True)
deaths_df.reset_index(inplace=True)

cases_df.rename(columns={'fall_dt': 'date', 'ktn': 'canton', 'akl': 'age', 'fallklasse_3':'cases'}, inplace=True) 
deaths_df.rename(columns={'pttoddat': 'date', 'ktn': 'canton', 'akl': 'age', 'pttod_1':'deaths'}, inplace=True) 

cases_index=pd.MultiIndex.from_frame(cases_df[['date', 'canton', 'age', 'sex']])
deaths_index=pd.MultiIndex.from_frame(deaths_df[['date', 'canton', 'age', 'sex']])

cases_df.set_index(cases_index, inplace=True)
deaths_df.set_index(deaths_index, inplace=True)

cases_df=cases_df[['cases']]
deaths_df=deaths_df[['deaths']]

df=cases_df.join(deaths_df, how='outer')
#df=cases_df[['cases']].merge(deaths_df[['deaths']], left_index=True, right_on=['date', 'canton','age', 'sex'])

df.fillna(value=0, inplace=True)
print(df.groupby(['date','age']).sum())
print(df.groupby(['age']).sum())
print(df.xs('BE', level='canton', drop_level=False))
print(df.xs('BE', level='canton', drop_level=False).groupby(['age']).sum())
print(df.sum())
df.xs('BE', level='canton', drop_level=False).groupby(['date']).sum().plot()
df.xs('BE', level='canton', drop_level=False).groupby(['date']).sum().rolling(window=7).mean().plot()
plt.show()
