import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import urllib.parse
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="🍔 Online Food Delivery Analysis", layout="wide")
st.title("🍔 Online Food Delivery Analysis")

user = "root"
password = "Welcome@4533"
host = "localhost"
port = "3306"
database = "food_delivery"
table_name = "orders"

try:
    password_encoded = urllib.parse.quote_plus(password)
    engine = create_engine(f"mysql+mysqlconnector://{user}:{password_encoded}@{host}:{port}/{database}")
    df = pd.read_sql(f"SELECT * FROM {table_name}", con=engine)
except Exception as e:
    st.error(f"Error connecting to MySQL: {e}")
    st.stop()

df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

for col in df.select_dtypes(include=np.number).columns:
    df[col] = df[col].fillna(df[col].median())

for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].fillna(df[col].mode()[0])

if 'delivery_rating' in df.columns:
    df['delivery_rating'] = df['delivery_rating'].apply(lambda x: min(x,5))
if 'restaurant_rating' in df.columns:
    df['restaurant_rating'] = df['restaurant_rating'].apply(lambda x: min(x,5))

if 'order_date' in df.columns:
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce', infer_datetime_format=True)
    df = df.dropna(subset=['order_date'])

st.sidebar.header("Filters")

def multiselect_filter(col_name, df_filtered):
    if col_name in df_filtered.columns:
        options = df_filtered[col_name].dropna().unique()
        selected = st.sidebar.multiselect(f"Select {col_name.replace('_',' ').title()}", options, default=list(options))
        df_filtered = df_filtered[df_filtered[col_name].isin(selected)]
    return df_filtered

filtered_df = df.copy()
filtered_df = multiselect_filter('city', filtered_df)
filtered_df = multiselect_filter('area', filtered_df)
filtered_df = multiselect_filter('cuisine_type', filtered_df)
filtered_df = multiselect_filter('order_status', filtered_df)
filtered_df = multiselect_filter('payment_mode', filtered_df)

if 'order_date' in filtered_df.columns:
    min_date = filtered_df['order_date'].min().date()
    max_date = filtered_df['order_date'].max().date()
    date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df['order_date'] >= pd.to_datetime(start_date)) & 
                                  (filtered_df['order_date'] <= pd.to_datetime(end_date))]

st.subheader("📊 Key Metrics")
cols = st.columns(4)

if 'order_id' in filtered_df.columns:
    cols[0].metric("Total Orders", filtered_df['order_id'].nunique())
if 'final_amount' in filtered_df.columns:
    cols[1].metric("Total Revenue", f"${filtered_df['final_amount'].sum():,.2f}")
    cols[2].metric("Average Order Value", f"${filtered_df['final_amount'].mean():,.2f}")
if 'delivery_time_min' in filtered_df.columns:
    cols[3].metric("Average Delivery Time (min)", f"{filtered_df['delivery_time_min'].mean():.2f}")

if 'order_status' in filtered_df.columns:
    cancel_rate = (filtered_df['order_status']=='Cancelled').mean()*100
    st.metric("Cancellation Rate", f"{cancel_rate:.2f}%")

if 'profit_margin' in filtered_df.columns:
    st.metric("Average Profit Margin %", f"{filtered_df['profit_margin'].mean():.2f}%")

if 'delivery_rating' in filtered_df.columns:
    st.metric("Avg Delivery Rating", f"{filtered_df['delivery_rating'].mean():.2f}/5")

if 'restaurant_rating' in filtered_df.columns:
    st.metric("Avg Restaurant Rating", f"{filtered_df['restaurant_rating'].mean():.2f}/5")

st.subheader("📈 Visual Analytics")

def bar_chart(col_name, title):
    if col_name in filtered_df.columns:
        st.markdown(f"### {title}")
        st.bar_chart(filtered_df[col_name].value_counts())

def pie_chart(col_name, title):
    if col_name in filtered_df.columns:
        st.markdown(f"### {title}")
        counts = filtered_df[col_name].value_counts()
        fig, ax = plt.subplots()
        ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')
        st.pyplot(fig)

bar_chart('city', 'Orders by City')
bar_chart('area', 'Orders by Area')
bar_chart('cuisine_type', 'Orders by Cuisine')
bar_chart('order_day', 'Weekday vs Weekend Orders')
bar_chart('peak_hour', 'Peak Hour Orders')
bar_chart('restaurant_name', 'Top 10 Restaurants by Orders')
bar_chart('delivery_partner_id', 'Top 10 Delivery Partners by Orders')

pie_chart('payment_mode', 'Payment Mode Distribution')
pie_chart('cancellation_reason', 'Cancellation Reasons')

# Revenue Over Time
if 'order_date' in filtered_df.columns and 'final_amount' in filtered_df.columns:
    st.markdown("### Revenue Over Time")
    revenue_time = filtered_df.groupby('order_date')['final_amount'].sum()
    st.line_chart(revenue_time)

# Delivery Time vs Distance
if 'delivery_time_min' in filtered_df.columns and 'distance_km' in filtered_df.columns:
    st.markdown("### Delivery Time vs Distance")
    fig, ax = plt.subplots()
    sns.scatterplot(data=filtered_df, x='distance_km', y='delivery_time_min', hue='order_status', ax=ax)
    st.pyplot(fig)

# Customer Age Groups
if 'customer_age' in filtered_df.columns:
    st.markdown("### Orders by Customer Age Group")
    bins = [0,18,25,35,45,60,100]
    labels = ['<18','18-25','26-35','36-45','46-60','60+']
    filtered_df['age_group'] = pd.cut(filtered_df['customer_age'], bins=bins, labels=labels)
    st.bar_chart(filtered_df['age_group'].value_counts())

st.subheader("Filtered Data Table")
st.dataframe(filtered_df)
