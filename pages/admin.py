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

    def kurum_id(kurum):
        for key in ("id", "kurum_id", "institution_id", "user_id"):
            if kurum.get(key) is not None:
                return kurum.get(key)
        return None

    def kurum_ad(kurum):
        return kurum.get("ad") or kurum.get("name") or "İsimsiz Kurum"

    def kurum_email(kurum):
        return kurum.get("email") or kurum.get("mail") or "-"

    def onaylandi_mi(kurum):
        if "onaylandi" in kurum:
            return bool(kurum.get("onaylandi"))
        if "onayli" in kurum:
            return bool(kurum.get("onayli"))
        if "approved" in kurum:
            return bool(kurum.get("approved"))
        # Eski backend'lerde sadece aktif alanı bulunabiliyor.
        return bool(kurum.get("aktif"))

    def aktif_mi(kurum):
        return bool(kurum.get("aktif", True))

    bekleyen = [k for k in kurumlar if not onaylandi_mi(k)]
    aktif = [k for k in kurumlar if onaylandi_mi(k) and aktif_mi(k)]
    pasif = [k for k in kurumlar if onaylandi_mi(k) and not aktif_mi(k)]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Toplam Kurum", len(kurumlar))
    m2.metric("Aktif", len(aktif))
    m3.metric("Onay Bekleyen", len(bekleyen), delta=f"+{len(bekleyen)}" if bekleyen else None,
              delta_color="inverse" if bekleyen else "off")
    m4.metric("Pasif", len(pasif))

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
            kid = kurum_id(k)
            with st.expander(f"⏳ {kurum_ad(k)}  ·  {kurum_email(k)}"):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**E-posta**  \n{kurum_email(k)}")
                c2.markdown(f"**Kayıt**  \n{k.get('created_at','')[:10]}")
                c3.markdown(f"**Öğrenci**  \n{k.get('ogrenci_sayisi', 0)}")
                if kid is None:
                    st.warning("Bu kayıtta kurum id bulunamadığı için işlem yapılamıyor.")
                    continue
                b1, b2 = st.columns(2)
                if b1.button("✅ Onayla", key=f"onayla_{kid}", type="primary", use_container_width=True):
                    if api.admin_onayla(kid):
                        st.success("Onaylandı!")
                        st.rerun()
                if b2.button("✉️ Resend", key=f"resend_{kid}", use_container_width=True):
                    if api.admin_resend_onay_mail(kid):
                        st.success("Resend talebi gönderildi.")

    # ── Aktif Kurumlar ────────────────────────────────────────────────────────
    st.markdown("""
    <div style='font-family:Sora,sans-serif;font-weight:700;font-size:15px;
         color:#1A2B4C;margin:16px 0 8px;'>✅ Aktif Kurumlar</div>""",
    unsafe_allow_html=True)

    for k in aktif:
        sg = sor_son_giris(k.get("son_giris"))
        kid = kurum_id(k)
        with st.expander(f"✅ {kurum_ad(k)}  ·  Son giriş: {sg}"):
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"**E-posta**  \n{kurum_email(k)}")
            c2.markdown(f"**Kayıt**  \n{k.get('created_at','')[:10]}")
            c3.markdown(f"**Öğrenci**  \n{k.get('ogrenci_sayisi', 0)}")
            c4.markdown(f"**Son giriş**  \n{sg}")

            if kid is None:
                st.warning("Bu kayıtta kurum id bulunamadığı için pasif işlemi yapılamıyor.")
                continue

            if st.button("🚫 Pasif Yap", key=f"pasif_{kid}"):
                if api.admin_pasif(kid):
                    st.warning("Pasif yapıldı.")
                    st.rerun()

    if pasif:
        st.markdown("""
        <div style='font-family:Sora,sans-serif;font-weight:700;font-size:15px;
             color:#1A2B4C;margin:16px 0 8px;'>🚫 Pasif Kurumlar</div>""",
        unsafe_allow_html=True)

        for k in pasif:
            with st.expander(f"🚫 {kurum_ad(k)}  ·  {kurum_email(k)}"):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**E-posta**  \n{kurum_email(k)}")
                c2.markdown(f"**Kayıt**  \n{k.get('created_at','')[:10]}")
                c3.markdown(f"**Öğrenci**  \n{k.get('ogrenci_sayisi', 0)}")
