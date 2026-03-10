import streamlit as st
import pandas as pd
import os
from datetime import date
import base64
import requests

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="KOÇ HALİL ŞAHAN", layout="wide")

# GitHub Bağlantı Ayarları (Streamlit Secrets'tan çeker)
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
REPO_NAME = st.secrets.get("REPO_NAME")

def github_a_kaydet(dosya_adi, df):
    """Verileri GitHub deposuna kalıcı olarak yazar."""
    if not GITHUB_TOKEN or not REPO_NAME:
        st.warning("GitHub Token veya Repo adı Secrets kısmında eksik! Veri kalıcı kaydedilemedi.")
        return False
    
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{dosya_adi}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Mevcut dosyanın SHA bilgisini al (güncelleme için şart)
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    
    # Veriyi base64 formatına çevir
    content = base64.b64encode(df.to_csv(index=False).encode()).decode()
    
    data = {
        "message": f"Kayıt Güncelleme: {date.today()}",
        "content": content,
        "branch": "main" # Eğer dal adın farklıysa (master vb.) burayı değiştir
    }
    if sha: data["sha"] = sha
    
    response = requests.put(url, headers=headers, json=data)
    return response.status_code in [200, 201]

# --- TASARIM VE ARKAPLAN ---
RESIM_YOLU = "panel_bg.jpg"
LOGO_YOLU = "logo.jpg" 

def set_bg(main_bg):
    if os.path.exists(main_bg):
        with open(main_bg, "rb") as f: data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""<style>
        .stApp {{ background: url("data:image/png;base64,{b64}"); background-size: cover; background-attachment: fixed; }}
        .stApp::before {{ content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.65); z-index: 0; }}
        .main .block-container {{ position: relative; z-index: 10; }}
        h1, h2, h3, p, label {{ color: white !important; text-shadow: 2px 2px 8px rgba(0,0,0,1) !important; }}
        .main-title {{ font-size: 4rem !important; font-weight: 800; text-align: center; color: white; }}
        </style>""", unsafe_allow_html=True)

set_bg(RESIM_YOLU)

# --- VERİ YÜKLEME ---
KILO_DOSYASI = "kilo_verileri.csv"
OLCU_DOSYASI = "haftalik_olculer.csv"

def veriyi_yukle(dosya, kolonlar):
    if os.path.exists(dosya):
        try:
            df = pd.read_csv(dosya)
            df['Tarih'] = pd.to_datetime(df['Tarih']).dt.date
            return df
        except: return pd.DataFrame(columns=kolonlar)
    return pd.DataFrame(columns=kolonlar)

def fark_hesapla(df):
    if df.empty: return df
    df = df.sort_values(by="Tarih")
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        df[f'{col} Fark'] = df[col].diff().fillna(0)
    return df.sort_values(by="Tarih", ascending=False)

# --- KULLANICI GİRİŞİ ---
KULLANICILAR = {"halil": "sahan123", "emrecan": "emrecan2026", "ceyda": "ceyda2026", "umuttatar": "tatar2026"}

if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.8, 1.4, 0.8])
    with col2:
        st.markdown('<p class="main-title">KOÇ HALİL ŞAHAN</p>', unsafe_allow_html=True)
        u = st.text_input("KULLANICI ADI").lower()
        p = st.text_input("ŞİFRE", type="password")
        if st.button("GİRİŞ YAP 🔥", use_container_width=True):
            if u in KULLANICILAR and KULLANICILAR[u] == p:
                st.session_state.user = u
                st.rerun()
            else: st.error("Hatalı Giriş!")
else:
    current_user = st.session_state.user
    
    # --- COACH PANELİ ---
    if current_user == "halil":
        st.sidebar.title("COACH PANELİ 👑")
        menu = st.sidebar.radio("MENÜ", ["📊 Detaylı Analiz", "🗑️ Veri Sil"])
        if st.sidebar.button("Çıkış"):
            st.session_state.user = None
            st.rerun()

        if menu == "📊 Detaylı Analiz":
            df_o = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', 'Bacak'])
            sporcular = df_o['Öğrenci Adı'].unique()
            if len(sporcular) > 0:
                secilen = st.selectbox("Sporcu Seç:", sporcular)
                st.table(fark_hesapla(df_o[df_o['Öğrenci Adı'] == secilen]))
            else: st.info("Henüz veri yok.")

    # --- ÖĞRENCİ PANELİ ---
    else:
        st.sidebar.title(f"SELAM {current_user.upper()}!")
        if st.sidebar.button("Çıkış"):
            st.session_state.user = None
            st.rerun()

        tab1, tab2 = st.tabs(["📏 Ölçü Gir", "📊 Geçmişim"])
        
        with tab1:
            with st.form("olcu_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                k = c1.number_input("Kilo", step=0.1)
                o = c2.number_input("Omuz", step=0.1)
                b = c1.number_input("Bel", step=0.1)
                ka = c2.number_input("Kalça", step=0.1)
                if st.form_submit_button("KAYDET 🔥"):
                    df = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', 'Bacak'])
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), k, 0, o, ka, 0, 0, 0, 0, b, 0]], columns=df.columns)
                    son_df = pd.concat([df, yeni])
                    if github_a_kaydet(OLCU_DOSYASI, son_df):
                        st.success("Veri kalıcı olarak GitHub'a işlendi! Artık silinmez.")
                    else: st.error("GitHub'a yazılamadı! Secrets ayarlarını kontrol et.")

        with tab2:
            df_o = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', 'Bacak'])
            st.table(fark_hesapla(df_o[df_o['Öğrenci Adı'].str.lower() == current_user]))
