import streamlit as st
import pandas as pd
import os
from datetime import date
import base64
import requests

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="KOÇ HALİL ŞAHAN", layout="wide")

# GitHub Secrets
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
REPO_NAME = st.secrets.get("REPO_NAME")

def github_a_kaydet(dosya_adi, df):
    if not GITHUB_TOKEN: return
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{dosya_adi}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    content = base64.b64encode(df.to_csv(index=False).encode()).decode()
    data = {"message": f"Veri Güncelleme: {date.today()}", "content": content}
    if sha: data["sha"] = sha
    requests.put(url, headers=headers, json=data)

# --- TASARIM VE ARKA PLAN ---
RESIM_YOLU = "panel_bg.jpg"
KULLANICILAR = {"halil": "sahan123", "canan": "canan2026", "hafize": "hafize2026", "umut": "tatar2026"}

def set_bg(main_bg):
    if os.path.exists(main_bg):
        with open(main_bg, "rb") as f: data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""<style>
        .stApp {{ background: url("data:image/png;base64,{b64}"); background-size: cover; background-attachment: fixed; }}
        .stApp::before {{ content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.65); z-index: 0; }}
        .main .block-container {{ position: relative; z-index: 10; }}
        h1, h2, h3, p, label {{ color: white !important; text-shadow: 2px 2px 8px rgba(0,0,0,1) !important; }}
        .main-title {{ font-size: 4.5rem !important; font-weight: 800; text-align: center; color: white; }}
        </style>""", unsafe_allow_html=True)

set_bg(RESIM_YOLU)

# --- VERİ DOSYALARI ---
OLCU_DOSYASI = "haftalik_olculer.csv"
BESLENME_DOSYASI = "beslenme_takibi.csv"
PROGRAM_DOSYASI = "antrenman_programlari.csv"

def veriyi_yukle(dosya, kolonlar):
    if os.path.exists(dosya):
        df = pd.read_csv(dosya)
        if 'Tarih' in df.columns: df['Tarih'] = pd.to_datetime(df['Tarih']).dt.date
        return df
    return pd.DataFrame(columns=kolonlar)

if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.8, 1.4, 0.8])
    with col2:
        st.markdown('<p class="main-title">KOÇ HALİL ŞAHAN</p>', unsafe_allow_html=True)
        u_in = st.text_input("KULLANICI ADI").lower()
        p_in = st.text_input("ŞİFRE", type="password")
        if st.button("GİRİŞ YAP 🔥", use_container_width=True):
            if u_in in KULLANICILAR and KULLANICILAR[u_in] == p_in:
                st.session_state.user = u_in
                st.rerun()
else:
    current_user = st.session_state.user
    
    # --- COACH PANELİ ---
    if current_user == "halil":
        with st.sidebar:
            st.title("COACH PANELİ 👑")
            menu = st.radio("MENÜ", ["📊 Analiz & Grafikler", "🥗 Beslenme Kontrol", "🏋️‍♂️ Program Yaz", "🗑️ Veri Sil"])
            if st.button("Çıkış"):
                st.session_state.user = None
                st.rerun()

        if menu == "📊 Analiz & Grafikler":
            df_o = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Omuz', 'Bel', 'Kalça'])
            sporcu = st.selectbox("Sporcu Seç:", df_o['Öğrenci Adı'].unique() if not df_o.empty else ["Veri Yok"])
            if sporcu != "Veri Yok":
                filt = df_o[df_o['Öğrenci Adı'] == sporcu].sort_values("Tarih")
                st.subheader(f"{sporcu} - Kilo Gelişimi")
                st.line_chart(filt.set_index("Tarih")["Kilo"])
                st.subheader("Ölçü Tablosu")
                st.table(filt.sort_values("Tarih", ascending=False))

        elif menu == "🏋️‍♂️ Program Yaz":
            st.title("Antrenman Ata")
            df_p = veriyi_yukle(PROGRAM_DOSYASI, ['Öğrenci Adı', 'Program'])
            hedef = st.selectbox("Kime yazıyorsun?", list(KULLANICILAR.keys())[1:])
            prog_notu = st.text_area("Antrenman Detayı (Hareket, Set, Tekrar)")
            if st.button("PROGRAMI GÖNDER"):
                yeni_p = pd.DataFrame([[hedef.capitalize(), prog_notu]], columns=['Öğrenci Adı', 'Program'])
                github_a_kaydet(PROGRAM_DOSYASI, yeni_p)
                st.success("Program iletildi!")

    # --- ÖĞRENCİ PANELİ ---
    else:
        st.sidebar.title(f"SELAM {current_user.upper()}!")
        tab1, tab2, tab3, tab4 = st.tabs(["📏 Ölçü Gir", "🥗 Beslenme", "🏋️‍♂️ Programım", "📊 Geçmişim"])
        
        with tab1:
            with st.form("o_f", clear_on_submit=True):
                k = st.number_input("Kilo (kg)", step=0.1)
                o = st.number_input("Omuz (cm)", step=0.1)
                be = st.number_input("Bel (cm)", step=0.1)
                if st.form_submit_button("KAYDET"):
                    df = veriyi_yukle(OLCU_DOSYASI, ['Tarih','Öğrenci Adı','Kilo','Omuz','Bel'])
                    y = pd.DataFrame([[date.today(), current_user.capitalize(), k, o, be]], columns=df.columns)
                    github_a_kaydet(OLCU_DOSYASI, pd.concat([df, y]))
                    st.success("Kaydedildi!")

        with tab2:
            with st.form("b_f", clear_on_submit=True):
                ogun = st.text_area("Bugün neler yedin?")
                if st.form_submit_button("BESLENMEYİ BİLDİR"):
                    df = veriyi_yukle(BESLENME_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Öğünler'])
                    y = pd.DataFrame([[date.today(), current_user.capitalize(), ogun]], columns=df.columns)
                    github_a_kaydet(BESLENME_DOSYASI, pd.concat([df, y]))
                    st.success("Afiyet olsun!")

        with tab3:
            df_p = veriyi_yukle(PROGRAM_DOSYASI, ['Öğrenci Adı', 'Program'])
            p_bak = df_p[df_p['Öğrenci Adı'] == current_user.capitalize()]
            if not p_bak.empty: st.info(p_bak.iloc[-1]['Program'])
            else: st.warning("Henüz program atanmamış.")
            
        with tab4:
            df_o = veriyi_yukle(OLCU_DOSYASI, ['Tarih','Öğrenci Adı','Kilo','Omuz','Bel'])
            filt = df_o[df_o['Öğrenci Adı'].str.lower() == current_user].sort_values("Tarih", ascending=False)
            st.line_chart(filt.set_index("Tarih")["Kilo"])
            st.table(filt)
