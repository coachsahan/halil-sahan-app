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
    if not GITHUB_TOKEN or not REPO_NAME:
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

# --- VERİ DOSYALARI VE YÜKLEME ---
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
    df = df.sort_values(by="Tarih")
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        df[f'{col} (Fark)'] = df[col].diff().fillna(0)
    return df.sort_values(by="Tarih", ascending=False)

# --- KULLANICI LİSTESİ ---
KULLANICILAR = {"halil": "sahan123", "emrecan": "emrecan2026", "ceyda": "ceyda2026", "umuttatar": "tatar2026"}

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
        st.sidebar.title("COACH PANELİ 👑")
        menu = st.sidebar.radio("MENÜ", ["🏠 Genel Tablo", "📊 Öğrenci Analizi", "🥗 Beslenme Takibi", "🗑️ Veri Sil"])
        if st.sidebar.button("Çıkış Yap"):
            st.session_state.user = None
            st.rerun()

        if menu == "🏠 Genel Tablo":
            st.title("Tüm Sporcu Verileri")
            st.dataframe(veriyi_yukle(KILO_DOSYASI, []), use_container_width=True)
            
        elif menu == "📊 Öğrenci Analizi":
            df_k = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
            sporcular = df_k['Öğrenci Adı'].unique()
            if len(sporcular) > 0:
                secilen = st.selectbox("Sporcu Seç:", sporcular)
                filtre_df = df_k[df_k['Öğrenci Adı'] == secilen].sort_values("Tarih")
                fig = px.line(filtre_df, x="Tarih", y="Kilo", title=f"{secilen} Kilo Değişim Grafiği", markers=True)
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                st.table(fark_hesapla(filtre_df))
            else: st.info("Henüz analiz edilecek veri yok.")

        elif menu == "🥗 Beslenme Takibi":
            st.title("Öğrenci Beslenme Notları")
            st.dataframe(veriyi_yukle(BESLENME_DOSYASI, []), use_container_width=True)

        elif menu == "🗑️ Veri Sil":
            st.title("Kayıt Silme")
            df_k = veriyi_yukle(KILO_DOSYASI, [])
            if not df_k.empty:
                idx = st.number_input("Silinecek Satır No:", 0, len(df_k)-1, 0)
                if st.button("SİL"):
                    yeni_df = df_k.drop(df_k.index[idx])
                    github_a_kaydet(KILO_DOSYASI, yeni_df)
                    st.success("Kayıt silindi ve GitHub güncellendi!")

    # --- ÖĞRENCİ PANELİ ---
    else:
        st.sidebar.title(f"SELAM {current_user.upper()}!")
        if st.sidebar.button("Güvenli Çıkış"):
            st.session_state.user = None
            st.rerun()
            
        tab1, tab2, tab3 = st.tabs(["⚖️ Kilo Kaydet", "🥗 Beslenme", "📊 Geçmişim"])
        
        with tab1:
            with st.form("k_form", clear_on_submit=True):
                kv = st.number_input("Bugünkü Kilon (kg)", step=0.1)
                nt = st.text_area("Hocana Notun")
                if st.form_submit_button("KİLOYU KAYDET"):
                    df = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), kv, nt]], columns=df.columns)
                    github_a_kaydet(KILO_DOSYASI, pd.concat([df, yeni]))
                    st.success("Kilo iletildi!")
        
        with tab2:
            with st.form("b_form", clear_on_submit=True):
                ogunler = st.text_area("Bugün neler yedin kanka? (Makroların veya öğünlerin)")
                if st.form_submit_button("BESLENMEYİ GÖNDER"):
                    df = veriyi_yukle(BESLENME_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Öğünler'])
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), ogunler]], columns=df.columns)
                    github_a_kaydet(BESLENME_DOSYASI, pd.concat([df, yeni]))
                    st.success("Beslenme günlüğün Coach Halil'e iletildi!")

        with tab3:
            df_k = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
            filtre = df_k[df_k['Öğrenci Adı'].str.lower() == current_user].sort_values("Tarih")
            if not filtre.empty:
                fig = px.line(filtre, x="Tarih", y="Kilo", title="Kilo Gelişim Grafiğin", markers=True)
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                st.table(fark_hesapla(filtre))
            else: st.info("Henüz geçmiş verin bulunmuyor.")
