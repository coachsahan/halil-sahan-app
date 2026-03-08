import streamlit as st
import pandas as pd
import os
from datetime import date
import base64

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="KOÇ HALİL ŞAHAN", layout="wide")

# RESİM DOSYA ADINI BURADAN KONTROL ET (GitHub'dakiyle aynı olmalı)
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
            background-attachment: fixed; 
        }}
        .stApp::before {{ 
            content: ""; 
            position: absolute; 
            top: 0; 
            left: 0; 
            width: 100%; 
            height: 100%; 
            background-color: rgba(0, 0, 0, 0.7); 
            z-index: 0; 
        }}
        .main .block-container {{ position: relative; z-index: 10; }}
        h1, h2, h3, p, label {{ color: white !important; text-shadow: 2px 2px 10px rgba(0,0,0,1) !important; }}
        .main-title {{ font-size: 4.5rem !important; font-weight: 800; text-align: center; color: white; margin-bottom: 0px; }}
        .sub-title {{ font-size: 1.5rem !important; font-style: italic; text-align: center; color: #f0f0f0; margin-top: -10px; margin-bottom: 20px; }}
        </style>""", unsafe_allow_html=True)

set_bg(RESIM_YOLU)

KILO_DOSYASI = "kilo_verileri.csv"
OLCU_DOSYASI = "haftalik_olculer.csv"

def veriyi_yukle(dosya, kolonlar):
    if os.path.exists(dosya):
        df = pd.read_csv(dosya)
        if not df.empty:
            df['Tarih'] = pd.to_datetime(df['Tarih']).dt.date
        return df
    return pd.DataFrame(columns=kolonlar)

if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.5, 2, 0.5])
    with col2:
        st.markdown('<p class="main-title">KOÇ HALİL ŞAHAN</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">be wild but stay soft</p>', unsafe_allow_html=True)
        u = st.text_input("KULLANICI ADI").lower()
        p = st.text_input("ŞİFRE", type="password")
        if st.button("GİRİŞ YAP 🔥", use_container_width=True):
            if u in KULLANICILAR and KULLANICILAR[u] == p:
                st.session_state.user = u
                st.rerun()
            else: st.error("Hatalı Giriş!")
else:
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
        elif menu == "⚖️ Günlük Kilolar":
            st.title("Kilo Kayıtları")
            st.dataframe(df_k, use_container_width=True)
        elif menu == "📏 Haftalık Ölçüler":
            st.title("Vücut Ölçümleri")
            st.dataframe(df_o, use_container_width=True)
        elif menu == "🗑️ Veri Sil":
            st.title("Veri Silme Paneli")
            dosya_sec = st.selectbox("Hangi dosyadan silinecek?", ["Günlük Kilolar", "Haftalık Ölçüler"])
            temp_df = df_k if dosya_sec == "Günlük Kilolar" else df_o
            if not temp_df.empty:
                st.write(temp_df)
                silinecek_index = st.number_input("Silinecek Satır No:", min_value=0, max_value=len(temp_df)-1, step=1)
                if st.button("SEÇİLEN SATIRI SİL ❌"):
                    new_df = temp_df.drop(temp_df.index[silinecek_index])
                    dosya_adi = KILO_DOSYASI if dosya_sec == "Günlük Kilolar" else OLCU_DOSYASI
                    new_df.to_csv(dosya_adi, index=False)
                    st.success("Veri silindi!")
                    st.rerun()
            else: st.info("Silinecek veri yok.")

    else:
        # ÖĞRENCİ PANELİ
        with st.sidebar:
            st.title(f"SELAM {current_user.upper()}!")
            if st.button("Güvenli Çıkış"):
                st.session_state.user = None
                st.rerun()
        st.markdown(f"<h2 style='text-align: center;'>GÜCÜ HİSSET {current_user.upper()}! 🏆</h2>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["⚖️ Günlük Kilo", "📏 Haftalık Ölçü", "📊 Geçmişim"])
        with tab1:
            with st.form("kilo_form"):
                k_val = st.number_input("Kilo (kg)", step=0.1)
                not_val = st.text_area("Hocana Notun")
                if st.form_submit_button("KİLOYU KAYDET"):
                    df_k = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), k_val, not_val]], columns=df_k.columns)
                    pd.concat([df_k, yeni]).to_csv(KILO_DOSYASI, index=False)
                    st.success("Kilo iletildi!")
        with tab2:
            with st.form("olcu_form"):
                c1, c2, c3 = st.columns(3)
                hk = c1.number_input("Güncel Kilo (kg)", step=0.1)
                hb = c2.number_input("Boy (cm)", step=1)
                ho = c3.number_input("Omuz (cm)", step=0.1)
                hg = c1.number_input("Göğüs (cm)", step=0.1)
                hb_ = c2.number_input("Bel (cm)", step=0.1)
                hka = c3.number_input("Kalça (cm)", step=0.1)
                if st.form_submit_button("ÖLÇÜLERİ GÖNDER 🔥"):
                    df_o = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', 'Bacak'])
                    yeni_o = pd.DataFrame([[date.today(), current_user.capitalize(), hk, hb, ho, hka, 0, 0, 0, hg, hb_, 0]], columns=df_o.columns)
                    pd.concat([df_o, yeni_o]).to_csv(OLCU_DOSYASI, index=False)
                    st.success("Ölçüler iletildi!")
        with tab3:
            df_k = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
            st.table(df_k[df_k['Öğrenci Adı'].str.lower() == current_user].tail(10))
