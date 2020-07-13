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
#df.xs('BE', level='canton', drop_level=False).groupby(['date']).sum().plot()
#df.xs('BE', level='canton', drop_level=False).groupby(['date']).sum().rolling(window=7).mean().plot()
#plt.show()
date_age=df.groupby(['date', 'age']).sum()[['cases']]
date=df.groupby(['date']).sum()[['cases']]

date_age =date_age.groupby(level='age').cases.apply(lambda x: x.rolling(window=7).mean()).unstack()[:-1]
date=date.rolling(window=7).mean().dropna()[:-1]

date_age_relative=date_age.divide(date_age.sum(axis=1), axis=0).dropna()


fig, ax1 = plt.subplots(1,1)
fig.set_size_inches(18.5,10.5, forward=True)
#date.plot(ax=ax1, kind='line', linewidth=4, color='black', logy=True)
ax1.plot(pd.to_datetime(date.index), date.to_numpy(), color='black', linewidth=4, label='Neue Fälle')

ax2 = ax1.twinx()
ax1.set_yscale('log')
cmap = matplotlib.cm.get_cmap('PuOr')
color =  cmap(np.linspace(0,1,10))

ax2.stackplot(pd.to_datetime(date_age_relative.index), date_age_relative.to_numpy().T,labels=date_age_relative.columns, colors=color) 
#date_age_relative.plot(ax=ax2, kind='area', stacked=True ,colormap='PuOr')
ax1.set_zorder(10)
ax1.yaxis.grid(color='black', linestyle='dashed')

mloc = mdates.MonthLocator()
wloc = mdates.WeekdayLocator()

ax1.xaxis.set_major_locator(wloc)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
#ax1.xaxis.set_minor_locator(wloc)
ax1.xaxis.grid(color='black', linestyle='dashed')
ax1.patch.set_visible(False)
ax2.set_ylim([0,1])

handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()

ax1.legend(handles1, labels1, loc='lower center', bbox_to_anchor=(0.5,1.0))
ax2.legend(handles2[::-1], labels2[::-1], loc='center left', bbox_to_anchor=(1.025,0.5))
plt.title('Altersverteilung und neue Fälle in der Schweiz', y=1.05)
plt.margins(x=0)
plt.subplots_adjust(left=0.05, right=0.9, top=0.9, bottom=0.05)
plt.show()
