"""
Rehapp – Ana uygulama
Landing: tam HTML, hiç Streamlit widget yok → açılır sekme sorunu çözüldü.
Login: routing düzeltildi → boş sayfa sorunu çözüldü.
"""
import streamlit as st
import api_client as api

st.set_page_config(
    page_title="Rehapp",
    page_icon="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA2NCA2NCI+CiAgPHJlY3Qgd2lkdGg9IjY0IiBoZWlnaHQ9IjY0IiByeD0iMTYiIGZpbGw9IiMwRDFCMzUiLz4KICA8Y2lyY2xlIGN4PSIxNiIgY3k9IjMyIiByPSIxMCIgZmlsbD0iIzI3NTZENiIvPgogIDxjaXJjbGUgY3g9IjMyIiBjeT0iMzIiIHI9IjEwIiBmaWxsPSIjMzhDOUMwIi8+CiAgPGNpcmNsZSBjeD0iNDgiIGN5PSIzMiIgcj0iMTAiIGZpbGw9IiNGNTg4M0EiLz4KPC9zdmc+",
    layout="wide",
    initial_sidebar_state="collapsed",
)

for key in ("token","kurum_id","kurum_ad","kurum_email","page"):
    if key not in st.session_state:
        st.session_state[key] = None

# URL param ile sayfa geçişi (landing → login)
params = st.query_params
if params.get("p") == "login" and not st.session_state.get("token"):
    st.session_state["page"] = "login"
    st.query_params.clear()


# ══════════════════════════════════════════════════════════════════════════════
# LANDING PAGE — saf HTML, Streamlit widget YOK
# ══════════════════════════════════════════════════════════════════════════════
def landing_sayfasi():
    # Token varsa zaten giriş yapılmış — ana uygulamaya git
    if st.session_state.get("token") and st.session_state.get("kurum_id"):
        st.session_state["page"] = "app"
        st.rerun()
    st.markdown("""<!DOCTYPE html>
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap');
*{margin:0;padding:0;box-sizing:border-box;}
:root{
  --navy:#0D1B35;
  --teal:#38C9C0;
  --teal2:#2BA8A1;
  --blue:#2756D6;
  --orange:#F5883A;
  --mid:#6B7A99;
  --light:#F0F4FA;
}
body{font-family:'Plus Jakarta Sans',sans-serif;background:white;color:var(--navy);overflow-x:hidden;}

/* NAV */
nav{position:fixed;top:0;left:0;right:0;z-index:1000;padding:0 6%;
  display:flex;align-items:center;justify-content:space-between;height:64px;
  background:rgba(255,255,255,.85);backdrop-filter:blur(16px);
  border-bottom:1px solid rgba(13,27,53,.07);}
.nav-logo{font-family:Sora,sans-serif;font-size:22px;font-weight:800;letter-spacing:-.8px;color:var(--navy);}
.nav-logo span{color:var(--teal);}
.nav-dots{display:flex;gap:5px;align-items:center;margin-right:4px;}
.nav-dot{width:7px;height:7px;border-radius:50%;}
.nav-cta{background:linear-gradient(135deg,var(--teal),var(--blue));color:#ffffff !important;font-family:Sora,sans-serif;font-size:13px;font-weight:700;
  padding:10px 22px;border-radius:50px;text-decoration:none !important;border:none;cursor:pointer;
  transition:all .25s;display:inline-flex;align-items:center;gap:6px;letter-spacing:.2px;
  box-shadow:0 4px 14px rgba(56,201,192,.35);-webkit-text-fill-color:#ffffff !important;}
.nav-cta:hover{transform:translateY(-1px);box-shadow:0 8px 20px rgba(56,201,192,.5);color:#ffffff !important;}
.nav-cta:visited{color:#ffffff !important;}
.nav-cta svg{width:14px;height:14px;}

/* HERO */
.hero{min-height:100vh;display:flex;align-items:center;justify-content:center;
  padding:100px 6% 80px;position:relative;overflow:hidden;background:white;}
.hero-bg{position:absolute;inset:0;pointer-events:none;overflow:hidden;}
.hero-blob1{position:absolute;width:600px;height:600px;border-radius:50%;
  background:radial-gradient(circle,rgba(56,201,192,.12),transparent 70%);
  top:-150px;right:-100px;animation:blob-float 8s ease-in-out infinite;}
.hero-blob2{position:absolute;width:500px;height:500px;border-radius:50%;
  background:radial-gradient(circle,rgba(39,86,214,.08),transparent 70%);
  bottom:-100px;left:-80px;animation:blob-float 10s ease-in-out 2s infinite reverse;}
.hero-grid{position:absolute;inset:0;
  background-image:linear-gradient(rgba(13,27,53,.03) 1px,transparent 1px),
    linear-gradient(90deg,rgba(13,27,53,.03) 1px,transparent 1px);
  background-size:60px 60px;}
@keyframes blob-float{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(20px,-20px) scale(1.05)}}

.hero-inner{position:relative;z-index:1;max-width:780px;margin:0 auto;text-align:center;}
.hero-badge{display:inline-flex;align-items:center;gap:8px;background:rgba(56,201,192,.1);
  border:1px solid rgba(56,201,192,.3);color:var(--teal2);font-size:12px;font-weight:600;
  padding:6px 16px;border-radius:50px;margin-bottom:28px;letter-spacing:.3px;}
.hero-badge-dot{width:6px;height:6px;border-radius:50%;background:var(--teal);
  animation:pulse-dot 2s ease-in-out infinite;}
@keyframes pulse-dot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(1.3)}}
@keyframes dot-drop{from{opacity:0;transform:scale(0) translateY(10px)}to{opacity:1;transform:scale(1) translateY(0)}}
@keyframes dot-bounce{0%,100%{transform:translateY(0)}40%{transform:translateY(-12px)}65%{transform:translateY(-5px)}}
.d1{animation:dot-drop .35s cubic-bezier(.34,1.56,.64,1) .05s both, dot-bounce .7s ease-in-out 1s 3;}
.d2{animation:dot-drop .35s cubic-bezier(.34,1.56,.64,1) .18s both, dot-bounce .7s ease-in-out 1.15s 3;}
.d3{animation:dot-drop .35s cubic-bezier(.34,1.56,.64,1) .31s both, dot-bounce .7s ease-in-out 1.3s 3;}

.hero-title{font-family:Sora,sans-serif;font-size:clamp(36px,6vw,72px);font-weight:800;
  line-height:1.08;letter-spacing:-2.5px;color:var(--navy);margin-bottom:24px;}
.hero-title .accent{
  background:linear-gradient(135deg,var(--teal),var(--blue));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  position:relative;}
.hero-title .accent::after{content:'';position:absolute;bottom:-4px;left:0;right:0;height:3px;
  background:linear-gradient(90deg,var(--teal),var(--blue));border-radius:2px;opacity:.4;}
.hero-title .line2{display:block;font-size:.85em;font-weight:300;color:var(--mid);
  letter-spacing:-1px;margin-top:6px;}

.hero-sub{font-size:clamp(15px,2vw,18px);font-weight:400;color:var(--mid);
  line-height:1.75;max-width:540px;margin:0 auto 40px;}

.hero-cta-group{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;}
.btn-primary{background:linear-gradient(135deg,var(--teal),var(--blue));color:#ffffff !important;
  font-family:Sora,sans-serif;font-size:15px;font-weight:700;padding:14px 32px;
  border-radius:50px;border:none;cursor:pointer;text-decoration:none !important;
  display:inline-flex;align-items:center;gap:8px;-webkit-text-fill-color:#ffffff !important;
  box-shadow:0 8px 24px rgba(56,201,192,.35);transition:all .25s;letter-spacing:.2px;}
.btn-primary:visited{color:#ffffff !important;}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 12px 32px rgba(56,201,192,.45);}
.btn-primary svg{width:16px;height:16px;transition:transform .2s;}
.btn-primary:hover svg{transform:translateX(3px);}
.btn-secondary{background:transparent;color:var(--navy);font-family:Sora,sans-serif;
  font-size:15px;font-weight:600;padding:14px 28px;border-radius:50px;
  border:2px solid rgba(13,27,53,.2);cursor:pointer;text-decoration:none;
  transition:all .25s;display:inline-flex;align-items:center;gap:8px;}
.btn-secondary:hover{background:var(--navy);color:white;border-color:var(--navy);}

/* STATS */
.hero-stats{display:flex;gap:40px;justify-content:center;margin-top:56px;flex-wrap:wrap;}
.stat{text-align:center;}
.stat-n{font-family:Sora,sans-serif;font-size:28px;font-weight:800;color:var(--navy);letter-spacing:-1px;}
.stat-n span{color:var(--teal);}
.stat-l{font-size:12px;color:var(--mid);font-weight:500;margin-top:2px;letter-spacing:.3px;}

/* FEATURES */
.features{padding:100px 6%;background:var(--light);}
.section-label{font-size:11px;font-weight:700;color:var(--teal);letter-spacing:3px;
  text-transform:uppercase;margin-bottom:12px;}
.section-title{font-family:Sora,sans-serif;font-size:clamp(26px,3vw,42px);font-weight:800;
  color:var(--navy);letter-spacing:-1.5px;line-height:1.2;margin-bottom:16px;}
.section-sub{font-size:16px;color:var(--mid);max-width:480px;line-height:1.7;}
.features-layout{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:start;margin-top:64px;}
@media(max-width:768px){.features-layout{grid-template-columns:1fr;gap:32px;}}
.features-left{}
.feature-card{background:white;border-radius:20px;padding:28px;margin-bottom:16px;
  border:1px solid rgba(13,27,53,.07);
  box-shadow:0 2px 12px rgba(13,27,53,.04);transition:all .25s;cursor:default;}
.feature-card:hover{transform:translateY(-3px);box-shadow:0 8px 28px rgba(13,27,53,.1);
  border-color:rgba(56,201,192,.2);}
.feature-icon{width:44px;height:44px;border-radius:12px;display:flex;align-items:center;
  justify-content:center;font-size:20px;margin-bottom:14px;flex-shrink:0;}
.feature-icon.teal{background:rgba(56,201,192,.12);}
.feature-icon.blue{background:rgba(39,86,214,.1);}
.feature-icon.orange{background:rgba(245,136,58,.1);}
.feature-icon.navy{background:rgba(13,27,53,.08);}
.feature-name{font-family:Sora,sans-serif;font-weight:700;font-size:16px;color:var(--navy);margin-bottom:6px;}
.feature-desc{font-size:14px;color:var(--mid);line-height:1.6;}
.feature-row{display:flex;gap:16px;align-items:flex-start;}

.features-right{}
.big-card{background:var(--navy);border-radius:24px;padding:36px;color:white;
  position:sticky;top:80px;}
.big-card-title{font-family:Sora,sans-serif;font-weight:700;font-size:20px;margin-bottom:8px;}
.big-card-sub{font-size:14px;color:rgba(255,255,255,.5);margin-bottom:28px;line-height:1.6;}
.flow-step{display:flex;gap:14px;align-items:flex-start;margin-bottom:20px;}
.flow-num{min-width:30px;height:30px;border-radius:50%;
  background:linear-gradient(135deg,var(--teal),var(--blue));
  display:flex;align-items:center;justify-content:center;
  font-family:Sora,sans-serif;font-size:12px;font-weight:700;color:white;flex-shrink:0;}
.flow-text{font-size:14px;color:rgba(255,255,255,.75);line-height:1.5;padding-top:5px;}
.flow-text strong{color:white;}
.flow-line{width:1px;height:16px;background:rgba(255,255,255,.12);margin-left:15px;margin-bottom:4px;}

/* HOW */
.how{padding:100px 6%;background:white;}
.how-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:2px;
  background:rgba(13,27,53,.06);border-radius:20px;overflow:hidden;margin-top:56px;}
.how-item{background:white;padding:40px 32px;transition:background .2s;}
.how-item:hover{background:rgba(56,201,192,.04);}
.how-num{font-family:Sora,sans-serif;font-size:48px;font-weight:900;
  background:linear-gradient(135deg,var(--teal),var(--blue));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  letter-spacing:-2px;line-height:1;margin-bottom:12px;}
.how-title{font-family:Sora,sans-serif;font-weight:700;font-size:15px;color:var(--navy);margin-bottom:6px;}
.how-desc{font-size:13px;color:var(--mid);line-height:1.6;}

/* CTA BANNER */
.cta-banner{padding:100px 6%;background:var(--navy);text-align:center;position:relative;overflow:hidden;}
.cta-banner::before{content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse at 30% 50%,rgba(56,201,192,.15),transparent 60%),
    radial-gradient(ellipse at 70% 50%,rgba(39,86,214,.15),transparent 60%);}
.cta-title{font-family:Sora,sans-serif;font-size:clamp(28px,4vw,52px);font-weight:800;
  color:white;letter-spacing:-2px;line-height:1.15;margin-bottom:16px;position:relative;}
.cta-title span{color:var(--teal);}
.cta-sub{font-size:16px;color:rgba(255,255,255,.5);margin-bottom:36px;position:relative;}

/* FOOTER */
footer{background:#07101F;padding:40px 6%;
  display:flex;align-items:center;justify-content:space-between;flex-wrap:gap;gap:16px;}
.footer-logo{font-family:Sora,sans-serif;font-size:18px;font-weight:800;color:white;letter-spacing:-.6px;}
.footer-logo span{color:var(--teal);}
.footer-copy{font-size:12px;color:rgba(255,255,255,.3);}
.footer-link{color:var(--teal);text-decoration:none;}

/* ANIMATIONS */
@keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.fade-1{animation:fadeUp .7s ease .1s both;}
.fade-2{animation:fadeUp .7s ease .25s both;}
.fade-3{animation:fadeUp .7s ease .4s both;}
.fade-4{animation:fadeUp .7s ease .55s both;}
.fade-5{animation:fadeUp .7s ease .7s both;}

/* HIDE ALL STREAMLIT CHROME */
#MainMenu{display:none!important;visibility:hidden!important;}
header[data-testid="stHeader"]{display:none!important;visibility:hidden!important;}
[data-testid="stToolbar"]{display:none!important;}
[data-testid="stSidebar"]{display:none!important;}
footer{display:none!important;}
.stApp > header{display:none!important;}
button[kind="header"]{display:none!important;}
section[data-testid="stSidebar"]{display:none!important;}
div[data-testid="collapsedControl"]{display:none!important;}
.reportview-container .main .block-container{padding-top:0!important;}
</style>

<nav>
  <div style="display:flex;align-items:center;gap:0px;flex-direction:column;justify-content:center;">
    <div class="nav-dots" style="margin-bottom:2px;">
      <div class="nav-dot" style="background:#2756D6;"></div>
      <div class="nav-dot" style="background:#38C9C0;"></div>
      <div class="nav-dot" style="background:#F5883A;"></div>
    </div>
    <div class="nav-logo">Reh<span>app</span></div>
  </div>
  <a class="nav-cta" href="?p=login" target="_self">
    Giriş Yap / Kayıt Ol
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
      <path d="M5 12h14M12 5l7 7-7 7"/>
    </svg>
  </a>
</nav>

<section class="hero">
  <div class="hero-bg">
    <div class="hero-grid"></div>
    <div class="hero-blob1"></div>
    <div class="hero-blob2"></div>
  </div>
  <div class="hero-inner">
    <div class="hero-logo-mark fade-1" style="display:flex;flex-direction:column;align-items:center;margin-bottom:28px;">
      <div style="display:flex;gap:10px;justify-content:center;margin-bottom:8px;">
        <div class="logo-dot d1" style="width:14px;height:14px;border-radius:50%;background:#2756D6;"></div>
        <div class="logo-dot d2" style="width:14px;height:14px;border-radius:50%;background:#38C9C0;"></div>
        <div class="logo-dot d3" style="width:14px;height:14px;border-radius:50%;background:#F5883A;"></div>
      </div>
      <div style="font-family:Sora,sans-serif;font-size:clamp(28px,4vw,40px);font-weight:800;letter-spacing:-1.5px;line-height:1;">
        <span style="color:#0D1B35;">Reh</span><span style="color:#38C9C0;">app</span>
      </div>
    </div>
    <div class="hero-badge fade-2" style="margin-bottom:20px;">
      <div class="hero-badge-dot"></div>
      Özel Eğitim ve Rehabilitasyon Merkezleri İçin
    </div>
    <h1 class="hero-title fade-3">
      Grup planlamasını<br>
      <span class="accent">zekaya</span> bırak
      <span class="line2">Saniyeler içinde, sıfır hata.</span>
    </h1>
    <p class="hero-sub fade-4">
      Öğrenci tanıları, RAM raporları ve modüller — hepsi tek platformda. 
      Uyumlu grupları otomatik bul, zamanını öğrencilere ayır.
    </p>
    <div class="hero-cta-group fade-5">
      <a class="btn-primary" href="?p=login" target="_self">
        Ücretsiz Başla
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      </a>
      <button class="btn-secondary" onclick="document.getElementById('how').scrollIntoView({behavior:'smooth'})">
        Nasıl Çalışır?
      </button>
    </div>
    <div class="hero-stats" style="animation:fadeUp .7s ease .85s both">
      <div class="stat">
        <div class="stat-n">7<span>+</span></div>
        <div class="stat-l">Tanı Programı</div>
      </div>
      <div class="stat" style="border-left:1px solid rgba(13,27,53,.1);border-right:1px solid rgba(13,27,53,.1);padding:0 40px;">
        <div class="stat-n">3<span>sn</span></div>
        <div class="stat-l">Grup Eşleştirme</div>
      </div>
      <div class="stat">
        <div class="stat-n">100<span>%</span></div>
        <div class="stat-l">Mevzuata Uygun</div>
      </div>
    </div>
  </div>
</section>

<section class="features" id="features">
  <div style="text-align:center;max-width:600px;margin:0 auto;">
    <div class="section-label">Özellikler</div>
    <h2 class="section-title">Her şey düşünüldü,<br>siz sadece kullanın</h2>
    <p class="section-sub" style="margin:0 auto;">Manuel hesaplamalar, Excel karmaşası, yaş farkı hatalar — bunlar artık geçmişte kaldı.</p>
  </div>
  <div class="features-layout">
    <div class="features-left">
      <div class="feature-card">
        <div class="feature-row">
          <div class="feature-icon teal">🧩</div>
          <div>
            <div class="feature-name">Akıllı Grup Eşleştirme</div>
            <div class="feature-desc">Tanı, modül ve yaş uyumunu aynı anda kontrol eder. Uyumsuz kombinasyonları otomatik engeller.</div>
          </div>
        </div>
      </div>
      <div class="feature-card">
        <div class="feature-row">
          <div class="feature-icon blue">📥</div>
          <div>
            <div class="feature-name">Lila Entegrasyonu</div>
            <div class="feature-desc">Lila'dan indirdiğiniz XLS dosyasını yükleyin. Öğrenci bilgileri, tanılar ve modüller otomatik aktarılır.</div>
          </div>
        </div>
      </div>
      <div class="feature-card">
        <div class="feature-row">
          <div class="feature-icon orange">📋</div>
          <div>
            <div class="feature-name">RAM Rapor Takibi</div>
            <div class="feature-desc">Bitiş tarihi yaklaşan raporları renkli uyarılarla öne çıkarır. Sürpriz bitmeler tarih oldu.</div>
          </div>
        </div>
      </div>
      <div class="feature-card">
        <div class="feature-row">
          <div class="feature-icon navy">📱</div>
          <div>
            <div class="feature-name">Mobil & Tablet Uyumlu</div>
            <div class="feature-desc">Sahada telefon, masada bilgisayar. Her cihazda aynı deneyim.</div>
          </div>
        </div>
      </div>
    </div>
    <div class="features-right">
      <div class="big-card">
        <div class="big-card-title">Grup nasıl oluşturulur?</div>
        <div class="big-card-sub">Üç adımda, sıfır hesap hatasıyla.</div>
        <div class="flow-step">
          <div class="flow-num">1</div>
          <div class="flow-text"><strong>Ana öğrenciyi seç</strong><br>Tanısı ve modülleri referans alınır.</div>
        </div>
        <div class="flow-line"></div>
        <div class="flow-step">
          <div class="flow-num">2</div>
          <div class="flow-text"><strong>Uyumlu öğrenciler listelenir</strong><br>Ortak tanı → ortak modül → max 3 yaş farkı kontrolü otomatik yapılır.</div>
        </div>
        <div class="flow-line"></div>
        <div class="flow-step">
          <div class="flow-num">3</div>
          <div class="flow-text"><strong>Grubu kaydet</strong><br>Liste adı ver, not ekle, Excel'e aktar.</div>
        </div>
        <div style="margin-top:28px;padding-top:24px;border-top:1px solid rgba(255,255,255,.1);">
          <div style="font-size:12px;color:rgba(255,255,255,.35);margin-bottom:12px;">Desteklenen tanılar</div>
          <div style="display:flex;flex-wrap:wrap;gap:6px;">
            <span style="background:rgba(56,201,192,.15);color:rgba(255,255,255,.7);border-radius:20px;padding:3px 10px;font-size:11px;">Otizm Spektrum</span>
            <span style="background:rgba(56,201,192,.15);color:rgba(255,255,255,.7);border-radius:20px;padding:3px 10px;font-size:11px;">Zihinsel Yetersizlik</span>
            <span style="background:rgba(56,201,192,.15);color:rgba(255,255,255,.7);border-radius:20px;padding:3px 10px;font-size:11px;">Öğrenme Güçlüğü</span>
            <span style="background:rgba(56,201,192,.15);color:rgba(255,255,255,.7);border-radius:20px;padding:3px 10px;font-size:11px;">İşitme Yetersizliği</span>
            <span style="background:rgba(56,201,192,.15);color:rgba(255,255,255,.7);border-radius:20px;padding:3px 10px;font-size:11px;">Görme Yetersizliği</span>
            <span style="background:rgba(56,201,192,.15);color:rgba(255,255,255,.7);border-radius:20px;padding:3px 10px;font-size:11px;">Dil ve Konuşma</span>
            <span style="background:rgba(56,201,192,.15);color:rgba(255,255,255,.7);border-radius:20px;padding:3px 10px;font-size:11px;">Bedensel Yetersizlik</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="how" id="how">
  <div style="text-align:center;max-width:560px;margin:0 auto;">
    <div class="section-label">Nasıl Çalışır</div>
    <h2 class="section-title">Kurulumdan kullanıma<br>5 dakika</h2>
  </div>
  <div class="how-grid">
    <div class="how-item">
      <div class="how-num">01</div>
      <div class="how-title">Hesap oluştur</div>
      <div class="how-desc">Kurum bilgilerinizle kaydolun, onaydan sonra hemen erişin.</div>
    </div>
    <div class="how-item">
      <div class="how-num">02</div>
      <div class="how-title">Lila'dan import</div>
      <div class="how-desc">Öğrenci listenizi tek dosyayla yükleyin, sistem geri kalanını halleder.</div>
    </div>
    <div class="how-item">
      <div class="how-num">03</div>
      <div class="how-title">Grubu oluştur</div>
      <div class="how-desc">Öğrenci seç, uyumlular listelenir, kaydet. Bitti.</div>
    </div>
    <div class="how-item">
      <div class="how-num">04</div>
      <div class="how-title">Excel'e aktar</div>
      <div class="how-desc">Kaydedilen grupları tek tıkla Excel dosyasına dönüştürün.</div>
    </div>
  </div>
</section>

<section class="cta-banner">
  <h2 class="cta-title">Hazır mısınız?<br>
    <span>Hemen başlayın.</span>
  </h2>
  <p class="cta-sub">Kurumunuzu sisteme ekleyin, onaydan sonra tüm özelliklere erişin.</p>
  <a class="btn-primary" href="?p=login" target="_self" style="font-size:16px;padding:16px 40px;display:inline-flex;">
    Ücretsiz Kaydol
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18">
      <path d="M5 12h14M12 5l7 7-7 7"/>
    </svg>
  </a>
</section>

<footer>
  <div class="footer-logo">Reh<span>app</span></div>
  <div class="footer-copy">
    © 2026 Rehapp &nbsp;·&nbsp; 
    <a href="mailto:info@rehapp.com.tr" class="footer-link">info@rehapp.com.tr</a>
  </div>
</footer>
""", unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN / KAYIT SAYFASI
# ══════════════════════════════════════════════════════════════════════════════
def login_sayfasi():
    # Token varsa zaten giriş yapılmış — ana uygulamaya git
    if st.session_state.get("token") and st.session_state.get("kurum_id"):
        st.session_state["page"] = "app"
        st.rerun()
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500&display=swap');
    html,body,[class*="css"]{font-family:'Plus Jakarta Sans',sans-serif!important;}
    .stApp{background:linear-gradient(145deg,#EBF2FF 0%,#E8F6F5 50%,#F0F4FA 100%)!important;min-height:100vh;}
    #MainMenu,footer,header{visibility:hidden!important;display:none!important;}
    [data-testid="stToolbar"]{display:none!important;}
    [data-testid="stSidebar"]{display:none!important;}
    [data-testid="stHeader"]{display:none!important;}
    div[data-testid="collapsedControl"]{display:none!important;}
    button[kind="header"]{display:none!important;}
    .block-container{max-width:420px!important;padding:0 1.25rem!important;margin:0 auto!important;}

    [data-baseweb="input"]>div{border-radius:12px!important;border:1.5px solid rgba(13,27,53,.12)!important;
      background:white!important;transition:all .2s!important;}
    [data-baseweb="input"]:focus-within>div{border-color:#38C9C0!important;
      box-shadow:0 0 0 3px rgba(56,201,192,.15)!important;}
    input{font-size:15px!important;color:#0D1B35!important;-webkit-text-fill-color:#0D1B35!important;}
    input:-webkit-autofill{-webkit-text-fill-color:#0D1B35!important;
      -webkit-box-shadow:0 0 0px 1000px white inset!important;}
    label,[data-testid="stWidgetLabel"] p{color:#0D1B35!important;font-size:14px!important;font-weight:500!important;}

    .stButton>button{font-family:'Sora',sans-serif!important;font-weight:600!important;font-size:15px!important;
      border-radius:12px!important;height:50px!important;border:none!important;transition:all .2s!important;}
    [data-testid="stFormSubmitButton"]>button{font-family:'Sora',sans-serif!important;font-weight:600!important;
      font-size:15px!important;border-radius:12px!important;height:50px!important;border:none!important;
      background:linear-gradient(135deg,#38C9C0,#2756D6)!important;color:white!important;
      box-shadow:0 8px 20px rgba(56,201,192,.35)!important;width:100%!important;transition:all .2s!important;}
    [data-testid="stFormSubmitButton"]>button:hover{transform:translateY(-1px)!important;
      box-shadow:0 12px 28px rgba(56,201,192,.45)!important;}

    [data-testid="stRadio"]>div{background:rgba(13,27,53,.06)!important;border-radius:12px!important;padding:4px!important;}
    [data-testid="stRadio"] label{border-radius:10px!important;font-family:'Sora',sans-serif!important;
      font-size:14px!important;font-weight:600!important;padding:9px 20px!important;
      flex:1!important;text-align:center!important;transition:all .2s!important;}
    [data-testid="stRadio"] label:has(input:checked){
      background:linear-gradient(135deg,#38C9C0,#2756D6)!important;color:white!important;
      box-shadow:0 4px 12px rgba(56,201,192,.3)!important;}
    [data-testid="stRadio"] [data-baseweb="radio"]>div:first-child{display:none!important;}
    [data-testid="stAlert"]{border-radius:12px!important;}
    </style>""", unsafe_allow_html=True)

    st.markdown("""
    <style>
    @keyframes drop-in{from{opacity:0;transform:translateY(-20px) scale(.95)}to{opacity:1;transform:none}}
    @keyframes rh-in{from{opacity:0;transform:scale(0) translateY(10px)}to{opacity:1;transform:scale(1) translateY(0)}}
    @keyframes rh-bounce{0%,100%{transform:translateY(0)}40%{transform:translateY(-14px)}65%{transform:translateY(-6px)}}
    .login-card{animation:drop-in .5s cubic-bezier(.34,1.3,.64,1) both;}
    .ld1{background:#2756D6;animation:rh-in .35s cubic-bezier(.34,1.56,.64,1) .05s both, rh-bounce .7s ease-in-out .8s 3;}
    .ld2{background:#38C9C0;animation:rh-in .35s cubic-bezier(.34,1.56,.64,1) .18s both, rh-bounce .7s ease-in-out .95s 3;}
    .ld3{background:#F5883A;animation:rh-in .35s cubic-bezier(.34,1.56,.64,1) .31s both, rh-bounce .7s ease-in-out 1.1s 3;}
    </style>
    <div class="login-card" style="text-align:center;padding:48px 0 32px;">
      <div style="display:flex;gap:10px;justify-content:center;margin-bottom:10px;">
        <div class="ld1" style="width:16px;height:16px;border-radius:50%;"></div>
        <div class="ld2" style="width:16px;height:16px;border-radius:50%;"></div>
        <div class="ld3" style="width:16px;height:16px;border-radius:50%;"></div>
      </div>
      <div style="font-family:Sora,sans-serif;font-size:40px;font-weight:800;color:#0D1B35;letter-spacing:-1.5px;">
        Reh<span style="color:#38C9C0;">app</span>
      </div>
      <div style="font-size:13px;color:#6B7A99;margin-top:6px;font-weight:400;">
        Özel Eğitim Grup Planlama Platformu
      </div>
    </div>""", unsafe_allow_html=True)

    # Geri butonu
    if st.button("← Ana Sayfa", key="back_btn"):
        st.session_state["page"] = None
        st.rerun()

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    mod = st.radio("", ["Giriş Yap", "Kayıt Ol"], horizontal=True, label_visibility="collapsed")
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    if mod == "Giriş Yap":
        if st.session_state.get("login_loading"):
            st.markdown("""
            <style>
            @keyframes lb-bounce{0%,100%{transform:translateY(0)}40%{transform:translateY(-18px)}65%{transform:translateY(-8px)}}
            .login-overlay{
              position:fixed;top:0;left:0;right:0;bottom:0;
              background:linear-gradient(145deg,#EBF2FF 0%,#E8F6F5 50%,#F0F4FA 100%);
              display:flex;flex-direction:column;align-items:center;justify-content:center;
              z-index:9999;}
            .login-balls{display:flex;gap:14px;margin-bottom:20px;}
            .lb1{width:18px;height:18px;border-radius:50%;background:#2756D6;animation:lb-bounce .65s ease-in-out infinite;}
            .lb2{width:18px;height:18px;border-radius:50%;background:#38C9C0;animation:lb-bounce .65s ease-in-out .15s infinite;}
            .lb3{width:18px;height:18px;border-radius:50%;background:#F5883A;animation:lb-bounce .65s ease-in-out .3s infinite;}
            .login-loading-text{font-family:Sora,sans-serif;font-size:13px;color:#6B7A99;}
            </style>
            <div class="login-overlay">
              <div class="login-balls">
                <div class="lb1"></div><div class="lb2"></div><div class="lb3"></div>
              </div>
              <div class="login-loading-text">Giriş yapılıyor...</div>
            </div>""", unsafe_allow_html=True)
            import time; time.sleep(0.4)
            data = api.login(st.session_state.get("_login_email",""), st.session_state.get("_login_sifre",""))
            st.session_state["login_loading"] = False
            if data and data.get("access_token"):
                st.session_state["token"]       = data["access_token"]
                st.session_state["kurum_id"]    = data.get("kurum_id")
                st.session_state["kurum_ad"]    = data.get("kurum_ad", "")
                st.session_state["kurum_email"] = st.session_state.get("_login_email", "")
                st.session_state["page"]        = "app"
                st.rerun()
        else:
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("E-posta", placeholder="ornek@kurum.com")
                sifre = st.text_input("Şifre", type="password", placeholder="••••••••")
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                submitted = st.form_submit_button("Giriş Yap →", use_container_width=True, type="primary")
            if submitted:
                if not email.strip() or not sifre:
                    st.error("E-posta ve şifre boş olamaz.")
                else:
                    st.session_state["login_loading"] = True
                    st.session_state["_login_email"] = email.strip()
                    st.session_state["_login_sifre"] = sifre
                    st.rerun()
    else:
        with st.form("register_form", clear_on_submit=True):
            k_ad    = st.text_input("Kurum Adı", placeholder="Umut Özel Eğitim Merkezi")
            k_email = st.text_input("E-posta",   placeholder="ornek@kurum.com")
            k_sifre = st.text_input("Şifre",     type="password", placeholder="En az 6 karakter")
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Hesap Oluştur →", use_container_width=True, type="primary")

        if submitted:
            if not all([k_ad.strip(), k_email.strip(), k_sifre]):
                st.error("Tüm alanları doldurun.")
            elif len(k_sifre) < 6:
                st.error("Şifre en az 6 karakter olmalı.")
            else:
                with st.spinner("Kaydediliyor..."):
                    data = api.register(k_ad.strip(), k_email.strip(), k_sifre)
                if data:
                    st.success("✅ Kaydınız alındı! Yönetici onayından sonra giriş yapabilirsiniz.")

    st.markdown("""
    <div style="text-align:center;margin-top:32px;font-size:12px;color:#aaa;">
      © 2026 Rehapp · 
      <a href="?p=" style="color:#38C9C0;text-decoration:none">rehapp.com.tr</a>
    </div>""", unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# ROUTING — ana uygulama sadece token + kurum_id varsa çalışır
# ══════════════════════════════════════════════════════════════════════════════
current_page = st.session_state.get("page")

_token    = st.session_state.get("token")
_kurum_id = st.session_state.get("kurum_id")

if not _token or not _kurum_id:
    # Oturum bozuksa temizle
    if _token and not _kurum_id:
        st.session_state.clear()
        st.query_params.clear()
    # Login veya landing göster, sonra HARD STOP
    if current_page == "login":
        login_sayfasi()
    else:
        landing_sayfasi()
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# ANA UYGULAMA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500&display=swap');
html,body,[class*="css"]{font-family:'Plus Jakarta Sans',sans-serif!important;font-size:15px!important;}
.stApp{background:#F0F4FA!important;}
.block-container{padding:.25rem 1.5rem 4rem!important;max-width:1100px!important;}
h1,h2,h3{font-family:'Sora',sans-serif!important;color:#0D1B35!important;letter-spacing:-.5px!important;}
h1{font-size:1.7rem!important;font-weight:700!important;}
h2{font-size:1.3rem!important;}
h3{font-size:1.1rem!important;}
#MainMenu,footer,header{visibility:hidden!important;display:none!important;}
[data-testid="stToolbar"]{display:none!important;}
[data-testid="stSidebar"]{display:none!important;}
[data-testid="stHeader"]{display:none!important;}
div[data-testid="collapsedControl"]{display:none!important;}
button[kind="header"]{display:none!important;}

[data-baseweb="tab-list"]{background:white!important;border-radius:14px!important;padding:5px!important;
  border:1px solid rgba(13,27,53,.08)!important;box-shadow:0 2px 8px rgba(13,27,53,.05)!important;
  gap:3px!important;overflow-x:auto!important;flex-wrap:nowrap!important;}
[data-baseweb="tab"]{border-radius:10px!important;font-family:'Sora',sans-serif!important;
  font-size:13px!important;font-weight:500!important;color:#6B7A99!important;
  padding:8px 14px!important;transition:all .2s!important;white-space:nowrap!important;flex-shrink:0!important;}
[aria-selected="true"][data-baseweb="tab"]{background:linear-gradient(135deg,#38C9C0,#2756D6)!important;
  color:white!important;font-weight:600!important;box-shadow:0 4px 12px rgba(56,201,192,.3)!important;}
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"]{display:none!important;}

.stButton>button{font-family:'Sora',sans-serif!important;font-weight:600!important;
  border-radius:10px!important;transition:all .2s!important;border:none!important;min-height:42px!important;}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#38C9C0,#2756D6)!important;
  color:white!important;box-shadow:0 4px 14px rgba(56,201,192,.3)!important;}
.stButton>button[kind="primary"]:hover{transform:translateY(-1px)!important;}
.stButton>button[kind="secondary"]{background:white!important;color:#0D1B35!important;
  border:1.5px solid rgba(13,27,53,.12)!important;}
[data-testid="stFormSubmitButton"]>button{font-family:'Sora',sans-serif!important;font-weight:600!important;
  border-radius:10px!important;border:none!important;
  background:linear-gradient(135deg,#38C9C0,#2756D6)!important;color:white!important;}

[data-baseweb="input"]>div,[data-baseweb="textarea"]>div{border-radius:10px!important;
  border-color:rgba(13,27,53,.12)!important;background:white!important;}
[data-baseweb="input"]:focus-within>div{border-color:#38C9C0!important;
  box-shadow:0 0 0 3px rgba(56,201,192,.12)!important;}
input{color:#0D1B35!important;-webkit-text-fill-color:#0D1B35!important;}

[data-baseweb="select"]>div{border-color:rgba(13,27,53,.12)!important;background:white!important;border-radius:10px!important;}
[data-baseweb="tag"]{background:rgba(56,201,192,.12)!important;color:#0D1B35!important;border-radius:6px!important;}

[data-testid="stExpander"]{background:white!important;border-radius:14px!important;
  border:1px solid rgba(13,27,53,.07)!important;box-shadow:0 2px 8px rgba(13,27,53,.04)!important;
  overflow:hidden!important;margin-bottom:8px!important;}
[data-testid="stExpander"] summary{font-family:'Sora',sans-serif!important;font-weight:600!important;
  font-size:14px!important;color:#0D1B35!important;padding:14px 18px!important;}
[data-testid="stAlert"]{border-radius:12px!important;border:none!important;}
hr{border-color:rgba(13,27,53,.08)!important;margin:16px 0!important;}
.stCaption{color:#6B7A99!important;font-size:12px!important;}

@media(max-width:768px){
  .block-container{padding:.5rem .75rem 4rem!important;}
  [data-baseweb="tab"]{font-size:11px!important;padding:6px 8px!important;}
  h1{font-size:1.35rem!important;}
}
@media(max-width:480px){
  [data-baseweb="tab"]{font-size:10px!important;padding:5px 6px!important;}
  .block-container{padding:.4rem .5rem 4rem!important;}
}
</style>""", unsafe_allow_html=True)

# ── Topbar ────────────────────────────────────────────────────────────────────
st.markdown('''
<style>
@keyframes rh-in{from{opacity:0;transform:scale(0) translateY(10px)}to{opacity:1;transform:scale(1) translateY(0)}}
@keyframes rh-bounce{0%,100%{transform:translateY(0)}40%{transform:translateY(-10px)}65%{transform:translateY(-4px)}}
.rh-d1{background:#2756D6;animation:rh-in .35s cubic-bezier(.34,1.56,.64,1) .05s both,rh-bounce .65s ease-in-out .8s 3}
.rh-d2{background:#38C9C0;animation:rh-in .35s cubic-bezier(.34,1.56,.64,1) .18s both,rh-bounce .65s ease-in-out .95s 3}
.rh-d3{background:#F5883A;animation:rh-in .35s cubic-bezier(.34,1.56,.64,1) .31s both,rh-bounce .65s ease-in-out 1.1s 3}
</style>
<div style="padding:8px 0 0 0;display:flex;align-items:center;justify-content:flex-start;">
  <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;">
    <div style="display:flex;gap:10px;align-items:center;justify-content:center;margin-bottom:4px;">
      <div class="rh-d1" style="width:14px;height:14px;border-radius:50%;"></div>
      <div class="rh-d2" style="width:14px;height:14px;border-radius:50%;"></div>
      <div class="rh-d3" style="width:14px;height:14px;border-radius:50%;"></div>
    </div>
    <div style="font-family:Sora,sans-serif;font-size:32px;font-weight:800;line-height:1;letter-spacing:-1px;">
      <span style="color:#1A2B4C">Reh</span><span style="color:#38C9C0">app</span>
    </div>
  </div>
</div>
''', unsafe_allow_html=True)

col_title, col_logout = st.columns([6, 1])
with col_logout:
    if st.button("🚪 Çıkış", use_container_width=True):
        st.session_state.clear()
        st.rerun()
with col_title:
    st.markdown(
        f"<div style='font-family:DM Sans,sans-serif;font-size:16px;font-weight:500;"
        f"color:#1A2B4C;margin-bottom:-6px;'>🏢 {st.session_state.get('kurum_ad','')}</div>",
        unsafe_allow_html=True,
    )

# ── Sekmeler ──────────────────────────────────────────────────────────────────
from pages import yonetim, ogrenciler, grup_ara, kaydedilen_gruplar, admin

is_admin = st.session_state.get("kurum_email", "") == "necmettinakgun@gmail.com"
tab_labels = ["⚙️ Yönetim", "👤 Öğrenci", "🔎 Grup Oluştur", "⭐ Gruplar"]
if is_admin:
    tab_labels.append("🛡️ Admin")

tabs = st.tabs(tab_labels)
with tabs[0]: yonetim.show()
with tabs[1]: ogrenciler.show()
with tabs[2]: grup_ara.show()
with tabs[3]: kaydedilen_gruplar.show()
if is_admin and len(tabs) > 4:
    with tabs[4]: admin.show()
