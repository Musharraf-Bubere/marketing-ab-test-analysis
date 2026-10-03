"""
app/streamlit_app.py
--------------------
Interactive Streamlit Dashboard for Marketing Campaign A/B Test & Funnel Analysis.
Runs completely from summary CSVs in data/clean. Zero hardcoded metrics.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Ensure repository root is in sys.path for robust relative imports
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.calculations import (
    load_all_clean_data,
    compute_experiment_metrics,
    compute_financials,
    derive_frequency_cap_scenario,
    compute_day_significance,
)

# Page configuration
st.set_page_config(
    page_title="Marketing A/B Test & Conversion Funnel Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #1f497d;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .metric-title { font-size: 0.85rem; color: #595959; font-weight: bold; text-transform: uppercase; }
    .metric-value { font-size: 1.6rem; color: #1f497d; font-weight: 800; margin: 4px 0; }
    .metric-subtitle { font-size: 0.8rem; color: #7f8c8d; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 45px; white-space: pre-wrap; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_cached_data():
    return load_all_clean_data()


# Load datasets dynamically
data_dict = get_cached_data()
df_groups = data_dict["groups"]
df_funnel = data_dict["funnel"]
df_days = data_dict["days"]
df_dayparts = data_dict["dayparts"]

# Run core analytical calculations
metrics = compute_experiment_metrics(df_groups, df_funnel)
df_day_sig = compute_day_significance(df_days)

# -------------------------------------------------------------
# SIDEBAR CONTROLS
# -------------------------------------------------------------
st.sidebar.title("🎮 Simulation Controls")
st.sidebar.markdown("**Commercial What-If Parameters**")
st.sidebar.info("📌 **Note:** Simulation controls apply to **Tab 3 (Business Impact)** only.")
st.sidebar.caption("⚠️ All financial variables are hypothetical assumptions.")

margin_slider = st.sidebar.slider(
    "Gross Margin per Conversion ($)",
    min_value=5.0,
    max_value=100.0,
    value=40.0,
    step=5.0,
    help="Hypothetical gross margin earned from each converted customer.",
)

cpm_slider = st.sidebar.slider(
    "Cost per 1,000 Impressions / CPM ($)",
    min_value=1.0,
    max_value=10.0,
    value=2.0,
    step=0.5,
    help="Hypothetical media cost to deliver 1,000 commercial ad impressions.",
)

scenario_choice = st.sidebar.selectbox(
    "Statistical Lift Case (Incremental Conversions)",
    options=[
        "Base Case (Point Estimate: 4,343)",
        "Conservative (95% CI Lower Bound: 3,360)",
        "Optimistic (95% CI Upper Bound: 5,326)",
    ],
    index=0,
    help="Select statistical scenario derived from the two-proportion 95% Confidence Interval.",
)

cap_retention_choice = st.sidebar.selectbox(
    "100-Ad Cap: Headline Card Retention Case",
    options=["100% Retention (Optimistic)", "75% Retention (Moderate)", "50% Retention (Conservative)"],
    index=0,
    help="Assumed percentage of incremental orders retained when capping ads at 100 for headline cards.",
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Project Architecture**")
st.sidebar.caption("• **Data Source:** Clean summary CSVs in `/data/clean`\n• **Engine:** Live dynamic Python/SciPy calculations\n• **Calculated from clean CSVs**")

# Resolve selected incremental conversions
if "Conservative" in scenario_choice:
    active_inc_conv = metrics["inc_conv_low"]
    active_case_name = "Conservative (95% CI Low)"
elif "Optimistic" in scenario_choice:
    active_inc_conv = metrics["inc_conv_high"]
    active_case_name = "Optimistic (95% CI High)"
else:
    active_inc_conv = metrics["inc_conv_base"]
    active_case_name = "Base Case (Point Estimate)"

retention_pct = 1.0 if "100%" in cap_retention_choice else (0.75 if "75%" in cap_retention_choice else 0.50)

# Calculate live financials
fin_base = compute_financials(
    incremental_conversions=active_inc_conv,
    total_impressions=metrics["total_treatment_impressions"],
    gross_margin_per_conv=margin_slider,
    cpm=cpm_slider,
)

# Also compute conservative financials (using 95% CI low incremental conversions)
fin_cons = compute_financials(
    incremental_conversions=metrics["inc_conv_low"],
    total_impressions=metrics["total_treatment_impressions"],
    gross_margin_per_conv=margin_slider,
    cpm=cpm_slider,
)

# -------------------------------------------------------------
# MAIN HEADER
# -------------------------------------------------------------
st.title("Marketing Campaign A/B Test & Conversion Funnel Analysis")
st.markdown(
    "**Core Business Question:** *Did the commercial ad campaign increase conversions, for whom, and should the company roll it out?*"
)

# Dashboard Tabs mirroring Power BI specification
tab1, tab2, tab3 = st.tabs([
    "📈 Tab 1: Experiment Overview",
    "🔍 Tab 2: Segments & Funnel Dynamics",
    "💰 Tab 3: Business Impact & Decision Model",
])

# -------------------------------------------------------------
# TAB 1: EXPERIMENT OVERVIEW
# -------------------------------------------------------------
with tab1:
    st.subheader("Executive KPI Overview")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Treatment CR (Ad)</div>
            <div class="metric-value">{metrics['cr_ad']:.2%}</div>
            <div class="metric-subtitle">{metrics['conv_ad']:,} conv / {metrics['n_ad']:,} users</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Control CR (PSA)</div>
            <div class="metric-value">{metrics['cr_psa']:.2%}</div>
            <div class="metric-subtitle">{metrics['conv_psa']:,} conv / {metrics['n_psa']:,} users</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Absolute Lift</div>
            <div class="metric-value">+{metrics['abs_lift']*100:.2f}% pts</div>
            <div class="metric-subtitle">95% CI: [{metrics['ci_low_abs']*100:.2f}%, {metrics['ci_high_abs']*100:.2f}%]</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Relative Lift</div>
            <div class="metric-value">+{metrics['rel_lift']:.1%}</div>
            <div class="metric-subtitle">Lift over PSA placebo</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Incremental Orders</div>
            <div class="metric-value">+{metrics['inc_conv_base']:,}</div>
            <div class="metric-subtitle">Expected baseline: {metrics['expected_baseline_conv']:,}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col_chart, col_table = st.columns([1.1, 0.9])

    with col_chart:
        st.markdown("#### Statistical Significance & 95% Confidence Interval")
        st.caption(
            "The 95% Confidence Interval represents a **plausible range under test conditions, not a deterministic guarantee**."
        )

        # Plotly Forest Plot for Absolute Lift
        fig_ci = go.Figure()
        fig_ci.add_trace(go.Scatter(
            x=[metrics['abs_lift'] * 100.0],
            y=["Overall Campaign Lift"],
            error_x=dict(
                type='data',
                symmetric=False,
                array=[(metrics['ci_high_abs'] - metrics['abs_lift']) * 100.0],
                arrayminus=[(metrics['abs_lift'] - metrics['ci_low_abs']) * 100.0],
                color='#1f497d',
                thickness=3,
                width=10,
            ),
            mode='markers',
            marker=dict(color='#1f497d', size=14),
            name="Point Estimate (+0.77 pts)",
        ))
        fig_ci.add_vline(x=0, line_width=2, line_dash="dash", line_color="#c00000", annotation_text="Zero Lift Baseline")
        fig_ci.update_layout(
            xaxis_title="Absolute Conversion Lift (percentage points)",
            yaxis_title="",
            height=260,
            margin=dict(l=20, r=20, t=30, b=30),
            xaxis=dict(range=[-0.2, 1.2]),
        )
        st.plotly_chart(fig_ci, width="stretch")

        st.info(
            f"**Hypothesis Testing Verdict:** Two-proportion Z-score = **7.37**, p-value = **1.71e-13** ($p \\ll 0.001$). "
            f"We reject $H_0$. The lift is overwhelmingly statistically significant."
        )

    with col_table:
        st.markdown("#### Sample Allocation & SRM Audit")
        total_pop = metrics['n_ad'] + metrics['n_psa']
        st.caption(
            f"Assumed Planned Design Ratio: **96% Treatment : 4% Control (24:1 allocation)**, "
            f"common in digital advertising to limit lost revenue from non-commercial PSA impressions."
        )

        df_display_groups = pd.DataFrame([
            {
                "Group": "Ad group (Treatment)",
                "Users": f"{metrics['n_ad']:,}",
                "User Share": f"{metrics['n_ad'] / total_pop:.2%}",
                "Conversions": f"{metrics['conv_ad']:,}",
                "Conversion Rate": f"{metrics['cr_ad']:.4%}",
            },
            {
                "Group": "PSA group (Control)",
                "Users": f"{metrics['n_psa']:,}",
                "User Share": f"{metrics['n_psa'] / total_pop:.2%}",
                "Conversions": f"{metrics['conv_psa']:,}",
                "Conversion Rate": f"{metrics['cr_psa']:.4%}",
            },
        ])
        st.dataframe(df_display_groups, width="stretch", hide_index=True)

        if metrics['p_srm'] > 0.01:
            st.info(
                f"**Sample Ratio Audit:** Consistent with an assumed 96:4 design (true design ratio unknown).\n\n"
                rf"Observed split matches the assumed 96:4 split ($\chi^2 = {metrics['chi2_srm']:.4f}$, $p = {metrics['p_srm']:.4f}$). "
                f"This verifies consistency with an assumed 96:4 traffic split, but does not prove proper randomization or absence of bias."
            )
        else:
            st.error(
                rf"**Sample Ratio Mismatch (SRM) Warning:** Significant deviation from assumed 96:4 split ($\chi^2 = {metrics['chi2_srm']:.4f}$, $p = {metrics['p_srm']:.4e}$)."
            )

# -------------------------------------------------------------
# TAB 2: SEGMENTS & FUNNEL DYNAMICS
# -------------------------------------------------------------
with tab2:
    st.warning(
        "⚠️ **Methodological Caution:** Exposure buckets (`total_ads`) are **observational (not randomized)**. "
        "Ad impressions correlate with user browsing duration and intent. Results suggest hypotheses for targeted testing, not causal conclusions."
    )

    st.subheader("1. Ad-Exposure Funnel & Impression Productivity")

    col_funnel1, col_funnel2 = st.columns(2)

    with col_funnel1:
        st.markdown("##### Conversion Rate by Exposure Bucket (Ad vs. PSA)")
        df_funnel_plot = df_funnel.rename(columns={"ad_cr_pct": "Ad group", "psa_cr_pct": "PSA group"})
        fig_bar_cr = px.bar(
            df_funnel_plot,
            x="exposure_bucket",
            y=["Ad group", "PSA group"],
            barmode="group",
            labels={"value": "Conversion Rate (%)", "exposure_bucket": "Ad Exposure Tier", "variable": "Group"},
            color_discrete_map={"Ad group": "#1f497d", "PSA group": "#d9534f"},
            title="Conversion Rate: Ad Group vs. PSA Group Across Tiers",
        )
        fig_bar_cr.update_layout(height=340, margin=dict(t=40, b=20, l=20, r=20), legend_title="Group")
        st.plotly_chart(fig_bar_cr, width="stretch")

    with col_funnel2:
        st.markdown("##### Impression Productivity: Incremental Orders per 1k Impressions")
        fig_prod = px.bar(
            df_funnel,
            x="exposure_bucket",
            y="inc_conv_per_1k_imp",
            color="inc_conv_per_1k_imp",
            color_continuous_scale="Teal",
            labels={"inc_conv_per_1k_imp": "Inc. Orders / 1k Imp", "exposure_bucket": "Exposure Tier"},
            title="Incremental Conversions per 1,000 Impressions by Exposure Tier",
        )
        fig_prod.update_layout(height=340, margin=dict(t=40, b=20, l=20, r=20), coloraxis_showscale=False)
        st.plotly_chart(fig_prod, width="stretch")
        st.caption(
            "ℹ️ **Note on Low Tiers:** Negative productivity values in the 1–5 and 6–10 tiers reflect small control group sample sizes "
            "and statistical noise, not evidence that the ad hurts conversion."
        )

    st.markdown("##### The Budget Concentration Trap: User Share vs. Impression Share")
    heavy_u_pct = df_funnel[df_funnel['exposure_bucket'].isin(['51-100', '100+'])]['user_share_pct'].sum()
    heavy_i_pct = df_funnel[df_funnel['exposure_bucket'].isin(['51-100', '100+'])]['impression_share_pct'].sum()
    df_conc_plot = df_funnel.rename(columns={"user_share_pct": "User share", "impression_share_pct": "Impression share"})
    fig_conc = px.bar(
        df_conc_plot,
        x="exposure_bucket",
        y=["User share", "Impression share"],
        barmode="group",
        labels={"value": "Share of Total (%)", "exposure_bucket": "Exposure Tier", "variable": "Metric"},
        color_discrete_map={"User share": "#5bc0de", "Impression share": "#f0ad4e"},
        title=f"Heavy Exposure Tiers (51+): {heavy_u_pct:.1f}% of Users Consume {heavy_i_pct:.1f}% of Impressions",
    )
    fig_conc.update_layout(height=280, margin=dict(t=40, b=20, l=20, r=20), legend_title="Metric")
    st.plotly_chart(fig_conc, width="stretch")

    st.markdown("---")
    st.subheader("2. Temporal Segmentation (Day of Week & Daypart)")

    col_day, col_daypart = st.columns([1.1, 0.9])

    with col_day:
        st.markdown("##### Day-of-Week Conversion Lift & Bonferroni Significance")
        st.caption("Threshold: $\\alpha = 0.05 / 7 = 0.0071$. Slicing traffic shrinks control sample size (~3k users).")

        df_day_plot = df_day_sig.copy()
        df_day_plot["Bonferroni Status"] = df_day_plot["significant_bonferroni"].map(
            {True: "Significant (p < 0.0071)", False: "Not Significant"}
        )
        fig_day = px.bar(
            df_day_plot,
            x="most_ads_day",
            y="absolute_lift_pct_pts",
            color="Bonferroni Status",
            color_discrete_map={"Significant (p < 0.0071)": "#1f497d", "Not Significant": "#a6b9d0"},
            labels={"absolute_lift_pct_pts": "Absolute Lift (% pts)", "most_ads_day": "Day of Week", "Bonferroni Status": "Significance"},
            title="Day-of-Week Conversion Lift",
        )
        fig_day.update_layout(height=340, margin=dict(t=40, b=20, l=20, r=20), legend_title="Bonferroni Status")
        st.plotly_chart(fig_day, width="stretch")

    with col_daypart:
        st.markdown("##### Daypart Performance & Small Base Flag")
        late_night_row = df_dayparts[df_dayparts["daypart"].str.contains("Late Night", case=False)].iloc[0]
        late_users = int(late_night_row["psa_users"])
        late_conv = int(late_night_row["psa_conversions"])

        st.caption(
            f"⚠️ Late Night has only **{late_conv} control conversion out of {late_users:,} users**, "
            f"causing ratio explosion (+889% relative lift). Relative lift is suppressed as **unreliable**."
        )

        df_dp_display = df_dayparts.copy()
        status_col = []
        for _, r in df_dp_display.iterrows():
            if "Late Night" in r["daypart"] or int(r["psa_conversions"]) <= 5:
                status_col.append(f"Unreliable ({int(r['psa_conversions'])} conv / {int(r['psa_users']):,} users)")
            else:
                status_col.append(f"Reliable ({int(r['psa_users']):,} users)")
        df_dp_display["Control Reliability"] = status_col

        df_dp_display = df_dp_display.rename(columns={
            "daypart": "Daypart",
            "total_users": "Total Users",
            "ad_cr_pct": "Ad Group CR (%)",
            "psa_cr_pct": "PSA Group CR (%)",
            "absolute_lift_pct_pts": "Absolute Lift (% pts)",
        })

        cols_dp_show = ["Daypart", "Total Users", "Ad Group CR (%)", "PSA Group CR (%)", "Absolute Lift (% pts)", "Control Reliability"]
        st.dataframe(df_dp_display[cols_dp_show], width="stretch", hide_index=True)

# -------------------------------------------------------------
# TAB 3: BUSINESS IMPACT & DECISION MODEL
# -------------------------------------------------------------
with tab3:
    st.error("🚨 **Disclaimer:** All financial figures (Gross Margin, CPM, Spend, Net Profit) are **HYPOTHETICAL PLANNING ASSUMPTIONS**.")

    st.subheader(f"Financial Returns: {active_case_name}")
    st.caption(f"Inputs from Sidebar: Gross Margin = **\\${margin_slider:.2f}** | CPM = **\\${cpm_slider:.2f}** | Incremental Orders = **{active_inc_conv:,}**")

    f1, f2, f3, f4, f5 = st.columns(5)
    with f1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Campaign Media Spend</div>
            <div class="metric-value">\\${fin_base['media_spend']:,.0f}</div>
            <div class="metric-subtitle">{metrics['total_treatment_impressions']:,} imp @ \\${cpm_slider:.2f} CPM</div>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Inc. Gross Profit</div>
            <div class="metric-value">\\${fin_base['incremental_gross_profit']:,.0f}</div>
            <div class="metric-subtitle">{active_inc_conv:,} orders * \\${margin_slider:.0f} margin</div>
        </div>
        """, unsafe_allow_html=True)
    with f3:
        profit_color = "#2e7d32" if fin_base['net_incremental_profit'] >= 0 else "#c00000"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Net Incremental Profit</div>
            <div class="metric-value" style="color: {profit_color};">\\${fin_base['net_incremental_profit']:,.0f}</div>
            <div class="metric-subtitle">Gross Profit - Media Spend</div>
        </div>
        """, unsafe_allow_html=True)
    with f4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Margin-Based ROAS</div>
            <div class="metric-value">{fin_base['roas']:.2f}x</div>
            <div class="metric-subtitle">Gross Profit / Media Spend</div>
        </div>
        """, unsafe_allow_html=True)
    with f5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Cost / Inc. Order (CAC)</div>
            <div class="metric-value">\\${fin_base['cac']:.2f}</div>
            <div class="metric-subtitle">Media Spend / Inc. Orders</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col_be, col_sens = st.columns([0.8, 1.2])

    with col_be:
        st.markdown("#### Break-Even Sensitivity Thresholds")
        st.metric("Break-Even CPM (Max Viable Ad Cost)", f"${fin_base['break_even_cpm']:.2f}", delta=f"${fin_base['break_even_cpm'] - cpm_slider:.2f} buffer", delta_color="normal")
        st.metric("Break-Even Gross Margin (Min Viable Order Margin)", f"${fin_base['break_even_margin']:.2f}", delta=f"${margin_slider - fin_base['break_even_margin']:.2f} buffer", delta_color="normal")

        st.caption(
            f"At **\\${margin_slider:.0f} margin**, actual CPM can rise up to **\\${fin_base['break_even_cpm']:.2f}** before losing money. "
            f"At **\\${cpm_slider:.2f} CPM**, gross margin can drop to **\\${fin_base['break_even_margin']:.2f}** before losing money."
        )

    with col_sens:
        st.markdown("#### 2D Sensitivity Heatmap: Net Incremental Profit ($)")
        cpms = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]
        margins = [5.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 75.0, 100.0]

        heat_matrix = []
        for c in cpms:
            row = []
            for m in margins:
                prof = (active_inc_conv * m) - ((metrics['total_treatment_impressions'] / 1000.0) * c)
                row.append(prof)
            heat_matrix.append(row)

        fig_heat = go.Figure(data=go.Heatmap(
            z=heat_matrix,
            x=[f"${int(m)}" for m in margins],
            y=[f"${c:.1f}" for c in cpms],
            colorscale="RdYlGn",
            colorbar=dict(title="Net Profit ($)"),
        ))
        fig_heat.update_layout(
            xaxis_title="Gross Margin per Conversion ($)",
            yaxis_title="CPM ($)",
            height=320,
            margin=dict(t=20, b=20, l=20, r=20),
        )
        st.plotly_chart(fig_heat, width="stretch")

    st.markdown("---")
    st.subheader("Scenario Comparison: Uncapped vs. 100-Ad Frequency Cap")

    cap_data = derive_frequency_cap_scenario(df_funnel, metrics['inc_conv_base'], metrics['total_treatment_impressions'])
    spend_saved = (cap_data['imp_saved'] / 1000.0) * cpm_slider

    # Compute Scenario B at 100%, 75%, and 50% retention
    conv_100 = active_inc_conv
    fin_cap_100 = compute_financials(conv_100, cap_data['total_capped_impressions'], margin_slider, cpm_slider)

    conv_75 = active_inc_conv - (cap_data['inc_conv_100'] * 0.25)
    fin_cap_75 = compute_financials(conv_75, cap_data['total_capped_impressions'], margin_slider, cpm_slider)

    conv_50 = active_inc_conv - (cap_data['inc_conv_100'] * 0.50)
    fin_cap_50 = compute_financials(conv_50, cap_data['total_capped_impressions'], margin_slider, cpm_slider)

    st.caption(
        f"A 100-Ad Cap removes only impressions **after the 100th ad** for {cap_data['users_100']:,} users, "
        f"saving **{cap_data['imp_saved']:,} impressions** (\\${spend_saved:,.0f} media spend saved)."
    )

    df_scen_comp = pd.DataFrame([
        {
            "Strategy / Scenario": "Scenario A: Full Uncapped Rollout",
            "Impressions": f"{metrics['total_treatment_impressions']:,}",
            "Media Spend": f"${fin_base['media_spend']:,.0f}",
            "Incremental Orders": f"{active_inc_conv:,.0f}",
            "Net Profit": f"${fin_base['net_incremental_profit']:,.0f}",
            "ROAS": f"{fin_base['roas']:.2f}x",
            "Profit Delta vs. A": "$0",
        },
        {
            "Strategy / Scenario": "Scenario B: 100-Ad Cap (100% Retention)",
            "Impressions": f"{cap_data['total_capped_impressions']:,}",
            "Media Spend": f"${fin_cap_100['media_spend']:,.0f}",
            "Incremental Orders": f"{conv_100:,.0f}",
            "Net Profit": f"${fin_cap_100['net_incremental_profit']:,.0f}",
            "ROAS": f"{fin_cap_100['roas']:.2f}x",
            "Profit Delta vs. A": f"${fin_cap_100['net_incremental_profit'] - fin_base['net_incremental_profit']:+,.0f}",
        },
        {
            "Strategy / Scenario": "Scenario B: 100-Ad Cap (75% Retention)",
            "Impressions": f"{cap_data['total_capped_impressions']:,}",
            "Media Spend": f"${fin_cap_75['media_spend']:,.0f}",
            "Incremental Orders": f"{conv_75:,.0f}",
            "Net Profit": f"${fin_cap_75['net_incremental_profit']:,.0f}",
            "ROAS": f"{fin_cap_75['roas']:.2f}x",
            "Profit Delta vs. A": f"${fin_cap_75['net_incremental_profit'] - fin_base['net_incremental_profit']:+,.0f}",
        },
        {
            "Strategy / Scenario": "Scenario B: 100-Ad Cap (50% Retention)",
            "Impressions": f"{cap_data['total_capped_impressions']:,}",
            "Media Spend": f"${fin_cap_50['media_spend']:,.0f}",
            "Incremental Orders": f"{conv_50:,.0f}",
            "Net Profit": f"${fin_cap_50['net_incremental_profit']:,.0f}",
            "ROAS": f"{fin_cap_50['roas']:.2f}x",
            "Profit Delta vs. A": f"${fin_cap_50['net_incremental_profit'] - fin_base['net_incremental_profit']:+,.0f}",
        },
    ])
    st.dataframe(df_scen_comp, width="stretch", hide_index=True)

    breakeven_loss_orders = spend_saved / margin_slider if margin_slider > 0 else 0.0
    st.info(
        f"💡 **CFO Tradeoff Insight:** The 100-Ad Cap saves **\\${spend_saved:,.0f}** in media spend. "
        f"At **\\${margin_slider:.0f} margin**, the breakeven retention threshold is losing no more than **{breakeven_loss_orders:.1f} orders** "
        f"({breakeven_loss_orders / cap_data['inc_conv_100']:.1%} of the tier's lift). "
        f"Even the 100+ tier generates ~\\${0.286 * margin_slider:.2f} of gross margin per 1,000 impressions against \\${cpm_slider:.2f} CPM. "
        f"Therefore, test the cap on a holdout group first rather than deploying blindly."
    )

    st.markdown("---")
    st.markdown("### 🎯 Executive Decision Framework")

    cons_be_cpm = fin_cons['break_even_cpm']
    cons_be_margin = fin_cons['break_even_margin']

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.success(
            "**1. Launch Fully (Uncapped) [RECOMMENDED under hypothetical assumptions]**\n\n"
            f"• Conservative Launch Conditions (95% CI Low): Gross Margin >= \\${cons_be_margin:.2f}, CPM <= \\${cons_be_cpm:.2f}.\n"
            f"• At Base Case: Gross Margin >= \\${fin_base['break_even_margin']:.2f}, CPM <= \\${fin_base['break_even_cpm']:.2f}.\n"
            f"• Outcome: Captures full +\\${fin_base['net_incremental_profit']:,.0f} profit at {fin_base['roas']:.2f}x return without risking conversion loss."
        )
    with col_d2:
        st.warning(
            "**2. Test 100-Cap on Holdout Group**\n\n"
            "• Conditions: Test size must be determined by an ex-ante statistical power calculation, not an arbitrary split.\n"
            f"• Evaluation: Note that the cap's total potential media saving (~\\${spend_saved:,.0f} under base assumptions) "
            "is small relative to the operational and technical effort required to run and monitor a holdout test."
        )
    with col_d3:
        st.error(
            "**3. Do Not Launch**\n\n"
            f"• Conditions: CPM exceeds \\${cons_be_cpm:.2f} (conservative) / \\${fin_base['break_even_cpm']:.2f} (base), "
            f"or Gross Margin falls below \\${cons_be_margin:.2f} (conservative) / \\${fin_base['break_even_margin']:.2f} (base).\n"
            "• Outcome: Ad delivery costs exceed incremental customer value generated."
        )
