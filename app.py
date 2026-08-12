import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Verified Logistics Dashboard",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# FILE PATHS
# =========================================================

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "logistics_dataset.csv"
# Full lockup (shield mark + "VERIFIED LOGISTICS" wordmark + tagline),
# background made transparent - used next to the title on the white header.
LOGO_PATH = BASE_DIR / "verified logo.png"
# Icon-only crop of just the shield mark, background transparent - used in
# the sidebar so it pairs with the sidebar's own white "VERIFIED"/"LOGISTICS"
# text instead of repeating the wordmark a second time.
SIDEBAR_ICON_PATH = BASE_DIR / "verified logo.png"


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* ================================
       MAIN BACKGROUND
       ================================ */

    .main {
        background-color: #ffffff;
    }

    /* ================================
       SIDEBAR
       ================================ */

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #0645A5 0%,
            #0B5BC7 100%
        );
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    /* Sidebar text */

    [data-testid="stSidebar"] label {
        color: white !important;
        font-weight: 500 !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p {
        color: white !important;
    }

    /* ================================
       SIDEBAR MULTISELECT
       ================================ */

    [data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: white;
        border-radius: 10px;
    }

    /* Selected filter tags */

    [data-testid="stSidebar"] div[data-baseweb="tag"] {
        background-color: #0B5BC7 !important;
        color: white !important;
        border-radius: 6px !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="tag"] span {
        color: white !important;
    }

    /* ================================
       DASHBOARD TITLE
       ================================ */

    .dashboard-title {
        font-size: 42px;
        font-weight: 750;
        color: #172033;
        line-height: 1.1;
        margin-bottom: 5px;
    }

    .dashboard-subtitle {
        font-size: 17px;
        color: #667085;
        margin-top: 5px;
    }

    /* ================================
       KPI CARDS
       ================================ */

    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    div[data-testid="stMetricLabel"] {
        color: #667085 !important;
        font-weight: 600 !important;
    }

    /* FIX: Streamlit's default metric-value styling applies
       white-space: nowrap + overflow: hidden + text-overflow: ellipsis,
       which clips long formatted numbers (e.g. "844,227" -> "84...").
       Override it to size down gracefully instead of truncating. */

    div[data-testid="stMetricValue"] {
        color: #172033 !important;
        font-weight: 700 !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        font-size: clamp(18px, 2vw, 28px) !important;
        line-height: 1.2 !important;
    }

    /* ================================
       SECTION HEADINGS
       ================================ */

    .section-title {
        font-size: 25px;
        font-weight: 700;
        color: #172033;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    /* ================================
       DATAFRAME
       ================================ */

    [data-testid="stDataFrame"] {
        border-radius: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    df = pd.read_csv(DATA_PATH)

    # Convert date column
    df["last_restock_date"] = pd.to_datetime(
        df["last_restock_date"],
        errors="coerce"
    )

    return df


df = load_data()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    # Logo (icon-only, since the sidebar text below already spells out
    # "VERIFIED LOGISTICS" - using the full lockup here would repeat it)
    if SIDEBAR_ICON_PATH.exists():
        st.image(
            str(SIDEBAR_ICON_PATH),
            width=90
        )
    else:
        st.warning("Sidebar icon file not found.")

    # Sidebar branding
    # FIX: every line of this HTML starts at column 0 (no leading
    # whitespace) and there is no blank line inside the block. A blank
    # line inside an st.markdown HTML string breaks Markdown's "raw HTML
    # passthrough," and any indented (4+ space) line that follows gets
    # parsed as an indented code block instead of HTML - which is what
    # was rendering as literal <div> text before.
    st.sidebar.markdown(
        """<div style="text-align:center;margin-top:8px;margin-bottom:30px;">
<div style="color:white;font-size:20px;font-weight:700;letter-spacing:2px;">VERIFIED</div>
<div style="color:#DCEBFF;font-size:12px;letter-spacing:4px;margin-top:2px;">LOGISTICS</div>
</div>""",
        unsafe_allow_html=True
    )

    st.markdown(
        """<div style="color:white;font-size:22px;font-weight:700;margin-bottom:20px;">Dashboard Filters</div>""",
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # CATEGORY FILTER
    # -----------------------------------------------------

    categories = sorted(
        df["category"].dropna().unique()
    )

    selected_categories = st.multiselect(
        "Category",
        options=categories,
        default=categories,
        key="category_filter"
    )

    # -----------------------------------------------------
    # WAREHOUSE ZONE FILTER
    # -----------------------------------------------------

    zones = sorted(
        df["zone"].dropna().unique()
    )

    selected_zones = st.multiselect(
        "Warehouse Zone",
        options=zones,
        default=zones,
        key="zone_filter"
    )


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df[
    (df["category"].isin(selected_categories))
    &
    (df["zone"].isin(selected_zones))
]


# =========================================================
# TITLE / HEADER
# =========================================================

logo_col, title_col = st.columns(
    [0.8, 9]
)

with logo_col:

    if LOGO_PATH.exists():
        st.image(
            str(LOGO_PATH),
            width=70
        )

with title_col:

    st.markdown(
        """
        <div class="dashboard-title">
            Verified Logistics Dashboard
        </div>

        <div class="dashboard-subtitle">
            Inventory, Warehouse & Supply Chain Performance
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_items = filtered_df["item_id"].nunique()

total_stock = filtered_df["stock_level"].sum()

avg_fulfillment = (
    filtered_df["order_fulfillment_rate"].mean() * 100
)

total_stockouts = (
    filtered_df["stockout_count_last_month"].sum()
)

avg_turnover = (
    filtered_df["turnover_ratio"].mean()
)

avg_kpi = (
    filtered_df["KPI_score"].mean()
)


# =========================================================
# KPI CARDS
# =========================================================

# FIX: 6 cards squeezed into one row left very little width per card,
# which is what triggered Streamlit's built-in ellipsis truncation in
# the first place. Two rows of three gives each card roughly double
# the width, so the CSS override above rarely even needs to shrink
# the font.

kpi_row1 = st.columns(3)
kpi_row2 = st.columns(3)

kpi_row1[0].metric("Total Items", f"{total_items:,}")
kpi_row1[1].metric("Total Stock", f"{total_stock:,.0f}")
kpi_row1[2].metric("Fulfillment", f"{avg_fulfillment:.1f}%")

kpi_row2[0].metric("Stockouts", f"{total_stockouts:,.0f}")
kpi_row2[1].metric("Turnover", f"{avg_turnover:.2f}")
kpi_row2[2].metric("Avg KPI", f"{avg_kpi:.2f}")


st.divider()


# =========================================================
# INVENTORY OVERVIEW
# =========================================================

st.markdown(
    '<div class="section-title">Inventory Overview</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)


# ---------------------------------------------------------
# INVENTORY BY CATEGORY
# ---------------------------------------------------------

with col1:

    category_stock = (
        filtered_df
        .groupby("category")["stock_level"]
        .sum()
        .reset_index()
        .sort_values(
            "stock_level",
            ascending=False
        )
    )

    fig_category_stock = px.bar(
        category_stock,
        x="category",
        y="stock_level",
        title="Total Inventory by Category",
        labels={
            "category": "Category",
            "stock_level": "Stock Level"
        }
    )

    st.plotly_chart(
        fig_category_stock,
        width="stretch",
        key="inventory_by_category"
    )


# ---------------------------------------------------------
# STOCKOUTS BY CATEGORY
# ---------------------------------------------------------

with col2:

    stockouts = (
        filtered_df
        .groupby("category")[
            "stockout_count_last_month"
        ]
        .sum()
        .reset_index()
        .sort_values(
            "stockout_count_last_month",
            ascending=False
        )
    )

    fig_stockouts = px.bar(
        stockouts,
        x="category",
        y="stockout_count_last_month",
        title="Stockouts by Category",
        labels={
            "category": "Category",
            "stockout_count_last_month": "Stockouts"
        }
    )

    st.plotly_chart(
        fig_stockouts,
        width="stretch",
        key="stockouts_by_category"
    )


# =========================================================
# INVENTORY RISK ANALYSIS
# =========================================================

st.markdown(
    '<div class="section-title">Inventory Risk Analysis</div>',
    unsafe_allow_html=True
)

fig_risk = px.scatter(
    filtered_df,
    x="reorder_point",
    y="stock_level",
    color="category",
    hover_data=[
        "item_id",
        "zone",
        "daily_demand",
        "forecasted_demand_next_7d"
    ],
    title="Stock Level vs Reorder Point",
    labels={
        "reorder_point": "Reorder Point",
        "stock_level": "Current Stock"
    }
)

st.plotly_chart(
    fig_risk,
    width="stretch",
    key="inventory_risk_analysis"
)


# =========================================================
# WAREHOUSE PERFORMANCE
# =========================================================

st.markdown(
    '<div class="section-title">Warehouse Performance</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)


# ---------------------------------------------------------
# FULFILLMENT RATE BY ZONE
# ---------------------------------------------------------

with col1:

    zone_fulfillment = (
        filtered_df
        .groupby("zone")[
            "order_fulfillment_rate"
        ]
        .mean()
        .reset_index()
    )

    zone_fulfillment[
        "order_fulfillment_rate"
    ] = (
        zone_fulfillment[
            "order_fulfillment_rate"
        ] * 100
    )

    fig_zone_fulfillment = px.bar(
        zone_fulfillment,
        x="zone",
        y="order_fulfillment_rate",
        title="Fulfillment Rate by Zone",
        labels={
            "zone": "Zone",
            "order_fulfillment_rate":
                "Fulfillment Rate (%)"
        }
    )

    st.plotly_chart(
        fig_zone_fulfillment,
        width="stretch",
        key="fulfillment_by_zone"
    )


# ---------------------------------------------------------
# PICKING TIME BY ZONE
# ---------------------------------------------------------

with col2:

    zone_picking = (
        filtered_df
        .groupby("zone")[
            "picking_time_seconds"
        ]
        .mean()
        .reset_index()
    )

    fig_zone_picking = px.bar(
        zone_picking,
        x="zone",
        y="picking_time_seconds",
        title="Average Picking Time by Zone",
        labels={
            "zone": "Zone",
            "picking_time_seconds":
                "Picking Time (seconds)"
        }
    )

    st.plotly_chart(
        fig_zone_picking,
        width="stretch",
        key="picking_time_by_zone"
    )


# =========================================================
# DEMAND ANALYSIS
# =========================================================

st.markdown(
    '<div class="section-title">Demand Analysis</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)


# ---------------------------------------------------------
# CURRENT VS FORECASTED DEMAND
# ---------------------------------------------------------

with col1:

    demand = (
        filtered_df
        .groupby("category")[
            [
                "daily_demand",
                "forecasted_demand_next_7d"
            ]
        ]
        .mean()
        .reset_index()
    )

    fig_demand = px.bar(
        demand,
        x="category",
        y=[
            "daily_demand",
            "forecasted_demand_next_7d"
        ],
        barmode="group",
        title="Current vs Forecasted Demand",
        labels={
            "value": "Demand",
            "category": "Category",
            "variable": "Demand Type"
        }
    )

    st.plotly_chart(
        fig_demand,
        width="stretch",
        key="current_vs_forecast_demand"
    )


# ---------------------------------------------------------
# DEMAND VS TURNOVER
# ---------------------------------------------------------

with col2:

    fig_turnover = px.scatter(
        filtered_df,
        x="daily_demand",
        y="turnover_ratio",
        color="category",
        hover_data=[
            "item_id",
            "stock_level",
            "order_fulfillment_rate"
        ],
        title="Demand vs Inventory Turnover",
        labels={
            "daily_demand": "Daily Demand",
            "turnover_ratio": "Turnover Ratio"
        }
    )

    st.plotly_chart(
        fig_turnover,
        width="stretch",
        key="demand_vs_turnover"
    )


# =========================================================
# KPI PERFORMANCE
# =========================================================

st.markdown(
    '<div class="section-title">⭐ KPI Performance by Zone</div>',
    unsafe_allow_html=True
)

zone_kpi = (
    filtered_df
    .groupby("zone")["KPI_score"]
    .mean()
    .reset_index()
    .sort_values(
        "KPI_score",
        ascending=False
    )
)

fig_kpi = px.bar(
    zone_kpi,
    x="zone",
    y="KPI_score",
    title="Average KPI Score by Warehouse Zone",
    labels={
        "zone": "Zone",
        "KPI_score": "KPI Score"
    }
)

st.plotly_chart(
    fig_kpi,
    width="stretch",
    key="kpi_performance_by_zone"
)


# =========================================================
# DETAILED DATA
# =========================================================

st.markdown(
    '<div class="section-title">📋 Detailed Logistics Data</div>',
    unsafe_allow_html=True
)

st.caption(
    f"Showing {len(filtered_df):,} records "
    "based on the selected filters."
)

st.dataframe(
    filtered_df,
    width="stretch",
    hide_index=True
)

