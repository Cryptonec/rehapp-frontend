import streamlit as st
import api_client as api
import pandas as pd
from io import BytesIO


def show():
    st.header("📁 Kaydedilen Gruplar")

    groups = api.get_saved_groups()

    if not groups:
        st.info("Henüz kaydedilmiş grup yok.")
        return

    # ── Liste adı filtresi ────────────────────────────────────────────────────
    liste_adlari = ["(Tümü)"] + sorted({g["liste_adi"] for g in groups if g["liste_adi"]})
    sec_liste = st.selectbox("Liste adına göre filtrele", options=liste_adlari)

    filtered = groups if sec_liste == "(Tümü)" else [g for g in groups if g["liste_adi"] == sec_liste]

    st.markdown(f"**{len(filtered)} grup gösteriliyor**")

    # ── Excel Export ──────────────────────────────────────────────────────────
    if filtered:
        df = pd.DataFrame([
            {
                "Liste Adı":  g["liste_adi"],
                "Öğrenciler": g["ogrenciler"],
                "Modüller":   g["moduller"],
                "Saat":       g.get("saat") or "",
                "Notlar":     g.get("notlar") or "",
                "Tarih":      g["created_at"][:10],
            }
            for g in filtered
        ])
        buf = BytesIO()
        df.to_excel(buf, index=False, engine="openpyxl")
        st.download_button(
            "📥 Excel İndir",
            data=buf.getvalue(),
            file_name="kaydedilen_gruplar.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    st.divider()

    # ── Grupları listele ──────────────────────────────────────────────────────
    for g in filtered:
        label = g["liste_adi"] or f"Grup #{g['id']}"
        with st.expander(f"📌 {label} — {g['created_at'][:10]}"):
            st.write(f"**Öğrenciler:** {g['ogrenciler']}")
            st.write(f"**Modüller:** {g['moduller']}")
            if g.get("saat"):
                st.write(f"**Saat:** {g['saat']}")

            # Not güncelleme
            with st.form(f"patch_{g['id']}"):
                new_liste = st.text_input("Liste adı", value=g["liste_adi"])
                new_not   = st.text_area("Not", value=g.get("notlar") or "")
                if st.form_submit_button("💾 Güncelle"):
                    result = api.patch_saved_group(
                        g["id"],
                        {"liste_adi": new_liste, "notlar": new_not},
                    )
                    if result:
                        st.success("Güncellendi!")
                        st.rerun()

            if st.button("🗑 Sil", key=f"del_grp_{g['id']}"):
                if api.delete_saved_group(g["id"]):
                    st.success("Grup silindi")
                    st.rerun()
