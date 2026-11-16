import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from backend.config import (
    MODEL_PATH,
    DATA_PATH,
    USD_TO_INR_RATE,
    INDUSTRIES,
    CITIES,
    INVESTMENT_TYPES,
    MODEL_BENCHMARKS
)
from backend.data_processor import DataProcessor
from backend.ml_service import MLService

# Page Configuration
st.set_page_config(
    page_title="StartupLens AI | Startup Valuation & Investor Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #3b82f6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #1e293b;
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }
    .highlight-box {
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.4), rgba(6, 182, 212, 0.2));
        border: 1px solid rgba(6, 182, 212, 0.4);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Cache services to prevent reloading on every interaction
@st.cache_resource
def get_services():
    dp = DataProcessor(DATA_PATH)
    ml = MLService(MODEL_PATH, data_processor=dp)
    return dp, ml

dp, ml = get_services()

# App Header
st.markdown('<div class="main-header">🚀 StartupLens AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Indian Startup Ecosystem Valuation, Funding Dynamics, and Investor Intelligence System • By <b>Dhruval</b> (AIML)</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=400&auto=format&fit=crop&q=60", use_column_width=True)
st.sidebar.title("Configuration & Hub")
st.sidebar.markdown(f"**Database:** `startup_funding.csv` ({len(dp.cleaned_df):,} records)")
st.sidebar.markdown(f"**Model:** Gradient Boosting Regressor ($R^2 \\approx 0.5218$)")

metadata = dp.get_summary_metadata()
st.sidebar.metric("Total Capital Analyzed", metadata["total_capital_formatted_usd"])
st.sidebar.metric("Total Deals Cataloged", f"{metadata['total_deals']:,}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎓 Academic Information")
st.sidebar.info("""
**Course:** Artificial Intelligence & Machine Learning (AIML)  
**Project:** StartupLens AI Venture Intelligence  
**Author:** Dhruval
""")

# Main Navigation Tabs
tab_predict, tab_whatif, tab_investors, tab_sectors, tab_macro, tab_model = st.tabs([
    "🔮 Valuation Predictor & Advisory",
    "🔄 What-If Hub Simulator",
    "🏢 Investor Intelligence",
    "📊 Sector Opportunity Matrix",
    "📈 Macro Ecosystem Explorer",
    "🔬 Model Diagnostics & Benchmarks"
])

# ================= TAB 1: VALUATION PREDICTOR =================
with tab_predict:
    st.subheader("Startup Architecture & Machine Learning Valuation Forecast")
    
    col1, col2 = st.columns([1, 1.25])
    
    with col1:
        st.markdown("#### Configure Startup Profile")
        with st.form("prediction_form"):
            industry = st.selectbox("Industry Vertical", INDUSTRIES, index=1)
            city = st.selectbox("Operating Tech Hub", CITIES, index=0)
            stage = st.selectbox("Financing Round / Stage", INVESTMENT_TYPES, index=1)
            year = st.slider("Target Funding Year", min_value=2015, max_value=2028, value=2026, step=1)
            syndicate = st.slider("Syndicate Size (Participating Investors)", min_value=1, max_value=15, value=3, step=1)
            
            submitted = st.form_submit_button("🚀 Run Valuation Inference", use_container_width=True)
            
    with col2:
        # Generate prediction
        pred = ml.predict_funding(industry, city, stage, year, syndicate)
        
        st.markdown("#### Projected Deal Valuation")
        st.markdown(f"""
        <div class="highlight-box">
            <h4 style="margin: 0; color: #94a3b8; text-transform: uppercase; font-size: 0.85rem;">Estimated Deal Ticket Size</h4>
            <h1 style="margin: 0.2rem 0; font-size: 2.8rem; color: #ffffff;">{pred['formatted_usd']}</h1>
            <h3 style="margin: 0; color: #34d399;">≈ {pred['formatted_inr']}</h3>
            <p style="margin-top: 0.6rem; margin-bottom: 0; font-size: 0.85rem; color: #a5b4fc;">
                <b>Valuation Bracket:</b> {pred['valuation_tier']} • <b>Percentile:</b> Top {100 - pred['comparable_percentile']}% of deals
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        m1, m2 = st.columns(2)
        m1.metric("Conservative Bound (-30%)", f"${pred['lower_bound_usd']/1e6:.2f}M")
        m2.metric("Aggressive Target (+35%)", f"${pred['upper_bound_usd']/1e6:.2f}M")
        
        st.markdown("##### 💡 Strategic Venture Capital Advisory")
        for insight in pred['advisory_insights']:
            st.markdown(f"- {insight}")

# ================= TAB 2: WHAT-IF SIMULATOR =================
with tab_whatif:
    st.subheader("Counterfactual Hub Simulator")
    st.write("Examine how location geography impacts projected funding while holding business model, stage, and syndicate size constant.")
    
    wcol1, wcol2, wcol3, wcol4 = st.columns(4)
    with wcol1:
        w_ind = st.selectbox("Select Industry", INDUSTRIES, index=0, key="w_ind")
    with wcol2:
        w_stage = st.selectbox("Select Stage", INVESTMENT_TYPES, index=1, key="w_stage")
    with wcol3:
        w_year = st.number_input("Year", min_value=2015, max_value=2030, value=2026, key="w_year")
    with wcol4:
        w_syn = st.number_input("Syndicate Size", min_value=1, max_value=15, value=2, key="w_syn")
        
    candidate_cities = ['Bangalore', 'Mumbai', 'Delhi NCR', 'Pune', 'Hyderabad', 'Chennai', 'Ahmedabad', 'Jaipur', 'Kolkata']
    whatif_res = ml.run_what_if_analysis(w_ind, w_stage, w_year, w_syn, candidate_cities)
    
    w_df = pd.DataFrame(whatif_res['results'])
    
    col_chart, col_table = st.columns([1.2, 1])
    with col_chart:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        colors = ['#06b6d4' if c == whatif_res['top_city'] else '#3b82f6' for c in w_df['city']]
        sns.barplot(data=w_df, x='city', y='estimated_amount_usd', palette=colors, ax=ax)
        ax.set_title(f"Projected Funding by City: {w_ind} ({w_stage})", fontweight='bold', fontsize=11)
        ax.set_ylabel("Funding (USD)")
        ax.set_xlabel("Startup Operating Hub")
        plt.xticks(rotation=35, ha='right')
        st.pyplot(fig)
        
    with col_table:
        display_df = w_df[['city', 'formatted_usd', 'formatted_inr', 'variance_pct']].copy()
        display_df.columns = ['Tech Hub', 'Projected (USD)', 'Projected (INR)', 'Delta vs Median (%)']
        st.dataframe(display_df, use_container_width=True)

# ================= TAB 3: INVESTOR INTELLIGENCE =================
with tab_investors:
    st.subheader("Institutional & Angel Investor Syndication Activity")
    top_n = st.slider("Display Top N Investors", 5, 25, 12)
    inv_data = dp.get_investor_analytics(top_n=top_n)
    inv_df = pd.DataFrame(inv_data)
    
    icol1, icol2 = st.columns([1.2, 1])
    with col1:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(data=inv_df, y='name', x='deal_count', palette='viridis', ax=ax)
        ax.set_title("Most Active Institutional & Angel Participants", fontweight='bold', fontsize=12)
        ax.set_xlabel("Rounds Participated")
        ax.set_ylabel("Investor Entity")
        st.pyplot(fig)
        
    with col2:
        st.dataframe(inv_df.rename(columns={'name': 'Investor Name', 'deal_count': 'Deals Participated'}), use_container_width=True)

# ================= TAB 4: SECTOR OPPORTUNITY MATRIX =================
with tab_sectors:
    st.subheader("Sector Opportunity Ranking Index")
    st.write("Composite scoring (0 to 100) combining capital absorption, round frequency, and geographic network breadth.")
    
    sec_data = dp.compute_sector_scores()
    sec_df = pd.DataFrame(sec_data)
    
    display_sec = sec_df[['industry', 'opportunity_score', 'formatted_total_usd', 'funding_rounds', 'formatted_median_usd', 'active_cities_count']].copy()
    display_sec.columns = ['Industry Vertical', 'Opportunity Score (0-100)', 'Total Capital', 'Rounds', 'Median Ticket', 'Active Hubs']
    st.dataframe(display_sec, use_container_width=True)

# ================= TAB 5: MACRO ECOSYSTEM =================
with tab_macro:
    st.subheader("Macro Indian Venture Capital Trajectory")
    eco = dp.get_ecosystem_overview()
    
    ecol1, ecol2 = st.columns(2)
    with ecol1:
        y_df = pd.DataFrame(eco['yearly_trends'])
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.barplot(data=y_df, x='year', y='deal_count', color='#3b82f6', ax=ax)
        ax.set_title("Annual Deal Volume (2015-2020)", fontweight='bold')
        ax.set_xlabel("Funding Year")
        ax.set_ylabel("Deal Count")
        st.pyplot(fig)
        
    with ecol2:
        c_df = pd.DataFrame(eco['city_distribution']).head(6)
        fig, ax = plt.subplots(figsize=(7, 4))
        plt.pie(c_df['total_funding_m'], labels=c_df['city'], autopct='%1.1f%%', colors=sns.color_palette('mako', 6))
        plt.title("Capital Geographic Allocation Share", fontweight='bold')
        st.pyplot(fig)

# ================= TAB 6: MODEL DIAGNOSTICS =================
with tab_model:
    st.subheader("Model Validation, Benchmarking & Attribution Diagnostics")
    
    st.markdown("#### 1. Algorithmic Cross-Validation Comparison Table")
    bm_df = pd.DataFrame(MODEL_BENCHMARKS)
    st.dataframe(bm_df[['algorithm', 'test_r2', 'test_rmse', 'test_mae', 'cv_r2', 'description']].rename(
        columns={
            'algorithm': 'Algorithm',
            'test_r2': 'Holdout R²',
            'test_rmse': 'RMSE (Log)',
            'test_mae': 'MAE (Log)',
            'cv_r2': '5-Fold CV R²',
            'description': 'Model Assessment'
        }
    ), use_container_width=True)
    
    st.markdown("#### 2. Key Valuation Drivers (Feature Importances)")
    feats = ml.feature_importances[:8]
    f_df = pd.DataFrame(feats)
    
    fig, ax = plt.subplots(figsize=(9, 4))
    sns.barplot(data=f_df, y='feature_label', x='importance_percentage', palette='flare', ax=ax)
    ax.set_title("Relative Feature Importance Attributions (%)", fontweight='bold')
    ax.set_xlabel("Relative Attribution (%)")
    ax.set_ylabel("Feature Name")
    st.pyplot(fig)
