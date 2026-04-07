import streamlit as st
import api_client as api


def show():
    if api.is_demo_mode():
        st.info("Demo hesapta BKDS Takip bağlantısı kullanılamaz.")
        return

    try:
        creds = api.get_bkds_credentials() or {}
    except Exception:
        creds = {}

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
        "🔧 Giriş bilgilerini güncelle" if configured else "🔧 Giriş bilgilerini gir",
        expanded=not configured,
    ):
        if configured:
            st.caption(f"Mevcut kullanıcı adı: **{creds.get('bkds_email')}**")
        else:
            st.caption("bkds-takip uygulamasındaki kurum admin hesabını girin.")
        with st.form("bkds_creds_form"):
            new_email = st.text_input(
                "BKDS Takip Kullanıcı Adı",
                value=creds.get("bkds_email") or "",
            )
            new_password = st.text_input(
                "BKDS Takip Şifresi",
                type="password",
            )
            submitted = st.form_submit_button("Kaydet", type="primary")

        if submitted:
            if not new_email:
                st.error("Kullanıcı adı boş olamaz.")
            else:
                result = api.update_bkds_credentials(new_email, new_password)
                if result and result.get("bkds_configured"):
                    st.success("Kaydedildi!")
                    st.rerun()
                elif result:
                    st.warning("Kullanıcı adı kaydedildi ancak şifre eksik.")
