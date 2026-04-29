import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# ==============================================================================
# CONFIG & CUSTOM CSS (MINIMALIST & PROFESSIONAL)
# ==============================================================================
st.set_page_config(page_title="Olist E-Commerce Dashboard", page_icon="🛒", layout="wide")

st.markdown("""
<style>
    .main { background-color: #F8F9FA; }
    .stMetric { background-color: #FFFFFF; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 5px solid #1A237E;}
    h1, h2, h3 { color: #1A237E; font-family: 'sans-serif'; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# LOAD DATA 
# ==============================================================================
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "main_data.csv")
    df = pd.read_csv(file_path)
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    return df

all_df = load_data()

# ==============================================================================
# SIDEBAR - KHUSUS FILTER
# ==============================================================================
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🛒 Olist Store</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Business Intelligence Dashboard</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.header("🔍 Filter Data")
    
    # 1. Filter Tanggal
    min_date = all_df["order_purchase_timestamp"].min().date()
    max_date = all_df["order_purchase_timestamp"].max().date()
    date_range = st.date_input('📅 Rentang Waktu', min_value=min_date, max_value=max_date, value=[min_date, max_date])

    # 2. Filter Negara Bagian
    states = sorted(all_df["customer_state"].dropna().unique())
    selected_states = st.multiselect("📍 Negara Bagian (State)", options=states, default=[])

    # 3. Filter Tipe Pembayaran
    payment_types = sorted(all_df["payment_type"].dropna().unique())
    selected_payments = st.multiselect("💳 Tipe Pembayaran", options=payment_types, default=payment_types)

# ==============================================================================
# APLIKASI FILTER (LOGIKA ANTI-BUG)
# ==============================================================================
main_df = all_df.copy()

# A. Terapkan Filter Tanggal
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

main_df = main_df[(main_df["order_purchase_timestamp"].dt.date >= start_date) & 
                  (main_df["order_purchase_timestamp"].dt.date <= end_date)]

# B. Terapkan Filter Negara Bagian (Jika kosong, tampilkan SEMUA)
if selected_states:
    main_df = main_df[main_df["customer_state"].isin(selected_states)]

# C. Terapkan Filter Tipe Pembayaran (Jika kosong, tampilkan SEMUA)
if selected_payments:
    main_df = main_df[main_df["payment_type"].isin(selected_payments)]

# ==============================================================================
# HEADER UTAMA & KPI METRICS
# ==============================================================================
st.title("📊 E-Commerce Performance Dashboard")
st.markdown(f"**Periode Analisis:** {start_date} s/d {end_date}")

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("📦 Total Pesanan", f"{main_df['order_id'].nunique():,}")
with col2: st.metric("💵 Total Pendapatan", f"R$ {main_df['payment_value'].sum():,.0f}")
with col3: st.metric("👥 Total Pelanggan", f"{main_df['customer_unique_id'].nunique():,}")
with col4: st.metric("💳 Avg. Transaksi", f"R$ {main_df['payment_value'].mean() if not main_df.empty else 0:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# TABS NAVIGASI
# ==============================================================================
tab1, tab2, tab3 = st.tabs(["📈 Q1: Tren Pendapatan", "🗺️ Q2: Demografi Geografis", "👥 Q3: Analisis RFM"])

# Helper Text untuk Data Kosong
def show_empty_data_warning():
    st.warning("⚠️ **Tidak ada transaksi pada rentang waktu atau kombinasi filter yang Anda pilih.**")
    st.info("💡 **Solusi:** Silakan perlebar rentang kalender Anda di panel samping (pastikan berada di antara tahun 2016 - 2018).")

# ------------------------------------------------------------------------------
# TAB 1: TREN PENDAPATAN
# ------------------------------------------------------------------------------
with tab1:
    if not main_df.empty:
        rev_2017 = all_df[all_df['order_purchase_timestamp'].dt.year == 2017]['payment_value'].sum()
        rev_2018 = all_df[all_df['order_purchase_timestamp'].dt.year == 2018]['payment_value'].sum()
        growth = ((rev_2018 - rev_2017) / rev_2017) * 100 if rev_2017 > 0 else 0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Pendapatan 2017", f"R$ {rev_2017:,.0f}")
        c2.metric("Pendapatan 2018", f"R$ {rev_2018:,.0f}")
        c3.metric("Pertumbuhan Tahunan", f"{growth:.2f}%", delta=f"+ R$ {rev_2018 - rev_2017:,.0f}")
        
        st.markdown("---")
        
        col_chart, col_insight = st.columns([7, 3])
        with col_chart:
            st.subheader("Tren Pendapatan Bulanan")
            monthly_df = main_df.resample(rule='M', on='order_purchase_timestamp').agg({"payment_value": "sum"}).reset_index()
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(monthly_df["order_purchase_timestamp"], monthly_df["payment_value"], marker='o', linewidth=2.5, color="#1A237E")
            plt.grid(axis='y', linestyle='--', alpha=0.3)
            sns.despine()
            st.pyplot(fig)
            
        with col_insight:
            st.subheader("💡 Analisis Puncak & Rekomendasi")
            st.info("""
            **Peak Season Historis:**
            Berdasarkan data, puncak transaksi tertinggi terjadi secara masif pada **November 2017** (bertepatan dengan momentum Black Friday).
            """)
            st.success("""
            **Action Item:**
            Tim Marketing disarankan mengalokasikan anggaran promosi maksimum pada Kuartal 4 (Q4), khususnya persiapan di bulan Oktober untuk menyambut lonjakan bulan November.
            """)
    else:
        show_empty_data_warning()

# ------------------------------------------------------------------------------
# TAB 2: DEMOGRAFI GEOGRAFIS
# ------------------------------------------------------------------------------
with tab2:
    if not main_df.empty:
        state_counts = main_df.groupby("customer_state").customer_unique_id.nunique().sort_values(ascending=False).head(10).reset_index()
        top_5_pct = (state_counts['customer_unique_id'].head(5).sum() / main_df['customer_unique_id'].nunique()) * 100
        
        st.subheader("Distribusi Geografis Pelanggan (Top 10)")
        c1, c2 = st.columns([6, 4])
        
        with c1:
            fig, ax = plt.subplots(figsize=(9, 5))
            colors = ["#1A237E" if i < 5 else "#B0BEC5" for i in range(len(state_counts))]
            sns.barplot(x="customer_unique_id", y="customer_state", data=state_counts, palette=colors, hue="customer_state", legend=False, ax=ax)
            ax.set_xlabel("Jumlah Pelanggan")
            ax.set_ylabel("Negara Bagian (State)")
            sns.despine()
            st.pyplot(fig)
            
        with c2:
            st.write("**Persentase Pangsa Pasar (Top 5)**")
            fig, ax = plt.subplots(figsize=(6, 4))
            top_5_data = state_counts.head(5)
            pie_colors = ['#1A237E', '#3949AB', '#5C6BC0', '#7986CB', '#9FA8DA']
            ax.pie(top_5_data['customer_unique_id'], labels=top_5_data['customer_state'], autopct='%1.1f%%', startangle=90, colors=pie_colors)
            st.pyplot(fig)
            
            st.success(f"""
            **Kesimpulan & Rekomendasi Logistik:**
            Kelima negara bagian teratas menguasai **{top_5_pct:.1f}%** total basis pelanggan. Tim logistik diprioritaskan untuk membangun **Main Hub di SP (Sao Paulo)** untuk memangkas *freight value* secara signifikan.
            """)
    else:
        show_empty_data_warning()

# ------------------------------------------------------------------------------
# TAB 3: ANALISIS RFM
# ------------------------------------------------------------------------------
with tab3:
    if not main_df.empty:
        recent_date = main_df['order_purchase_timestamp'].max()
        rfm_df = main_df.groupby('customer_unique_id').agg({
            'order_purchase_timestamp': 'max',
            'order_id': 'nunique',
            'payment_value': 'sum'
        }).reset_index()
        
        rfm_df.columns = ['id', 'max_order_timestamp', 'frequency', 'monetary']
        rfm_df['recency'] = (recent_date - rfm_df['max_order_timestamp']).dt.days
        
        rfm_df['Segment'] = 'Biasa'
        rfm_df.loc[(rfm_df['recency'] > 180) & (rfm_df['frequency'] > 1), 'Segment'] = 'At Risk'
        rfm_df.loc[(rfm_df['recency'] <= 180) & (rfm_df['frequency'] > 1), 'Segment'] = 'Loyal'
        rfm_df.loc[(rfm_df['frequency'] == 1), 'Segment'] = 'One-time Shopper'
        
        at_risk_df = rfm_df[rfm_df['Segment'] == 'At Risk']
        
        c1, c2, c3 = st.columns(3)
        c1.metric("🚨 Pelanggan At-Risk", f"{at_risk_df.shape[0]:,}", delta="High Priority", delta_color="inverse")
        c2.metric("✨ Pelanggan Loyal", f"{rfm_df[rfm_df['Segment'] == 'Loyal'].shape[0]:,}")
        c3.metric("💰 Total Nilai At-Risk", f"R$ {at_risk_df['monetary'].sum():,.0f}")
        
        st.markdown("---")
        col_chart, col_info = st.columns([6, 4])
        
        with col_chart:
            st.write("**Distribusi Segmen Pelanggan**")
            fig, ax = plt.subplots(figsize=(8, 4))
            seg_order = ['At Risk', 'Loyal', 'One-time Shopper']
            sns.countplot(y='Segment', data=rfm_df, order=seg_order, palette=["#D32F2F", "#1A237E", "#B0BEC5"], hue='Segment', legend=False, ax=ax)
            ax.set_ylabel("")
            sns.despine()
            st.pyplot(fig)
            
        with col_info:
            st.subheader("💡 Rekomendasi Tim CRM")
            st.success(f"""
            Terdapat potensi perputaran uang sebesar **R$ {at_risk_df['monetary'].sum():,.0f}** dari segmen At-Risk yang terancam *churn*. 
            
            Segera eksekusi **Win-Back Campaign** (Email Marketing) yang menawarkan voucher eksklusif berbatas waktu kepada pelanggan prioritas ini.
            """)
            
            st.write("📋 **Top 5 Prioritas Dihubungi (Berdasarkan Monetary)**")
            st.dataframe(at_risk_df.sort_values(by='monetary', ascending=False).head(5)[['id', 'recency', 'monetary']], hide_index=True)
    else:
        show_empty_data_warning()