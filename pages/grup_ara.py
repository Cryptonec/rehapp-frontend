"""
Grup Oluştur — Manuel + Akıllı Öneri sekmeleri.

Performans optimizasyonları:
- Öğrenci + modül + tanı verisi TEK seferde API'den çekilir, session_state'te cache'lenir
- frozenset ile O(1) kesişim kontrolü
- Aday listesi her seçimde sadece mevcut gruptan türetilir, tüm öğrenciler taranmaz
- Grup üyeleri session_state["srch_grup_uyeleri"]'nde tutulur (eski proje adı korundu)
- Cache bust: Lila import sonrası students_cache_bust +1 → veri yeniden çekilir
"""
import streamlit as st
from datetime import date
from itertools import combinations
import api_client as api


# ── Yardımcı fonksiyonlar ─────────────────────────────────────────────────────

def age_years(dob_str):
    if not dob_str: return None
    try:
        days = (date.today() - date.fromisoformat(dob_str)).days
        if days <= 0: return None  # gelecek/bugün → geçersiz
        return days / 365.25
    except: return None

def rapor_renk(rb):
    if not rb: return "#22C55E"
    try:
        k = (date.fromisoformat(str(rb)[:10]) - date.today()).days
        return "#EF4444" if k < 0 else "#F59E0B" if k <= 30 else "#22C55E"
    except: return "#22C55E"

def rapor_etiketi(rb):
    if not rb: return ""
    try:
        k = (date.fromisoformat(str(rb)[:10]) - date.today()).days
        if k < 0:   return " (rapor bitti)"
        if k <= 30: return f" (rapor bitmesine {k} gün)"
        return ""
    except: return ""

def turkish_sort_key(s):
    return s.lower().translate(str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosucgiosu"))


# ── Veri yükleme — session_state cache ───────────────────────────────────────

def _load():
    """
    Öğrenci verisini session_state'te cache'ler.
    students_cache_bust değişince (Lila import sonrası) yeniden yükler.
    """
    bust = st.session_state.get("students_cache_bust", 0)
    if st.session_state.get("_sc_bust") != bust or "_sc_students" not in st.session_state:
        raw = api.get_students()

        # Her öğrenci için frozenset — kesişim O(1)
        mods_by_id  = {s["id"]: frozenset(m["name"] for m in s.get("modules",   [])) for s in raw}
        diags_by_id = {s["id"]: frozenset(d["name"] for d in s.get("diagnoses", [])) for s in raw}

        # Hızlı isim→id haritası
        id_by_name  = {s["name"]: s["id"] for s in raw}

        st.session_state.update({
            "_sc_students":  raw,
            "_sc_mods":      mods_by_id,
            "_sc_diags":     diags_by_id,
            "_sc_id_by_name":id_by_name,
            "_sc_bust":      bust,
        })

    return (
        st.session_state["_sc_students"],
        st.session_state["_sc_mods"],
        st.session_state["_sc_diags"],
        st.session_state["_sc_id_by_name"],
    )


# ── Akıllı Öneri Algoritması ──────────────────────────────────────────────────

def _onerici_hesapla(students, mods_by_id, diags_by_id, tani_filtre, grup_boyutu):
    """
    Seçili tanı ve grup boyutuna göre en ideal grupları hesaplar.
    Önce ≥2 ortak modül aranır; hiç sonuç yoksa ≥1 ortak modüle düşülür.
    Puan = ortak_modül_sayısı * 10 - yaş_farkı * 2
    Döner: (sonuclar, uygun_sayi, kullanilan_min_modul)
    """
    from pages.lila_import import TANI_MODUL_MAP

    tani_modulleri = frozenset(TANI_MODUL_MAP.get(tani_filtre, []))

    # Seçili tanıya sahip, yaşı hesaplanabilen öğrenciler
    uygun = [
        s for s in students
        if tani_filtre in diags_by_id.get(s["id"], frozenset())
        and age_years(s.get("dob")) is not None
    ]

    if len(uygun) < grup_boyutu:
        return [], len(uygun), 2

    def _tara(min_modul):
        sonuclar = []
        for kombo in combinations(uygun, grup_boyutu):
            yaslar = [age_years(s["dob"]) for s in kombo]
            yas_farki = max(yaslar) - min(yaslar)
            if yas_farki > 4:
                continue
            mod_setleri = [mods_by_id.get(s["id"], frozenset()) & tani_modulleri for s in kombo]
            ortak_modul = frozenset.intersection(*mod_setleri)
            if len(ortak_modul) < min_modul:
                continue
            puan = len(ortak_modul) * 10 - yas_farki * 2
            sonuclar.append({
                "uyeler":      list(kombo),
                "ortak_modul": ortak_modul,
                "yas_farki":   round(yas_farki, 2),
                "puan":        round(puan, 2),
            })
        sonuclar.sort(key=lambda x: (-x["puan"], x["yas_farki"]))
        return sonuclar[:10]

    sonuclar = _tara(2)
    if sonuclar:
        return sonuclar, len(uygun), 2

    # Fallback: 1 ortak modül
    sonuclar = _tara(1)
    return sonuclar, len(uygun), 1


# ── Akıllı Öneri Sekmesi ──────────────────────────────────────────────────────

def _show_oneri(students, mods_by_id, diags_by_id):
    from pages.lila_import import TANI_MODUL_MAP

    st.markdown(
        "<p style='color:#6B7A99;font-size:14px;margin-bottom:16px;'>"
        "Tanı ve grup büyüklüğü seçin — sistem yaşa ve ortak modüllere göre en uyumlu grupları sıralar."
        "</p>",
        unsafe_allow_html=True,
    )

    # Sistemde kayıtlı tanıları TANI_MODUL_MAP ile kesişime göre sırala
    mevcut_tanilar = sorted(
        {
            t
            for sid, ds in diags_by_id.items()
            for t in ds
            if t in TANI_MODUL_MAP
        },
        key=turkish_sort_key,
    )

    if not mevcut_tanilar:
        st.info("Sistemde henüz kayıtlı öğrenci bulunmuyor.")
        return

    # Kısa tanı adları (UI'da görünecek)
    TANI_KISA = {
        "Otizm Spektrum Bozukluğu Olan Bireyler İçin Destek Eğitim Programı":    "Otizm Spektrum Bozukluğu (OSB)",
        "Zihinsel Yetersizliği Olan Bireyler İçin Destek Eğitim Programı":        "Zihinsel Yetersizlik",
        "Öğrenme Güçlüğü Olan Bireyler İçin Destek Eğitim Programı":             "Öğrenme Güçlüğü",
        "Dil ve Konuşma Bozukluğu Olan Bireyler İçin Destek Eğitim Programı":    "Dil ve Konuşma Bozukluğu",
        "Bedensel Yetersizliği Olan Bireyler İçin Destek Eğitim Programı":        "Bedensel Yetersizlik",
        "İşitme Yetersizliği Olan Bireyler İçin Destek Eğitim Programı":          "İşitme Yetersizliği",
        "Görme Yetersizliği Olan Bireyler İçin Destek Eğitim Programı":           "Görme Yetersizliği",
    }

    col1, col2 = st.columns(2)
    with col1:
        tani_lblleri = [TANI_KISA.get(t, t) for t in mevcut_tanilar]
        tani_sec_lbl = st.selectbox(
            "Tanı",
            tani_lblleri,
            key="onr_tani",
        )
        tani_sec = mevcut_tanilar[tani_lblleri.index(tani_sec_lbl)]
    with col2:
        grup_boyutu = st.selectbox(
            "Grup büyüklüğü",
            [2, 3, 4, 5, 6],
            index=1,
            key="onr_boyut",
        )

    if st.button("🔍 Grupları Öner", key="onr_hesapla", type="primary", use_container_width=False):
        with st.spinner("Gruplar hesaplanıyor…"):
            sonuclar, uygun_sayi, min_modul = _onerici_hesapla(
                students, mods_by_id, diags_by_id, tani_sec, grup_boyutu
            )
        st.session_state["_onr_sonuclar"]    = sonuclar
        st.session_state["_onr_uygun_sayi"]  = uygun_sayi
        st.session_state["_onr_min_modul"]   = min_modul
        st.session_state["_onr_tani"]        = tani_sec
        st.session_state["_onr_boyut"]       = grup_boyutu

    # Sonuçları göster
    sonuclar   = st.session_state.get("_onr_sonuclar")
    uygun_sayi = st.session_state.get("_onr_uygun_sayi", 0)
    min_modul  = st.session_state.get("_onr_min_modul", 2)
    onr_tani   = st.session_state.get("_onr_tani", "")
    onr_boyut  = st.session_state.get("_onr_boyut", 0)

    if sonuclar is None:
        return

    if not sonuclar:
        if uygun_sayi < onr_boyut:
            st.warning(
                f"Seçili tanıda yeterli öğrenci yok. "
                f"({uygun_sayi} öğrenci bulundu, {onr_boyut} kişilik grup için en az {onr_boyut} gerekli)"
            )
        else:
            st.warning(
                "Kriterleri karşılayan grup bulunamadı. "
                "(Yaş farkı ≤4 yıl koşulunu sağlayan yeterli öğrenci yok)"
            )
        return

    fallback_notu = (
        '<div style="font-size:12px;color:#F59E0B;margin-bottom:8px;">'
        '⚠️ 2 ortak modülle uyumlu grup bulunamadı — 1 ortak modülle önerildi, puanlar daha düşük.'
        '</div>'
        if min_modul == 1 else ""
    )
    st.markdown(
        f"<div style='font-size:13px;color:#6B7A99;margin-bottom:6px;'>"
        f"<b>{len(sonuclar)}</b> öneri bulundu · {uygun_sayi} uygun öğrenci tarandı"
        f"</div>"
        f"{fallback_notu}",
        unsafe_allow_html=True,
    )

    for i, sn in enumerate(sonuclar):
        uyeler      = sn["uyeler"]
        ortak_modul = sorted(sn["ortak_modul"])
        yas_farki   = sn["yas_farki"]
        puan        = sn["puan"]

        mod_badges = "".join(
            f'<span class="mod-badge">{m}</span>' for m in ortak_modul
        )
        isimler = "  ·  ".join(u["name"] for u in uyeler)

        # Puan rengi
        puan_renk = "#22C55E" if puan >= 18 else "#F59E0B" if puan >= 10 else "#94A3B8"

        col_kart, col_btn = st.columns([8, 2])
        with col_kart:
            st.markdown(f"""
            <div class="oneri-kart">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <div class="oneri-rozet">#{i+1}</div>
                <div style="font-family:Sora,sans-serif;font-weight:600;
                     font-size:14px;color:#1A2B4C;flex:1;">{isimler}</div>
                <div style="font-size:12px;font-weight:700;color:{puan_renk};
                     background:rgba(56,201,192,.1);border-radius:20px;
                     padding:3px 10px;">Puan: {puan}</div>
              </div>
              <div style="margin-bottom:6px;">{mod_badges}</div>
              <div style="font-size:12px;color:#6B7A99;">
                🎂 {yas_farki} yıl yaş farkı &nbsp;·&nbsp;
                📚 {len(ortak_modul)} ortak modül &nbsp;·&nbsp;
                👥 {len(uyeler)} kişi
              </div>
            </div>""", unsafe_allow_html=True)
        with col_btn:
            st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
            if st.button("Bu grubu seç", key=f"onr_sec_{i}", use_container_width=True):
                # Manuel sekmeye yükle
                grup_uyeleri = []
                for u in uyeler:
                    sid = u["id"]
                    grup_uyeleri.append({
                        "id":          sid,
                        "name":        u["name"],
                        "dob":         u.get("dob"),
                        "rapor_bitis": u.get("rapor_bitis"),
                        "mod_adlari":  sorted(mods_by_id.get(sid, frozenset())),
                        "diag_adlari": sorted(diags_by_id.get(sid, frozenset())),
                    })
                st.session_state["srch_grup_uyeleri"] = grup_uyeleri
                st.session_state["_onr_aktif_tab"]    = 0   # Manuel sekmeye geç
                st.session_state["_rerun_tab"]        = 2
                st.rerun()


# ── Manuel Oluştur Sekmesi ────────────────────────────────────────────────────

def _show_manuel(students, mods_by_id, diags_by_id, id_by_name):
    grup = st.session_state["srch_grup_uyeleri"]
    secilen_isimler = {u["name"] for u in grup}

    st.markdown("#### 👤 Grup üyelerini seçin")
    st.caption("Parantez içi rapor durumu gösterir · Sadece uyumlu öğrenciler listelenir")

    # ── Seçili üyeler ─────────────────────────────────────────────────────────
    for i, uye in enumerate(grup):
        mod_badges = "".join(
            f'<span class="mod-badge">{m}</span>'
            for m in uye.get("mod_adlari", [])
        )
        renk       = rapor_renk(uye.get("rapor_bitis"))
        etiket_str = rapor_etiketi(uye.get("rapor_bitis"))
        is_last    = (i == len(grup) - 1)

        col_kart, col_x = st.columns([10, 1])
        with col_kart:
            etiket_span = (
                f'<span style="font-size:12px;font-weight:400;color:{renk};margin-left:4px;">'
                f'{etiket_str}</span>'
                if etiket_str else ""
            )
            st.markdown(f"""
            <div class="oyuncu-kart">
              <div class="oyuncu-numara">{i+1}</div>
              <div style="flex:1">
                <div class="oyuncu-ad">
                  <span style="display:inline-block;width:8px;height:8px;border-radius:50%;
                    background:{renk};margin-right:7px;vertical-align:middle;"></span>
                  {uye["name"]}{etiket_span}
                </div>
                <div style="margin-top:4px;">{mod_badges}</div>
              </div>
            </div>""", unsafe_allow_html=True)
        with col_x:
            if is_last:
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                if st.button("✕", key=f"srch_sil_{i}", help="Bu üyeyi çıkar"):
                    st.session_state["srch_grup_uyeleri"].pop()
                    st.session_state["_rerun_tab"] = 2
                    st.rerun()

    # ── Sonraki aday hesaplama ────────────────────────────────────────────────
    if len(grup) < 10:
        etiket_lbl = "İlk öğrenciyi seçin" if not grup else f"{len(grup)+1}. üyeyi seçin"

        if not grup:
            aday_isimler = [s["name"] for s in students if s["name"] not in secilen_isimler]
        else:
            mod_setleri  = [mods_by_id.get(u["id"],  frozenset()) for u in grup]
            diag_setleri = [diags_by_id.get(u["id"], frozenset()) for u in grup]
            mevcut_modler= frozenset.intersection(*mod_setleri)
            mevcut_diag  = frozenset.intersection(*diag_setleri)

            s_by_id2 = {s["id"]: s for s in students}
            doblar   = [s_by_id2.get(u["id"], u).get("dob") for u in grup]
            doblar   = [d for d in doblar if d]
            yas_min  = min(age_years(d) for d in doblar) if doblar else 0
            yas_max  = max(age_years(d) for d in doblar) if doblar else 100

            aday_isimler = []
            for s in students:
                if s["name"] in secilen_isimler:
                    continue

                s_mods  = mods_by_id.get(s["id"],  frozenset())
                s_diags = diags_by_id.get(s["id"], frozenset())

                # 1. Tanı uyumu — ortak tanı zorunlu
                if not mevcut_diag or not s_diags or not (s_diags & mevcut_diag):
                    continue

                # 2. Modül uyumu — ortak tanıdan gelen modüller eşleşmeli
                ortak_tani_adaylar = s_diags & mevcut_diag
                from pages.lila_import import TANI_MODUL_MAP
                ortak_tani_modulleri = frozenset(
                    m for t in ortak_tani_adaylar
                    for m in TANI_MODUL_MAP.get(t, [])
                )
                if not (s_mods & mevcut_modler & ortak_tani_modulleri):
                    continue

                # 3. Yaş uyumu — yeni üye eklenince max fark 4 yılı geçmemeli
                s_yas = age_years(s.get("dob"))
                if s_yas is None:
                    continue
                if max(yas_max, s_yas) - min(yas_min, s_yas) > 4:
                    continue

                aday_isimler.append(s["name"])

        aday_isimler.sort(key=turkish_sort_key)

        s_map    = {s["name"]: s for s in students}
        aday_lst = []
        aday_map = {}
        for isim in aday_isimler:
            s   = s_map.get(isim, {})
            et  = rapor_etiketi(s.get("rapor_bitis", ""))
            lbl = f"{isim}{et}"
            aday_lst.append(lbl)
            aday_map[lbl] = isim

        siradaki_lbl = st.selectbox(
            etiket_lbl,
            ["— Seçiniz —"] + aday_lst,
            key=f"srch_siradaki_{len(grup)}",
            label_visibility="visible",
        )

        if siradaki_lbl != "— Seçiniz —":
            siradaki = aday_map.get(siradaki_lbl, siradaki_lbl)
            s  = s_map.get(siradaki, {})
            sid = s.get("id")
            st.session_state["srch_grup_uyeleri"].append({
                "id":          sid,
                "name":        siradaki,
                "dob":         s.get("dob"),
                "rapor_bitis": s.get("rapor_bitis"),
                "mod_adlari":  sorted(mods_by_id.get(sid, frozenset())),
                "diag_adlari": sorted(diags_by_id.get(sid, frozenset())),
            })
            st.session_state["_rerun_tab"] = 2
            st.rerun()

        if not aday_lst and grup:
            st.info("Bu gruba eklenebilecek uyumlu öğrenci bulunamadı.")

    # ── Özet + Kaydet ─────────────────────────────────────────────────────────
    if len(grup) >= 2:
        st.divider()

        mod_setleri  = [mods_by_id.get(u["id"],  frozenset()) for u in grup]
        diag_setleri = [diags_by_id.get(u["id"], frozenset()) for u in grup]
        ortak_modul  = frozenset.intersection(*mod_setleri)
        ortak_tani   = frozenset.intersection(*diag_setleri)

        s_by_id = {s["id"]: s for s in students}
        doblar  = [s_by_id.get(u["id"], u).get("dob") for u in grup]
        doblar  = [d for d in doblar if d]
        yas_farki = None
        if len(doblar) == len(grup):
            yaslar    = [age_years(d) for d in doblar]
            yas_farki = round(max(yaslar) - min(yaslar), 2)

        from pages.lila_import import TANI_MODUL_MAP
        uyarilar = []
        if not ortak_tani:
            uyarilar.append("⚠️ Ortak tanı yok — bu öğrenciler birlikte gruplanamaz.")
        else:
            ortak_tani_modulleri = frozenset(
                m for t in ortak_tani for m in TANI_MODUL_MAP.get(t, [])
            )
            if not (ortak_modul & ortak_tani_modulleri):
                uyarilar.append("⚠️ Ortak tanıya ait ortak modül yok — bu öğrenciler birlikte gruplanamaz.")
        if not ortak_modul:
            uyarilar.append("⚠️ Ortak modül yok — bu öğrenciler birlikte gruplanamaz.")
        if yas_farki is not None and yas_farki > 4:
            uyarilar.append(f"⚠️ Yaş farkı {yas_farki} yıl — 4 yılı aşıyor.")

        if uyarilar:
            for u in uyarilar:
                st.warning(u)
        else:
            mod_badges  = "".join(
                f'<span class="mod-badge">{m}</span>' for m in sorted(ortak_modul)
            )
            isimler_str = "  ·  ".join(u["name"] for u in grup)
            yas_str     = f"{yas_farki} yıl fark" if yas_farki is not None else "—"

            st.markdown(f"""
            <div class="grup-ozet-kart">
              <div style="font-family:Sora,sans-serif;font-weight:700;font-size:14px;
                   color:#1A2B4C;margin-bottom:8px;">✅ Grup oluşturulabilir</div>
              <div style="font-size:14px;color:#1A2B4C;margin-bottom:10px;font-weight:500;">
                {isimler_str}
              </div>
              <div style="margin-bottom:8px;">
                <span style="font-size:12px;color:#6B7A99;">Ortak modüller:</span><br>
                {mod_badges}
              </div>
              <div style="font-size:12px;color:#6B7A99;">
                🎂 {yas_str} &nbsp;·&nbsp; 👥 {len(grup)} kişi
              </div>
            </div>""", unsafe_allow_html=True)

            col_not, col_kaydet = st.columns([3, 1])
            with col_not:
                not_val = st.text_input(
                    "Not (isteğe bağlı)",
                    key="srch_not",
                    placeholder="Grup notu..."
                )
            with col_kaydet:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                if st.button("⭐ Grubu Kaydet", key="srch_kaydet",
                             type="primary", use_container_width=True):
                    payload = {
                        "ogrenciler": " | ".join(u["name"] for u in grup),
                        "moduller":   " / ".join(sorted(ortak_modul)),
                        "saat":       None,
                        "notlar":     not_val or "",
                        "liste_adi":  "",
                    }
                    if api.create_saved_group(payload):
                        st.success("✅ Grup kaydedildi!")
                        st.session_state["srch_grup_uyeleri"] = []
                        st.session_state["_rerun_tab"] = 2
                        st.rerun()


# ── Ana sayfa ─────────────────────────────────────────────────────────────────

def show():
    st.markdown("""
    <style>
    .oyuncu-kart{background:white;border:2px solid #38C9C0;border-radius:14px;
      padding:12px 16px;margin-bottom:8px;display:flex;align-items:center;gap:12px;}
    .oyuncu-numara{background:linear-gradient(135deg,#38C9C0,#2756D6);color:white;
      border-radius:50%;width:28px;height:28px;display:flex;align-items:center;
      justify-content:center;font-family:Sora,sans-serif;font-weight:700;
      font-size:13px;flex-shrink:0;}
    .oyuncu-ad{font-family:Sora,sans-serif;font-weight:600;font-size:15px;color:#1A2B4C;}
    .mod-badge{display:inline-block;background:rgba(56,201,192,.12);color:#2B7A76;
      border-radius:20px;padding:3px 12px;font-size:12px;font-weight:500;margin:2px 3px;
      border:1px solid rgba(56,201,192,.25);}
    .grup-ozet-kart{background:linear-gradient(135deg,rgba(56,201,192,.08),rgba(39,86,214,.06));
      border:1.5px solid rgba(56,201,192,.3);border-radius:16px;padding:20px 24px;margin:16px 0;}
    .oneri-kart{background:white;border:1.5px solid rgba(56,201,192,.35);border-radius:14px;
      padding:14px 18px;margin-bottom:10px;transition:box-shadow .2s;}
    .oneri-rozet{background:linear-gradient(135deg,#38C9C0,#2756D6);color:white;
      border-radius:8px;padding:2px 10px;font-family:Sora,sans-serif;font-weight:700;
      font-size:13px;flex-shrink:0;}
    </style>""", unsafe_allow_html=True)

    # ── Veri yükle (cache'li) ─────────────────────────────────────────────────
    students, mods_by_id, diags_by_id, id_by_name = _load()

    if not students:
        st.info("Önce Lila'dan öğrenci aktarın veya manuel ekleyin.")
        return

    # Session state
    if "srch_grup_uyeleri" not in st.session_state:
        st.session_state["srch_grup_uyeleri"] = []

    # Akıllı öneri "Bu grubu seç" butonundan geliniyorsa Manuel sekmeyi aç
    aktif_tab_idx = st.session_state.pop("_onr_aktif_tab", 1)

    # Sekme başlıkları
    tab_manuel, tab_oneri = st.tabs(["🔎 Manuel Oluştur", "✨ Akıllı Öneri"])

    with tab_oneri:
        _show_oneri(students, mods_by_id, diags_by_id)

    with tab_manuel:
        if st.button("🧹 Sıfırla", key="srch_clear"):
            st.session_state.pop("srch_grup_uyeleri", None)
            st.session_state["_rerun_tab"] = 2
            st.rerun()
        _show_manuel(students, mods_by_id, diags_by_id, id_by_name)
