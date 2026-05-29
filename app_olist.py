# RetailIQ Streamlit App using SQLite3
# ============================================================

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# 1. Page Setup
# ============================================================

st.set_page_config(
    page_title="RetailIQ Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# DASHBOARD HEADER
# ============================================================

st.markdown(
    """
    <style>

    /* Main app background */
    .stApp {
        background-color: #F5F7FA;
    }

    /* Main Title Styling */
    .main-title {
        text-align: center;
        font-size: 50px;
        font-weight: 800;
        background: linear-gradient(90deg, #4F8BF9, #1F4E79);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }

    /* Subtitle Box */
    .subtitle-box {
        background: linear-gradient(90deg, #4F8BF9, #FF4B4B);
        padding: 22px;
        border-radius: 18px;
        text-align: center;
        color: white;
        font-size: 22px;
        font-weight: 500;
        box-shadow: 0px 6px 20px rgba(0,0,0,0.15);
        margin-bottom: 30px;
    }

    /* Divider Line */
    .custom-line {
        border-top: 3px solid #4F8BF9;
        margin-top: 10px;
        margin-bottom: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# MAIN TITLE
# ============================================================

st.markdown(
    """
    <div class="main-title">
        RetailIQ: Advanced E-Commerce Intelligence Platform
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SUBTITLE / DESCRIPTION
# ============================================================

st.markdown(
    """
    <div class="subtitle-box">
        This dashboard analyzes e-commerce sales, customer behavior,
        delivery performance, review scores, and product categories
        using <b>Python</b>, <b>SQL</b>, <b>SQLite3</b>, 
        <b>Tableau</b>, and <b>Streamlit</b>.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DIVIDER
# ============================================================

st.markdown(
    """
    <div class="custom-line"></div>
    """,
    unsafe_allow_html=True
)

# 2. Load Data From SQLite
# ============================================================

@st.cache_data
def load_data():
    conn = sqlite3.connect("e_commerce_olist.db")

    query = """
    SELECT *
    FROM Complete_data;
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df

@st.cache_data
def load_rfm_segments():
    conn = sqlite3.connect("dashboard_data.db")

    query = """
    SELECT *
    FROM rfm_segments;
    """

    rfm = pd.read_sql_query(query, conn)

    conn.close()

    return rfm


df = load_data()
rfm_summary = load_rfm_segments()

# FIX MISSING VALUES
# ============================================================

df["customer_state"] = df["customer_state"].fillna("Unknown")

df["product_category_name_english"] = (
    df["product_category_name_english"]
    .fillna("Unknown")
)

# 3. Data Preparation
# ============================================================

df["order_purchase_timestamp"] = pd.to_datetime(
    df["order_purchase_timestamp"],
    errors="coerce"
)

df["order_year"] = df["order_purchase_timestamp"].dt.year

# 4. Sidebar Filters
# ============================================================


# Sidebar Styling
st.markdown("""
<style>

/* Sidebar background */
section[data-testid="stSidebar"] {
    background: linear-gradient( 180deg,
        #2E8B57);
    padding-top: 20px;
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: white;
}

/* Sidebar title */
.sidebar-title {
    font-size: 28px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 20px;
}

/* Filter section */
.filter-box {
    background-color: rgba(255,255,255,0.1);
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR HEADER
# ============================================================

st.sidebar.markdown(
    """
    <div class="sidebar-title">
        🎛 Dashboard Filters
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CUSTOMER STATE FILTER
# ============================================================

st.sidebar.markdown(
    """
    <div class="filter-box">
    <h4>📍 Select Customer State</h4>
    </div>
    """,
    unsafe_allow_html=True
)

states = sorted(df["customer_state"].dropna().unique())

selected_states = st.sidebar.multiselect(
    label="",
    options=states,
    default=states[:5]
)


# ============================================================
# PRODUCT CATEGORY FILTER
# ============================================================

st.sidebar.markdown(
    """
    <div class="filter-box">
    <h4>📦 Select Product Category</h4>
    </div>
    """,
    unsafe_allow_html=True
)

categories = sorted(
    df["product_category_name_english"]
    .dropna()
    .unique()
)

selected_categories = st.sidebar.multiselect(
    label="",
    options=categories,
    default=categories[:5]
)


# ============================================================
# YEAR FILTER
# ============================================================

st.sidebar.markdown(
    """
    <div class="filter-box">
    <h4>📅 Select Year</h4>
    </div>
    """,
    unsafe_allow_html=True
)

years = sorted(df["order_year"].dropna().unique())

selected_years = st.sidebar.multiselect(
    label="",
    options=years,
    default=years
)

# 5. Apply Filters
# ============================================================

filtered_df = df[
    (df["customer_state"].isin(selected_states)) &
    (df["product_category_name_english"].isin(selected_categories)) &
    (df["order_year"].isin(selected_years))
]

# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df[
    (df["customer_state"].isin(selected_states)) &
    (df["product_category_name_english"].isin(selected_categories)) &
    (df["order_year"].isin(selected_years))
]


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_revenue = filtered_df["revenue"].sum()

total_orders = filtered_df["order_id"].nunique()

total_customers = filtered_df["customer_unique_id"].nunique()

avg_order_value = (
    total_revenue / total_orders
    if total_orders > 0
    else 0
)

avg_review_score = filtered_df["review_score"].mean()

delay_rate = filtered_df["is_delayed"].mean() * 100


# ============================================================
# BEAUTIFUL EXECUTIVE KPI SECTION
# ============================================================

st.markdown(
    """
    <style>

    /* KPI Section Title */
    .kpi-title {
        font-size: 38px;
        font-weight: 800;
        color: #1F4E79;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 25px;
        letter-spacing: 1px;
    }

    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #4F8BF9, #1F4E79);
        padding: 22px;
        border-radius: 20px;
        text-align: center;
        color: white;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.15);
        transition: 0.3s;
    }

    /* Hover Effect */
    .kpi-card:hover {
        transform: scale(1.03);
    }

    /* KPI Labels */
    .kpi-label {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 10px;
        opacity: 0.9;
    }

    /* KPI Values */
    .kpi-value {
        font-size: 30px;
        font-weight: 800;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# KPI TITLE
# ============================================================

st.markdown(
    """
    <div class="kpi-title">
        📈 Executive KPI Overview
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4, col5, col6 = st.columns(6)


# Revenue
with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">💰 Revenue</div>
        <div class="kpi-value">${total_revenue:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)


# Orders
with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">📦 Orders</div>
        <div class="kpi-value">{total_orders:,}</div>
    </div>
    """, unsafe_allow_html=True)


# Customers
with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">👥 Customers</div>
        <div class="kpi-value">{total_customers:,}</div>
    </div>
    """, unsafe_allow_html=True)


# Average Order Value
with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">🛒 Avg Order</div>
        <div class="kpi-value">${avg_order_value:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)


# Average Review
with col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">⭐ Avg Review</div>
        <div class="kpi-value">{avg_review_score:.2f}</div>
    </div>
    """, unsafe_allow_html=True)


# Delay Rate
with col6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">🚚 Delay Rate</div>
        <div class="kpi-value">{delay_rate:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

# CREATE DASHBOARD TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Sales Analysis",
    "📦 Product Analysis",
    "🚚 Delivery & Reviews",
    "👥 Customer Segmentation",
    "💡 Recommendations"
])

# TAB 1: Sales Analysis
# ============================================================

with tab1:

    st.subheader("Monthly Revenue Trend")

    monthly_sales = filtered_df.groupby("year_month").agg(
        total_revenue=("revenue", "sum"),
        total_orders=("order_id", "nunique")
    ).reset_index()

    fig_monthly = px.line(
        monthly_sales,
        x="year_month",
        y="total_revenue",
        markers=True,
        title="Monthly Revenue Trend"
    )

    st.plotly_chart(fig_monthly, use_container_width=True)

    st.info(
        "Insight: This chart shows how revenue changes over time and helps identify growth or seasonality."
    )

    st.subheader("Revenue by State")

    state_revenue = filtered_df.groupby("customer_state").agg(
        total_revenue=("revenue", "sum"),
        total_orders=("order_id", "nunique")
    ).reset_index()

    state_revenue = state_revenue.sort_values(
        "total_revenue",
        ascending=False
    )

    fig_state = px.bar(
        state_revenue,
        x="customer_state",
        y="total_revenue",
        title="Revenue by State"
    )

    st.plotly_chart(fig_state, use_container_width=True)


    # TAB 2: Product Analysis
# ============================================================

with tab2:

    st.subheader("Top Product Categories")

    category_revenue = filtered_df.groupby(
        "product_category_name_english"
    ).agg(
        total_revenue=("revenue", "sum"),
        total_orders=("order_id", "nunique"),
        avg_review_score=("review_score", "mean")
    ).reset_index()

    category_revenue = category_revenue.sort_values(
        "total_revenue",
        ascending=False
    ).head(10)

    fig_category = px.bar(
        category_revenue,
        x="product_category_name_english",
        y="total_revenue",
        title="Top 10 Product Categories by Revenue"
    )

    st.plotly_chart(fig_category, use_container_width=True)

    st.info(
        "Insight: These categories generate the highest revenue and can be prioritized for marketing."
    )

    st.subheader("Average Review Score by Top Categories")

    fig_category_review = px.bar(
        category_revenue,
        x="product_category_name_english",
        y="avg_review_score",
        title="Average Review Score by Category"
    )

    st.plotly_chart(fig_category_review, use_container_width=True)

# ============================================================
# TAB 3: DELIVERY & REVIEW ANALYSIS
# ============================================================

with tab3:

    st.subheader("🚚 Delivery Delay vs Review Score")


    # ========================================================
    # CREATE READABLE LABELS
    # ========================================================

    delivery_review = filtered_df.copy()

    delivery_review["delivery_status"] = delivery_review[
        "is_delayed"
    ].map({
        0: "✅ On-Time Delivery",
        1: "❌ Delayed Delivery"
    })


    # ========================================================
    # REVIEW SCORE SUMMARY
    # ========================================================

    review_summary = delivery_review.groupby(
        "delivery_status"
    ).agg(
        avg_review_score=("review_score", "mean"),
        total_orders=("order_id", "nunique")
    ).reset_index()


    # ========================================================
    # BEAUTIFUL BAR CHART
    # ========================================================

    fig_delay_review = px.bar(
        review_summary,
        x="delivery_status",
        y="avg_review_score",
        color="delivery_status",
        text_auto=".2f",
        title="Average Review Score: On-Time vs Delayed Orders",
        labels={
            "delivery_status": "Delivery Status",
            "avg_review_score": "Average Review Score"
        }
    )


    # ========================================================
    # IMPROVE CHART DESIGN
    # ========================================================

    fig_delay_review.update_layout(
        title_x=0.18,
        xaxis_title="Delivery Status",
        yaxis_title="Average Review Score",
        showlegend=False,
        height=500,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            size=14
        )
    )


    # ========================================================
    # IMPROVE BAR APPEARANCE
    # ========================================================

    fig_delay_review.update_traces(
        textposition="outside",
        marker_line_width=2
    )


    # ========================================================
    # SHOW CHART
    # ========================================================

    st.plotly_chart(
        fig_delay_review,
        use_container_width=True
    )


    # ========================================================
    # BUSINESS INSIGHT
    # ========================================================

    st.info("""
    📌 Insight:
    
    Customers who receive delayed orders tend to give lower review scores.
    This suggests that delivery performance directly impacts customer satisfaction.
    """)


    # ========================================================
    # DELIVERY PERFORMANCE BY STATE
    # ========================================================

    st.subheader("📍 Delivery Performance by State")

    delivery_state = filtered_df.groupby(
        "customer_state"
    ).agg(
        avg_delivery_days=("delivery_days", "mean"),
        avg_delay_days=("delay_days", "mean"),
        delay_rate=("is_delayed", "mean"),
        avg_review_score=("review_score", "mean")
    ).reset_index()

    delivery_state["delay_rate"] = (
        delivery_state["delay_rate"] * 100
    )

    delivery_state = delivery_state.sort_values(
        "avg_delivery_days",
        ascending=False
    )


    # ========================================================
    # STATE DELIVERY BAR CHART
    # ========================================================

    fig_delivery = px.bar(
        delivery_state,
        x="customer_state",
        y="avg_delivery_days",
        color="delay_rate",
        title="Average Delivery Days by State",
        labels={
            "customer_state": "State",
            "avg_delivery_days": "Avg Delivery Days",
            "delay_rate": "Delay Rate %"
        }
    )


    # ========================================================
    # UPDATE DESIGN
    # ========================================================

    fig_delivery.update_layout(
        title_x=0.25,
        height=550,
        plot_bgcolor="white",
        paper_bgcolor="white"
    )


    # ========================================================
    # SHOW CHART
    # ========================================================

    st.plotly_chart(
        fig_delivery,
        use_container_width=True
    )


    # ========================================================
    # DELIVERY INSIGHT
    # ========================================================

    st.info("""
    📌 Insight:
    
    States with higher delivery days and delay rates may require
    logistics optimization and improved shipping efficiency.
    """)

# TAB 4: Customer Segmentation
# ============================================================

# TAB 4: Customer Segmentation
# ============================================================

with tab4:

    st.subheader("Customer Segmentation Summary")

    segment_summary = rfm_summary.groupby("customer_segment").agg(
        customers=("customer_unique_id", "count"),
        total_revenue=("monetary", "sum"),
        avg_monetary=("monetary", "mean"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean")
    ).reset_index()

    fig_segment_revenue = px.bar(
        segment_summary,
        x="customer_segment",
        y="total_revenue",
        title="Revenue by Customer Segment"
    )

    st.plotly_chart(fig_segment_revenue, use_container_width=True)

    fig_segment_count = px.bar(
        segment_summary,
        x="customer_segment",
        y="customers",
        title="Number of Customers by Segment"
    )

    st.plotly_chart(fig_segment_count, use_container_width=True)

    st.dataframe(segment_summary)

# TAB 5: Business Recommendations
# ============================================================

with tab5:

    st.subheader("Business Recommendations")

    st.markdown("""
    ### 1. Improve Delivery Performance
    Focus on states with high delivery days and high delay rates.

    ### 2. Prioritize Top Categories
    Promote categories that generate the highest revenue and strong review scores.

    ### 3. Focus on High-Value Customers
    Champions and Loyal Customers should receive loyalty campaigns.

    ### 4. Reactivate At-Risk Customers
    At Risk customers can be targeted with personalized offers.

    ### 5. Monitor Review Scores
    Track low review scores together with delivery delay and product category.
    """)

# ============================================================
# 8. Filtered Data Preview
# ============================================================

with st.expander("View Filtered Data"):
    st.dataframe(filtered_df.head(200))


# ============================================================
# 9. Footer
# ============================================================

st.write("---")
st.write("RetailIQ Project | SQLite3 + Python + Tableau + Streamlit")





st.markdown(
    """
    <div style="
        text-align: center;
        font-size: 28px;
        font-weight: 800;
        color: #1F4E79;
        margin-top: 20px;
        letter-spacing: 1px:
    ">
         By Pollob Sikder🙏
    </div>
    """,
    unsafe_allow_html=True
)