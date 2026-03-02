"""
Lila XLS / XLSX import modülü.
Sadece GRUP eğitimi alan öğrenciler, sadece grup eğitimi verilebilen modüller.
Önizleme tablosunda ham kodlar gösterilmez.
"""
import re
import io
import zipfile
import xml.etree.ElementTree as ET
import unicodedata
from datetime import date, timedelta, datetime
import streamlit as st
import api_client as api

TANI_MODUL_MAP = {
    "Bedensel Yetersizliği Olan Bireyler İçin Destek Eğitim Programı": ["Günlük Yaşam Aktiviteleri"],
    "Dil ve Konuşma Bozukluğu Olan Bireyler İçin Destek Eğitim Programı": ["Dil"],
    "Görme Yetersizliği Olan Bireyler İçin Destek Eğitim Programı": [
        "Dil ve İletişim","Erken Matematik","Günlük Yaşam Becerileri",
        "Matematik","Okuma ve Yazma","Sosyal Beceriler","Toplumsal Yaşam Becerileri"],
    "İşitme Yetersizliği Olan Bireyler İçin Destek Eğitim Programı": [
        "Erken Matematik","Matematik","Okuma ve Yazma","Sosyal İletişim"],
    "Otizm Spektrum Bozukluğu Olan Bireyler İçin Destek Eğitim Programı": [
        "Birey ve Çevre","Dil, İletişim ve Oyun","Erken Matematik",
        "Günlük Yaşam Becerileri","Matematik","Okuma ve Yazma",
        "Sosyal Beceriler","Toplumsal Yaşam Becerileri"],
    "Öğrenme Güçlüğü Olan Bireyler İçin Destek Eğitim Programı": [
        "Dil ve İletişim","Erken Matematik","Matematik","Okuma ve Yazma","Sosyal Etkileşim"],
    "Zihinsel Yetersizliği Olan Bireyler İçin Destek Eğitim Programı": [
        "Birey ve Çevre","Dil, İletişim ve Oyun","Erken Matematik",
        "Günlük Yaşam Becerileri","Matematik","Okuma ve Yazma",
        "Sosyal Beceriler","Toplumsal Yaşam Becerileri"],
}

def normalize(s):
    return " ".join(unicodedata.normalize("NFC", s).split()).strip()

def modul_from_tani(taniler):
    moduller = set()
    for tani in taniler:
        tn = normalize(tani)
        for key, mods in TANI_MODUL_MAP.items():
            if normalize(key) == tn or normalize(key) in tn:
                moduller.update(mods)
    return sorted(moduller)

def excel_serial(s):
    try:
        n = int(float(s))
        return (date(1899,12,30) + timedelta(days=n)).isoformat() if n > 0 else None
    except:
        return None

def parse_xls(fb):
    content = fb.decode("utf-8", errors="ignore")
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', content, re.DOTALL|re.IGNORECASE)
    parsed = []
    for row in rows:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL|re.IGNORECASE)
        cells = [re.sub(r'<[^>]+>','',c).strip() for c in cells]
        parsed.append(cells)
    if len(parsed) < 3:
        return []
    headers = parsed[2]
    def col(n):
        try: return headers.index(n)
        except: return None
    idx_adi=col("ADI"); idx_soyadi=col("SOYADI"); idx_dob=col("DOĞUM TARİHİ")
    idx_program=col("EĞİTİM PROGRAMI"); idx_rapor=col("BİTİŞ TARİHİ")
    idx_sekil=col("EĞİTSEL TANI VE EĞİTİM ÖNERİSİ")
    students=[]; seen=set()
    for row in parsed[3:]:
        if not row: continue
        sekil = row[idx_sekil].upper() if idx_sekil is not None and len(row)>idx_sekil else ""
        if "GRUP" not in sekil: continue
        ad    = row[idx_adi].strip()    if idx_adi    is not None and len(row)>idx_adi    else ""
        soyad = row[idx_soyadi].strip() if idx_soyadi is not None and len(row)>idx_soyadi else ""
        tam_ad = f"{ad} {soyad}".strip()
        if not tam_ad or tam_ad in seen: continue
        seen.add(tam_ad)
        dob=None
        if idx_dob is not None and len(row)>idx_dob:
            try: dob=datetime.strptime(row[idx_dob].strip(),"%d.%m.%Y").date().isoformat()
            except: pass
        rapor=None
        if idx_rapor is not None and len(row)>idx_rapor:
            try: rapor=datetime.strptime(row[idx_rapor].strip(),"%d.%m.%Y").date().isoformat()
            except: pass
        prog_str = row[idx_program].strip() if idx_program is not None and len(row)>idx_program else ""
        taniler = list(dict.fromkeys(t.strip() for t in prog_str.split(",") if t.strip()))
        students.append({"name":tam_ad,"dob":dob,"rapor_bitis":rapor,
                         "taniler":taniler,"moduller":modul_from_tani(taniler)})
    return students

def parse_xlsx(fb):
    ns={"ns":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(io.BytesIO(fb)) as z:
        with z.open("xl/sharedStrings.xml") as f:
            ss=ET.parse(f)
        shared=["".join(t.text or "" for t in si.findall(".//ns:t",ns))
                for si in ss.findall(".//ns:si",ns)]
        with z.open("xl/worksheets/sheet1.xml") as f:
            sheet=ET.parse(f)
    def cval(c):
        v=c.find("ns:v",ns)
        if v is None: return ""
        return shared[int(v.text)] if c.get("t")=="s" else (v.text or "")
    rows=[]
    for r in sheet.findall(".//ns:row",ns):
        row={}
        for c in r.findall("ns:c",ns):
            col="".join(x for x in c.get("r","") if x.isalpha())
            row[col]=cval(c)
        rows.append(row)
    seen=set(); students=[]
    for row in rows[3:]:
        if "GRUP" not in row.get("BN","").upper(): continue
        tam_ad=f"{row.get('D','').strip()} {row.get('E','').strip()}".strip()
        if not tam_ad or tam_ad in seen: continue
        seen.add(tam_ad)
        tanilar=list(dict.fromkeys(t.strip() for t in row.get("BO","").split(",") if t.strip()))
        students.append({"name":tam_ad,"dob":excel_serial(row.get("J","")),"rapor_bitis":excel_serial(row.get("BK","")),
                         "taniler":tanilar,"moduller":modul_from_tani(tanilar)})
    return students

def show_import():
    with st.expander("📥 Lila'dan Öğrenci Listesi İçe Aktar", expanded=st.session_state.get("lila_ac",False)):
        st.caption("**.xls** veya **.xlsx** dosyasını yükleyin — sadece GRUP eğitimi alanlar, sadece grup modülleri aktarılır.")
        uploaded = st.file_uploader("", type=["xls","xlsx"], key="lila_upload", label_visibility="collapsed")
        if not uploaded:
            return
        with st.spinner("Okunuyor..."):
            try:
                fb = uploaded.read()
                students = parse_xlsx(fb) if uploaded.name.endswith(".xlsx") else parse_xls(fb)
                fmt = "XLSX" if uploaded.name.endswith(".xlsx") else "XLS"
            except Exception as e:
                st.error(f"Dosya okunamadı: {e}"); return
        if not students:
            st.warning("GRUP eğitimi alan öğrenci bulunamadı."); return

        # Önizleme — sadece temiz bilgiler
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,rgba(66,184,177,.12),rgba(43,82,196,.08));
             border-radius:12px;padding:14px 18px;margin:8px 0 16px;border:1px solid rgba(66,184,177,.25);'>
          <span style='font-family:Sora,sans-serif;font-weight:700;font-size:15px;color:#1A2B4C;'>
            📋 {len(students)} öğrenci bulundu
          </span>
          <span style='font-size:12px;color:#6B7A99;margin-left:12px;'>Format: {fmt}</span>
        </div>""", unsafe_allow_html=True)

        # Tablo — sadece ad, doğum, rapor, tanı kısaltması, modüller
        rows_html = ""
        for i,s in enumerate(students,1):
            tani_kisalt = " / ".join(
                t.replace("Olan Bireyler İçin Destek Eğitim Programı","").strip()
                for t in s["taniler"]
            ) or "–"
            mod_tags = "".join(
                f'<span style="display:inline-block;background:rgba(66,184,177,.15);color:#1A2B4C;'
                f'border-radius:4px;padding:1px 7px;margin:2px;font-size:11px;">{m}</span>'
                for m in s["moduller"]
            ) or "–"
            rows_html += f"""<tr>
              <td style='padding:8px 10px;color:#6B7A99;font-size:12px;'>{i}</td>
              <td style='padding:8px 10px;font-weight:600;color:#1A2B4C;'>{s['name']}</td>
              <td style='padding:8px 10px;color:#1A2B4C;font-size:13px;'>{s['dob'] or '–'}</td>
              <td style='padding:8px 10px;color:#1A2B4C;font-size:13px;'>{s['rapor_bitis'] or '–'}</td>
              <td style='padding:8px 10px;font-size:12px;color:#1A2B4C;'>{tani_kisalt}</td>
              <td style='padding:8px 10px;'>{mod_tags}</td>
            </tr>"""

        st.markdown(f"""
        <div style='overflow-x:auto;'>
        <table style='width:100%;border-collapse:collapse;font-family:DM Sans,sans-serif;font-size:13px;'>
          <thead><tr style='background:linear-gradient(135deg,#42B8B1,#2B52C4);'>
            <th style='padding:10px;color:white;font-family:Sora,sans-serif;text-align:left;'>#</th>
            <th style='padding:10px;color:white;font-family:Sora,sans-serif;text-align:left;'>Ad Soyad</th>
            <th style='padding:10px;color:white;font-family:Sora,sans-serif;text-align:left;'>Doğum</th>
            <th style='padding:10px;color:white;font-family:Sora,sans-serif;text-align:left;'>Rapor Bitiş</th>
            <th style='padding:10px;color:white;font-family:Sora,sans-serif;text-align:left;'>Tanı</th>
            <th style='padding:10px;color:white;font-family:Sora,sans-serif;text-align:left;'>Grup Modülleri</th>
          </tr></thead>
          <tbody style='background:white;'>{rows_html}</tbody>
        </table></div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        mevcut = {s["name"] for s in api.get_students()}
        yeni = len([s for s in students if s["name"] not in mevcut])
        guncelle = len([s for s in students if s["name"] in mevcut])

        col_info, col_btn = st.columns([3,1])
        with col_info:
            if yeni: st.markdown(f"🟢 **{yeni}** yeni öğrenci eklenecek")
            if guncelle: st.markdown(f"🔄 **{guncelle}** öğrenci güncellenecek")
        with col_btn:
            if st.button("🚀 İçe Aktar", type="primary", use_container_width=True, key="lila_btn"):
                _do_import(students, mevcut)

def _do_import(students, mevcut_names):
    mevcut_tanilar  = {d["name"]:d["id"] for d in api.get_diagnoses()}
    mevcut_moduller = {m["name"]:m["id"] for m in api.get_modules()}
    for t in set(t for s in students for t in s["taniler"]):
        if t not in mevcut_tanilar:
            r=api.create_diagnosis(t)
            if r: mevcut_tanilar[t]=r["id"]
    for m in set(m for s in students for m in s["moduller"]):
        if m not in mevcut_moduller:
            r=api.create_module(m)
            if r: mevcut_moduller[m]=r["id"]
    id_map = {s["name"]:s["id"] for s in api.get_students()}
    eklendi=guncellendi=hatali=0
    prog=st.progress(0)
    for i,s in enumerate(students):
        diag_ids=[mevcut_tanilar[t] for t in s["taniler"] if t in mevcut_tanilar]
        mod_ids=[mevcut_moduller[m] for m in s["moduller"] if m in mevcut_moduller]
        try:
            if s["name"] in mevcut_names:
                if s["name"] in id_map:
                    api.update_student(id_map[s["name"]],
                        {"rapor_bitis":s["rapor_bitis"],"diagnosis_ids":diag_ids,"module_ids":mod_ids})
                    guncellendi+=1
            else:
                r=api.create_student({"name":s["name"],"dob":s["dob"],"rapor_bitis":s["rapor_bitis"],
                                       "diagnosis_ids":diag_ids,"module_ids":mod_ids})
                if r: eklendi+=1
                else: hatali+=1
        except: hatali+=1
        prog.progress((i+1)/len(students))
    prog.empty()
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,rgba(66,184,177,.15),rgba(43,82,196,.1));
         border-radius:12px;padding:16px 20px;border:1px solid rgba(66,184,177,.3);'>
      <div style='font-family:Sora,sans-serif;font-weight:700;font-size:15px;color:#1A2B4C;margin-bottom:6px;'>
        ✅ İçe Aktarma Tamamlandı
      </div>
      <div style='font-size:14px;color:#1A2B4C;'>
        🟢 <b>{eklendi}</b> yeni &nbsp;·&nbsp; 🔄 <b>{guncellendi}</b> güncellendi &nbsp;·&nbsp; ❌ <b>{hatali}</b> hata
      </div>
    </div>""", unsafe_allow_html=True)
    st.session_state["lila_ac"]=False
    st.rerun()
