"""Module 6: Executive KPI Dashboard."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA_DIR = Path("data")

FUNNEL_STEP_ORDER = [
    "Session Start", "View Item", "Add to Cart",
    "Begin Checkout", "Add Payment Info", "Purchase",
]

st.set_page_config(page_title="Drishti - Product Analytics Dashboard", layout="wide")


@st.cache_data
def load_csv(name):
    return pd.read_csv(DATA_DIR / name)


kpis = load_csv("kpi_summary.csv").iloc[0]
funnel_overall = load_csv("funnel_overall.csv")
funnel_device = load_csv("funnel_by_device.csv")
funnel_channel = load_csv("funnel_by_channel.csv")
cohort = load_csv("cohort_retention.csv")
channel_attribution = load_csv("channel_attribution.csv")
chi_square = load_csv("chi_square_test.csv")
seg_new_returning = load_csv("segment_new_vs_returning.csv")
seg_high_value = load_csv("segment_high_value.csv")
seg_device_buyers = load_csv("segment_device_buyers.csv")
monthly_revenue = load_csv("monthly_revenue.csv")
dau_mau = load_csv("dau_mau.csv")

st.title("Drishti - Product Analytics Intelligence Dashboard")
st.caption(
    "GA4 e-commerce event data, Nov 2020 - Jan 2021 "
    "(bigquery-public-data.ga4_obfuscated_sample_ecommerce)"
)

row1 = st.columns(3)
row1[0].metric("Total Revenue", f"${kpis['total_revenue']:,.0f}")
row1[1].metric("Overall Conversion Rate", f"{kpis['overall_conversion_pct']}%")
row1[2].metric("Avg Order Value", f"${kpis['avg_order_value']:.2f}")

row2 = st.columns(3)
row2[0].metric("Cart Abandonment Rate", f"{kpis['cart_abandonment_pct']}%")
row2[1].metric("Month-over-Month Revenue Growth", f"{kpis['mom_revenue_growth_pct']}%")
row2[2].metric("DAU/MAU Stickiness", f"{kpis['avg_dau_mau_ratio_pct']}%")

st.divider()

tab_overview, tab_funnel, tab_retention, tab_channels, tab_segments, tab_recs = st.tabs(
    ["Overview", "Funnel", "Retention", "Channels", "Segments", "Recommendations"]
)

with tab_overview:
    st.subheader("Monthly Revenue Trend")
    fig_rev = px.line(monthly_revenue, x="month", y="total_revenue", markers=True)
    st.plotly_chart(fig_rev, use_container_width=True)
    st.caption(
        "Revenue peaks in December (holiday season) then drops sharply in January - "
        "a common retail seasonality pattern, not necessarily a standalone problem."
    )

    st.subheader("DAU/MAU Stickiness by Month")
    fig_dau = px.bar(dau_mau, x="month", y="dau_mau_ratio_pct")
    st.plotly_chart(fig_dau, use_container_width=True)

with tab_funnel:
    view_by = st.radio("View funnel by:", ["Overall", "Device", "Channel"], horizontal=True)

    if view_by == "Overall":
        fig = go.Figure(go.Funnel(
            y=funnel_overall["step"],
            x=funnel_overall["users"],
            textinfo="value+percent initial",
        ))
        st.plotly_chart(fig, use_container_width=True)
    else:
        source_df = funnel_device if view_by == "Device" else funnel_channel
        group_col = "device" if view_by == "Device" else "channel"
        all_groups = sorted(source_df[group_col].dropna().unique())
        groups = st.multiselect(
            f"Select {group_col}(s) to compare:",
            options=all_groups,
            default=all_groups[:3],
        )
        filtered = source_df[source_df[group_col].isin(groups)]
        fig = px.line(
            filtered, x="step", y="overall_conversion_pct", color=group_col,
            markers=True, category_orders={"step": FUNNEL_STEP_ORDER},
        )
        fig.update_layout(yaxis_title="% of top-of-funnel users remaining")
        st.plotly_chart(fig, use_container_width=True)

with tab_retention:
    pivot = cohort.pivot(index="cohort_month", columns="months_since_first", values="retention_pct")
    fig = px.imshow(
        pivot, text_auto=".1f", color_continuous_scale="RdYlGn", zmin=0, zmax=100,
        labels=dict(x="Months Since First Purchase", y="Cohort Month", color="% Retained"),
    )
    st.plotly_chart(fig, use_container_width=True)

    selected_cohort = st.selectbox("Inspect a cohort:", cohort["cohort_month"].unique())
    st.dataframe(cohort[cohort["cohort_month"] == selected_cohort], hide_index=True)

with tab_channels:
    fig = px.bar(
        channel_attribution.sort_values("total_revenue"),
        x="total_revenue", y="channel", orientation="h",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(channel_attribution, hide_index=True)

    st.subheader("Organic vs Paid: Statistical Significance")
    sig_row = chi_square.iloc[0]
    verdict = "statistically significant" if sig_row["significant_at_0.05"] else "not statistically significant"
    st.write(
        f"Chi-square test: chi2 = {sig_row['chi2_statistic']}, "
        f"p-value = {sig_row['p_value']} - the conversion-rate difference between "
        f"organic and cpc is **{verdict}** (alpha = 0.05)."
    )

with tab_segments:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("New vs Returning Users")
        st.dataframe(seg_new_returning, hide_index=True)
        fig = px.bar(seg_new_returning, x="user_type", y="conversion_rate_pct")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top 20% Spenders vs Rest")
        st.dataframe(seg_high_value, hide_index=True)
        fig = px.pie(seg_high_value, names="segment", values="total_revenue")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Mobile vs Desktop Buyers")
    st.dataframe(seg_device_buyers, hide_index=True)

with tab_recs:
    st.info(
        "Preliminary priorities based on Days 1-5 findings. Full analysis with "
        "quantified expected impact is written up in Module 7 (Day 7)."
    )
    recommendations = pd.DataFrame([
        {
            "Priority": "P1",
            "Finding": "Only ~23% of visitors ever view a product, and only ~20% of "
                       "those add to cart - the biggest leak is engagement, not checkout.",
            "Recommended Action": "Investigate product discovery/browsing UX (search "
                                  "relevance, homepage merchandising, product-list design).",
        },
        {
            "Priority": "P2",
            "Finding": "cpc (paid search) is the worst channel on every metric - "
                       "conversion, AOV, and repeat purchase rate - despite being the "
                       "one channel we pay for.",
            "Recommended Action": "Reallocate marketing budget from cpc toward "
                                  "referral and organic-driving activities.",
        },
        {
            "Priority": "P3",
            "Finding": "Retention is very low (6.4% month-1), but returning users "
                       "convert ~5x better and the top 20% of buyers drive 56.5% of revenue.",
            "Recommended Action": "Build a retention/loyalty program targeting "
                                  "first-time buyers and the high-value segment specifically.",
        },
    ])
    st.dataframe(recommendations, hide_index=True)

