import streamlit as st
import pandas as pd
from datetime import datetime
import os
from utils import (
    load_data, save_data, add_vehicle, update_vehicle, 
    delete_vehicle, add_service, get_vehicle_services,
    generate_qr_code, get_total_stats, create_service_chart,
    create_cost_chart, filter_by_date, search_vehicle,
    export_to_excel, validate_vehicle_data, validate_service_data,
    decode_qr_from_image
)

# Konfigurasi halaman
st.set_page_config(
    page_title="Tracking Perawatan Kendaraan",
    page_icon="🚗",
    layout="wide"
)

# Inisialisasi folder dan file
if not os.path.exists('data'):
    os.makedirs('data')
if not os.path.exists('qr'):
    os.makedirs('qr')

# File paths
VEHICLE_FILE = 'data/vehicles.csv'
SERVICE_FILE = 'data/service_log.csv'

# Inisialisasi session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'
if 'scanned_plat' not in st.session_state:
    st.session_state.scanned_plat = None

# Sidebar Menu
st.sidebar.title("🚗 Menu Navigasi")
menu = st.sidebar.radio(
    "Pilih Halaman:",
    ['Dashboard', 'Data Kendaraan', 'Scan QR Code', 'Laporan & Grafik', 'Tentang Aplikasi']
)

# ===== HALAMAN DASHBOARD =====
if menu == 'Dashboard':
    st.title("📊 Dashboard Tracking Perawatan Kendaraan")
    st.markdown("---")
    
    # Load data
    df_vehicles = load_data(VEHICLE_FILE)
    df_services = load_data(SERVICE_FILE)
    
    # Statistik utama
    col1, col2, col3, col4 = st.columns(4)
    
    stats = get_total_stats(df_vehicles, df_services)
    
    with col1:
        st.metric("Total Kendaraan", stats['total_vehicles'])
    with col2:
        st.metric("Total Servis", stats['total_services'])
    with col3:
        st.metric("Total Biaya", f"Rp {stats['total_cost']:,.0f}")
    with col4:
        st.metric("Servis Bulan Ini", stats['services_this_month'])
    
    st.markdown("---")
    
    # Grafik dan data terbaru
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Grafik Servis per Kendaraan")
        if not df_services.empty:
            chart = create_service_chart(df_services)
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("Belum ada data servis untuk ditampilkan")
    
    with col2:
        st.subheader("📝 Servis Terbaru")
        if not df_services.empty:
            recent = df_services.sort_values('tanggal', ascending=False).head(5)
            for idx, row in recent.iterrows():
                with st.container():
                    st.write(f"**{row['plat_nomor']}** - {row['jenis_servis']}")
                    st.caption(f"📅 {row['tanggal']} | 💰 Rp {row['biaya']:,.0f}")
                    st.markdown("---")
        else:
            st.info("Belum ada riwayat servis")

# ===== HALAMAN DATA KENDARAAN =====
elif menu == 'Data Kendaraan':
    st.title("🚗 Manajemen Data Kendaraan")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lihat Data", "➕ Tambah Kendaraan", "✏️ Edit Kendaraan", "🗑️ Hapus Kendaraan"])
    
    # Tab 1: Lihat Data
    with tab1:
        st.subheader("Daftar Kendaraan")
        
        df_vehicles = load_data(VEHICLE_FILE)
        
        # Fitur pencarian
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("🔍 Cari kendaraan (plat nomor, merk, model)", "")
        with col2:
            st.write("")
            st.write("")
            if st.button("Refresh Data"):
                st.rerun()
        
        if not df_vehicles.empty:
            if search_term:
                df_filtered = search_vehicle(df_vehicles, search_term)
            else:
                df_filtered = df_vehicles
            
            st.dataframe(df_filtered, use_container_width=True, height=400)
            st.success(f"Menampilkan {len(df_filtered)} kendaraan")
        else:
            st.info("Belum ada data kendaraan. Silakan tambah kendaraan baru.")
    
    # Tab 2: Tambah Kendaraan
    with tab2:
        st.subheader("Tambah Kendaraan Baru")
        
        with st.form("form_add_vehicle"):
            col1, col2 = st.columns(2)
            
            with col1:
                plat_nomor = st.text_input("Plat Nomor *", placeholder="B 1234 XYZ")
                merk = st.text_input("Merk *", placeholder="Honda")
                model = st.text_input("Model *", placeholder="Beat")
                tahun = st.number_input("Tahun *", min_value=1980, max_value=2025, value=2020)
            
            with col2:
                jenis = st.selectbox("Jenis Kendaraan *", ["Motor", "Mobil"])
                warna = st.text_input("Warna", placeholder="Hitam")
                km_terakhir = st.number_input("Kilometer Terakhir", min_value=0, value=0)
                catatan = st.text_area("Catatan", placeholder="Catatan tambahan...")
            
            submit = st.form_submit_button("💾 Simpan Kendaraan", use_container_width=True)
            
            if submit:
                vehicle_data = {
                    'plat_nomor': plat_nomor,
                    'merk': merk,
                    'model': model,
                    'tahun': tahun,
                    'jenis': jenis,
                    'warna': warna,
                    'km_terakhir': km_terakhir,
                    'catatan': catatan
                }
                
                is_valid, message = validate_vehicle_data(vehicle_data)
                
                if is_valid:
                    df_vehicles = load_data(VEHICLE_FILE)
                    
                    # Cek duplikat plat nomor
                    if not df_vehicles.empty and plat_nomor in df_vehicles['plat_nomor'].values:
                        st.error(f"❌ Plat nomor {plat_nomor} sudah terdaftar!")
                    else:
                        success = add_vehicle(VEHICLE_FILE, vehicle_data)
                        if success:
                            # Generate QR Code OTOMATIS
                            qr_path = generate_qr_code(plat_nomor)
                            st.success(f"✅ Kendaraan {plat_nomor} berhasil ditambahkan!")
                            st.success(f"✅ QR Code otomatis dibuat!")
                            
                            # Tampilkan QR Code
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.image(qr_path, caption=f"QR Code {plat_nomor}", width=200)
                            with col2:
                                st.info("📱 Scan QR Code ini dengan HP untuk melihat detail kendaraan")
                                with open(qr_path, 'rb') as f:
                                    st.download_button(
                                        label="📥 Download QR Code",
                                        data=f.read(),
                                        file_name=f"QR_{plat_nomor}.png",
                                        mime="image/png"
                                    )
                        else:
                            st.error("❌ Gagal menambahkan kendaraan!")
                else:
                    st.error(f"❌ {message}")
    
    # Tab 3: Edit Kendaraan
    with tab3:
        st.subheader("Edit Data Kendaraan")
        
        df_vehicles = load_data(VEHICLE_FILE)
        
        if not df_vehicles.empty:
            plat_edit = st.selectbox("Pilih Plat Nomor", df_vehicles['plat_nomor'].tolist())
            
            if plat_edit:
                vehicle_data = df_vehicles[df_vehicles['plat_nomor'] == plat_edit].iloc[0]
                
                with st.form("form_edit_vehicle"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_merk = st.text_input("Merk", value=vehicle_data['merk'])
                        new_model = st.text_input("Model", value=vehicle_data['model'])
                        new_tahun = st.number_input("Tahun", min_value=1980, max_value=2025, value=int(vehicle_data['tahun']))
                    
                    with col2:
                        new_jenis = st.selectbox("Jenis", ["Motor", "Mobil"], index=0 if vehicle_data['jenis'] == 'Motor' else 1)
                        new_warna = st.text_input("Warna", value=vehicle_data['warna'])
                        new_km = st.number_input("Kilometer", min_value=0, value=int(vehicle_data['km_terakhir']))
                        new_catatan = st.text_area("Catatan", value=vehicle_data['catatan'])
                    
                    submit_edit = st.form_submit_button("💾 Update Data", use_container_width=True)
                    
                    if submit_edit:
                        updated_data = {
                            'merk': new_merk,
                            'model': new_model,
                            'tahun': new_tahun,
                            'jenis': new_jenis,
                            'warna': new_warna,
                            'km_terakhir': new_km,
                            'catatan': new_catatan
                        }
                        
                        success = update_vehicle(VEHICLE_FILE, plat_edit, updated_data)
                        if success:
                            st.success(f"✅ Data kendaraan {plat_edit} berhasil diupdate!")
                            st.rerun()
                        else:
                            st.error("❌ Gagal mengupdate data!")
        else:
            st.info("Belum ada data kendaraan untuk diedit.")
    
    # Tab 4: Hapus Kendaraan
    with tab4:
        st.subheader("Hapus Kendaraan")
        st.warning("⚠️ Perhatian: Menghapus kendaraan akan menghapus semua riwayat servisnya!")
        
        df_vehicles = load_data(VEHICLE_FILE)
        
        if not df_vehicles.empty:
            plat_delete = st.selectbox("Pilih Plat Nomor yang akan dihapus", df_vehicles['plat_nomor'].tolist())
            
            if plat_delete:
                vehicle_info = df_vehicles[df_vehicles['plat_nomor'] == plat_delete].iloc[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Merk:** {vehicle_info['merk']}")
                    st.info(f"**Model:** {vehicle_info['model']}")
                with col2:
                    st.info(f"**Tahun:** {vehicle_info['tahun']}")
                    st.info(f"**Jenis:** {vehicle_info['jenis']}")
                
                confirm = st.checkbox("Saya yakin ingin menghapus kendaraan ini")
                
                if st.button("🗑️ Hapus Kendaraan", type="primary", disabled=not confirm):
                    success = delete_vehicle(VEHICLE_FILE, SERVICE_FILE, plat_delete)
                    if success:
                        st.success(f"✅ Kendaraan {plat_delete} berhasil dihapus!")
                        st.rerun()
                    else:
                        st.error("❌ Gagal menghapus kendaraan!")
        else:
            st.info("Belum ada data kendaraan untuk dihapus.")

# ===== HALAMAN SCAN QR CODE =====
elif menu == 'Scan QR Code':
    st.title("📱 Scan QR Code Kendaraan")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📸 Upload & Scan QR", "🔍 Input Manual", "📝 Tambah Servis"])
    
    # Tab 1: Upload & Scan QR
    with tab1:
        st.subheader("📸 Scan QR Code dengan Upload Foto")
        
        st.info("💡 **Cara Pakai:** Foto QR Code dengan HP → Upload di sini → Data kendaraan akan muncul otomatis!")
        
        # Upload image
        uploaded_file = st.file_uploader(
            "📤 Upload Foto QR Code",
            type=['png', 'jpg', 'jpeg'],
            help="Ambil foto QR Code kendaraan dengan HP, lalu upload di sini"
        )
        
        if uploaded_file is not None:
            # Tampilkan image yang diupload
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(uploaded_file, caption="QR Code yang diupload", width=250)
            
            with col2:
                with st.spinner("🔍 Membaca QR Code..."):
                    # Decode QR Code
                    plat_nomor = decode_qr_from_image(uploaded_file)
                    
                    if plat_nomor:
                        st.success(f"✅ QR Code berhasil dibaca: **{plat_nomor}**")
                        st.session_state.scanned_plat = plat_nomor
                    else:
                        st.error("❌ Tidak dapat membaca QR Code. Pastikan foto jelas dan QR Code terlihat.")
                        st.session_state.scanned_plat = None
        
        # Tampilkan data jika QR berhasil di-scan
        if st.session_state.scanned_plat:
            plat_nomor = st.session_state.scanned_plat
            
            st.markdown("---")
            st.subheader(f"📋 Detail Kendaraan: {plat_nomor}")
            
            df_vehicles = load_data(VEHICLE_FILE)
            
            if not df_vehicles.empty and plat_nomor in df_vehicles['plat_nomor'].values:
                vehicle = df_vehicles[df_vehicles['plat_nomor'] == plat_nomor].iloc[0]
                
                # Detail Kendaraan
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("🚗 Merk", vehicle['merk'])
                    st.metric("📦 Model", vehicle['model'])
                
                with col2:
                    st.metric("📅 Tahun", vehicle['tahun'])
                    st.metric("🎨 Warna", vehicle['warna'])
                
                with col3:
                    st.metric("🏍️ Jenis", vehicle['jenis'])
                    st.metric("🛣️ KM Terakhir", f"{vehicle['km_terakhir']:,} km")
                
                if vehicle['catatan']:
                    st.info(f"📝 **Catatan:** {vehicle['catatan']}")
                
                st.markdown("---")
                
                # Riwayat Servis
                st.subheader("🔧 Riwayat Servis")
                
                df_services = get_vehicle_services(SERVICE_FILE, plat_nomor)
                
                if not df_services.empty:
                    # Statistik Servis
                    col1, col2, col3 = st.columns(3)
                    
                    total_servis = len(df_services)
                    total_biaya = df_services['biaya'].sum()
                    avg_biaya = df_services['biaya'].mean()
                    
                    with col1:
                        st.metric("Total Servis", total_servis)
                    with col2:
                        st.metric("Total Biaya", f"Rp {total_biaya:,.0f}")
                    with col3:
                        st.metric("Rata-rata Biaya", f"Rp {avg_biaya:,.0f}")
                    
                    st.markdown("---")
                    
                    # Tabel Riwayat
                    st.dataframe(
                        df_services[['tanggal', 'km_saat_servis', 'jenis_servis', 'bengkel', 'biaya', 'teknisi']],
                        use_container_width=True,
                        height=300
                    )
                    
                    # Detail per servis (expandable)
                    st.markdown("### 📄 Detail Servis")
                    for idx, row in df_services.iterrows():
                        with st.expander(f"🔧 {row['jenis_servis']} - {row['tanggal']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Tanggal:** {row['tanggal']}")
                                st.write(f"**Jenis Servis:** {row['jenis_servis']}")
                                st.write(f"**Bengkel:** {row['bengkel']}")
                            with col2:
                                st.write(f"**KM Saat Servis:** {row['km_saat_servis']:,} km")
                                st.write(f"**Biaya:** Rp {row['biaya']:,.0f}")
                                st.write(f"**Teknisi:** {row['teknisi']}")
                            if row['keterangan']:
                                st.write(f"**Keterangan:** {row['keterangan']}")
                else:
                    st.info("📭 Belum ada riwayat servis untuk kendaraan ini")
                
            else:
                st.error(f"❌ Kendaraan dengan plat nomor **{plat_nomor}** tidak ditemukan di database!")
    
    # Tab 2: Input Manual
    with tab2:
        st.subheader("🔍 Cari Kendaraan Manual")
        st.info("💡 Jika tidak bisa scan QR, ketik plat nomor secara manual di sini")
        
        plat_input = st.text_input("Masukkan Plat Nomor", placeholder="B 1234 XYZ", key="manual_input")
        
        if st.button("🔍 Cari Kendaraan", use_container_width=True):
            if plat_input:
                st.session_state.scanned_plat = plat_input
                st.rerun()
            else:
                st.warning("⚠️ Masukkan plat nomor terlebih dahulu!")
    
    # Tab 3: Tambah Servis
    with tab3:
        st.subheader("📝 Tambah Catatan Servis Baru")
        
        df_vehicles = load_data(VEHICLE_FILE)
        
        if not df_vehicles.empty:
            with st.form("form_add_service"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Pre-fill jika sudah scan QR
                    default_index = 0
                    if st.session_state.scanned_plat and st.session_state.scanned_plat in df_vehicles['plat_nomor'].values:
                        default_index = df_vehicles['plat_nomor'].tolist().index(st.session_state.scanned_plat)
                    
                    plat_service = st.selectbox("Pilih Kendaraan *", df_vehicles['plat_nomor'].tolist(), index=default_index)
                    tanggal = st.date_input("Tanggal Servis *", value=datetime.now())
                    km_saat_servis = st.number_input("Kilometer Saat Servis *", min_value=0, value=0)
                    jenis_servis = st.selectbox("Jenis Servis *", 
                        ["Ganti Oli", "Service Berkala", "Ganti Ban", "Tune Up", 
                         "Ganti Aki", "Perbaikan Mesin", "Cuci Kendaraan", "Lainnya"])
                
                with col2:
                    bengkel = st.text_input("Nama Bengkel", placeholder="Bengkel ABC")
                    biaya = st.number_input("Biaya Servis (Rp) *", min_value=0, value=0)
                    teknisi = st.text_input("Nama Teknisi", placeholder="Nama teknisi")
                    keterangan = st.text_area("Keterangan Detail", placeholder="Detail pekerjaan yang dilakukan...")
                
                submit_service = st.form_submit_button("💾 Simpan Servis", use_container_width=True)
                
                if submit_service:
                    service_data = {
                        'plat_nomor': plat_service,
                        'tanggal': str(tanggal),
                        'km_saat_servis': km_saat_servis,
                        'jenis_servis': jenis_servis,
                        'bengkel': bengkel,
                        'biaya': biaya,
                        'teknisi': teknisi,
                        'keterangan': keterangan
                    }
                    
                    is_valid, message = validate_service_data(service_data)
                    
                    if is_valid:
                        success = add_service(SERVICE_FILE, service_data)
                        if success:
                            # Update KM terakhir di data kendaraan
                            df_vehicles = load_data(VEHICLE_FILE)
                            df_vehicles.loc[df_vehicles['plat_nomor'] == plat_service, 'km_terakhir'] = km_saat_servis
                            save_data(VEHICLE_FILE, df_vehicles)
                            
                            st.success(f"✅ Catatan servis untuk {plat_service} berhasil disimpan!")
                            st.balloons()
                        else:
                            st.error("❌ Gagal menyimpan catatan servis!")
                    else:
                        st.error(f"❌ {message}")
        else:
            st.warning("⚠️ Belum ada kendaraan terdaftar. Tambahkan kendaraan terlebih dahulu!")

# ===== HALAMAN LAPORAN & GRAFIK =====
elif menu == 'Laporan & Grafik':
    st.title("📊 Laporan & Analisis Data")
    st.markdown("---")
    
    df_services = load_data(SERVICE_FILE)
    df_vehicles = load_data(VEHICLE_FILE)
    
    if not df_services.empty:
        # Filter tanggal
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Dari Tanggal", value=datetime(2024, 1, 1))
        with col2:
            end_date = st.date_input("Sampai Tanggal", value=datetime.now())
        with col3:
            st.write("")
            st.write("")
            if st.button("📥 Export ke Excel"):
                file_path = export_to_excel(df_vehicles, df_services)
                with open(file_path, 'rb') as f:
                    st.download_button(
                        label="Download Excel",
                        data=f,
                        file_name=f"laporan_kendaraan_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        
        # Filter data berdasarkan tanggal
        df_filtered = filter_by_date(df_services, str(start_date), str(end_date))
        
        st.markdown("---")
        
        # Statistik periode
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Servis", len(df_filtered))
        with col2:
            total_biaya_periode = df_filtered['biaya'].sum()
            st.metric("Total Biaya", f"Rp {total_biaya_periode:,.0f}")
        with col3:
            avg_biaya = df_filtered['biaya'].mean() if len(df_filtered) > 0 else 0
            st.metric("Rata-rata Biaya", f"Rp {avg_biaya:,.0f}")
        with col4:
            unique_vehicles = df_filtered['plat_nomor'].nunique()
            st.metric("Kendaraan Terservis", unique_vehicles)
        
        st.markdown("---")
        
        # Grafik
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Jumlah Servis per Kendaraan")
            chart1 = create_service_chart(df_filtered)
            st.plotly_chart(chart1, use_container_width=True)
        
        with col2:
            st.subheader("💰 Total Biaya per Jenis Servis")
            chart2 = create_cost_chart(df_filtered)
            st.plotly_chart(chart2, use_container_width=True)
        
        st.markdown("---")
        
        # Tabel detail servis
        st.subheader("📋 Detail Servis Periode Terpilih")
        st.dataframe(df_filtered, use_container_width=True, height=400)
        
    else:
        st.info("📊 Belum ada data servis untuk ditampilkan. Mulai tambahkan catatan servis!")

# ===== HALAMAN TENTANG APLIKASI =====
elif menu == 'Tentang Aplikasi':
    st.title("ℹ️ Tentang Aplikasi")
    st.markdown("---")
    
    st.subheader("🚗 Tracking Perawatan Motor/Mobil")
    st.write("""
    Aplikasi ini dirancang untuk membantu Anda melacak dan mengelola perawatan kendaraan 
    (motor dan mobil) secara digital dan terorganisir.
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✨ Fitur Utama")
        st.write("""
        - ✅ **CRUD Kendaraan**: Tambah, lihat, edit, hapus data kendaraan
        - ✅ **QR Code**: Generate dan scan QR code untuk setiap kendaraan
        - ✅ **Riwayat Servis**: Catat semua perawatan dan perbaikan
        - ✅ **Laporan Visual**: Grafik dan statistik interaktif
        - ✅ **Export Excel**: Download laporan lengkap
        - ✅ **Filter Data**: Cari dan filter berdasarkan tanggal
        - ✅ **Mode Offline**: Semua data tersimpan lokal (CSV)
        """)
    
    with col2:
        st.subheader("🛠️ Teknologi")
        st.write("""
        - **Python**: Bahasa pemrograman utama
        - **Streamlit**: Framework UI/UX
        - **Pandas**: Pengolahan data
        - **Plotly**: Visualisasi data interaktif
        - **QR Code**: Generate dan scan QR
        - **CSV**: Penyimpanan data lokal
        """)
    
    st.markdown("---")
    
    st.subheader("📖 Cara Menggunakan")
    with st.expander("1️⃣ Tambah Kendaraan"):
        st.write("""
        - Buka menu **Data Kendaraan**
        - Pilih tab **Tambah Kendaraan**
        - Isi form dengan data lengkap
        - Klik **Simpan Kendaraan**
        - QR Code akan otomatis dibuat
        """)
    
    with st.expander("2️⃣ Scan QR dari HP"):
        st.write("""
        - Buka aplikasi ini di **browser HP**
        - Buka menu **Scan QR Code**
        - Tab **Upload & Scan QR**
        - Foto QR Code dengan kamera HP
        - Upload foto di aplikasi
        - Data kendaraan & riwayat servis akan **muncul otomatis**!
        """)
    
    with st.expander("3️⃣ Tambah Catatan Servis"):
        st.write("""
        - Buka menu **Scan QR Code**
        - Pilih tab **Input Manual / Tambah Servis**
        - Pilih kendaraan dan isi detail servis
        - Klik **Simpan Servis**
        """)
    
    with st.expander("4️⃣ Lihat Laporan"):
        st.write("""
        - Buka menu **Laporan & Grafik**
        - Pilih rentang tanggal
        - Lihat grafik dan statistik
        - Download laporan Excel jika perlu
        """)
    
    st.markdown("---")
    
    st.subheader("👨‍💻 Informasi Proyek")
    st.write("""
    **Mata Kuliah**: Pemrograman Terstruktur  
    **Framework**: Python + Streamlit  
    **Storage**: CSV (Offline)  
    **QR Code**: Terintegrasi  
    """)
    
    st.info("💡 **Catatan**: Aplikasi ini 100% offline dan data tersimpan di folder lokal Anda.")
    
    st.markdown("---")
    st.success("✅ Dibuat sesuai aturan: Tanpa Class/OOP, Menggunakan Fungsi, Storage CSV, QR Code Integration")
