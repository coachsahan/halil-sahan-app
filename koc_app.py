import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
from PIL import Image
import base64

# --- AYARLAR ---
st.set_page_config(page_title="HALİL ŞAHAN ELITE", layout="wide", page_icon="⚡")

# ❗ YOLLARI GÜNCELLEMEYİ UNUTMA ❗
RESIM_YOLU = "panel_bg.jpg"
LOGO_YOLU = "logo.jpg"

# --- ARKA PLAN VE TASARIM ---
def set_bg(main_bg):
    if os.path.exists(main_bg):
        with open(main_bg, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""
            <style>
            .stApp {{ background: url("data:image/png;base64,{b64}"); background-size: cover; background-attachment: fixed; }}
            .stApp::before {{ content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.75); z-index: -1; }}
            h1, h2, h3 {{ color: #ff4b4b !important; text-shadow: 2px 2px 4px black; font-family: 'Impact'; }}
            .stDataFrame {{ background: rgba(255, 255, 255, 0.05); border-radius: 10px; }}
            </style>
            """, unsafe_allow_html=True)

set_bg(RESIM_YOLU)

# --- VERİ YÖNETİMİ ---
VERI_DOSYASI = "ogrenci_veritabani.csv"
def veriyi_yukle():
    if os.path.exists(VERI_DOSYASI): 
        df = pd.read_csv(VERI_DOSYASI)
        df['Tarih'] = pd.to_datetime(df['Tarih'])
        return df
    return pd.DataFrame(columns=['Tarih', 'Öğrenci Adı', 'Kilo', 'Bel (cm)', 'Notlar'])

# --- GİRİŞ SİSTEMİ ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; font-size: 4em;'>HALİL ŞAHAN</h1>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        user = st.text_input("👤 KULLANICI ADI")
        pw = st.text_input("🔑 ŞİFRE", type="password")
        if st.button("GİRİŞ YAP 🔥"):
            if user == "halil" and pw == "sahan123":
                st.session_state.logged_in = True
                st.rerun()
else:
    df = veriyi_yukle()
    with st.sidebar:
        if os.path.exists(LOGO_YOLU): st.image(Image.open(LOGO_YOLU))
        st.markdown("<h2 style='text-align:center;'>COACH HALİL</h2>", unsafe_allow_html=True)
        menu = ["🏠 ANA SAYFA", "📝 VERİ GİRİŞİ", "📊 HAFTALIK ANALİZ"]
        secim = st.selectbox("Menü", menu)
        if st.button("Çıkış"):
            st.session_state.logged_in = False
            st.rerun()

    if secim == "🏠 ANA SAYFA":
        st.title("GÜCÜ HİSSET! 🏆")
        st.write("Son girilen öğrenci verileri:")
        st.dataframe(df.tail(10), use_container_width=True) # Son 10 veri tablosu

    elif secim == "📝 VERİ GİRİŞİ":
        st.header("YENİ SPORCU VERİSİ")
        with st.form("veri_formu"):
            ad = st.text_input("Öğrenci Adı")
            kilo = st.number_input("Kilo (kg)", step=0.1)
            bel = st.number_input("Bel (cm)", step=0.1)
            notlar = st.text_area("Coach Notu")
            if st.form_submit_button("KAYDET"):
                yeni = pd.DataFrame([[date.today(), ad, kilo, bel, notlar]], columns=df.columns)
                df = pd.concat([df, yeni], ignore_index=True)
                df.to_csv(VERI_DOSYASI, index=False)
                st.success("Veri başarıyla tabloya eklendi!")

    elif secim == "📊 HAFTALIK ANALİZ":
        st.header("ÖĞRENCİ GELİŞİM TAKİBİ")
        isimler = df['Öğrenci Adı'].unique()
        if len(isimler) > 0:
            secilen_ogrenci = st.selectbox("Öğrenci Seç", isimler)
            filtre = df[df['Ö. Adı'] == secilen_ogrenci] # Basit tablo gösterimi
            st.subheader(f"{secilen_ogrenci} - Değişim Tablosu")
            st.table(filtre) # Tüm geçmişini tablo olarak döküyoruz
