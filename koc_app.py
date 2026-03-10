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

# KOLONLAR (SABİT)
KILO_KOLON = ['Tarih', 'Sporcu', 'Kilo', 'Not']
OLCU_KOLON = ['Tarih', 'Sporcu', 'Kilo', 'Boy', 'Omuz', 'Kalca', 'Baldır', 'UstKol', 'AltKol', 'Gogus', 'Bel', 'Bacak']
BESLENME_KOLON = ['Tarih', 'Sporcu', 'Ogunler']

def veriyi_yukle(dosya, kolonlar):
    if not os.path.exists(dosya):
        return pd.DataFrame(columns=kolonlar)
    try:
        df = pd.read_csv(dosya)
        if df.empty: return pd.DataFrame(columns=kolonlar)
        
        # ESKİ SÜTUNLARI YENİSİYLE DEĞİŞTİR (TAMİR MOTORU)
        if 'Öğrenci Adı' in df.columns:
            df.rename(columns={'Öğrenci Adı': 'Sporcu'}, inplace=True)
        if 'Öğünler' in df.columns:
            df.rename(columns={'Öğünler': 'Ogunler'}, inplace=True)
            
        # Eksik sütunları 0 ile doldur
        for col in kolonlar:
            if col not in df.columns: df[col] = 0.0
            
        df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce').dt.date
        return df[kolonlar]
    except:
        return pd.DataFrame(columns=kolonlar)

def fark_motoru(df):
    if df.empty or len(df) < 1: return df
    df_sorted = df.copy().sort_values(by="Tarih")
    numeric_cols = df_sorted.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        df_sorted[f'{col} (Fark)'] = df_sorted[col].diff().fillna(0.0)
    return df_sorted.sort_values(by="Tarih", ascending=False)

# --- GİRİŞ SİSTEMİ ---
KULLANICILAR = {"halil": "sahan123", "emrecan": "emrecan2026", "ceyda": "ceyda2026", "umuttatar": "tatar2026"}
if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.8, 1.4, 0.8])
    with col2:
        st.markdown('<p class="main-title">KOÇ HALİL ŞAHAN</p>', unsafe_allow_html=True)
        u_in = st.text_input("KULLANICI ADI").lower().strip()
        p_in = st.text_input("ŞİFRE", type="password")
        if st.button("SİSTEME GİR 🔥", use_container_width=True):
            if u_in in KULLANICILAR and KULLANICILAR[u_in] == p_in:
                st.session_state.user = u_in
                st.rerun()
            else: st.error("Hatalı Giriş!")
else:
    u = st.session_state.user
    
    if u == "halil":
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title("COACH PANELİ")
            menu = st.radio("MENÜ", ["🏠 Genel Tablo", "🥗 Beslenme", "📏 Ölçü Kayıtları", "📊 Detaylı Analiz", "🗑️ Veri Sil"])
            if st.button("Çıkış"):
                st.session_state.user = None
                st.rerun()

        if menu == "🏠 Genel Tablo":
            st.dataframe(fark_motoru(veriyi_yukle(KILO_DOSYASI, KILO_KOLON)), use_container_width=True)
        elif menu == "🥗 Beslenme":
            st.dataframe(veriyi_yukle(BESLENME_DOSYASI, BESLENME_KOLON), use_container_width=True)
        elif menu == "📏 Ölçü Kayıtları":
            st.dataframe(fark_motoru(veriyi_yukle(OLCU_DOSYASI, OLCU_KOLON)), use_container_width=True)
        elif menu == "📊 Detaylı Analiz":
            df_k = veriyi_yukle(KILO_DOSYASI, KILO_KOLON)
            sporcular = df_k['Sporcu'].unique()
            if len(sporcular) > 0:
                s_sec = st.selectbox("Sporcu:", sporcular)
                f = df_k[df_k['Sporcu'] == s_sec].sort_values("Tarih")
                st.plotly_chart(px.line(f, x="Tarih", y="Kilo", markers=True).update_layout(template="plotly_dark"))
        elif menu == "🗑️ Veri Sil":
            d_sec = st.selectbox("Dosya:", ["Kilo", "Ölçü", "Beslenme"])
            d_adi = KILO_DOSYASI if d_sec=="Kilo" else (OLCU_DOSYASI if d_sec=="Ölçü" else BESLENME_DOSYASI)
            df = veriyi_yukle(d_adi, [])
            if not df.empty:
                st.dataframe(df)
                idx = st.number_input("Silinecek Index:", 0, len(df)-1, 0)
                if st.button("SİL"):
                    github_a_kaydet(d_adi, df.drop(df.index[idx]))
                    st.rerun()

    else:
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title(f"SELAM {u.upper()}")
            if st.button("Çıkış"):
                st.session_state.user = None
                st.rerun()
        
        t1, t2, t3, t4 = st.tabs(["⚖️ Kilo", "🥗 Beslenme", "📏 Ölçü", "📊 Geçmişim"])
        
        with t1:
            with st.form("k"):
                kv = st.number_input("Kilo", step=0.1)
                nt = st.text_area("Not")
                if st.form_submit_button("KAYDET"):
                    df = veriyi_yukle(KILO_DOSYASI, KILO_KOLON)
                    yeni = pd.DataFrame([[date.today(), u, kv, nt]], columns=KILO_KOLON)
                    github_a_kaydet(KILO_DOSYASI, pd.concat([df, yeni]))
                    st.success("Kaydedildi!")

        with t2:
            with st.form("b"):
                og = st.text_area("Beslenme")
                if st.form_submit_button("GÖNDER"):
                    df = veriyi_yukle(BESLENME_DOSYASI, BESLENME_KOLON)
                    yeni = pd.DataFrame([[date.today(), u, og]], columns=BESLENME_KOLON)
                    github_a_kaydet(BESLENME_DOSYASI, pd.concat([df, yeni]))
                    st.success("Gönderildi!")

        with t3:
            with st.form("o"):
                c1, c2, c3 = st.columns(3)
                ok = c1.number_input("Güncel Kilo", step=0.1)
                ob = c2.number_input("Boy", step=1.0)
                oo = c3.number_input("Omuz", step=0.1)
                oka = c1.number_input("Kalça", step=0.1)
                hba = c2.number_input("Baldır", step=0.1)
                ouk = c3.number_input("Üst Kol", step=0.1)
                oak = c1.number_input("Alt Kol", step=0.1)
                og = c2.number_input("Göğüs", step=0.1)
                obe = c3.number_input("Bel", step=0.1)
                oba = c1.number_input("Bacak", step=0.1)
                if st.form_submit_button("ÖLÇÜLERİ GÖNDER"):
                    df = veriyi_yukle(OLCU_DOSYASI, OLCU_KOLON)
                    yeni = pd.DataFrame([[date.today(), u, ok, ob, oo, oka, hba, ouk, oak, og, obe, oba]], columns=OLCU_KOLON)
                    github_a_kaydet(OLCU_DOSYASI, pd.concat([df, yeni]))
                    st.success("Ölçüler kaydedildi!")

        with t4:
            st.subheader("Gelişim Arşivin")
            dk = veriyi_yukle(KILO_DOSYASI, KILO_KOLON)
            do = veriyi_yukle(OLCU_DOSYASI, OLCU_KOLON)
            
            # KÜÇÜK HARF EŞLEŞTİRME (GARANTİ OLSUN)
            fk = dk[dk['Sporcu'].astype(str).str.lower() == u.lower()]
            if not fk.empty:
                st.plotly_chart(px.line(fk.sort_values("Tarih"), x="Tarih", y="Kilo", title="Kilo Grafiği", markers=True).update_layout(template="plotly_dark"))
                st.table(fark_motoru(fk))
            
            fo = do[do['Sporcu'].astype(str).str.lower() == u.lower()]
            if not fo.empty:
                st.markdown("---")
                st.table(fark_motoru(fo))
            else: st.info("Henüz ölçü geçmişin bulunamadı.")

