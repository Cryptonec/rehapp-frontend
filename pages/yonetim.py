"""
Yönetim — otomatik seed + tanı→modül haritası.
Tanılar/modüller listesi kaldırıldı.
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


@st.cache_data(ttl=30, show_spinner=False)
def _get_counts():
    return len(api.get_diagnoses()), len(api.get_modules())


def show():
    st.header("⚙️ Yönetim")

    diag_count, mod_count = _get_counts()
    eksik_t = max(0, len(ALL_TANILAR)  - diag_count)
    eksik_m = max(0, len(ALL_MODULLER) - mod_count)

    if eksik_t > 0 or eksik_m > 0:
        st.warning(f"⚠️ {eksik_t} tanı ve {eksik_m} modül henüz sisteme eklenmemiş.")
        if st.button("🚀 Tüm Tanı ve Modülleri Otomatik Ekle", type="primary"):
            diags = api.get_diagnoses(); mods = api.get_modules()
            mevcut_t = {d["name"] for d in diags}
            mevcut_m = {m["name"] for m in mods}
            for t in ALL_TANILAR:
                if t not in mevcut_t: api.create_diagnosis(t)
            for m in ALL_MODULLER:
                if m not in mevcut_m: api.create_module(m)
            _get_counts.clear()
            st.success("✅ Tamamlandı!")
            st.rerun()
    else:
        st.success("✅ Tüm tanı ve modüller sistemde mevcut.")

    st.divider()
    st.subheader("📋 Grup Eğitimi Tanı → Modül Haritası")
    st.caption("Bu eşleştirme Lila import ve grup oluşturma işlemlerinde kullanılır.")

    for tani, modul_listesi in TANI_MODUL_MAP.items():
        kisa = tani.replace(" Olan Bireyler İçin Destek Eğitim Programı", "")
        with st.expander(f"🔵 {kisa}"):
            for m in modul_listesi:
                st.markdown(f"&nbsp;&nbsp;&nbsp;✅ {m}")
