# ====================== Import Required Libraries ======================
import streamlit as st
import pandas as pd
# Import custom scripts for modularity and readability
from scripts.data_loader import load_data                # Function to load and preprocess data
from scripts.filters import apply_filters                # (Optional here, filters are inline)
from scripts.visualizations import (                     # Custom Plotly-based visualization functions
    create_box_plot,
    create_trend_plot,
    create_choropleth,
    create_pollution_barchart
)
from scripts.stats import calculate_metrics              # Function to calculate summary metrics

# ======================== Streamlit Page Setup ========================
st.set_page_config(page_title="Average PM2.5 By Region", layout="wide")
st.title("🌍 Average PM2.5 Levels by Region")  # Dashboard title

# ========================= Load Data ==========================
df = load_data()                     # Load the cleaned and structured dataset

# ========================= Main Tabs ==========================
# One tab for each ParentLocation (region)
regions = df['ParentLocation'].unique()
tabs = st.tabs([f"{region} Overview" for region in regions])

# ========================= Populate Tabs ==========================
# In each tab, display the average PM2.5 levels for each Location in the Region
for region, tab in zip(regions, tabs):
    with tab:
        st.header(f"Region: {region}")  # Region title
        region_df = df[df['ParentLocation'] == region]  # Filter data for the current region
        
        # Prepare chart data to plot average PM2.5 levels over time per Location
        avg_pm25 = region_df.groupby(['Location', 'Period'])['FactValueNumeric'].mean().reset_index()
        avg_pm25 = avg_pm25.rename(columns={'FactValueNumeric': 'Average PM2.5'})
        avg_pm25 = avg_pm25.pivot(index='Period', columns='Location', values='Average PM2.5')
        avg_pm25 = avg_pm25.reset_index()
        avg_pm25 = avg_pm25.fillna(0)

        # Display a bar chart of average PM2.5 levels by Location with the Top 10 Locations
        top_locations = avg_pm25.iloc[:, 1:].mean().nlargest(10).index.tolist()
        avg_pm25 = avg_pm25[['Period'] + top_locations]
        # Display the bar chart of average PM2.5 levels
        #st.subheader("Average PM2.5 Levels Bar Chart")
        #st.bar_chart(avg_pm25.set_index('Period'), use_container_width=True)
        
        # Display a line plot of average PM2.5 levels over time with the Top 10 Locations
        st.subheader("Average PM2.5 Levels Over Time")
        st.line_chart(avg_pm25.set_index('Period'), use_container_width=True)