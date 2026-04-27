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

# KOLON TANIMLARI
KILO_KOLON = ['Tarih', 'Öğrenci Adı', 'Kilo', 'Not']
OLCU_KOLON = ['Tarih', 'Öğrenci Adı', 'Kilo', 'Boy', 'Omuz', 'Kalça', 'Baldır', 'Üst Kol', 'Alt Kol', 'Göğüs', 'Bel', 'Bacak']
BESLENME_KOLON = ['Tarih', 'Öğrenci Adı', 'Öğünler']

def veriyi_yukle(dosya, varsayilan_kolonlar):
    if not os.path.exists(dosya):
        return pd.DataFrame(columns=varsayilan_kolonlar)
    try:
        df = pd.read_csv(dosya)
        # Dosya boşsa veya bozuksa
        if df.empty: return pd.DataFrame(columns=varsayilan_kolonlar)
        # Tarih formatı
        df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce').dt.date
        return df
    except:
        return pd.DataFrame(columns=varsayilan_kolonlar)

def fark_motoru(df):
    if df.empty or len(df) < 1: return df
    df_sorted = df.copy().sort_values(by="Tarih")
    numeric_cols = df_sorted.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        df_sorted[f'{col} (Fark)'] = df_sorted[col].diff().fillna(0.0)
    return df_sorted.sort_values(by="Tarih", ascending=False)

# --- KULLANICI SİSTEMİ ---
KULLANICILAR = {"halil": "sahan26", "canan": "canan2026", "hafize": "hafize2026", "umut": "tatar2026", "emine": "emine2026", "rabia": "rabia2026", "uğur": "uğur2026", "emre": "emre2026", "Ahmet": "topcu2026" }
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
    current_user = st.session_state.user
    
    # --- COACH PANELİ ---
    if current_user == "halil":
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title("COACH PANELİ 👑")
            menu = st.radio("MENÜ", ["🏠 Genel Tablo", "📊 Detaylı Analiz", "🥗 Beslenme", "⚖️ Günlük Kilolar", "📏 Ölçü Kayıtları", "🗑️ Veri Sil"])
            if st.button("Çıkış Yap"):
                st.session_state.user = None
                st.rerun()

        if menu == "🏠 Genel Tablo" or menu == "⚖️ Günlük Kilolar":
            st.title("Günlük Kilo Takibi")
            df = veriyi_yukle(KILO_DOSYASI, KILO_KOLON)
            st.dataframe(fark_motoru(df), use_container_width=True)

        elif menu == "🥗 Beslenme":
            st.title("Öğrenci Beslenmeleri")
            df = veriyi_yukle(BESLENME_DOSYASI, BESLENME_KOLON)
            st.dataframe(df, use_container_width=True)

        elif menu == "📏 Ölçü Kayıtları":
            st.title("Haftalık Ölçü Kayıtları")
            df = veriyi_yukle(OLCU_DOSYASI, OLCU_KOLON)
            st.dataframe(fark_motoru(df), use_container_width=True)

        elif menu == "📊 Detaylı Analiz":
            st.title("Sporcu Analizi")
            df_k = veriyi_yukle(KILO_DOSYASI, KILO_KOLON)
            df_o = veriyi_yukle(OLCU_DOSYASI, OLCU_KOLON)
            tum_sporcular = pd.concat([df_k['Öğrenci Adı'], df_o['Öğrenci Adı']]).unique()
            if len(tum_sporcular) > 0:
                secilen = st.selectbox("Sporcu:", tum_sporcular)
                f_k = df_k[df_k['Öğrenci Adı'] == secilen].sort_values("Tarih")
                if not f_k.empty:
                    fig = px.line(f_k, x="Tarih", y="Kilo", title="Ağırlık Grafiği", markers=True)
                    st.plotly_chart(fig, use_container_width=True)
                st.table(fark_motoru(f_k))
            else: st.info("Veri bulunamadı.")

        elif menu == "🗑️ Veri Sil":
            st.title("🗑️ Veri Silme Paneli")
            dosya_sec = st.selectbox("Hangi dosyadan sileceksin?", ["Kilo", "Ölçü", "Beslenme"])
            
            # Doğru dosyayı seçtirelim
            dosya_adi = KILO_DOSYASI if dosya_sec == "Kilo" else (OLCU_DOSYASI if dosya_sec == "Ölçü" else BESLENME_DOSYASI)
            kolonlar = KILO_KOLON if dosya_sec == "Kilo" else (OLCU_KOLON if dosya_sec == "Ölçü" else BESLENME_KOLON)
            
            df_sil = veriyi_yukle(dosya_adi, kolonlar)
            
            if not df_sil.empty:
                st.dataframe(df_sil)
                idx = st.number_input("Silmek istediğin satırın index no:", 0, len(df_sil)-1, 0)
                if st.button("SEÇİLEN KAYDI SİL ❌"):
                    df_yeni = df_sil.drop(df_sil.index[idx])
                    github_a_kaydet(dosya_adi, df_yeni)
                    st.success("Veri silindi!")
                    st.rerun()
            else:
                st.warning(f"{dosya_sec} dosyasında silinecek veri bulunamadı.")

    # --- ÖĞRENCİ PANELİ ---
    else:
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title(f"SELAM {current_user.upper()}")
            if st.button("Çıkış"):
                st.session_state.user = None
                st.rerun()
        
        tab1, tab2, tab3, tab4 = st.tabs(["⚖️ Kilo", "🥗 Beslenme", "📏 Haftalık Ölçü", "📊 Geçmişim"])
        
        with tab1:
            with st.form("k_form", clear_on_submit=True):
                kv = st.number_input("Kilon (kg)", step=0.1)
                nt = st.text_area("Not")
                if st.form_submit_button("KAYDET"):
                    df = veriyi_yukle(KILO_DOSYASI, KILO_KOLON)
                    yeni = pd.DataFrame([[date.today(), current_user, kv, nt]], columns=KILO_KOLON)
                    github_a_kaydet(KILO_DOSYASI, pd.concat([df, yeni]))
                    st.success("Gönderildi!")

        with tab2:
            with st.form("b_form", clear_on_submit=True):
                og = st.text_area("Yediklerini yaz")
                if st.form_submit_button("GÖNDER"):
                    df = veriyi_yukle(BESLENME_DOSYASI, BESLENME_KOLON)
                    yeni = pd.DataFrame([[date.today(), current_user, og]], columns=BESLENME_KOLON)
                    github_a_kaydet(BESLENME_DOSYASI, pd.concat([df, yeni]))
                    st.success("Gönderildi!")

        with tab3:
            with st.form("o_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                ok = c1.number_input("Kilo", step=0.1)
                ob = c2.number_input("Boy", step=1.0)
                oo = c3.number_input("Omuz", step=0.1)
                oka = c1.number_input("Kalça", step=0.1)
                hbal = c2.number_input("Baldır", step=0.1)
                ouk = c3.number_input("Üst Kol", step=0.1)
                oak = c1.number_input("Alt Kol", step=0.1)
                og = c2.number_input("Göğüs", step=0.1)
                obel = c3.number_input("Bel", step=0.1)
                oba = c1.number_input("Bacak", step=0.1)
                if st.form_submit_button("ÖLÇÜLERİ GÖNDER 🔥"):
                    df = veriyi_yukle(OLCU_DOSYASI, OLCU_KOLON)
                    yeni = pd.DataFrame([[date.today(), current_user, ok, ob, oo, oka, hbal, ouk, oak, og, obel, oba]], columns=OLCU_KOLON)
                    github_a_kaydet(OLCU_DOSYASI, pd.concat([df, yeni]))
                    st.success("Kaydedildi!")

        with tab4:
            st.subheader("Gelişim Arşivin")
            df_k = veriyi_yukle(KILO_DOSYASI, KILO_KOLON)
            df_o = veriyi_yukle(OLCU_DOSYASI, OLCU_KOLON)
            f_k = df_k[df_k['Öğrenci Adı'].astype(str).str.lower() == current_user.lower()]
            if not f_k.empty:
                st.table(fark_motoru(f_k))
            f_o = df_o[df_o['Öğrenci Adı'].astype(str).str.lower() == current_user.lower()]
            if not f_o.empty:
                st.markdown("---")
                st.table(fark_motoru(f_o))
