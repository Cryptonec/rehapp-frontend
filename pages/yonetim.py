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

# Her tanı için renk
TANI_RENKLER = {
    "Bedensel Yetersizliği Olan Bireyler İçin Destek Eğitim Programı":      ("#FF6B6B", "#FFF0F0"),
    "Dil ve Konuşma Bozukluğu Olan Bireyler İçin Destek Eğitim Programı":  ("#F5883A", "#FFF5ED"),
    "Görme Yetersizliği Olan Bireyler İçin Destek Eğitim Programı":         ("#9B59B6", "#F8F0FF"),
    "İşitme Yetersizliği Olan Bireyler İçin Destek Eğitim Programı":        ("#2756D6", "#EEF3FF"),
    "Otizm Spektrum Bozukluğu Olan Bireyler İçin Destek Eğitim Programı":  ("#38C9C0", "#EDFAFA"),
    "Öğrenme Güçlüğü Olan Bireyler İçin Destek Eğitim Programı":           ("#E67E22", "#FFF8F0"),
    "Zihinsel Yetersizliği Olan Bireyler İçin Destek Eğitim Programı":      ("#27AE60", "#EDFFF4"),
}


def _otomatik_seed():
    try:
        mevcut_t = {d["name"] for d in api.get_diagnoses()}
        mevcut_m = {m["name"] for m in api.get_modules()}
        for t in ALL_TANILAR:
            if t not in mevcut_t: api.create_diagnosis(t)
        for m in ALL_MODULLER:
            if m not in mevcut_m: api.create_module(m)
    except Exception:
        pass


def show():
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

    st.markdown("""
    <div style="font-family:Sora,sans-serif;font-size:17px;font-weight:700;
         color:#0D1B35;margin-bottom:4px;">📋 Grup Eğitimi — Tanı & Modül Haritası</div>
    <div style="font-size:13px;color:#6B7A99;margin-bottom:20px;">
        Grup oluşturmada kullanılan tanı → modül eşleştirme tablosu
    </div>""", unsafe_allow_html=True)

    # Her tanıyı kart olarak göster
    for tani, moduller in TANI_MODUL_MAP.items():
        renk, bg = TANI_RENKLER.get(tani, ("#2756D6", "#EEF3FF"))
        kisa = tani.replace(" Olan Bireyler İçin Destek Eğitim Programı", "")
        mod_badges = "".join(
            f'<span style="display:inline-block;background:white;color:{renk};'
            f'border:1.5px solid {renk};border-radius:20px;padding:3px 12px;'
            f'font-size:12px;font-weight:500;margin:3px 4px;">{m}</span>'
            for m in moduller
        )
        st.markdown(f"""
        <div style="background:{bg};border:1.5px solid {renk}33;border-radius:14px;
             padding:16px 20px;margin-bottom:12px;">
          <div style="font-family:Sora,sans-serif;font-weight:700;font-size:14px;
               color:{renk};margin-bottom:10px;">
            ● {kisa}
          </div>
          <div style="line-height:2;">{mod_badges}</div>
        </div>""", unsafe_allow_html=True)
