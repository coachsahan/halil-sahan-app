import streamlit as st
import pandas as pd
import os
from datetime import date
import base64

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="KOÇ HALİL ŞAHAN", layout="centered")

RESIM_YOLU = "panel_bg.jpg"
LOGO_YOLU = "logo.jpg" 

# --- KULLANICI VERİTABANI ---
KULLANICILAR = {"halil": "sahan123", "ahmet": "ahmet2024", "mehmet": "mehmet55", "can": "canelite1"}

def set_bg(main_bg):
    if os.path.exists(main_bg):
        with open(main_bg, "rb") as f: data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""<style>
        .stApp {{ 
            background: url("data:image/png;base64,{b64}"); 
            background-size: cover; 
            background-position: center;
            background-attachment: fixed; 
        }}
        /* Karartma katmanı ve Panel Ortalama */
        .stApp::before {{ 
            content: ""; 
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
            background-color: rgba(0, 0, 0, 0.6); 
            z-index: 0; 
        }}
        .main .block-container {{ 
            position: relative; 
            z-index: 10; 
            max-width: 500px !important; /* Paneli daraltıp ortalayan kısım */
            padding-top: 5rem !important;
        }}
        h1, h2, h3, p, label {{ color: white !important; text-shadow: 2px 2px 10px rgba(0,0,0,1) !important; }}
        .main-title {{ font-size: 3.2rem !important; font-weight: 800; text-align: center; color: white; margin-bottom: 0px; line-height: 1.2; }}
        .sub-title {{ font-size: 1.2rem !important; font-style: italic; text-align: center; color: #f0f0f0; margin-top: 5px; margin-bottom: 30px; }}
        div.stButton > button {{ width: 100% !important; }}
        </style>""", unsafe_allow_html=True)

set_bg(RESIM_YOLU)

KILO_DOSYASI = "kilo_verileri.csv"
OLCU_DOSYASI = "haftalik_olculer.csv"

def veriyi_yukle(dosya, kolonlar):
    if os.path.exists(dosya):
        df = pd.read_csv(dosya)
        if not df.empty: df['Tarih'] = pd.to_datetime(df['Tarih']).dt.date
        return df
    return pd.DataFrame(columns=kolonlar)

if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    # GİRİŞ EKRANI (DAR VE ORTALI)
    st.markdown('<p class="main-title">KOÇ HALİL ŞAHAN</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">be wild but stay soft</p>', unsafe_allow_html=True)
    u = st.text_input("KULLANICI ADI").lower()
    p = st.text_input("ŞİFRE", type="password")
    if st.button("GİRİŞ YAP 🔥"):
        if u in KULLANICILAR and KULLANICILAR[u] == p:
            st.session_state.user = u
            st.rerun()
        else: st.error("Hatalı Giriş!")
else:
    # --- BURADAN SONRASI AYNI (ADMİN VE ÖĞRENCİ PANELLERİ) ---
    current_user = st.session_state.user
    if current_user == "halil":
        with st.sidebar:
            st.title("COACH PANELİ 👑")
            menu = st.radio("MENÜ", ["🏠 Genel Tablo", "📊 Detaylı Analiz", "⚖️ Günlük Kilolar", "📏 Haftalık Ölçüler", "🗑️ Veri Sil"])
            if st.button("Çıkış Yap"):
                st.session_state.user = None
                st.rerun()
        
        df_k = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
        df_o = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', 'Bacak'])

        if menu == "🏠 Genel Tablo":
            st.title("Toplu Sporcu Özeti")
            st.dataframe(df_k, use_container_width=True)
        elif menu == "📊 Detaylı Analiz":
            st.title("Gelişim Analizi")
            sporcular = df_k['Öğrenci Adı'].unique()
            if len(sporcular) > 0:
                secilen = st.selectbox("Sporcu seç:", sporcular)
                st.table(df_k[df_k['Öğrenci Adı'] == secilen])
            else: st.warning("Veri yok.")
        elif menu == "🗑️ Veri Sil":
            st.title("Veri Silme Paneli")
            dosya_sec = st.selectbox("Hangi dosyadan silinecek?", ["Günlük Kilolar", "Haftalık Ölçüler"])
            temp_df = df_k if dosya_sec == "Günlük Kilolar" else df_o
            if not temp_df.empty:
                st.write(temp_df)
                idx = st.number_input("Silinecek Satır No:", min_value=0, max_value=len(temp_df)-1, step=1)
                if st.button("SEÇİLEN SATIRI SİL ❌"):
                    new_df = temp_df.drop(temp_df.index[idx])
                    d_adi = KILO_DOSYASI if dosya_sec == "Günlük Kilolar" else OLCU_DOSYASI
                    new_df.to_csv(d_adi, index=False)
                    st.success("Veri silindi!")
                    st.rerun()
    else:
        with st.sidebar:
            st.title(f"SELAM {current_user.upper()}!")
            if st.button("Güvenli Çıkış"):
                st.session_state.user = None
                st.rerun()
        st.markdown(f"<h2 style='text-align: center;'>GÜCÜ HİSSET {current_user.upper()}! 🏆</h2>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["⚖️ Günlük Kilo", "📏 Haftalık Ölçü", "📊 Geçmişim"])
        # ... (Öğrenci formları içeriği burada devam ediyor)
