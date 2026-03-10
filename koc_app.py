import streamlit as st
import pandas as pd
import os
from datetime import date
import base64
import requests
import plotly.express as px

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="KOÇ HALİL ŞAHAN", layout="wide")

# GitHub Bağlantısı (Secrets'tan çeker)
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
REPO_NAME = st.secrets.get("REPO_NAME")

def github_a_kaydet(dosya_adi, df):
    """Verileri GitHub'a kalıcı olarak gönderir"""
    if not GITHUB_TOKEN or not REPO_NAME:
        st.error("GitHub bağlantı ayarları eksik!")
        return False
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{dosya_adi}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    content = base64.b64encode(df.to_csv(index=False).encode()).decode()
    data = {"message": f"Güncelleme: {date.today()}", "content": content}
    if sha: data["sha"] = sha
    res = requests.put(url, headers=headers, json=data)
    return res.status_code in [200, 201]

# --- TASARIM VE ARKAPLAN ---
RESIM_YOLU = "panel_bg.jpg"
LOGO_YOLU = "logo.jpg" 

def set_bg(main_bg):
    if os.path.exists(main_bg):
        with open(main_bg, "rb") as f: data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""<style>
        .stApp {{ background: url("data:image/png;base64,{b64}"); background-size: cover; background-attachment: fixed; }}
        .stApp::before {{ content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.7); z-index: 0; }}
        .main .block-container {{ position: relative; z-index: 10; }}
        h1, h2, h3, p, label {{ color: white !important; text-shadow: 2px 2px 10px rgba(0,0,0,1) !important; }}
        .main-title {{ font-size: 4.5rem !important; font-weight: 800; text-align: center; color: white; }}
        .sub-title {{ font-size: 1.5rem !important; font-style: italic; text-align: center; color: #f0f0f0; margin-top: -10px; }}
        </style>""", unsafe_allow_html=True)

set_bg(RESIM_YOLU)

# --- VERİ DOSYALARI ---
KILO_DOSYASI = "kilo_verileri.csv"
OLCU_DOSYASI = "haftalik_olculer.csv"
BESLENME_DOSYASI = "beslenme_verileri.csv"

def veriyi_yukle(dosya, kolonlar):
    if os.path.exists(dosya):
        try:
            df = pd.read_csv(dosya)
            df['Tarih'] = pd.to_datetime(df['Tarih']).dt.date
            return df
        except: return pd.DataFrame(columns=kolonlar)
    return pd.DataFrame(columns=kolonlar)

def fark_hesapla(df):
    if df.empty: return df
    df = df.copy().sort_values(by="Tarih")
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        df[f'{col} (Fark)'] = df[col].diff().fillna(0)
    return df.sort_values(by="Tarih", ascending=False)

# --- KULLANICI LİSTESİ ---
KULLANICILAR = {"halil": "sahan123", "canan": "canan2026", "hafize": "hafize2026", "umut": "tatar2026"}

if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.8, 1.4, 0.8])
    with col2:
        st.markdown('<p class="main-title">KOÇ HALİL ŞAHAN</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">be wild but stay soft</p>', unsafe_allow_html=True)
        u_input = st.text_input("KULLANICI ADI").lower()
        p_input = st.text_input("ŞİFRE", type="password")
        if st.button("GİRİŞ YAP 🔥", use_container_width=True):
            if u_input in KULLANICILAR and KULLANICILAR[u_input] == p_input:
                st.session_state.user = u_input
                st.rerun()
            else: st.error("Hatalı Giriş!")
else:
    current_user = st.session_state.user
    
    # --- COACH PANELİ (ADMİN) ---
    if current_user == "halil":
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title("COACH PANELİ 👑")
            menu = st.radio("MENÜ", ["🏠 Genel Tablo", "📊 Detaylı Analiz", "🥗 Beslenme Takibi", "🗑️ Veri Sil"])
            if st.button("Çıkış Yap"):
                st.session_state.user = None
                st.rerun()

        if menu == "🏠 Genel Tablo":
            st.title("Toplu Sporcu Özeti")
            st.dataframe(veriyi_yukle(KILO_DOSYASI, []), use_container_width=True)
            
        elif menu == "📊 Detaylı Analiz":
            df_k = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
            sporcular = df_k['Öğrenci Adı'].unique()
            if len(sporcular) > 0:
                secilen = st.selectbox("Sporcu Seç:", sporcular)
                filtre_df = df_k[df_k['Öğrenci Adı'] == secilen].sort_values("Tarih")
                fig = px.line(filtre_df, x="Tarih", y="Kilo", title=f"{secilen} Kilo Grafiği", markers=True)
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                st.subheader("Gelişim ve Farklar")
                st.table(fark_hesapla(filtre_df))
            else: st.info("Veri yok.")

        elif menu == "🥗 Beslenme Takibi":
            st.title("Öğrenci Beslenme Notları")
            st.dataframe(veriyi_yukle(BESLENME_DOSYASI, []), use_container_width=True)

        elif menu == "🗑️ Veri Sil":
            st.title("Kayıt Silme")
            target = st.selectbox("Hangi tablo?", ["Kilolar", "Ölçüler", "Beslenmeler"])
            dosya = KILO_DOSYASI if target=="Kilolar" else OLCU_DOSYASI if target=="Ölçüler" else BESLENME_DOSYASI
            df_del = veriyi_yukle(dosya, [])
            if not df_del.empty:
                st.dataframe(df_del)
                idx = st.number_input("Silinecek Satır No:", 0, len(df_del)-1, 0)
                if st.button("SİL ❌"):
                    yeni_df = df_del.drop(df_del.index[idx])
                    github_a_kaydet(dosya, yeni_df)
                    st.success("Silindi!")
                    st.rerun()

    # --- ÖĞRENCİ PANELİ ---
    else:
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title(f"SELAM {current_user.upper()}!")
            if st.button("Çıkış"):
                st.session_state.user = None
                st.rerun()
            
        st.markdown(f"<h2 style='text-align: center;'>GÜCÜ HİSSET {current_user.upper()}! 🏆</h2>", unsafe_allow_html=True)
        tab1, tab2, tab3, tab4 = st.tabs(["⚖️ Kilo", "📏 Haftalık Ölçü", "🥗 Beslenme", "📊 Geçmişim"])
        
        with tab1:
            with st.form("k_form", clear_on_submit=True):
                kv = st.number_input("Bugünkü Kilon (kg)", step=0.1)
                nt = st.text_area("Hocana Notun")
                if st.form_submit_button("KAYDET"):
                    df = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), kv, nt]], columns=df.columns)
                    github_a_kaydet(KILO_DOSYASI, pd.concat([df, yeni]))
                    st.success("Kilo iletildi!")
        
        with tab2:
            with st.form("o_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                kh = c1.number_input("Kilo (kg)", step=0.1)
                oh = c2.number_input("Omuz (cm)", step=0.1)
                bh = c3.number_input("Bel (cm)", step=0.1)
                gh = c1.number_input("Göğüs (cm)", step=0.1)
                kah = c2.number_input("Kalça (cm)", step=0.1)
                boyh = c3.number_input("Boy (cm)", step=1)
                if st.form_submit_button("ÖLÇÜLERİ GÖNDER 🔥"):
                    df_o = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', '
