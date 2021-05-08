# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import seaborn as sns


df = pd.read_csv("raw_data_TSC.csv")



df['PD'] = pd.to_datetime(df['PD'])
df.sort_values(by='PD', inplace=True)
print(df.head(5))
df['PD_Year'] =  df['PD'].astype(str).str[:4]
df['PD_Month'] = df['PD'].astype(str).str[5:7]
print(df[['PD', 'PD_Month', 'PD_Year']].head(5))

df1 = df[['PD_Month', 'PD_Year', 'days']]

df['notice date'] = pd.to_datetime(df['notice date'])

df2021 = df[df['notice date'] > '2021-01-01']
print( df2021[df2021['PD_Year'] == '2020']['PD_Month'].value_counts())

df1 = df1.rename(columns = {'days': 'M'})

##
## df['PD']=df['PD'].dt.strftime('%Y-%m')
## print(df.head(5))

 # df.index = df['PD']

 # print(df.head(5))

 # df.groupby(pd.Grouper(freq='M')).agg({'days': ['mean', 'min', 'max']}) 



wait_days_per_pd_month = df1.groupby(['PD_Year','PD_Month'])['M'].mean().reset_index(name ='Month')
pivot_table = pd.pivot_table(wait_days_per_pd_month, index='PD_Year', columns='PD_Month', fill_value=0)

# pivot_table.reset_index(inplace=True)

pivot_table.columns = [' '.join(col).strip() for col in pivot_table.columns.values]
print(pivot_table.columns.values.tolist())

print(pivot_table)

print(type(pivot_table.loc['2014']))

fig, axarr = plt.subplots(2, figsize=(10,8))
ticks = [50, 100, 150,200,250,300,350,400]

 # axarr[0,0].scatter(pivot_table.columns, pivot_table[pivot_table['PD_Year'] == '2014'])
 # axarr[0,0].set_title('2014')
 # axarr[0,1].scatter(pivot_table.columns,pivot_table[pivot_table['PD_Year'] == '2016'])
 # axarr[0,1].set_title('2016')
# axarr[0].plot(pivot_table.columns,pivot_table.loc['2018'], '*m-')
# axarr[0].set_title('2018')
axarr[0].plot(pivot_table.columns,pivot_table.loc['2019'],'*g-')
axarr[0].set_title('2019')
axarr[1].plot(pivot_table.columns,pivot_table.loc['2020'],'*b-')
axarr[1].set_title('2020')

# axarr[0].set_yticks([100,200,300,400, 500])
axarr[0].set_yticks(ticks)
axarr[1].set_yticks(ticks)

 # fig.text(0.5, 0.04, 'Priority Date - Month in year', ha='center', va='center')
fig.text(0.01, 0.5, 'Waiting time in number of days', ha='center', va='center', rotation='vertical')
fig.tight_layout()

fig.show()


df1 = df1.rename(columns = {'M': 'Number of days of wait time'})

print(wait_days_per_pd_month.columns)

f, axes = plt.subplots(2)
 # pivot_table.reset_index(inplace=True)

 # di = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul", 8: "Aug",9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec" }
 # df1['PD_Month'] = df1['PD_Month'].map(di)

sns.boxplot(x='PD_Month',y='Number of days of wait time',data=df1[df1['PD_Year']=='2019'] ,ax=axes[0])
axes[0].set_title('2019')
sns.boxplot(x='PD_Month',y='Number of days of wait time',data=df1[df1['PD_Year']=='2020'] ,ax=axes[1])
axes[1].set_title('2020')
f.tight_layout()
f.show()

df['PD_Year_Month'] = df['PD'].astype(str).str[:7]
df['Notice_Year_Month'] = df['notice date'].astype(str).str[:7]

PD_list = list(df['PD_Year_Month'])

Notice_list = list(df['Notice_Year_Month'])

from collections import Counter

most_common = Counter(zip(PD_list,Notice_list)).most_common()
##print(Counter(zip(PD_list,Notice_list)).most_common())

most_common_ind_sept_2019 = [i for i, val in enumerate(most_common) if val[0][0]=='2019-09']
most_common_ind_sept_2020 = [i for i, val in enumerate(most_common) if val[0][0]=='2020-09']

sept_most_common = [most_common[i] for i in most_common_ind_sept_2019]

num_cases = sum([val[1] for val in sept_most_common])

print("*"*45)
print("Total Number of Cases in Sept-2019")
print("########  "+str(num_cases)+"  #############")
print("*"*45)

percent = [(val[1]/num_cases) * 100 for val in sept_most_common]

print("*"*45)
for i in range(len(sept_most_common)):
    print("Percentage cases approved in: {} - {}".format(sept_most_common[i][0][1], int(percent[i])))
print("*"*45)

sept_most_common_2020 = [most_common[i] for i in most_common_ind_sept_2020]

num_cases = sum([val[1] for val in sept_most_common_2020])
percent = [(val[1]/num_cases) * 100 for val in sept_most_common_2020]

print("*"*45)
print("Total Number of Cases in Sept-2020")
print("########  "+str(num_cases)+"  #############")
print("*"*45)

print("*"*45)
for i in range(len(sept_most_common_2020)):
    print("Percentage cases approved in: {} - {}".format(sept_most_common_2020[i][0][1], int(percent[i])))
print("*"*45)

fig, axarr = plt.subplots(2, figsize=(10,8))
ticks = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]

sept_2019_cols = ['2020-04', '2020-05', '2020-06', '2020-07', '2020-08','2020-09', '2020-10', '2020-11', '2020-12', '2021-01', '2021-02','2021-03','2021-04']
sept_2019_vals = [0]*len(sept_2019_cols)
for i in range(len(sept_2019_cols)):
    for j in range(len(sept_most_common)):
        if (sept_most_common[j][0][1] == sept_2019_cols[i]):
            sept_2019_vals[i] = sept_most_common[j][1]

print(sept_2019_vals)
axarr[0].plot(sept_2019_cols,sept_2019_vals,'*g-')
axarr[0].set_title('I140 NIW Sept 2019 PD Case Approvals')
sept_2020_cols = ['2021-04', '2021-05', '2021-06', '2021-07', '2021-08','2021-09', '2021-10', '2021-11', '2021-12', '2022-01', '2022-02','2022-03','2022-04']
sept_2020_vals = [0]*len(sept_2020_cols)
for i in range(len(sept_2020_cols)):
    for j in range(len(sept_most_common_2020)):
        if (sept_most_common_2020[j][0][1] == sept_2020_cols[i]):
            sept_2020_vals[i] = sept_most_common_2020[j][1]

print(sept_2020_vals)
axarr[1].plot(sept_2020_cols,sept_2020_vals,'*b-')
axarr[1].set_title('I140 NIW Sept 2020 PD Case Approvals')
axarr[0].set_yticks(ticks)
axarr[1].set_yticks(ticks)
fig.text(0.01, 0.5, 'I140 NIW approvals for Sept Month', ha='center', va='center', rotation='vertical')
fig.tight_layout()

fig.show()




