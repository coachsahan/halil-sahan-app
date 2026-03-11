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
    try:
        r = requests.get(url, headers=headers)
        sha = r.json().get('sha') if r.status_code == 200 else None
        content = base64.b64encode(df.to_csv(index=False).encode()).decode()
        data = {"message": f"Veri Güncelleme: {date.today()}", "content": content}
        if sha: data["sha"] = sha
        res = requests.put(url, headers=headers, json=data)
        return res.status_code in [200, 201]
    except: return False

# --- TASARIM ---
RESIM_YOLU = "panel_bg.jpg"
def set_bg(main_bg):
    if os.path.exists(main_bg):
        with open(main_bg, "rb") as f: data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""<style>
        .stApp {{ background: url("data:image/png;base64,{b64}"); background-size: cover; background-attachment: fixed; }}
        .stApp::before {{ content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.75); z-index: 0; }}
        .main .block-container {{ position: relative; z-index: 10; }}
        h1, h2, h3, p, label {{ color: white !important; text-shadow: 2px 2px 10px rgba(0,0,0,1) !important; }}
        .main-title {{ font-size: 3.5rem !important; font-weight: 800; text-align: center; color: white; }}
        </style>""", unsafe_allow_html=True)

set_bg(RESIM_YOLU)

# --- VERİ DOSYALARI ---
KILO_DOSYASI = "kilo_verileri.csv"
OLCU_DOSYASI = "haftalik_olculer.csv"
KILO_KOLON = ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not']
OLCU_KOLON = ['Tarih', 'Öğrenci Adı', 'Kilo', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', 'Bacak']

def veriyi_yukle(dosya, varsayilan_kolonlar):
    if not os.path.exists(dosya):
        return pd.DataFrame(columns=varsayilan_kolonlar)
    try:
        df = pd.read_csv(dosya)
        if df.empty: return pd.DataFrame(columns=varsayilan_kolonlar)
        df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce').dt.date
        return df
    except: return pd.DataFrame(columns=varsayilan_kolonlar)

def fark_motoru(df):
    if df.empty or len(df) < 1: return df
    df_sorted = df.copy().sort_values(by="Tarih")
    numeric_cols = df_sorted.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        df_sorted[f'{col} (Fark)'] = df_sorted[col].diff().fillna(0.0)
    return df_sorted.sort_values(by="Tarih", ascending=False)

# --- KULLANICI SİSTEMİ ---
KULLANICILAR = {"halil": "sahan123", "emrecan": "emrecan2026", "ceyda": "ceyda2026", "umuttatar": "tatar2026"}
if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.8, 1.4, 0.8])
    with col2:
        st.markdown('<p class="main-title">KOÇ HALİL ŞAHAN</p>', unsafe_allow_html=True)
        u_in = st.text_input("KULLANICI ADI").lower().strip()
        p_in = st.text_input("ŞİFRE", type="password")
        if st.button("SİSTEME GİR 🔥", use_container_width=True):
            if u_in in KULLANICILAR and KULLANICILAR[u_in] == p_in:
                st.session_state.user = u_in
                st.rerun()
            else: st.error("Hatalı Giriş!")
else:
    current_user = st.session_state.user
    if current_user == "halil":
        st.sidebar.title("COACH PANELİ 👑")
        menu = st.sidebar.radio("MENÜ", ["📊 Analiz", "⚖️ Kilolar", "📏 Ölçüler", "🗑️ Sil"])
        if st.sidebar.button("Çıkış Yap"):
            st.session_state.user = None
            st.rerun()

        if menu == "⚖️ Kilolar":
            df = veriyi_yukle(KILO_DOSYASI, KILO_KOLON)
            st.dataframe(fark_motoru(df), use_container_width=True)
        elif menu == "📊 Analiz":
            df_k = veriyi_yukle(KILO_DOSYASI, KILO_KOLON)
            if not df_k.empty:
                s = st.selectbox("Sporcu Seç:", df_k['Öğrenci Adı'].unique())
                fig = px.line(df_k[df_k['Öğrenci Adı']==s], x="Tarih", y="Kilo", markers=True)
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("Henüz veri yok.")
    else:
        st.sidebar.title(f"SELAM {current_user.upper()}")
        tab1, tab2, tab3 = st.tabs(["⚖️ Kilo Bildir", "📏 Ölçü Bildir", "📊 Geçmişim"])
        with tab1:
            with st.form("k"):
                kv = st.number_input("Kilo (kg)", step=0.1)
                if st.form_submit_button("KAYDET"):
                    df = veriyi_yukle(KILO_DOSYASI, KILO_KOLON)
                    yeni = pd.DataFrame([[date.today(), current_user, kv, ""]], columns=KILO_KOLON)
                    github_a_kaydet(KILO_DOSYASI, pd.concat([df, yeni]))
                    st.success("Kaydedildi!")
        with tab3:
            df_k = veriyi_yukle(KILO_DOSYASI, KILO_KOLON)
            f_k = df_k[df_k['Öğrenci Adı'].astype(str).str.lower() == current_user.lower()]
            if not f_k.empty: st.table(fark_motoru(f_k))
