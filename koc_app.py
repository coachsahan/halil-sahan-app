import streamlit as st
import pandas as pd
import os
from datetime import date
import base64
import requests

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="KOÇ HALİL ŞAHAN", layout="wide")

# GitHub Bağlantı Ayarları (Secrets'tan çeker)
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
REPO_NAME = st.secrets.get("REPO_NAME")

def github_a_kaydet(dosya_adi, df):
    """Verileri doğrudan GitHub'daki CSV dosyasına yazar"""
    if not GITHUB_TOKEN:
        st.error("Giriş Anahtarı (Token) Secrets kısmına eklenmemiş! Veriler kalıcı kaydedilemez.")
        return
    
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{dosya_adi}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # Mevcut dosyanın SHA bilgisini al (GitHub üzerine yazmak için şarttır)
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    
    # Veriyi Base64 formatına çevir
    content = base64.b64encode(df.to_csv(index=False).encode()).decode()
    data = {"message": f"Kalıcı Veri Güncelleme: {date.today()}", "content": content}
    if sha: data["sha"] = sha
    
    res = requests.put(url, headers=headers, json=data)
    if res.status_code not in [200, 201]:
        st.error(f"GitHub'a yazılırken hata oluştu: {res.text}")

# --- TASARIM VE ARKA PLAN ---
RESIM_YOLU = "panel_bg.jpg"
LOGO_YOLU = "logo.jpg" 

KULLANICILAR = {
    "halil": "sahan123",
    "canan": "canan2025",
    "hafize": "hafize2026",
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
        df['Tarih'] = pd.to_datetime(df['Tarih']).dt.date
        return df
    return pd.DataFrame(columns=kolonlar)

def fark_hesapla(df):
    if df.empty: return df
    df = df.sort_values(by="Tarih")
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        df[f'{col} (Fark)'] = df[col].diff().fillna(0)
    return df.sort_values(by="Tarih", ascending=False)

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
        # --- COACH PANELİ ---
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
            st.title("Gelişim Analizi ve Farklar")
            sporcular = df_k['Öğrenci Adı'].unique()
            if len(sporcular) > 0:
                secilen = st.selectbox("Sporcu seç:", sporcular)
                st.table(fark_hesapla(df_k[df_k['Öğrenci Adı'] == secilen]))
                filtre_o = df_o[df_o['Öğrenci Adı'] == secilen]
                if not filtre_o.empty:
                    st.subheader("Haftalık Ölçü Farkları")
                    st.table(fark_hesapla(filtre_o))
        elif menu == "🗑️ Veri Sil":
            st.title("Kayıt Silme Paneli")
            dosya_sec = st.selectbox("Hangi veriyi silmek istersin?", ["Günlük Kilolar", "Haftalık Ölçüler"])
            temp_df = df_k if dosya_sec == "Günlük Kilolar" else df_o
            if not temp_df.empty:
                st.dataframe(temp_df)
                idx = st.number_input("Silinecek Satır Numarası:", min_value=0, max_value=len(temp_df)-1, step=1)
                if st.button("SEÇİLEN SATIRI SİL ❌"):
                    temp_df = temp_df.drop(temp_df.index[idx])
                    github_a_kaydet(KILO_DOSYASI if dosya_sec == "Günlük Kilolar" else OLCU_DOSYASI, temp_df)
                    st.success("Veri GitHub'dan kalıcı olarak silindi!")
                    st.rerun()
        else:
            st.dataframe(df_k if menu == "⚖️ Günlük Kilolar" else df_o)

    else:
        # --- ÖĞRENCİ PANELİ ---
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
                kilo_gunluk = st.number_input("Bugünkü Kilon (kg)", step=0.1)
                notum = st.text_area("Hocana Notun")
                if st.form_submit_button("KİLOYU KAYDET"):
                    df = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), kilo_gunluk, notum]], columns=df.columns)
                    son_df = pd.concat([df, yeni])
                    github_a_kaydet(KILO_DOSYASI, son_df)
                    st.success("Kilo kalıcı olarak kaydedildi!")
        
        with tab2:
            st.subheader("Haftalık Detaylı Ölçüm Formu")
            with st.form("olcu_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                k_h = c1.number_input("Güncel Kilo (kg)", step=0.1)
                b_h = c2.number_input("Boy (cm)", step=1)
                o_h = c3.number_input("Omuz (cm)", step=0.1)
                g_h = c1.number_input("Göğüs (cm)", step=0.1)
                be_h = c2.number_input("Bel (cm)", step=0.1)
                ka_h = c3.number_input("Kalça (cm)", step=0.1)
                uk_h = c1.number_input("Üst Kol (cm)", step=0.1)
                ak_h = c2.number_input("Alt Kol (cm)", step=0.1)
                ba_h = c3.number_input("Bacak (cm)", step=0.1)
                blr_h = c1.number_input("Baldır (cm)", step=0.1)
                if st.form_submit_button("ÖLÇÜLERİ GÖNDER 🔥"):
                    df = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', 'Bacak'])
                    yeni = pd.DataFrame([[date.today(), current_user.capitalize(), k_h, b_h, o_h, ka_h, blr_h, uk_h, ak_h, g_h, be_h, ba_h]], columns=df.columns)
                    son_df = pd.concat([df, yeni])
                    github_a_kaydet(OLCU_DOSYASI, son_df)
                    st.success("Haftalık veriler kalıcı kaydedildi!")

        with tab3:
            df_k = veriyi_yukle(KILO_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not'])
            df_o = veriyi_yukle(OLCU_DOSYASI, ['Tarih', 'Öğrenci Adı', 'Kilo', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', 'Bacak'])
            st.markdown("### ⚖️ Kilo Geçmişin ve Gelişim Farkı")
            st.table(fark_hesapla(df_k[df_k['Öğrenci Adı'].str.lower() == current_user]).head(10))
            st.markdown("---")
            st.markdown("### 📏 Haftalık Ölçü Geçmişin ve Farklar")
            st.table(fark_hesapla(df_o[df_o['Öğrenci Adı'].str.lower() == current_user]).head(10))

