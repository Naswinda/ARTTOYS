import streamlit as st
import pandas as pd
from pinotdb import connect
import plotly.express as px
import plotly.graph_objects as go

# Set up page layout
st.set_page_config(layout="wide")

# Page title and subtitle
st.title("NANAS ARTTOYS 🧸")
st.subheader("Squeeze the Fun, Taste the Joy!")

# Connect to PinotDB
conn = connect(host='13.229.51.129', port=8099, path='/query/sql', schema='http')
curs = conn.cursor()

# Query for product types, total quantity, and total sales
curs.execute(''' 
SELECT 
  TYPE, 
  SUM(QUANTITY) AS totalQuantity,
  SUM(TOTAL_PRICE) AS totalSales
FROM orders
GROUP BY TYPE
ORDER BY totalQuantity DESC;
''')
tables = [row for row in curs.fetchall()]
df_product = pd.DataFrame(tables, columns=['TYPE', 'totalQuantity', 'totalSales'])

# Format the totalSales to 2 decimal places
df_product['totalSales'] = df_product['totalSales'].apply(lambda x: f"{x:.2f}")

# Product table visualization
fig_product = go.Figure(data=[go.Table(
    header=dict(values=["Product Type", "Total Quantity", "Total Sales"]),
    cells=dict(values=[df_product['TYPE'], df_product['totalQuantity'], df_product['totalSales']])
)])

fig_product.update_layout(
    title="Total Quantity and Sales by Product Type",
    title_x=0.5,
    margin={"t": 20, "b": 20},
    height=400
)

# Query for sales by country
curs.execute(''' 
SELECT 
  COUNTRY, 
  SUM(TOTAL_PRICE) AS totalSales
FROM orders
GROUP BY COUNTRY
ORDER BY totalSales DESC;
''')


tables = [row for row in curs.fetchall()]
df_sales = pd.DataFrame(tables, columns=['COUNTRY', 'totalSales'])


country_map = {
    'Thailand': 'THA',
    'China': 'CHN',
    'Singapore': 'SGP',
    'Hong Kong': 'HKG',
    'Japan': 'JPN',
    'Malaysia': 'MYS',
    'Korea': 'KOR',
    'Vietnam': 'VNM',
    'Australia': 'AUS'
}


df_sales['COUNTRY_CODE'] = df_sales['COUNTRY'].map(country_map)


fig_sales = px.choropleth(df_sales, 
                          locations='COUNTRY_CODE', 
                          color='totalSales', 
                          hover_name='COUNTRY', 
                          color_continuous_scale='Viridis', 
                          labels={'totalSales': 'Total Sales ($)', 'COUNTRY': 'Country'},
                          title='Total Sales by Country')
# Query for hourly sales
curs.execute(''' 
SELECT 
  SUBSTR(ORDER_TIMESTAMP, 1, 13) AS hour,  -- YYYY-MM-DDTHH
  SUM(TOTAL_PRICE) AS totalSales
FROM orders
GROUP BY hour
ORDER BY hour;
''')


tables = [row for row in curs.fetchall()]
hours = [f"{row[0][10:13]}:00" for row in tables]
total_sales = [row[1] for row in tables]


fig_hourly_sales = go.Figure()
fig_hourly_sales.add_trace(go.Scatter(
    x=hours, 
    y=total_sales, 
    mode='lines+markers',
    name='Total Sales',
    line=dict(color='blue'),
    marker=dict(size=8)
))


fig_hourly_sales.update_layout(
    title='Hourly Total Sales',
    xaxis_title='Times',
    yaxis_title='Total Sales',
    xaxis=dict(
        tickangle=45, 
        type='category',  
        categoryorder='array', 
        categoryarray=['10:00', '11:00', '12:00', '13:00', '14:00']  
    ),
    template='plotly_white',
    height=500,
    width=900
)
# Query for gender distribution
curs.execute(''' 
SELECT 
  gender, 
  COUNT(*) AS userCount
FROM 2_users
GROUP BY gender
ORDER BY userCount DESC;
''')
tables = [row for row in curs.fetchall()]
genders = [row[0] for row in tables]
user_counts = [row[1] for row in tables]

# Gender distribution pie chart
fig_gender_pie = go.Figure(go.Pie(
    labels=genders,
    values=user_counts,
    hole=0.3,
    textinfo='label+percent',
    marker=dict(colors=['#FF9999', '#66B3FF'])
))

fig_gender_pie.update_layout(
    title='Gender Distribution of Users',
    template='plotly_white',
    height=500,
    width=500
)

# Layout with columns
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_product)
with col2:
    st.plotly_chart(fig_hourly_sales)

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(fig_sales)
with col4:
    st.plotly_chart(fig_gender_pie)
