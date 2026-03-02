"""
Grup Oluştur.
Filtre sırası: 1) ORTAK TANI (her iki tarafta da tanı varsa kesişim zorunlu)
               2) ORTAK MODÜL (tanıdan türeyen grup modülleri)
               3) MAX 3 YAŞ FARKI

Optimizasyon: öğrenci verisi session_state'te cache'lenir, her sekme değişiminde
yeniden çekilmez. Rerun sonrası invalidate edilir (import/güncelleme).
"""
import streamlit as st
from datetime import date
import api_client as api


def yas(dob_str):
    if not dob_str: return None
    try: return (date.today() - date.fromisoformat(dob_str)).days / 365.25
    except: return None

def rapor_renk(r):
    if not r: return "#22C55E"
    try:
        k = (date.fromisoformat(r) - date.today()).days
        return "#EF4444" if k < 0 else "#F59E0B" if k <= 30 else "#22C55E"
    except: return "#22C55E"

def rapor_etiket(r):
    if not r: return ""
    try:
        k = (date.fromisoformat(r) - date.today()).days
        if k < 0:   return " (rapor bitti)"
        if k <= 30: return f" ({k} gün)"
        return ""
    except: return ""

def tr_sort(s):
    return s.lower().translate(str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosucgiosu"))


def _load_students():
    """
    Öğrenci verisini session_state'te cache'le.
    'students_cache_bust' değişince yeniden yükler (Lila import sonrası).
    """
    bust = st.session_state.get("students_cache_bust", 0)
    if st.session_state.get("_students_bust") != bust or "_students_data" not in st.session_state:
        raw = api.get_students()
        mods_by_id  = {s["id"]: frozenset(m["name"] for m in s.get("modules",[])) for s in raw}
        diags_by_id = {s["id"]: frozenset(d["name"] for d in s.get("diagnoses",[])) for s in raw}
        st.session_state["_students_data"]  = raw
        st.session_state["_mods_by_id"]    = mods_by_id
        st.session_state["_diags_by_id"]   = diags_by_id
        st.session_state["_students_bust"] = bust
    return (
        st.session_state["_students_data"],
        st.session_state["_mods_by_id"],
        st.session_state["_diags_by_id"],
    )


def show():
    st.markdown("""
    <style>
    .oyuncu-kart{background:white;border:1.5px solid rgba(66,184,177,.35);border-radius:12px;
      padding:10px 14px;margin-bottom:7px;display:flex;align-items:center;gap:10px;}
    .oyuncu-numara{background:linear-gradient(135deg,#42B8B1,#2B52C4);color:white;border-radius:50%;
      min-width:28px;width:28px;height:28px;display:flex;align-items:center;justify-content:center;
      font-family:Sora,sans-serif;font-weight:700;font-size:13px;flex-shrink:0;}
    .oyuncu-ad{font-family:Sora,sans-serif;font-weight:600;font-size:14px;color:#1A2B4C;line-height:1.3;}
    .oyuncu-sub{font-size:11px;color:#6B7A99;margin-top:2px;}
    .mod-badge{display:inline-block;background:rgba(66,184,177,.12);color:#2B7A76;border-radius:20px;
      padding:1px 9px;font-size:11px;font-weight:500;margin:2px 3px;border:1px solid rgba(66,184,177,.2);}
    .grup-ozet{background:linear-gradient(135deg,rgba(66,184,177,.08),rgba(43,82,196,.05));
      border:1.5px solid rgba(66,184,177,.28);border-radius:14px;padding:16px 20px;margin:12px 0;}
    </style>""", unsafe_allow_html=True)

    students, mods_by_id, diags_by_id = _load_students()

    if not students:
        st.info("Önce Lila'dan öğrenci aktarın.")
        return

    if "grup_uyeleri" not in st.session_state:
        st.session_state["grup_uyeleri"] = []
    grup = st.session_state["grup_uyeleri"]
    secilen_ids = {u["id"] for u in grup}

    bc1, bc2 = st.columns([6, 1])
    with bc1: st.header("🔎 Grup Oluştur")
    with bc2:
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        if st.button("🧹 Sıfırla", use_container_width=True):
            st.session_state["grup_uyeleri"] = []
            st.rerun()

    # ── Seçili üyeler ─────────────────────────────────────────────────────────
    for i, u in enumerate(grup):
        mod_badges = "".join(f'<span class="mod-badge">{m}</span>' for m in u["mod_adlari"])
        renk   = rapor_renk(u.get("rapor_bitis"))
        etiket = rapor_etiket(u.get("rapor_bitis"))
        yas_str = f"{yas(u.get('dob')):.0f} yaş" if yas(u.get("dob")) else ""
        sub = "  ·  ".join(p for p in [yas_str, etiket.strip()] if p)

        kc, kx = st.columns([11, 1])
        with kc:
            st.markdown(f"""
            <div class="oyuncu-kart">
              <div class="oyuncu-numara">{i+1}</div>
              <div style="flex:1;min-width:0;">
                <div class="oyuncu-ad">
                  <span style="display:inline-block;width:7px;height:7px;border-radius:50%;
                    background:{renk};margin-right:5px;vertical-align:middle;"></span>{u['name']}
                </div>
                <div class="oyuncu-sub">{sub}</div>
                <div style="margin-top:4px;">{mod_badges}</div>
              </div>
            </div>""", unsafe_allow_html=True)
        with kx:
            if i == len(grup) - 1:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                if st.button("✕", key=f"cikart_{i}"):
                    st.session_state["grup_uyeleri"].pop()
                    st.rerun()

    # ── Aday hesaplama ────────────────────────────────────────────────────────
    if len(grup) < 10:
        baslik = "👤 İlk öğrenciyi seçin" if not grup else f"➕ {len(grup)+1}. üyeyi seçin"
        st.caption(baslik + (" · tanı eşleşmesi → ortak modül → max 3 yaş" if grup else ""))

        if not grup:
            adaylar = [s for s in students if s["id"] not in secilen_ids]
        else:
            # Grubun mevcut kesişimleri
            diag_setleri = [diags_by_id.get(u["id"], frozenset()) for u in grup]
            mod_setleri  = [mods_by_id.get(u["id"],  frozenset()) for u in grup]
            ortak_tani   = frozenset.intersection(*diag_setleri)
            ortak_modul  = frozenset.intersection(*mod_setleri)

            doblar  = [u["dob"] for u in grup if u.get("dob")]
            yas_min = min(yas(d) for d in doblar) if doblar else 0
            yas_max = max(yas(d) for d in doblar) if doblar else 100

            adaylar = []
            for s in students:
                if s["id"] in secilen_ids:
                    continue

                s_diags = diags_by_id.get(s["id"], frozenset())
                s_mods  = mods_by_id.get(s["id"],  frozenset())

                # ── ADIM 1: TANI KONTROLÜ ──────────────────────────────────
                # Grupta da adayda da tanı varsa → mutlaka ortak tanı olmalı.
                # Eğer ortak_tani boşsa (grupta tanısız biri var), tanı engellemez.
                if ortak_tani and s_diags and not (s_diags & ortak_tani):
                    continue   # tanılar uyuşmuyor → modüle bile bakma

                # ── ADIM 2: MODÜL KONTROLÜ ─────────────────────────────────
                # Adayın modülleri ile grubun ortak modül kümesi kesişmeli
                if not (s_mods & ortak_modul):
                    continue

                # ── ADIM 3: YAŞ KONTROLÜ ───────────────────────────────────
                s_yas = yas(s.get("dob"))
                if s_yas is not None:
                    if max(yas_max, s_yas) - min(yas_min, s_yas) > 3:
                        continue

                adaylar.append(s)

        if not adaylar and grup:
            st.info("Bu gruba eklenebilecek uyumlu öğrenci bulunamadı.")
        elif adaylar:
            aday_liste = ["— Seçiniz —"]
            aday_map   = {}
            for s in sorted(adaylar, key=lambda x: tr_sort(x["name"])):
                sy  = yas(s.get("dob"))
                ret = rapor_etiket(s.get("rapor_bitis"))
                et  = s["name"]
                if sy:  et += f"  ·  {sy:.0f} yaş"
                if ret: et += ret
                aday_liste.append(et)
                aday_map[et] = s

            sec = st.selectbox("", aday_liste, key=f"aday_{len(grup)}", label_visibility="collapsed")
            if sec != "— Seçiniz —":
                s = aday_map[sec]
                st.session_state["grup_uyeleri"].append({
                    "id":          s["id"],
                    "name":        s["name"],
                    "dob":         s.get("dob"),
                    "rapor_bitis": s.get("rapor_bitis"),
                    "mod_adlari":  sorted(mods_by_id.get(s["id"], frozenset())),
                    "diag_adlari": sorted(diags_by_id.get(s["id"], frozenset())),
                })
                st.rerun()

    # ── Özet ve kaydet ────────────────────────────────────────────────────────
    if len(grup) >= 2:
        st.divider()

        mod_setleri  = [mods_by_id.get(u["id"], frozenset()) for u in grup]
        diag_setleri = [diags_by_id.get(u["id"], frozenset()) for u in grup]
        ortak_modul  = frozenset.intersection(*mod_setleri)
        ortak_tani   = frozenset.intersection(*diag_setleri)

        doblar = [u["dob"] for u in grup if u.get("dob")]
        yas_farki = None
        if len(doblar) == len(grup):
            yaslar = [yas(d) for d in doblar]
            yas_farki = round(max(yaslar) - min(yaslar), 1)

        uyarilar = []
        # Tanı uyumsuzluğu
        if all(diags_by_id.get(u["id"]) for u in grup) and not ortak_tani:
            uyarilar.append("⚠️ Ortak tanı yok — bu öğrenciler birlikte gruplanamaz.")
        if not ortak_modul:
            uyarilar.append("⚠️ Ortak modül yok — gruplanamaz.")
        if yas_farki is not None and yas_farki > 3:
            uyarilar.append(f"⚠️ Yaş farkı {yas_farki} yıl — 3 yılı aşıyor.")

        if uyarilar:
            for u in uyarilar: st.warning(u)
        else:
            mod_badges = "".join(f'<span class="mod-badge">{m}</span>' for m in sorted(ortak_modul))
            isimler    = "  ·  ".join(u["name"] for u in grup)
            yas_str    = f"{yas_farki} yıl fark" if yas_farki is not None else "—"

            st.markdown(f"""
            <div class="grup-ozet">
              <div style="font-family:Sora,sans-serif;font-weight:700;font-size:14px;color:#1A2B4C;margin-bottom:6px;">
                ✅ Grup oluşturulabilir
              </div>
              <div style="font-size:13px;color:#1A2B4C;font-weight:500;margin-bottom:8px;">{isimler}</div>
              <div style="margin-bottom:6px;"><span style="font-size:11px;color:#6B7A99;">Ortak modüller:</span><br>{mod_badges}</div>
              <div style="font-size:12px;color:#6B7A99;">🎂 {yas_str} &nbsp;·&nbsp; 👥 {len(grup)} kişi</div>
            </div>""", unsafe_allow_html=True)

            nc, nkay = st.columns([3, 1])
            with nc:
                not_val = st.text_input("Not (isteğe bağlı)", placeholder="Grup notu...", key="grup_not")
            with nkay:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                if st.button("⭐ Kaydet", type="primary", use_container_width=True, key="grup_kaydet"):
                    if api.create_saved_group({
                        "ogrenciler": " | ".join(u["name"] for u in grup),
                        "moduller":   " / ".join(sorted(ortak_modul)),
                        "saat":       None,
                        "notlar":     not_val or "",
                        "liste_adi":  "",
                    }):
                        st.success("✅ Kaydedildi!")
                        st.session_state["grup_uyeleri"] = []
                        st.rerun()
