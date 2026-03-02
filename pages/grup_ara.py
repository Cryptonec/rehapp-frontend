"""
Grup Oluştur.
Filtre: 1) ORTAK TANI  2) ORTAK MODÜL  3) MAX 3 YAŞ FARKI

Optimizasyon (eski projeden):
- build_student_records: tek API çağrısıyla tüm öğrenci + modül + tanı verisini çeker
- frozenset ile O(min) kesişim
- session_state cache: students_cache_bust değişince invalidate
- records listesi önceden hazırlanır, her filtre O(n) linear scan
"""
import streamlit as st
from datetime import date
import api_client as api


def _yas(dob_str):
    if not dob_str: return None
    try: return (date.today() - date.fromisoformat(dob_str)).days / 365.25
    except: return None

def _rapor_renk(r):
    if not r: return "#22C55E"
    try:
        k = (date.fromisoformat(r) - date.today()).days
        return "#EF4444" if k < 0 else "#F59E0B" if k <= 30 else "#22C55E"
    except: return "#22C55E"

def _rapor_etiket(r):
    if not r: return ""
    try:
        k = (date.fromisoformat(r) - date.today()).days
        if k < 0:   return " (rapor bitti)"
        if k <= 30: return f" ({k} gün)"
        return ""
    except: return ""

def _tr_sort(s):
    return s.lower().translate(str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosucgiosu"))


def _build_records():
    """
    Eski projeden: tek seferde tüm veriyi çek, records listesine dönüştür.
    Her record: {id, name, dob, rapor_bitis, mods: frozenset, diags: frozenset}
    session_state'te cache'lenir; students_cache_bust değişince yenilenir.
    """
    bust = st.session_state.get("students_cache_bust", 0)
    if st.session_state.get("_rec_bust") == bust and "_records" in st.session_state:
        return st.session_state["_records"]

    raw = api.get_students()
    records = []
    for s in raw:
        records.append({
            "id":          s["id"],
            "name":        s["name"],
            "dob":         s.get("dob"),
            "rapor_bitis": s.get("rapor_bitis"),
            "mods":        frozenset(m["name"] for m in s.get("modules",  [])),
            "diags":       frozenset(d["name"] for d in s.get("diagnoses", [])),
        })
    st.session_state["_records"]  = records
    st.session_state["_rec_bust"] = bust
    return records


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

    records = _build_records()
    if not records:
        st.info("Önce Lila'dan öğrenci aktarın.")
        return

    if "grup_uyeleri" not in st.session_state:
        st.session_state["grup_uyeleri"] = []
    grup = st.session_state["grup_uyeleri"]
    secilen_ids = frozenset(u["id"] for u in grup)

    # Record hızlı erişim map'i
    rec_by_id = {r["id"]: r for r in records}

    bc1, bc2 = st.columns([6, 1])
    with bc1: st.header("🔎 Grup Oluştur")
    with bc2:
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        if st.button("🧹 Sıfırla", use_container_width=True):
            st.session_state["grup_uyeleri"] = []
            st.rerun()

    # ── Seçili üyeler ─────────────────────────────────────────────────────────
    for i, u in enumerate(grup):
        mod_badges = "".join(f'<span class="mod-badge">{m}</span>' for m in sorted(u["mods"]))
        renk   = _rapor_renk(u.get("rapor_bitis"))
        etiket = _rapor_etiket(u.get("rapor_bitis"))
        yas_v  = _yas(u.get("dob"))
        yas_str = f"{yas_v:.0f} yaş" if yas_v else ""
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
        st.caption(baslik + (" · tanı → modül → yaş filtresi" if grup else ""))

        if not grup:
            adaylar = [r for r in records if r["id"] not in secilen_ids]
        else:
            # Grubun kesişimleri — frozenset O(min(n,m))
            diag_setleri = [rec_by_id[u["id"]]["diags"] for u in grup]
            mod_setleri  = [rec_by_id[u["id"]]["mods"]  for u in grup]
            ortak_tani   = frozenset.intersection(*diag_setleri)
            ortak_modul  = frozenset.intersection(*mod_setleri)

            doblar  = [u["dob"] for u in grup if u.get("dob")]
            yas_vals = [_yas(d) for d in doblar if _yas(d) is not None]
            yas_min = min(yas_vals) if yas_vals else 0
            yas_max = max(yas_vals) if yas_vals else 100

            adaylar = []
            for r in records:
                if r["id"] in secilen_ids: continue

                # ── 1. TANI KONTROLÜ ───────────────────────────────────────
                # Her iki tarafta tanı varsa kesişim zorunlu.
                # Tanısız öğrenci gruba girebilir (Lila'da tanı gelmemiş olabilir).
                if ortak_tani and r["diags"] and not (r["diags"] & ortak_tani):
                    continue  # tanı uyuşmuyor → modüle bakma

                # ── 2. MODÜL KONTROLÜ ──────────────────────────────────────
                if not (r["mods"] & ortak_modul):
                    continue

                # ── 3. YAŞ KONTROLÜ ────────────────────────────────────────
                r_yas = _yas(r.get("dob"))
                if r_yas is not None:
                    if max(yas_max, r_yas) - min(yas_min, r_yas) > 3:
                        continue

                adaylar.append(r)

        if not adaylar and grup:
            st.info("Bu gruba eklenebilecek uyumlu öğrenci bulunamadı.")
        elif adaylar:
            aday_liste = ["— Seçiniz —"]
            aday_map   = {}
            for r in sorted(adaylar, key=lambda x: _tr_sort(x["name"])):
                yas_v = _yas(r.get("dob"))
                et = r["name"]
                if yas_v: et += f"  ·  {yas_v:.0f} yaş"
                ret = _rapor_etiket(r.get("rapor_bitis"))
                if ret: et += ret
                aday_liste.append(et)
                aday_map[et] = r

            sec = st.selectbox("", aday_liste, key=f"aday_{len(grup)}", label_visibility="collapsed")
            if sec != "— Seçiniz —":
                r = aday_map[sec]
                st.session_state["grup_uyeleri"].append({
                    "id":          r["id"],
                    "name":        r["name"],
                    "dob":         r.get("dob"),
                    "rapor_bitis": r.get("rapor_bitis"),
                    "mods":        r["mods"],
                    "diags":       r["diags"],
                })
                st.rerun()

    # ── Özet ve kaydet ────────────────────────────────────────────────────────
    if len(grup) >= 2:
        st.divider()

        ortak_modul = frozenset.intersection(*[rec_by_id[u["id"]]["mods"]  for u in grup])
        ortak_tani  = frozenset.intersection(*[rec_by_id[u["id"]]["diags"] for u in grup])

        doblar = [u["dob"] for u in grup if u.get("dob")]
        yas_farki = None
        if len(doblar) == len(grup):
            yaslar = [_yas(d) for d in doblar if _yas(d)]
            if yaslar: yas_farki = round(max(yaslar) - min(yaslar), 1)

        uyarilar = []
        if all(rec_by_id[u["id"]]["diags"] for u in grup) and not ortak_tani:
            uyarilar.append("⚠️ Ortak tanı yok — bu öğrenciler birlikte gruplanamaz.")
        if not ortak_modul:
            uyarilar.append("⚠️ Ortak modül yok — gruplanamaz.")
        if yas_farki is not None and yas_farki > 3:
            uyarilar.append(f"⚠️ Yaş farkı {yas_farki} yıl — 3 yılı aşıyor.")

        if uyarilar:
            for w in uyarilar: st.warning(w)
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
