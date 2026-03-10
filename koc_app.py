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
    if not GITHUB_TOKEN or not REPO_NAME: return False
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{dosya_adi}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    content = base64.b64encode(df.to_csv(index=False).encode()).decode()
    data = {"message": f"Veri Güncelleme: {date.today()}", "content": content}
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

# --- VERİ DOSYALARI ---
KILO_DOSYASI = "kilo_verileri.csv"
OLCU_DOSYASI = "haftalik_olculer.csv"
BESLENME_DOSYASI = "beslenme_verileri.csv"
PROGRAM_DOSYASI = "programlar.csv"

def veriyi_yukle(dosya, kolonlar):
    if os.path.exists(dosya):
        try:
            df = pd.read_csv(dosya)
            df['Tarih'] = pd.to_datetime(df['Tarih']).dt.date
            return df
        except: return pd.DataFrame(columns=kolonlar)
    return pd.DataFrame(columns=kolonlar)

# --- KULLANICI LİSTESİ ---
KULLANICILAR = {"halil": "sahan123", "emrecan": "emrecan2026", "ceyda": "ceyda2026", "umuttatar": "tatar2026"}

if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.8, 1.4, 0.8])
    with col2:
        st.markdown('<p class="main-title">KOÇ HALİL ŞAHAN</p>', unsafe_allow_html=True)
        u_input = st.text_input("KULLANICI ADI").lower().strip()
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
        menu = st.sidebar.radio("MENÜ", ["📊 Detaylı Analiz", "📝 Program Yükle", "🥗 Beslenme Takip", "⚖️ Günlük Kilolar", "📏 Ölçü Kayıtları", "🗑️ Veri Sil"])
        
        if st.sidebar.button("Çıkış Yap"):
            st.session_state.user = None
            st.rerun()

        if menu == "📝 Program Yükle":
            st.title("Program Hazırla ✍️")
            sporcu_listesi = [k for k in KULLANICILAR.keys() if k != "halil"]
            secilen_ogrenci = st.selectbox("Sporcu Seç:", sporcu_listesi)
            df_p = veriyi_yukle(PROGRAM_DOSYASI, ['Sporcu', 'Beslenme_Prog', 'Antrenman_Prog', 'Guncelleme'])
            
            bes_prog = st.text_area("🥗 Beslenme Programı", height=200)
            ant_prog = st.text_area("🏋️‍♂️ Antrenman Programı", height=200)

            if st.button("PROGRAMI GÖNDER"):
                yeni_p = pd.DataFrame([[secilen_ogrenci, bes_prog, ant_prog, date.today()]], columns=['Sporcu', 'Beslenme_Prog', 'Antrenman_Prog', 'Guncelleme'])
                github_a_kaydet(PROGRAM_DOSYASI, pd.concat([df_p, yeni_p]))
                st.success("Program iletildi!")

        elif menu == "📊 Detaylı Analiz":
            df_k = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
            if not df_k.empty:
                sporcu = st.selectbox("Sporcu Seç:", df_k['Öğrenci Adı'].unique())
                f_df = df_k[df_k['Öğrenci Adı'] == sporcu].sort_values("Tarih")
                st.plotly_chart(px.line(f_df, x="Tarih", y="Kilo", title=f"{sporcu} Gelişim"))
            else: st.info("Henüz veri yok.")

        elif menu == "🗑️ Veri Sil":
            st.warning("Veri silme modülü aktif.")

    # --- ÖĞRENCİ PANELİ ---
    else:
        st.sidebar.title(f"SELAM {current_user.upper()}!")
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📜 Programım", "⚖️ Kilo", "🥗 Beslenme", "📏 Ölçü", "📊 Geçmişim"])
        
        with tab1:
            st.subheader("Koç Halil'in Senin İçin Hazırladığı Program")
            df_p = veriyi_yukle(PROGRAM_DOSYASI, ['Sporcu', 'Beslenme_Prog', 'Antrenman_Prog', 'Guncelleme'])
            prog = df_p[df_p['Sporcu'] == current_user].tail(1)
            if not prog.empty:
                st.info(f"Son Güncelleme: {prog['Guncelleme'].values[0]}")
                st.markdown(f"**Beslenme:** {prog['Beslenme_Prog'].values[0]}")
                st.markdown(f"**Antrenman:** {prog['Antrenman_Prog'].values[0]}")
            else: st.info("Programın koçun tarafından hazırlanıyor.")

        with tab2:
            with st.form("k_form", clear_on_submit=True):
                kv = st.number_input("Güncel Kilo (kg)", step=0.1)
                if st.form_submit_button("KAYDET"):
                    df = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), kv, ""]], columns=df.columns)
                    github_a_kaydet(KILO_DOSYASI, pd.concat([df, yeni]))
                    st.success("Kilo iletildi!")
        
        with tab4:
            st.subheader("Haftalık Ölçülerini Gir")
            with st.form("o_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                ok = c1.number_input("Kilo", step=0.1)
                ob = c2.number_input("Boy", step=1)
                oo = c1.number_input("Omuz", step=0.1)
                obel = c2.number_input("Bel", step=0.1)
                obald = c1.number_input("Baldır", step=0.1) # BALDIR BURADA!
                if st.form_submit_button("ÖLÇÜLERİ GÖNDER"):
                    df = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Boy', 'Omuz', 'Bel', 'Baldır'])
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), ok, ob, oo, obel, obald]], columns=df.columns)
                    github_a_kaydet(OLCU_DOSYASI, pd.concat([df, yeni]))
                    st.success("Ölçüler kaydedildi!")

        if st.sidebar.button("Çıkış Yap"):
            st.session_state.user = None
            st.rerun()
