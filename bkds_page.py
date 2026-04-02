"""
rehapp-frontend/bkds_page.py
BKDS Takip buton/link bileşeni
"""
import streamlit as st
import api_client as api


def render_bkds_button():
    """
    Sidebar veya herhangi bir yerde BKDS Takip butonu gösterir.
    Tıklanınca SSO URL alır, yeni sekmede açar.
    """
    st.markdown("""
    <style>
    .bkds-btn-wrap { margin: 8px 0; }
    .bkds-btn-wrap a {
        display: flex; align-items: center; gap: 10px;
        background: linear-gradient(135deg, #1A2B4C, #2756D6);
        color: white !important; text-decoration: none;
        border-radius: 10px; padding: 10px 16px;
        font-family: Sora, sans-serif; font-size: 13px; font-weight: 600;
        transition: opacity .2s;
    }
    .bkds-btn-wrap a:hover { opacity: .85; }
    </style>""", unsafe_allow_html=True)

    if st.button("📊 BKDS Takip Sistemine Git", use_container_width=True, key="bkds_btn"):
        with st.spinner("Bağlanıyor..."):
            try:
                result = api.get_bkds_sso_url()
                if result and result.get("redirect_url"):
                    url = result["redirect_url"]
                    st.markdown(
                        f"""<div class="bkds-btn-wrap">
                          <a href="{url}" target="_blank">
                            📊 BKDS Takip — Giriş yap
                          </a>
                        </div>
                        <div style="font-size:12px;color:#6B7A99;margin-top:4px;">
                          Yukarıdaki linke tıklayın (2 dakika geçerli)
                        </div>""",
                        unsafe_allow_html=True
                    )
                else:
                    st.error("BKDS bağlantısı kurulamadı.")
            except Exception as e:
                st.error(f"Hata: {e}")
