"""
Rehapp – Özel Eğitim / Rehabilitasyon Merkezi Grup Planlayıcı
Frontend: Streamlit  |  Backend: FastAPI  |  DB: PostgreSQL
"""
import streamlit as st
import api_client as api

# ── Sayfa ayarları ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Rehapp",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state başlangıç değerleri ─────────────────────────────────────────
for key in ("token", "kurum_id", "kurum_ad"):
    if key not in st.session_state:
        st.session_state[key] = None


# ── Yardımcı: giriş sayfasına yönlendir ──────────────────────────────────────
def require_login() -> bool:
    """Giriş yoksa login panelini göster, True ise devam et."""
    return st.session_state["token"] is not None


# ── Login / Kayıt formu ───────────────────────────────────────────────────────
def show_login():
    st.title("🧠 Rehapp – Giriş")
    tab_giris, tab_kayit = st.tabs(["Giriş Yap", "Kayıt Ol"])

    with tab_giris:
        with st.form("login_form"):
            email    = st.text_input("E-posta")
            password = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş Yap"):
                if not email or not password:
                    st.warning("E-posta ve şifre zorunlu.")
                else:
                    data = api.login(email, password)
                    if data:
                        st.session_state["token"]    = data["access_token"]
                        st.session_state["kurum_id"] = data["kurum_id"]
                        st.session_state["kurum_ad"] = data["kurum_ad"]
                        st.rerun()

    with tab_kayit:
        with st.form("register_form"):
            ad       = st.text_input("Kurum adı")
            email    = st.text_input("E-posta")
            password = st.text_input("Şifre", type="password")
            if st.form_submit_button("Kayıt Ol"):
                if not all([ad, email, password]):
                    st.warning("Tüm alanlar zorunlu.")
                else:
                    data = api.register(ad, email, password)
                    if data:
                        st.session_state["token"]    = data["access_token"]
                        st.session_state["kurum_id"] = data["kurum_id"]
                        st.session_state["kurum_ad"] = data["kurum_ad"]
                        st.success("Kayıt başarılı! Yönlendiriliyor…")
                        st.rerun()


# ── Üst bar ───────────────────────────────────────────────────────────────────
def show_topbar():
    col1, col2 = st.columns([8, 2])
    col1.markdown(f"### 🧠 Rehapp &nbsp; | &nbsp; {st.session_state['kurum_ad']}")
    if col2.button("🚪 Çıkış Yap"):
        for key in ("token", "kurum_id", "kurum_ad"):
            st.session_state[key] = None
        st.rerun()
    st.divider()


# ── Ana akış ──────────────────────────────────────────────────────────────────
if not require_login():
    show_login()
    st.stop()

# Kurum ID kontrolü (token var ama kurum_id yoksa güvenlik için logout)
if not st.session_state.get("kurum_id"):
    st.error("Kurum bilgisi bulunamadı. Lütfen tekrar giriş yapın.")
    for key in ("token", "kurum_id", "kurum_ad"):
        st.session_state[key] = None
    st.stop()

show_topbar()

# ── Sekmeler ──────────────────────────────────────────────────────────────────
from pages import yonetim, ogrenciler, grup_ara, kaydedilen_gruplar  # noqa: E402

tab1, tab2, tab3, tab4 = st.tabs([
    "⚙️ Yönetim",
    "👨‍🎓 Öğrenci",
    "🔍 Öğrenciye Göre Ara",
    "📁 Kaydedilen Gruplar",
])

with tab1:
    yonetim.show()
with tab2:
    ogrenciler.show()
with tab3:
    grup_ara.show()
with tab4:
    kaydedilen_gruplar.show()
