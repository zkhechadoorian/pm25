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
st.set_page_config(page_title="Urban PM2.5 Overview", layout="wide")
st.title("🌆 Urban PM2.5 Air Quality Overview")  # Dashboard title

# ========================= Load Data ==========================
df = load_data()                     # Load the cleaned and structured dataset
latest_year = df['Period'].max()      # Get the most recent year for default filter

# ========================= Sidebar Filters ==========================
st.sidebar.header("Filters")

# Year slider for selecting a specific year
selected_year = st.sidebar.slider(
    "Select Year",
    min_value=int(df['Period'].min()),
    max_value=int(df['Period'].max()),
    value=int(latest_year)
)

# Multiselect filter for choosing regions (e.g., continents)
selected_regions = st.sidebar.multiselect(
    "Select Regions",
    options=df['ParentLocation'].unique(),
    default=df['ParentLocation'].unique()  # All regions selected by default
)

# ========================= Apply Filters ==========================
# Filter data based on year and selected regions
filtered_df = df[
    (df['Period'] == selected_year) &
    (df['ParentLocation'].isin(selected_regions))
]

# ========================= Main Tabs ==========================
tab1, tab2, tab3 = st.tabs(["Global Overview", "Regional Analysis", "Data Explorer"])

# ========================= Tab 1: Global Overview ==========================
with tab1:
    st.header("Global PM2.5 Overview")

    col1, col2 = st.columns(2)  # Two visual columns side-by-side

    # Choropleth map of PM2.5 levels by country
    with col1:
        st.plotly_chart(
            create_choropleth(filtered_df, selected_year),
            use_container_width=True
        )

    # Bar chart for most polluted countries
    with col2:
        st.plotly_chart(
            create_pollution_barchart(filtered_df, selected_year),
            use_container_width=True
        )

# ========================= Tab 2: Regional Analysis ==========================
with tab2:
    st.header("Regional Analysis")

    # Box plot to show PM2.5 distribution by region
    st.subheader("PM2.5 Distribution by Region")
    st.plotly_chart(
        create_box_plot(filtered_df),
        use_container_width=True
    )

    # Line chart to show trend over time (all years)
    st.subheader("PM2.5 Trends Over Time")
    trend_df = df.groupby(['Period', 'ParentLocation'])['FactValueNumeric'].mean().reset_index()
    st.plotly_chart(
        create_trend_plot(trend_df, x_column="Period"),  # Specify Year as x-axis
        use_container_width=True
    )

# ========================= Tab 3: Data Explorer ==========================
with tab3:
    st.header("Data Explorer")

    # Function to show a simplified, renamed table view for users
    def show_data_table(df):
        return st.dataframe(
            df[[
                'Location', 'ParentLocation', 'Period', 
                'FactValueNumeric', 'Dim1'
            ]].rename(columns={
                'Location': 'City',
                'ParentLocation': 'Region',
                'FactValueNumeric': 'PM2.5 (µg/m³)',
                'Dim1': 'Area Type'
            }),
            hide_index=True,
            use_container_width=True,
            height=400
        )

    # Show table
    show_data_table(filtered_df)

    # CSV download button for the current filtered data
    st.download_button(
        label="Download Current View",
        data=filtered_df.to_csv(index=False),
        file_name=f"pm25_data_{selected_year}.csv",
        mime="text/csv"
    )

# ========================= Sidebar Key Metrics ==========================
# Calculate metrics from the filtered data
metrics = calculate_metrics(filtered_df)

# Display key metrics in the sidebar
st.sidebar.header("Key Metrics")
st.sidebar.metric("Average PM2.5", f"{metrics['average_pm25']:.1f} µg/m³")
st.sidebar.metric("Highest PM2.5", f"{metrics['max_pm25']:.1f} µg/m³")
st.sidebar.metric("Lowest PM2.5", f"{metrics['min_pm25']:.1f} µg/m³")

# ========================= Sidebar About Section ==========================
# Function to show static dashboard info
def show_about():
    st.sidebar.header("About")
    st.sidebar.info("""
    This dashboard visualizes urban PM2.5 concentration data from the WHO.
    PM2.5 refers to atmospheric particulate matter ≤ 2.5 μm in diameter.
    It is a critical pollutant linked to respiratory and cardiovascular health risks.
    """)

# Show About section
show_about()
