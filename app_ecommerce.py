import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="RetailIQ Dashboard", layout="wide")

st.markdown(
    """
    <h1 style='
    text-align: center;
    font-size: 55px;
    color: #1F4E79;
    '>
    RetailIQ: Advanced E-Commerce Intelligence Platform
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h3 style='
    text-align: center;
    font-size: 28px;
    color: #FF4B4B;
    background: linear-gradient(90deg, #4F8BF9, #FF4B4B);
    padding: 15px;
    border-radius: 12px;
    color: white;
    font-weight: bold;
    '>
    This dashboard analyzes e-commerce sales, customers, delivery performance, reviews, and product categories using SQL and Python.
    </h3>
    """,
    unsafe_allow_html=True
)

conn = sqlite3.connect("e_commerce_olist.db")

df = pd.read_sql("SELECT * FROM Complete_data", conn)

# Fix missing values
df["customer_state"] = df["customer_state"].fillna("Unknown")

df["product_category_name_english"] = (
    df["product_category_name_english"]
    .fillna("Unknown")
)

states = st.sidebar.multiselect(
    "Select Customer State",
    options=sorted(df["customer_state"].dropna().unique()),
    default=sorted(df["customer_state"].dropna().unique())[:5]
)

categories = st.sidebar.multiselect(
    "Select Product Category",
    options=sorted(df["product_category_name_english"].dropna().unique()),
    default=sorted(df["product_category_name_english"].dropna().unique())[:5]
)

filtered_df = df[
    (df["customer_state"].isin(states)) &
    (df["product_category_name_english"].isin(categories))
]

# DEBUG CHECK
st.write("Full unique orders:", df["order_id"].nunique())

st.write("Filtered unique orders:", filtered_df["order_id"].nunique())

st.write("Rows:", filtered_df.shape)

total_revenue = filtered_df["revenue"].sum()
total_orders = filtered_df["order_id"].nunique()
total_customers = filtered_df["customer_unique_id"].nunique()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
avg_review = filtered_df["review_score"].mean()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div style="background-color:#F5F7FA;padding:20px;border-radius:12px;text-align:center;">
        <h3 style="font-size:24px;color:#1F4E79;">Total Revenue 💸</h3>
        <h1 style="font-size:38px;">${total_revenue:,.0f}</h1>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background-color:#F5F7FA;padding:20px;border-radius:12px;text-align:center;">
        <h3 style="font-size:24px;color:#1F4E79;">Total Orders 🛒</h3>
        <h1 style="font-size:38px;">{total_orders:,}</h1>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="background-color:#F5F7FA;padding:20px;border-radius:12px;text-align:center;">
        <h3 style="font-size:24px;color:#1F4E79;">Customers 🛍️</h3>
        <h1 style="font-size:38px;">{total_customers:,}</h1>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style="background-color:#F5F7FA;padding:20px;border-radius:12px;text-align:center;">
        <h3 style="font-size:24px;color:#1F4E79;">Avg Order Value 💰</h3>
        <h1 style="font-size:38px;">${avg_order_value:,.2f}</h1>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div style="background-color:#F5F7FA;padding:20px;border-radius:12px;text-align:center;">
        <h3 style="font-size:24px;color:#1F4E79;">Avg Review 🙋</h3>
        <h1 style="font-size:38px;">{avg_review:.2f}</h1>
    </div>
    """, unsafe_allow_html=True)

#Monthly Revenue trends
st.markdown(
    """
    <h2 style='
    text-align: center;
    color: white;
    background: linear-gradient(90deg, #4F8BF9, #FF4B4B);
    padding: 12px;
    border-radius: 12px;
    font-size: 35px;
    '>
    📈 Monthly Revenue Trend
    </h2>
    """,
    unsafe_allow_html=True
)

monthly = filtered_df.groupby("year_month")["revenue"].sum().reset_index()

fig = px.line(
    monthly,
    x="year_month",
    y="revenue",
    title="📊 Monthly Revenue Trend",
    markers=True,
    template="plotly_dark"
)

fig.update_traces(
    line=dict(width=4),
    marker=dict(size=8)
)

fig.update_layout(
    title_font_size=28,
    title_font_color="#00E5FF",
    plot_bgcolor="#111111",
    paper_bgcolor="#111111",
    font=dict(color="white", size=14),
    xaxis_title="Month",
    yaxis_title="Revenue",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)


#Delivery Delay vs Review Score

st.markdown(
    """
    <h2 style='
    text-align: center;
    color: white;
    background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
    padding: 12px;
    border-radius: 12px;
    font-size: 34px;
    '>
    🚚 Delivery Delay vs Review Score
    </h2>
    """,
    unsafe_allow_html=True
)

# Average review score by delay status
review_data = (
    filtered_df
    .groupby("is_delayed")["review_score"]
    .mean()
    .reset_index()
)

# Rename 0 and 1 before plotting
review_data["Delivery Status"] = review_data["is_delayed"].map({
    0: "On Time ✅",
    1: "Delayed ❌"
})

fig2 = px.bar(
    review_data,
    x="Delivery Status",
    y="review_score",
    text="review_score",
    title="⭐ Average Review Score: On-Time vs Delayed Orders",
    color="Delivery Status",
    color_discrete_map={
        "On Time ✅": "#4ECDC4",
        "Delayed ❌": "#FF6B6B"
    },
    template="plotly_dark"
)

fig2.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

fig2.update_layout(
    title_font_size=26,
    title_font_color="#00E5FF",
    plot_bgcolor="#111111",
    paper_bgcolor="#111111",
    font=dict(color="white", size=14),
    xaxis_title="Delivery Status",
    yaxis_title="Average Review Score",
    showlegend=False,
    coloraxis_showscale=False
)

st.plotly_chart(fig2, use_container_width=True)

#Revenue by Category
st.markdown(
    """
    <h2 style='
    text-align: center;
    color: white;
    background: linear-gradient(90deg, #6A11CB, #2575FC);
    padding: 12px;
    border-radius: 12px;
    font-size: 34px;
    '>
    📊 Revenue by Product Category [Top 10 Category]
    </h2>
    """,
    unsafe_allow_html=True
)

cat = filtered_df.groupby("product_category_name_english")["revenue"].sum().reset_index()
cat = cat.sort_values("revenue", ascending=False).head(10)

fig3 = px.bar(
    cat,
    x="product_category_name_english",
    y="revenue",
    title="💰 Top Product Categories by Revenue"
)

fig3.update_layout(
    title_font_size=26,
    title_font_color="#FF4B4B"
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown(
    """
    <h2 style='
    text-align: center;
    color: white;
    background: linear-gradient(90deg, #FF512F, #DD2476);
    padding: 12px;
    border-radius: 12px;
    font-size: 34px;
    '>
    📋 Data Preview
    </h2>
    """,
    unsafe_allow_html=True
)

st.dataframe(
    filtered_df.head(100),
    use_container_width=True
)

conn.close()