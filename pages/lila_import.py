"""
Lila XLS / XLSX import modülü.
Öğrenciler sekmesinin içinden çağrılır.
Sadece GRUP eğitimi alan öğrenciler ve sadece grup eğitimi verilebilen modüller alınır.
"""
import re
import io
import zipfile
import xml.etree.ElementTree as ET
import unicodedata
from datetime import date, timedelta, datetime
import streamlit as st
import api_client as api

# ── Tanı → Grup Modül Haritası (sadece grup eğitimi verilenler) ───────────────
TANI_MODUL_MAP = {
    "Bedensel Yetersizliği Olan Bireyler İçin Destek Eğitim Programı": [
        "Günlük Yaşam Aktiviteleri",
    ],
    "Dil ve Konuşma Bozukluğu Olan Bireyler İçin Destek Eğitim Programı": [
        "Dil",
    ],
    "Görme Yetersizliği Olan Bireyler İçin Destek Eğitim Programı": [
        "Dil ve İletişim", "Erken Matematik", "Günlük Yaşam Becerileri",
        "Matematik", "Okuma ve Yazma", "Sosyal Beceriler", "Toplumsal Yaşam Becerileri",
    ],
    "İşitme Yetersizliği Olan Bireyler İçin Destek Eğitim Programı": [
        "Erken Matematik", "Matematik", "Okuma ve Yazma", "Sosyal İletişim",
    ],
    "Otizm Spektrum Bozukluğu Olan Bireyler İçin Destek Eğitim Programı": [
        "Birey ve Çevre", "Dil, İletişim ve Oyun", "Erken Matematik",
        "Günlük Yaşam Becerileri", "Matematik", "Okuma ve Yazma",
        "Sosyal Beceriler", "Toplumsal Yaşam Becerileri",
    ],
    "Öğrenme Güçlüğü Olan Bireyler İçin Destek Eğitim Programı": [
        "Dil ve İletişim", "Erken Matematik", "Matematik", "Okuma ve Yazma", "Sosyal Etkileşim",
    ],
    "Zihinsel Yetersizliği Olan Bireyler İçin Destek Eğitim Programı": [
        "Birey ve Çevre", "Dil, İletişim ve Oyun", "Erken Matematik",
        "Günlük Yaşam Becerileri", "Matematik", "Okuma ve Yazma",
        "Sosyal Beceriler", "Toplumsal Yaşam Becerileri",
    ],
}


def normalize(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    return " ".join(s.split()).strip()


def modul_from_tani(taniler: list) -> list:
    moduller = set()
    for tani in taniler:
        tani_norm = normalize(tani)
        for key, mods in TANI_MODUL_MAP.items():
            if normalize(key) == tani_norm or normalize(key) in tani_norm:
                moduller.update(mods)
    return sorted(moduller)


def excel_serial_to_date(serial: str):
    try:
        n = int(float(serial))
        if n <= 0:
            return None
        return (date(1899, 12, 30) + timedelta(days=n)).isoformat()
    except Exception:
        return None


# ── XLS Parser (HTML tabanlı, eski projeden) ──────────────────────────────────
def parse_xls(file_bytes: bytes) -> list:
    content = file_bytes.decode("utf-8", errors="ignore")
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', content, re.DOTALL | re.IGNORECASE)

    parsed = []
    for row in rows:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL | re.IGNORECASE)
        cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
        parsed.append(cells)

    if len(parsed) < 3:
        return []

    headers = parsed[2]
    data_rows = parsed[3:]

    def col(name):
        try:
            return headers.index(name)
        except ValueError:
            return None

    idx_adi         = col("ADI")
    idx_soyadi      = col("SOYADI")
    idx_dob         = col("DOĞUM TARİHİ")
    idx_program     = col("EĞİTİM PROGRAMI")
    idx_rapor_bitis = col("BİTİŞ TARİHİ")
    idx_sekil       = col("EĞİTSEL TANI VE EĞİTİM ÖNERİSİ")

    students = []
    seen = set()

    for row in data_rows:
        if not row:
            continue
        sekil = row[idx_sekil].strip().upper() if idx_sekil is not None and len(row) > idx_sekil else ""
        if "GRUP" not in sekil:
            continue

        ad    = row[idx_adi].strip()    if idx_adi    is not None and len(row) > idx_adi    else ""
        soyad = row[idx_soyadi].strip() if idx_soyadi is not None and len(row) > idx_soyadi else ""
        tam_ad = f"{ad} {soyad}".strip()
        if not tam_ad or tam_ad in seen:
            continue
        seen.add(tam_ad)

        dob = None
        if idx_dob is not None and len(row) > idx_dob:
            try:
                dob = datetime.strptime(row[idx_dob].strip(), "%d.%m.%Y").date().isoformat()
            except Exception:
                pass

        rapor_bitis = None
        if idx_rapor_bitis is not None and len(row) > idx_rapor_bitis:
            try:
                rapor_bitis = datetime.strptime(row[idx_rapor_bitis].strip(), "%d.%m.%Y").date().isoformat()
            except Exception:
                pass

        prog_str = row[idx_program].strip() if idx_program is not None and len(row) > idx_program else ""
        taniler = list(dict.fromkeys(t.strip() for t in prog_str.split(",") if t.strip()))

        students.append({
            "name": tam_ad,
            "dob": dob,
            "rapor_bitis": rapor_bitis,
            "taniler": taniler,
            "moduller": modul_from_tani(taniler),
        })

    return students


# ── XLSX Parser ───────────────────────────────────────────────────────────────
def parse_xlsx(file_bytes: bytes) -> list:
    ns = {"ns": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

    with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
        with z.open("xl/sharedStrings.xml") as f:
            ss_tree = ET.parse(f)
        shared = []
        for si in ss_tree.findall(".//ns:si", ns):
            text = "".join(t.text or "" for t in si.findall(".//ns:t", ns))
            shared.append(text)

        with z.open("xl/worksheets/sheet1.xml") as f:
            sheet_tree = ET.parse(f)

    def cell_val(cell):
        t = cell.get("t", "")
        v_el = cell.find("ns:v", ns)
        if v_el is None:
            return ""
        val = v_el.text or ""
        if t == "s":
            return shared[int(val)]
        return val

    rows = []
    for row_el in sheet_tree.findall(".//ns:row", ns):
        row = {}
        for cell in row_el.findall("ns:c", ns):
            ref = cell.get("r", "")
            col = "".join(c for c in ref if c.isalpha())
            row[col] = cell_val(cell)
        rows.append(row)

    seen = set()
    students = []

    for row in rows[3:]:
        sekil = row.get("BN", "").strip().upper()
        if "GRUP" not in sekil:
            continue

        ad    = row.get("D", "").strip()
        soyad = row.get("E", "").strip()
        tam_ad = f"{ad} {soyad}".strip()
        if not tam_ad or tam_ad in seen:
            continue
        seen.add(tam_ad)

        dob   = excel_serial_to_date(row.get("J", ""))
        rapor = excel_serial_to_date(row.get("BK", ""))
        tani_raw = row.get("BO", "")
        taniler = list(dict.fromkeys(t.strip() for t in tani_raw.split(",") if t.strip()))

        students.append({
            "name": tam_ad,
            "dob": dob,
            "rapor_bitis": rapor,
            "taniler": taniler,
            "moduller": modul_from_tani(taniler),
        })

    return students


# ── Import UI ─────────────────────────────────────────────────────────────────
def show_import():
    """Öğrenciler sekmesinin içine gömülü Lila import bölümü."""

    with st.expander("📥 Lila'dan Öğrenci Listesi İçe Aktar", expanded=st.session_state.get("lila_ac", False)):
        st.caption("Lila'dan indirdiğiniz **.xls** veya **.xlsx** dosyasını yükleyin. Sadece GRUP eğitimi alan öğrenciler aktarılır.")

        uploaded = st.file_uploader("Dosya seç", type=["xls", "xlsx"], key="lila_upload", label_visibility="collapsed")

        if not uploaded:
            return

        with st.spinner("Dosya okunuyor..."):
            try:
                file_bytes = uploaded.read()
                if uploaded.name.endswith(".xlsx"):
                    students = parse_xlsx(file_bytes)
                    fmt = "XLSX"
                else:
                    students = parse_xls(file_bytes)
                    fmt = "XLS"
            except Exception as e:
                st.error(f"Dosya okunamadı: {e}")
                return

        if not students:
            st.warning("Dosyada BİREYSEL+GRUP öğrenci bulunamadı.")
            return

        # ── Önizleme Tablosu ──────────────────────────────────────────────────
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(66,184,177,0.1),rgba(43,82,196,0.08));
                    border-radius:12px;padding:16px 20px;margin-bottom:16px;
                    border:1px solid rgba(66,184,177,0.2);">
          <div style="font-family:Sora,sans-serif;font-weight:700;font-size:16px;color:#1A2B4C;">
            📋 {len(students)} öğrenci bulundu
          </div>
          <div style="font-size:13px;color:#6B7A99;margin-top:4px;">
            Format: {fmt} &nbsp;·&nbsp; Sadece GRUP eğitimi alanlar listeleniyor
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Tablo HTML
        tablo_html = """
        <style>
        .lila-tablo { width:100%; border-collapse:collapse; font-size:13px; font-family:'DM Sans',sans-serif; }
        .lila-tablo thead tr { background:linear-gradient(135deg,#42B8B1,#2B52C4); color:white; }
        .lila-tablo thead th { padding:10px 12px; text-align:left; font-family:Sora,sans-serif; font-weight:600; }
        .lila-tablo tbody tr { border-bottom:1px solid rgba(26,43,76,0.07); }
        .lila-tablo tbody tr:hover { background:rgba(66,184,177,0.06); }
        .lila-tablo tbody td { padding:9px 12px; color:#1A2B4C; vertical-align:top; }
        .lila-tablo .tag { display:inline-block; background:rgba(66,184,177,0.15); color:#1A2B4C;
                           border-radius:4px; padding:2px 8px; margin:2px; font-size:11px; }
        </style>
        <table class="lila-tablo">
          <thead><tr>
            <th>#</th><th>Ad Soyad</th><th>Doğum</th><th>Rapor Bitiş</th><th>Tanılar</th><th>Grup Modülleri</th>
          </tr></thead>
          <tbody>
        """

        for i, s in enumerate(students, 1):
            tanilar_html = "".join(f'<span class="tag">{t[:30]}{"…" if len(t)>30 else ""}</span>' for t in s["taniler"]) or "–"
            moduller_html = "".join(f'<span class="tag">{m}</span>' for m in s["moduller"]) or "–"
            tablo_html += f"""
            <tr>
              <td style="color:#6B7A99">{i}</td>
              <td><strong>{s['name']}</strong></td>
              <td>{s['dob'] or '–'}</td>
              <td>{s['rapor_bitis'] or '–'}</td>
              <td>{tanilar_html}</td>
              <td>{moduller_html}</td>
            </tr>"""

        tablo_html += "</tbody></table>"
        st.markdown(tablo_html, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # Mevcut öğrenciler
        mevcut_ogrenciler = {s["name"] for s in api.get_students()}
        yeni_sayisi = len([s for s in students if s["name"] not in mevcut_ogrenciler])
        guncelle_sayisi = len([s for s in students if s["name"] in mevcut_ogrenciler])

        col_bilgi, col_btn = st.columns([3, 1])
        with col_bilgi:
            if yeni_sayisi:
                st.markdown(f"🟢 **{yeni_sayisi}** yeni öğrenci eklenecek")
            if guncelle_sayisi:
                st.markdown(f"🔄 **{guncelle_sayisi}** mevcut öğrenci güncellenecek")

        with col_btn:
            if st.button("🚀 İçe Aktar", type="primary", use_container_width=True, key="lila_import_btn"):
                _do_import(students, mevcut_ogrenciler)


def _do_import(students, mevcut_ogrenciler):
    """Veritabanına kaydet."""
    # 1. Eksik tanı ve modülleri ekle
    mevcut_tanilar  = {d["name"]: d["id"] for d in api.get_diagnoses()}
    mevcut_moduller = {m["name"]: m["id"] for m in api.get_modules()}

    tum_tanilar  = set(t for s in students for t in s["taniler"])
    tum_moduller = set(m for s in students for m in s["moduller"])

    for t in tum_tanilar:
        if t not in mevcut_tanilar:
            r = api.create_diagnosis(t)
            if r:
                mevcut_tanilar[t] = r["id"]

    for m in tum_moduller:
        if m not in mevcut_moduller:
            r = api.create_module(m)
            if r:
                mevcut_moduller[m] = r["id"]

    # 2. Öğrencileri ekle / güncelle
    eklendi = guncellendi = hatali = 0
    progress = st.progress(0)

    tum_ogrenciler = api.get_students()
    ogrenci_id_map = {s["name"]: s["id"] for s in tum_ogrenciler}

    for i, s in enumerate(students):
        diag_ids = [mevcut_tanilar[t] for t in s["taniler"] if t in mevcut_tanilar]
        mod_ids  = [mevcut_moduller[m] for m in s["moduller"] if m in mevcut_moduller]

        try:
            if s["name"] in mevcut_ogrenciler:
                sid = ogrenci_id_map.get(s["name"])
                if sid:
                    api.update_student(sid, {
                        "rapor_bitis": s["rapor_bitis"],
                        "diagnosis_ids": diag_ids,
                        "module_ids": mod_ids,
                    })
                    guncellendi += 1
            else:
                result = api.create_student({
                    "name": s["name"],
                    "dob": s["dob"],
                    "rapor_bitis": s["rapor_bitis"],
                    "diagnosis_ids": diag_ids,
                    "module_ids": mod_ids,
                })
                if result:
                    eklendi += 1
                else:
                    hatali += 1
        except Exception:
            hatali += 1

        progress.progress((i + 1) / len(students))

    progress.empty()

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(66,184,177,0.15),rgba(43,82,196,0.1));
                border-radius:12px;padding:16px 20px;border:1px solid rgba(66,184,177,0.3);">
      <div style="font-family:Sora,sans-serif;font-weight:700;font-size:15px;color:#1A2B4C;margin-bottom:8px;">
        ✅ İçe Aktarma Tamamlandı
      </div>
      <div style="font-size:14px;color:#1A2B4C;">
        🟢 <strong>{eklendi}</strong> yeni öğrenci eklendi &nbsp;·&nbsp;
        🔄 <strong>{guncellendi}</strong> öğrenci güncellendi &nbsp;·&nbsp;
        ❌ <strong>{hatali}</strong> hata
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.session_state["lila_ac"] = False
    st.rerun()
