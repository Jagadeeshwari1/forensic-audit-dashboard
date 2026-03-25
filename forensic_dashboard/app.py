import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIG ---
st.set_page_config(page_title="NY Forensic Audit 2020-2024", layout="wide")

@st.cache_data
def load_and_fix_data():
    file_name = 'audit_data_5year.csv'
    # Look for file in root or subfolder
    if not os.path.exists(file_name):
        file_name = 'forensic_dashboard/audit_data_5year.csv'
    
    if not os.path.exists(file_name):
        st.error(f"🚨 File '{file_name}' not found!")
        st.stop()
        
    df = pd.read_csv(file_name)
    
    # --- SELF-HEALING LOGIC ---
    # 1. Ensure column names are clean
    df.columns = df.columns.str.strip()
    
    # 2. Re-calculate Audit_Risk_Level if missing (Fixes the KeyError)
    if 'Audit_Risk_Level' not in df.columns:
        # Ratio of Gov Spending to Private Salary
        ratio = df['Efficiency_Index'] / df['avg_annual_pay']
        df['Audit_Risk_Level'] = '✅ Healthy'
        df.loc[ratio >= 0.5, 'Audit_Risk_Level'] = '🟡 Watchlist'
        df.loc[ratio > 1.0, 'Audit_Risk_Level'] = '🚨 Market Perversion'
        
    ny_df = df[df['area_title'].str.contains("New York", case=False, na=False)].copy()
    return df, ny_df

df, ny_df = load_and_fix_data()

# --- 2. SIDEBAR NAVIGATION ---
st.sidebar.title("🔍 Audit Menu")
menu = st.sidebar.radio("Navigate to:", 
    ["1. Overview", "2. The 5-Year Trend", "3. New York Deep-Dive", "4. Risk Detection"])

# --- 3. PAGE 1: OVERVIEW ---
if menu == "1. Overview":
    st.title("🏛️ Federal Earmark Efficiency Audit (2020-2024)")
    
    col1, col2, col3 = st.columns(3)
    total_spend = df['Allocated_Spending'].sum()
    avg_efficiency = df['Efficiency_Index'].mean()
    # Now this line is safe because of our Self-Healing logic above
    high_risk_count = len(df[df['Audit_Risk_Level'] == '🚨 Market Perversion'])
    
    col1.metric("Total Audited Spending", f"${total_spend/1e9:.2f}B")
    col2.metric("Avg. Taxpayer Cost/Job", f"${avg_efficiency:,.0f}")
    col3.metric("High Risk Counties", high_risk_count)

    st.markdown("### The Efficiency Logic")
    st.info("We compare **Federal Spending** to **Private Salaries**. If the gov spends more to 'support' a job than the job actually pays, it's an inefficient 'Market Perversion'.")
    
    fig = px.histogram(df, x="Efficiency_Index", color="Audit_Risk_Level", 
                       title="Distribution of Taxpayer Cost per Job")
    st.plotly_chart(fig, use_container_width=True)

# --- 4. PAGE 2: THE 5-YEAR TREND ---
elif menu == "2. The 5-Year Trend":
    st.title("📉 Longitudinal Efficiency Trend")
    trend_data = ny_df.groupby('year')[['Efficiency_Index', 'avg_annual_pay']].mean().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend_data['year'], y=trend_data['Efficiency_Index'], name="Gov Cost Per Job", line=dict(color='red', width=4)))
    fig.add_trace(go.Scatter(x=trend_data['year'], y=trend_data['avg_annual_pay'], name="Avg Private Salary", line=dict(color='blue', dash='dash')))
    st.plotly_chart(fig, use_container_width=True)
    st.warning("**Forensic Insight:** Notice the gap widening in New York as federal spending outpaces local wage growth.")

# --- 5. PAGE 3: NEW YORK DEEP-DIVE ---
elif menu == "3. New York Deep-Dive":
    st.title("🍎 New York County-Level Forensics")
    st.dataframe(ny_df[['area_title', 'year', 'avg_annual_pay', 'Efficiency_Index', 'Audit_Risk_Level']], use_container_width=True)

# --- 6. PAGE 4: RISK DETECTION ---
elif menu == "4. Risk Detection":
    st.title("🚨 Statistical Anomaly Detection")
    # Identify bubbles where spending is high but pay is low
    fig = px.scatter(ny_df, x="avg_annual_pay", y="Efficiency_Index", 
                     size="Efficiency_Index", color="Audit_Risk_Level", hover_name="area_title")
    st.plotly_chart(fig, use_container_width=True)
    st.error("Bubbles in the top-left are your primary targets: High taxpayer cost, low worker benefit.")
