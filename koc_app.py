import streamlit as st
import pandas as pd
import os
from datetime import date
import base64
import requests
import plotly.express as px

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="KOÇ HALİL ŞAHAN", layout="wide")

# GitHub Bağlantısı
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
REPO_NAME = st.secrets.get("REPO_NAME")

def github_a_kaydet(dosya_adi, df):
    if not GITHUB_TOKEN or not REPO_NAME:
        return False
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{dosya_adi}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    content = base64.b64encode(df.to_csv(index=False).encode()).decode()
    data = {"message": f"Güncelleme: {date.today()}", "content": content}
    if sha: data["sha"] = sha
    res = requests.put(url, headers=headers, json=data)
    return res.status_code in [200, 201]

# --- TASARIM VE ARKAPLAN ---
RESIM_YOLU = "panel_bg.jpg"
LOGO_YOLU = "logo.jpg" 

def set_bg(main_bg):
    if os.path.exists(main_bg):
        with open(main_bg, "rb") as f: data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""<style>
        .stApp {{ background: url("data:image/png;base64,{b64}"); background-size: cover; background-attachment: fixed; }}
        .stApp::before {{ content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.7); z-index: 0; }}
        .main .block-container {{ position: relative; z-index: 10; }}
        h1, h2, h3, p, label {{ color: white !important; text-shadow: 2px 2px 10px rgba(0,0,0,1) !important; }}
        [data-testid="stSidebar"] [data-testid="stImage"] {{ background-color: rgba(128, 128, 128, 0.3); padding: 15px; border-radius: 20px; }}
        .main-title {{ font-size: 4.5rem !important; font-weight: 800; text-align: center; color: white; }}
        .sub-title {{ font-size: 1.5rem !important; font-style: italic; text-align: center; color: #f0f0f0; margin-top: -10px; }}
        </style>""", unsafe_allow_html=True)

set_bg(RESIM_YOLU)

# --- VERİ DOSYALARI ---
KILO_DOSYASI = "kilo_verileri.csv"
OLCU_DOSYASI = "haftalik_olculer.csv"
BESLENME_DOSYASI = "beslenme_verileri.csv"

def veriyi_yukle(dosya, kolonlar):
    if os.path.exists(dosya):
        try:
            df = pd.read_csv(dosya)
            df['Tarih'] = pd.to_datetime(df['Tarih']).dt.date
            return df
        except: return pd.DataFrame(columns=kolonlar)
    return pd.DataFrame(columns=kolonlar)

def farkli_tablo_yap(df):
    if df.empty: return df
    df = df.sort_values(by="Tarih")
    # Sayısal kolonları bul ve farklarını hesapla
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        df[f'{col} (Fark)'] = df[col].diff().fillna(0)
    return df.sort_values(by="Tarih", ascending=False)

# --- KULLANICILAR ---
KULLANICILAR = {"halil": "sahan123", "emrecan": "emrecan2026", "ceyda": "ceyda2026", "umuttatar": "tatar2026"}

if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.8, 1.4, 0.8])
    with col2:
        st.markdown('<p class="main-title">KOÇ HALİL ŞAHAN</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">be wild but stay soft</p>', unsafe_allow_html=True)
        u_in = st.text_input("KULLANICI ADI").lower()
        p_in = st.text_input("ŞİFRE", type="password")
        if st.button("GİRİŞ YAP 🔥", use_container_width=True):
            if u_in in KULLANICILAR and KULLANICILAR[u_in] == p_in:
                st.session_state.user = u_in
                st.rerun()
else:
    current_user = st.session_state.user
    
    # --- COACH PANELİ ---
    if current_user == "halil":
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title("COACH PANELİ 👑")
            menu = st.radio("MENÜ", ["🏠 Genel Tablo", "📊 Detaylı Analiz", "🥗 Beslenme", "📏 Ölçü Kayıtları", "🗑️ Veri Sil"])
            if st.button("Çıkış Yap"):
                st.session_state.user = None
                st.rerun()

        if menu == "🏠 Genel Tablo":
            st.title("Günlük Kilo Özetleri")
            st.dataframe(farkli_tablo_yap(veriyi_yukle(KILO_DOSYASI, [])), use_container_width=True)
        elif menu == "📊 Detaylı Analiz":
            df_k = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
            sporcular = df_k['Öğrenci Adı'].unique()
            if len(sporcular) > 0:
                secilen = st.selectbox("Sporcu Seç:", sporcular)
                filtre = df_k[df_k['Öğrenci Adı'] == secilen].sort_values("Tarih")
                fig = px.line(filtre, x="Tarih", y="Kilo", title=f"{secilen} Gelişim Grafiği", markers=True)
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                st.table(farkli_tablo_yap(filtre))
        elif menu == "🥗 Beslenme":
            st.dataframe(veriyi_yukle(BESLENME_DOSYASI, []), use_container_width=True)
        elif menu == "📏 Ölçü Kayıtları":
            st.dataframe(farkli_tablo_yap(veriyi_yukle(OLCU_DOSYASI, [])), use_container_width=True)
        elif menu == "🗑️ Veri Sil":
            st.warning("Veri silme modülü aktif.")

    # --- ÖĞRENCİ PANELİ ---
    else:
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title(f"SELAM {current_user.upper()}!")
            if st.button("Güvenli Çıkış"):
                st.session_state.user = None
                st.rerun()
        
        tab1, tab2, tab3, tab4 = st.tabs(["⚖️ Kilo", "🥗 Beslenme", "📏 Haftalık Ölçü", "📊 Geçmişim"])
        
        with tab1:
            with st.form("k_form", clear_on_submit=True):
                kv = st.number_input("Güncel Kilon (kg)", step=0.1)
                nt = st.text_area("Hocana Mesajın")
                if st.form_submit_button("KAYDET"):
                    df = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), kv, nt]], columns=df.columns)
                    github_a_kaydet(KILO_DOSYASI, pd.concat([df, yeni]))
                    st.success("Kilo kaydedildi!")

        with tab2:
            with st.form("b_form", clear_on_submit=True):
                og = st.text_area("Öğünlerini / Makrolarını buraya yaz")
                if st.form_submit_button("GÖNDER"):
                    df = veriyi_yukle(BESLENME_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Öğünler'])
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), og]], columns=df.columns)
                    github_a_kaydet(BESLENME_DOSYASI, pd.concat([df, yeni]))
                    st.success("Beslenme günlüğün iletildi!")

        with tab3:
            st.subheader("Vücut Ölçülerini Gir")
            with st.form("olcu_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                hkilo = c1.number_input("Kilo (kg)", step=0.1)
                hboy = c2.number_input("Boy (cm)", step=1)
                homuz = c3.number_input("Omuz (cm)", step=0.1)
                hgogus = c1.number_input("Göğüs (cm)", step=0.1)
                hbel = c2.number_input("Bel (cm)", step=0.1)
                hkalca = c3.number_input("Kalça (cm)", step=0.1)
                hust_kol = c1.number_input("Üst Kol (cm)", step=0.1)
                halt_kol = c2.number_input("Alt Kol (cm)", step=0.1)
                hbacak = c3.number_input("Bacak (cm)", step=0.1)
                hbaldir = c1.number_input("Baldır (cm)", step=0.1)
                if st.form_submit_button("ÖLÇÜLERİ MÜHÜRLE 🔥"):
                    df = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', 'Bacak'])
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), hkilo, hboy, homuz, hkalca, hbaldir, hust_kol, halt_kol, hgogus, hbel, hbacak]], columns=df.columns)
                    github_a_kaydet(OLCU_DOSYASI, pd.concat([df, yeni]))
                    st.success("Haftalık ölçülerin Coach Halil'e uçtu!")

        with tab4:
            df_k = veriyi_yukle(KILO_DOSYASI, [])
            df_o = veriyi_yukle(OLCU_DOSYASI, [])
            # Sadece bu öğrencinin verileri
            f_kilo = df_k[df_k['Öğrenci Adı'].str.lower() == current_user.lower()]
            f_olcu = df_o[df_o['Öğrenci Adı'].str.lower() == current_user.lower()]
            
            if not f_kilo.empty:
                fig = px.line(f_kilo.sort_values("Tarih"), x="Tarih", y="Kilo", title="Kilo Grafiğin", markers=True)
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("### ⚖️ Kilo ve Fark Analizi")
                st.table(farkli_tablo_yap(f_kilo))
            
            if not f_olcu.empty:
                st.markdown("---")
                st.markdown("### 📏 Ölçü ve Fark Analizi")
                st.table(farkli_tablo_yap(f_olcu))
            else:
                st.info("Henüz ölçü verisi girilmemiş.")
