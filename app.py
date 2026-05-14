import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Arhat's Wealth Engine", 
    layout="wide", 
    page_icon="🚀"
)

# --- CUSTOM FINTECH STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    div[data-testid="stMetricValue"] { color: #2ecc71 !important; font-size: 24px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 Premium Wealth Engine v2.0")
st.markdown("---")

# --- SIDEBAR: DYNAMIC INPUTS ---
with st.sidebar:
    st.header("⚙️ Investment Controls")
    monthly_sip = st.number_input("Monthly SIP Amount (NPR)", value=10000, step=1000)
    initial_lump = st.number_input("Initial Investment (Lump Sum)", value=100000)
    expected_return = st.slider("Expected Annual Return (%)", 5, 25, 12)
    inflation_rate = st.slider("Avg. Inflation Rate (%)", 0, 12, 6)
    duration_years = st.slider("Horizon (Years)", 1, 40, 15)
    
    st.markdown("---")
    st.header("🎯 Goal Setting")
    target_goal = st.number_input("Target Wealth Goal (NPR)", value=10000000, step=1000000)
    st.caption("Default is set to 1 Crore.")

# --- CALCULATION LOGIC ---
months = duration_years * 12
m_rate = (expected_return / 100) / 12
inf_m_rate = (inflation_rate / 100) / 12
time_axis = np.arange(months + 1)

# Nominal and Real Growth
sip_nominal = [monthly_sip * (((1 + m_rate)**m - 1) / m_rate) * (1 + m_rate) if m > 0 else 0 for m in time_axis]
lump_nominal = initial_lump * (1 + m_rate)**time_axis
total_nominal = np.array(sip_nominal) + np.array(lump_nominal)
total_real = total_nominal / (1 + inf_m_rate)**time_axis

# Principal and Tax
total_invested = (monthly_sip * time_axis) + initial_lump
final_wealth = total_nominal[-1]
final_profit = final_wealth - total_invested[-1]
cgt_tax = max(0, final_profit * 0.05) 
post_tax_wealth = final_wealth - cgt_tax

# --- KEY PERFORMANCE INDICATORS ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Invested", f"Rs. {total_invested[-1]:,.0f}")
with c2:
    st.metric("Final Wealth (Nominal)", f"Rs. {final_wealth:,.0f}")
with c3:
    st.metric("Post-Tax (5% CGT)", f"Rs. {post_tax_wealth:,.0f}")
with c4:
    st.metric("Real Value (Adjusted)", f"Rs. {total_real[-1]:,.0f}")

# --- INTERACTIVE VISUALIZATION ---
fig = go.Figure()

# Nominal Growth Area
fig.add_trace(go.Scatter(
    x=time_axis, y=total_nominal, name='Nominal Wealth', 
    line=dict(color='#2ecc71', width=4),
    fill='tozeroy', fillcolor='rgba(46, 204, 113, 0.1)'
))

# Target Goal Line
fig.add_hline(y=target_goal, line_dash="dash", line_color="#e74c3c", 
              annotation_text=f"Target: {target_goal:,.0f}", annotation_position="top left")

fig.update_layout(
    title=f"Wealth Accumulation vs Target Goal",
    xaxis_title="Months", yaxis_title="Amount (NPR)",
    template="plotly_dark", hovermode="x unified", height=500
)
st.plotly_chart(fig, use_container_width=True)

# --- GOAL ANALYSIS SECTION ---
st.markdown("### 🔍 Goal Analytics")
i1, i2 = st.columns(2)

with i1:
    if final_wealth >= target_goal:
        st.success(f"🎉 **Goal Achieved!** You surpassed your target by **Rs. {final_wealth - target_goal:,.0f}**.")
    else:
        gap = target_goal - final_wealth
        st.error(f"🚩 **Goal Shortfall:** You are **Rs. {gap:,.0f}** away from your target.")

with i2:
    # Logic to estimate how many more months to reach target if not reached
    if final_wealth < target_goal:
        # Simple iterative estimation for remaining time
        future_val = final_wealth
        extra_months = 0
        while future_val < target_goal and extra_months < 600: # limit to 50 extra years
            extra_months += 1
            future_val = (future_val + monthly_sip) * (1 + m_rate)
        
        st.info(f"⏳ **Time Adjustment:** At this rate, it would take approx. **{extra_months} more months** to hit your goal.")
    else:
        # Calculate when exactly the goal was hit
        months_to_hit = np.argmax(total_nominal >= target_goal)
        st.info(f"⏱️ **Efficiency:** You will hit your goal in **Year {months_to_hit//12}, Month {months_to_hit%12}**.")

# --- DATA TABLE ---
with st.expander("📊 View Detailed Ledger"):
    df = pd.DataFrame({
        "Month": time_axis,
        "Total Invested": total_invested,
        "Nominal Wealth": total_nominal,
        "Real Value": total_real
    }).set_index("Month")
    st.dataframe(df.style.format("Rs. {0:,.0f}"), use_container_width=True)