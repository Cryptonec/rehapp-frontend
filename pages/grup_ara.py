"""
Grup Oluştur — Harf oyunu mantığı:
1. Bir öğrenci seç
2. O öğrencinin modülleriyle uyumlu, max 3 yaş farkı olan öğrenciler otomatik listelenir
3. Birden fazla grup arkadaşı seçilebilir
4. Uyumluluk anlık kontrol edilir
"""
import streamlit as st
from datetime import date
import api_client as api


def yas(dob_str):
    if not dob_str:
        return None
    try:
        d = date.fromisoformat(dob_str)
        return (date.today() - d).days / 365.25
    except:
        return None


def show():
    st.header("🔎 Grup Oluştur")

    students = api.get_students()
    if not students:
        st.info("Önce Lila'dan öğrenci aktarın veya manuel ekleyin.")
        return

    # Öğrenci adı → obje map
    s_map = {s["name"]: s for s in students}

    # ── ADIM 1: Ana öğrenci seç ───────────────────────────────────────────────
    st.markdown("""
    <div style='background:white;border-radius:14px;padding:20px 24px;
         border:1px solid rgba(26,43,76,.08);box-shadow:0 2px 8px rgba(26,43,76,.05);margin-bottom:16px;'>
      <div style='font-family:Sora,sans-serif;font-weight:700;font-size:15px;color:#1A2B4C;margin-bottom:4px;'>
        1️⃣ Ana öğrenciyi seç
      </div>
      <div style='font-size:13px;color:#6B7A99;'>Grup için merkez öğrenci — modülleri baz alınacak</div>
    </div>""", unsafe_allow_html=True)

    ana_adi = st.selectbox(
        "Öğrenci",
        options=["— Seç —"] + sorted(s_map.keys()),
        key="grup_ana",
        label_visibility="collapsed",
    )

    if ana_adi == "— Seç —":
        return

    ana = s_map[ana_adi]
    ana_mods = {m["name"] for m in ana.get("modules", [])}
    ana_yas  = yas(ana.get("dob"))

    # Ana öğrenci bilgi kartı
    tanilar = ", ".join(d["name"].replace("Olan Bireyler İçin Destek Eğitim Programı","").strip()
                        for d in ana.get("diagnoses", [])) or "–"
    mods_str = ", ".join(sorted(ana_mods)) or "–"

    col_k1, col_k2, col_k3 = st.columns(3)
    col_k1.markdown(f"**Doğum**  \n{ana.get('dob') or '–'}")
    col_k2.markdown(f"**Yaş**  \n{f'{ana_yas:.1f}' if ana_yas else '–'}")
    col_k3.markdown(f"**Rapor bitiş**  \n{ana.get('rapor_bitis') or '–'}")
    st.markdown(f"**Tanı:** {tanilar}")
    st.markdown(f"**Modüller:** {mods_str}")

    if not ana_mods:
        st.warning("Bu öğrenciye modül atanmamış. Lütfen önce Lila'dan import yapın.")
        return

    # ── ADIM 2: Uyumlu öğrenciler ────────────────────────────────────────────
    st.markdown("""
    <div style='background:white;border-radius:14px;padding:20px 24px;
         border:1px solid rgba(26,43,76,.08);box-shadow:0 2px 8px rgba(26,43,76,.05);
         margin:16px 0;'>
      <div style='font-family:Sora,sans-serif;font-weight:700;font-size:15px;color:#1A2B4C;margin-bottom:4px;'>
        2️⃣ Grup arkadaşı seç
      </div>
      <div style='font-size:13px;color:#6B7A99;'>Max 3 yaş farkı · Ortak modül zorunlu · Birden fazla seçilebilir</div>
    </div>""", unsafe_allow_html=True)

    uyumlu = []
    uyumsuz = []
    for s in students:
        if s["name"] == ana_adi:
            continue
        s_mods = {m["name"] for m in s.get("modules", [])}
        ortak  = ana_mods & s_mods
        s_yas  = yas(s.get("dob"))
        yas_fark = abs(ana_yas - s_yas) if (ana_yas and s_yas) else None

        if ortak and (yas_fark is None or yas_fark <= 3):
            uyumlu.append({
                "s": s,
                "ortak": ortak,
                "yas_fark": yas_fark,
            })
        else:
            uyumsuz.append({"s": s, "ortak": ortak, "yas_fark": yas_fark})

    if not uyumlu:
        st.warning("Bu öğrenci için uyumlu grup arkadaşı bulunamadı.")
        return

    uyumlu.sort(key=lambda x: (-len(x["ortak"]), x["yas_fark"] or 0))

    # Seçim listesi — her satırda uyumluluk bilgisi
    secenekler = []
    secenek_bilgi = {}
    for u in uyumlu:
        s   = u["s"]
        yf  = f"{u['yas_fark']:.1f} yaş farkı" if u["yas_fark"] is not None else "yaş bilinmiyor"
        ortak_str = ", ".join(sorted(u["ortak"]))
        etiket = f"{s['name']}  ·  {yf}  ·  Ortak: {ortak_str}"
        secenekler.append(etiket)
        secenek_bilgi[etiket] = {"s": s, "ortak": u["ortak"]}

    secili_etiketler = st.multiselect(
        "Grup arkadaşları",
        options=secenekler,
        key="grup_arkadaslar",
        label_visibility="collapsed",
    )

    # ── Uyumluluk Kartı ──────────────────────────────────────────────────────
    if secili_etiketler:
        secili_students = [ana] + [secenek_bilgi[e]["s"] for e in secili_etiketler]

        # Ortak modüller
        ortak_mods = ana_mods.copy()
        for e in secili_etiketler:
            ortak_mods &= secenek_bilgi[e]["ortak"]

        # Yaş kontrolü
        yaslar = [yas(s.get("dob")) for s in secili_students]
        yaslar = [y for y in yaslar if y is not None]
        max_fark = max(yaslar) - min(yaslar) if len(yaslar) >= 2 else 0

        yas_ok  = max_fark <= 3
        mod_ok  = len(ortak_mods) > 0
        kisi_ok = len(secili_students) >= 2

        renk_yas = "#22c55e" if yas_ok else "#ef4444"
        renk_mod = "#22c55e" if mod_ok else "#ef4444"
        renk_kisi = "#22c55e" if kisi_ok else "#ef4444"

        st.markdown(f"""
        <div style='background:white;border-radius:14px;padding:20px 24px;
             border:1px solid rgba(26,43,76,.08);box-shadow:0 2px 8px rgba(26,43,76,.05);margin-top:16px;'>
          <div style='font-family:Sora,sans-serif;font-weight:700;font-size:15px;color:#1A2B4C;margin-bottom:14px;'>
            👥 Grup Önizleme
          </div>
          <div style='display:flex;gap:12px;flex-wrap:wrap;margin-bottom:14px;'>
            <div style='background:rgba(0,0,0,.04);border-radius:8px;padding:8px 14px;font-size:13px;'>
              <span style='color:{renk_kisi};font-weight:700;'>{len(secili_students)}</span>
              <span style='color:#6B7A99;'> kişi</span>
            </div>
            <div style='background:rgba(0,0,0,.04);border-radius:8px;padding:8px 14px;font-size:13px;'>
              <span style='color:{renk_yas};font-weight:700;'>{max_fark:.1f} yıl</span>
              <span style='color:#6B7A99;'> max yaş farkı</span>
            </div>
            <div style='background:rgba(0,0,0,.04);border-radius:8px;padding:8px 14px;font-size:13px;'>
              <span style='color:{renk_mod};font-weight:700;'>{len(ortak_mods)}</span>
              <span style='color:#6B7A99;'> ortak modül</span>
            </div>
          </div>
        """, unsafe_allow_html=True)

        if ortak_mods:
            tags = "".join(
                f'<span style="display:inline-block;background:rgba(66,184,177,.15);color:#1A2B4C;'
                f'border-radius:5px;padding:3px 10px;margin:3px;font-size:12px;">{m}</span>'
                for m in sorted(ortak_mods)
            )
            st.markdown(f"<div style='margin-bottom:8px;'><b>Ortak modüller:</b><br>{tags}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        uyumsuzluk = []
        if not yas_ok:  uyumsuzluk.append(f"⚠️ Yaş farkı {max_fark:.1f} yıl (max 3 yıl)")
        if not mod_ok:  uyumsuzluk.append("⚠️ Ortak modül yok")
        if not kisi_ok: uyumsuzluk.append("⚠️ En az 2 kişi gerekli")

        if uyumsuzluk:
            for u in uyumsuzluk:
                st.error(u)
        else:
            st.divider()

            # ── Kaydet ───────────────────────────────────────────────────────
            st.markdown("**3️⃣ Grubu kaydet**")
            c1, c2 = st.columns(2)
            with c1:
                saat = st.text_input("Saat (opsiyonel)", placeholder="10:00", key="grup_saat")
            with c2:
                liste = st.text_input("Liste adı (opsiyonel)", placeholder="Salı Grubu", key="grup_liste")
            notlar = st.text_area("Notlar (opsiyonel)", key="grup_notlar", height=80)

            if st.button("💾 Grubu Kaydet", type="primary", use_container_width=True):
                payload = {
                    "ogrenciler": " | ".join(s["name"] for s in secili_students),
                    "moduller":   " / ".join(sorted(ortak_mods)),
                    "saat":       saat.strip() or None,
                    "notlar":     notlar.strip() or None,
                    "liste_adi":  liste.strip() or "",
                }
                if api.create_saved_group(payload):
                    st.success("✅ Grup kaydedildi!")
                    st.balloons()
                    for k in ["grup_ana","grup_arkadaslar","grup_saat","grup_liste","grup_notlar"]:
                        st.session_state.pop(k, None)
                    st.rerun()

    # Uyumsuz öğrenciler (collapsible)
    if uyumsuz:
        with st.expander(f"🚫 Uyumsuz öğrenciler ({len(uyumsuz)}) — neden?"):
            for u in uyumsuz:
                s   = u["s"]
                yf  = f"{u['yas_fark']:.1f} yıl fark" if u["yas_fark"] is not None else "yaş bilinmiyor"
                neden = []
                if not u["ortak"]: neden.append("ortak modül yok")
                if u["yas_fark"] and u["yas_fark"] > 3: neden.append(f"yaş farkı fazla ({yf})")
                st.markdown(f"- **{s['name']}** — {', '.join(neden)}")
