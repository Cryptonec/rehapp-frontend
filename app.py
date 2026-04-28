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
for key in ("token", "kurum_id", "kurum_ad", "is_demo"):
    if key not in st.session_state:
        st.session_state[key] = None


# ── Yardımcı: giriş sayfasına yönlendir ──────────────────────────────────────
def require_login() -> bool:
    """Giriş yoksa login panelini göster, True ise devam et."""
    return st.session_state["token"] is not None


def _start_demo():
    """Demo hesabı oturumunu başlat."""
    st.session_state["token"]    = "DEMO_TOKEN"
    st.session_state["kurum_id"] = 0
    st.session_state["kurum_ad"] = "Demo Kurumu"
    st.session_state["is_demo"]  = True
    st.session_state["demo_students"]        = []
    st.session_state["demo_saved_groups"]    = []
    st.session_state["demo_next_student_id"] = 2000
    st.session_state["demo_next_group_id"]   = 4000


# ── Login / Kayıt formu ───────────────────────────────────────────────────────
def show_login():
    st.title("🧠 Rehapp – Giriş")

    with st.container(border=True):
        col_txt, col_btn = st.columns([5, 2])
        col_txt.markdown(
            "**Demo Hesap** – Kayıt olmadan uygulamayı deneyin. "
            "20 örnek öğrenci ve 3 kaydedilmiş grup ile gelir. "
            "Gerçek veriler kaydedilmez."
        )
        if col_btn.button("🎭 Demo ile Giriş", use_container_width=True, type="primary"):
            _start_demo()
            st.rerun()

    st.divider()

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
    kurum_label = st.session_state["kurum_ad"]
    if st.session_state.get("is_demo"):
        kurum_label += " 🎭"
    col1.markdown(f"### 🧠 Rehapp &nbsp; | &nbsp; {kurum_label}")
    if col2.button("🚪 Çıkış Yap"):
        for key in ("token", "kurum_id", "kurum_ad", "is_demo",
                    "demo_students", "demo_saved_groups",
                    "demo_next_student_id", "demo_next_group_id"):
            st.session_state[key] = None
        st.rerun()
    st.divider()

    if st.session_state.get("is_demo"):
        st.info(
            "🎭 **Demo Hesap** – Yaptığınız değişiklikler yalnızca bu oturumda geçerlidir. "
            "Gerçek hesap için çıkış yapıp kayıt olabilirsiniz.",
            icon=None,
        )


# ── Ana akış ──────────────────────────────────────────────────────────────────
if not require_login():
    show_login()
    st.stop()

if st.session_state.get("kurum_id") is None:
    st.error("Kurum bilgisi bulunamadı. Lütfen tekrar giriş yapın.")
    for key in ("token", "kurum_id", "kurum_ad", "is_demo"):
        st.session_state[key] = None
    st.stop()

show_topbar()

# ── Sekmeler ──────────────────────────────────────────────────────────────────
from pages import yonetim, ogrenciler, grup_ara, kaydedilen_gruplar  # noqa: E402

TAB_LABELS = [
    "⚙️ Yönetim",
    "👨‍🎓 Öğrenci",
    "🔍 Öğrenciye Göre Ara",
    "📁 Kaydedilen Gruplar",
]

if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = TAB_LABELS[0]

active = st.radio(
    "Sayfa",
    TAB_LABELS,
    horizontal=True,
    label_visibility="collapsed",
    key="active_tab",
)

st.divider()

if active == TAB_LABELS[0]:
    yonetim.show()
elif active == TAB_LABELS[1]:
    ogrenciler.show()
elif active == TAB_LABELS[2]:
    grup_ara.show()
elif active == TAB_LABELS[3]:
    kaydedilen_gruplar.show()
