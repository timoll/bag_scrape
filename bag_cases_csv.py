import csv
import sys
import pandas as pd
import requests
import io
import matplotlib.pyplot as plt
from pathlib import Path

all_link='https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-basisdaten-fallzahlen.xlsx.download.xlsx/Dashboards_1&2_COVID19_swiss_data_pv.xlsx'

population_link='https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-basisdaten-bevoelkerungszahlen.xlsx.download.xlsx/Population_Size_BFS.xlsx'

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


excel_all=requests.get(all_link).content
excel_population=requests.get(population_link).content
cases_df=pd.ExcelFile(excel_all).parse().set_index("fall_dt")
deaths_df=pd.ExcelFile(excel_all).parse().set_index("pttoddat")
population_df=pd.ExcelFile(excel_population).parse()

cases_df=cases_df[cases_df.index.notnull()]
deaths_df=deaths_df[deaths_df.index.notnull()]

cases_df.reset_index(inplace=True)
deaths_df.reset_index(inplace=True)

cases_df.rename(columns={'fall_dt': 'date', 'ktn': 'canton', 'akl': 'age', 'fallklasse_3':'cases'}, inplace=True) 
deaths_df.rename(columns={'pttoddat': 'date', 'ktn': 'canton', 'akl': 'age', 'pttod_1':'deaths'}, inplace=True) 
population_df.rename(columns={'ktn':'canton', 'Geschlecht':'sex', 'akl':'age', 'pop_size':'population'}, inplace=True)

cases_df['sex'].replace(to_replace={1:'male', 2:'female', 9:'unknown'}, inplace=True)
deaths_df['sex'].replace(to_replace={1:'male', 2:'female', 9:'unknown'}, inplace=True)
population_df['sex'].replace(to_replace={'Männlich':'male', 'Weiblich':'female'}, inplace=True)

cases_index=pd.MultiIndex.from_frame(cases_df[['date', 'canton', 'age', 'sex']])
deaths_index=pd.MultiIndex.from_frame(deaths_df[['date', 'canton', 'age', 'sex']])
population_index=pd.MultiIndex.from_frame(population_df[['canton','age','sex']])

cases_df.set_index(cases_index, inplace=True)
deaths_df.set_index(deaths_index, inplace=True)

population_df.set_index(population_index, inplace=True)

cases_df=cases_df[['cases']]
deaths_df=deaths_df[['deaths']]
population_df=population_df[['population']]
df=cases_df.join(deaths_df, how='outer')
population_df = population_df.groupby(['canton','age','sex']).sum()
print(population_df)

#df=cases_df[['cases']].merge(deaths_df[['deaths']], left_index=True, right_on=['date', 'canton','age', 'sex'])

df.fillna(value=0, inplace=True)
df=df.join(population_df, how='outer')
print(df.groupby(['date','age']).sum())

df_prevalence=df.groupby(['date', 'age']).sum()
df_prevalence['prevalence per 100 000']=df_prevalence['cases']/df_prevalence['population']*100000
print(df_prevalence)
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

df_ch_cantons_prevalence = df.groupby(['date', 'canton']).sum()
df_ch_cantons_prevalence['prevalence per 100 000'] = df_ch_cantons_prevalence['cases']/df_ch_cantons_prevalence['population']*100000
df_ch_cantons_prevalence = df_ch_cantons_prevalence[['prevalence per 100 000']].unstack(level='canton')
df_ch_cantons_prevalence.columns = df_ch_cantons_prevalence.columns.droplevel(0)
df_ch_cantons_prevalence.columns.names=[None]

df_ch_cantons_deaths = df[['deaths']].groupby(['date', 'canton']).sum().unstack(level='canton')
df_ch_cantons_deaths.columns = df_ch_cantons_deaths.columns.droplevel(0)
df_ch_cantons_deaths.columns.names=[None]

df_ch_cantons_prevalence_deaths = df.groupby(['date', 'canton']).sum()
df_ch_cantons_prevalence_deaths['prevalence per 100 000'] = df_ch_cantons_prevalence_deaths['deaths']/df_ch_cantons_prevalence_deaths['population']*100000
df_ch_cantons_prevalence_deaths = df_ch_cantons_prevalence_deaths[['prevalence per 100 000']].unstack(level='canton')
df_ch_cantons_prevalence_deaths.columns = df_ch_cantons_prevalence_deaths.columns.droplevel(0)
df_ch_cantons_prevalence_deaths.columns.names=[None]

Path(r'out/ch_cantons/').mkdir(parents=True, exist_ok=True)
df_ch_cantons.to_csv(r'out/ch_cantons/cases.csv')
df_ch_cantons_deaths.to_csv(r'out/ch_cantons/deaths.csv')
df_ch_cantons_prevalence.to_csv(r'out/ch_cantons/prevalence.csv')
df_ch_cantons_prevalence_deaths.to_csv(r'out/ch_cantons/deaths_prevalence.csv')

def generate_age_csv(df, path, column):
    df_age_men = df[[column]].xs('male', level='sex').groupby(['date', 'age']).sum().unstack(level='age')
    df_age_men.columns = df_age_men.columns.droplevel(0)
    df_age_men.columns.names=[None]
    df_age_men.to_csv(path + 'men.csv')

    df_age_men_prevalence = df.xs('male', level='sex').groupby(['date', 'age']).sum()
    df_age_men_prevalence['prevalence per 100 000'] = df_age_men_prevalence[column]/df_age_men_prevalence['population']*100000
    df_age_men_prevalence = df_age_men_prevalence[['prevalence per 100 000']].unstack(level='age')
    df_age_men_prevalence.columns = df_age_men_prevalence.columns.droplevel(0)
    df_age_men_prevalence.columns.names=[None]
    df_age_men_prevalence.to_csv(path + 'men_prevalence.csv')

    df_age_women = df[[column]].xs('female', level='sex').groupby(['date', 'age']).sum().unstack(level='age')
    df_age_women.columns = df_age_women.columns.droplevel(0)
    df_age_women.columns.names=[None]
    df_age_women.to_csv(path + 'women.csv')

    df_age_women_prevalence = df.xs('female', level='sex').groupby(['date', 'age']).sum()
    df_age_women_prevalence['prevalence per 100 000'] = df_age_women_prevalence[column]/df_age_women_prevalence['population']*100000
    df_age_women_prevalence = df_age_women_prevalence[['prevalence per 100 000']].unstack(level='age')
    df_age_women_prevalence.columns = df_age_women_prevalence.columns.droplevel(0)
    df_age_women_prevalence.columns.names=[None]
    df_age_women_prevalence.to_csv(path + 'women_prevalence.csv')
    
    df_age_all = df[[column]].groupby(['date', 'age']).sum().unstack(level='age')
    df_age_all.columns = df_age_all.columns.droplevel(0)
    df_age_all.columns.names=[None]
    df_age_all.to_csv(path + 'all.csv')
    
    df_age_all_prevalence = df.groupby(['date', 'age']).sum()
    df_age_all_prevalence['prevalence per 100 000'] = df_age_all_prevalence[column]/df_age_all_prevalence['population']*100000
    df_age_all_prevalence = df_age_all_prevalence[['prevalence per 100 000']].unstack(level='age')
    df_age_all_prevalence.columns = df_age_all_prevalence.columns.droplevel(0)
    df_age_all_prevalence.columns.names=[None]
    df_age_all_prevalence.to_csv(path + 'all_prevalence.csv')

Path(r'out/ch_age/').mkdir(parents=True, exist_ok=True)
Path(r'out/ch_age_deaths/').mkdir(parents=True, exist_ok=True)
generate_age_csv(df, r'out/ch_age/', 'cases')
generate_age_csv(df, r'out/ch_age_deaths/', 'deaths')

for key, cantons in regions_DE.items():
    df=df_all.query('canton in @cantons')
    Path(r'out/region_age/{}/'.format(key)).mkdir(parents=True, exist_ok=True)
    Path(r'out/region_age/{}_deaths/'.format(key)).mkdir(parents=True, exist_ok=True)
    generate_age_csv(df, r'out/region_age/{}/'.format(key), 'cases')
    generate_age_csv(df, r'out/region_age/{}_deaths/'.format(key), 'deaths')

for key, canton in cantons_DE.items():
    print(key + '>' + canton)
    df= df_all.xs(key, level='canton', drop_level=False)
    Path(r'out/canton_age/{}/'.format(key)).mkdir(parents=True, exist_ok=True)
    Path(r'out/canton_age/{}_deaths/'.format(key)).mkdir(parents=True, exist_ok=True)
    generate_age_csv(df, r'out/canton_age/{}/'.format(key), 'cases')
    generate_age_csv(df, r'out/canton_age/{}_deaths/'.format(key), 'deaths')


