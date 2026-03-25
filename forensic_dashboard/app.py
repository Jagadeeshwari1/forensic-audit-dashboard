import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="OTB Forensic Audit: NY", layout="wide")

# --- DATA LOAD ---
@st.cache_data
def load_data():
    df = pd.read_csv('audit_data_5year.csv')
    ny_df = df[df['area_title'].str.contains("New York", na=False)].copy()
    return df, ny_df

df, ny_df = load_data()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🔍 Audit Menu")
page = st.sidebar.radio("Navigate to:", ["1. Overview", "2. Jobs Audit", "3. New York Deep-Dive", "4. Efficiency Index"])

# --- PAGE 1: OVERVIEW ---
if page == "1. Overview":
    st.title("🏛️ Project Overview: The Taxpayer Price Tag")
    st.info("**Logic:** We measure federal efficiency by asking: *How much does it cost the taxpayer to support one local job?*")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("How we did it")
        st.write("- **Data:** 5-Year Study (2020-2024)")
        st.write("- **Sources:** BLS Labor Stats + Federal Earmark Records")
        st.write("- **Cleaning:** Focused on Private Sector vs. Gov Earmarks")
    
    st.error("**The Goal:** Identify 'Market Perversions' where gov spending per job exceeds the worker's actual salary.")

# --- PAGE 2: JOBS AUDIT ---
elif page == "2. Jobs Audit":
    st.title("📊 Jobs Audit: Gov vs. Private Spending")
    fig = px.bar(df, x='area_title', y=['avg_annual_pay', 'Efficiency_Index'], 
                 barmode='group', title="Cost per Job vs. Market Salary")
    st.plotly_chart(fig, use_container_width=True)
    st.warning("**Interpretation:** If the red bar (Gov Spending) is higher than the blue bar (Salary), the government is overpaying for economic growth.")

# --- PAGE 3: NEW YORK DEEP-DIVE ---
elif page == "3. New York Deep-Dive":
    st.title("🍎 New York Deep-Dive")
    st.write(f"Auditing the **$1.88 Billion** FY2024 New York Earmark Pool.")
    
    # Highlight Market Perversion
    perverted_counties = ny_df[ny_df['Efficiency_Index'] > ny_df['avg_annual_pay']]
    st.metric("Counties with Market Perversion", len(perverted_counties))
    
    st.dataframe(ny_df[['area_title', 'avg_annual_pay', 'Efficiency_Index', 'Audit_Risk_Level']], use_container_width=True)
    st.write("**Non-Technical Note:** When 'Efficiency Index' is higher than 'Avg Pay', the job costs more than it's worth.")

# --- PAGE 4: EFFICIENCY INDEX ---
elif page == "4. Efficiency Index":
    st.title("🛡️ Taxpayer Burden & Efficiency")
    fig = px.scatter(df, x='avg_annual_pay', y='Efficiency_Index', size='Efficiency_Index', 
                     color='Audit_Risk_Level', hover_name='area_title')
    st.plotly_chart(fig, use_container_width=True)
    st.info("**Logic:** The higher the dot, the more inefficient the taxpayer dollar.")
