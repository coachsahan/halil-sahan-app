import streamlit as st
import pandas as pd
import os
from datetime import date
import base64

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="KOÇ HALİL ŞAHAN", layout="wide")

RESIM_YOLU = "panel_bg.jpg"
LOGO_YOLU = "logo.jpg" 

# --- KULLANICI VERİTABANI ---
KULLANICILAR = {
    "halil": "sahan123",
    "emrecan": "emrecan2026",
    "ceyda": "ceyda2026",
    "umut": "tatar2026"
}

def set_bg(main_bg):
    if os.path.exists(main_bg):
        with open(main_bg, "rb") as f: data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""<style>
        .stApp {{ background: url("data:image/png;base64,{b64}"); background-size: cover; background-attachment: fixed; }}
        .stApp::before {{ content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.65); z-index: 0; }}
        .main .block-container {{ position: relative; z-index: 10; }}
        h1, h2, h3, p, label {{ color: white !important; text-shadow: 2px 2px 8px rgba(0,0,0,1) !important; }}
        [data-testid="stSidebar"] [data-testid="stImage"] {{ background-color: rgba(128, 128, 128, 0.3); padding: 15px; border-radius: 20px; }}
        .main-title {{ font-size: 4.5rem !important; font-weight: 800; margin-bottom: 0px; text-align: center; color: white; }}
        .sub-title {{ font-size: 1.5rem !important; font-style: italic; font-weight: 300; margin-top: -10px; margin-bottom: 30px; text-align: center; color: #f0f0f0; opacity: 0.9; }}
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
    col1, col2, col3 = st.columns([0.8, 1.4, 0.8])
    with col2:
        st.markdown('<p class="main-title">KOÇ HALİL ŞAHAN</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">be wild but stay soft</p>', unsafe_allow_html=True)
        user_input = st.text_input("KULLANICI ADI").lower()
        pw_input = st.text_input("ŞİFRE", type="password")
        if st.button("GİRİŞ YAP 🔥", use_container_width=True):
            if user_input in KULLANICILAR and KULLANICILAR[user_input] == pw_input:
                st.session_state.user = user_input
                st.rerun()
            else: st.error("Hatalı Giriş!")
else:
    current_user = st.session_state.user
    if current_user == "halil":
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
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
                st.subheader(f"{secilen} - Günlük Kilo Takibi")
                st.table(df_k[df_k['Öğrenci Adı'] == secilen].sort_values(by="Tarih", ascending=False))
                filtre_o = df_o[df_o['Öğrenci Adı'] == secilen].sort_values(by="Tarih", ascending=False)
                if not filtre_o.empty:
                    st.subheader(f"{secilen} - Haftalık Ölçü Geçmişi")
                    st.table(filtre_o)
            else: st.warning("Veri yok.")
        elif menu == "🗑️ Veri Sil":
            st.title("Veri Silme Paneli")
            d_sec = st.selectbox("Hangi tablo?", ["Kilolar", "Ölçüler"])
            temp = df_k if d_sec == "Kilolar" else df_o
            if not temp.empty:
                st.write(temp)
                idx = st.number_input("Silinecek Satır No:", min_value=0, max_value=len(temp)-1, step=1)
                if st.button("SEÇİLENİ SİL ❌"):
                    new_df = temp.drop(temp.index[idx])
                    new_df.to_csv(KILO_DOSYASI if d_sec == "Kilolar" else OLCU_DOSYASI, index=False)
                    st.success("Silindi! Sayfayı yenileyin.")
            else: st.info("Silinecek veri yok.")
        else: st.dataframe(df_k if menu == "⚖️ Günlük Kilolar" else df_o)

    else:
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title(f"SELAM {current_user.upper()}!")
            if st.button("Çıkış"):
                st.session_state.user = None
                st.rerun()
        
        st.markdown(f"<h2 style='text-align: center;'>GÜCÜ HİSSET {current_user.upper()}! 🏆</h2>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["⚖️ Günlük Kilo", "📏 Haftalık Ölçü", "📊 Geçmişim"])
        
        with tab1:
            with st.form("kilo_form", clear_on_submit=True):
                kilo_v = st.number_input("Bugünkü Kilon (kg)", step=0.1)
                notum = st.text_area("Hocana Notun")
                if st.form_submit_button("KİLOYU KAYDET"):
                    df = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), kilo_v, notum]], columns=df.columns)
                    pd.concat([df, yeni]).to_csv(KILO_DOSYASI, index=False)
                    st.success("İletildi!")
        with tab2:
            st.subheader("Haftalık Detaylı Ölçüm Formu")
            with st.form("olcu_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                hkilo = c1.number_input("Güncel Kilo (kg)", step=0.1)
                hboy = c2.number_input("Boy (cm)", step=1)
                homuz = c3.number_input("Omuz (cm)", step=0.1)
                hgogus = c1.number_input("Göğüs (cm)", step=0.1)
                hbel = c2.number_input("Bel (cm)", step=0.1)
                hkalca = c3.number_input("Kalça (cm)", step=0.1)
                if st.form_submit_button("ÖLÇÜLERİ GÖNDER 🔥"):
                    df = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', 'Bacak'])
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), hkilo, hboy, homuz, hkalca, 0, 0, 0, hgogus, hbel, 0]], columns=df.columns)
                    pd.concat([df, yeni]).to_csv(OLCU_DOSYASI, index=False)
                    st.success("Haftalık veriler iletildi!")
        with tab3:
            df_k = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
            df_o = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', 'Bacak'])
            st.markdown("### ⚖️ Günlük Kilo Geçmişin")
            st.table(df_k[df_k['Öğrenci Adı'].str.lower() == current_user].tail(10))
            st.markdown("---")
            st.markdown("### 📏 Haftalık Ölçü Geçmişin")
            st.table(df_o[df_o['Öğrenci Adı'].str.lower() == current_user].tail(10))

