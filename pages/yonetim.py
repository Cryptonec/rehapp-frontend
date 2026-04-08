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
    current_user = creds.get("bkds_email", "")

    # Durum kartı
    if configured:
        st.markdown(
            f"""
            <div style="background:#f0fdf4;border:1.5px solid #86efac;border-radius:12px;
                        padding:16px 20px;margin-bottom:16px;display:flex;align-items:center;gap:12px;">
                <span style="font-size:1.4rem;">✅</span>
                <div>
                    <div style="font-weight:700;color:#166534;font-size:0.95rem;">BKDS Bağlı</div>
                    <div style="color:#15803d;font-size:0.85rem;">Kullanıcı: <b>{current_user}</b></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # BKDS Takip'i Aç butonu
        bkds_url = api.get_bkds_sso_url()
        if bkds_url:
            st.markdown(
                f"""<a href="{bkds_url}" target="_blank" rel="noopener noreferrer"
                       style="display:inline-flex;align-items:center;gap:8px;
                              padding:0.6rem 1.4rem;background:#1d4ed8;color:white;
                              border-radius:8px;text-decoration:none;font-size:1rem;
                              font-weight:700;box-shadow:0 2px 8px #1d4ed822;">
                      📊&nbsp; BKDS Takip&apos;i Aç
                    </a>
                    <span style="display:block;margin-top:6px;color:#6b7280;font-size:0.8rem;">
                      Yeni sekmede açılır · Tekrar giriş gerektirmez
                    </span>""",
                unsafe_allow_html=True,
            )
        else:
            st.error("BKDS bağlantısı kurulamadı.")
    else:
        st.markdown(
            """
            <div style="background:#fff7ed;border:1.5px solid #fed7aa;border-radius:12px;
                        padding:16px 20px;margin-bottom:16px;display:flex;align-items:center;gap:12px;">
                <span style="font-size:1.4rem;">⚠️</span>
                <div>
                    <div style="font-weight:700;color:#9a3412;font-size:0.95rem;">BKDS henüz bağlanmamış</div>
                    <div style="color:#c2410c;font-size:0.85rem;">Aşağıdan giriş bilgilerinizi girin.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # Giriş bilgileri formu
    with st.expander(
        "✏️ Giriş bilgilerini güncelle" if configured else "🔑 Giriş bilgilerini gir",
        expanded=not configured,
    ):
        st.caption("bkds.meb.gov.tr hesabınızın giriş bilgilerini girin.")
        with st.form("bkds_creds_form"):
            new_email = st.text_input(
                "Kullanıcı Adı",
                value=current_user,
                placeholder="bkds.meb.gov.tr kullanıcı adı",
            )
            new_password = st.text_input(
                "Şifre",
                type="password",
                placeholder="bkds.meb.gov.tr şifresi",
            )
            submitted = st.form_submit_button("💾  Kaydet", type="primary", use_container_width=True)

        if submitted:
            if not new_email:
                st.error("Kullanıcı adı boş olamaz.")
            elif not new_password:
                st.error("Şifre boş olamaz.")
            else:
                result = api.update_bkds_credentials(new_email, new_password)
                if result and result.get("bkds_configured"):
                    st.success("✅ Kaydedildi!")
                    st.rerun()
                else:
                    st.error("Kaydetme başarısız.")
