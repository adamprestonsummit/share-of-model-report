import streamlit as st
import pandas as pd
import altair as alt # Excellent for interactive Streamlit charts
import numpy as np

# --- Configuration ---
st.set_page_config(
    layout="wide", 
    page_title="Share of Model Report: AI Visibility",
    initial_sidebar_state="expanded"
)

# --- Data Loading (Crucial for Performance) ---
# @st.cache_data ensures the app loads the data ONLY ONCE, 
# even if a user interacts with filters or buttons.
@st.cache_data
def load_data():
    try:
        # Streamlit Cloud finds the CSV file in the root of the repository
        df = pd.read_csv('share_of_model_data.csv')
        
        # Ensure the boolean column is correct for calculations
        df['rank_1_survived_ai'] = df['rank_1_survived_ai'].astype(bool)
        
        # Add a simple 'Category' for filtering in the demo
        # NOTE: You may want to replace this with a real category column 
        # that you define when you generate your 10k keywords.
        conditions = [
            df['keyword'].str.contains('crm|software|saas'),
            df['keyword'].str.contains('food|air fryer|recipe'),
            df['keyword'].str.contains('shoe|boot|hiking|apparel')
        ]
        choices = ['Software/SaaS', 'Consumer Goods/Food', 'Apparel/Footwear']
        df['category'] = np.select(conditions, choices, default='Other')
        
        return df
    except FileNotFoundError:
        st.error("Data file 'share_of_model_data.csv' not found. Ensure it is committed to your GitHub repo.")
        return pd.DataFrame()

data_df = load_data() 

# --- App Layout and Logic ---

if not data_df.empty:
    
    # --- Sidebar Filtering ---
    st.sidebar.header("Filter Data Set")
    
    # Category Filter
    categories = data_df['category'].unique()
    selected_category = st.sidebar.selectbox(
        "Filter by Industry Category:", 
        ['All'] + list(categories)
    )

    if selected_category != 'All':
        filtered_df = data_df[data_df['category'] == selected_category]
    else:
        filtered_df = data_df

    # --- Calculations for Filtered Data ---
    total_keywords = len(filtered_df)
    survived_count = filtered_df['rank_1_survived_ai'].sum()
    survival_rate = (survived_count / total_keywords) * 100 if total_keywords > 0 else 0
    at_risk_count = total_keywords - survived_count
    
    # --- HEADER & METRICS ---
    st.title("🤖 Share of Model Report: Visibility in AI Search")
    st.markdown(f"### Analysis Scope: {selected_category} ({total_keywords:,} Keywords)")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        label="Overall Rank #1 Survival Rate (Cited by AI)",
        value=f"{survival_rate:.1f}%",
        delta=f"-{100 - survival_rate:.1f}% At Risk" if survival_rate < 100 else None,
        delta_color="inverse" # Makes negative delta red (good for 'At Risk' metric)
    )
    col2.metric("Total Keywords Analyzed", f"{total_keywords:,}")
    col3.metric("Rank #1 Brands Ignored by AI", f"{at_risk_count:,}")

    st.markdown("---")

    # --- VISUALIZATION: Survival Rate by Category ---
    st.header("Survival Rate Breakdown")
    
    # Calculate aggregate survival rate per category
    category_summary = data_df.groupby('category')['rank_1_survived_ai'].mean().reset_index()
    category_summary.columns = ['Category', 'Survival Rate']
    category_summary['Survival Rate'] = category_summary['Survival Rate'] * 100

    chart = alt.Chart(category_summary).mark_bar().encode(
        x=alt.X('Survival Rate', axis=alt.Axis(title='Survival Rate (%)', format='.1f')),
        y=alt.Y('Category', sort='-x'),
        tooltip=['Category', alt.Tooltip('Survival Rate', format='.1f')],
        color=alt.Color('Survival Rate', scale=alt.Scale(range=['#e4575e', '#59a14f'], domain=[0, 100]))
    ).properties(
        title="Rank #1 Survival Rate in AI by Industry"
    ).interactive() # Enable zoom and pan

    st.altair_chart(chart, use_container_width=True)
    

    st.markdown("---")
    
    # --- DATA TABLE: Invisible Giants ---
    st.header(f"Data Deep Dive: The 'Invisible Giants' (Ignored by AI)")
    
    # Filter for the brands that failed the check
    invisible_giants = filtered_df[filtered_df['rank_1_survived_ai'] == False]
    
    # Show the top 20 examples
    st.subheader(f"Top 20 Examples of Failing Keywords (Total: {len(invisible_giants):,})")
    
    display_cols = ['keyword', 'google_top_1_brand', 'llm_recs']
    
    # Clean up the display column for the LLM recommendations
    display_df = invisible_giants[display_cols].copy()
    display_df['llm_recs'] = display_df['llm_recs'].apply(lambda x: ', '.join(eval(x)) if pd.notnull(x) and x.startswith('[') else x)

    st.dataframe(display_df.head(20).set_index('keyword'), use_container_width=True)

# --- Error Handling for Empty Data ---
else:
    st.warning("Dataframe is empty. Please ensure your 'share_of_model_data.csv' file has data.")
