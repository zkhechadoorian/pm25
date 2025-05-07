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
st.set_page_config(page_title="Global PM2.5 Overview", layout="wide")
st.title("🌆 Urban PM2.5 Air Quality Overview")  # Dashboard title

# ========================= Load Data ==========================
df = load_data()                     # Load the cleaned and structured dataset
latest_year = df['Period'].max()      # Get the most recent year for default filter

# Display GIF version of the choropleth animation
st.subheader("PM2.5 Levels by Country (Animated)")
st.write("This animation shows the average PM2.5 levels by country over the years.")
#st.image("https://github.com/zkhechadooorian/pm25/blob/main/notebooks/pm25_choropleth_animation.gif", use_column_width=True)  
st.image("notebooks/pm25_choropleth_animation.gif", use_container_width=False)  # Local file path
