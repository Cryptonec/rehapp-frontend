"""
Yönetim — hoşgeldiniz + otomatik seed + tanı→modül haritası.
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


def _otomatik_seed():
    """Eksik tanı/modülleri sessizce ekle."""
    try:
        diags    = api.get_diagnoses()
        mods     = api.get_modules()
        mevcut_t = {d["name"] for d in diags}
        mevcut_m = {m["name"] for m in mods}
        for t in ALL_TANILAR:
            if t not in mevcut_t:
                api.create_diagnosis(t)
        for m in ALL_MODULLER:
            if m not in mevcut_m:
                api.create_module(m)
    except Exception:
        pass


def show():
    # Sayfa açıldığında sessizce seed et
    _otomatik_seed()

    kurum_ad = st.session_state.get("kurum_ad", "")

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(56,201,192,.1),rgba(39,86,214,.08));
         border:1.5px solid rgba(56,201,192,.25);border-radius:18px;padding:28px 32px;margin-bottom:24px;">
      <div style="font-family:Sora,sans-serif;font-size:22px;font-weight:800;
           color:#0D1B35;margin-bottom:6px;">
        👋 Hoş geldiniz, <span style="color:#38C9C0;">{kurum_ad}</span>
      </div>
      <div style="font-size:14px;color:#6B7A99;line-height:1.7;">
        Rehapp'a bağlısınız. Öğrencilerinizi <b>Öğrenci</b> sekmesinden yönetebilir,
        <b>Grup Oluştur</b> sekmesinden mevzuata uygun gruplar kurabilir,
        <b>Gruplar</b> sekmesinden kayıtlı gruplarınızı görüntüleyebilirsiniz.
      </div>
    </div>""", unsafe_allow_html=True)

    st.subheader("📋 Grup Eğitimi Tanı → Modül Haritası")
    st.caption("Grup oluşturmada kullanılan eşleştirme tablosu.")

    for tani, modul_listesi in TANI_MODUL_MAP.items():
        kisa = tani.replace(" Olan Bireyler İçin Destek Eğitim Programı", "")
        with st.expander(f"🔵 {kisa}"):
            for m in modul_listesi:
                st.markdown(f"&nbsp;&nbsp;&nbsp;✅ {m}")