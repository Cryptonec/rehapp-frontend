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

TANI_META = {
    "Bedensel Yetersizliği Olan Bireyler İçin Destek Eğitim Programı":
        {"renk": "#E74C3C", "bg": "#FEF0EF", "border": "#FADADD", "ikon": "♿"},
    "Dil ve Konuşma Bozukluğu Olan Bireyler İçin Destek Eğitim Programı":
        {"renk": "#E67E22", "bg": "#FEF5EC", "border": "#FAE0C8", "ikon": "🗣"},
    "Görme Yetersizliği Olan Bireyler İçin Destek Eğitim Programı":
        {"renk": "#8E44AD", "bg": "#F5EEF8", "border": "#E8D5F0", "ikon": "👁"},
    "İşitme Yetersizliği Olan Bireyler İçin Destek Eğitim Programı":
        {"renk": "#2756D6", "bg": "#EEF3FF", "border": "#C9D8F8", "ikon": "👂"},
    "Otizm Spektrum Bozukluğu Olan Bireyler İçin Destek Eğitim Programı":
        {"renk": "#16A085", "bg": "#E8F8F5", "border": "#A9DFBF", "ikon": "🧩"},
    "Öğrenme Güçlüğü Olan Bireyler İçin Destek Eğitim Programı":
        {"renk": "#D35400", "bg": "#FDF0E7", "border": "#F5CBA7", "ikon": "📚"},
    "Zihinsel Yetersizliği Olan Bireyler İçin Destek Eğitim Programı":
        {"renk": "#1A8A4A", "bg": "#E9F7EF", "border": "#A9DFBF", "ikon": "🧠"},
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

    # ── Hoşgeldiniz kartı ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0D1B35 0%,#1A3A6B 60%,#1A7A74 100%);
         border-radius:20px;padding:32px 36px;margin-bottom:28px;position:relative;overflow:hidden;">
      <div style="position:absolute;top:-30px;right:-30px;width:160px;height:160px;
           border-radius:50%;background:rgba(56,201,192,.12);"></div>
      <div style="position:absolute;bottom:-40px;right:60px;width:100px;height:100px;
           border-radius:50%;background:rgba(39,86,214,.15);"></div>
      <div style="font-family:Sora,sans-serif;font-size:13px;font-weight:600;
           color:rgba(56,201,192,.8);letter-spacing:1.5px;text-transform:uppercase;
           margin-bottom:8px;">HOŞ GELDİNİZ</div>
      <div style="font-family:Sora,sans-serif;font-size:26px;font-weight:800;
           color:white;margin-bottom:10px;">{kurum_ad}</div>
      <div style="font-size:14px;color:rgba(255,255,255,.65);line-height:1.8;max-width:520px;">
        Öğrencilerinizi <b style="color:rgba(56,201,192,.9);">Öğrenci</b> sekmesinden,
        mevzuata uygun grupları <b style="color:rgba(56,201,192,.9);">Grup Oluştur</b> sekmesinden,
        kayıtlı gruplarınızı <b style="color:rgba(56,201,192,.9);">Gruplar</b> sekmesinden yönetebilirsiniz.
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Harita başlığı ────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">
      <div style="width:4px;height:28px;background:linear-gradient(#38C9C0,#2756D6);
           border-radius:4px;"></div>
      <div style="font-family:Sora,sans-serif;font-size:18px;font-weight:800;color:#0D1B35;">
        Grup Eğitimi Tanı → Modül Haritası
      </div>
    </div>
    <div style="font-size:13px;color:#8896B0;margin-bottom:24px;margin-left:16px;">
      Grup oluşturmada kullanılan mevzuat tabanlı eşleştirme rehberi
    </div>""", unsafe_allow_html=True)

    # ── Tanı kartları ─────────────────────────────────────────────────────────
    for tani, moduller in TANI_MODUL_MAP.items():
        meta = TANI_META.get(tani, {"renk":"#2756D6","bg":"#EEF3FF","border":"#C9D8F8","ikon":"📋"})
        renk   = meta["renk"]
        bg     = meta["bg"]
        border = meta["border"]
        ikon   = meta["ikon"]
        mod_count = len(moduller)

        mod_badges = "".join(
            f"""<span style="display:inline-flex;align-items:center;gap:5px;
                background:white;color:{renk};border:1.5px solid {border};
                border-radius:30px;padding:5px 14px;font-size:12px;font-weight:600;
                margin:4px 3px;box-shadow:0 1px 3px rgba(0,0,0,.06);">
                <span style="width:6px;height:6px;border-radius:50%;
                  background:{renk};display:inline-block;flex-shrink:0;"></span>
                {m}
              </span>"""
            for m in moduller
        )

        st.markdown(f"""
        <div style="background:{bg};border:1.5px solid {border};border-radius:16px;
             padding:0;margin-bottom:14px;overflow:hidden;
             box-shadow:0 2px 8px rgba(0,0,0,.05);">

          <div style="background:linear-gradient(135deg,{renk}18,{renk}08);
               border-bottom:1px solid {border};padding:16px 22px;
               display:flex;align-items:center;gap:14px;">
            <div style="width:42px;height:42px;border-radius:12px;
                 background:{renk}22;display:flex;align-items:center;
                 justify-content:center;font-size:20px;flex-shrink:0;">{ikon}</div>
            <div style="flex:1;">
              <div style="font-family:Sora,sans-serif;font-weight:700;font-size:14px;
                   color:{renk};line-height:1.4;">{tani}</div>
            </div>
            <div style="background:{renk};color:white;border-radius:20px;
                 padding:3px 12px;font-size:12px;font-weight:700;
                 font-family:Sora,sans-serif;white-space:nowrap;flex-shrink:0;">
              {mod_count} modül
            </div>
          </div>

          <div style="padding:14px 22px 18px;">
            {mod_badges}
          </div>
        </div>""", unsafe_allow_html=True)
