import streamlit as st
import pandas as pd
import os
from datetime import date
import base64
import requests
import plotly.express as px

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="KOÇ HALİL ŞAHAN", layout="wide")

# GitHub Bağlantısı
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

# --- TASARIM ---
RESIM_YOLU = "panel_bg.jpg"
LOGO_YOLU = "logo.jpg" 

def set_bg(main_bg):
    if os.path.exists(main_bg):
        with open(main_bg, "rb") as f: data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""<style>
        .stApp {{ background: url("data:image/png;base64,{b64}"); background-size: cover; background-attachment: fixed; }}
        .stApp::before {{ content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.75); z-index: 0; }}
        .main .block-container {{ position: relative; z-index: 10; }}
        h1, h2, h3, p, label {{ color: white !important; text-shadow: 2px 2px 10px rgba(0,0,0,1) !important; }}
        .main-title {{ font-size: 4rem !important; font-weight: 800; text-align: center; color: white; }}
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

def fark_motoru(df):
    if df.empty or len(df) < 1: return df
    df = df.sort_values(by="Tarih")
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        df[f'{col} (Fark)'] = df[col].diff().fillna(0)
    return df.sort_values(by="Tarih", ascending=False)

# --- GİRİŞ SİSTEMİ ---
KULLANICILAR = {"halil": "sahan123", "emrecan": "emrecan2026", "ceyda": "ceyda2026", "umuttatar": "tatar2026"}
if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.8, 1.4, 0.8])
    with col2:
        st.markdown('<p class="main-title">KOÇ HALİL ŞAHAN</p>', unsafe_allow_html=True)
        u_in = st.text_input("KULLANICI ADI").lower()
        p_in = st.text_input("ŞİFRE", type="password")
        if st.button("SİSTEME GİR 🔥", use_container_width=True):
            if u_in in KULLANICILAR and KULLANICILAR[u_in] == p_in:
                st.session_state.user = u_in
                st.rerun()
else:
    current_user = st.session_state.user
    
    # --- ADMIN / COACH PANELİ ---
    if current_user == "halil":
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title("COACH PANELİ 👑")
            menu = st.radio("MENÜ", ["🏠 Genel Tablo", "📊 Detaylı Analiz", "🥗 Beslenme", "📏 Ölçü Kayıtları", "🗑️ Veri Sil"])
            if st.button("Çıkış Yap"):
                st.session_state.user = None
                st.rerun()

        if menu == "🏠 Genel Tablo":
            st.title("Tüm Kilo Geçmişi")
            st.dataframe(fark_motoru(veriyi_yukle(KILO_DOSYASI, [])), use_container_width=True)
        
        elif menu == "📏 Ölçü Kayıtları":
            st.title("Sporcu Ölçü Arşivi")
            st.dataframe(fark_motoru(veriyi_yukle(OLCU_DOSYASI, [])), use_container_width=True)

        elif menu == "📊 Detaylı Analiz":
            df_k = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
            sporcular = df_k['Öğrenci Adı'].unique()
            if len(sporcular) > 0:
                secilen = st.selectbox("Sporcu Seç:", sporcular)
                f_df = df_k[df_k['Öğrenci Adı'] == secilen].sort_values("Tarih")
                fig = px.line(f_df, x="Tarih", y="Kilo", title=f"{secilen} Gelişim Grafiği", markers=True)
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                st.table(fark_motoru(f_df))

        elif menu == "🥗 Beslenme":
            st.title("Beslenme Günlükleri")
            st.dataframe(veriyi_yukle(BESLENME_DOSYASI, []), use_container_width=True)

        elif menu == "🗑️ Veri Sil":
            st.title("🗑️ Veri Silme Paneli")
            dosya_secimi = st.selectbox("Hangi dosyadan silinsin?", ["Kilo Kayıtları", "Ölçü Kayıtları", "Beslenme Günlükleri"])
            
            dosya_adi = KILO_DOSYASI if dosya_secimi == "Kilo Kayıtları" else (OLCU_DOSYASI if dosya_secimi == "Ölçü Kayıtları" else BESLENME_DOSYASI)
            df_sil = veriyi_yukle(dosya_adi, [])
            
            if not df_sil.empty:
                st.write(f"Şu anki {dosya_secimi} listesi:")
                st.dataframe(df_sil)
                satir_no = st.number_input("Silmek istediğin satırın index numarası:", 0, len(df_sil)-1, 0)
                if st.button("SEÇİLEN SATIRI SİL ❌"):
                    df_yeni = df_sil.drop(df_sil.index[satir_no])
                    if github_a_kaydet(dosya_adi, df_yeni):
                        st.success("Kayıt GitHub'dan kalıcı olarak silindi!")
                        st.rerun()
            else: st.info("Silinecek veri bulunamadı.")

    # --- ÖĞRENCİ PANELİ ---
    else:
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title(f"SELAM {current_user.upper()}")
            if st.button("Çıkış"):
                st.session_state.user = None
                st.rerun()
        
        tab1, tab2, tab3, tab4 = st.tabs(["⚖️ Kilo Kaydı", "🥗 Beslenme", "📏 Haftalık Ölçü", "📊 Geçmişim"])
        
        with tab1:
            with st.form("k_form", clear_on_submit=True):
                kilo_v = st.number_input("Güncel Kilo (kg)", step=0.1)
                not_v = st.text_area("Notun")
                if st.form_submit_button("KAYDET"):
                    df = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), kilo_v, not_v]], columns=df.columns)
                    github_a_kaydet(KILO_DOSYASI, pd.concat([df, yeni]))
                    st.success("Kilo iletildi!")

        with tab2:
            with st.form("b_form", clear_on_submit=True):
                ogunler = st.text_area("Beslenme Notların")
                if st.form_submit_button("GÖNDER"):
                    df = veriyi_yukle(BESLENME_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Öğünler'])
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), ogunler]], columns=df.columns)
                    github_a_kaydet(BESLENME_DOSYASI, pd.concat([df, yeni]))
                    st.success("Beslenme iletildi!")

        with tab3:
            with st.form("olcu_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                ok = c1.number_input("Kilo", step=0.1)
                ob = c2.number_input("Boy", step=1)
                oo = c3.number_input("Omuz", step=0.1)
                og = c1.number_input("Göğüs", step=0.1)
                obel = c2.number_input("Bel", step=0.1)
                oka = c3.number_input("Kalça", step=0.1)
                ouk = c1.number_input("Üst Kol", step=0.1)
                oak = c2.number_input("Alt Kol", step=0.1)
                oba = c3.number_input("Bacak", step=0.1)
                if st.form_submit_button("ÖLÇÜLERİ GÖNDER 🔥"):
                    df = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', 'Bacak'])
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), ok, ob, oo, oka, 0, ouk, oak, og, obel, oba]], columns=df.columns)
                    github_a_kaydet(OLCU_DOSYASI, pd.concat([df, yeni]))
                    st.success("Ölçüler kaydedildi!")

        with tab4:
            st.markdown("### 📊 Gelişim Grafiğin ve Geçmişin")
            df_k = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
            df_o = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', 'Bacak'])
            
            f_k = df_k[df_k['Öğrenci Adı'].str.lower() == current_user.lower()]
            if not f_k.empty:
                fig = px.line(f_k.sort_values("Tarih"), x="Tarih", y="Kilo", title="Kilo Grafiği", markers=True)
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("#### ⚖️ Kilo Geçmişi ve Farklar")
                st.table(fark_motoru(f_k))
            
            f_o = df_o[df_o['Öğrenci Adı'].str.lower() == current_user.lower()]
            if not f_o.empty:
                st.markdown("---")
                st.markdown("#### 📏 Ölçü Geçmişi ve Farklar")
                st.table(fark_motoru(f_o))
            else: st.info("Geçmiş ölçü verisi bulunamadı.")
