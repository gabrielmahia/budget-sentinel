"""
Budget Sentinel Kenya — County development fund absorption tracker.

Tracks how Kenya's 47 counties allocate and spend their annual budgets
against the plans they submitted to the Controller of Budget.

Data: Controller of Budget Annual County Budget Implementation Review Reports.
Source: cob.go.ke/reports/county-budget-implementation-review/
Coverage: FY 2022/23 (47 counties). Annual updates as COB publishes.

Trust rule:
  - All figures are from COB published reports (public domain).
  - When a county's development absorption is below 70%, this tool flags it
    as LOW — this is a factual observation, not an accusation of misconduct.
  - Infrastructure diversion (recurrent spending exceeding its allocation)
    is flagged as an ALERT — again factual, not forensic.
  - This tool does not make accusations. Users verify at cob.go.ke.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Budget Sentinel Kenya",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Mobile CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

.bs-header {
    background: linear-gradient(135deg, #1a2942 0%, #2d4a6e 60%, #3d6491 100%);
    color: white; padding: 1.6rem 2rem; border-radius: 10px; margin-bottom: 1.2rem;
}
.bs-header h1 { font-family:'IBM Plex Mono',monospace; font-size:1.8rem; margin:0 0 .2rem; letter-spacing:-1px; }
.bs-header p  { font-size:.9rem; opacity:.75; margin:0; }

.kpi-card {
    background:#f8f9fa; border-radius:8px; padding:1rem 1.4rem;
    border-left:4px solid #2d4a6e; margin-bottom:.6rem;
}
.kpi-card .label { font-size:.72rem; text-transform:uppercase; letter-spacing:.08em; color:#6c757d; }
.kpi-card .value { font-family:'IBM Plex Mono',monospace; font-size:1.5rem; font-weight:600; color:#1a2942; }

.alert-high   { background:#d4edda; border-left:4px solid #28a745; padding:.6rem 1rem; border-radius:4px; font-size:.83rem; margin:.3rem 0; }
.alert-medium { background:#fff3cd; border-left:4px solid #ffc107; padding:.6rem 1rem; border-radius:4px; font-size:.83rem; margin:.3rem 0; }
.alert-low    { background:#f8d7da; border-left:4px solid #dc3545; padding:.6rem 1rem; border-radius:4px; font-size:.83rem; margin:.3rem 0; }
.alert-warn   { background:#e2d9f3; border-left:4px solid #6f42c1; padding:.6rem 1rem; border-radius:4px; font-size:.83rem; margin:.3rem 0; }

.source-note { background:#e8f4fd; border-left:3px solid #2d4a6e; padding:.5rem .9rem; border-radius:3px; font-size:.8rem; margin-bottom:1rem; }

@media (max-width: 768px) {
    [data-testid="column"] { width:100% !important; flex:1 1 100% !important; min-width:100% !important; }
    [data-testid="stMetricValue"] { font-size:1.3rem !important; }
    [data-testid="stDataFrame"]   { overflow-x:auto !important; }
    .stButton>button { width:100% !important; min-height:48px !important; }
    .bs-header h1 { font-size:1.3rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
DATA = Path(__file__).parent / "data" / "allocations"

@st.cache_data(ttl=86400)
def load_budgets():
    df = pd.read_csv(DATA / "county_budgets_fy2223.csv")
    # Compute derived fields
    df["dev_utilised_kes_m"] = (
        df["development_exp_kes_m"] * df["development_absorption_pct"] / 100
    ).round(1)
    df["dev_unspent_kes_m"] = (
        df["development_exp_kes_m"] - df["dev_utilised_kes_m"]
    ).round(1)
    df["per_capita_kes"] = (
        (df["total_allocation_kes_m"] * 1_000_000) / df["population_2019"]
    ).round(0)
    df["health_pct_of_total"] = (
        df["health_allocation_kes_m"] / df["total_allocation_kes_m"] * 100
    ).round(1)
    df["dev_absorption_band"] = df["development_absorption_pct"].apply(
        lambda x: "🟢 HIGH (≥80%)" if x >= 80
        else "🟡 MEDIUM (70–79%)" if x >= 70
        else "🔴 LOW (<70%)"
    )
    return df

df = load_budgets()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="bs-header">
  <h1>🛡️ Budget Sentinel Kenya</h1>
  <p>County development fund absorption · FY 2022/23 · Controller of Budget data</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="source-note">
📋 <strong>Data source:</strong> Controller of Budget Annual County Budget Implementation Review,
FY 2022/23. All figures are from the public COB report.
Verify and download originals at <a href="https://cob.go.ke/reports/county-budget-implementation-review/" target="_blank">cob.go.ke</a>.
This tool does not make accusations — flag anomalies directly with the COB office.
</div>
""", unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
PAGE = st.sidebar.radio(
    "Navigate",
    ["🗺️ National Overview", "🔍 County Detail", "⚠️ Risk Alerts", "📊 Sector Breakdown", "🔗 Data Sources"],
)

fy_options = ["FY 2022/23"]
fy = st.sidebar.selectbox("Financial year", fy_options)
region_filter = st.sidebar.selectbox(
    "Filter by region",
    ["All regions"] + sorted(df["region"].unique().tolist()),
)

filtered = df.copy()
if region_filter != "All regions":
    filtered = filtered[filtered["region"] == region_filter]


# ═══════════════════════════════════════════════════════════
# NATIONAL OVERVIEW
# ═══════════════════════════════════════════════════════════
if PAGE == "🗺️ National Overview":

    total_allocated = df["total_allocation_kes_m"].sum() / 1000
    total_dev = df["development_exp_kes_m"].sum() / 1000
    total_unspent = df["dev_unspent_kes_m"].sum() / 1000
    avg_absorption = df["development_absorption_pct"].mean()
    low_absorption = (df["development_absorption_pct"] < 70).sum()
    high_absorption = (df["development_absorption_pct"] >= 80).sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total allocated (47 counties)", f"KES {total_allocated:.1f}B")
    c2.metric("Average dev. absorption", f"{avg_absorption:.1f}%")
    c3.metric("Counties: absorption < 70%", str(low_absorption), delta="needs attention", delta_color="inverse")
    c4.metric("Dev. funds unspent", f"KES {total_unspent:.1f}B", delta="vs allocation", delta_color="inverse")

    st.divider()

    # Map / choropleth — county absorption rates ranked
    st.subheader("Development absorption by county")
    st.caption("Development absorption = actual development spending ÷ development allocation × 100")

    chart_df = filtered.sort_values("development_absorption_pct", ascending=True)
    fig = px.bar(
        chart_df,
        x="development_absorption_pct",
        y="county",
        orientation="h",
        color="development_absorption_pct",
        color_continuous_scale=["#dc3545", "#ffc107", "#28a745"],
        range_color=[55, 100],
        labels={"development_absorption_pct": "Dev. absorption %", "county": "County"},
        height=max(500, len(chart_df) * 18),
    )
    fig.add_vline(x=70, line_dash="dash", line_color="#856404", annotation_text="70% threshold")
    fig.add_vline(x=80, line_dash="dot", line_color="#155724", annotation_text="80% target")
    fig.update_layout(showlegend=False, margin=dict(l=140, r=20, t=30, b=30))
    st.plotly_chart(fig, use_container_width=True)

    # Ranked table
    st.subheader("Full county ranking")
    display = filtered[[
        "county", "region", "total_allocation_kes_m",
        "development_exp_kes_m", "development_absorption_pct",
        "dev_unspent_kes_m", "per_capita_kes", "dev_absorption_band"
    ]].sort_values("development_absorption_pct").rename(columns={
        "county": "County",
        "region": "Region",
        "total_allocation_kes_m": "Total (KES M)",
        "development_exp_kes_m": "Dev. budget (KES M)",
        "development_absorption_pct": "Dev. absorption %",
        "dev_unspent_kes_m": "Dev. unspent (KES M)",
        "per_capita_kes": "Per capita (KES)",
        "dev_absorption_band": "Band",
    })
    st.dataframe(display, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════
# COUNTY DETAIL
# ═══════════════════════════════════════════════════════════
elif PAGE == "🔍 County Detail":

    county_name = st.selectbox("Select county", sorted(df["county"].tolist()))
    row = df[df["county"] == county_name].iloc[0]

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f"## {county_name} County")
        st.caption(f"Region: {row['region']} · Population (2019): {int(row['population_2019']):,}")

        # Key metrics
        cc1, cc2, cc3, cc4 = st.columns(4)
        cc1.metric("Total allocation", f"KES {row['total_allocation_kes_m']:,.0f}M")
        cc2.metric("Own revenue raised", f"KES {row['revenue_raised_kes_m']:,.0f}M",
                   delta=f"{row['revenue_raised_kes_m']/row['total_allocation_kes_m']*100:.0f}% of budget")
        cc3.metric("Development absorption", f"{row['development_absorption_pct']:.1f}%")
        cc4.metric("Dev. funds unspent", f"KES {row['dev_unspent_kes_m']:,.0f}M",
                   delta_color="inverse", delta="unspent")

        st.divider()

        # Absorption gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=row["development_absorption_pct"],
            title={"text": "Development absorption %"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#2d4a6e"},
                "steps": [
                    {"range": [0, 70], "color": "#f8d7da"},
                    {"range": [70, 80], "color": "#fff3cd"},
                    {"range": [80, 100], "color": "#d4edda"},
                ],
                "threshold": {
                    "line": {"color": "#dc3545", "width": 3},
                    "thickness": 0.75,
                    "value": 70,
                },
            },
        ))
        fig_gauge.update_layout(height=280, margin=dict(t=30, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with c2:
        st.markdown("#### Sector allocations")
        sectors = {
            "Health": row["health_allocation_kes_m"],
            "Education": row["education_allocation_kes_m"],
            "Infrastructure": row["infrastructure_allocation_kes_m"],
            "Other": row["total_allocation_kes_m"] - row["health_allocation_kes_m"]
                     - row["education_allocation_kes_m"] - row["infrastructure_allocation_kes_m"],
        }
        fig_pie = px.pie(
            values=list(sectors.values()),
            names=list(sectors.keys()),
            color_discrete_sequence=["#2d4a6e", "#4a7fa5", "#7ab3d1", "#b8d4e8"],
        )
        fig_pie.update_layout(height=280, margin=dict(t=10, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)

        st.caption(f"Per capita allocation: **KES {int(row['per_capita_kes']):,}**")
        st.caption(f"Health % of budget: **{row['health_pct_of_total']:.1f}%** (WHO target: 15%)")

    # Absorption status
    st.divider()
    band = row["dev_absorption_band"]
    if "HIGH" in band:
        st.markdown(f'<div class="alert-high">✅ {county_name} development absorption: {row["development_absorption_pct"]:.1f}% — above 80% target</div>', unsafe_allow_html=True)
    elif "MEDIUM" in band:
        st.markdown(f'<div class="alert-medium">🟡 {county_name} development absorption: {row["development_absorption_pct"]:.1f}% — between 70–80%, below target</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="alert-low">⚠️ {county_name} development absorption: '
            f'{row["development_absorption_pct"]:.1f}% — below 70% threshold. '
            f'KES {row["dev_unspent_kes_m"]:,.0f}M in development funds unspent. '
            f'This is a factual observation from COB data — verify at cob.go.ke.</div>',
            unsafe_allow_html=True
        )

    st.caption(f"Source: {row['source']}")


# ═══════════════════════════════════════════════════════════
# RISK ALERTS
# ═══════════════════════════════════════════════════════════
elif PAGE == "⚠️ Risk Alerts":

    st.subheader("⚠️ Development absorption alerts")
    st.caption(
        "These are factual observations from COB data, not accusations. "
        "Low absorption can result from delayed procurement, disputed contracts, "
        "late release of funds, or staffing gaps — as well as misallocation. "
        "Verify causes at cob.go.ke before drawing conclusions."
    )

    low_df = filtered[filtered["development_absorption_pct"] < 70].sort_values("development_absorption_pct")

    if len(low_df) == 0:
        st.success(f"No counties in the selected filter have development absorption below 70%.")
    else:
        st.markdown(f"**{len(low_df)} counties** below 70% development absorption threshold:")
        for _, row in low_df.iterrows():
            with st.expander(
                f"🔴 {row['county']} — {row['development_absorption_pct']:.1f}% "
                f"(KES {row['dev_unspent_kes_m']:,.0f}M unspent)"
            ):
                c1, c2, c3 = st.columns(3)
                c1.metric("Dev. absorption", f"{row['development_absorption_pct']:.1f}%")
                c2.metric("Dev. budget", f"KES {row['development_exp_kes_m']:,.0f}M")
                c3.metric("Unspent", f"KES {row['dev_unspent_kes_m']:,.0f}M")
                st.caption(
                    f"Region: {row['region']} · "
                    f"Total allocation: KES {row['total_allocation_kes_m']:,.0f}M · "
                    f"Own revenue: KES {row['revenue_raised_kes_m']:,.0f}M"
                )
                st.markdown(
                    f"[🔗 Verify at Controller of Budget](https://cob.go.ke/reports/county-budget-implementation-review/)",
                    unsafe_allow_html=False
                )

    st.divider()
    st.subheader("💰 Total unspent development funds")
    total_unspent = filtered["dev_unspent_kes_m"].sum()
    st.metric(
        "Development funds unspent — selected counties",
        f"KES {total_unspent/1000:.2f}B",
        help="Sum of (development budget × (1 - absorption rate)) for all counties in the current filter"
    )
    st.caption(
        "This represents the gap between what was planned for development spending "
        "and what was actually spent. Unspent funds must be returned to the Consolidated Fund "
        "or re-appropriated in the next budget cycle."
    )

    # Scatter: absorption vs per-capita allocation
    st.divider()
    st.subheader("Absorption vs per-capita allocation")
    fig = px.scatter(
        filtered,
        x="per_capita_kes",
        y="development_absorption_pct",
        text="county",
        color="region",
        size="total_allocation_kes_m",
        labels={
            "per_capita_kes": "Per capita allocation (KES)",
            "development_absorption_pct": "Dev. absorption %",
        },
        title="More resources ≠ better absorption",
        height=450,
    )
    fig.add_hline(y=70, line_dash="dash", line_color="#856404", annotation_text="70% threshold")
    fig.update_traces(textposition="top center", textfont_size=9)
    fig.update_layout(margin=dict(t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Bubble size = total budget allocation. Counties above the dashed line met the 70% threshold."
    )


# ═══════════════════════════════════════════════════════════
# SECTOR BREAKDOWN
# ═══════════════════════════════════════════════════════════
elif PAGE == "📊 Sector Breakdown":

    st.subheader("📊 Health, education, and infrastructure allocations")
    st.caption("Sector allocations as a share of total county budget — FY 2022/23")

    sector_df = filtered[["county", "region", "health_allocation_kes_m",
                           "education_allocation_kes_m", "infrastructure_allocation_kes_m",
                           "total_allocation_kes_m"]].copy()
    sector_df["health_pct"] = (sector_df["health_allocation_kes_m"] / sector_df["total_allocation_kes_m"] * 100).round(1)
    sector_df["edu_pct"] = (sector_df["education_allocation_kes_m"] / sector_df["total_allocation_kes_m"] * 100).round(1)
    sector_df["infra_pct"] = (sector_df["infrastructure_allocation_kes_m"] / sector_df["total_allocation_kes_m"] * 100).round(1)

    tab_health, tab_edu, tab_infra = st.tabs(["🏥 Health", "📚 Education", "🏗️ Infrastructure"])

    with tab_health:
        health_sorted = sector_df.sort_values("health_pct", ascending=True)
        fig = px.bar(
            health_sorted, x="health_pct", y="county", orientation="h",
            color="health_pct", color_continuous_scale=["#f8d7da", "#d4edda"],
            labels={"health_pct": "Health % of total budget", "county": ""},
            height=max(500, len(health_sorted) * 18),
        )
        fig.add_vline(x=15, line_dash="dash", annotation_text="WHO 15% target")
        fig.update_layout(showlegend=False, margin=dict(l=140))
        st.plotly_chart(fig, use_container_width=True)
        above_who = (sector_df["health_pct"] >= 15).sum()
        st.metric("Counties meeting WHO 15% health target", f"{above_who} / {len(sector_df)}")

    with tab_edu:
        edu_sorted = sector_df.sort_values("edu_pct", ascending=True)
        fig = px.bar(
            edu_sorted, x="edu_pct", y="county", orientation="h",
            color="edu_pct", color_continuous_scale=["#f8d7da", "#cfe2ff"],
            labels={"edu_pct": "Education % of total budget", "county": ""},
            height=max(500, len(edu_sorted) * 18),
        )
        fig.update_layout(showlegend=False, margin=dict(l=140))
        st.plotly_chart(fig, use_container_width=True)

    with tab_infra:
        infra_sorted = sector_df.sort_values("infra_pct", ascending=True)
        fig = px.bar(
            infra_sorted, x="infra_pct", y="county", orientation="h",
            color="infra_pct", color_continuous_scale=["#f8d7da", "#fff3cd"],
            labels={"infra_pct": "Infrastructure % of total budget", "county": ""},
            height=max(500, len(infra_sorted) * 18),
        )
        fig.update_layout(showlegend=False, margin=dict(l=140))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Regional comparison")
    region_agg = filtered.groupby("region").agg(
        avg_dev_absorption=("development_absorption_pct", "mean"),
        total_allocated=("total_allocation_kes_m", "sum"),
        total_unspent=("dev_unspent_kes_m", "sum"),
        counties=("county", "count"),
    ).round(1).reset_index()
    region_agg.columns = ["Region", "Avg dev. absorption %", "Total allocated (KES M)", "Dev. unspent (KES M)", "Counties"]
    st.dataframe(region_agg, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════
# DATA SOURCES
# ═══════════════════════════════════════════════════════════
elif PAGE == "🔗 Data Sources":

    st.subheader("🔗 Data sources and methodology")
    st.markdown("""
**Primary source**

All county allocation and absorption figures are from the
[Controller of Budget Annual County Budget Implementation Review Report, FY 2022/23](https://cob.go.ke/reports/county-budget-implementation-review/).
The Controller of Budget is an independent office established under Article 228 of the
Constitution of Kenya. Reports are public domain.

**Coverage**

- 46 counties covered (FY 2022/23 data; all 47 counties available in COB report)
- Annual updates will be added as COB publishes new reports
- Quarterly implementation data (where published) will be added in future releases

**Column definitions**

| Column | Definition |
|--------|-----------|
| `total_allocation_kes_m` | Total county government budget allocation (KES millions) |
| `revenue_raised_kes_m` | Own-source revenue collected by the county |
| `recurrent_exp_kes_m` | Spending on salaries, operations, and non-capital items |
| `development_exp_kes_m` | Capital / development project budget |
| `absorption_pct` | Total expenditure ÷ total allocation × 100 |
| `development_absorption_pct` | Dev. expenditure ÷ dev. allocation × 100 |

**Thresholds used in alerts**

- **Development absorption < 70%** — flagged as LOW (COB benchmarks counties against 70%)
- **Development absorption 70–80%** — flagged as MEDIUM
- **Development absorption ≥ 80%** — flagged as HIGH (COB target)
- **Health < 15% of total** — flagged against WHO Abuja Declaration target

**What this tool does NOT do**

- It does not access or display individual procurement records or contracts
- It does not name individuals as responsible for under-absorption
- It does not make forensic accounting conclusions
- Low absorption has many causes beyond misconduct (procurement delays, late fund releases, capacity gaps)

**How to report an error**

Open a GitHub issue at github.com/gabrielmahia/budget-sentinel with the correct
figure and a link to the relevant COB report page.
""")

    st.divider()
    st.subheader("Download raw data")
    df_download = df.drop(columns=["dev_absorption_band"])
    st.download_button(
        "📥 Download full dataset (CSV)",
        df_download.to_csv(index=False).encode(),
        file_name="budget_sentinel_fy2223.csv",
        mime="text/csv",
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Budget Sentinel Kenya · Data: Controller of Budget FY 2022/23 (public domain) · "
    "App: CC BY-NC-ND 4.0 · contact@aikungfu.dev · "
    "Not affiliated with the Controller of Budget or any county government · "
    "Low absorption is a factual observation, not an accusation"
)
