"""
Grup Oluştur — Eski proje mantığı klonu.

Performans optimizasyonları:
- Öğrenci + modül + tanı verisi TEK seferde API'den çekilir, session_state'te cache'lenir
- frozenset ile O(1) kesişim kontrolü
- Aday listesi her seçimde sadece mevcut gruptan türetilir, tüm öğrenciler taranmaz
- Grup üyeleri session_state["srch_grup_uyeleri"]'nde tutulur (eski proje adı korundu)
- Cache bust: Lila import sonrası students_cache_bust +1 → veri yeniden çekilir
"""
import streamlit as st
from datetime import date
import api_client as api


# ── Yardımcı fonksiyonlar ─────────────────────────────────────────────────────

def age_years(dob_str):
    if not dob_str: return None
    try: return (date.today() - date.fromisoformat(dob_str)).days / 365.25
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
    </style>""", unsafe_allow_html=True)

    # Sıfırla butonu
    if st.button("🧹 Sıfırla", key="srch_clear"):
        st.session_state.pop("srch_grup_uyeleri", None)
        st.rerun()

    # ── Veri yükle (cache'li) ─────────────────────────────────────────────────
    students, mods_by_id, diags_by_id, id_by_name = _load()

    if not students:
        st.info("Önce Lila'dan öğrenci aktarın veya manuel ekleyin.")
        return

    # Session state
    if "srch_grup_uyeleri" not in st.session_state:
        st.session_state["srch_grup_uyeleri"] = []

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
        renk      = rapor_renk(uye.get("rapor_bitis"))
        etiket_str= rapor_etiketi(uye.get("rapor_bitis"))
        is_last   = (i == len(grup) - 1)

        col_kart, col_x = st.columns([10, 1])
        with col_kart:
            st.markdown(f"""
            <div class="oyuncu-kart">
              <div class="oyuncu-numara">{i+1}</div>
              <div style="flex:1">
                <div class="oyuncu-ad">
                  <span style="display:inline-block;width:8px;height:8px;border-radius:50%;
                    background:{renk};margin-right:7px;vertical-align:middle;"></span>
                  {uye["name"]}
                  <span style="font-size:12px;font-weight:400;color:{renk};margin-left:4px;">
                    {etiket_str}
                  </span>
                </div>
                <div style="margin-top:4px;">{mod_badges}</div>
              </div>
            </div>""", unsafe_allow_html=True)
        with col_x:
            if is_last:
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                if st.button("✕", key=f"srch_sil_{i}", help="Bu üyeyi çıkar"):
                    st.session_state["srch_grup_uyeleri"].pop()
                    st.rerun()

    # ── Sonraki aday hesaplama ────────────────────────────────────────────────
    if len(grup) < 10:
        etiket_lbl = "İlk öğrenciyi seçin" if not grup else f"{len(grup)+1}. üyeyi seçin"

        if not grup:
            # İlk seçimde herkes
            aday_isimler = [s["name"] for s in students if s["name"] not in secilen_isimler]

        else:
            # Grubun mevcut kesişimleri — frozenset, O(1)
            mod_setleri  = [mods_by_id.get(u["id"],  frozenset()) for u in grup]
            diag_setleri = [diags_by_id.get(u["id"], frozenset()) for u in grup]
            mevcut_modler= frozenset.intersection(*mod_setleri)
            mevcut_diag  = frozenset.intersection(*diag_setleri)

            doblar   = [u["dob"] for u in grup if u.get("dob")]
            yas_min  = min(age_years(d) for d in doblar) if doblar else 0
            yas_max  = max(age_years(d) for d in doblar) if doblar else 100

            aday_isimler = []
            for s in students:
                if s["name"] in secilen_isimler:
                    continue

                s_mods  = mods_by_id.get(s["id"],  frozenset())
                s_diags = diags_by_id.get(s["id"], frozenset())

                # 1. Modül uyumu — ortak modül kalmalı
                if not (s_mods & mevcut_modler):
                    continue

                # 2. Tanı uyumu — her iki tarafta tanı varsa kesişim zorunlu
                if mevcut_diag and s_diags and not (s_diags & mevcut_diag):
                    continue

                # 3. Yaş uyumu — yeni üye eklenince max fark 3 yılı geçmemeli
                s_yas = age_years(s.get("dob"))
                if s_yas is None:
                    continue
                if max(yas_max, s_yas) - min(yas_min, s_yas) > 3:
                    continue

                aday_isimler.append(s["name"])

        # Türkçe sırala
        aday_isimler.sort(key=turkish_sort_key)

        # Dropdown etiketi — rapor durumu
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
            s = s_map.get(siradaki, {})
            sid = s.get("id")
            st.session_state["srch_grup_uyeleri"].append({
                "id":          sid,
                "name":        siradaki,
                "dob":         s.get("dob"),
                "rapor_bitis": s.get("rapor_bitis"),
                "mod_adlari":  sorted(mods_by_id.get(sid, frozenset())),
                "diag_adlari": sorted(diags_by_id.get(sid, frozenset())),
            })
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

        doblar = [u["dob"] for u in grup if u.get("dob")]
        yas_farki = None
        if len(doblar) == len(grup):
            yaslar    = [age_years(d) for d in doblar]
            yas_farki = round(max(yaslar) - min(yaslar), 2)

        # Uyarı kontrolleri
        uyarilar = []
        if all(diags_by_id.get(u["id"]) for u in grup) and not ortak_tani:
            uyarilar.append("⚠️ Ortak tanı yok — bu öğrenciler birlikte gruplanamaz.")
        if not ortak_modul:
            uyarilar.append("⚠️ Ortak modül yok — bu öğrenciler birlikte gruplanamaz.")
        if yas_farki is not None and yas_farki > 3:
            uyarilar.append(f"⚠️ Yaş farkı {yas_farki} yıl — 3 yılı aşıyor.")

        if uyarilar:
            for u in uyarilar:
                st.warning(u)
        else:
            mod_badges = "".join(
                f'<span class="mod-badge">{m}</span>'
                for m in sorted(ortak_modul)
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
                        st.rerun()
