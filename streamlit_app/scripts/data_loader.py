import pandas as pd
import streamlit as st
from pathlib import Path
import ssl
import certifi
import urllib.request

# Using Streamlit's caching to speed up repeated data loading
@st.cache_data

def load_data(filepath="./data/processed/pm25_cleaned.csv"):
    """
    This function loads the cleaned PM2.5 dataset from the given filepath.
    It also extracts the 'Year' from the 'Period' column and adds it as a new column.

    Parameters:
    - filepath: The file path to the CSV file containing the cleaned dataset

    Returns:
    - df: The cleaned DataFrame with an additional 'Year' column
    """

    # Option 3
    url="https://raw.githubusercontent.com/zkhechadoorian/pm25/refs/heads/main/data/processed/pm25_cleaned.csv"
    # Create an SSL context using certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    # Fetch the CSV file from the URL
    with urllib.request.urlopen(url, context=ssl_context) as response:
        df = pd.read_csv(response)
    return df

    # Option 1
"""
    # Load the data from the provided CSV file path
    df = pd.read_csv(filepath)
    
    # Convert the 'Period' column (which represents year in string format) to datetime and extract the year
    df['Year'] = pd.to_datetime(df['Period'], format='%Y').dt.year  # Only extract the year part
    
    # Return the dataframe with the new 'Year' column
    return df

        # Option 2
    # Get the absolute path relative to the script's location
    base_path = Path(__file__).parent.parent.parent  # Adjust based on your directory structure
    absolute_path = base_path / filepath
    df = pd.read_csv(absolute_path)
    df['Year'] = pd.to_datetime(df['Period'], format='%Y').dt.year
    return df
"""
