import streamlit as st
import requests
import py3Dmol
from stmol import showmol
import math
import streamlit.components.v1 as components

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="ChemPro AI - Kelompok 1 PBTIK", 
    page_icon="🧪", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS UNTUK TAMPILAN PREMIUM ---
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
        © 2026 Developed by Kelompok 1 PBTIK | Pendidikan Kimia UNILA 2024
    </div>
    """, unsafe_allow_html=True)

# --- 3. FUNGSI PINTAR (BACKEND) ---
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
    view.spin(True)
    showmol(view, height=450, width=800)

# --- 4. SIDEBAR (NAVIGASI) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/995/995440.png", width=80)
    st.title("ChemPro AI")
    st.caption("Lab Assistant v3.5 (Full Edition)")
    st.divider()
    
    menu = st.radio("Pilih Modul Lab:", 
             ["⚖️ Stoikiometri Padatan", 
              "💧 Kalkulator Pengenceran", 
              "🌡️ pH & Analitik", 
              "🌐 Ensiklopedia 3D",
              "🔋 Simulasi Sel Volta",
              "📈 Laju & Kinetika",
              "🛡️ K3 & Keamanan Lab",
              "📋 Generator Diagram Alir"])
    
    st.divider()
    st.markdown("### 🛠️ Developer:")
    st.success("✨ *Kelompok 1 PBTIK*")
    st.info("Projek Kimia Digital - Pendidikan Kimia Universitas Lampung")

# --- 5. LOGIKA MODUL ---

# MODUL 1: STOIKIOMETRI
if menu == "⚖️ Stoikiometri Padatan":
    st.title("⚖️ Kalkulator Massa Padatan")
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            zat = st.text_input("Nama Zat (Inggris):", "Sodium Hydroxide")
            molar = st.number_input("Molaritas (M):", 0.001, 10.0, 0.1)
            vol = st.number_input("Volume (mL):", 10, 5000, 250)
            btn = st.button("Hitung", type="primary", use_container_width=True)
    with col2:
        if btn:
            data = get_chem_data(zat)
            if data:
                massa = molar * (vol/1000) * data['mr']
                st.metric("Massa Wajib Timbang", f"{massa:.4f} g")
                st.write(f"**Info:** {data['formula']} | Mr: {data['mr']}")
            else: st.error("Zat tidak ditemukan.")

# MODUL 2: PENGENCERAN
elif menu == "💧 Kalkulator Pengenceran":
    st.title("💧 Pengenceran Larutan")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        m1 = c1.number_input("M1 (Pekat):", 0.1, 18.0, 1.0)
        m2 = c2.number_input("M2 (Target):", 0.01, 10.0, 0.1)
        v2 = c3.number_input("V2 (Akhir) mL:", 10, 1000, 100)
    if m2 < m1:
        v1 = (m2 * v2) / m1
        st.success(f"Ambil larutan pekat: **{v1:.2f} mL**")
    else: st.warning("M2 harus < M1")

# MODUL 3: PH & ANALITIK
elif menu == "🌡️ pH & Analitik":
    st.title("🌡️ Analisis pH")
    with st.container(border=True):
        kat = st.selectbox("Jenis:", ["Asam Kuat", "Basa Kuat", "Asam Lemah", "Basa Lemah"])
        m = st.number_input("Konsentrasi (M):", 0.0001, 1.0, 0.1, format="%.4f")
        val = st.number_input("Valensi:", 1, 3, 1)
        if "Lemah" in kat: ka = st.number_input("Ka/Kb:", value=1.8e-5, format="%.2e")
        if st.button("Hitung pH", use_container_width=True):
            if "Kuat" in kat: h = m * val
            else: h = math.sqrt(ka * m)
            ph = -math.log10(h) if "Asam" in kat else 14 - (-math.log10(h))
            st.metric("Hasil pH", f"{ph:.2f}")

# MODUL 4: ENSIKLOPEDIA 3D
elif menu == "🌐 Ensiklopedia 3D":
    st.title("🌐 Visualisasi Molekuler")
    cari = st.text_input("Ketik Nama Molekul (Inggris):", "Caffeine")
    if cari:
        sdf, c_data, desc = get_3d_sdf(cari), get_chem_data(cari), get_wiki_summary(cari)
        if sdf and c_data:
            c1, c2 = st.columns([1.5, 1])
            with c1: render_3d_molecule(sdf)
            with c2:
                st.subheader("🧬 Info")
                st.write(f"IUPAC: {c_data['iupac']}\n\nFormula: {c_data['formula']}")
                st.divider()
                st.write(desc)

# MODUL 5: SEL VOLTA
elif menu == "🔋 Simulasi Sel Volta":
    st.title("🔋 Sel Volta")
    e_nol = {"Li":-3.04, "K":-2.92, "Na":-2.71, "Mg":-2.37, "Al":-1.66, "Zn":-0.76, "Fe":-0.44, "Ni":-0.25, "Sn":-0.14, "Pb":-0.13, "H2":0.0, "Cu":0.34, "Ag":0.80, "Au":1.50}
    c1, c2 = st.columns(2)
    l1 = c1.selectbox("Logam A:", list(e_nol.keys()), index=9)
    l2 = c2.selectbox("Logam B:", list(e_nol.keys()), index=12)
    if st.button("Reaksikan"):
        v1, v2 = e_nol[l1], e_nol[l2]
        anoda, katoda = (l1, l2) if v1 < v2 else (l2, l1)
        st.metric("E-Cell", f"{abs(v1-v2):.2f} V")
        st.code(f"{anoda} | {anoda}ⁿ⁺ || {katoda}ⁿ⁺ | {katoda}")

# MODUL 6: KINETIKA
elif menu == "📈 Laju & Kinetika":
    st.title("📈 Kinetika Reaksi")
    orde = st.selectbox("Orde:", [0, 1, 2])
    k, a0, t_max = st.number_input("k:", 0.01, 1.0, 0.05), st.number_input("A0:", 0.1, 2.0, 1.0), st.slider("Waktu:", 10, 200, 50)
    if st.button("Gambarkan Grafik"):
        ts = list(range(t_max))
        if orde==0: ys = [max(0, a0 - k*t) for t in ts]
        elif orde==1: ys = [a0 * math.exp(-k*t) for t in ts]
        else: ys = [1/(1/a0 + k*t) for t in ts]
        st.line_chart(ys)

# MODUL 7: K3 & KEAMANAN
elif menu == "🛡️ K3 & Keamanan Lab":
    st.title("🛡️ Keamanan Laboratorium")
    haz = {"H2SO4": "Korosif berat!", "NaOH": "Iritasi kuat!", "Metanol": "Mudah terbakar!", "HCl": "Uap beracun!"}
    p = st.selectbox("Bahan:", list(haz.keys()))
    st.error(haz[p])
    st.info("1. Gunakan Jas Lab\n2. Gunakan Goggles\n3. Jangan makan/minum")

# MODUL 8: DIAGRAM ALIR
elif menu == "📋 Generator Diagram Alir":
    st.title("📋 Diagram Alir Prosedur")
    teks = st.text_area("Masukkan Prosedur (Satu langkah per baris):", "Timbang 2g NaOH\nLarutkan dalam air\nMasukkan ke labu ukur")
    if st.button("Buat Diagram"):
        lines = [l.strip() for l in teks.split('\n') if l.strip()]
        mm = "graph TD\n"
        for i, line in enumerate(lines):
            mm += f'    Node{i}["{line}"]\n'
            if i > 0: mm += f'    Node{i-1} --> Node{i}\n'
        html = f"""<div class="mermaid">{mm}</div><script type="module">import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';mermaid.initialize({{startOnLoad:true, theme:'neutral'}});</script>"""
        components.html(html, height=len(lines)*100)