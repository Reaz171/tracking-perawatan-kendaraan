# 🚗 Tracking Perawatan Motor/Mobil

Aplikasi berbasis **Python + Streamlit** untuk mengelola dan melacak perawatan kendaraan (motor dan mobil) secara digital dengan fitur **QR Code**, **CRUD lengkap**, dan **laporan visual**.

## 📋 Deskripsi Proyek

Aplikasi ini dirancang untuk membantu pemilik kendaraan dalam:
- Mencatat semua data kendaraan mereka
- Melacak riwayat perawatan dan servis
- Generate QR Code untuk setiap kendaraan
- Melihat statistik dan laporan visual
- Export data ke Excel

**Mode Offline** - Semua data tersimpan lokal dalam format CSV.

---

## ✨ Fitur Utama

### 1. 📊 Dashboard
- Statistik total kendaraan dan servis
- Grafik servis per kendaraan
- Riwayat servis terbaru
- Total biaya perawatan

### 2. 🚗 Manajemen Data Kendaraan (CRUD)
- **Create**: Tambah kendaraan baru
- **Read**: Lihat daftar semua kendaraan
- **Update**: Edit data kendaraan
- **Delete**: Hapus kendaraan dan riwayat servisnya
- Validasi input data
- Pencarian kendaraan

### 3. 📱 QR Code Integration
- Generate QR Code otomatis untuk setiap kendaraan
- Scan QR untuk melihat detail kendaraan
- Download QR Code dalam format PNG
- QR disimpan di folder `/qr`

### 4. 🔧 Catatan Servis
- Tambah riwayat servis baru
- Detail lengkap (tanggal, jenis servis, biaya, bengkel, teknisi)
- Update kilometer otomatis
- Riwayat servis per kendaraan

### 5. 📈 Laporan & Grafik
- Filter data berdasarkan tanggal
- Grafik jumlah servis per kendaraan (Bar Chart)
- Grafik distribusi biaya per jenis servis (Pie Chart)
- Statistik periode
- Export laporan ke Excel

---

## 🛠️ Teknologi yang Digunakan

| Teknologi | Fungsi |
|-----------|--------|
| **Python 3.8+** | Bahasa pemrograman utama |
| **Streamlit** | Framework UI/UX web app |
| **Pandas** | Pengolahan dan manipulasi data |
| **QRCode** | Generate QR Code |
| **Plotly** | Visualisasi data interaktif |
| **OpenPyXL** | Export data ke Excel |

---

## 📁 Struktur Folder

```
tracking-perawatan-kendaraan/
│
├── app.py                  # File utama aplikasi Streamlit
├── utils.py                # File fungsi utility (16 fungsi)
├── requirements.txt        # Daftar dependencies
├── README.md               # Dokumentasi proyek
│
├── data/                   # Folder penyimpanan data CSV
│   ├── vehicles.csv        # Data kendaraan
│   └── service_log.csv     # Data riwayat servis
│
└── qr/                     # Folder QR Code
    └── QR_*.png            # File QR Code kendaraan
```

---

## 🚀 Cara Menjalankan Aplikasi

### 1. Clone Repository

```bash
git clone https://github.com/username/tracking-perawatan-kendaraan.git
cd tracking-perawatan-kendaraan
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi

```bash
streamlit run app.py
```

### 4. Buka Browser

Aplikasi akan terbuka otomatis di browser pada alamat:
```
http://localhost:8501
```

---

## 📸 Screenshot Aplikasi

### Dashboard
![Dashboard](assets/dashboard.png)
*Tampilan dashboard dengan statistik dan grafik*

### Data Kendaraan
![Data Kendaraan](assets/data_kendaraan.png)
*Halaman manajemen CRUD kendaraan*

### QR Code Generator
![QR Code](assets/qr_code.png)
*Generate dan scan QR Code*

### Laporan & Grafik
![Laporan](assets/laporan.png)
*Visualisasi data dengan grafik interaktif*

---

## 💡 Cara Penggunaan

### Menambah Kendaraan Baru
1. Buka menu **Data Kendaraan**
2. Pilih tab **Tambah Kendaraan**
3. Isi form:
   - Plat Nomor (wajib)
   - Merk (wajib)
   - Model (wajib)
   - Tahun (wajib)
   - Jenis (Motor/Mobil)
   - Warna
   - Kilometer terakhir
   - Catatan
4. Klik **Simpan Kendaraan**
5. QR Code akan otomatis dibuat

### Scan QR & Lihat Detail
1. Buka menu **Scan QR Code**
2. Input plat nomor kendaraan (manual)
3. Klik **Cari Kendaraan**
4. Lihat detail kendaraan dan riwayat servis

### Menambah Catatan Servis
1. Buka menu **Scan QR Code**
2. Tab **Input Manual / Tambah Servis**
3. Pilih kendaraan
4. Isi detail servis:
   - Tanggal servis
   - Kilometer saat servis
   - Jenis servis
   - Bengkel
   - Biaya
   - Teknisi
   - Keterangan
5. Klik **Simpan Servis**

### Melihat Laporan
1. Buka menu **Laporan & Grafik**
2. Pilih rentang tanggal
3. Lihat grafik dan statistik
4. Klik **Export ke Excel** untuk download

---

## 📊 Daftar Fungsi (16 Fungsi)

### Fungsi CRUD & Data Management
1. `load_data()` - Membaca data dari CSV
2. `save_data()` - Menyimpan data ke CSV
3. `add_vehicle()` - Tambah kendaraan baru (CREATE)
4. `update_vehicle()` - Update data kendaraan (UPDATE)
5. `delete_vehicle()` - Hapus kendaraan (DELETE)
6. `add_service()` - Tambah catatan servis (CREATE)
7. `get_vehicle_services()` - Ambil riwayat servis (READ)

### Fungsi QR Code
8. `generate_qr_code()` - Generate QR Code

### Fungsi Statistik & Analisis
9. `get_total_stats()` - Hitung statistik dashboard
10. `create_service_chart()` - Buat grafik servis
11. `create_cost_chart()` - Buat grafik biaya

### Fungsi Filter & Search
12. `filter_by_date()` - Filter data berdasarkan tanggal
13. `search_vehicle()` - Cari kendaraan

### Fungsi Export & Validasi
14. `export_to_excel()` - Export data ke Excel
15. `validate_vehicle_data()` - Validasi data kendaraan
16. `validate_service_data()` - Validasi data servis

---

## ⚙️ Aturan Teknis

### ✅ Yang Digunakan
- ✅ Python + Streamlit
- ✅ Fungsi (def) dengan parameter
- ✅ CSV/Excel untuk storage
- ✅ QR Code generation
- ✅ Mode Offline 100%
- ✅ Layout wide
- ✅ Minimal 10 fungsi (ada 16 fungsi)

### ❌ Yang TIDAK Digunakan
- ❌ Class / OOP
- ❌ Inheritance / Polymorphism
- ❌ Database SQL (MySQL, PostgreSQL, MongoDB, dll)
- ❌ Fitur yang memerlukan internet

---

## 📝 Catatan Penting

1. **Data Storage**: Semua data disimpan di folder `data/` dalam format CSV
2. **QR Code**: File QR disimpan di folder `qr/` dengan format `QR_[PLAT_NOMOR].png`
3. **Backup**: Disarankan backup folder `data/` secara berkala
4. **Excel Export**: File export disimpan di folder `data/`

---

Proyek ini dibuat untuk tugas **Pemrograman Terstruktur** - Program Studi Teknologi Informasi


- Dosen Pengampu: Budi Sutomo S.
- Mata Kuliah: Pemrograman Terstruktur
- Universitas: Universitas Dharma Wacana
- Tahun Akademik: 2024/2025


