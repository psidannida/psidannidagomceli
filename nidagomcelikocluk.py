import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. VERİ YÖNETİMİ ---
VERI_DOSYASI = "nida_akademi_final.json"

def veri_yukle():
    if os.path.exists(VERI_DOSYASI) and os.path.getsize(VERI_DOSYASI) > 0:
        try:
            with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {"ogrenciler": {}}
    return {"ogrenciler": {}}

def veri_kaydet(veri):
    with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = veri_yukle()

# --- 2. EKSİKSİZ VE TAM MÜFREDAT ---
mufredat_yks = {
    "TYT Matematik": ["Temel Kavramlar", "Rasyonel Sayılar", "Üslü-Köklü", "Problemler", "Mantık", "Fonksiyonlar", "Veri-İstatistik", "Permütasyon-Kombinasyon-Olasılık"],
    "TYT Türkçe": ["Paragraf", "Sözcük-Cümle Anlamı", "Yazım-Noktalama", "Dil Bilgisi"],
    "AYT Matematik (SAY/EA)": ["Trigonometri", "Logaritma", "Diziler", "Limit", "Türev", "İntegral", "Polinomlar", "Eşitsizlikler"],
    "AYT Fen (SAYISAL)": ["Fizik (Mekanik, Elektrik, Modern)", "Kimya (Organik, Enerji, Hız)", "Biyoloji (Sistemler, Genetik)"],
    "AYT Ed-Sos (EA)": ["Edebiyat (Dönemler, Sanatçılar)", "Tarih (İnkılap, Dünya Tarihi)", "Coğrafya (Beşeri, Ekonomik)"],
    "YKS Diğer": ["TYT Fizik", "TYT Kimya", "TYT Biyoloji", "TYT Tarih", "TYT Coğrafya", "TYT Din/Felsefe"]
}

mufredat_lgs = {
    "LGS Matematik": ["Çarpanlar Katlar", "Üslü İfadeler", "Kareköklü İfadeler", "Veri Analizi", "Olasılık", "Cebirsel İfadeler", "Denklemler", "Eşitsizlikler", "Üçgenler", "Geometrik Cisimler"],
    "LGS Fen": ["Mevsimler", "DNA-Genetik", "Basınç", "Madde-Endüstri", "Basit Makineler", "Enerji Dönüşümü", "Elektrik"],
    "LGS Türkçe": ["Fiilimsiler", "Anlam Bilgisi", "Cümlenin Ögeleri", "Fiilde Çatı", "Cümle Türleri", "Yazım-Noktalama"],
    "LGS İnkılap": ["Bir Kahraman Doğuyor", "Milli Uyanış", "Ya İstiklal Ya Ölüm", "Atatürkçülük"],
    "LGS Din Kültürü": ["Kader İnancı", "Zekat ve Sadaka", "Din ve Hayat", "Hz. Muhammed'in Örnekliği"],
    "LGS İngilizce": ["Friendship", "Teen Life", "In the Kitchen", "On the Phone", "The Internet", "Adventures"]
}

# --- 3. TASARIM ---
st.set_page_config(page_title="Nida GÖMCELİ Akademi", layout="wide")
st.markdown("<style>.stApp { background-color: #05070a; color: white; }</style>", unsafe_allow_html=True)

# --- GİRİŞ VE PANEL YÖNETİMİ ---
if "logged_in" not in st.session_state:
    st.title("🛡️ Nida GÖMCELİ Akademi")
    u = st.text_input("Kullanıcı Adı")
    p = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        if u == "admin" and p == "nida2024":
            st.session_state.update({"logged_in": True, "role": "admin"})
            st.rerun()
        elif u in st.session_state.db["ogrenciler"] and st.session_state.db["ogrenciler"][u].get("sifre") == p:
            st.session_state.update({"logged_in": True, "role": "ogrenci", "user": u})
            st.rerun()
        else: st.error("Hata!")
else:
    if st.session_state["role"] == "admin":
        st.sidebar.title("Yönetici")
        if st.sidebar.button("Çıkış"): del st.session_state["logged_in"]; st.rerun()
        with st.expander("👤 Öğrenci Kaydet"):
            ad = st.text_input("Öğrenci Ad Soyad")
            g = st.selectbox("Grup", ["LGS", "YKS"])
            h = st.number_input("Haftalık Hedef", 500)
            if st.button("Kaydet"):
                st.session_state.db["ogrenciler"][ad] = {"soru_takip": [], "sinav": g, "hedef": h, "sifre": "123"}
                veri_kaydet(st.session_state.db); st.success(f"{ad} Eklendi (Şifre: 123)")
    else:
        u = st.session_state["user"]
        o = st.session_state.db["ogrenciler"][u]
        m = mufredat_lgs if o["sinav"] == "LGS" else mufredat_yks
        st.sidebar.title(f"Öğrenci: {u}")
        if st.sidebar.button("Çıkış"): del st.session_state["logged_in"]; st.rerun()

        t1, t2, t3 = st.tabs(["📝 Soru Girişi", "🎯 Hedef Takibi", "🧮 2024/2025 Puan Hesapla"])

        with t1:
            ders = st.selectbox("Ders", list(m.keys()))
            konu = st.selectbox("Konu", m[ders])
            d = st.number_input("Doğru", 0)
            y = st.number_input("Yanlış", 0)
            if st.button("Kaydet"):
                o["soru_takip"].append({"Tarih": datetime.now().strftime("%d/%m/%Y"), "Ders": ders, "Konu": konu, "Toplam": d+y})
                veri_kaydet(st.session_state.db); st.success("Kaydedildi!")

        with t3:
            st.subheader("📊 LGS/YKS Puan Motoru")
            if o["sinav"] == "LGS":
                col1, col2 = st.columns(2)
                mat = col1.number_input("Matematik Net", 0.0, 20.0)
                fen = col2.number_input("Fen Net", 0.0, 20.0)
                tur = col1.number_input("Türkçe Net", 0.0, 20.0)
                ink = col2.number_input("İnkılap Net", 0.0, 10.0)
                din = col1.number_input("Din Net", 0.0, 10.0)
                ing = col2.number_input("İngilizce Net", 0.0, 10.0)
                # 2024/2025 Katsayı Tahmini (Standart Sapma Dahil Yaklaşık)
                puan = 194.7 + (mat * 4.9) + (fen * 4.1) + (tur * 3.7) + (ink * 1.7) + (din * 1.9) + (ing * 1.6)
                st.metric("Tahmini LGS Yerleştirme Puanı", f"{min(puan, 500.0):.3f}")
            else:
                tyt = st.number_input("TYT Toplam Net", 0.0, 120.0)
                ayt = st.number_input("AYT Toplam Net", 0.0, 80.0)
                yks_p = 100 + (tyt * 1.32) + (ayt * 3.06)
                st.metric("Tahmini YKS Ham Puan (SAY/EA Ortalama)", f"{min(yks_p, 500.0):.3f}")