import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Load the data
path = "./data"
@st.cache_data
def load_data_daily_1():
    return pd.read_csv(path+'/level_1_daily.csv', parse_dates=['date'])
@st.cache_data
def load_data_daily_2():
    return pd.read_csv(path+'/level_2_daily.csv', parse_dates=['date'])

# Load the data
@st.cache_data
def load_data_total_1():
    return pd.read_csv(path+'/level_1_total.csv')
# Load the data
@st.cache_data
def load_data_total_2():
    return pd.read_csv(path+'/level_2_total.csv')

# Sidebar for filtering
st.sidebar.header("Filter Data")
# select level data
selected_level = st.sidebar.selectbox("Select Level", ["level 1", "level 2"])
# if nothing selected, select level 1
if selected_level == "": # default to level 1
    selected_level = "level 1"
    data = load_data_daily_1()
    total_data = load_data_total_1()
    message = """
    First pass in cleaning out profiles data. Level 1: low level de-plucation of linkedin_url and email.
    """
if selected_level == "level 1":
    data = load_data_daily_1()
    total_data = load_data_total_1()
    message = """
    First pass in cleaning out profiles data. Level 1: low level de-plucation of linkedin_url and email.
    """
if selected_level == "level 2":
    data = load_data_daily_2()
    total_data = load_data_total_2()
    message = """
    Level 2, a more in-depth cleaning of profiles. higher level de-duplication of linkedin_url, handling supsicious emails, 
    no name, same name, and other anomalies.
    """


#data = load_data()
data['month_year'] = data['date'].dt.strftime('%m-%Y')

#total_data = load_data()
# 
total_profiles = total_data['total_profiles'].values[0]
monthly_avg = total_data['monthly_avg'].values[0]
annual_growth_YOY = total_data['annual_growth_YOY'].values[0]

# Sidebar for filtering
st.sidebar.header("Filter Data")
selected_year = st.sidebar.selectbox("Select Year", sorted(list(data['date'].dt.year.unique()), reverse=True))
# list of months
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October','November','December']


selected_month_str = st.sidebar.selectbox("Select Month", months, index=0)
# convert month name to number
selected_month = datetime.strptime(selected_month_str, "%B").month

# Filter data based on user input
filtered_data_year = data[(data['date'].dt.year == selected_year)]
filtered_data_month = data[(data['date'].dt.year == selected_year) & (data['date'].dt.month == selected_month)] 

# Calculate KPIs for filtered data
total_unique_profiles_year = filtered_data_year['profile_id'].sum() # yearly number of unique profiles
total_unique_profiles_month = filtered_data_month['profile_id'].sum() # monthly number of unique profiles


# Display KPIs on Streamlit with a prettier layout
st.title("Unique Profiles Data")
st.markdown("""
**Count of unique profiles/people we have in our database**
""")

# Create columns for KPIs
col1, col2, col3 = st.columns([2,1,1])

# Display KPIs in columns with styling
with col1:
    st.subheader("Total Unique Profiles")
    formatted_total_profiles = f"{total_profiles:,}" 
    st.markdown(f"<div style='font-size: 40px; text-align: left; color: green;'>{formatted_total_profiles}</div>", unsafe_allow_html=True)
    #st.markdown(f"**{total_profiles}**", unsafe_allow_html=True)

with col2:
    st.subheader("Monthly Average")
    formatted_monthly_avg = f"{monthly_avg:,.0f}"
    st.markdown(f"<div style='font-size: 30px; text-align: left; color: blue;'>{formatted_monthly_avg}</div>", unsafe_allow_html=True)
    #st.markdown(f"**{formatted_monthly_avg}**", unsafe_allow_html=True)

with col3:
    st.subheader("YoY Growth")
    formatted_yoy_avg = f"{annual_growth_YOY:.2f}%"
    st.markdown(f"<div style='font-size: 30px; text-align: left; color: black;'>{formatted_yoy_avg}</div>", unsafe_allow_html=True)
    #st.markdown(f"**{formatted_monthly_avg}**", unsafe_allow_html=True)

# add markdown
st.markdown(message)

# chart 1
# Create an interactive chart with a rolling average
data['month_year'] = data['date'].dt.to_period('M')
monthly_data = data[data['date'].dt.year > 2018]
monthly_data = monthly_data.groupby('month_year')['profile_id'].sum().reset_index()
monthly_data['rolling_avg'] = monthly_data['profile_id'].rolling(window=3).mean()

# Convert month_year from Period to string
monthly_data['month_year'] = monthly_data['month_year'].astype(str)

fig = px.line(monthly_data, x='month_year', y=['profile_id', 'rolling_avg'], 
        labels={'profile_id': 'Monthly Profiles', 'rolling_avg': 'Rolling Average'}, 
        title='Monthly Profiles with Rolling Average - Total')

# # Update the color of the rolling average to red
fig.data[1].line.color = 'red'
fig.update_layout(xaxis_title="Year", yaxis_title="Profiles", height=325 )
st.plotly_chart(fig)

### --- selected year data and charts --- ###
# subeader
st.subheader(f"Selected Year: {selected_year}")

# Create columns for KPIs
col7, col8 = st.columns(2)

with col7:
    st.subheader(f"Total Unique Profiles: {selected_year}")
    formatted_total_unique_profiles = f"{total_unique_profiles_year:,}"
    st.markdown(f"<div style='font-size: 30px; text-align: left; color: green;'>{formatted_total_unique_profiles}</div>", unsafe_allow_html=True)
    #st.markdown(f"**{formatted_total_unique_profiles}**", unsafe_allow_html=True)

with col8:
    st.subheader(f"Month: {selected_month_str}")
    formatted_total_unique_profiles = f"{total_unique_profiles_month:,}"
    st.markdown(f"<div style='font-size: 30px; text-align: left; color: blue;'>{formatted_total_unique_profiles}</div>", unsafe_allow_html=True)
    #st.markdown(f"**{formatted_total_unique_profiles}**", unsafe_allow_html=True)




# chart 2
# Filter data for the selected month and year for daily chart
# Create an interactive chart with a rolling average

yearly_data = data[(data['date'].dt.year == selected_year)]
yearly_data = yearly_data.groupby(yearly_data['date'].dt.month)['profile_id'].sum().reset_index()
yearly_data['rolling_avg'] = yearly_data['profile_id'].rolling(window=3).mean()

fig_yearly = px.line(yearly_data, x='date', y=['profile_id', 'rolling_avg'], 
                     labels={'profile_id': 'Monthly Profiles', 'rolling_avg': 'Rolling Average'}, 
                     title=f'Monthly Profiles with Rolling Average - {selected_year}')

# Update the color of the rolling average to red
fig_yearly.data[1].line.color = 'red'

fig_yearly.update_layout(xaxis_title="Month", yaxis_title="Profiles", height=300)
st.plotly_chart(fig_yearly)



# chart 3
daily_data = data[(data['date'].dt.year == selected_year) & (data['date'].dt.month == selected_month)]
daily_data = daily_data.groupby(daily_data['date'].dt.day)['profile_id'].sum().reset_index()
daily_data['rolling_avg'] = daily_data['profile_id'].rolling(window=3).mean()

fig_daily = px.line(daily_data, x='date', y=['profile_id', 'rolling_avg'], 
        labels={'profile_id': 'Daily Profiles', 'rolling_avg': 'Rolling Average'}, 
        title=f'Daily Profiles with Rolling Average for {selected_month}/{selected_year}')
        
# Update the color of the rolling average to red
fig_daily.data[1].line.color = 'red'
fig_daily.update_layout(xaxis_title="Day", yaxis_title="Profiles", height=300 )
st.plotly_chart(fig_daily)



