import streamlit as st
import requests
import py3Dmol
from stmol import showmol
import math

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="ChemPro AI - Kelompok 1 PBTIK", 
    page_icon="🧪", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS UNTUK TAMPILAN PREMIUM ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    .stMetric { background-color: #161B22; padding: 15px; border-radius: 10px; border: 1px solid #30363D; }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0E1117;
        color: #8B949E;
        text-align: center;
        padding: 5px;
        font-size: 12px;
        border-top: 1px solid #30363D;
        z-index: 999;
    }
    </style>
    <div class="footer">
        © 2024 Developed by Kelompok 1 PBTIK | Laboratorium Kimia Digital
    </div>
    """, unsafe_allow_html=True)

# --- FUNGSI PINTAR (BACKEND) ---
@st.cache_data
def get_chem_data(nama_zat):
    nama_zat = nama_zat.strip()
    if not nama_zat: return None
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{nama_zat}/property/MolecularWeight,MolecularFormula,IUPACName/JSON"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['PropertyTable']['Properties'][0]
            return {
                "mr": float(data.get('MolecularWeight', 0)),
                "formula": data.get('MolecularFormula', 'N/A'),
                "iupac": data.get('IUPACName', 'N/A')
            }
        return None
    except: return None

@st.cache_data
def get_3d_sdf(nama_zat):
    nama_zat = nama_zat.strip()
    if not nama_zat: return None
    url_3d = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{nama_zat}/record/SDF/?record_type=3d"
    try:
        response = requests.get(url_3d)
        if response.status_code == 200: return response.text
        url_2d = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{nama_zat}/record/SDF/?record_type=2d"
        res_2d = requests.get(url_2d)
        if res_2d.status_code == 200: return res_2d.text
        return None
    except: return None

@st.cache_data
def get_wiki_summary(nama_zat):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{nama_zat}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('extract', 'Deskripsi tidak ditemukan.')
        return "Deskripsi tidak tersedia."
    except: return "Gagal memuat ensiklopedia."

def render_3d_molecule(sdf_data):
    view = py3Dmol.view(width=800, height=450)
    view.addModel(sdf_data, 'sdf')
    view.setStyle({'stick': {'radius': 0.15}, 'sphere': {'scale': 0.3}})
    view.setBackgroundColor('#0E1117') 
    view.zoomTo()
    view.spin(True) # Animasi putar otomatis
    showmol(view, height=450, width=800)

# --- SIDEBAR (NAVIGASI & KREDIT) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/995/995440.png", width=80)
    st.title("ChemPro AI")
    st.caption("Asisten Lab Pintar v2.1")
    st.divider()
    
    menu = st.radio("Navigasi Modul:", 
             ["⚖️ Stoikiometri Padatan", 
              "💧 Kalkulator Pengenceran", 
              "🌡️ pH & Analitik", 
              "🌐 Ensiklopedia 3D"])
    
    st.divider()
    # Identitas Kelompok di Sidebar
    st.markdown("### 🛠️ Developer:")
    st.success("✨ *Kelompok 1 PBTIK*")
    st.info("Projek Integrasi Teknologi Informasi untuk Laboratorium Kimia.")

# --- ROUTING HALAMAN ---
if menu == "⚖️ Stoikiometri Padatan":
    st.title("⚖️ Kalkulator Massa Padatan")
    st.write("Gunakan modul ini untuk menentukan massa penimbangan zat padat secara presisi.")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            zat = st.text_input("Nama Zat (Inggris):", "Sodium Hydroxide")
            molar = st.number_input("Target Molaritas (M):", 0.001, 5.0, 0.1, step=0.01)
            vol = st.number_input("Volume Akhir (mL):", 10, 2000, 250, step=10)
            btn = st.button("Hitung Sekarang", type="primary", use_container_width=True)
            
    with col2:
        if btn:
            data = get_chem_data(zat)
            if data:
                massa = molar * (vol/1000) * data['mr']
                st.metric("Massa Wajib Ditimbang", f"{massa:.4f} g")
                st.markdown(f"*Data Publikasi:* \nFormula: {data['formula']}  \nMr: {data['mr']} g/mol")
            else:
                st.error("Zat tidak ditemukan.")

elif menu == "💧 Kalkulator Pengenceran":
    st.title("💧 Pengenceran Larutan")
    st.markdown("Menghitung volume pemipetan menggunakan hukum $M_1V_1 = M_2V_2$")
    
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        m1 = c1.number_input("M1 (Pekat):", 0.1, 18.0, 1.0)
        m2 = c2.number_input("M2 (Target):", 0.01, 10.0, 0.1)
        v2 = c3.number_input("V2 (Volume Akhir) mL:", 10, 1000, 100)
        
    if m2 < m1:
        v1 = (m2 * v2) / m1
        st.success(f"Ambil larutan pekat sebanyak: *{v1:.2f} mL*")
    else:
        st.warning("Molaritas target harus lebih kecil dari stok awal.")

elif menu == "🌡️ pH & Analitik":
    st.title("🌡️ Analisis Derajat Keasaman (pH)")
    
    with st.container(border=True):
        kat = st.selectbox("Jenis Zat:", ["Asam Kuat", "Basa Kuat", "Asam Lemah", "Basa Lemah"])
        col_a, col_b = st.columns(2)
        m = col_a.number_input("Konsentrasi (M):", 0.0001, 1.0, 0.1, format="%.4f")
        val = col_b.number_input("Valensi (H+/OH-):", 1, 3, 1)
        
        if "Lemah" in kat:
            k_val = st.number_input("Nilai Ka/Kb (cth: 1.8e-5):", value=1.8e-5, format="%.2e")
        
        if st.button("Hitung pH", use_container_width=True):
            if kat == "Asam Kuat": h = m * val
            elif kat == "Basa Kuat": h = m * val # ini sebenarnya OH-
            elif kat == "Asam Lemah": h = math.sqrt(k_val * m)
            elif kat == "Basa Lemah": h = math.sqrt(k_val * m) # ini sebenarnya OH-
            
            res = -math.log10(h)
            final_ph = res if "Asam" in kat else 14 - res
            st.metric("Hasil pH Larutan", f"{final_ph:.2f}")

elif menu == "🌐 Ensiklopedia 3D":
    st.title("🌐 Visualisasi & Data Molekuler")
    cari = st.text_input("Ketik Nama Molekul (cth: Caffeine, Benzene, Glucose):", "Caffeine")
    
    if cari:
        with st.spinner("Mengunduh Model 3D..."):
            sdf = get_3d_sdf(cari)
            c_data = get_chem_data(cari)
            desc = get_wiki_summary(cari)
            
        if sdf and c_data:
            c1, c2 = st.columns([1.5, 1])
            with c1:
                st.info("Molekul Interaktif (Auto-Spin On)")
                render_3d_molecule(sdf)
            with c2:
                st.subheader("🧬 Informasi Kimia")
                st.write(f"*Nama:* {c_data['iupac']}")
                st.write(f"*Rumus:* {c_data['formula']}")
                st.divider()
                st.subheader("📚 Deskripsi")
                st.write(desc)