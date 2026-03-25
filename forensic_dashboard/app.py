import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="NY Forensic Audit 2020-2024", layout="wide")

@st.cache_data
def load_data():
    file_name = 'audit_data_5year.csv'
    if not os.path.exists(file_name):
        st.error(f"🚨 '{file_name}' not found in the root directory!")
        st.stop()
    df = pd.read_csv(file_name)
    # Filter for New York specifically
    ny_df = df[df['area_title'].str.contains("New York", case=False, na=False)].copy()
    return df, ny_df

df, ny_df = load_data()

# --- 2. SIDEBAR & LOGIC EXPLANATION ---
st.sidebar.title("🔍 Audit Control Center")
st.sidebar.info("""
**The Logic:** We calculate the **Efficiency Index** ($Spending \div Workers$). 
If the cost to 'support' a job is higher than the worker's salary, we flag it as **Market Perversion**.
""")

menu = st.sidebar.radio("Analysis Type:", 
    ["Audit Overview", "The 5-Year Trend", "New York Deep-Dive", "Risk Anomaly Detection"])

# --- 3. PAGE: AUDIT OVERVIEW ---
if menu == "Audit Overview":
    st.title("🏛️ Federal Earmark Efficiency Audit (2020-2024)")
    
    col1, col2, col3 = st.columns(3)
    total_spend = df['Allocated_Spending'].sum()
    avg_efficiency = df['Efficiency_Index'].mean()
    high_risk_count = len(df[df['Audit_Risk_Level'].str.contains('Market Perversion', na=False)])
    
    col1.metric("Total Audited Spending", f"${total_spend/1e9:.2f}B")
    col2.metric("Avg. Taxpayer Cost/Job", f"${avg_efficiency:,.0f}")
    col3.metric("High Risk Counties", high_risk_count)

    st.markdown("### National Cost vs. Salary Distribution")
    fig = px.histogram(df, x="Efficiency_Index", color="Audit_Risk_Level", 
                       title="How often does the government overpay for jobs?",
                       labels={'Efficiency_Index': 'Taxpayer Cost per Job ($)'})
    st.plotly_chart(fig, use_container_width=True)

# --- 4. PAGE: THE 5-YEAR TREND ---
elif menu == "The 5-Year Trend":
    st.title("📉 Longitudinal Efficiency Trend")
    st.write("Tracking how the 'Price Tag' of a New York job has changed over 5 years.")
    
    trend_data = ny_df.groupby('year')[['Efficiency_Index', 'avg_annual_pay']].mean().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend_data['year'], y=trend_data['Efficiency_Index'], name="Gov Cost Per Job", line=dict(color='red', width=4)))
    fig.add_trace(go.Scatter(x=trend_data['year'], y=trend_data['avg_annual_pay'], name="Avg Private Salary", line=dict(color='blue', dash='dash')))
    
    fig.update_layout(title="The Growing Gap: Spending vs. Earnings", xaxis_title="Year", yaxis_title="USD ($)")
    st.plotly_chart(fig, use_container_width=True)
    
    st.warning("**Forensic Insight:** If the Red line rises faster than the Blue line, the government is inflating the economy artificially.")

# --- 5. PAGE: NEW YORK DEEP-DIVE ---
elif menu == "New York Deep-Dive":
    st.title("🍎 New York County-Level Forensics")
    selected_year = st.selectbox("Select Audit Year", sorted(ny_df['year'].unique(), reverse=True))
    yearly_ny = ny_df[ny_df['year'] == selected_year]
    
    st.write(f"### Top 10 Most Inefficient Counties in {selected_year}")
    top_10 = yearly_ny.nlargest(10, 'Efficiency_Index')
    st.table(top_10[['area_title', 'avg_annual_pay', 'Efficiency_Index', 'Audit_Risk_Level']])

# --- 6. PAGE: RISK ANOMALY DETECTION ---
elif menu == "Risk Anomaly Detection":
    st.title("🚨 Statistical Anomaly Detection")
    st.write("We use a **Salary Replacement Ratio** to find where spending is mathematically absurd.")
    
    # Calculate Ratio: Spending / Salary
    ny_df['Ratio'] = ny_df['Efficiency_Index'] / ny_df['avg_annual_pay']
    
    fig = px.scatter(ny_df, x="avg_annual_pay", y="Efficiency_Index", 
                     size="Ratio", color="Ratio", hover_name="area_title",
                     title="Identifying Outliers (Bigger Bubble = Higher Waste)")
    st.plotly_chart(fig, use_container_width=True)
    
    st.error("**The Smoking Gun:** Bubbles at the top left represent counties where pay is LOW but spending is HIGH. These are the primary targets for the Substack investigation.")
