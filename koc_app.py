import streamlit as st
import pandas as pd
import os
from datetime import date
import base64

# --- AYARLAR ---
st.set_page_config(page_title="HALİL ŞAHAN ELITE", layout="wide")

# Resim yolları (GitHub'daki isimlerle aynı olmalı)
RESIM_YOLU = "panel_bg.jpg"
LOGO_YOLU = "logo.jpg"

# Arka Plan Fonksiyonu
def set_bg(main_bg):
    if os.path.exists(main_bg):
        with open(main_bg, "rb") as f: data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""<style>.stApp {{ background: url("data:image/png;base64,{b64}"); background-size: cover; background-attachment: fixed; }} .stApp::before {{ content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.75); z-index: -1; }}</style>""", unsafe_allow_html=True)

set_bg(RESIM_YOLU)

# Veri Yükleme
VERI_DOSYASI = "ogrenci_veritabani.csv"
def veriyi_yukle():
    if os.path.exists(VERI_DOSYASI): return pd.read_csv(VERI_DOSYASI)
    return pd.DataFrame(columns=['Tarih', 'Öğrenci Adı', 'Kilo', 'Bel (cm)', 'Notlar'])

# --- GİRİŞ SİSTEMİ ---
if 'role' not in st.session_state: st.session_state.role = None

if st.session_state.role is None:
    st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>HALİL ŞAHAN ELITE</h1>", unsafe_allow_html=True)
    user = st.text_input("KULLANICI ADI").lower()
    pw = st.text_input("ŞİFRE", type="password")
    
    if st.button("GİRİŞ YAP 🔥"):
        if user == "halil" and pw == "sahan123":
            st.session_state.role = "admin"
            st.rerun()
        elif user == "sporcu" and pw == "elite2024":
            st.session_state.role = "user"
            st.rerun()
        else:
            st.error("Hatalı Giriş!")

else:
    df = veriyi_yukle()
    
    # --- ADMIN PANELİ (SADECE SEN GÖRÜRSÜN) ---
    if st.session_state.role == "admin":
        st.sidebar.title("COACH PANELİ 👑")
        menu = ["🏠 Genel Tablo", "📈 Gelişim Analizi", "📝 Veri Ekle"]
        choice = st.sidebar.selectbox("Menü", menu)
        
        if choice == "🏠 Genel Tablo":
            st.title("Tüm Sporcular")
            st.dataframe(df, use_container_width=True)
            
        elif choice == "📈 Gelişim Analizi":
            isim = st.selectbox("Sporcu Seç", df['Öğrenci Adı'].unique())
            st.table(df[df['Öğrenci Adı'] == isim])

    # --- ÖĞRENCİ PANELİ (SADECE VERİ GİRER, BAŞKASINI GÖRMEZ) ---
    elif st.session_state.role == "user":
        st.sidebar.title("SPORCU GİRİŞİ 🏋️")
        st.title("Günlük Veri Girişi")
        with st.form("ogrenci_form"):
            ad = st.text_input("Adınız Soyadınız")
            kilo = st.number_input("Bugünkü Kilonuz", step=0.1)
            bel = st.number_input("Bel Ölçüsü (cm)", step=0.1)
            notum = st.text_area("Coach'a Notun")
            if st.form_submit_button("VERİLERİ GÖNDER 🔥"):
                yeni = pd.DataFrame([[date.today(), ad, kilo, bel, notum]], columns=df.columns)
                df = pd.concat([df, yeni], ignore_index=True)
                df.to_csv(VERI_DOSYASI, index=False)
                st.success("Verilerin başarıyla Coach Halil'e iletildi!")

    if st.sidebar.button("Çıkış Yap"):
        st.session_state.role = None
        st.rerun()
