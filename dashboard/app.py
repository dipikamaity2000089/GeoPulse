
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="GeoPulse | Retail Intelligence",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

base_path = Path(__file__).resolve().parent.parent
data_path = base_path / "data" / "hourly_footfall.csv"

st.markdown("""
<style>
.stApp {
    background: #F3F6FA;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #102A43, #164E63);
}
[data-testid="stSidebar"] * {
    color: white !important;
}
.main-title {
    color: #102A43;
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -1px;
}
.subtitle {
    color: #627D98;
    font-size: 15px;
    margin-bottom: 20px;
}
.section-title {
    color: #102A43;
    font-size: 22px;
    font-weight: 750;
    margin-top: 12px;
    margin-bottom: 12px;
}
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #D9E2EC;
    padding: 19px;
    border-radius: 14px;
    box-shadow: 0 4px 14px rgba(16,42,67,0.06);
}
[data-testid="stMetricLabel"] {
    color: #627D98;
    font-size: 14px;
}
[data-testid="stMetricValue"] {
    color: #102A43;
    font-weight: 800;
}
div[data-testid="stPlotlyChart"] {
    background: white;
    border: 1px solid #D9E2EC;
    border-radius: 14px;
    padding: 12px;
}
.stButton button, .stDownloadButton button {
    background: #087E8B;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
}
hr {
    border-color: #D9E2EC;
}
</style>
""", unsafe_allow_html=True)

if not data_path.exists():
    st.error(f"Dataset not found: {data_path}")
    st.stop()

df = pd.read_csv(data_path)
st.write("DATASET SHAPE:", df.shape)
st.write("DATASET PREVIEW:", df.head(10))
st.write("MAX GPS PINGS:", df["Total_GPS_Pings"].max())
st.write("DATA TYPES:", df.dtypes)
df.columns = df.columns.str.strip()

required_columns = [
    "Nearest_Store_ID",
    "Hour",
    "Total_GPS_Pings",
    "Unique_Visitors"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    st.error(f"Missing columns: {missing_columns}")
    st.stop()

df["Nearest_Store_ID"] = df["Nearest_Store_ID"].astype(str).str.strip()

for col in ["Hour", "Total_GPS_Pings", "Unique_Visitors"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=required_columns).copy()

if df.empty:
    st.error("No valid records found in the dataset.")
    st.stop()

df["Hour"] = df["Hour"].astype(int)

st.sidebar.markdown("## 📍 GeoPulse")
st.sidebar.caption("RETAIL MOBILITY INTELLIGENCE")
st.sidebar.divider()

st.sidebar.markdown("### Dashboard Filters")

stores = sorted(df["Nearest_Store_ID"].unique())

selected_store = st.sidebar.selectbox(
    "Select Store",
    ["All Stores"] + stores
)

min_hour = int(df["Hour"].min())
max_hour = int(df["Hour"].max())

selected_hours = st.sidebar.slider(
    "Select Operating Hours",
    min_value=min_hour,
    max_value=max_hour,
    value=(min_hour, max_hour)
)

st.sidebar.divider()
st.sidebar.markdown("### About this dashboard")
st.sidebar.caption("Synthetic GPS footfall dataset")
st.sidebar.caption("Retail catchment and visitor analysis")
st.sidebar.caption("GeoPulse Analytics | 2026")

filtered_df = df[
    df["Hour"].between(selected_hours[0], selected_hours[1])
].copy()

if selected_store != "All Stores":
    filtered_df = filtered_df[
        filtered_df["Nearest_Store_ID"] == selected_store
    ].copy()

if filtered_df.empty:
    st.warning("No records found for the selected filters.")
    st.stop()

st.markdown(
    '<div class="main-title">GeoPulse Analytics</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Hyper-local Retail Mobility & Footfall Intelligence</div>',
    unsafe_allow_html=True
)

st.divider()

st.markdown(
    '<div class="section-title">Business Overview</div>',
    unsafe_allow_html=True
)

total_stores = filtered_df["Nearest_Store_ID"].nunique()
total_pings = int(filtered_df["Total_GPS_Pings"].sum())
hourly_visitor_counts = int(filtered_df["Unique_Visitors"].sum())

peak_hour = int(
    filtered_df.groupby("Hour")["Total_GPS_Pings"].sum().idxmax()
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("🏬 Stores Analyzed", f"{total_stores}")
c2.metric("📍 Total GPS Pings", f"{total_pings:,}")
c3.metric("👥 Hourly Visitor Counts", f"{hourly_visitor_counts:,}")
c4.metric("⏰ Peak Hour", f"{peak_hour}:00")

st.divider()

st.markdown(
    '<div class="section-title">Footfall Performance</div>',
    unsafe_allow_html=True
)

hourly_data = (
    filtered_df.groupby("Hour", as_index=False)
    .agg(Total_GPS_Pings=("Total_GPS_Pings", "sum"))
    .sort_values("Hour")
)

store_data = (
    filtered_df.groupby("Nearest_Store_ID", as_index=False)
    .agg(Total_GPS_Pings=("Total_GPS_Pings", "sum"))
    .sort_values("Total_GPS_Pings", ascending=False)
)

left, right = st.columns([1.5, 1])

with left:
    st.markdown("#### 📈 Hourly Footfall Trend")

    fig1 = px.line(
        hourly_data,
        x="Hour",
        y="Total_GPS_Pings",
        markers=True,
        text="Total_GPS_Pings"
    )

    fig1.update_traces(
        line=dict(color="#087E8B", width=3),
        marker=dict(size=8),
        textposition="top center",
        hovertemplate="Hour: %{x}:00<br>GPS Pings: %{y:,}<extra></extra>"
    )

    fig1.update_layout(
        template="plotly_white",
        height=390,
        margin=dict(l=15, r=15, t=25, b=15),
        xaxis_title="Hour of Day",
        yaxis_title="Total GPS Pings",
        xaxis=dict(
            tickmode="linear",
            dtick=1,
            showgrid=False
        ),
        yaxis=dict(
            rangemode="tozero",
            tickformat=",",
            gridcolor="#E8EEF3"
        ),
        hovermode="x unified"
    )

    st.plotly_chart(fig1, use_container_width=True)

with right:
    st.markdown("#### 🏬 Store-wise Comparison")

    fig2 = px.bar(
        store_data,
        x="Nearest_Store_ID",
        y="Total_GPS_Pings",
        text="Total_GPS_Pings",
        color="Nearest_Store_ID",
        color_discrete_sequence=[
            "#087E8B", "#164E63", "#4C8C91", "#82B4B7"
        ]
    )

    fig2.update_traces(
        texttemplate="%{y:,}",
        textposition="outside",
        hovertemplate="Store: %{x}<br>GPS Pings: %{y:,}<extra></extra>"
    )

    fig2.update_layout(
        template="plotly_white",
        height=390,
        margin=dict(l=15, r=15, t=25, b=15),
        xaxis_title="Store ID",
        yaxis_title="Total GPS Pings",
        yaxis=dict(
            rangemode="tozero",
            tickformat=",",
            gridcolor="#E8EEF3"
        ),
        showlegend=False
    )

    st.plotly_chart(fig2, use_container_width=True)

st.divider()

st.markdown(
    '<div class="section-title">Visitor Distribution</div>',
    unsafe_allow_html=True
)

visitor_data = (
    filtered_df.groupby("Nearest_Store_ID", as_index=False)
    .agg(Unique_Visitors=("Unique_Visitors", "sum"))
)

fig3 = px.pie(
    visitor_data,
    names="Nearest_Store_ID",
    values="Unique_Visitors",
    hole=0.58,
    color_discrete_sequence=[
        "#087E8B", "#164E63", "#4C8C91", "#82B4B7"
    ]
)

fig3.update_layout(
    template="plotly_white",
    height=380,
    legend_title="Store",
    margin=dict(l=15, r=15, t=20, b=15)
)

st.plotly_chart(fig3, use_container_width=True)

st.divider()

st.markdown(
    '<div class="section-title">Detailed Footfall Records</div>',
    unsafe_allow_html=True
)

tab1, tab2 = st.tabs(["📊 Footfall Data", "🔍 Data Summary"])

with tab1:
    st.dataframe(
        filtered_df.sort_values(
            ["Nearest_Store_ID", "Hour"]
        ),
        use_container_width=True,
        hide_index=True
    )

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Download Footfall Report",
        data=csv_data,
        file_name="geopulse_footfall_report.csv",
        mime="text/csv"
    )

with tab2:
    st.write("Hourly footfall summary")

    st.dataframe(
        hourly_data,
        use_container_width=True,
        hide_index=True
    )

    st.write("Store-wise visitor summary")

    st.dataframe(
        visitor_data,
        use_container_width=True,
        hide_index=True
    )

st.divider()

st.caption(
    "GeoPulse | Retail Strategy & Geospatial Analytics | "
    "Synthetic demonstration data"
)
