"""
Rehapp – Ana uygulama
Sekme sırası: Kaydedilen Gruplar | Öğrenci | Grup Oluştur | Yönetim | (Admin)
"""
import streamlit as st
import api_client as api

st.set_page_config(
    page_title="Rehapp",
    page_icon="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzMiAzMiI+CiAgPHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiByeD0iOCIgZmlsbD0iIzFBMkI0QyIvPgogIDxjaXJjbGUgY3g9IjgiIGN5PSIxNiIgcj0iNSIgZmlsbD0iIzJCNTJDNCIvPgogIDxjaXJjbGUgY3g9IjE2IiBjeT0iMTYiIHI9IjUiIGZpbGw9IiM0MkI4QjEiLz4KICA8Y2lyY2xlIGN4PSIyNCIgY3k9IjE2IiByPSI1IiBmaWxsPSIjRjM5MjM3Ii8+Cjwvc3ZnPg==",
    layout="wide",
    initial_sidebar_state="collapsed",
)

for key in ("token","kurum_id","kurum_ad","kurum_email","show_login"):
    if key not in st.session_state:
        st.session_state[key] = None


# ══════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
def landing_sayfasi():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
    html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;}
    .stApp{background:#fff!important;}
    #MainMenu,footer,header{visibility:hidden!important;}
    [data-testid="stToolbar"]{display:none!important;}
    .block-container{padding:0!important;max-width:100%!important;}
    .stButton{position:fixed!important;top:16px!important;right:24px!important;z-index:9999!important;width:auto!important;}
    .stButton>button{background:linear-gradient(135deg,#42B8B1,#2B52C4)!important;color:white!important;
      font-family:Sora,sans-serif!important;font-weight:600!important;font-size:14px!important;
      border-radius:50px!important;border:none!important;padding:10px 24px!important;
      height:auto!important;white-space:nowrap!important;width:auto!important;
      box-shadow:0 4px 14px rgba(66,184,177,.35)!important;}
    @keyframes rh-in{from{opacity:0;transform:scale(0) translateY(14px)}to{opacity:1;transform:scale(1) translateY(0)}}
    @keyframes rh-bounce{0%,100%{transform:translateY(0)}40%{transform:translateY(-14px)}65%{transform:translateY(-6px)}}
    @keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
    .rh-d1{background:#2B52C4;animation:rh-in .35s cubic-bezier(.34,1.56,.64,1) .05s both,rh-bounce .7s ease-in-out .8s 3}
    .rh-d2{background:#42B8B1;animation:rh-in .35s cubic-bezier(.34,1.56,.64,1) .18s both,rh-bounce .7s ease-in-out .95s 3}
    .rh-d3{background:#F39237;animation:rh-in .35s cubic-bezier(.34,1.56,.64,1) .31s both,rh-bounce .7s ease-in-out 1.1s 3}
    .rh-word{animation:fadeUp .4s ease .55s both}
    .rh-tag{animation:fadeUp .4s ease .75s both}
    .rh-hero{animation:fadeUp .6s ease 1.1s both}
    </style>""", unsafe_allow_html=True)

    if st.button("Giriş Yap / Kayıt Ol →"):
        st.session_state["show_login"] = True
        st.rerun()

    st.markdown("""
    <div style="min-height:100vh;background:white;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:60px 20px 40px;text-align:center;position:relative;overflow:hidden;">
      <div style="position:absolute;width:500px;height:500px;border-radius:50%;background:#42B8B1;filter:blur(80px);opacity:.06;top:-150px;right:-100px;pointer-events:none"></div>
      <div style="position:absolute;width:400px;height:400px;border-radius:50%;background:#2B52C4;filter:blur(80px);opacity:.05;bottom:-100px;left:-80px;pointer-events:none"></div>
      <div style="display:flex;gap:14px;justify-content:center;margin-bottom:16px;">
        <div class="rh-d1" style="width:18px;height:18px;border-radius:50%;"></div>
        <div class="rh-d2" style="width:18px;height:18px;border-radius:50%;"></div>
        <div class="rh-d3" style="width:18px;height:18px;border-radius:50%;"></div>
      </div>
      <div class="rh-word" style="font-family:Sora,sans-serif;font-size:48px;font-weight:800;color:#1A2B4C;letter-spacing:-2px;line-height:1;">Reh<span style="color:#42B8B1">app</span></div>
      <div class="rh-tag" style="font-size:15px;font-weight:300;color:#6B7A99;margin-top:8px;margin-bottom:40px;">Akıllı Grup Planlama Platformu</div>
      <div class="rh-hero" style="max-width:580px;">
        <div style="display:inline-flex;align-items:center;gap:8px;background:rgba(66,184,177,.1);border:1px solid rgba(66,184,177,.25);color:#42B8B1;font-size:13px;font-weight:500;padding:6px 16px;border-radius:50px;margin-bottom:24px;">
          <span style="width:6px;height:6px;background:#42B8B1;border-radius:50%;display:inline-block;"></span>
          Özel Eğitim ve Rehabilitasyon Merkezleri İçin
        </div>
        <h1 style="font-family:Sora,sans-serif;font-size:clamp(32px,5vw,54px);font-weight:800;line-height:1.15;letter-spacing:-1.5px;color:#1A2B4C;margin-bottom:20px;">
          Grupları <span style="color:#42B8B1;border-bottom:3px solid #F39237;">akıllıca</span> planla,<br>zamanı kazan
        </h1>
        <p style="font-size:17px;font-weight:300;color:#6B7A99;line-height:1.7;margin-bottom:0;">
          Öğrenci tanılarını, modüllerini ve RAM raporlarını tek platformda yönetin. Uygun grupları saniyeler içinde bulun.
        </p>
      </div>
    </div>
    <div style="background:#F4F7FB;padding:80px 6%;">
      <div style="text-align:center;margin-bottom:48px;">
        <div style="font-size:12px;font-weight:600;color:#42B8B1;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">Özellikler</div>
        <h2 style="font-family:Sora,sans-serif;font-size:clamp(24px,3vw,36px);font-weight:700;color:#1A2B4C;">Her şey tek platformda</h2>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:20px;max-width:1100px;margin:0 auto;">
        <div style="background:white;border-radius:16px;padding:28px;border:1px solid rgba(26,43,76,.06);">
          <div style="font-size:28px;margin-bottom:12px;">🧩</div>
          <div style="font-family:Sora,sans-serif;font-weight:600;color:#1A2B4C;margin-bottom:8px;">Akıllı Grup Eşleştirme</div>
          <div style="font-size:14px;color:#6B7A99;line-height:1.6;">Tanı ve modüllere göre en uygun kombinasyonları otomatik bulur.</div>
        </div>
        <div style="background:white;border-radius:16px;padding:28px;border:1px solid rgba(26,43,76,.06);">
          <div style="font-size:28px;margin-bottom:12px;">📋</div>
          <div style="font-family:Sora,sans-serif;font-weight:600;color:#1A2B4C;margin-bottom:8px;">RAM Rapor Takibi</div>
          <div style="font-size:14px;color:#6B7A99;line-height:1.6;">Bitiş tarihi yaklaşan raporlar için otomatik uyarılar.</div>
        </div>
        <div style="background:white;border-radius:16px;padding:28px;border:1px solid rgba(26,43,76,.06);">
          <div style="font-size:28px;margin-bottom:12px;">📥</div>
          <div style="font-family:Sora,sans-serif;font-weight:600;color:#1A2B4C;margin-bottom:8px;">Lila Import</div>
          <div style="font-size:14px;color:#6B7A99;line-height:1.6;">Lila dosyalarını tek tıkla içe aktarın, öğrenci bilgileri otomatik eşleşir.</div>
        </div>
        <div style="background:white;border-radius:16px;padding:28px;border:1px solid rgba(26,43,76,.06);">
          <div style="font-size:28px;margin-bottom:12px;">📱</div>
          <div style="font-family:Sora,sans-serif;font-weight:600;color:#1A2B4C;margin-bottom:8px;">Mobil Uyumlu</div>
          <div style="font-size:14px;color:#6B7A99;line-height:1.6;">Telefon veya tabletten tam performansla çalışır.</div>
        </div>
      </div>
    </div>
    <div style="background:#1A2B4C;padding:40px 6%;text-align:center;">
      <div style="font-family:Sora,sans-serif;font-size:20px;font-weight:800;color:white;margin-bottom:6px;">Reh<span style="color:#42B8B1">app</span></div>
      <p style="font-size:13px;color:rgba(255,255,255,.4);margin:0;">© 2026 Rehapp · <a href="mailto:info@rehapp.com.tr" style="color:#42B8B1;text-decoration:none;">info@rehapp.com.tr</a></p>
    </div>""", unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN SAYFASI
# ══════════════════════════════════════════════════════════════════════════════
def login_sayfasi():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
    html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;}
    .stApp{background:linear-gradient(135deg,#F4F7FB 0%,#EBF4F3 100%)!important;min-height:100vh;}
    #MainMenu,footer,header{visibility:hidden!important;}
    [data-testid="stToolbar"]{display:none!important;}
    .block-container{max-width:460px!important;padding:0 1.5rem!important;margin:0 auto!important;}
    [data-baseweb="input"]>div{border-radius:12px!important;border:1.5px solid rgba(26,43,76,.12)!important;background:white!important;transition:all .2s!important;}
    [data-baseweb="input"]:focus-within>div{border-color:#42B8B1!important;box-shadow:0 0 0 3px rgba(66,184,177,.15)!important;}
    input{font-size:15px!important;color:#1A2B4C!important;-webkit-text-fill-color:#1A2B4C!important;}
    input:-webkit-autofill{-webkit-text-fill-color:#1A2B4C!important;-webkit-box-shadow:0 0 0px 1000px white inset!important;}
    label,[data-testid="stWidgetLabel"] p{color:#1A2B4C!important;}
    .stButton>button{font-family:'Sora',sans-serif!important;font-weight:600!important;font-size:15px!important;
      border-radius:12px!important;height:50px!important;border:none!important;}
    [data-testid="stFormSubmitButton"]>button{font-family:'Sora',sans-serif!important;font-weight:600!important;
      font-size:15px!important;border-radius:12px!important;height:50px!important;border:none!important;
      background:linear-gradient(135deg,#42B8B1,#2B52C4)!important;color:white!important;
      box-shadow:0 6px 18px rgba(66,184,177,.35)!important;width:100%!important;}
    [data-testid="stRadio"]>div{background:rgba(26,43,76,.05)!important;border-radius:12px!important;padding:4px!important;}
    [data-testid="stRadio"] label{border-radius:10px!important;font-family:'Sora',sans-serif!important;
      font-size:14px!important;font-weight:500!important;padding:8px 20px!important;flex:1!important;text-align:center!important;}
    [data-testid="stRadio"] label:has(input:checked){background:linear-gradient(135deg,#42B8B1,#2B52C4)!important;color:white!important;}
    [data-testid="stRadio"] [data-baseweb="radio"]>div:first-child{display:none!important;}
    [data-testid="stAlert"]{border-radius:12px!important;}
    </style>""", unsafe_allow_html=True)

    st.markdown("""
    <style>
    @keyframes rh-in{from{opacity:0;transform:scale(0) translateY(14px)}to{opacity:1;transform:scale(1) translateY(0)}}
    @keyframes rh-bounce{0%,100%{transform:translateY(0)}40%{transform:translateY(-14px)}65%{transform:translateY(-6px)}}
    .rh-d1{background:#2B52C4;animation:rh-in .35s cubic-bezier(.34,1.56,.64,1) .05s both,rh-bounce .7s ease-in-out .8s 3}
    .rh-d2{background:#42B8B1;animation:rh-in .35s cubic-bezier(.34,1.56,.64,1) .18s both,rh-bounce .7s ease-in-out .95s 3}
    .rh-d3{background:#F39237;animation:rh-in .35s cubic-bezier(.34,1.56,.64,1) .31s both,rh-bounce .7s ease-in-out 1.1s 3}
    </style>
    <div style="text-align:center;margin:40px 0 32px;">
      <div style="display:flex;gap:12px;justify-content:center;margin-bottom:10px;">
        <div class="rh-d1" style="width:16px;height:16px;border-radius:50%;"></div>
        <div class="rh-d2" style="width:16px;height:16px;border-radius:50%;"></div>
        <div class="rh-d3" style="width:16px;height:16px;border-radius:50%;"></div>
      </div>
      <div style="font-family:Sora,sans-serif;font-size:38px;font-weight:800;color:#1A2B4C;letter-spacing:-1.5px;">
        Reh<span style="color:#42B8B1">app</span>
      </div>
      <div style="font-size:13px;color:#6B7A99;margin-top:6px;">Akıllı Grup Planlama Platformu</div>
    </div>""", unsafe_allow_html=True)

    mod = st.radio("", ["Giriş Yap","Kayıt Ol"], horizontal=True, label_visibility="collapsed")
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    if mod == "Giriş Yap":
        with st.form("login_form"):
            email = st.text_input("📧 E-posta", placeholder="ornek@kurum.com")
            sifre = st.text_input("🔒 Şifre", type="password", placeholder="••••••••")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.form_submit_button("Giriş Yap →", use_container_width=True, type="primary"):
                if not email or not sifre:
                    st.error("E-posta ve şifre boş olamaz.")
                else:
                    data = api.login(email, sifre)
                    if data:
                        st.session_state["token"]       = data["access_token"]
                        st.session_state["kurum_id"]    = data["kurum_id"]
                        st.session_state["kurum_ad"]    = data["kurum_ad"]
                        st.session_state["kurum_email"] = email
                        st.session_state["show_login"]  = None
                        st.rerun()
    else:
        with st.form("register_form"):
            k_ad    = st.text_input("🏢 Kurum Adı", placeholder="Umut Özel Eğitim Merkezi")
            k_email = st.text_input("📧 E-posta",   placeholder="ornek@kurum.com")
            k_sifre = st.text_input("🔒 Şifre",     type="password", placeholder="En az 6 karakter")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.form_submit_button("Hesap Oluştur →", use_container_width=True, type="primary"):
                if not all([k_ad, k_email, k_sifre]):
                    st.error("Tüm alanları doldurun.")
                elif len(k_sifre) < 6:
                    st.error("Şifre en az 6 karakter olmalı.")
                else:
                    data = api.register(k_ad, k_email, k_sifre)
                    if data:
                        st.success("✅ Kaydınız alındı! Yönetici onayından sonra giriş yapabilirsiniz.")

    st.markdown("""<div style="text-align:center;margin-top:40px;font-size:12px;color:#aaa;">
        © 2026 Rehapp · <a href="https://rehapp.com.tr" style="color:#42B8B1;text-decoration:none">rehapp.com.tr</a>
    </div>""", unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# YÖNLENDİRME
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.get("token"):
    if st.session_state.get("show_login"):
        login_sayfasi()
    else:
        landing_sayfasi()

if not st.session_state.get("kurum_id"):
    for k in ("token","kurum_id","kurum_ad","kurum_email"):
        st.session_state[k] = None
    st.error("Oturum sona erdi. Lütfen tekrar giriş yapın.")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# ANA UYGULAMA — Global CSS (Mobil dahil)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;font-size:16px!important;}
p,li,label,.stMarkdown,.stText{font-size:15px!important;line-height:1.6!important;}
.stApp{background:#F4F7FB!important;}
.block-container{padding:.75rem 1.5rem 4rem!important;max-width:1100px!important;}
h1,h2,h3{font-family:'Sora',sans-serif!important;color:#1A2B4C!important;letter-spacing:-.5px!important;}
h1{font-size:1.8rem!important;font-weight:700!important;}
h2{font-size:1.4rem!important;}
h3{font-size:1.15rem!important;}

/* Sekmeler */
[data-baseweb="tab-list"]{background:white!important;border-radius:14px!important;padding:6px!important;
  border:1px solid rgba(26,43,76,.08)!important;box-shadow:0 2px 8px rgba(26,43,76,.05)!important;gap:4px!important;
  overflow-x:auto!important;-webkit-overflow-scrolling:touch!important;flex-wrap:nowrap!important;}
[data-baseweb="tab"]{border-radius:10px!important;font-family:'Sora',sans-serif!important;font-size:13px!important;
  font-weight:500!important;color:#1A2B4C!important;padding:8px 14px!important;transition:all .2s!important;
  white-space:nowrap!important;flex-shrink:0!important;}
[aria-selected="true"][data-baseweb="tab"]{background:linear-gradient(135deg,#42B8B1,#2B52C4)!important;
  color:white!important;font-weight:600!important;box-shadow:0 4px 12px rgba(66,184,177,.3)!important;}
[data-baseweb="tab-highlight"]{display:none!important;}
[data-baseweb="tab-border"]{display:none!important;}

/* Butonlar */
.stButton>button{font-family:'Sora',sans-serif!important;font-weight:600!important;
  border-radius:10px!important;transition:all .2s!important;border:none!important;min-height:42px!important;}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#42B8B1,#2B52C4)!important;
  color:white!important;box-shadow:0 4px 14px rgba(66,184,177,.3)!important;}
.stButton>button[kind="primary"]:hover{transform:translateY(-1px)!important;box-shadow:0 6px 20px rgba(66,184,177,.4)!important;}
.stButton>button[kind="secondary"]{background:white!important;color:#1A2B4C!important;
  border:1.5px solid rgba(26,43,76,.15)!important;}
[data-testid="stFormSubmitButton"]>button{font-family:'Sora',sans-serif!important;font-weight:600!important;
  border-radius:10px!important;border:none!important;background:linear-gradient(135deg,#42B8B1,#2B52C4)!important;color:white!important;}

/* Input */
[data-baseweb="input"],[data-baseweb="textarea"]{border-radius:10px!important;
  border-color:rgba(26,43,76,.12)!important;background:white!important;}
[data-baseweb="input"]:focus-within{border-color:#42B8B1!important;box-shadow:0 0 0 3px rgba(66,184,177,.12)!important;}
input{color:#1A2B4C!important;-webkit-text-fill-color:#1A2B4C!important;}

/* Select */
[data-baseweb="select"]{border-radius:10px!important;font-size:14px!important;}
[data-baseweb="select"]>div{border-color:rgba(26,43,76,.12)!important;background:white!important;border-radius:10px!important;}
[data-baseweb="single-value"],[data-baseweb="select"] [data-baseweb="single-value"]{color:#1A2B4C!important;}
[data-baseweb="tag"]{background:rgba(66,184,177,.12)!important;color:#1A2B4C!important;border-radius:6px!important;}

/* Expander */
[data-testid="stExpander"]{background:white!important;border-radius:14px!important;
  border:1px solid rgba(26,43,76,.07)!important;box-shadow:0 2px 8px rgba(26,43,76,.04)!important;
  overflow:hidden!important;margin-bottom:8px!important;}
[data-testid="stExpander"] summary{font-family:'Sora',sans-serif!important;font-weight:600!important;
  font-size:14px!important;color:#1A2B4C!important;padding:14px 18px!important;}

/* Alert */
[data-testid="stAlert"]{border-radius:12px!important;border:none!important;}
hr{border-color:rgba(26,43,76,.08)!important;margin:16px 0!important;}
.stCaption,[data-testid="stCaptionContainer"]{color:#6B7A99!important;font-size:12px!important;}
[data-testid="stSidebar"]{display:none!important;}
#MainMenu,footer,header{visibility:hidden!important;}
[data-testid="stToolbar"]{display:none!important;}

/* Dataframe */
[data-testid="stDataFrame"]{border-radius:12px!important;overflow:hidden!important;}

/* Mobil */
@media(max-width:768px){
  .block-container{padding:.75rem .75rem 4rem!important;}
  [data-baseweb="tab"]{font-size:11px!important;padding:6px 8px!important;}
  [data-baseweb="select"]{font-size:16px!important;min-height:48px!important;}
  button,input,select,textarea{touch-action:manipulation!important;-webkit-tap-highlight-color:transparent!important;}
  h1{font-size:1.4rem!important;}
  h2{font-size:1.2rem!important;}
}
@media(max-width:480px){
  [data-baseweb="tab"]{font-size:10px!important;padding:5px 6px!important;}
  .block-container{padding:.5rem .5rem 4rem!important;}
}
</style>
<script>
document.addEventListener('touchstart',function(e){
  const sel=e.target.closest('[data-baseweb="select"]');
  if(sel){const inp=sel.querySelector('input');if(inp){e.preventDefault();inp.focus();inp.click();}}
},{passive:false});
</script>""", unsafe_allow_html=True)

# ── Logo + Üst Bar ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@keyframes rh-in{from{opacity:0;transform:scale(0) translateY(10px)}to{opacity:1;transform:scale(1) translateY(0)}}
@keyframes rh-bounce{0%,100%{transform:translateY(0)}40%{transform:translateY(-10px)}65%{transform:translateY(-4px)}}
.rh-d1{background:#2B52C4;animation:rh-in .35s cubic-bezier(.34,1.56,.64,1) .05s both,rh-bounce .65s ease-in-out .8s 3}
.rh-d2{background:#42B8B1;animation:rh-in .35s cubic-bezier(.34,1.56,.64,1) .18s both,rh-bounce .65s ease-in-out .95s 3}
.rh-d3{background:#F39237;animation:rh-in .35s cubic-bezier(.34,1.56,.64,1) .31s both,rh-bounce .65s ease-in-out 1.1s 3}
</style>
<div style="padding:8px 0 4px;display:flex;align-items:center;">
  <div style="display:flex;flex-direction:column;align-items:center;">
    <div style="display:flex;gap:8px;align-items:center;margin-bottom:3px;">
      <div class="rh-d1" style="width:12px;height:12px;border-radius:50%;"></div>
      <div class="rh-d2" style="width:12px;height:12px;border-radius:50%;"></div>
      <div class="rh-d3" style="width:12px;height:12px;border-radius:50%;"></div>
    </div>
    <div style="font-family:Sora,sans-serif;font-size:26px;font-weight:800;line-height:1;letter-spacing:-1px;">
      <span style="color:#1A2B4C">Reh</span><span style="color:#42B8B1">app</span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

col_title, col_logout = st.columns([6, 1])
with col_title:
    st.markdown(
        f"<div style='font-family:DM Sans,sans-serif;font-size:14px;font-weight:500;"
        f"color:#6B7A99;margin-bottom:-4px;'>🏢 {st.session_state.get('kurum_ad','')}</div>",
        unsafe_allow_html=True)
with col_logout:
    if st.button("🚪 Çıkış", use_container_width=True):
        for k in list(st.session_state.keys()):
            st.session_state.pop(k, None)
        st.rerun()

st.divider()

# ── Sekmeler ──────────────────────────────────────────────────────────────────
from pages import yonetim, ogrenciler, grup_ara, kaydedilen_gruplar, admin

is_admin = st.session_state.get("kurum_email", "") == "necmettinakgun@gmail.com"

tab_labels = ["⭐ Gruplar", "👤 Öğrenci", "🔎 Grup Oluştur", "⚙️ Yönetim"]
if is_admin:
    tab_labels.append("🛡️ Admin")

tabs = st.tabs(tab_labels)

with tabs[0]:
    kaydedilen_gruplar.show()
with tabs[1]:
    ogrenciler.show()
with tabs[2]:
    grup_ara.show()
with tabs[3]:
    yonetim.show()
if is_admin and len(tabs) > 4:
    with tabs[4]:
        admin.show()
