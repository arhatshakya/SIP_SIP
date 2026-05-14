import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Arhat's Wealth Engine", layout="wide", page_icon="💰")

# --- CUSTOM THEME & CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .metric-card { background-color: #161b22; border-radius: 10px; padding: 20px; border: 1px solid #30363d; }
    div[data-testid="stMetricValue"] { color: #2ecc71 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 Premium SIP Wealth Engine")
st.markdown("---")

# --- SIDEBAR: ADVANCED INPUTS ---
with st.sidebar:
    st.header("⚙️ Configuration")
    monthly_sip = st.number_input("Monthly SIP (NPR)", value=10000, step=1000)
    initial_lump = st.number_input("Initial Lump Sum", value=100000)
    expected_return = st.slider("Expected Annual Return (%)", 5, 25, 12)
    inflation_rate = st.slider("Average Inflation Rate (%)", 0, 12, 6)
    duration_years = st.slider("Horizon (Years)", 1, 30, 15)

# --- CALCULATION LOGIC ---
months = duration_years * 12
m_rate = (expected_return / 100) / 12
inf_m_rate = (inflation_rate / 100) / 12
time_axis = np.arange(months + 1)

# Nominal Growth (Face Value)
sip_nominal = [monthly_sip * (((1 + m_rate)**m - 1) / m_rate) * (1 + m_rate) if m > 0 else 0 for m in time_axis]
lump_nominal = initial_lump * (1 + m_rate)**time_axis
total_nominal = np.array(sip_nominal) + np.array(lump_nominal)

# Inflation-Adjusted Growth (Real Purchasing Power)
# We discount the future value back to today's NPR value
total_real = total_nominal / (1 + inf_m_rate)**time_axis

total_invested = (monthly_sip * time_axis) + initial_lump

# --- DASHBOARD METRICS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Wealth (Nominal)", f"Rs. {total_nominal[-1]:,.0f}")
with col2:
    st.metric("Real Value (Adjusted for Inflation)", f"Rs. {total_real[-1]:,.0f}", 
              delta=f"-{((1 - total_real[-1]/total_nominal[-1])*100):.1f}% Loss in Power", delta_color="inverse")
with col3:
    st.metric("Total Profit", f"Rs. {total_nominal[-1] - total_invested[-1]:,.0f}")

# --- INTERACTIVE CHART ---
fig = go.Figure()

# Nominal wealth line
fig.add_trace(go.Scatter(x=time_axis, y=total_nominal, name='Nominal Wealth', 
                         line=dict(color='#2ecc71', width=4)))

# Real wealth line (shaded)
fig.add_trace(go.Scatter(x=time_axis, y=total_real, name='Real Purchasing Power', 
                         line=dict(color='#3498db', width=2, dash='dash'),
                         fill='tonexty', fillcolor='rgba(52, 152, 219, 0.1)'))

# Principal line
fig.add_trace(go.Scatter(x=time_axis, y=total_invested, name='Principal Invested', 
                         line=dict(color='#95a5a6', width=2, dash='dot')))

fig.update_layout(
    title="Nominal Wealth vs. Inflation-Adjusted Value",
    xaxis_title="Months",
    yaxis_title="NPR Value",
    template="plotly_dark",
    hovermode="x unified",
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# --- PRO-INSIGHTS SECTION ---
st.markdown("### 🔍 Professional Insights")
c1, c2 = st.columns(2)
with c1:
    st.info(f"**Wealth Multiplier:** Your total wealth will be **{(total_nominal[-1]/total_invested[-1]):.2f}x** your investment.")
with c2:
    target_1cr = 10000000
    if total_nominal[-1] < target_1cr:
        shortfall = target_1cr - total_nominal[-1]
        st.warning(f"**Goal Tracking:** To reach **1 Crore**, you are short by Rs. {shortfall:,.0f}.")
    else:
        st.success("**Goal Tracking:** You have surpassed the **1 Crore** mark!")