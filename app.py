# app.py snippet for Streamlit Cloud
import streamlit as st
import pandas as pd

# This tells Streamlit Cloud to load the CSV file saved in the GitHub repository ONCE.
@st.cache_data 
def load_data():
    # Streamlit will find the file in the repository's root directory
    df = pd.read_csv('share_of_model_data.csv') 
    df['rank_1_survived_ai'] = df['rank_1_survived_ai'].astype(bool)
    return df

data_df = load_data() 

# (The rest of your code for metrics, charts, and tables follows)
# ...
