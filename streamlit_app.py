import streamlit as st
import pandas as pd
from pinotdb import connect
import plotly.express as px
import plotly.graph_objects as go

# Establish connection
conn = connect(host='13.229.51.129', port=8099, path='/query/sql', schema='http')

# Create a cursor object
curs = conn.cursor()

# Execute the first query for sales by country
curs.execute(''' 
SELECT 
  COUNTRY, 
  SUM(TOTAL_PRICE) AS totalSales
FROM orders
GROUP BY COUNTRY
ORDER BY totalSales DESC;
''')

# Fetch the results
tables = [row for row in curs.fetchall()]

# Convert results to a DataFrame
df_sales = pd.DataFrame(tables, columns=['COUNTRY', 'totalSales'])

# Map country names to Plotly's ISO-3166-1 alpha-3 codes
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

# Replace the country names with their corresponding country codes
df_sales['COUNTRY_CODE'] = df_sales['COUNTRY'].map(country_map)

# Create a choropleth map using Plotly
fig_sales = px.choropleth(df_sales, 
                          locations='COUNTRY_CODE', 
                          color='totalSales', 
                          hover_name='COUNTRY', 
                          color_continuous_scale='Viridis', 
                          labels={'totalSales': 'Total Sales ($)', 'COUNTRY': 'Country'},
                          title='Total Sales by Country')

# Execute the second query for product sales and quantities
curs.execute(''' 
SELECT 
  TYPE, 
  SUM(QUANTITY) AS totalQuantity,
  SUM(TOTAL_PRICE) AS totalSales
FROM orders
GROUP BY TYPE
ORDER BY totalQuantity DESC;
''')

# Fetch the results
tables = [row for row in curs.fetchall()]

# Convert results to a DataFrame
df_product = pd.DataFrame(tables, columns=['TYPE', 'totalQuantity', 'totalSales'])

# Create a fancy table using Plotly
fig_product = go.Figure(data=[go.Table(
    header=dict(values=["Product Type", "Total Quantity", "Total Sales"]),
    cells=dict(values=[df_product['TYPE'], df_product['totalQuantity'], df_product['totalSales']])
)])

# Customize the table style
fig_product.update_layout(
    title="Total Quantity and Sales by Product Type",
    title_x=0.5,
    margin={"t": 20, "b": 20},
    height=400
)

# Streamlit layout: two columns
col1, col2 = st.columns(2)

# Display the maps and tables in the respective columns
with col1:
    st.plotly_chart(fig_sales)
    
with col2:
    st.plotly_chart(fig_product)
