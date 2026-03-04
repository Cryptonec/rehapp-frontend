"""
Öğrenciler sayfası.
- Lila import en üstte
- Öğrenciler kart listesi halinde, kapalı gelir
- Tek tek açılarak düzenlenebilir
"""
import streamlit as st
from datetime import date
import api_client as api
from pages import lila_import


def rapor_durumu(rapor_bitis_str):
    if not rapor_bitis_str:
        return "", ""
    try:
        bitis = date.fromisoformat(rapor_bitis_str)
        bugun = date.today()
        kalan = (bitis - bugun).days
        if kalan < 0:
            return "🔴", f"{abs(kalan)} gün önce doldu"
        elif kalan <= 30:
            return "🟠", f"{kalan} gün kaldı"
        elif kalan <= 60:
            return "🟡", f"{kalan} gün kaldı"
        else:
            return "🟢", f"{kalan} gün kaldı"
    except Exception:
        return "", ""


def show():
    st.header("👤 Öğrenciler")

    # ── Lila Import ───────────────────────────────────────────────────────────
    lila_import.show_import()
    st.divider()

    students = api.get_students()
    diags    = api.get_diagnoses()
    mods     = api.get_modules()
    diag_map = {d["name"]: d["id"] for d in diags}
    mod_map  = {m["name"]: m["id"] for m in mods}

    # ── Arama / Filtre ────────────────────────────────────────────────────────
    col_ara, col_filtre = st.columns([3, 1])
    with col_ara:
        arama = st.text_input("🔍 Öğrenci ara", placeholder="Ad ile ara...", label_visibility="collapsed")
    with col_filtre:
        filtre = st.selectbox("Filtre", ["Tümü", "Raporu Biten", "30 Gün İçinde", "Normal"], label_visibility="collapsed")

    filtered = students
    if arama:
        filtered = [s for s in filtered if arama.lower() in s["name"].lower()]
    if filtre == "Raporu Biten":
        filtered = [s for s in filtered if s.get("rapor_bitis") and (date.fromisoformat(s["rapor_bitis"]) < date.today())]
    elif filtre == "30 Gün İçinde":
        filtered = [s for s in filtered if s.get("rapor_bitis") and 0 <= (date.fromisoformat(s["rapor_bitis"]) - date.today()).days <= 30]
    elif filtre == "Normal":
        filtered = [s for s in filtered if s.get("rapor_bitis") and (date.fromisoformat(s["rapor_bitis"]) - date.today()).days > 30]

    st.caption(f"Toplam **{len(filtered)}** öğrenci")

    if not filtered:
        st.info("Öğrenci bulunamadı.")
    else:
        # Tablo başlığı
        st.markdown("""
        <div style='overflow-x:auto;border-radius:12px;border:1px solid rgba(26,43,76,.08);margin-bottom:8px;'>
        <table style='width:100%;border-collapse:collapse;font-family:DM Sans,sans-serif;'>
          <thead><tr style='background:linear-gradient(135deg,#38C9C0,#2756D6);'>
            <th style='padding:10px 12px;color:white;font-family:Sora,sans-serif;font-size:12px;text-align:left;'>#</th>
            <th style='padding:10px 12px;color:white;font-family:Sora,sans-serif;font-size:12px;text-align:left;'>Ad Soyad</th>
            <th style='padding:10px 12px;color:white;font-family:Sora,sans-serif;font-size:12px;text-align:left;'>Doğum</th>
            <th style='padding:10px 12px;color:white;font-family:Sora,sans-serif;font-size:12px;text-align:left;'>Rapor Bitiş</th>
            <th style='padding:10px 12px;color:white;font-family:Sora,sans-serif;font-size:12px;text-align:left;'>Tanı</th>
            <th style='padding:10px 12px;color:white;font-family:Sora,sans-serif;font-size:12px;text-align:left;'>Modüller</th>
          </tr></thead>
          <tbody style='background:white;'>
        """, unsafe_allow_html=True)

        for i, s in enumerate(filtered, 1):
            renk_emoji, etiket = rapor_durumu(s.get("rapor_bitis"))
            tani_kisa = " / ".join(
                d["name"].replace(" Olan Bireyler İçin Destek Eğitim Programı", "").strip()
                for d in s.get("diagnoses", [])
            ) or "–"
            mod_tags = "".join(
                f'<span style="display:inline-block;background:rgba(56,201,192,.12);color:#2B7A76;border-radius:4px;padding:1px 7px;margin:2px;font-size:11px;">{m["name"]}</span>'
                for m in s.get("modules", [])
            ) or "–"
            rapor_str = s.get("rapor_bitis") or "–"
            dob_str   = s.get("dob") or "–"
            etiket_html = f'<span style="font-size:11px;color:#6B7A99;margin-left:6px;">{etiket}</span>' if etiket else ""

            st.markdown(f"""
            <tr style='border-bottom:1px solid rgba(26,43,76,.06);'>
              <td style='padding:8px 12px;color:#6B7A99;font-size:12px;'>{renk_emoji} {i}</td>
              <td style='padding:8px 12px;font-weight:600;color:#1A2B4C;font-size:13px;'>{s["name"]}{etiket_html}</td>
              <td style='padding:8px 12px;color:#1A2B4C;font-size:12px;'>{dob_str}</td>
              <td style='padding:8px 12px;color:#1A2B4C;font-size:12px;'>{rapor_str}</td>
              <td style='padding:8px 12px;font-size:12px;color:#1A2B4C;'>{tani_kisa}</td>
              <td style='padding:8px 12px;'>{mod_tags}</td>
            </tr>""", unsafe_allow_html=True)

        st.markdown("</tbody></table></div>", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        for s in filtered:
            renk, etiket = rapor_durumu(s.get("rapor_bitis"))
            tanilar  = ", ".join(d["name"] for d in s.get("diagnoses", [])) or "–"
            moduller = ", ".join(m["name"] for m in s.get("modules", [])) or "–"
            baslik = f"{renk} {s['name']}"
            if etiket:
                baslik += f"  ·  {etiket}"

            with st.expander(baslik):
                ic1, ic2, ic3 = st.columns(3)
                ic1.markdown(f"**Doğum**  \n{s.get('dob') or '–'}")
                ic2.markdown(f"**Rapor bitiş**  \n{s.get('rapor_bitis') or '–'}")
                ic3.markdown(f"**Tanılar**  \n{tanilar[:80]}{'…' if len(tanilar) > 80 else ''}")
                st.markdown(f"**Modüller:** {moduller}")
                st.markdown("---")

                with st.form(f"edit_{s['id']}"):
                    fc1, fc2, fc3 = st.columns(3)
                    with fc1:
                        new_name = st.text_input("Ad Soyad", value=s["name"])
                    with fc2:
                        new_dob = st.date_input(
                            "Doğum tarihi",
                            value=date.fromisoformat(s["dob"]) if s.get("dob") else None,
                        )
                    with fc3:
                        new_rapor = st.date_input(
                            "Rapor bitiş",
                            value=date.fromisoformat(s["rapor_bitis"]) if s.get("rapor_bitis") else None,
                        )

                    sel_diags = st.multiselect(
                        "Tanılar",
                        options=list(diag_map.keys()),
                        default=[d["name"] for d in s.get("diagnoses", [])],
                    )
                    sel_mods = st.multiselect(
                        "Modüller",
                        options=list(mod_map.keys()),
                        default=[m["name"] for m in s.get("modules", [])],
                    )

                    btn1, btn2 = st.columns([3, 1])
                    with btn1:
                        if st.form_submit_button("💾 Güncelle", type="primary", use_container_width=True):
                            payload = {
                                "name": new_name,
                                "dob": new_dob.isoformat() if new_dob else None,
                                "rapor_bitis": new_rapor.isoformat() if new_rapor else None,
                                "diagnosis_ids": [diag_map[x] for x in sel_diags],
                                "module_ids": [mod_map[x] for x in sel_mods],
                            }
                            if api.update_student(s["id"], payload):
                                st.success("Güncellendi!")
                                st.rerun()
                    with btn2:
                        if st.form_submit_button("🗑 Sil", use_container_width=True):
                            if api.delete_student(s["id"]):
                                st.rerun()

    st.divider()

    # ── Yeni Öğrenci Ekle ─────────────────────────────────────────────────────
    with st.expander("➕ Yeni Öğrenci Ekle"):
        with st.form("new_student", clear_on_submit=True):
            nc1, nc2, nc3 = st.columns(3)
            with nc1:
                name = st.text_input("Ad Soyad *")
            with nc2:
                dob = st.date_input("Doğum tarihi", value=None)
            with nc3:
                rapor = st.date_input("Rapor bitiş tarihi", value=None)

            sel_diags = st.multiselect("Tanılar", options=list(diag_map.keys()))
            sel_mods  = st.multiselect("Modüller", options=list(mod_map.keys()))

            if st.form_submit_button("✅ Kaydet", type="primary", use_container_width=True):
                if not name.strip():
                    st.warning("Ad alanı zorunlu.")
                else:
                    payload = {
                        "name": name.strip(),
                        "dob": dob.isoformat() if dob else None,
                        "rapor_bitis": rapor.isoformat() if rapor else None,
                        "diagnosis_ids": [diag_map[x] for x in sel_diags],
                        "module_ids": [mod_map[x] for x in sel_mods],
                    }
                    if api.create_student(payload):
                        st.success("Öğrenci eklendi!")
                        st.rerun()
