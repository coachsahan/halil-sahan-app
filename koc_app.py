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
        .main-title {{ font-size: 3.5rem !important; font-weight: 800; text-align: center; color: white; }}
        </style>""", unsafe_allow_html=True)

set_bg(RESIM_YOLU)

# --- VERİ DOSYALARI ---
KILO_DOSYASI = "kilo_verileri.csv"
OLCU_DOSYASI = "haftalik_olculer.csv"
BESLENME_DOSYASI = "beslenme_verileri.csv"
PROGRAM_DOSYASI = "programlar.csv"

KILO_KOLON = ['Tarih', 'Sporcu', 'Kilo', 'Not']
OLCU_KOLON = ['Tarih', 'Sporcu', 'Kilo', 'Boy', 'Omuz', 'Kalca', 'Baldır', 'UstKol', 'AltKol', 'Gogus', 'Bel', 'Bacak']
BESLENME_KOLON = ['Tarih', 'Sporcu', 'Ogunler']
PROGRAM_KOLON = ['Sporcu', 'Beslenme_Prog', 'Antrenman_Prog', 'Guncelleme']

def veriyi_yukle(dosya, kolonlar):
    if not os.path.exists(dosya):
        return pd.DataFrame(columns=kolonlar)
    try:
        df = pd.read_csv(dosya)
        if df.empty: return pd.DataFrame(columns=kolonlar)
        if 'Tarih' in df.columns:
            df['Tarih'] = pd.to_datetime(df['Tarih']).dt.date
        return df
    except:
        return pd.DataFrame(columns=kolonlar)

def fark_motoru(df):
    if df.empty or len(df) < 1: return df
    df_sorted = df.copy().sort_values(by="Tarih")
    numeric_cols = df_sorted.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        df_sorted[f'{col} (Fark)'] = df_sorted[col].diff().fillna(0.0)
    return df_sorted.sort_values(by="Tarih", ascending=False)

# --- KULLANICI SİSTEMİ ---
KULLANICILAR = {"halil": "sahan123", "emrecan": "emrecan2026", "ceyda": "ceyda2026", "umuttatar": "tatar2026"}
if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.8, 1.4, 0.8])
    with col2:
        st.markdown('<p class="main-title">KOÇ HALİL ŞAHAN</p>', unsafe_allow_html=True)
        u_in = st.text_input("KULLANICI ADI").lower().strip()
        p_in = st.text_input("ŞİFRE", type="password")
        if st.button("SİSTEME GİR 🔥", use_container_width=True):
            if u_in in KULLANICILAR and KULLANICILAR[u_in] == p_in:
                st.session_state.user = u_in
                st.rerun()
            else: st.error("Kullanıcı adı veya şifre hatalı!")
else:
    current_user = st.session_state.user
    
    # --- COACH PANELİ ---
    if current_user == "halil":
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title("COACH PANELİ 👑")
            menu = st.radio("MENÜ", ["🏠 Genel Tablo", "📊 Detaylı Analiz", "📝 Program Yükle", "🥗 Beslenme Takip", "⚖️ Günlük Kilolar", "📏 Ölçü Kayıtları", "🗑️ Veri Sil"])
            if st.button("Güvenli Çıkış"):
                st.session_state.user = None
                st.rerun()

        if menu == "📝 Program Yükle":
            st.title("Program Hazırla ✍️")
            sporcular = [k for k in KULLANICILAR.keys() if k != "halil"]
            secilen = st.selectbox("Sporcu Seç:", sporcular)
            df_p = veriyi_yukle(PROGRAM_DOSYASI, PROGRAM_KOLON)
            mevcut = df_p[df_p['Sporcu'] == secilen]
            
            b_val = mevcut['Beslenme_Prog'].values[0] if not mevcut.empty else ""
            a_val = mevcut['Antrenman_Prog'].values[0] if not mevcut.empty else ""

            bes_prog = st.text_area("🥗 Beslenme Programı", value=b_val, height=200)
            ant_prog = st.text_area("🏋️‍♂️ Antrenman Programı", value=a_val, height=200)

            if st.button("PROGRAMI KAYDET VE GÖNDER"):
                if not mevcut.empty:
                    df_p.loc[df_p['Sporcu'] == secilen, ['Beslenme_Prog', 'Antrenman_Prog', 'Guncelleme']] = [bes_prog, ant_prog, date.today()]
                else:
                    yeni_p = pd.DataFrame([[secilen, bes_prog, ant_prog, date.today()]], columns=PROGRAM_KOLON)
                    df_p = pd.concat([df_p, yeni_p])
                github_a_kaydet(PROGRAM_DOSYASI, df_p)
                st.success(f"{secilen.upper()} için program güncellendi!")

        elif menu == "🏠 Genel Tablo":
            st.title("Genel Sporcu Durumu")
            st.dataframe(fark_motoru(veriyi_yukle(KILO_DOSYASI, KILO_KOLON)), use_container_width=True)

        elif menu == "🥗 Beslenme Takip":
            st.title("Öğrenci Beslenme Notları")
            st.dataframe(veriyi_yukle(BESLENME_DOSYASI, BESLENME_KOLON), use_container_width=True)

        elif menu == "📊 Detaylı Analiz":
            st.title("Gelişim Analizi")
            df_k = veriyi_yukle(KILO_DOSYASI, KILO_KOLON)
            sporcular = df_k['Sporcu'].unique()
            if len(sporcular) > 0:
                s = st.selectbox("Sporcu Analizi:", sporcular)
                f = df_k[df_k['Sporcu'] == s].sort_values("Tarih")
                st.plotly_chart(px.line(f, x="Tarih", y="Kilo", title=f"{s.upper()} Kilo Değişimi", markers=True).update_layout(template="plotly_dark"))
                st.table(fark_motoru(f))
        
        elif menu == "⚖️ Günlük Kilolar":
            st.dataframe(fark_motoru(veriyi_yukle(KILO_DOSYASI, KILO_KOLON)))
            
        elif menu == "📏 Ölçü Kayıtları":
            st.dataframe(fark_motoru(veriyi_yukle(OLCU_DOSYASI, OLCU_KOLON)))

        elif menu == "🗑️ Veri Sil":
            d_sec = st.selectbox("Dosya:", ["Kilo", "Ölçü", "Beslenme"])
            d_adi = KILO_DOSYASI if d_sec=="Kilo" else (OLCU_DOSYASI if d_sec=="Ölçü" else BESLENME_DOSYASI)
            df = veriyi_yukle(d_adi, [])
            if not df.empty:
                st.dataframe(df)
                idx = st.number_input("Silinecek Index:", 0, len(df)-1, 0)
                if st.button("SİL"):
                    df_yeni = df.drop(df.index[idx])
                    github_a_kaydet(d_adi, df_yeni)
                    st.rerun()

    # --- ÖĞRENCİ PANELİ ---
    else:
        with st.sidebar:
            if os.path.exists(LOGO_YOLU): st.image(LOGO_YOLU)
            st.title(f"HOŞ GELDİN {current_user.upper()}")
            if st.button("Çıkış Yap"):
                st.session_state.user = None
                st.rerun()
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📜 Programım", "⚖️ Kilo Bildir", "🥗 Beslenme Notu", "📏 Ölçü Bildir", "📊 Geçmişim"])
        
        with tab1:
            st.subheader("Koç Halil'in Senin İçin Hazırladığı Program")
            df_p = veriyi_yukle(PROGRAM_DOSYASI, PROGRAM_KOLON)
            prog = df_p[df_p['Sporcu'] == current_user]
            if not prog.empty:
                st.warning(f"Son Güncelleme: {prog['Guncelleme'].values[0]}")
                c1, c2 = st.columns(2)
                with c1:
                    st.info("🥗 BESLENME PLANI")
                    st.write(prog['Beslenme_Prog'].values[0])
                with c2:
                    st.info("🏋️‍♂️ ANTRENMAN PLANI")
                    st.write(prog['Antrenman_Prog'].values[0])
            else:
                st.info("Programın koçun tarafından hazırlanıyor, takipte kal!")

        with tab2:
            with st.form("k_form", clear_on_submit=True):
                kilo_v = st.number_input("Bugünkü Kilon (kg)", step=0.1)
                not_v = st.text_input("Koçuna notun var mı?")
                if st.form_submit_button("KİLOYU GÖNDER"):
                    df = veriyi_yukle(KILO_DOSYASI, KILO_KOLON)
                    yeni = pd.DataFrame([[date.today(), current_user, kilo_v, not_v]], columns=KILO_KOLON)
                    github_a_kaydet(KILO_DOSYASI, pd.concat([df, yeni]))
                    st.success("Kilo bilgisi başarıyla iletildi!")

        with tab3:
            with st.form("b_form", clear_on_submit=True):
                yediklerin = st.text_area("Bugün neler yedin? (Öğün öğün yazabilirsin)")
                if st.form_submit_button("NOTU GÖNDER"):
                    df = veriyi_yukle(BESLENME_DOSYASI, BESLENME_KOLON)
                    yeni = pd.DataFrame([[date.today(), current_user, yediklerin]], columns=BESLENME_KOLON)
                    github_a_kaydet(BESLENME_DOSYASI, pd.concat([df, yeni]))
                    st.success("Beslenme notun koçuna iletildi!")

        with tab4:
            with st.form("o_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                ok = c1.number_input("Kilo", step=0.1)
                ob = c2.number_input("Boy", step=1.0)
                oo = c3.number_input("Omuz", step=0.1)
                oka = c1.number_input("Kalça", step=0.1)
                hba = c2.number_input("Baldır", step=0.1)
                ouk = c3.number_input("Üst Kol", step=0.1)
                if st.form_submit_button("TÜM ÖLÇÜLERİ KAYDET"):
                    df = veriyi_yukle(OLCU_DOSYASI, OLCU_KOLON)
                    yeni = pd.DataFrame([[date.today(), current_user, ok, ob, oo, oka, hba, ouk, 0, 0, 0, 0]], columns=OLCU_KOLON)
                    github_a_kaydet(OLCU_DOSYASI, pd.concat([df, yeni]))
                    st.success("Ölçüler kaydedildi!")

        with tab5:
            st.subheader("Senin Gelişimin")
            df_k = veriyi_yukle(KILO_DOSYASI, KILO_KOLON)
            f_k = df_k[df_k['Sporcu'] == current_user]
            if not f_k.empty:
                st.table(fark_motoru(f_k))
            else:
                st.info("Henüz geçmiş kaydın bulunamadı.")
