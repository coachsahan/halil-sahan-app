import streamlit as st
import pandas as pd
import os
from datetime import date
import base64

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="HALİL ŞAHAN ELITE", layout="wide")

RESIM_YOLU = "panel_bg.jpg"
LOGO_YOLU = "logo.jpg" 

# --- KULLANICI VERİTABANI ---
KULLANICILAR = {
    "halil": "sahan123",
    "ahmet": "ahmet2024",
    "mehmet": "mehmet55",
    "can": "canelite1"
}

def set_bg(main_bg):
    if os.path.exists(main_bg):
        with open(main_bg, "rb") as f: data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""<style>
        .stApp {{ background: url("data:image/png;base64,{b64}"); background-size: cover; background-attachment: fixed; }}
        .stApp::before {{ content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.65); z-index: 0; }}
        .main .block-container {{ position: relative; z-index: 10; }}
        h1, h2, h3, p, label {{ color: white !important; text-shadow: 2px 2px 5px rgba(0,0,0,1) !important; }}
        [data-testid="stSidebar"] [data-testid="stImage"] {{ background-color: rgba(128, 128, 128, 0.3); padding: 15px; border-radius: 20px; }}
        </style>""", unsafe_allow_html=True)

set_bg(RESIM_YOLU)

# --- VERİ DOSYALARI ---
KILO_DOSYASI = "kilo_verileri.csv"
OLCU_DOSYASI = "haftalik_olculer.csv"

def veriyi_yukle(dosya, kolonlar):
    if os.path.exists(dosya):
        df = pd.read_csv(dosya)
        df['Tarih'] = pd.to_datetime(df['Tarih']).dt.date
        return df
    return pd.DataFrame(columns=kolonlar)

# --- GİRİŞ SİSTEMİ (ORTALANMIŞ) ---
if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2: # Ortadaki kolon
        st.markdown("<h1 style='text-align: center;'>HALİL ŞAHAN ELITE</h1>", unsafe_allow_html=True)
        user_input = st.text_input("KULLANICI ADI").lower()
        pw_input = st.text_input("ŞİFRE", type="password")
        if st.button("GİRİŞ YAP 🔥", use_container_width=True):
            if user_input in KULLANICILAR and KULLANICILAR[user_input] == pw_input:
                st.session_state.user = user_input
                st.rerun()
            else: st.error("Hatalı Giriş!")
else:
    current_user = st.session_state.user
    
    # --- ADMIN ---
    if current_user == "halil":
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title("COACH PANELİ 👑")
            menu = st.radio("MENÜ", ["🏠 Günlük Kilolar", "📏 Haftalık Ölçüler"])
            if st.button("Çıkış Yap"):
                st.session_state.user = None
                st.rerun()
        
        if menu == "🏠 Günlük Kilolar":
            st.title("Tüm Sporcu Kiloları")
            df_k = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
            st.dataframe(df_k, use_container_width=True)
        else:
            st.title("Haftalık Vücut Ölçüleri")
            df_o = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', 'Bacak'])
            st.dataframe(df_o, use_container_width=True)

    # --- ÖĞRENCİ ---
    else:
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title(f"SELAM {current_user.upper()}!")
            if st.button("Güvenli Çıkış"):
                st.session_state.user = None
                st.rerun()
        
        st.markdown(f"<h2 style='text-align: center;'>GÜCÜ HİSSET {current_user.upper()}! 🏆</h2>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["⚖️ Günlük Kilo", "📏 Haftalık Ölçü", "📊 Geçmişim"])
        
        with tab1:
            st.subheader("Bugünkü Kilonu Gir")
            with st.form("kilo_form"):
                kilo = st.number_input("Kilo (kg)", step=0.1)
                notum = st.text_area("Hocana Notun")
                if st.form_submit_button("KİLOYU KAYDET"):
                    df_k = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), kilo, notum]], columns=df_k.columns)
                    pd.concat([df_k, yeni]).to_csv(KILO_DOSYASI, index=False)
                    st.success("Kilo iletildi!")
        
        with tab2:
            st.subheader("Haftalık Vücut Ölçülerini Gir")
            with st.form("olcu_form"):
                c1, c2, c3 = st.columns(3)
                boy = c1.number_input("Boy (cm)", step=1)
                omuz = c2.number_input("Omuz (cm)", step=0.1)
                gogus = c3.number_input("Göğüs (cm)", step=0.1)
                bel = c1.number_input("Bel (cm)", step=0.1)
                kalca = c2.number_input("Kalça (cm)", step=0.1)
                ust_kol = c3.number_input("Üst Kol (cm)", step=0.1)
                alt_kol = c1.number_input("Alt Kol (cm)", step=0.1)
                bacak = c2.number_input("Bacak (cm)", step=0.1)
                baldir = c3.number_input("Baldır (cm)", step=0.1)
                
                if st.form_submit_button("ÖLÇÜLERİ GÖNDER 🔥"):
                    df_o = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', 'Bacak'])
                    yeni_o = pd.DataFrame([[date.today(), current_user.capitalize(), boy, omuz, kalca, baldir, ust_kol, alt_kol, gogus, bel, bacak]], columns=df_o.columns)
                    pd.concat([df_o, yeni_o]).to_csv(OLCU_DOSYASI, index=False)
                    st.success("Ölçüler Coach Halil'e iletildi!")

        with tab3:
            df_k = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
            st.write("Son Kilo Kayıtların:")
            st.table(df_k[df_k['Öğrenci Adı'].str.lower() == current_user].tail(5))
