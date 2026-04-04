import streamlit as st
from datetime import date
import pandas as pd
from io import BytesIO
import api_client as api


def show():
    st.header("👨‍🎓 Öğrenciler")

    students  = api.get_students()
    diags     = api.get_diagnoses()
    mods      = api.get_modules()
    diag_map  = {d["name"]: d["id"] for d in diags}
    mod_map   = {m["name"]: m["id"] for m in mods}

    is_demo = api.is_demo_mode()

    # Demo bilgi bandı
    if is_demo:
        from demo_data import DEMO_MAX_STUDENTS
        user_count = len(st.session_state.get("demo_students", []))
        remaining  = DEMO_MAX_STUDENTS - user_count
        st.info(
            f"🎭 Demo hesap: {user_count}/{DEMO_MAX_STUDENTS} öğrenci eklediniz. "
            f"{'Ekleyebileceğiniz öğrenci kalmadı.' if remaining == 0 else f'{remaining} öğrenci daha ekleyebilirsiniz.'}"
        )

    # ── Mevcut Öğrenciler ────────────────────────────────────────────────────
    if not students:
        st.info("Henüz öğrenci kaydı yok.")
    else:
        for s in students:
            is_user_added = s["id"] >= 2000  # Demo: kullanıcının eklediği öğrenci

            with st.expander(f"📋 {s['name']}" + (" *(sizin eklediğiniz)*" if is_demo and is_user_added else "")):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Doğum:** {s.get('dob') or '–'}")
                c2.write(f"**Rapor bitiş:** {s.get('rapor_bitis') or '–'}")
                c3.write(f"**Tanılar:** {', '.join(d['name'] for d in s.get('diagnoses', [])) or '–'}")
                st.write(f"**Modüller:** {', '.join(m['name'] for m in s.get('modules', [])) or '–'}")

                # Demo'da yalnızca kullanıcının eklediği öğrenciler düzenlenebilir/silinebilir
                if is_demo and not is_user_added:
                    st.caption("🔒 Demo öğrenciler salt-okunurdur.")
                    continue

                col_edit, col_del = st.columns([3, 1])

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

    # ── Yeni Öğrenci Ekle ────────────────────────────────────────────────────
    if is_demo:
        from demo_data import DEMO_MAX_STUDENTS
        user_count = len(st.session_state.get("demo_students", []))
        if user_count >= DEMO_MAX_STUDENTS:
            st.subheader("➕ Yeni Öğrenci Ekle")
            st.warning(
                f"Demo hesapta en fazla {DEMO_MAX_STUDENTS} öğrenci ekleyebilirsiniz. "
                "Limite ulaştınız."
            )
        else:
            st.subheader(f"➕ Yeni Öğrenci Ekle ({user_count}/{DEMO_MAX_STUDENTS})")
            _show_add_form(diag_map, mod_map)
    else:
        st.subheader("➕ Yeni Öğrenci Ekle")
        _show_add_form(diag_map, mod_map)

    st.divider()

    # ── Excel İçe Aktar ──────────────────────────────────────────────────────
    _show_import_section(diag_map, mod_map, is_demo)


def _show_add_form(diag_map: dict, mod_map: dict):
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


def _show_import_section(diag_map: dict, mod_map: dict, is_demo: bool):
    """Excel / CSV dosyasından öğrenci içe aktarma.

    Beklenen sütunlar (Türkçe başlıklar):
        Ad Soyad | Doğum Tarihi | Rapor Bitiş | Tanılar | Modüller

    Demo modda: dosya önizlemesi gösterilir ama kayıt yapılmaz.
    """
    with st.expander("📥 Excel / CSV ile Toplu İçe Aktar"):
        st.markdown(
            "**Beklenen sütunlar:** `Ad Soyad` *(zorunlu)*, `Doğum Tarihi`, "
            "`Rapor Bitiş`, `Tanılar` *(virgülle ayrılmış)*, `Modüller` *(virgülle ayrılmış)*"
        )

        uploaded = st.file_uploader(
            "Dosya seçin (.xlsx veya .csv)",
            type=["xlsx", "xls", "csv"],
            key="import_uploader",
        )

        if not uploaded:
            return

        # Dosyayı oku
        try:
            if uploaded.name.endswith(".csv"):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded, engine="openpyxl")
        except Exception as e:
            st.error(f"Dosya okunamadı: {e}")
            return

        if df.empty:
            st.warning("Dosya boş.")
            return

        # Zorunlu sütun kontrolü
        if "Ad Soyad" not in df.columns:
            st.error("Dosyada `Ad Soyad` sütunu bulunamadı.")
            return

        # Önizleme tablosu
        st.markdown(f"**{len(df)} satır bulundu – önizleme:**")
        st.dataframe(df, use_container_width=True)

        if is_demo:
            st.warning(
                "🎭 **Demo hesapta içe aktarma yapılamaz.** "
                "Yukarıdaki liste yalnızca önizleme amaçlıdır. "
                "Öğrencileri gerçekten içe aktarmak için tam hesap oluşturun."
            )
            return

        # Gerçek hesap: içe aktarma butonu
        if st.button("⬆️ İçe Aktar", type="primary"):
            success_count = 0
            error_rows    = []

            for idx, row in df.iterrows():
                name = str(row.get("Ad Soyad", "")).strip()
                if not name:
                    error_rows.append(idx + 2)
                    continue

                # Tanı ID'leri
                raw_diags = str(row.get("Tanılar", "") or "")
                diag_ids  = [
                    diag_map[t.strip()]
                    for t in raw_diags.split(",")
                    if t.strip() in diag_map
                ]

                # Modül ID'leri
                raw_mods = str(row.get("Modüller", "") or "")
                mod_ids  = [
                    mod_map[m.strip()]
                    for m in raw_mods.split(",")
                    if m.strip() in mod_map
                ]

                dob_raw   = row.get("Doğum Tarihi")
                rapor_raw = row.get("Rapor Bitiş")

                def _to_iso(val):
                    if val is None or (isinstance(val, float) and pd.isna(val)):
                        return None
                    try:
                        return pd.to_datetime(val).date().isoformat()
                    except Exception:
                        return None

                payload = {
                    "name": name,
                    "dob": _to_iso(dob_raw),
                    "rapor_bitis": _to_iso(rapor_raw),
                    "diagnosis_ids": diag_ids,
                    "module_ids": mod_ids,
                }
                result = api.create_student(payload)
                if result:
                    success_count += 1
                else:
                    error_rows.append(idx + 2)

            if success_count:
                st.success(f"✅ {success_count} öğrenci başarıyla içe aktarıldı.")
            if error_rows:
                st.warning(f"⚠️ Şu satırlar atlandı (ad eksik veya hata): {error_rows}")
            if success_count:
                st.rerun()
