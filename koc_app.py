import streamlit as st
import pandas as pd
import os
from datetime import date
from PIL import Image
import base64

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="HALİL ŞAHAN ELITE", layout="wide")

# GitHub'daki dosya isimlerinle birebir aynı olmalı!
RESIM_YOLU = "panel_bg.jpg"
LOGO_YOLU = "logo.jpg" 

# --- TASARIM VE ARKA PLAN ---
def set_bg(main_bg):
    if os.path.exists(main_bg):
        with open(main_bg, "rb") as f: data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""
            <style>
            .stApp {{
                background: url("data:image/png;base64,{b64}");
                background-size: cover;
                background-attachment: fixed;
            }}
            /* Arka planı aydınlatmak için perdeyi şeffaflaştırdık */
            .stApp::before {{
                content: "";
                position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background-color: rgba(0, 0, 0, 0.45); 
                z-index: 0;
            }}
            /* Yazıları ve butonları en ön katmana çekiyoruz */
            .main .block-container, [data-testid="stSidebar"] {{
                position: relative;
                z-index: 10;
            }}
            h1, h2, h3, p, label {{
                color: white !important;
                text-shadow: 2px 2px 5px rgba(0,0,0,1) !important;
            }}
            /* Senin fotoğrafının arkasındaki gri çerçeve */
            [data-testid="stSidebar"] [data-testid="stImage"] {{
                background-color: rgba(128, 128, 128, 0.3);
                padding: 15px;
                border-radius: 20px;
                border: 2px solid rgba(255, 255, 255, 0.1);
            }}
            </style>
            """, unsafe_allow_html=True)

set_bg(RESIM_YOLU)

# --- VERİ YÜKLEME ---
VERI_DOSYASI = "ogrenci_veritabani.csv"
def veriyi_yukle():
    if os.path.exists(VERI_DOSYASI): return pd.read_csv(VERI_DOSYASI)
    return pd.DataFrame(columns=['Tarih', 'Öğrenci Adı', 'Kilo', 'Bel (cm)', 'Notlar'])

# --- GİRİŞ SİSTEMİ ---
if 'role' not in st.session_state: st.session_state.role = None

if st.session_state.role is None:
    st.markdown("<h1 style='text-align: center; font-size: 4em;'>HALİL ŞAHAN</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        user = st.text_input("KULLANICI ADI").lower()
        pw = st.text_input("ŞİFRE", type="password")
        if st.button("GÜCÜ HİSSET VE GİRİŞ YAP 🔥"):
            if user == "halil" and pw == "sahan123":
                st.session_state.role = "admin"
                st.rerun()
            elif user == "sporcu" and pw == "elite2024":
                st.session_state.role = "user"
                st.rerun()
            else: st.error("Hatalı Giriş!")
else:
    df = veriyi_yukle()
    # --- ADMIN (SENİN PANELİN) ---
    if st.session_state.role == "admin":
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.markdown("<h2 style='text-align:center;'>COACH PANELİ 👑</h2>", unsafe_allow_html=True)
            if st.button("Çıkış Yap"):
                st.session_state.role = None
                st.rerun()
        st.title("Tüm Sporcular")
        st.dataframe(df, use_container_width=True)
    
    # --- USER (ÖĞRENCİ PANELİ) ---
    elif st.session_state.role == "user":
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.markdown("<h2 style='text-align:center;'>ELITE SPORCU 🏋️</h2>", unsafe_allow_html=True)
            if st.button("Çıkış"):
                st.session_state.role = None
                st.rerun()
        st.title("GÜCÜ HİSSET! 🏆")
        with st.form("ogrenci_form"):
            ad = st.text_input("Ad Soyad")
            kilo = st.number_input("Bugünkü Kilon (kg)", step=0.1)
            bel = st.number_input("Bel Ölçün (cm)", step=0.1)
            if st.form_submit_button("VERİLERİ COACH'A GÖNDER 🔥"):
                yeni = pd.DataFrame([[date.today(), ad, kilo, bel, ""]], columns=df.columns)
                df = pd.concat([df, yeni], ignore_index=True)
                df.to_csv(VERI_DOSYASI, index=False)
                st.success("Başarıyla iletildi!")
