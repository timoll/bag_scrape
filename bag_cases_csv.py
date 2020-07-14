import csv
import sys
import pandas as pd
import requests
import io
import argparse
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.pylab as pl
import matplotlib.dates as mdates
import cycler

all_link='https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-basisdaten-fallzahlen.xlsx.download.xlsx/Dashboards_1&2_COVID19_swiss_data_pv.xlsx'
cantons_DE={
        'AG': 'Aargau', 
        'AR': 'Appelzell Ausserrhoden',
        'AI': 'Appenzell Innerrhoden',
        'BL': 'Basel-Landschaft',
        'BS': 'Basel-Stadt',
        'BE': 'Bern',
        'FR': 'Freiburg',
        'GE': 'Genf',
        'GL': 'Glarus',
        'GR': 'Graubünden',
        'JU': 'Jura',
        'LU': 'Luzern',
        'NE': 'Neuenburg',
        'NW': 'Nidwalden',
        'OW': 'Obwalden',
        'SH': 'Schaffhausen',
        'SZ': 'Schwyz',
        'SO': 'Solothurn',
        'SG': 'St. Gallen',
        'TI': 'Tessin',
        'TG': 'Thurgau',
        'UR': 'Uri',
        'VD': 'Waadt',
        'VS': 'Wallis',
        'ZG': 'Zug',
        'ZH': 'Zürich'}
regions_DE={
        'Genferseeregion'   : ['GE', 'VD', 'VS'],
        'Espace Mittelland' : ['BE', 'JU', 'FR', 'NE', 'SO'],
        'Nordwestschweiz'   : ['BS', 'BL', 'AG'],
        'Zürich'            : ['ZH'],
        'Ostschweiz'        : ['SG', 'TG', 'AI', 'AR', 'GL', 'SH', 'GR'],
        'Zentralschweiz'    : ['UR', 'SZ', 'OW', 'NW', 'LU', 'ZG'],
        'Tessin'            : ['TI']
        }

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
print(df.query('canton in ["BE","ZH"]').groupby('canton').sum())
print(df.xs('BE', level='canton', drop_level=False))
print(df.xs('BE', level='canton', drop_level=False).groupby(['age']).sum())
print(df.sum())
#df.xs('BE', level='canton', drop_level=False).groupby(['date']).sum().plot()
#df.xs('BE', level='canton', drop_level=False).groupby(['date']).sum().rolling(window=7).mean().plot()
#plt.show()

df_all=df


df_ch_cantons = df[['cases']].groupby(['date', 'canton']).sum().unstack(level='canton')
df_ch_cantons.columns = df_ch_cantons.columns.droplevel(0)
df_ch_cantons.columns.names=[None]
df_ch_cantons.to_csv(r'out/ch_cantons/cases.csv')

df_ch_age_men = df[['cases']].xs(1, level='sex').groupby(['date', 'age']).sum().unstack(level='age')
df_ch_age_men.columns = df_ch_age_men.columns.droplevel(0)
df_ch_age_men.columns.names=[None]
df_ch_age_men.to_csv(r'out/ch_age/men.csv')

df_ch_age_women = df[['cases']].xs(2, level='sex').groupby(['date', 'age']).sum().unstack(level='age')
df_ch_age_women.columns = df_ch_age_women.columns.droplevel(0)
df_ch_age_women.columns.names=[None]
df_ch_age_women.to_csv(r'out/ch_age/women.csv')

df_ch_age_all = df[['cases']].groupby(['date', 'age']).sum().unstack(level='age')
df_ch_age_all.columns = df_ch_age_all.columns.droplevel(0)
df_ch_age_all.columns.names=[None]
df_ch_age_all.to_csv(r'out/ch_age/all.csv')


for key, cantons in regions_DE.items():
    df=df_all.query('canton in @cantons')
for key, canton in cantons_DE.items():
    print(key + '>' + canton)
    df= df_all.xs(key, level='canton', drop_level=False)


