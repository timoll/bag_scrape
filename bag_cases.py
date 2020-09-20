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
import covid_importer.importer as importer
import matplotlib.ticker as mtick
import matplotlib.patheffects as PathEffects

def generate_figure(df, title, name):
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
    plt.title(title, y=1.05)
    plt.margins(x=0)
    plt.subplots_adjust(left=0.05, right=0.9, top=0.9, bottom=0.05)
    plt.savefig(name)
    plt.close()

def generate_growth_figure(df, title, name):
    fig, ax1 =plt.subplots(1,1)
    fig.set_size_inches(18.5,10.5, forward=True)
    dates=df.index.strftime('%Y-%m-%d')
    change=df['change']*100
    average=df['average']*100

    plt.ylim(-100,150)

    ax1.bar(x=dates, height=change, color=df['change'].map(lambda x : 'lightcoral' if (x > 0) else 'cornflowerblue'), label='Anstieg gegenüber vorwoche')
    ax1.plot(dates, average, label='Durchschnittlicher Anstieg über 4 Wochen', color='black', linewidth=3)
    ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax1.set_axisbelow(True)
    ax1.yaxis.grid(True)

    plt.xticks(rotation=90)
    
    for x,y1,y2 in zip(dates,change, average):

        label1 = "{:.0f}%".format(y1)
        label2 = "{:.0f}%".format(y2)
        y1_cord=10
        y2_cord=15
        color='lightcoral'
        if y1<0:
            y1_cord=-10
            color='cornflowerblue'
        if y2<0:
            y2_cord=-15
        if(abs(y1-y2)<10):
            y2_cord*=-1
        xy1=(0,y1_cord)
        xy2=(0,y2_cord)

        txt=plt.annotate(label1, # this is the text
                 (x,min(150,y1)), # this is the point to label
                 textcoords="offset points", # how to position the text
                 xytext=xy1, # distance from text to points (x,y)
                 ha='center', # horizontal alignment can be left, right or center
                 va='center',
                 color=color)
        txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='white')])
        
        txt=plt.annotate(label2, # this is the text
                 (x,min(150,y2)), # this is the point to label
                 textcoords="offset points", # how to position the text
                 xytext=xy2, # distance from text to points (x,y)
                 ha='center', # horizontal alignment can be left, right or center
                 va='center')
    
        txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='white')])
    plt.title(title, y=1.05)     
    plt.savefig(name)
    plt.close()

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

df=importer.import_ch()
#print(df.query('canton in ["BE","ZH"]').groupby('canton').sum())
#print(df.xs('BE', level='canton', drop_level=False))
#print(df.xs('BE', level='canton', drop_level=False).groupby(['age']).sum())
#print(df.sum())
#df.xs('BE', level='canton', drop_level=False).groupby(['date']).sum().plot()
#df.xs('BE', level='canton', drop_level=False).groupby(['date']).sum().rolling(window=7).mean().plot()
#plt.show()

df_weekly_base = pd.DataFrame(df['cases'].groupby([pd.Grouper(level='date', freq='W-MON', label='left'),'canton']).sum())
df_weekly_ch = df_weekly_base.groupby('date').sum()
df_weekly_ch['change']=df_weekly_ch.pct_change()
df_weekly_ch['average']=(1.+df_weekly_ch['change']).rolling(window=4).apply(np.prod, raw=True).pow(1/4)-1

weekly_base_text='Wachstum der neuen Fälle gegenüber der Vorwoche sowie der gleitende Schnitt des Wachstums über 4 Wochen'
generate_growth_figure(df_weekly_ch.iloc[8:-1],weekly_base_text + ' in der Schweiz', 'CH_growth')


df_all=df
generate_figure(df, 'Altersverteilung der neuen Fälle in der Schweiz', 'CH')

for key, cantons in regions_DE.items():
    print(key)
    generate_figure(df_all.query('canton in @cantons'),'Altersverteilung der neuen Fälle in der Region {}'.format(key), key)
    df_weekly= df_weekly_base.query('canton in @cantons').groupby('date').sum()
    df_weekly['change']=df_weekly.pct_change()
    df_weekly['average']=(1.+df_weekly['change']).rolling(window=4).apply(np.prod, raw=True).pow(1/4)-1
    generate_growth_figure(df_weekly.iloc[8:-1], weekly_base_text + ' in der Region {}'.format(key), '{}_growth'.format(key))

for key, canton in cantons_DE.items():
    print(key + '>' + canton)
    generate_figure(df_all.xs(key, level='canton', drop_level=False), 'Altersverteilung der neuen Fälle im Kanton {}'.format(canton), key)
    df_weekly= df_weekly_base.xs(key, level='canton', drop_level=True).groupby('date').sum()
    df_weekly['change']=df_weekly.pct_change()
    df_weekly['average']=(1.+df_weekly['change']).rolling(window=4).apply(np.prod, raw=True).pow(1/4)-1
    #df_weekly.reset_index(inplace=True)
    generate_growth_figure(df_weekly.iloc[8:-1], weekly_base_text + ' im Kanton {}'.format(canton), '{}_growth'.format(key))


