import streamlit as st
from datetime import date
import api_client as api


def show():
    st.header("👨‍🎓 Öğrenciler")

    students  = api.get_students()
    diags     = api.get_diagnoses()
    mods      = api.get_modules()
    diag_map  = {d["name"]: d["id"] for d in diags}
    mod_map   = {m["name"]: m["id"] for m in mods}

    # ── Mevcut Öğrenciler ────────────────────────────────────────────────────
    if not students:
        st.info("Henüz öğrenci kaydı yok.")
    else:
        for s in students:
            with st.expander(f"📋 {s['name']}"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Doğum:** {s.get('dob') or '–'}")
                c2.write(f"**Rapor bitiş:** {s.get('rapor_bitis') or '–'}")
                c3.write(f"**Tanılar:** {', '.join(d['name'] for d in s.get('diagnoses', [])) or '–'}")
                st.write(f"**Modüller:** {', '.join(m['name'] for m in s.get('modules', [])) or '–'}")

                col_edit, col_del = st.columns([3, 1])

                # Düzenle formu
                with col_edit:
                    with st.form(f"edit_{s['id']}"):
                        new_name = st.text_input("Ad", value=s["name"])
                        new_dob  = st.date_input(
                            "Doğum tarihi",
                            value=date.fromisoformat(s["dob"]) if s.get("dob") else None,
                        )
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
                        if st.form_submit_button("💾 Güncelle"):
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

                with col_del:
                    if st.button("🗑 Sil", key=f"del_st_{s['id']}"):
                        if api.delete_student(s["id"]):
                            st.success("Öğrenci silindi")
                            st.rerun()

    st.divider()
    st.subheader("➕ Yeni Öğrenci Ekle")

    with st.form("new_student", clear_on_submit=True):
        name  = st.text_input("Ad Soyad")
        dob   = st.date_input("Doğum tarihi", value=None)
        rapor = st.date_input("Rapor bitiş tarihi", value=None)
        sel_diags = st.multiselect("Tanılar", options=list(diag_map.keys()))
        sel_mods  = st.multiselect("Modüller", options=list(mod_map.keys()))

        if st.form_submit_button("Kaydet"):
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
