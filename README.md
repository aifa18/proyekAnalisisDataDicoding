# Olist E-Commerce Analytics Dashboard ✨

## Deskripsi
Dashboard ini merupakan aplikasi visualisasi data interaktif yang dibangun menggunakan Streamlit. Aplikasi ini menyajikan analisis mendalam terhadap performa bisnis Olist Store (E-Commerce Brazil), yang mencakup tren pendapatan tahunan, sebaran geografis pelanggan untuk optimasi logistik, serta segmentasi pelanggan menggunakan analisis RFM (Recency, Frequency, Monetary) guna mendukung strategi retensi pelanggan.

## Struktur Proyek
- `dashboard/`: Direktori utama untuk aplikasi dashboard.
    - `dashboard.py`: File kode sumber utama aplikasi Streamlit.
    - `main_data.csv`: Dataset yang telah melalui proses pembersihan (Cleaned Data).
- `data/`: Direktori yang berisi berkas dataset mentah (.csv).
- `notebook.ipynb`: Dokumentasi lengkap proses Data Wrangling, Exploratory Data Analysis (EDA), hingga visualisasi data.
- `README.md`: Panduan penggunaan dan informasi proyek.
- `requirements.txt`: Daftar pustaka (library) Python yang diperlukan untuk menjalankan proyek.
- `url.txt`: Berisi tautan (URL) dashboard jika sudah dideploy ke Streamlit Cloud.

## Setup Environment - Anaconda
```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```bash
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run Streamlit
Untuk menjalankan dashboard secara lokal, pastikan Anda berada di root folder proyek, lalu jalankan perintah berikut:
```bash
streamlit run dashboard/dashboard.py
```

---
**Azmi Naifah Iftinah** 