import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os  

# Set page configuration
st.set_page_config(page_title="Olist E-Commerce Dashboard", layout="wide")

# Load Data
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "main_data.csv")
    
    df = pd.read_csv(file_path)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

all_df = load_data()

all_df = load_data()

# ==============================================================================
# SIDEBAR: FILTER TANGGAL
# ==============================================================================
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png") # Logo Dicoding
    st.title("Filter Rentang Waktu")
    
    # Mengambil range tanggal minimum dan maksimum (jadikan date() agar formatnya bersih)
    min_date = all_df["order_purchase_timestamp"].min().date()
    max_date = all_df["order_purchase_timestamp"].max().date()

    # Menerima input dari date_input
    date_range = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Cek apakah user sudah memilih 2 tanggal
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    st.error("Silakan pilih rentang waktu (tanggal awal dan tanggal akhir) pada sidebar terlebih dahulu.")
    st.stop() # Menghentikan eksekusi kode di bawahnya sementara sampai user selesai memilih

# Filter data berdasarkan rentang tanggal
main_df = all_df[(all_df["order_purchase_timestamp"].dt.date >= start_date) & 
                 (all_df["order_purchase_timestamp"].dt.date <= end_date)]

# ==============================================================================
# HEADER & METRICS
# ==============================================================================
st.title("📊 Olist E-Commerce Business Performance Dashboard")

col1, col2, col3 = st.columns(3)
with col1:
    total_revenue = main_df.payment_value.sum()
    st.metric("Total Revenue", value=f"R$ {total_revenue:,.0f}")

with col2:
    total_orders = main_df.order_id.nunique()
    st.metric("Total Orders", value=f"{total_orders:,}")

with col3:
    total_customers = main_df.customer_unique_id.nunique()
    st.metric("Total Unique Customers", value=f"{total_customers:,}")

st.markdown("---")

# ==============================================================================
# VISUALISASI 1: TREN PENDAPATAN
# ==============================================================================
st.subheader("📈 Tren Pendapatan Bulanan")

monthly_rev_df = main_df.resample(rule='M', on='order_purchase_timestamp').agg({
    "payment_value": "sum"
}).reset_index()
monthly_rev_df.rename(columns={"payment_value": "revenue"}, inplace=True)
monthly_rev_df['month_year'] = monthly_rev_df['order_purchase_timestamp'].dt.strftime('%b %Y')

fig, ax = plt.subplots(figsize=(16, 6))
ax.plot(monthly_rev_df['month_year'], monthly_rev_df['revenue'], marker='o', linewidth=3, color="#1A237E")
plt.xticks(rotation=45)
ax.set_title("Total Revenue per Bulan (BRL)", loc="center", fontsize=18, fontweight='bold')
plt.grid(axis='y', linestyle='--', alpha=0.4)
sns.despine()
st.pyplot(fig)

with st.expander("💡 Lihat Insight Tren Pendapatan"):
    st.write("""
    - Terlihat tren pertumbuhan pendapatan yang positif secara keseluruhan.
    - Lonjakan pendapatan paling tajam secara historis terjadi pada bulan **November**, yang menandakan tingginya aktivitas belanja selama periode kampanye akhir tahun (Black Friday).
    """)

# ==============================================================================
# VISUALISASI 2: DEMOGRAFI PELANGGAN & RFM
# ==============================================================================
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🌍 Persebaran Pelanggan (Top 5 State)")
    state_df = main_df.groupby("customer_state").customer_unique_id.nunique().reset_index()
    state_df = state_df.sort_values("customer_unique_id", ascending=False).head(5)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x="customer_unique_id", y="customer_state", data=state_df, palette="Blues_d", ax=ax)
    ax.set_title("5 Negara Bagian dengan Pelanggan Terbanyak", fontsize=15, fontweight='bold')
    sns.despine()
    st.pyplot(fig)
    
    with st.expander("💡 Lihat Insight Geospasial"):
        st.write("""
        - Wilayah **Sao Paulo (SP)** mendominasi basis pelanggan dengan selisih yang sangat signifikan.
        - Konsentrasi pelanggan di wilayah Tenggara Brazil menunjukkan perlunya memprioritaskan infrastruktur logistik di area tersebut.
        """)

with col_right:
    st.subheader("⚠️ Segmentasi Pelanggan At-Risk")
    
    # Perbaikan RFM Sederhana untuk Dashboard
    recent_date = main_df['order_purchase_timestamp'].max()
    
    # Grouping mencari tanggal max dan jumlah transaksi
    rfm_df = main_df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': 'max',
        'order_id': 'nunique'
    }).reset_index()
    
    # Ganti nama kolom
    rfm_df.columns = ['id', 'max_order_timestamp', 'frequency']
    
    # Hitung selisih hari (recency) secara aman menggunakan dt.days
    rfm_df['recency'] = (recent_date - rfm_df['max_order_timestamp']).dt.days
    
    # Logika perhitungan segmentasi
    at_risk_count = rfm_df[(rfm_df['recency'] > 180) & (rfm_df['frequency'] > 1)].shape[0]
    loyal_count = rfm_df[(rfm_df['frequency'] > 1)].shape[0] - at_risk_count
    one_time_count = rfm_df[(rfm_df['frequency'] == 1)].shape[0]

    # Menyiapkan data untuk chart
    segment_data = pd.DataFrame({
        'Segment': ['At-Risk', 'Loyal', 'One-time Shopper'],
        'Count': [at_risk_count, loyal_count, one_time_count]
    })

    # Membuat Chart
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x="Count", y="Segment", data=segment_data, palette=["#D32F2F", "#1976D2", "#B0BEC5"], ax=ax)
    ax.set_title("Distribusi Segmen Pelanggan", fontsize=15, fontweight='bold')
    sns.despine()
    st.pyplot(fig)

    with st.expander("💡 Lihat Insight RFM"):
        st.write(f"""
        - Terdapat **{at_risk_count:,} pelanggan At-Risk** yang perlu segera diberikan penawaran khusus (voucher/diskon).
        - Mayoritas pelanggan masih berupa 'One-time Shoppers', menunjukkan tantangan besar dalam meningkatkan retensi.
        """)

st.caption('Copyright © 2026 | Proyek Analisis Data Olist E-Commerce')