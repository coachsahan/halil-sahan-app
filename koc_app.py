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
    if not GITHUB_TOKEN or not REPO_NAME: return False
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{dosya_adi}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    content = base64.b64encode(df.to_csv(index=False).encode()).decode()
    data = {"message": f"Veri Güncelleme: {date.today()}", "content": content}
    if sha: data["sha"] = sha
    res = requests.put(url, headers=headers, json=data)
    return res.status_code in [200, 201]

# --- TASARIM ---
RESIM_YOLU = "panel_bg.jpg"
LOGO_YOLU = "logo.jpg" 

def set_bg(main_bg):
    if os.path.exists(main_bg):
        with open(main_bg, "rb") as f: data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""<style>
        .stApp {{ background: url("data:image/png;base64,{b64}"); background-size: cover; background-attachment: fixed; }}
        .stApp::before {{ content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.75); z-index: 0; }}
        .main .block-container {{ position: relative; z-index: 10; }}
        h1, h2, h3, p, label {{ color: white !important; text-shadow: 2px 2px 10px rgba(0,0,0,1) !important; }}
        .main-title {{ font-size: 4rem !important; font-weight: 800; text-align: center; color: white; }}
        </style>""", unsafe_allow_html=True)

set_bg(RESIM_YOLU)

# --- VERİ DOSYALARI ---
KILO_DOSYASI = "kilo_verileri.csv"
OLCU_DOSYASI = "haftalik_olculer.csv"
BESLENME_DOSYASI = "beslenme_verileri.csv"

# KOLON İSİMLERİNİ SABİTLEDİK (Harf hatası olmasın diye)
KILO_KOLON = ['Tarih', 'Ogrenci', 'Kilo', 'Not']
OLCU_KOLON = ['Tarih', 'Ogrenci', 'Kilo', 'Boy', 'Omuz', 'Kalca', 'Baldir', 'UstKol', 'AltKol', 'Gogus', 'Bel', 'Bacak']
BESLENME_KOLON = ['Tarih', 'Ogrenci', 'Ogunler']

def veriyi_yukle(dosya, varsayilan_kolonlar):
    if not os.path.exists(dosya):
        return pd.DataFrame(columns=varsayilan_kolonlar)
    try:
        df = pd.read_csv(dosya)
        if df.empty: return pd.DataFrame(columns=varsayilan_kolonlar)
        # Sütunları temizle ve tarih ayarla
        df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce').dt.date
        return df
    except:
        return pd.DataFrame(columns=varsayilan_kolonlar)

def fark_motoru(df):
    if df.empty or len(df) < 1: return df
    df_sorted = df.copy().sort_values(by="Tarih")
    # Sayısal olan her şeyin farkını al
    numeric_cols = df_sorted.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        df_sorted[f'{col} (Fark)'] = df_sorted[col].diff().fillna(0.0)
    return df_sorted.sort_values(by="Tarih", ascending=False)

# --- KULLANICI SİSTEMİ ---
KULLANICILAR = {"halil": "sahan123", "emrecan": "emrecan2026", "ceyda": "ceyda2026", "umuttatar": "tatar2026"}
if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.8, 1.4
