import streamlit as st
import pandas as pd
import os
from datetime import date
import base64

# --- AYARLAR ---
st.set_page_config(page_title="HALİL ŞAHAN ELITE", layout="wide")

# GitHub'daki dosya isimlerin neyse buraya tam olarak onu yaz!
RESIM_YOLU = "panel_bg.jpg"
LOGO_YOLU = "logo.jpg" 

# Arka Plan ve Katman Ayarı (Yazıların Görünmesi İçin)
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
            /* Arka planı yazılardan ayırmak için karartma katmanı */
            .stApp::before {{
                content: "";
                position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background-color: rgba(0, 0, 0, 0.75); 
                z-index: 0;
            }}
            /* Tüm içeriği en ön katmana (layer) taşıyoruz */
            .main .block-container {{
                position: relative;
                z-index: 10;
            }}
            h1, h2, h3, p, span, label {{
                color: white !important;
                text-shadow: 2px 2px 4px rgba(0,0,0,1) !important;
            }}
            </style>
            """, unsafe_allow_html=True)

set_bg(RESIM_YOLU)

# Veri Yükleme
VERI_DOSYASI = "ogrenci_veritabani.csv"
def veriyi_yukle():
    if os.path.exists(VERI_DOSYASI): return pd.read_csv(VERI_DOSYASI)
    return pd.DataFrame(columns=['Tarih', 'Öğrenci Adı', 'Kilo', 'Bel (cm)', 'Notlar'])

# --- GİRİŞ SİSTEMİ ---
if 'role' not in st.session_state: st.session_state.role = None

if st.session_state.role is None:
    st.markdown("<h1 style='text-align: center; font-size: 3.5em;'>HALİL ŞAHAN</h1>", unsafe_allow_html=True)
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
    if st.session_state.role == "admin":
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title("COACH PANELİ 👑")
            if st.button("Çıkış Yap"):
                st.session_state.role = None
                st.rerun()
        st.title("Tüm Sporcular")
        st.dataframe(df, use_container_width=True)
    
    elif st.session_state.role == "user":
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title("SPORCU GİRİŞİ 🏋️")
            if st.button("Çıkış"):
                st.session_state.role = None
                st.rerun()
        st.title("GÜCÜ HİSSET! 🏆")
        with st.form("ogrenci_form"):
            ad = st.text_input("Ad Soyad")
            kilo = st.number_input("Kilo (kg)", step=0.1)
            bel = st.number_input("Bel (cm)", step=0.1)
            if st.form_submit_button("VERİLERİ GÖNDER 🔥"):
                yeni = pd.DataFrame([[date.today(), ad, kilo, bel, ""]], columns=df.columns)
                df = pd.concat([df, yeni], ignore_index=True)
                df.to_csv(VERI_DOSYASI, index=False)
                st.success("Başarıyla iletildi!")
