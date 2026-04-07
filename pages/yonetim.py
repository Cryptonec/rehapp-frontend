import streamlit as st
import api_client as api


def _render_bkds_section():
    st.subheader("📊 BKDS Takip")

    if api.is_demo_mode():
        st.info("Demo hesapta BKDS Takip bağlantısı kullanılamaz.")
        return

try:
    creds = api.get_bkds_credentials()
except Exception:
    creds = {"bkds_email": None, "bkds_configured": False}
    configured = creds.get("bkds_configured", False)

    if configured:
        bkds_url = api.get_bkds_sso_url()
        if bkds_url:
            st.markdown(
                f"""<a href="{bkds_url}" target="_blank" rel="noopener noreferrer"
                       style="display:inline-flex;align-items:center;gap:6px;
                              padding:0.45rem 1.1rem;background:#1d4ed8;color:white;
                              border-radius:6px;text-decoration:none;font-size:0.95rem;
                              font-weight:600;">
                      📊 BKDS Takip'i Aç
                    </a>""",
                unsafe_allow_html=True,
            )
            st.caption("Yeni sekmede açılır. Tekrar giriş gerektirmez.")
        else:
            st.error("BKDS bağlantısı kurulamadı. Kimlik bilgilerini kontrol edin.")
    else:
        st.warning("BKDS Takip henüz bağlanmamış. Aşağıdan giriş bilgilerini girin.")

    with st.expander(
        "🔧 BKDS giriş bilgilerini güncelle" if configured else "🔧 BKDS giriş bilgilerini gir",
        expanded=not configured,
    ):
        st.caption(
            f"Mevcut e-posta: **{creds['bkds_email']}**" if configured else
            "bkds-takip uygulamasındaki kurum admin hesabını girin."
        )
        with st.form("bkds_creds_form"):
            new_email = st.text_input(
                "BKDS Takip E-posta",
                value=creds.get("bkds_email") or "",
                placeholder="admin@kurumunuz.com",
            )
            new_password = st.text_input(
                "BKDS Takip Şifresi",
                type="password",
                placeholder="Değiştirmek istemiyorsanız boş bırakın" if configured else "",
            )
            submitted = st.form_submit_button("Kaydet", type="primary")

        if submitted:
            if not new_email:
                st.error("E-posta boş olamaz.")
            else:
                result = api.update_bkds_credentials(new_email, new_password)
                if result and result.get("bkds_configured"):
                    st.success("Kaydedildi!")
                    st.rerun()
                elif result:
                    st.warning("E-posta kaydedildi ancak şifre eksik.")


def show():
    st.header("⚙️ Yönetim")

    is_demo = api.is_demo_mode()
    if is_demo:
        st.info("🎭 Demo hesapta tanı ve modüller salt-okunurdur. Ekleme veya silme yapılamaz.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Tanılar")
        diags = api.get_diagnoses()
        for d in diags:
            c1, c2 = st.columns([4, 1])
            c1.write(d["name"])
            if not is_demo:
                if c2.button("🗑", key=f"del_diag_{d['id']}"):
                    if api.delete_diagnosis(d["id"]):
                        st.success("Tanı silindi")
                        st.rerun()
        if not is_demo:
            with st.form("new_diag", clear_on_submit=True):
                name = st.text_input("Yeni tanı adı")
                if st.form_submit_button("Ekle"):
                    if name.strip():
                        api.create_diagnosis(name.strip())
                        st.rerun()

    with col2:
        st.subheader("Modüller")
        mods = api.get_modules()
        for m in mods:
            c1, c2 = st.columns([4, 1])
            c1.write(m["name"])
            if not is_demo:
                if c2.button("🗑", key=f"del_mod_{m['id']}"):
                    if api.delete_module(m["id"]):
                        st.success("Modül silindi")
                        st.rerun()
        if not is_demo:
            with st.form("new_mod", clear_on_submit=True):
                name = st.text_input("Yeni modül adı")
                if st.form_submit_button("Ekle"):
                    if name.strip():
                        api.create_module(name.strip())
                        st.rerun()

    st.divider()
    _render_bkds_section()
