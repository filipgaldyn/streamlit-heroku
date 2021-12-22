import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime
import os
st.set_page_config(layout="wide")
st.title('PIAD')

st.markdown("""
This app performs simple serching data and calculate correlation!
* **Python libraries:** base64, pandas, streamlit
""")
dirname = os.path.dirname(os.path.abspath("__file__"))
directory = os.path.join(dirname,"Data")
data_list = os.listdir(directory)

selected_data = st.sidebar.selectbox('Data', data_list)
today = datetime.date.today()
st.sidebar.header('User Input Features')
start_date = st.sidebar.date_input('Start date', datetime.date(2020,5,1))
end_date = st.sidebar.date_input('End date', datetime.date(2020,6,1))
#if start_date < end_date:
#    st.success('Start date: `%s`\n\nEnd date: `%s`' % (start_date, end_date))
#else:
#    st.error('Error: End date must fall after start date.')


file = "Data/{}".format(str(selected_data))
if selected_data == "dane inklinometry.txt":
    tach = pd.read_csv(file, delimiter='\t', encoding='unicode_escape', names=["Sensor", "Time", "Inclination X [mm/m]", "Inclination Y [mm/m]", "Nivel Temperature[stC]"])
    tach = tach.set_index("Time")
    tach.index = pd.to_datetime(tach.index, format="%d-%m-%Y %H:%M:%S")
    sorted_unique_team = sorted(tach.loc[:,'Sensor'].unique())
    selected_team = st.sidebar.multiselect('Sensor', sorted_unique_team, sorted_unique_team)
    # Sidebar - Position selection
    unique_pos = tach.columns.to_list()
    selected_pos = st.sidebar.multiselect('columns', unique_pos, unique_pos)
    sel_tach = tach[(tach.loc[:,'Sensor'].isin(selected_team))]

elif selected_data.startswith("dane meteo"):
    tach = pd.read_csv(file, delimiter='\t', encoding='unicode_escape', names=["Sensor", "Time", "Temperature [C]", "Pressure [hPa]", "Humidity [%]", "WindDirection", "WindSpeed", "Hail"])
    tach = tach.set_index("Time")
    tach.index = pd.to_datetime(tach.index, format="%d-%m-%Y %H:%M:%S")
    tach["WindDirection"] = pd.to_numeric(tach["WindDirection"], errors='coerce')
    tach["WindSpeed"] = pd.to_numeric(tach["WindSpeed"], errors='coerce')
    sorted_unique_team = sorted(tach.loc[:,'Sensor'].unique())
    selected_team = st.sidebar.multiselect('Sensor', sorted_unique_team, sorted_unique_team)
    # Sidebar - Position selection
    unique_pos = tach.columns.to_list()
    selected_pos = st.sidebar.multiselect('columns', unique_pos, unique_pos)
    sel_tach = tach[(tach.loc[:,'Sensor'].isin(selected_team))]

else:
    tach = pd.read_csv(file, delimiter='\t', encoding= 'unicode_escape')
    tach = tach.set_index("Time")
    tach.index = pd.to_datetime(tach.index, format="%d-%m-%Y %H:%M:%S")

    # Sidebar - Team selection
    sorted_unique_team = sorted(tach.loc[:,'Point ID'].unique())
    selected_team = st.sidebar.multiselect('Point ID', sorted_unique_team, sorted_unique_team)

    # Sidebar - Position selection
    unique_pos = tach.columns.to_list()
    selected_pos = st.sidebar.multiselect('columns', unique_pos, unique_pos)

    # Filtering data
    sel_tach = tach[(tach.loc[:,'Point ID'].isin(selected_team))]

df_selected_team = sel_tach[selected_pos]
df_selected_time = df_selected_team.loc[str(start_date):str(end_date)]


st.header('Display GeoMos results')
st.write('Data Dimension: ' + str(df_selected_time.shape[0]) + ' rows and ' + str(df_selected_time.shape[1]) + ' columns.')
test = df_selected_team.astype(str)
st.dataframe(df_selected_time)


# Download NBA player stats data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="stats.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

# Heatmap
if st.button('Intercorrelation Heatmap'):
    st.header('Intercorrelation Matrix Heatmap')
    df_selected_team.to_csv('output.csv',index=False)
    df = pd.read_csv('output.csv')

    corr = df.corr()
    mask = np.zeros_like(corr)
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()
    