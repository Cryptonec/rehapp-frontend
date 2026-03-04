"""
Admin Paneli — sadece necmettinakgun@gmail.com görebilir.
"""
import streamlit as st
import api_client as api
from datetime import datetime, timezone


def sor_son_giris(tarih_str):
    if not tarih_str:
        return "–"
    try:
        dt = datetime.fromisoformat(tarih_str.replace("Z", "+00:00"))
        fark = datetime.now(timezone.utc) - dt
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

    def kid(k):
        for key in ("id", "kurum_id", "institution_id", "user_id"):
            if k.get(key) is not None:
                return k.get(key)
        return None

    def kad(k):
        return k.get("ad") or k.get("name") or "İsimsiz Kurum"

    def kemail(k):
        return k.get("email") or k.get("mail") or "-"

    def onaylandi_mi(k):
        for f in ("onaylandi", "onayli", "approved", "aktif"):
            if f in k:
                return bool(k[f])
        return False

    def aktif_mi(k):
        return bool(k.get("aktif", True))

    bekleyen = [k for k in kurumlar if not onaylandi_mi(k)]
    aktif    = [k for k in kurumlar if onaylandi_mi(k) and aktif_mi(k)]
    pasif    = [k for k in kurumlar if onaylandi_mi(k) and not aktif_mi(k)]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Toplam", len(kurumlar))
    m2.metric("Aktif", len(aktif))
    m3.metric("Onay Bekleyen", len(bekleyen),
              delta=f"+{len(bekleyen)}" if bekleyen else None,
              delta_color="inverse" if bekleyen else "off")
    m4.metric("Pasif", len(pasif))

    st.divider()

    # ── Silme onay dialogu ────────────────────────────────────────────────────
    if "sil_id" not in st.session_state:
        st.session_state["sil_id"] = None

    if st.session_state["sil_id"]:
        sil_id = st.session_state["sil_id"]
        sil_ad = st.session_state.get("sil_ad", "")
        st.warning(f"⚠️ **{sil_ad}** kurumunu silmek istediğinizden emin misiniz? Bu işlem **geri alınamaz.**")
        c1, c2 = st.columns(2)
        if c1.button("🗑️ Evet, Kalıcı Olarak Sil", type="primary", use_container_width=True):
            if api.admin_sil_kurum(sil_id):
                st.success("Kurum silindi.")
            else:
                st.error("Silme başarısız.")
            st.session_state["sil_id"] = None
            st.rerun()
        if c2.button("İptal", use_container_width=True):
            st.session_state["sil_id"] = None
            st.rerun()
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
            _id = kid(k)
            with st.expander(f"⏳ {kad(k)}  ·  {kemail(k)}"):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**E-posta**  \n{kemail(k)}")
                c2.markdown(f"**Kayıt**  \n{k.get('created_at','')[:10]}")
                c3.markdown(f"**Öğrenci**  \n{k.get('ogrenci_sayisi', 0)}")
                if _id is None:
                    st.warning("Kurum id bulunamadı.")
                    continue
                b1, b2, b3 = st.columns(3)
                if b1.button("✅ Onayla", key=f"onayla_{_id}", type="primary", use_container_width=True):
                    if api.admin_onayla(_id):
                        st.success("Onaylandı!")
                        st.rerun()
                if b2.button("✉️ Mail", key=f"resend_{_id}", use_container_width=True):
                    if api.admin_resend_onay_mail(_id):
                        st.success("Mail gönderildi.")
                if b3.button("🗑️ Sil", key=f"sil_b_{_id}", use_container_width=True):
                    st.session_state["sil_id"] = _id
                    st.session_state["sil_ad"] = kad(k)
                    st.rerun()

    # ── Aktif Kurumlar ────────────────────────────────────────────────────────
    st.markdown("""
    <div style='font-family:Sora,sans-serif;font-weight:700;font-size:15px;
         color:#1A2B4C;margin:16px 0 8px;'>✅ Aktif Kurumlar</div>""",
    unsafe_allow_html=True)

    for k in aktif:
        sg  = sor_son_giris(k.get("son_giris"))
        _id = kid(k)
        with st.expander(f"✅ {kad(k)}  ·  Son giriş: {sg}"):
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"**E-posta**  \n{kemail(k)}")
            c2.markdown(f"**Kayıt**  \n{k.get('created_at','')[:10]}")
            c3.markdown(f"**Öğrenci**  \n{k.get('ogrenci_sayisi', 0)}")
            c4.markdown(f"**Son giriş**  \n{sg}")
            if _id is None:
                continue
            b1, b2 = st.columns(2)
            if b1.button("🚫 Pasif Yap", key=f"pasif_{_id}", use_container_width=True):
                if api.admin_pasif(_id):
                    st.warning("Pasif yapıldı.")
                    st.rerun()
            if b2.button("🗑️ Sil", key=f"sil_a_{_id}", use_container_width=True):
                st.session_state["sil_id"] = _id
                st.session_state["sil_ad"] = kad(k)
                st.rerun()

    # ── Pasif Kurumlar ────────────────────────────────────────────────────────
    if pasif:
        st.markdown("""
        <div style='font-family:Sora,sans-serif;font-weight:700;font-size:15px;
             color:#1A2B4C;margin:16px 0 8px;'>🚫 Pasif Kurumlar</div>""",
        unsafe_allow_html=True)

        for k in pasif:
            _id = kid(k)
            with st.expander(f"🚫 {kad(k)}  ·  {kemail(k)}"):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**E-posta**  \n{kemail(k)}")
                c2.markdown(f"**Kayıt**  \n{k.get('created_at','')[:10]}")
                c3.markdown(f"**Öğrenci**  \n{k.get('ogrenci_sayisi', 0)}")
                if _id is None:
                    continue
                if st.button("🗑️ Sil", key=f"sil_p_{_id}", use_container_width=True):
                    st.session_state["sil_id"] = _id
                    st.session_state["sil_ad"] = kad(k)
                    st.rerun()