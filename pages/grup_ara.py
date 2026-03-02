"""
Grup Oluştur — eski projedeki harf oyunu mantığı.
Numara rozetleri + mod badge'ler. Minimal kart tasarımı.
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
        k=(date.fromisoformat(r)-date.today()).days
        return "#EF4444" if k<0 else "#F59E0B" if k<=30 else "#22C55E"
    except: return "#22C55E"

def rapor_etiket(r):
    if not r: return ""
    try:
        k=(date.fromisoformat(r)-date.today()).days
        if k<0:   return " (rapor bitti)"
        if k<=30: return f" ({k} gün)"
        return ""
    except: return ""


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

    students = api.get_students()
    if not students:
        st.info("Önce Lila'dan öğrenci aktarın.")
        return

    mods_by_id  = {s["id"]: [m["name"] for m in s.get("modules",[])]   for s in students}
    diags_by_id = {s["id"]: [d["name"] for d in s.get("diagnoses",[])] for s in students}

    if "grup_uyeleri" not in st.session_state:
        st.session_state["grup_uyeleri"] = []
    grup = st.session_state["grup_uyeleri"]
    secilen_ids = {u["id"] for u in grup}

    # Başlık + sıfırla
    bc1, bc2 = st.columns([6,1])
    with bc1: st.header("🔎 Grup Oluştur")
    with bc2:
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        if st.button("🧹 Sıfırla", use_container_width=True):
            st.session_state["grup_uyeleri"] = []
            st.rerun()

    # ── Seçili üyeler ─────────────────────────────────────────────────────────
    for i, u in enumerate(grup):
        mod_badges = "".join(f'<span class="mod-badge">{m}</span>' for m in u["mod_adlari"])
        renk  = rapor_renk(u.get("rapor_bitis"))
        etiket= rapor_etiket(u.get("rapor_bitis"))
        yas_str = f"{yas(u.get('dob')):.0f} yaş" if yas(u.get('dob')) else ""
        sub_parts = [p for p in [yas_str, etiket.strip()] if p]
        sub_html  = " · ".join(sub_parts)

        kc, kx = st.columns([11,1])
        with kc:
            st.markdown(f"""
            <div class="oyuncu-kart">
              <div class="oyuncu-numara">{i+1}</div>
              <div style="flex:1;min-width:0;">
                <div class="oyuncu-ad">
                  <span style="display:inline-block;width:7px;height:7px;border-radius:50%;
                    background:{renk};margin-right:5px;vertical-align:middle;flex-shrink:0;"></span>
                  {u['name']}
                </div>
                <div class="oyuncu-sub">{sub_html}</div>
                <div style="margin-top:4px;">{mod_badges}</div>
              </div>
            </div>""", unsafe_allow_html=True)
        with kx:
            if i == len(grup)-1:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                if st.button("✕", key=f"cikart_{i}"):
                    st.session_state["grup_uyeleri"].pop()
                    st.rerun()

    # ── Sonraki seçim ─────────────────────────────────────────────────────────
    if len(grup) < 10:
        baslik = "👤 İlk öğrenciyi seçin" if not grup else f"➕ {len(grup)+1}. üyeyi seçin"
        if grup: st.caption(baslik + " · ortak modüllü, max 3 yaş farkı")
        else:     st.caption(baslik)

        if not grup:
            adaylar = [s for s in students if s["id"] not in secilen_ids]
        else:
            mod_setleri = [set(u["mod_adlari"]) for u in grup]
            ortak = set.intersection(*mod_setleri)
            doblar=[u["dob"] for u in grup if u.get("dob")]
            yas_min=min(yas(d) for d in doblar) if doblar else 0
            yas_max=max(yas(d) for d in doblar) if doblar else 100
            adaylar=[]
            for s in students:
                if s["id"] in secilen_ids: continue
                if not (set(mods_by_id.get(s["id"],[])) & ortak): continue
                sy=yas(s.get("dob"))
                if sy is not None and (sy < yas_min-3 or sy > yas_max+3): continue
                adaylar.append(s)

        if not adaylar and grup:
            st.info("Uyumlu öğrenci bulunamadı.")
        elif adaylar:
            aday_liste=["— Seç —"]
            aday_map={}
            for s in sorted(adaylar, key=lambda x:x["name"]):
                sy=yas(s.get("dob")); re_str=rapor_etiket(s.get("rapor_bitis"))
                et=s["name"]
                if sy: et+=f"  ·  {sy:.0f} yaş"
                if re_str: et+=re_str
                aday_liste.append(et); aday_map[et]=s
            sec=st.selectbox("", aday_liste, key=f"aday_{len(grup)}", label_visibility="collapsed")
            if sec!="— Seç —":
                s=aday_map[sec]
                st.session_state["grup_uyeleri"].append({
                    "id":s["id"],"name":s["name"],
                    "dob":s.get("dob"),"rapor_bitis":s.get("rapor_bitis"),
                    "mod_adlari":mods_by_id.get(s["id"],[]),
                    "diag_adlari":diags_by_id.get(s["id"],[]),
                })
                st.rerun()

    # ── Özet ve kaydet ────────────────────────────────────────────────────────
    if len(grup) >= 2:
        st.divider()
        ortak_mod = set.intersection(*[set(u["mod_adlari"]) for u in grup])
        doblar=[u["dob"] for u in grup if u.get("dob")]
        yas_farki=None
        if len(doblar)==len(grup):
            yaslar=[yas(d) for d in doblar]
            yas_farki=round(max(yaslar)-min(yaslar),1)

        uyarilar=[]
        if not ortak_mod: uyarilar.append("⚠️ Ortak modül yok — gruplanamaz.")
        if yas_farki and yas_farki>3: uyarilar.append(f"⚠️ Yaş farkı {yas_farki} yıl — 3 yılı aşıyor.")

        if uyarilar:
            for u in uyarilar: st.warning(u)
        else:
            mod_badges="".join(f'<span class="mod-badge">{m}</span>' for m in sorted(ortak_mod))
            isimler=" · ".join(u["name"] for u in grup)
            yas_str=f"{yas_farki} yıl fark" if yas_farki else "—"
            st.markdown(f"""
            <div class="grup-ozet">
              <div style="font-family:Sora,sans-serif;font-weight:700;font-size:14px;color:#1A2B4C;margin-bottom:6px;">
                ✅ Grup oluşturulabilir
              </div>
              <div style="font-size:13px;color:#1A2B4C;font-weight:500;margin-bottom:8px;">{isimler}</div>
              <div style="margin-bottom:6px;"><span style="font-size:11px;color:#6B7A99;">Ortak modüller:</span><br>{mod_badges}</div>
              <div style="font-size:12px;color:#6B7A99;">🎂 {yas_str} &nbsp;·&nbsp; 👥 {len(grup)} kişi</div>
            </div>""", unsafe_allow_html=True)

            nc, nkay = st.columns([3,1])
            with nc:
                not_val=st.text_input("Not (isteğe bağlı)", placeholder="Grup notu...", key="grup_not")
            with nkay:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                if st.button("⭐ Kaydet", type="primary", use_container_width=True, key="grup_kaydet"):
                    if api.create_saved_group({
                        "ogrenciler":" | ".join(u["name"] for u in grup),
                        "moduller":" / ".join(sorted(ortak_mod)),
                        "saat":None,"notlar":not_val or "","liste_adi":""}):
                        st.success("✅ Kaydedildi!")
                        st.session_state["grup_uyeleri"]=[]
                        st.rerun()
