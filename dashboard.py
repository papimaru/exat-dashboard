import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import json
import plotly.figure_factory as ff
import plost
import calendar
import datetime


datenow = datetime.datetime.now()
lastYear = 6
curYear = datenow.year
yearList = []
yearApiList = []
for y in range(lastYear):
    yearList.append(str(curYear))
    yearApiList.append(str(curYear+543))
    curYear -= 1
    
st.set_page_config(layout='wide', initial_sidebar_state='expanded')
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
## Sidebar Control 
st.sidebar.header('Expressway Authority of Thailand')

st.sidebar.subheader('Filter Year')

# year_param = st.sidebar.selectbox('Year', ('2022','2021','2020','2019','2018', '2017')) 
year_param = st.sidebar.selectbox('Year', yearList) 

st.sidebar.subheader('Filter Station')
station_data = st.sidebar.multiselect('Station', ['ศรีรัช','บางพลี-สุขสวัสดิ์','เฉลิมมหานคร','บูรพาวิถี','ฉลองรัช','ทางหลวงพิเศษหมายเลข 37','อุดรรัถยา','ศรีรัช-วงแหวนรอบนอก','S1'], ['ศรีรัช','บางพลี-สุขสวัสดิ์','เฉลิมมหานคร','บูรพาวิถี','ฉลองรัช','ทางหลวงพิเศษหมายเลข 37','อุดรรัถยา','ศรีรัช-วงแหวนรอบนอก','S1'])

plot_height = st.sidebar.slider('Specify Line Char height', 200, 500, 250)

## Convert timestamp to period
def convertTimeToPeriod(time):
    if time > datetime.time(hour=3)  and time < datetime.time(hour=6):
        return '03:00 - 06:00'
    elif time > datetime.time(hour=7)  and time < datetime.time(hour=10):
        return '07:00 - 10:00'
    elif time > datetime.time(hour=11)  and time < datetime.time(hour=14):
        return '01:00 - 14:00'
    elif time > datetime.time(hour=15)  and time < datetime.time(hour=18):
        return '15:00 - 18:00'
    elif time > datetime.time(hour=19)  and time < datetime.time(hour=22):
        return '19:00 - 22:00'
    else:
        return '23:00 - 02:00'

## GetDate from Api default 2560 - 2565
def getdata():
    d = []
    year = yearApiList
    for y in year:
        for i in range(12):
            url = 'https://exat-man.web.app/api/EXAT_Accident/{year}/{month}'
            r = requests.get(url.format(year=y,month=str(i+1))).json()
            d += r['result']
    with open('accident.json','w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=4)
        
## Prepare Data
f = open('accident.json',encoding='utf-8')
data = json.load(f)
df = pd.json_normalize(data)
df_cur = df
df['month'] = pd.DatetimeIndex(df['accident_date']).month
df['year'] = pd.DatetimeIndex(df['accident_date']).year
df['time'] = pd.DatetimeIndex(df['accident_time']).time
df['time'] = df['time'].apply(lambda t: convertTimeToPeriod(t))
df = df[df['year'] == int(year_param)]
df = df[df['expw_step'].isin(station_data)]



## Title Dashboard
st.title('การเกิดอุบัติเหตุการทางพิเศษแห่งประเทศไทย')

## Button Update Data to Current
if st.button('Refresh Data'):
    getdata()
    f = open('accident.json',encoding='utf-8')
    data = json.load(f)
    df = pd.json_normalize(data)

## Checkbox for Show Raw Data
if st.checkbox('Show Raw Data'):
    st.subheader('Raw Data')
    st.write(df)




## Prepare Data last 7 day
last7day = datenow + datetime.timedelta(days=-7)
count_7day = len(df_cur[pd.DatetimeIndex(df_cur['accident_date']) > last7day ])
count_all = len(df_cur)

sumInjury = df_cur['injur_man'].sum() + df_cur['injur_femel'].sum()
sumInjury7day = df_cur[pd.DatetimeIndex(df_cur['accident_date']) > last7day ]['injur_man'].sum()\
    + df_cur[pd.DatetimeIndex(df_cur['accident_date']) > last7day ]['injur_femel'].sum()
    
sumDead = df_cur['dead_man'].sum() + df_cur['dead_femel'].sum()
sumDead7day = df_cur[pd.DatetimeIndex(df_cur['accident_date']) > last7day ]['dead_man'].sum()\
    + df_cur[pd.DatetimeIndex(df_cur['accident_date']) > last7day ]['dead_femel'].sum()

## Metric last 7 day
st.markdown('### จำนวนที่เปลี่ยนแปลง 7 วันล่าสุด')
col1, col2, col3 = st.columns(3)
col1.metric("อุบัติเหตุทั้งหมด", str(count_all), str(count_7day))
col2.metric("บาดเจ็บทั้งหมด", str(sumInjury), str(sumInjury7day))
col3.metric("เสียชีวิตทั้งหมด", str(sumDead), str(sumDead7day))

r1c1, r1c2 = st.columns((5,5))
## Prepare Data last 7 day Count
accdate_cur = {'accident_date':df_cur.accident_date.value_counts().sort_index().index.tolist(), 'count':df_cur.accident_date.value_counts().sort_index().tolist()}
df_accdate_cur = pd.DataFrame(data=accdate_cur)
df_accdate7day = df_accdate_cur[pd.DatetimeIndex(df_accdate_cur['accident_date']) > last7day]

## Line Chart lasy 7 day Count
with r1c1:
    st.markdown('### จำนวนครั้งที่เกิดอุบัติเหตุ 7 วันล่าสุด')
    line_7day = px.line(df_accdate7day, x="accident_date", y="count",color_discrete_sequence=['Green'])
    st.write(line_7day)

## Prepare Data Accident site
station = df.expw_step.value_counts().index.tolist()
station_data = df.expw_step.value_counts().tolist()
d = {'station':station, 'count':station_data}
df_station = pd.DataFrame(data=d)

## Donut Cart Data Accident site
with r1c2:
    st.markdown('### ทางพิเศษที่เกิดอุบัติเหตุ')
    plost.pie_chart(
        data=df_station,
        theta='count',
        color='station',
        legend='bottom', 
        use_container_width=True,height=400)


## Prepare Data All Count
accdate = {'accident_date':df.accident_date.value_counts().sort_index().index.tolist(), 'count':df.accident_date.value_counts().sort_index().tolist()}
df_accdate = pd.DataFrame(data=accdate)
## Line Chart All Count
st.markdown('### จำนวนครั้งที่เกิดอุบัติเหตุ')
st.line_chart(df_accdate, x = 'accident_date', y = 'count', height = plot_height)

r2c1, r2c2 = st.columns((5,5))

## Cause of Accident
with r2c1:
    st.markdown('### สาเหตุที่เกิดอุบัติเหตุ')
    cause = {'cause':df.cause.value_counts().sort_values().index.tolist()[-9:], 'count':df.cause.value_counts().sort_values().tolist()[-9:]}
    df_cause = pd.DataFrame(data=cause)
    fig=px.bar(df_cause,x='cause',y='count',labels={
        'cause' : 'สาเหตุ',
        'count': 'จำนวนครั้ง'
    })
    st.write(fig)

## Period Time Most Accident
with r2c2:
    st.markdown('### ช่วงเวลาที่เกิดอุบัติเหตุ')
    his = px.histogram(df, y="time",color_discrete_sequence=['indianred'],orientation='h',labels={
        'time':''
    })
    st.write(his)
    
## Table Injury & Dead
st.markdown('### ผู้บาดเจ็บและเสียชีวิต')
dfs = df.groupby(['month','year'],as_index = False).sum().sort_values(by=['month','year']).drop(['_id'],axis=1)
dfs['month'] = dfs['month'].apply(lambda m: calendar.month_name[m])
st.table(dfs)

