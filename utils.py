import pandas as pd
import os
import qrcode
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# ===== FUNGSI 1: LOAD DATA =====
def load_data(file_path):
    """
    Membaca data dari file CSV
    Parameter: file_path (string) - path file CSV
    Return: DataFrame pandas
    """
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            return df
        else:
            # Buat file baru jika belum ada
            if 'vehicles' in file_path:
                df = pd.DataFrame(columns=[
                    'plat_nomor', 'merk', 'model', 'tahun', 'jenis', 
                    'warna', 'km_terakhir', 'catatan', 'tanggal_daftar'
                ])
            else:  # service_log
                df = pd.DataFrame(columns=[
                    'id_servis', 'plat_nomor', 'tanggal', 'km_saat_servis',
                    'jenis_servis', 'bengkel', 'biaya', 'teknisi', 'keterangan'
                ])
            df.to_csv(file_path, index=False)
            return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

# ===== FUNGSI 2: SAVE DATA =====
def save_data(file_path, dataframe):
    """
    Menyimpan DataFrame ke file CSV
    Parameter: 
        - file_path (string): path file CSV
        - dataframe (DataFrame): data yang akan disimpan
    Return: Boolean (True jika sukses)
    """
    try:
        dataframe.to_csv(file_path, index=False)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

# ===== FUNGSI 3: ADD VEHICLE (CREATE) =====
def add_vehicle(file_path, vehicle_data):
    """
    Menambah data kendaraan baru (CREATE)
    Parameter:
        - file_path (string): path file CSV
        - vehicle_data (dict): dictionary berisi data kendaraan
    Return: Boolean (True jika sukses)
    """
    try:
        df = load_data(file_path)
        
        # Tambahkan tanggal pendaftaran
        vehicle_data['tanggal_daftar'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Buat DataFrame baru dari data kendaraan
        new_row = pd.DataFrame([vehicle_data])
        
        # Gabungkan dengan data existing
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Simpan ke CSV
        return save_data(file_path, df)
    except Exception as e:
        print(f"Error adding vehicle: {e}")
        return False

# ===== FUNGSI 4: UPDATE VEHICLE (UPDATE) =====
def update_vehicle(file_path, plat_nomor, updated_data):
    """
    Mengupdate data kendaraan (UPDATE)
    Parameter:
        - file_path (string): path file CSV
        - plat_nomor (string): plat nomor kendaraan yang akan diupdate
        - updated_data (dict): data baru
    Return: Boolean (True jika sukses)
    """
    try:
        df = load_data(file_path)
        
        # Update data
        for key, value in updated_data.items():
            df.loc[df['plat_nomor'] == plat_nomor, key] = value
        
        return save_data(file_path, df)
    except Exception as e:
        print(f"Error updating vehicle: {e}")
        return False

# ===== FUNGSI 5: DELETE VEHICLE (DELETE) =====
def delete_vehicle(vehicle_file, service_file, plat_nomor):
    """
    Menghapus data kendaraan dan semua riwayat servisnya (DELETE)
    Parameter:
        - vehicle_file (string): path file kendaraan
        - service_file (string): path file servis
        - plat_nomor (string): plat nomor yang akan dihapus
    Return: Boolean (True jika sukses)
    """
    try:
        # Hapus dari data kendaraan
        df_vehicles = load_data(vehicle_file)
        df_vehicles = df_vehicles[df_vehicles['plat_nomor'] != plat_nomor]
        save_data(vehicle_file, df_vehicles)
        
        # Hapus riwayat servis
        df_services = load_data(service_file)
        if not df_services.empty:
            df_services = df_services[df_services['plat_nomor'] != plat_nomor]
            save_data(service_file, df_services)
        
        # Hapus QR Code file jika ada
        qr_path = f"qr/QR_{plat_nomor}.png"
        if os.path.exists(qr_path):
            os.remove(qr_path)
        
        return True
    except Exception as e:
        print(f"Error deleting vehicle: {e}")
        return False

# ===== FUNGSI 6: ADD SERVICE (CREATE) =====
def add_service(file_path, service_data):
    """
    Menambah catatan servis baru
    Parameter:
        - file_path (string): path file CSV
        - service_data (dict): data servis
    Return: Boolean (True jika sukses)
    """
    try:
        df = load_data(file_path)
        
        # Generate ID servis otomatis
        if df.empty:
            service_id = 'SRV001'
        else:
            last_id = df['id_servis'].iloc[-1] if 'id_servis' in df.columns else 'SRV000'
            num = int(last_id.replace('SRV', '')) + 1
            service_id = f'SRV{num:03d}'
        
        service_data['id_servis'] = service_id
        
        # Buat DataFrame baru
        new_row = pd.DataFrame([service_data])
        
        # Gabungkan
        df = pd.concat([df, new_row], ignore_index=True)
        
        return save_data(file_path, df)
    except Exception as e:
        print(f"Error adding service: {e}")
        return False

# ===== FUNGSI 7: GET VEHICLE SERVICES (READ) =====
def get_vehicle_services(file_path, plat_nomor):
    """
    Mengambil semua riwayat servis untuk kendaraan tertentu
    Parameter:
        - file_path (string): path file CSV
        - plat_nomor (string): plat nomor kendaraan
    Return: DataFrame pandas
    """
    try:
        df = load_data(file_path)
        if not df.empty:
            df_filtered = df[df['plat_nomor'] == plat_nomor]
            # Urutkan berdasarkan tanggal terbaru
            if not df_filtered.empty:
                df_filtered = df_filtered.sort_values('tanggal', ascending=False)
            return df_filtered
        return pd.DataFrame()
    except Exception as e:
        print(f"Error getting vehicle services: {e}")
        return pd.DataFrame()

# ===== FUNGSI 8: GENERATE QR CODE =====
def generate_qr_code(plat_nomor):
    """
    Generate QR Code untuk kendaraan
    Parameter: plat_nomor (string)
    Return: string (path file QR Code)
    """
    try:
        # Buat QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Data yang akan di-encode: plat nomor
        qr.add_data(plat_nomor)
        qr.make(fit=True)
        
        # Buat image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Simpan
        if not os.path.exists('qr'):
            os.makedirs('qr')
        
        file_path = f"qr/QR_{plat_nomor}.png"
        img.save(file_path)
        
        return file_path
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None

# ===== FUNGSI 9: GET TOTAL STATS =====
def get_total_stats(df_vehicles, df_services):
    """
    Menghitung statistik total untuk dashboard
    Parameter:
        - df_vehicles (DataFrame): data kendaraan
        - df_services (DataFrame): data servis
    Return: dict berisi statistik
    """
    try:
        total_vehicles = len(df_vehicles) if not df_vehicles.empty else 0
        total_services = len(df_services) if not df_services.empty else 0
        
        total_cost = 0
        services_this_month = 0
        
        if not df_services.empty:
            total_cost = df_services['biaya'].sum()
            
            # Hitung servis bulan ini
            current_month = datetime.now().strftime('%Y-%m')
            df_services['tanggal'] = pd.to_datetime(df_services['tanggal'])
            services_this_month = len(df_services[df_services['tanggal'].dt.strftime('%Y-%m') == current_month])
        
        return {
            'total_vehicles': total_vehicles,
            'total_services': total_services,
            'total_cost': total_cost,
            'services_this_month': services_this_month
        }
    except Exception as e:
        print(f"Error calculating stats: {e}")
        return {
            'total_vehicles': 0,
            'total_services': 0,
            'total_cost': 0,
            'services_this_month': 0
        }

# ===== FUNGSI 10: CREATE SERVICE CHART =====
def create_service_chart(df_services):
    """
    Membuat grafik jumlah servis per kendaraan
    Parameter: df_services (DataFrame)
    Return: plotly figure
    """
    try:
        if df_services.empty:
            fig = go.Figure()
            fig.add_annotation(text="Tidak ada data", showarrow=False)
            return fig
        
        # Hitung jumlah servis per kendaraan
        service_counts = df_services['plat_nomor'].value_counts().reset_index()
        service_counts.columns = ['plat_nomor', 'jumlah_servis']
        
        # Buat bar chart
        fig = px.bar(
            service_counts,
            x='plat_nomor',
            y='jumlah_servis',
            title='Jumlah Servis per Kendaraan',
            labels={'plat_nomor': 'Plat Nomor', 'jumlah_servis': 'Jumlah Servis'},
            color='jumlah_servis',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            xaxis_title="Plat Nomor",
            yaxis_title="Jumlah Servis",
            showlegend=False,
            height=400
        )
        
        return fig
    except Exception as e:
        print(f"Error creating service chart: {e}")
        fig = go.Figure()
        fig.add_annotation(text="Error membuat grafik", showarrow=False)
        return fig

# ===== FUNGSI 11: CREATE COST CHART =====
def create_cost_chart(df_services):
    """
    Membuat grafik total biaya per jenis servis
    Parameter: df_services (DataFrame)
    Return: plotly figure
    """
    try:
        if df_services.empty:
            fig = go.Figure()
            fig.add_annotation(text="Tidak ada data", showarrow=False)
            return fig
        
        # Hitung total biaya per jenis servis
        cost_by_type = df_services.groupby('jenis_servis')['biaya'].sum().reset_index()
        cost_by_type = cost_by_type.sort_values('biaya', ascending=False)
        
        # Buat pie chart
        fig = px.pie(
            cost_by_type,
            values='biaya',
            names='jenis_servis',
            title='Distribusi Biaya per Jenis Servis',
            hole=0.4
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )
        
        fig.update_layout(height=400)
        
        return fig
    except Exception as e:
        print(f"Error creating cost chart: {e}")
        fig = go.Figure()
        fig.add_annotation(text="Error membuat grafik", showarrow=False)
        return fig

# ===== FUNGSI 12: FILTER BY DATE =====
def filter_by_date(df_services, start_date, end_date):
    """
    Filter data servis berdasarkan rentang tanggal
    Parameter:
        - df_services (DataFrame): data servis
        - start_date (string): tanggal mulai (YYYY-MM-DD)
        - end_date (string): tanggal akhir (YYYY-MM-DD)
    Return: DataFrame yang sudah difilter
    """
    try:
        if df_services.empty:
            return df_services
        
        df_services['tanggal'] = pd.to_datetime(df_services['tanggal'])
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        filtered = df_services[(df_services['tanggal'] >= start) & (df_services['tanggal'] <= end)]
        return filtered
    except Exception as e:
        print(f"Error filtering by date: {e}")
        return df_services

# ===== FUNGSI 13: SEARCH VEHICLE =====
def search_vehicle(df_vehicles, search_term):
    """
    Mencari kendaraan berdasarkan plat nomor, merk, atau model
    Parameter:
        - df_vehicles (DataFrame): data kendaraan
        - search_term (string): kata kunci pencarian
    Return: DataFrame hasil pencarian
    """
    try:
        if df_vehicles.empty or not search_term:
            return df_vehicles
        
        search_term = search_term.lower()
        
        filtered = df_vehicles[
            df_vehicles['plat_nomor'].str.lower().str.contains(search_term) |
            df_vehicles['merk'].str.lower().str.contains(search_term) |
            df_vehicles['model'].str.lower().str.contains(search_term)
        ]
        
        return filtered
    except Exception as e:
        print(f"Error searching vehicle: {e}")
        return df_vehicles

# ===== FUNGSI 14: EXPORT TO EXCEL =====
def export_to_excel(df_vehicles, df_services):
    """
    Export data ke file Excel dengan multiple sheets
    Parameter:
        - df_vehicles (DataFrame): data kendaraan
        - df_services (DataFrame): data servis
    Return: string (path file Excel)
    """
    try:
        file_name = f"laporan_kendaraan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = f"data/{file_name}"
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df_vehicles.to_excel(writer, sheet_name='Data Kendaraan', index=False)
            df_services.to_excel(writer, sheet_name='Riwayat Servis', index=False)
            
            # Buat summary sheet
            summary_data = {
                'Keterangan': [
                    'Total Kendaraan',
                    'Total Servis',
                    'Total Biaya Servis',
                    'Tanggal Export'
                ],
                'Nilai': [
                    len(df_vehicles),
                    len(df_services),
                    f"Rp {df_services['biaya'].sum():,.0f}" if not df_services.empty else "Rp 0",
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
            }
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Ringkasan', index=False)
        
        return file_path
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return None

# ===== FUNGSI 15: VALIDATE VEHICLE DATA =====
def validate_vehicle_data(vehicle_data):
    """
    Validasi data kendaraan sebelum disimpan
    Parameter: vehicle_data (dict)
    Return: tuple (Boolean, string message)
    """
    try:
        # Cek field wajib
        required_fields = ['plat_nomor', 'merk', 'model', 'tahun']
        
        for field in required_fields:
            if not vehicle_data.get(field) or str(vehicle_data[field]).strip() == '':
                return False, f"Field {field} wajib diisi!"
        
        # Validasi tahun
        tahun = int(vehicle_data['tahun'])
        if tahun < 1980 or tahun > 2025:
            return False, "Tahun kendaraan tidak valid!"
        
        # Validasi plat nomor format (sederhana)
        plat = vehicle_data['plat_nomor'].strip()
        if len(plat) < 3:
            return False, "Plat nomor terlalu pendek!"
        
        return True, "Data valid"
    except Exception as e:
        return False, f"Error validasi: {str(e)}"

# ===== FUNGSI 16: VALIDATE SERVICE DATA =====
def validate_service_data(service_data):
    """
    Validasi data servis sebelum disimpan
    Parameter: service_data (dict)
    Return: tuple (Boolean, string message)
    """
    try:
        # Cek field wajib
        required_fields = ['plat_nomor', 'tanggal', 'jenis_servis', 'biaya']
        
        for field in required_fields:
            value = service_data.get(field)
            if value is None or (isinstance(value, str) and value.strip() == ''):
                return False, f"Field {field} wajib diisi!"
        
        # Validasi biaya
        biaya = float(service_data['biaya'])
        if biaya < 0:
            return False, "Biaya tidak boleh negatif!"
        
        # Validasi km
        km = float(service_data.get('km_saat_servis', 0))
        if km < 0:
            return False, "Kilometer tidak boleh negatif!"
        
        return True, "Data valid"
    except Exception as e:
        return False, f"Error validasi: {str(e)}"
