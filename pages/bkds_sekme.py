"""
rehapp-frontend/pages/bkds_sekme.py
BKDS Takip sekmesi
"""
import streamlit as st
import api_client as api


def show():
    st.markdown("""
    <style>
    .bkds-hero {
        background: linear-gradient(135deg, #0D1B35 0%, #1A3A6B 60%, #0E6655 100%);
        border-radius: 20px; padding: 36px 40px; margin-bottom: 28px;
        position: relative; overflow: hidden;
    }
    .bkds-hero::before {
        content: ''; position: absolute; top: -40px; right: -40px;
        width: 180px; height: 180px; border-radius: 50%;
        background: rgba(56,201,192,.1);
    }
    .bkds-btn {
        display: inline-flex; align-items: center; gap: 10px;
        background: linear-gradient(135deg, #38C9C0, #2756D6);
        color: white !important; text-decoration: none;
        border-radius: 12px; padding: 14px 28px;
        font-family: Sora, sans-serif; font-size: 15px; font-weight: 700;
        box-shadow: 0 4px 15px rgba(39,86,214,.3);
        transition: opacity .2s; margin-top: 8px;
    }
    .bkds-btn:hover { opacity: .88; }
    .bkds-info-card {
        background: white; border: 1px solid rgba(26,43,76,.08);
        border-radius: 14px; padding: 20px 24px; margin-bottom: 12px;
    }
    </style>""", unsafe_allow_html=True)

    kurum_ad = st.session_state.get("kurum_ad", "")

    st.markdown(f"""
    <div class="bkds-hero">
      <div style="font-family:Sora,sans-serif;font-size:12px;font-weight:600;
           color:rgba(56,201,192,.8);letter-spacing:1.5px;text-transform:uppercase;
           margin-bottom:8px;">BKDS TAKİP SİSTEMİ</div>
      <div style="font-family:Sora,sans-serif;font-size:22px;font-weight:800;
           color:white;margin-bottom:10px;">Biyometrik Devamsızlık Takibi</div>
      <div style="font-size:14px;color:rgba(255,255,255,.65);line-height:1.8;max-width:500px;">
        Devlet destekli eğitim için BKDS sistemine entegre devamsızlık takibi.
        Rehapp hesabınızla otomatik giriş yapın.
      </div>
    </div>""", unsafe_allow_html=True)

    # SSO URL al ve butonu göster
    col1, col2 = st.columns([2, 3])
    with col1:
        if st.button("📊 BKDS Takip'i Aç", type="primary",
                     use_container_width=True, key="bkds_ac"):
            with st.spinner("Bağlantı kuruluyor..."):
                result = api.get_bkds_sso_url()
                if result and result.get("redirect_url"):
                    url = result["redirect_url"]
                    st.session_state["bkds_url"] = url
                    st.rerun()
                else:
                    st.error("BKDS bağlantısı kurulamadı. Yöneticinizle iletişime geçin.")

    # URL hazırsa link göster
    if st.session_state.get("bkds_url"):
        url = st.session_state.pop("bkds_url")
        st.markdown(f"""
        <div style="background:rgba(56,201,192,.08);border:1.5px solid rgba(56,201,192,.3);
             border-radius:12px;padding:16px 20px;margin-top:8px;">
          <div style="font-family:Sora,sans-serif;font-size:13px;font-weight:600;
               color:#1A2B4C;margin-bottom:8px;">✅ Bağlantı hazır — aşağıya tıklayın</div>
          <a href="{url}" target="_blank" class="bkds-btn">
            📊 BKDS Takip'e Git →
          </a>
          <div style="font-size:11px;color:#6B7A99;margin-top:10px;">
            Bu link 5 dakika geçerlidir. Yeni sekme açılır, tekrar giriş gerekmez.
          </div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # Bilgi kartları
    st.markdown("""
    <div style="font-family:Sora,sans-serif;font-size:15px;font-weight:700;
         color:#0D1B35;margin-bottom:12px;">BKDS Takip Nedir?</div>""",
    unsafe_allow_html=True)

    cols = st.columns(3)
    kartlar = [
        ("🖥️", "Canlı Takip", "Personelin giriş-çıkışlarını anlık olarak izleyin"),
        ("📋", "Devamsızlık Raporu", "Günlük, haftalık devamsızlık raporlarına erişin"),
        ("🔔", "Otomatik Bildirim", "Geç kalma ve devamsızlıklarda anında uyarı alın"),
    ]
    for col, (ikon, baslik, aciklama) in zip(cols, kartlar):
        with col:
            st.markdown(f"""
            <div class="bkds-info-card">
              <div style="font-size:28px;margin-bottom:8px;">{ikon}</div>
              <div style="font-family:Sora,sans-serif;font-weight:700;font-size:14px;
                   color:#1A2B4C;margin-bottom:6px;">{baslik}</div>
              <div style="font-size:13px;color:#6B7A99;line-height:1.6;">{aciklama}</div>
            </div>""", unsafe_allow_html=True)
