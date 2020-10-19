import pandas as pd
import requests
def import_ch_summary():
    summary_link='https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-datengrundlage-lagebericht.xlsx.download.xlsx/200325_Datengrundlage_Grafiken_COVID-19-Bericht.xlsx'

    excel_summary=requests.get(summary_link).content
    df=pd.ExcelFile(excel_summary).parse(header=None, skiprows=7,names=['date','cases','hospitalizations','deaths'], usecols='A,B,D,F', index_col=0).fillna(0).astype('int32')
    return df
def import_ch():
	all_link='https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-basisdaten-fallzahlen.xlsx.download.xlsx/Dashboards_1&2_COVID19_swiss_data_pv.xlsx'

	population_link='https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-basisdaten-bevoelkerungszahlen.xlsx.download.xlsx/Population_Size_BFS.xlsx'


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

	cases_df['date']=pd.to_datetime(cases_df['date'])
	deaths_df['date']=pd.to_datetime(deaths_df['date'])

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

	df.fillna(value=0, inplace=True)
	df=df.join(population_df, how='outer')
	return df
