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
        .stApp::before {{ 
            content: ""; 
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
            background-color: rgba(0, 0, 0, 0.6); 
            z-index: 0; 
        }}
        .main .block-container {{ 
            position: relative; 
            z-index: 10; 
            max-width: 600px !important;
            padding-top: 5rem !important;
        }}
        h1, h2, h3, p, label {{ color: white !important; text-shadow: 2px 2px 10px rgba(0,0,0,1) !important; }}
        .main-title {{ font-size: 3.5rem !important; font-weight: 800; text-align: center; color: white; margin-bottom: 0px; }}
        .sub-title {{ font-size: 1.3rem !important; font-style: italic; text-align: center; color: #f0f0f0; margin-top: 5px; margin-bottom: 30px; }}
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
            menu = st.radio("MENÜ", ["🏠 Genel Tablo", "📊 Analiz", "⚖️ Günlük", "📏 Haftalık", "🗑️ Veri Sil"])
            if st.button("Çıkış Yap"):
                st.session_state.user = None
                st.rerun()
        
        df_k = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
        df_o = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', 'Bacak'])

        if menu == "🗑️ Veri Sil":
            st.title("Veri Silme")
            d_sec = st.selectbox("Dosya:", ["Kilo", "Ölçü"])
            temp = df_k if d_sec == "Kilo" else df_o
            if not temp.empty:
                st.write(temp)
                idx = st.number_input("Satır No:", 0, len(temp)-1, 0)
                if st.button("SİL"):
                    temp = temp.drop(temp.index[idx])
                    temp.to_csv(KILO_DOSYASI if d_sec == "Kilo" else OLCU_DOSYASI, index=False)
                    st.success("Silindi! Yenileyin.")
            else: st.info("Veri yok.")
        elif menu == "🏠 Genel Tablo": st.dataframe(df_k)
        elif menu == "📊 Analiz":
            sec = st.selectbox("Seç:", df_k['Öğrenci Adı'].unique())
            st.table(df_k[df_k['Öğrenci Adı'] == sec])
        elif menu == "⚖️ Günlük": st.dataframe(df_k)
        elif menu == "📏 Haftalık": st.dataframe(df_o)

    else:
        with st.sidebar:
            if st.button("Çıkış"):
                st.session_state.user = None
                st.rerun()
        st.markdown(f"<h2 style='text-align: center;'>SELAM {current_user.upper()}! 🏆</h2>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["⚖️ Kilo", "📏 Ölçü", "📊 Geçmiş"])
        with tab1:
            with st.form("k"):
                kv = st.number_input("Kilo", step=0.1)
                nt = st.text_area("Not")
                if st.form_submit_button("KAYDET"):
                    df = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
                    y = pd.DataFrame([[date.today(), current_user.capitalize(), kv, nt]], columns=df.columns)
                    pd.concat([df, y]).to_csv(KILO_DOSYASI, index=False)
                    st.success("Gitti!")
        with tab2:
            with st.form("o"):
                c1, c2 = st.columns(2)
                ok = c1.number_input("Kilo ", step=0.1)
                ob = c2.number_input("Boy ", step=1)
                oom = c1.number_input("Omuz ", step=0.1)
                obel = c2.number_input("Bel ", step=0.1)
                if st.form_submit_button("ÖLÇÜ GÖNDER"):
                    df = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', 'Bacak'])
                    y = pd.DataFrame([[date.today(), current_user.capitalize(), ok, ob, oom, 0, 0, 0, 0, 0, obel, 0]], columns=df.columns)
                    pd.concat([df, y]).to_csv(OLCU_DOSYASI, index=False)
                    st.success("Ölçü gitti!")
        with tab3:
            st.table(veriyi_yukle(KILO_DOSYASI, []).tail(5))
