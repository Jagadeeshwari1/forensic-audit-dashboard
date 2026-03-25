import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="NY Forensic Audit Dashboard", layout="wide")

# --- 2. ROBUST DATA LOADING ---
@st.cache_data
def load_data():
    # This logic automatically finds the file whether it is in the root or a subfolder
    possible_paths = [
        'audit_data_5year.csv', 
        'forensic_dashboard/audit_data_5year.csv'
    ]
    
    df = None
    for path in possible_paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            break
            
    if df is None:
        st.error("🚨 Error: 'audit_data_5year.csv' not found. Please ensure it is uploaded to your GitHub repository.")
        st.stop()
        
    # Standardize New York filtering
    ny_df = df[df['area_title'].str.contains("New York", case=False, na=False)].copy()
    return df, ny_df

df, ny_df = load_data()

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("🔍 Audit Menu")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Go to Page:", 
    ["1. Project Overview", "2. Jobs Audit (All States)", "3. New York Deep-Dive", "4. Efficiency Index Logic"]
)

# --- 4. PAGE 1: OVERVIEW (NON-TECHNICAL) ---
if page == "1. Project Overview":
    st.title("🏛️ Project Overview: The Taxpayer Price Tag")
    st.markdown("""
    ### What is this project about?
    This dashboard is a **Forensic Audit** designed to identify "Market Perversions" in federal spending. 
    We compare how much the government spends on earmarks versus how much workers actually earn.
    """)
    
    st.info("""
    **The Logic:** 1. **Collection:** We pulled 5 years (2020-2024) of BLS Labor stats and Federal Earmark records.
    2. **Cleaning:** We filtered for private-sector employment to see the real economic "anchor."
    3. **Efficiency Index:** We divide Total Spending by Total Workers to find the "Taxpayer Price Tag" per job.
    """)
    
    st.success("**Goal:** To show Christopher and the Substack readers exactly where the government is overpaying for economic growth.")

# --- 5. PAGE 2: JOBS AUDIT ---
elif page == "2. Jobs Audit (All States)":
    st.title("📊 Jobs Audit: Government vs. Private Sector")
    
    fig = px.bar(
        df, x='area_title', y=['avg_annual_pay', 'Efficiency_Index'], 
        barmode='group', 
        title="Annual Salary vs. Taxpayer Cost per Job",
        labels={'value': 'Amount (USD $)', 'variable': 'Metric'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div style="background-color: #f8f9fa; border-left: 5px solid #dc3545; padding: 15px;">
        <strong>Interpretation:</strong> If the <b>Efficiency Index</b> (Red) is higher than the <b>Avg Pay</b> (Blue), 
        it means the government is spending more to "support" a job than the job pays the worker.
    </div>
    """, unsafe_allow_html=True)

# --- 6. PAGE 3: NEW YORK DEEP-DIVE ---
elif page == "3. New York Deep-Dive":
    st.title("🍎 New York State Focus")
    st.write("Analyzing the **$1.88 Billion** FY2024 New York Earmark Pool.")
    
    # Summary Metrics
    avg_ny_pay = ny_df['avg_annual_pay'].mean()
    avg_ny_efficiency = ny_df['Efficiency_Index'].mean()
    
    col1, col2 = st.columns(2)
    col1.metric("Avg. NY Private Salary", f"${avg_ny_pay:,.0f}")
    col2.metric("Avg. NY Taxpayer Cost/Job", f"${avg_ny_efficiency:,.0f}")
    
    st.write("### County-Level Forensic Breakdown")
    st.dataframe(ny_df[['area_title', 'avg_annual_pay', 'Efficiency_Index', 'Audit_Risk_Level']], use_container_width=True)
    
    st.warning("**Substack Hook:** In several NY counties, the government 'Price Tag' per job is triple the local salary.")

# --- 7. PAGE 4: EFFICIENCY INDEX LOGIC ---
elif page == "4. Efficiency Index Logic":
    st.title("🛡️ The Efficiency Index & Taxpayer Burden")
    
    fig = px.scatter(
        df, x='avg_annual_pay', y='Efficiency_Index', 
        size='Efficiency_Index', color='Audit_Risk_Level',
        hover_name='area_title', log_x=True
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    **Why this matters:** A high Efficiency Index indicates that federal money is being "dumped" into a region without regard for the actual market value of labor. 
    This creates a 'Market Perversion' where the government effectively prices out private businesses.
    """)
