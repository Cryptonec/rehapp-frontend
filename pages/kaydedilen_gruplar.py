"""
Kaydedilen Gruplar — Modern kart tasarımı, liste yönetimi, Excel export.
"""
import streamlit as st
import api_client as api
from io import BytesIO
from datetime import datetime


def show():
    st.header("⭐ Kaydedilen Gruplar")

    groups = api.get_saved_groups()

    if not groups:
        st.markdown("""
        <div style='text-align:center;padding:60px 20px;'>
          <div style='font-size:48px;margin-bottom:16px;'>📭</div>
          <div style='font-family:Sora,sans-serif;font-weight:600;font-size:18px;color:#1A2B4C;'>
            Henüz kaydedilmiş grup yok
          </div>
          <div style='font-size:14px;color:#6B7A99;margin-top:8px;'>
            Grup Oluştur sekmesinden gruplarınızı oluşturup kaydedin.
          </div>
        </div>""", unsafe_allow_html=True)
        return

    # ── Üst toolbar ──────────────────────────────────────────────────────────
    listeler = sorted({g["liste_adi"] for g in groups if g["liste_adi"]})
    toolbar1, toolbar2, toolbar3 = st.columns([2, 2, 1])

    with toolbar1:
        sec_liste = st.selectbox("Liste filtrele", ["Tümü"] + listeler, label_visibility="collapsed")
    with toolbar2:
        ara = st.text_input("", placeholder="Öğrenci ara...", label_visibility="collapsed")
    with toolbar3:
        # Excel export
        try:
            import pandas as pd
            filtered_export = [g for g in groups if (sec_liste == "Tümü" or g["liste_adi"] == sec_liste)]
            df = pd.DataFrame([{
                "Liste": g["liste_adi"], "Öğrenciler": g["ogrenciler"],
                "Modüller": g["moduller"], "Saat": g.get("saat") or "",
                "Notlar": g.get("notlar") or "", "Tarih": g["created_at"][:10]
            } for g in filtered_export])
            buf = BytesIO()
            df.to_excel(buf, index=False, engine="openpyxl")
            st.download_button("📥 Excel", data=buf.getvalue(),
                file_name="gruplar.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        except:
            pass

    # Filtrele
    filtered = groups
    if sec_liste != "Tümü":
        filtered = [g for g in filtered if g["liste_adi"] == sec_liste]
    if ara:
        filtered = [g for g in filtered if ara.lower() in g["ogrenciler"].lower()]

    st.caption(f"**{len(filtered)}** grup gösteriliyor")
    st.divider()

    # ── Liste grupları halinde göster ─────────────────────────────────────────
    listesiz = [g for g in filtered if not g["liste_adi"]]
    listeli  = {l: [g for g in filtered if g["liste_adi"] == l] for l in listeler
                if any(g["liste_adi"] == l for g in filtered)}

    def grup_kart(g):
        ogr_list = g["ogrenciler"].split(" | ")
        mod_list = g["moduller"].split(" / ") if g["moduller"] and g["moduller"] != "–" else []

        tarih = g["created_at"][:10] if g.get("created_at") else "–"
        baslik = f"👥 {g['ogrenciler'][:50]}{'…' if len(g['ogrenciler'])>50 else ''}"

        with st.expander(baslik):
            # Öğrenci tag'leri
            ogr_html = "".join(
                f'<span style="display:inline-block;background:rgba(43,82,196,.1);color:#1A2B4C;'
                f'border-radius:6px;padding:3px 10px;margin:3px;font-size:13px;font-weight:500;">{o}</span>'
                for o in ogr_list
            )
            mod_html = "".join(
                f'<span style="display:inline-block;background:rgba(66,184,177,.15);color:#1A2B4C;'
                f'border-radius:6px;padding:3px 10px;margin:3px;font-size:12px;">{m}</span>'
                for m in mod_list
            ) or "–"

            st.markdown(f"""
            <div style='margin-bottom:10px;'>
              <div style='font-size:12px;color:#6B7A99;margin-bottom:6px;'>👤 Öğrenciler</div>
              <div>{ogr_html}</div>
            </div>
            <div style='margin-bottom:10px;'>
              <div style='font-size:12px;color:#6B7A99;margin-bottom:6px;'>📚 Modüller</div>
              <div>{mod_html}</div>
            </div>
            <div style='font-size:12px;color:#6B7A99;'>
              🕐 {g.get('saat') or '–'} &nbsp;·&nbsp; 📅 {tarih}
            </div>""", unsafe_allow_html=True)

            if g.get("notlar"):
                st.info(f"📝 {g['notlar']}")

            st.markdown("---")
            ec1, ec2, ec3 = st.columns([3, 3, 1])
            with ec1:
                with st.form(f"patch_liste_{g['id']}"):
                    nl = st.text_input("Liste adı", value=g["liste_adi"] or "", placeholder="Liste adı...", label_visibility="collapsed")
                    if st.form_submit_button("Liste Güncelle"):
                        if api.patch_saved_group(g["id"], {"liste_adi": nl, "notlar": g.get("notlar") or ""}):
                            st.rerun()
            with ec2:
                with st.form(f"patch_not_{g['id']}"):
                    nn = st.text_input("Not ekle", value=g.get("notlar") or "", placeholder="Not...", label_visibility="collapsed")
                    if st.form_submit_button("Notu Kaydet"):
                        if api.patch_saved_group(g["id"], {"liste_adi": g["liste_adi"] or "", "notlar": nn}):
                            st.rerun()
            with ec3:
                if st.button("🗑", key=f"del_{g['id']}", use_container_width=True):
                    if api.delete_saved_group(g["id"]):
                        st.rerun()

    # Liste bazlı göster
    for liste_adi, liste_gruplar in listeli.items():
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:12px;margin:20px 0 8px;'>
          <div style='font-family:Sora,sans-serif;font-weight:700;font-size:16px;color:#1A2B4C;'>
            📋 {liste_adi}
          </div>
          <div style='background:rgba(66,184,177,.15);color:#42B8B1;border-radius:20px;
               padding:2px 10px;font-size:12px;font-weight:600;'>{len(liste_gruplar)} grup</div>
        </div>""", unsafe_allow_html=True)
        for g in liste_gruplar:
            grup_kart(g)

    if listesiz:
        if listeli:
            st.markdown("""
            <div style='font-family:Sora,sans-serif;font-weight:700;font-size:16px;
                 color:#1A2B4C;margin:24px 0 8px;'>📥 Listeye Eklenmemiş</div>""",
            unsafe_allow_html=True)
        for g in listesiz:
            grup_kart(g)
