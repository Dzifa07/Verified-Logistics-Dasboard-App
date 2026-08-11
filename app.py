import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Verified Logistics Dashboard",
    page_icon="📦",
    layout="wide"
)

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():
    df = pd.read_csv("logistics_dataset.csv")
    
    # Convert date column
    df["last_restock_date"] = pd.to_datetime(
        df["last_restock_date"],
        errors="coerce"
    )
    
    return df


df = load_data()

# =========================================================
# TITLE
# =========================================================

st.title("📦 Verified Logistics Dashboard")

st.markdown(
    "### Inventory, Warehouse & Supply Chain Performance"
)

st.divider()

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🔎 Dashboard Filters")

# Category filter
categories = sorted(df["category"].dropna().unique())

selected_categories = st.sidebar.multiselect(
    "Category",
    options=categories,
    default=categories
)

# Zone filter
zones = sorted(df["zone"].dropna().unique())

selected_zones = st.sidebar.multiselect(
    "Warehouse Zone",
    options=zones,
    default=zones
)

# Apply filters
filtered_df = df[
    (df["category"].isin(selected_categories)) &
    (df["zone"].isin(selected_zones))
]

# =========================================================
# KPI CALCULATIONS
# =========================================================

total_items = filtered_df["item_id"].nunique()

total_stock = filtered_df["stock_level"].sum()

avg_fulfillment = filtered_df[
    "order_fulfillment_rate"
].mean() * 100

total_stockouts = filtered_df[
    "stockout_count_last_month"
].sum()

avg_turnover = filtered_df[
    "turnover_ratio"
].mean()

avg_kpi = filtered_df[
    "KPI_score"
].mean()

# =========================================================
# KPI CARDS
# =========================================================

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric(
    "Total Items",
    f"{total_items:,}"
)

col2.metric(
    "Total Stock",
    f"{total_stock:,.0f}"
)

col3.metric(
    "Fulfillment Rate",
    f"{avg_fulfillment:.1f}%"
)

col4.metric(
    "Stockouts",
    f"{total_stockouts:,.0f}"
)

col5.metric(
    "Turnover Ratio",
    f"{avg_turnover:.2f}"
)

col6.metric(
    "Avg KPI Score",
    f"{avg_kpi:.2f}"
)

st.divider()

# =========================================================
# INVENTORY BY CATEGORY
# =========================================================

st.subheader("📦 Inventory Overview")

col1, col2 = st.columns(2)

with col1:

    category_stock = (
        filtered_df
        .groupby("category")["stock_level"]
        .sum()
        .reset_index()
        .sort_values("stock_level", ascending=False)
    )

    fig = px.bar(
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
        fig,
        use_container_width=True
    )

# =========================================================
# STOCKOUTS BY CATEGORY
# =========================================================

with col2:

    stockouts = (
        filtered_df
        .groupby("category")["stockout_count_last_month"]
        .sum()
        .reset_index()
        .sort_values(
            "stockout_count_last_month",
            ascending=False
        )
    )

    fig = px.bar(
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
        fig,
        use_container_width=True
    )

# =========================================================
# STOCK LEVEL VS REORDER POINT
# =========================================================

st.subheader("📊 Inventory Risk Analysis")

fig = px.scatter(
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
    fig,
    use_container_width=True
)

# =========================================================
# WAREHOUSE PERFORMANCE
# =========================================================

st.subheader("🏭 Warehouse Performance")

col1, col2 = st.columns(2)

with col1:

    zone_fulfillment = (
        filtered_df
        .groupby("zone")["order_fulfillment_rate"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        zone_fulfillment,
        x="zone",
        y="order_fulfillment_rate",
        title="Fulfillment Rate by Zone",
        labels={
            "zone": "Zone",
            "order_fulfillment_rate": "Fulfillment Rate (%)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    zone_picking = (
        filtered_df
        .groupby("zone")["picking_time_seconds"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        zone_picking,
        x="zone",
        y="picking_time_seconds",
        title="Average Picking Time by Zone",
        labels={
            "zone": "Zone",
            "picking_time_seconds": "Picking Time (seconds)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================================================
# DEMAND ANALYSIS
# =========================================================

st.subheader("📈 Demand Analysis")

col1, col2 = st.columns(2)

with col1:

    demand = (
        filtered_df
        .groupby("category")[
            ["daily_demand", "forecasted_demand_next_7d"]
        ]
        .mean()
        .reset_index()
    )

    fig = px.bar(
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
        fig,
        use_container_width=True
    )

with col2:

    fig = px.scatter(
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
        fig,
        use_container_width=True
    )

# =========================================================
# KPI PERFORMANCE
# =========================================================

st.subheader("⭐ KPI Performance by Zone")

zone_kpi = (
    filtered_df
    .groupby("zone")["KPI_score"]
    .mean()
    .reset_index()
    .sort_values("KPI_score", ascending=False)
)

fig = px.bar(
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
    fig,
    st.plotly_chart(fig, width="stretch")
)

# =========================================================
# DETAILED DATA
# =========================================================

st.subheader("📋 Detailed Logistics Data")

st.caption(
    f"Showing {len(filtered_df):,} records based on the selected filters."
)

st.dataframe(
    filtered_df,
    width="stretch",
    hide_index=True
)

df = load_data()

st.write("Fulfillment Rate values:")
st.write(df["order_fulfillment_rate"].describe())

st.write("KPI Score values:")
st.write(df["KPI_score"].describe())

df = load_data()

st.write("Fulfillment Rate values:")
st.write(df["order_fulfillment_rate"].describe())

st.write("KPI Score values:")
st.write(df["KPI_score"].describe())

