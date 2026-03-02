import streamlit as st
import api_client as api
import re
from html import unescape


def _clean_text(value: str) -> str:
    """API'den yanlışlıkla gelen HTML parçalarını temizler."""
    text = unescape(value or "")
    return re.sub(r"<[^>]+>", "", text).strip()


def show():
    st.header("🔍 Öğrenciye Göre Ara & Grup Oluştur")

    students = api.get_students()
    mods = api.get_modules()
    mod_names = [_clean_text(m["name"]) for m in mods if _clean_text(m.get("name", ""))]

    if not students:
        st.info("Önce öğrenci ekleyin.")
        return

    # ── Filtreler ────────────────────────────────────────────────────────────
    st.subheader("Filtrele")
    col1, col2 = st.columns(2)

    with col1:
        sec_mod = st.multiselect(
            "Modüle göre filtrele",
            options=mod_names,
            help="Seçilen modüllerin tümünde olan öğrenciler",
        )

    with col2:
        diag_names = list({d["name"] for s in students for d in s.get("diagnoses", [])})
        sec_diag = st.multiselect("Tanıya göre filtrele", options=sorted(diag_names))

    # ── Filtreleme mantığı ────────────────────────────────────────────────────
    filtered = students
    if sec_mod:
        filtered = [
            s for s in filtered
            if all(
                any(_clean_text(m.get("name", "")) == mod for m in s.get("modules", []))
                for mod in sec_mod
            )
        ]
    if sec_diag:
        filtered = [
            s for s in filtered
            if any(d["name"] in sec_diag for d in s.get("diagnoses", []))
        ]

    st.markdown(f"**{len(filtered)} öğrenci bulundu**")

    if not filtered:
        st.warning("Filtre kriterlerine uyan öğrenci yok.")
        return

    # ── Öğrenci seçimi ───────────────────────────────────────────────────────
    student_names = [s["name"] for s in filtered]
    selected_names = st.multiselect("Gruba eklenecek öğrenciler", options=student_names, default=student_names)

    if not selected_names:
        return

    # ── Grup ayarları ────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Grup Ayarları")

    saat      = st.text_input("Saat (opsiyonel)", placeholder="10:00")
    liste_adi = st.text_input("Liste adı (opsiyonel)", placeholder="Salı Grubu")
    notlar    = st.text_area("Notlar (opsiyonel)")

    # Ortak modüller
    selected_students = [s for s in filtered if s["name"] in selected_names]
    common_mods: set[str] = set()
    if selected_students:
        common_mods = set(
            _clean_text(m.get("name", ""))
            for m in selected_students[0].get("modules", [])
            if _clean_text(m.get("name", ""))
        )
        for s in selected_students[1:]:
            common_mods &= {
                _clean_text(m.get("name", ""))
                for m in s.get("modules", [])
                if _clean_text(m.get("name", ""))
            }

    st.write("**Ortak modüller:**", ", ".join(sorted(common_mods)) if common_mods else "–")

    # ── Kaydet ──────────────────────────────────────────────────────────────
    if st.button("💾 Grubu Kaydet", type="primary"):
        payload = {
            "ogrenciler": " | ".join(selected_names),
            "moduller":   " / ".join(sorted(common_mods)) if common_mods else "–",
            "saat":       saat.strip() or None,
            "notlar":     notlar.strip() or None,
            "liste_adi":  liste_adi.strip(),
        }
        result = api.create_saved_group(payload)
        if result:
            st.success("✅ Grup kaydedildi!")
            st.balloons()
