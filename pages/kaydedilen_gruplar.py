"""
Kaydedilen Gruplar — liste yönetimi, kart tasarımı, Excel export.
Eski proje mantığı: liste oluştur → gruplara ata.
"""
import streamlit as st
import api_client as api
from io import BytesIO


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
            Grup Oluştur sekmesinden grup oluşturup kaydedin.
          </div>
        </div>""", unsafe_allow_html=True)
        return

    # ── Üst toolbar: sayaç + liste oluştur + excel ────────────────────────────
    listeler = sorted({g["liste_adi"] for g in groups if g.get("liste_adi") and g["liste_adi"] not in ("","nan","None")})

    tc1, tc2, tc3 = st.columns([3,2,1])
    with tc1:
        st.caption(f"**{len(groups)}** kayıtlı grup · **{len(listeler)}** liste")
    with tc2:
        kl1, kl2 = st.columns([3,1])
        with kl1:
            kg_yeni = st.text_input("", placeholder="Yeni liste adı...", key="kg_yeni", label_visibility="collapsed")
        with kl2:
            if st.button("➕", use_container_width=True, key="kg_yeni_btn", help="Liste oluştur"):
                if kg_yeni.strip():
                    if kg_yeni.strip() not in listeler:
                        st.session_state["kg_bekl"] = kg_yeni.strip()
                        st.rerun()
                    else:
                        st.warning("Bu isim zaten var.")
    with tc3:
        try:
            import pandas as pd
            df = pd.DataFrame([{
                "Liste":g.get("liste_adi",""),"Öğrenciler":g["ogrenciler"],
                "Modüller":g.get("moduller",""),"Not":g.get("notlar",""),
                "Tarih":g.get("created_at","")[:10]} for g in groups])
            buf=BytesIO()
            df.to_excel(buf,index=False,engine="openpyxl")
            st.download_button("📥 Excel",data=buf.getvalue(),file_name="gruplar.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        except: pass

    # Bekleyen yeni liste
    kg_bekl = st.session_state.get("kg_bekl","")
    if kg_bekl and kg_bekl not in listeler:
        listeler = sorted(listeler + [kg_bekl])

    st.divider()

    # ── Kart fonksiyonu ───────────────────────────────────────────────────────
    def grup_kart(g, sfx):
        ogr_list = [o.strip() for o in g["ogrenciler"].split("|")]
        mod_list = [m.strip() for m in g.get("moduller","").split("/") if m.strip() and m.strip()!="–"]
        tarih    = g.get("created_at","")[:10]

        # Kart başlığı: sadece isimler kısa
        ogr_kisa = " · ".join(ogr_list[:3]) + (f" +{len(ogr_list)-3}" if len(ogr_list)>3 else "")

        with st.expander(f"👥 {ogr_kisa}  —  {tarih}"):
            # Öğrenci rozetleri
            ogr_html="".join(
                f'<span style="display:inline-block;background:rgba(43,82,196,.1);color:#1A2B4C;'
                f'border-radius:6px;padding:2px 10px;margin:3px;font-size:13px;font-weight:500;">{o}</span>'
                for o in ogr_list)
            mod_html="".join(
                f'<span style="display:inline-block;background:rgba(66,184,177,.13);color:#1A2B4C;'
                f'border-radius:6px;padding:2px 10px;margin:3px;font-size:12px;">{m}</span>'
                for m in mod_list) or "–"

            st.markdown(f"""
            <div style='margin-bottom:8px;'>
              <div style='font-size:11px;color:#6B7A99;margin-bottom:4px;'>👤 Öğrenciler</div>
              <div>{ogr_html}</div>
            </div>
            <div>
              <div style='font-size:11px;color:#6B7A99;margin-bottom:4px;'>📚 Modüller</div>
              <div>{mod_html}</div>
            </div>""", unsafe_allow_html=True)

            if g.get("notlar"): st.info(f"📝 {g['notlar']}")

            st.markdown("---")
            ec1, ec2, ec3, ec4 = st.columns([3,3,2,1])

            with ec1:
                # Listeye ata
                kg_opts = ["— Listeye ekle —"] + listeler
                current_idx = 0
                if g.get("liste_adi") and g["liste_adi"] in listeler:
                    current_idx = listeler.index(g["liste_adi"]) + 1
                kg_sel = st.selectbox("Liste", kg_opts, index=current_idx,
                    key=f"kgls_{sfx}_{g['id']}", label_visibility="collapsed")
                if kg_sel != "— Listeye ekle —" and kg_sel != g.get("liste_adi",""):
                    api.patch_saved_group(g["id"], {"liste_adi":kg_sel, "notlar":g.get("notlar","")})
                    st.rerun()

            with ec2:
                with st.form(f"not_{sfx}_{g['id']}"):
                    nn = st.text_input("Not", value=g.get("notlar",""), placeholder="Not...", label_visibility="collapsed")
                    if st.form_submit_button("💾 Not"):
                        api.patch_saved_group(g["id"], {"liste_adi":g.get("liste_adi",""), "notlar":nn})
                        st.rerun()

            with ec3:
                # Listeden çıkar
                if g.get("liste_adi"):
                    if st.button("📤 Listeden Çıkar", key=f"listec_{sfx}_{g['id']}", use_container_width=True):
                        api.patch_saved_group(g["id"], {"liste_adi":"", "notlar":g.get("notlar","")})
                        st.rerun()

            with ec4:
                if st.button("🗑", key=f"del_{sfx}_{g['id']}", use_container_width=True, help="Sil"):
                    if api.delete_saved_group(g["id"]): st.rerun()

    # ── Listeli gruplar ───────────────────────────────────────────────────────
    for lad in listeler:
        lgrp = [g for g in groups if g.get("liste_adi") == lad]

        llc1, llc2, llc3 = st.columns([5,1,1])
        with llc1:
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:10px;margin:12px 0 6px;'>
              <div style='font-family:Sora,sans-serif;font-weight:700;font-size:16px;color:#1A2B4C;'>📋 {lad}</div>
              <div style='background:rgba(66,184,177,.15);color:#42B8B1;border-radius:20px;
                   padding:2px 10px;font-size:12px;font-weight:600;'>{len(lgrp)} grup</div>
            </div>""", unsafe_allow_html=True)
        with llc2: st.markdown("")
        with llc3:
            lsok = f"kglsil_{lad}"
            if st.session_state.get(lsok):
                if st.button("✅ Evet", key=f"kglsil_evet_{lad}", use_container_width=True):
                    for g in lgrp:
                        api.patch_saved_group(g["id"], {"liste_adi":"", "notlar":g.get("notlar","")})
                    st.session_state.pop(lsok)
                    if "kg_bekl" in st.session_state and st.session_state["kg_bekl"]==lad:
                        del st.session_state["kg_bekl"]
                    st.rerun()
            else:
                if st.button("🗑 Liste", key=f"kglsil_{lad}", use_container_width=True, help="Listeyi sil (gruplar kalır)"):
                    st.session_state[lsok] = True; st.rerun()

        if st.session_state.get(f"kglsil_{lad}"):
            st.warning(f"'{lad}' listesi silinecek. Gruplar listeye eklenmemiş bölümüne düşer.")

        if not lgrp:
            st.caption("Henüz grup eklenmedi.")
        else:
            for g in lgrp:
                grup_kart(g, f"l_{lad}")
        st.divider()

    # ── Listesiz gruplar ──────────────────────────────────────────────────────
    listesiz = [g for g in groups if not g.get("liste_adi") or g["liste_adi"] in ("","nan","None")]
    if listesiz:
        if listeler:
            st.markdown("""
            <div style='font-family:Sora,sans-serif;font-weight:700;font-size:15px;
                 color:#1A2B4C;margin:12px 0 6px;'>📥 Listeye Eklenmemiş</div>""",
            unsafe_allow_html=True)
        for g in listesiz:
            grup_kart(g, "lsz")
