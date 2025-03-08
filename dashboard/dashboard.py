import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🌿 Dashboard Kualitas Udara 🌍</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #808080;'>Pantau kualitas udara dengan data untuk lingkungan yang lebih sehat!</p>", unsafe_allow_html=True)
st.markdown("---")


df_combined = pd.read_csv("https://drive.google.com/uc?id=1j3fQGRt9WVzqhAGse25ZXpa83pR3gFKw")



def plot_air_quality(df_combined, station=None):
    
    df_combined['date'] = pd.to_datetime(df_combined['date'])

    if station:
        df_filtered = df_combined[df_combined['station'] == station]
    else:
        df_filtered = df_combined


    monthly_avg = df_filtered.groupby(pd.Grouper(key='date', freq='M'))[['PM2.5', 'PM10', 'NO2', 'SO2', 'O3', 'CO']].mean().reset_index()

    fig, axes = plt.subplots(3, 1, figsize=(12, 15))

    axes[0].plot(monthly_avg['date'], monthly_avg['PM2.5'], label='PM2.5', marker='o')
    axes[0].plot(monthly_avg['date'], monthly_avg['PM10'], label='PM10', marker='s')
    axes[0].set_ylabel('Konsentrasi Partikulat')
    axes[0].legend()
    axes[0].grid(True, linestyle='--', alpha=0.5)


    axes[1].plot(monthly_avg['date'], monthly_avg['NO2'], label='NO2', marker='s')
    axes[1].plot(monthly_avg['date'], monthly_avg['SO2'], label='SO2', marker='x')
    axes[1].plot(monthly_avg['date'], monthly_avg['O3'], label='O3', marker='^')
    axes[1].set_ylabel('Konsentrasi Gas')
    axes[1].legend()
    axes[1].grid(True, linestyle='--', alpha=0.5)


    axes[2].plot(monthly_avg['date'], monthly_avg['CO'], label='CO', marker='d', color='purple')
    axes[2].set_xlabel('Waktu')
    axes[2].set_ylabel('Konsentrasi CO')
    axes[2].legend()
    axes[2].grid(True, linestyle='--', alpha=0.5)

    plt.xticks(rotation=45)
    st.pyplot(fig)


st.markdown("<h3 style='text-align: center; color: #4CAF50;'>Pola Perubahan Kualitas Udara 🪟</h1>", unsafe_allow_html=True)


stations = df_combined['station'].unique()  
selected_station = st.selectbox("Pilih Stasiun", ["Semua Stasiun"] + list(stations))


st.markdown("---")
if selected_station == "Semua Stasiun":
    plot_air_quality(df_combined)
else:
    plot_air_quality(df_combined, station=selected_station)



def plot_pollution_per_station(df_combined, start_year, end_year):
    
    df_combined['date'] = pd.to_datetime(df_combined['date'])

    df_filtered = df_combined[(df_combined['date'].dt.year >= start_year) & (df_combined['date'].dt.year <= end_year)]
    
    station_avg = df_filtered.groupby('station')[['PM2.5', 'PM10', 'NO2', 'SO2', 'O3', 'CO']].sum()

    station_avg['total_pollution'] = station_avg.sum(axis=1)

    worst_station = station_avg['total_pollution'].idxmax()
    best_station = station_avg['total_pollution'].idxmin()

    plt.figure(figsize=(12, 6))

    colors = ['red' if station == worst_station else 'green' if station == best_station else 'skyblue' for station in station_avg.index]

    plt.bar(station_avg.index, station_avg['total_pollution'], color=colors)

    plt.title(f'Total Polusi per Stasiun ({start_year}-{end_year})')
    plt.xlabel('Stasiun')
    plt.ylabel('Total Polusi (µg/m³)')
    plt.xticks(rotation=45)


    for i, v in enumerate(station_avg['total_pollution']):
        plt.text(i, v + 20, f'{v:.2f}', ha='center', va='bottom', fontsize=9)

    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()


    st.pyplot(plt)

st.markdown("---")

st.markdown("<h3 style='text-align: center; color: #4CAF50;'>Station dengan Kualitas Udara Tertinggi dan Terendah</h1>", unsafe_allow_html=True)


start_year, end_year = st.slider(
    "Pilih Rentang Tahun",
    min_value=2013, max_value=2017,
    value=(2013, 2017),
    step=1
)


st.markdown("---")
plot_pollution_per_station(df_combined, start_year, end_year)



def plot_contribution_per_station(df_combined, station_name):
    pollutants = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
    
    
    df_station = df_combined[df_combined['station'] == station_name]

    
    total_pollution = df_station[pollutants].sum()

    
    total_pollution_all_stations = df_combined[pollutants].sum()
    contribution = total_pollution / total_pollution_all_stations.sum()

    
    contribution_sorted = contribution.sort_values(ascending=False)

    
    fig, ax = plt.subplots(figsize=(8, 6))

    
    ax.bar(contribution_sorted.index, contribution_sorted.values, color='skyblue')

    
    ax.set_title(f'Kontribusi Polutan - {station_name}')
    ax.set_xlabel('Polutan')
    ax.set_ylabel('Kontribusi Terhadap Total Polusi')
    ax.grid(True, linestyle='--', alpha=0.5)

    
    for j, value in enumerate(contribution_sorted.values):
        ax.text(j, value + 0.01, f'{value:.2f}', ha='center', va='bottom', fontsize=9, color='black')

    
    st.pyplot(fig)


st.markdown("---")
st.markdown("<h3 style='text-align: center; color: #4CAF50;'>Kontribusi Polutan Pertahun</h1>", unsafe_allow_html=True)


stations = df_combined['station'].unique()
station_name = st.selectbox("Pilih Stasiun", stations)


plot_contribution_per_station(df_combined, station_name)



def plot_wind_speed_vs_pm(df_combined):
    plt.figure(figsize=(8, 6))
    plt.scatter(df_combined['WSPM'], df_combined['PM2.5'])
    plt.title('Kecepatan Angin vs PM2.5')
    plt.xlabel('Kecepatan Angin (m/s)')
    plt.ylabel('PM2.5 (µg/m³)')
    plt.grid(True)
    st.pyplot(plt)


def plot_correlation_heatmap(df_combined):
    
    numeric_cols = df_combined[['WSPM', 'wd', 'PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']].select_dtypes(include='number')

    
    numeric_cols = numeric_cols.dropna()

    
    correlation_matrix = numeric_cols.corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Korelasi antara Kecepatan Angin, Arah Angin, dan Polutan')
    st.pyplot(plt)


def plot_boxplot_by_wind_direction(df_combined):
    plt.figure(figsize=(12, 8))
    sns.boxplot(x='wd', y='PM2.5', data=df_combined)
    plt.title('Distribusi PM2.5 Berdasarkan Arah Angin')
    plt.xlabel('Arah Angin')
    plt.ylabel('PM2.5 (µg/m³)')
    plt.xticks(rotation=45)
    st.pyplot(plt)


st.markdown("---")
st.markdown("<h3 style='text-align: center; color: #4CAF50;'>Pengaruh Pola Arah dan Kecepatan Angin</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Kecepatan Angin vs PM2.5", "Korelasi Polutan", "Distribusi PM2.5 Berdasarkan Arah Angin"])


with tab1:
    plot_wind_speed_vs_pm(df_combined)

with tab2:
    plot_correlation_heatmap(df_combined)

with tab3:
    plot_boxplot_by_wind_direction(df_combined)



# Fungsi untuk mengklasifikasikan kualitas udara
def classify_air_quality(row):
    if row['PM2.5'] < 50 and row['PM10'] < 50 and row['CO'] < 100 and row['NO2'] < 50:
        return 'Baik'
    elif row['PM2.5'] < 100 and row['PM10'] < 100 and row['CO'] < 150 and row['NO2'] < 100:
        return 'Sedang'
    else:
        return 'Buruk'

# Fungsi untuk menampilkan distribusi kualitas udara
def plot_air_quality_distribution(df_combined, station=None):
    # Filter berdasarkan station jika dipilih
    if station:
        df_combined = df_combined[df_combined['station'] == station]

    # Menambahkan kolom Kualitas_Udara berdasarkan fungsi classify_air_quality
    df_combined['Kualitas_Udara'] = df_combined.apply(classify_air_quality, axis=1)

    # Menampilkan distribusi kualitas udara
    st.write(f"Distribusi Kualitas Udara untuk Stasiun: {station if station else 'Semua Stasiun'}")
    st.write(df_combined['Kualitas_Udara'].value_counts())

    # Visualisasi distribusi kualitas udara
    plt.figure(figsize=(8, 6))
    df_combined['Kualitas_Udara'].value_counts().plot(kind='bar', color=['green', 'yellow', 'red'])
    plt.title('Distribusi Kualitas Udara')
    plt.xlabel('Kualitas Udara')
    plt.ylabel('Jumlah')
    plt.xticks(rotation=0)
    st.pyplot(plt)

# UI Streamlit
st.title("Dashboard Kualitas Udara 🌿")

# Menampilkan selectbox untuk memilih station
station_list = df_combined['station'].unique().tolist()

# Selectbox untuk memilih stasiun
selected_station = st.selectbox("Pilih Stasiun", station_list, key="station_selectbox")

# Menampilkan distribusi kualitas udara berdasarkan pilihan stasiun
plot_air_quality_distribution(df_combined, selected_station)



# Fungsi untuk menampilkan profil
def show_profile():
    # Menampilkan header
    st.sidebar.title("Tentang Saya")
    
    # Menambahkan foto profil (Pastikan Anda sudah punya gambar di folder yang tepat)
    st.sidebar.image("dashboard/Desain tanpa judul.png", width=150)  # Ganti dengan path gambar Anda
    
    # Menambahkan deskripsi singkat tentang diri Anda
    st.sidebar.subheader("Nama: Moh. Novil Ma'arij")
    st.sidebar.write("Saya adalah seorang pengembang dashboard dan peneliti data. "
                     "Saya memiliki latar belakang di bidang IT. "
                     "Saya membuat dashboard ini untuk memvisualisasikan kualitas udara dan memberikan insight "
                     "terkait polusi udara di berbagai lokasi.")
    
    # Menambahkan link sosial media atau kontak
    st.sidebar.subheader("Kontak & Sosial Media")
    st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/novil-m/)")
    st.sidebar.markdown("[Instagram](https://www.instagram.com/me_ezpzy/)")
    st.sidebar.markdown("[GitHub](https://github.com/Nvl123)")

# Memanggil fungsi profil
show_profile()


