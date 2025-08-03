import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Page Config
st.set_page_config(page_title="Climate Dashboard", layout="wide")

st.title("🌦️ Indian Cities Climate Dashboard")
st.write("Upload your weather dataset (CSV) to visualize Heatwaves, Rainfall Trends, and Temperature Patterns.")

# File Upload
uploaded_file = st.file_uploader("Upload your Weather CSV", type=['csv'])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Preprocess Dates
    df['time'] = pd.to_datetime(df['time'], dayfirst=True, errors='coerce')
    df['Year'] = df['time'].dt.year
    df['Month'] = df['time'].dt.month

    # Clean Columns
    df['prcp'] = pd.to_numeric(df['prcp'], errors='coerce')
    df['tmax'] = pd.to_numeric(df['tmax'], errors='coerce')
    df['tavg'] = pd.to_numeric(df['tavg'], errors='coerce')

    # Sidebar Filters
    min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
    year_range = st.sidebar.slider('Select Year Range', min_year, max_year, (min_year, max_year))
    heatwave_threshold = st.sidebar.slider('Heatwave Threshold (°C)', 30, 45, 35)

    # Filter Data by Year
    df_filtered = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]

    # Heatwave Days Calculation
    heatwave_days = df_filtered[df_filtered['tmax'] > heatwave_threshold]
    heatwave_trend = heatwave_days.groupby('Year').size().reset_index(name='Heatwave_Days')
    heatwave_trend['5yr_Rolling_Avg'] = heatwave_trend['Heatwave_Days'].rolling(window=5).mean()

    # Rainfall Trend
    rainfall_trend = df_filtered.groupby('Year')['prcp'].sum().reset_index()

    # Monthly Heatwave Distribution
    monthly_heatwave = heatwave_days['Month'].value_counts().sort_index()

    # Temperature Category Distribution
    def temp_category(temp):
        if temp < 20:
            return 'Cool (<20°C)'
        elif 20 <= temp < 25:
            return 'Warm (20-25°C)'
        elif 25 <= temp < 30:
            return 'Hot (25-30°C)'
        else:
            return 'Very Hot (30°C+)'
    df_filtered['Temp_Category'] = df_filtered['tavg'].apply(temp_category)
    category_counts = df_filtered['Temp_Category'].value_counts()

    # Seaborn Theme
    sns.set_theme(style="whitegrid", palette="muted")

    # Layout: 2x2 Grid
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    # Heatwave Trendline
    with col1:
        fig, ax = plt.subplots(figsize=(8,5))
        sns.lineplot(data=heatwave_trend, x='Year', y='Heatwave_Days', label='Actual', color='gray', linestyle='--', marker='o', ax=ax)
        sns.lineplot(data=heatwave_trend, x='Year', y='5yr_Rolling_Avg', label='5yr Rolling Avg', color='red', ax=ax)
        ax.set_title('Heatwave Days Trend')
        ax.set_ylabel('Days > {}°C'.format(heatwave_threshold))
        ax.set_xlabel('Year')
        st.pyplot(fig)

    # Rainfall Trend
    with col2:
        fig, ax = plt.subplots(figsize=(8,5))
        sns.barplot(data=rainfall_trend, x='Year', y='prcp', color='navy', ax=ax)
        ax.set_title('Annual Rainfall Trend')
        ax.set_ylabel('Total Precipitation (mm)')
        ax.set_xticklabels(ax.get_xticks(), rotation=45)
        st.pyplot(fig)

    # Monthly Heatwave Distribution
    with col3:
        fig, ax = plt.subplots(figsize=(8,5))
        sns.barplot(x=monthly_heatwave.index, y=monthly_heatwave.values, palette="flare", ax=ax)
        ax.set_title('Monthly Heatwave Distribution')
        ax.set_xlabel('Month')
        ax.set_ylabel('Heatwave Days')
        st.pyplot(fig)

    # Temperature Distribution Pie Chart
    with col4:
        fig, ax = plt.subplots(figsize=(6,6))
        colors = sns.color_palette("coolwarm", len(category_counts))
        ax.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', startangle=140, colors=colors)
        ax.set_title('Temperature Distribution')
        st.pyplot(fig)

else:
    st.info("Upload a weather dataset to get started!")

