"""
Yönetim sayfası.
Tanı ve modüller otomatik olarak TANI_MODUL_MAP'ten tohumlanır.
Kurum manuel seçim yapmak zorunda değil.
"""
import streamlit as st
import api_client as api

# ── Sabit tanı→modül haritası ─────────────────────────────────────────────────
TANI_MODUL_MAP = {
    "Bedensel Yetersizliği Olan Bireyler İçin Destek Eğitim Programı": [
        "Günlük Yaşam Aktiviteleri",
    ],
    "Dil ve Konuşma Bozukluğu Olan Bireyler İçin Destek Eğitim Programı": [
        "Dil",
    ],
    "Görme Yetersizliği Olan Bireyler İçin Destek Eğitim Programı": [
        "Dil ve İletişim",
        "Erken Matematik",
        "Günlük Yaşam Becerileri",
        "Matematik",
        "Okuma ve Yazma",
        "Sosyal Beceriler",
        "Toplumsal Yaşam Becerileri",
    ],
    "İşitme Yetersizliği Olan Bireyler İçin Destek Eğitim Programı": [
        "Erken Matematik",
        "Matematik",
        "Okuma ve Yazma",
        "Sosyal İletişim",
    ],
    "Otizm Spektrum Bozukluğu Olan Bireyler İçin Destek Eğitim Programı": [
        "Birey ve Çevre",
        "Dil, İletişim ve Oyun",
        "Erken Matematik",
        "Günlük Yaşam Becerileri",
        "Matematik",
        "Okuma ve Yazma",
        "Sosyal Beceriler",
        "Toplumsal Yaşam Becerileri",
    ],
    "Öğrenme Güçlüğü Olan Bireyler İçin Destek Eğitim Programı": [
        "Dil ve İletişim",
        "Erken Matematik",
        "Matematik",
        "Okuma ve Yazma",
        "Sosyal Etkileşim",
    ],
    "Zihinsel Yetersizliği Olan Bireyler İçin Destek Eğitim Programı": [
        "Birey ve Çevre",
        "Dil, İletişim ve Oyun",
        "Erken Matematik",
        "Günlük Yaşam Becerileri",
        "Matematik",
        "Okuma ve Yazma",
        "Sosyal Beceriler",
        "Toplumsal Yaşam Becerileri",
    ],
}

ALL_TANILAR = sorted(TANI_MODUL_MAP.keys())
ALL_MODULLER = sorted(set(m for mods in TANI_MODUL_MAP.values() for m in mods))


def seed_all():
    """Tüm tanı ve modülleri sisteme ekle (yoksa)."""
    mevcut_tanilar = {d["name"] for d in api.get_diagnoses()}
    mevcut_moduller = {m["name"] for m in api.get_modules()}

    eklenen = 0
    for tani in ALL_TANILAR:
        if tani not in mevcut_tanilar:
            api.create_diagnosis(tani)
            eklenen += 1
    for modul in ALL_MODULLER:
        if modul not in mevcut_moduller:
            api.create_module(modul)
            eklenen += 1
    return eklenen


def show():
    st.header("⚙️ Yönetim")

    # ── Otomatik Tohumlama ────────────────────────────────────────────────────
    mevcut_tanilar  = {d["name"] for d in api.get_diagnoses()}
    mevcut_moduller = {m["name"] for m in api.get_modules()}
    eksik_tani   = [t for t in ALL_TANILAR  if t not in mevcut_tanilar]
    eksik_modul  = [m for m in ALL_MODULLER if m not in mevcut_moduller]

    if eksik_tani or eksik_modul:
        st.warning(f"⚠️ {len(eksik_tani)} tanı ve {len(eksik_modul)} modül henüz sisteme eklenmemiş.")
        if st.button("🚀 Tüm Tanı ve Modülleri Otomatik Ekle", type="primary"):
            eklenen = seed_all()
            st.success(f"✅ {eklenen} kayıt eklendi!")
            st.rerun()
        st.divider()
    else:
        st.success("✅ Tüm tanı ve modüller sistemde mevcut.")
        st.divider()

    # ── Tanı-Modül Listesi ────────────────────────────────────────────────────
    st.subheader("📋 Grup Eğitimi Tanı → Modül Haritası")
    st.caption("Aşağıdaki eşleştirme Lila import ve grup oluşturma işlemlerinde kullanılır.")

    for tani, moduller in TANI_MODUL_MAP.items():
        with st.expander(f"🔵 {tani}"):
            for m in moduller:
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;✅ {m}")

    st.divider()

    # ── Manuel Tanı/Modül Yönetimi ────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Tanılar")
        diags = api.get_diagnoses()
        for d in diags:
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"<div style='padding:6px 0;font-size:14px;color:#1A2B4C'>{d['name']}</div>", unsafe_allow_html=True)
            if c2.button("🗑", key=f"del_diag_{d['id']}"):
                if api.delete_diagnosis(d["id"]):
                    st.rerun()

        with st.form("new_diag", clear_on_submit=True):
            name = st.text_input("Yeni tanı adı", placeholder="Tanı adı girin...")
            if st.form_submit_button("➕ Ekle"):
                if name.strip():
                    api.create_diagnosis(name.strip())
                    st.rerun()

    with col2:
        st.subheader("Modüller")
        mods = api.get_modules()
        for m in mods:
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"<div style='padding:6px 0;font-size:14px;color:#1A2B4C'>{m['name']}</div>", unsafe_allow_html=True)
            if c2.button("🗑", key=f"del_mod_{m['id']}"):
                if api.delete_module(m["id"]):
                    st.rerun()

        with st.form("new_mod", clear_on_submit=True):
            name = st.text_input("Yeni modül adı", placeholder="Modül adı girin...")
            if st.form_submit_button("➕ Ekle"):
                if name.strip():
                    api.create_module(name.strip())
                    st.rerun()
