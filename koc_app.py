import streamlit as st
import pandas as pd
import os
from datetime import date
import base64

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="HALİL ŞAHAN ELITE", layout="wide")

RESIM_YOLU = "panel_bg.jpg"
LOGO_YOLU = "logo.jpg" 

# --- KULLANICI VERİTABANI (Buraya yeni öğrenciler ekleyebilirsin) ---
# Format: "kullanıcı_adı": "şifre"
KULLANICILAR = {
    "halil": "sahan123",       # Senin girişin (Admin)
    "ahmet": "ahmet2024",      # 1. Öğrenci
    "mehmet": "mehmet55",      # 2. Öğrenci
    "can": "canelite1"         # 3. Öğrenci
}

def set_bg(main_bg):
    if os.path.exists(main_bg):
        with open(main_bg, "rb") as f: data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""<style>.stApp {{ background: url("data:image/png;base64,{b64}"); background-size: cover; background-attachment: fixed; }} .stApp::before {{ content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.50); z-index: 0; }} .main .block-container, [data-testid="stSidebar"] {{ position: relative; z-index: 10; }} h1, h2, h3, p, label {{ color: white !important; text-shadow: 2px 2px 5px rgba(0,0,0,1) !important; }} [data-testid="stSidebar"] [data-testid="stImage"] {{ background-color: rgba(128, 128, 128, 0.3); padding: 15px; border-radius: 20px; border: 2px solid rgba(255, 255, 255, 0.1); }}</style>""", unsafe_allow_html=True)

set_bg(RESIM_YOLU)

VERI_DOSYASI = "ogrenci_veritabani.csv"
def veriyi_yukle():
    if os.path.exists(VERI_DOSYASI):
        df = pd.read_csv(VERI_DOSYASI)
        df['Tarih'] = pd.to_datetime(df['Tarih']).dt.date
        return df
    return pd.DataFrame(columns=['Tarih', 'Öğrenci Adı', 'Kilo', 'Bel (cm)', 'Notlar'])

# --- GİRİŞ SİSTEMİ ---
if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.markdown("<h1 style='text-align: center; font-size: 4em;'>HALİL ŞAHAN</h1>", unsafe_allow_html=True)
    user_input = st.text_input("KULLANICI ADI").lower()
    pw_input = st.text_input("ŞİFRE", type="password")
    if st.button("GİRİŞ YAP 🔥"):
        if user_input in KULLANICILAR and KULLANICILAR[user_input] == pw_input:
            st.session_state.user = user_input
            st.rerun()
        else: st.error("Hatalı Kullanıcı Adı veya Şifre!")
else:
    df = veriyi_yukle()
    current_user = st.session_state.user
    
    # --- COACH (ADMIN) EKRANI ---
    if current_user == "halil":
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title("COACH PANELİ 👑")
            menu = st.radio("MENÜ", ["🏠 Genel Tablo", "📊 Detaylı Analiz"])
            if st.button("Çıkış Yap"):
                st.session_state.user = None
                st.rerun()
        
        if menu == "🏠 Genel Tablo":
            st.title("Tüm Sporcu Verileri")
            st.dataframe(df, use_container_width=True)
        else:
            sporcu = st.selectbox("Sporcu Seç", df['Öğrenci Adı'].unique())
            st.table(df[df['Öğrenci Adı'] == sporcu])

    # --- ÖĞRENCİ (USER) EKRANI ---
    else:
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title(f"SELAM {current_user.upper()}! 🏋️")
            if st.button("Güvenli Çıkış"):
                st.session_state.user = None
                st.rerun()
        
        st.title("KİŞİSEL GELİŞİM PANELİN")
        
        # Sadece bu öğrencinin kendi verilerini göster
        kendi_verisi = df[df['Öğrenci Adı'].str.lower() == current_user]
        
        tab1, tab2 = st.tabs(["📝 Veri Gir", "📊 Geçmişim"])
        
        with tab1:
            with st.form("veri_form"):
                kilo = st.number_input("Kilon (kg)", step=0.1)
                bel = st.number_input("Bel Ölçün (cm)", step=0.1)
                notum = st.text_area("Hocana Notun")
                if st.form_submit_button("KAYDET VE GÖNDER"):
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), kilo, bel, notum]], columns=df.columns)
                    df = pd.concat([df, yeni], ignore_index=True)
                    df.to_csv(VERI_DOSYASI, index=False)
                    st.success("Verilerin Coach Halil'e iletildi!")
        
        with tab2:
            if not kendi_verisi.empty:
                st.table(kendi_verisi.sort_values(by="Tarih", ascending=False))
            else:
                st.info("Henüz geçmiş verin bulunmuyor.")
