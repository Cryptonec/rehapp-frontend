"""
Yönetim — sadece mevcut tanı/modülleri göster + otomatik seed.
Manuel ekleme yok.
"""
import streamlit as st
import api_client as api

TANI_MODUL_MAP = {
    "Bedensel Yetersizliği Olan Bireyler İçin Destek Eğitim Programı": ["Günlük Yaşam Aktiviteleri"],
    "Dil ve Konuşma Bozukluğu Olan Bireyler İçin Destek Eğitim Programı": ["Dil"],
    "Görme Yetersizliği Olan Bireyler İçin Destek Eğitim Programı": [
        "Dil ve İletişim","Erken Matematik","Günlük Yaşam Becerileri",
        "Matematik","Okuma ve Yazma","Sosyal Beceriler","Toplumsal Yaşam Becerileri"],
    "İşitme Yetersizliği Olan Bireyler İçin Destek Eğitim Programı": [
        "Erken Matematik","Matematik","Okuma ve Yazma","Sosyal İletişim"],
    "Otizm Spektrum Bozukluğu Olan Bireyler İçin Destek Eğitim Programı": [
        "Birey ve Çevre","Dil, İletişim ve Oyun","Erken Matematik",
        "Günlük Yaşam Becerileri","Matematik","Okuma ve Yazma",
        "Sosyal Beceriler","Toplumsal Yaşam Becerileri"],
    "Öğrenme Güçlüğü Olan Bireyler İçin Destek Eğitim Programı": [
        "Dil ve İletişim","Erken Matematik","Matematik","Okuma ve Yazma","Sosyal Etkileşim"],
    "Zihinsel Yetersizliği Olan Bireyler İçin Destek Eğitim Programı": [
        "Birey ve Çevre","Dil, İletişim ve Oyun","Erken Matematik",
        "Günlük Yaşam Becerileri","Matematik","Okuma ve Yazma",
        "Sosyal Beceriler","Toplumsal Yaşam Becerileri"],
}
ALL_TANILAR  = sorted(TANI_MODUL_MAP.keys())
ALL_MODULLER = sorted({m for v in TANI_MODUL_MAP.values() for m in v})


def show():
    st.header("⚙️ Yönetim")

    mevcut_t = {d["name"] for d in api.get_diagnoses()}
    mevcut_m = {m["name"] for m in api.get_modules()}
    eksik_t  = [t for t in ALL_TANILAR  if t not in mevcut_t]
    eksik_m  = [m for m in ALL_MODULLER if m not in mevcut_m]

    if eksik_t or eksik_m:
        st.warning(f"⚠️ {len(eksik_t)} tanı ve {len(eksik_m)} modül henüz sisteme eklenmemiş.")
        if st.button("🚀 Tüm Tanı ve Modülleri Otomatik Ekle", type="primary"):
            for t in eksik_t:
                api.create_diagnosis(t)
            for m in eksik_m:
                api.create_module(m)
            st.success("✅ Tamamlandı!")
            st.rerun()
    else:
        st.success("✅ Tüm tanı ve modüller sistemde mevcut.")

    st.divider()
    st.subheader("📋 Grup Eğitimi Tanı → Modül Haritası")
    st.caption("Bu eşleştirme Lila import ve grup oluşturma işlemlerinde kullanılır. Değiştirilemez.")

    for tani, modller in TANI_MODUL_MAP.items():
        kisa = tani.replace(" Olan Bireyler İçin Destek Eğitim Programı", "")
        with st.expander(f"🔵 {kisa}"):
            for m in modller:
                st.markdown(f"&nbsp;&nbsp;&nbsp;✅ {m}")

    st.divider()

    # Sadece görüntüleme — sistemdeki tanı ve modüller
    col1, col2 = st.columns(2)
    diags = api.get_diagnoses()
    mods  = api.get_modules()

    with col1:
        st.subheader(f"Tanılar ({len(diags)})")
        for d in diags:
            kisa = d["name"].replace(" Olan Bireyler İçin Destek Eğitim Programı","").strip()
            c1, c2 = st.columns([5,1])
            c1.markdown(f"<div style='padding:5px 0;font-size:13px;color:#1A2B4C'>{kisa}</div>", unsafe_allow_html=True)
            if c2.button("🗑", key=f"del_d_{d['id']}"):
                if api.delete_diagnosis(d["id"]): st.rerun()

    with col2:
        st.subheader(f"Modüller ({len(mods)})")
        for m in mods:
            c1, c2 = st.columns([5,1])
            c1.markdown(f"<div style='padding:5px 0;font-size:13px;color:#1A2B4C'>{m['name']}</div>", unsafe_allow_html=True)
            if c2.button("🗑", key=f"del_m_{m['id']}"):
                if api.delete_module(m["id"]): st.rerun()
