"""
Admin Paneli — sadece necmettinakgun@gmail.com görebilir.
Üyelik onayı, son giriş zamanı, pasif yapma.
"""
import streamlit as st
import api_client as api
from datetime import datetime


def sor_son_giris(tarih_str):
    if not tarih_str:
        return "–"
    try:
        dt = datetime.fromisoformat(tarih_str.replace("Z",""))
        fark = datetime.now() - dt
        g = fark.days
        s = fark.seconds // 3600
        if g == 0 and s == 0: return "Az önce"
        if g == 0: return f"{s} saat önce"
        if g == 1: return "Dün"
        if g < 30: return f"{g} gün önce"
        return tarih_str[:10]
    except:
        return tarih_str[:10] if tarih_str else "–"


def show():
    email = st.session_state.get("kurum_email", "")
    if email != "necmettinakgun@gmail.com":
        st.error("Bu sayfaya erişim yetkiniz yok.")
        return

    st.header("🛡️ Admin Paneli")

    kurumlar = api.admin_get_kurumlar()
    if not kurumlar:
        st.info("Kurum bulunamadı.")
        return

    aktif   = [k for k in kurumlar if k.get("aktif")]
    bekleyen = [k for k in kurumlar if not k.get("aktif")]

    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Kurum", len(kurumlar))
    m2.metric("Aktif", len(aktif))
    m3.metric("Onay Bekleyen", len(bekleyen), delta=f"+{len(bekleyen)}" if bekleyen else None,
              delta_color="inverse" if bekleyen else "off")

    st.divider()

    # ── Onay Bekleyenler ──────────────────────────────────────────────────────
    if bekleyen:
        st.markdown("""
        <div style='background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.2);
             border-radius:12px;padding:12px 16px;margin-bottom:16px;'>
          <span style='font-family:Sora,sans-serif;font-weight:600;color:#dc2626;'>
            ⏳ Onay Bekleyen Kurumlar
          </span>
        </div>""", unsafe_allow_html=True)

        for k in bekleyen:
            with st.expander(f"⏳ {k['ad']}  ·  {k['email']}"):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**E-posta**  \n{k['email']}")
                c2.markdown(f"**Kayıt**  \n{k.get('created_at','')[:10]}")
                c3.markdown(f"**Öğrenci**  \n{k.get('ogrenci_sayisi', 0)}")
                if st.button("✅ Onayla", key=f"onayla_{k['id']}", type="primary"):
                    if api.admin_onayla(k["id"]):
                        st.success("Onaylandı!")
                        st.rerun()

    # ── Aktif Kurumlar ────────────────────────────────────────────────────────
    st.markdown("""
    <div style='font-family:Sora,sans-serif;font-weight:700;font-size:15px;
         color:#1A2B4C;margin:16px 0 8px;'>✅ Aktif Kurumlar</div>""",
    unsafe_allow_html=True)

    for k in aktif:
        sg = sor_son_giris(k.get("son_giris"))
        with st.expander(f"✅ {k['ad']}  ·  Son giriş: {sg}"):
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"**E-posta**  \n{k['email']}")
            c2.markdown(f"**Kayıt**  \n{k.get('created_at','')[:10]}")
            c3.markdown(f"**Öğrenci**  \n{k.get('ogrenci_sayisi', 0)}")
            c4.markdown(f"**Son giriş**  \n{sg}")

            if st.button("🚫 Pasif Yap", key=f"pasif_{k['id']}"):
                if api.admin_pasif(k["id"]):
                    st.warning("Pasif yapıldı.")
                    st.rerun()
