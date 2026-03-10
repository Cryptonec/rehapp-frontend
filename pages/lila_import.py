"""
Lila import — sadece GRUP eğitimi, sadece TANI_MODUL_MAP'teki modüller.
"""
import re, io, zipfile, unicodedata, xml.etree.ElementTree as ET
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

GECERLI_MODULLER = {m for v in TANI_MODUL_MAP.values() for m in v}
MODUL_LISTESI = sorted(GECERLI_MODULLER, key=len, reverse=True)


def norm(s):
    return " ".join(unicodedata.normalize("NFC", s).split()).strip()

def tani_bul(tani_str):
    tn = norm(tani_str)
    for key in TANI_MODUL_MAP:
        if norm(key) == tn or norm(key) in tn or tn in norm(key):
            return key
    return None

def modul_bul_greedy(modul_str):
    kalan = norm(modul_str)
    bulunanlar = []
    while kalan:
        eslesti = False
        for bm in MODUL_LISTESI:
            if kalan.startswith(norm(bm)):
                bulunanlar.append(bm)
                kalan = kalan[len(norm(bm)):].lstrip(",").strip()
                eslesti = True
                break
        if not eslesti:
            idx = kalan.find(",")
            if idx == -1: break
            kalan = kalan[idx+1:].strip()
    return list(dict.fromkeys(bulunanlar))

def excel_serial(s):
    try:
        n = int(float(s))
        return (date(1899,12,30) + timedelta(days=n)).isoformat() if n > 0 else None
    except: return None

def parse_xls(fb):
    content = fb.decode("utf-8", errors="ignore")
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', content, re.DOTALL|re.IGNORECASE)
    parsed = []
    for row in rows:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL|re.IGNORECASE)
        parsed.append([re.sub(r'<[^>]+>','',c).strip() for c in cells])
    if len(parsed) < 3: return [], []
    headers = parsed[2]
    def col(n):
        try: return headers.index(n)
        except: return None
    idx_adi=col("ADI"); idx_soy=col("SOYADI"); idx_dob=col("DOĞUM TARİHİ")
    idx_prog=col("EĞİTİM PROGRAMI"); idx_modul=col("EĞİTİM MODÜLÜ")
    idx_rapor=col("BİTİŞ TARİHİ"); idx_sekil=col("EĞİTSEL TANI VE EĞİTİM ÖNERİSİ")
    students=[]; seen=set(); atlananlar=[]
    for row in parsed[3:]:
        if not row: continue
        sekil = row[idx_sekil].upper() if idx_sekil is not None and len(row)>idx_sekil else ""
        if "GRUP" not in sekil: continue
        ad  = row[idx_adi].strip()  if idx_adi  is not None and len(row)>idx_adi  else ""
        soy = row[idx_soy].strip()  if idx_soy  is not None and len(row)>idx_soy  else ""
        tam = f"{ad} {soy}".strip()
        if not tam or tam in seen: continue
        seen.add(tam)
        dob = None
        if idx_dob is not None and len(row)>idx_dob:
            try: dob = datetime.strptime(row[idx_dob].strip(),"%d.%m.%Y").date().isoformat()
            except: pass
        rapor = None
        if idx_rapor is not None and len(row)>idx_rapor:
            try: rapor = datetime.strptime(row[idx_rapor].strip(),"%d.%m.%Y").date().isoformat()
            except: pass
        prog_str = row[idx_prog].strip() if idx_prog is not None and len(row)>idx_prog else ""
        taniler_raw = [t.strip() for t in prog_str.split(",") if t.strip()]
        taniler = []
        for t in taniler_raw:
            k = tani_bul(t)
            if k and k not in taniler: taniler.append(k)
        modul_str = row[idx_modul].strip() if idx_modul is not None and len(row)>idx_modul else ""
        if modul_str:
            moduller = modul_bul_greedy(modul_str)
        else:
            moduller = sorted({m for t in taniler for m in TANI_MODUL_MAP.get(t,[])})
        moduller = [m for m in moduller if m in GECERLI_MODULLER]
        if not dob:
            atlananlar.append(tam)
            continue
        students.append({"name":tam,"dob":dob,"rapor_bitis":rapor,"taniler":taniler,"moduller":moduller})
    return students, atlananlar

def parse_xlsx(fb):
    ns={"ns":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(io.BytesIO(fb)) as z:
        with z.open("xl/sharedStrings.xml") as f: ss=ET.parse(f)
        shared=["".join(t.text or "" for t in si.findall(".//ns:t",ns)) for si in ss.findall(".//ns:si",ns)]
        with z.open("xl/worksheets/sheet1.xml") as f: sheet=ET.parse(f)
    def cv(c):
        v=c.find("ns:v",ns)
        if v is None: return ""
        return shared[int(v.text)] if c.get("t")=="s" else (v.text or "")
    rows=[]
    for r in sheet.findall(".//ns:row",ns):
        row={}
        for c in r.findall("ns:c",ns):
            col="".join(x for x in c.get("r","") if x.isalpha())
            row[col]=cv(c)
        rows.append(row)
    seen=set(); students=[]; atlananlar=[]
    for row in rows[3:]:
        if "GRUP" not in row.get("BN","").upper(): continue
        tam=f"{row.get('D','').strip()} {row.get('E','').strip()}".strip()
        if not tam or tam in seen: continue
        seen.add(tam)
        tani_raw=[t.strip() for t in row.get("BO","").split(",") if t.strip()]
        taniler=[]
        for t in tani_raw:
            k=tani_bul(t)
            if k and k not in taniler: taniler.append(k)
        modul_str=row.get("BP","")
        if modul_str:
            moduller=modul_bul_greedy(modul_str)
        else:
            moduller=sorted({m for t in taniler for m in TANI_MODUL_MAP.get(t,[])})
        moduller=[m for m in moduller if m in GECERLI_MODULLER]
        _dob = excel_serial(row.get("J",""))
        if not _dob:
            atlananlar.append(tam)
            continue
        students.append({"name":tam,"dob":_dob,"rapor_bitis":excel_serial(row.get("BK","")),
                         "taniler":taniler,"moduller":moduller})
    return students, atlananlar

def show_import():
    expanded = st.session_state.get("lila_ac", False)
    with st.expander("📥 Lila'dan Öğrenci Listesi İçe Aktar", expanded=expanded):
        st.caption("**.xls** veya **.xlsx** yükleyin — sadece GRUP eğitimi + sadece grup modülleri aktarılır.")
        uploaded = st.file_uploader("", type=["xls","xlsx"], key="lila_upload", label_visibility="collapsed")
        if not uploaded: return

        with st.spinner("Okunuyor..."):
            try:
                fb = uploaded.read()
                result = parse_xlsx(fb) if uploaded.name.endswith(".xlsx") else parse_xls(fb)
                students, atlananlar = result
                fmt = "XLSX" if uploaded.name.endswith(".xlsx") else "XLS"
            except Exception as e:
                st.error(f"Dosya okunamadı: {e}"); return

        if atlananlar:
            st.warning(
                f"⚠️ **{len(atlananlar)} öğrenci atlandı** — doğum tarihi eksik:\n\n" +
                "\n".join(f"• {isim}" for isim in atlananlar)
            )

        if not students:
            st.warning("GRUP eğitimi alan öğrenci bulunamadı."); return

        # Silinecekleri hesapla
        tum_mevcut = api.get_students()
        mevcut_names = {s["name"] for s in tum_mevcut}
        lila_names   = {s["name"] for s in students}
        silinecekler = [s for s in tum_mevcut if s["name"] not in lila_names]

        yeni     = sum(1 for s in students if s["name"] not in mevcut_names)
        guncelle = sum(1 for s in students if s["name"] in mevcut_names)

        st.markdown(f"""
        <div style='background:linear-gradient(135deg,rgba(66,184,177,.1),rgba(43,82,196,.07));
             border-radius:12px;padding:12px 16px;margin:8px 0 14px;border:1px solid rgba(66,184,177,.2);'>
          <b style='font-family:Sora,sans-serif;color:#1A2B4C;'>{len(students)} öğrenci bulundu</b>
          <span style='font-size:12px;color:#6B7A99;margin-left:10px;'>Format: {fmt}</span>
        </div>""", unsafe_allow_html=True)

        # Tablo
        rows_html = ""
        for i,s in enumerate(students,1):
            tani_kisa = " / ".join(
                t.replace(" Olan Bireyler İçin Destek Eğitim Programı","").strip()
                for t in s["taniler"]
            ) or "–"
            mod_tags = "".join(
                f'<span style="display:inline-block;background:rgba(66,184,177,.13);color:#1A2B4C;'
                f'border-radius:4px;padding:1px 7px;margin:2px;font-size:11px;">{m}</span>'
                for m in s["moduller"]) or "–"
            rows_html += f"""<tr style='border-bottom:1px solid rgba(26,43,76,.06);'>
              <td style='padding:7px 10px;color:#6B7A99;font-size:12px;'>{i}</td>
              <td style='padding:7px 10px;font-weight:600;color:#1A2B4C;font-size:13px;'>{s['name']}</td>
              <td style='padding:7px 10px;color:#1A2B4C;font-size:12px;'>{s['dob'] or '–'}</td>
              <td style='padding:7px 10px;color:#1A2B4C;font-size:12px;'>{s['rapor_bitis'] or '–'}</td>
              <td style='padding:7px 10px;font-size:12px;color:#1A2B4C;'>{tani_kisa}</td>
              <td style='padding:7px 10px;'>{mod_tags}</td>
            </tr>"""

        st.markdown(f"""
        <div style='overflow-x:auto;border-radius:10px;border:1px solid rgba(26,43,76,.08);'>
        <table style='width:100%;border-collapse:collapse;font-family:DM Sans,sans-serif;'>
          <thead><tr style='background:linear-gradient(135deg,#42B8B1,#2B52C4);'>
            {''.join(f"<th style='padding:9px 10px;color:white;font-family:Sora,sans-serif;font-size:12px;text-align:left;'>{h}</th>" for h in ['#','Ad Soyad','Doğum','Rapor Bitiş','Tanı','Grup Modülleri'])}
          </tr></thead>
          <tbody style='background:white;'>{rows_html}</tbody>
        </table></div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        c1, c2 = st.columns([3,1])
        with c1:
            if yeni:        st.markdown(f"🟢 **{yeni}** yeni öğrenci eklenecek")
            if guncelle:    st.markdown(f"🔄 **{guncelle}** öğrenci güncellenecek")
            if silinecekler:
                isimler = ", ".join(s["name"] for s in silinecekler[:5])
                fazla   = f" ve {len(silinecekler)-5} kişi daha" if len(silinecekler) > 5 else ""
                st.markdown(f"🗑️ **{len(silinecekler)}** öğrenci silinecek: {isimler}{fazla}")
        with c2:
            if st.button("🚀 İçe Aktar", type="primary", use_container_width=True, key="lila_btn"):
                _do_import(students, mevcut_names, silinecekler)

def _do_import(students, mevcut_names, silinecekler):
    mt = {d["name"]:d["id"] for d in api.get_diagnoses()}
    mm = {m["name"]:m["id"] for m in api.get_modules()}
    for t in {t for s in students for t in s["taniler"]}:
        if t not in mt:
            r=api.create_diagnosis(t)
            if r: mt[t]=r["id"]
    for m in {m for s in students for m in s["moduller"]}:
        if m not in mm:
            r=api.create_module(m)
            if r: mm[m]=r["id"]
    id_map={s["name"]:s["id"] for s in api.get_students()}
    eklendi=guncellendi=silindi=hatali=0
    toplam = len(students) + len(silinecekler)
    prog=st.progress(0)

    # Ekle / güncelle
    for i,s in enumerate(students):
        diag_ids=[mt[t] for t in s["taniler"] if t in mt]
        mod_ids =[mm[m] for m in s["moduller"] if m in mm]
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
        prog.progress((i+1)/toplam)

    # Sil
    for j,s in enumerate(silinecekler):
        try:
            api.delete_student(s["id"])
            silindi+=1
        except: hatali+=1
        prog.progress((len(students)+j+1)/toplam)

    prog.empty()
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,rgba(66,184,177,.12),rgba(43,82,196,.08));
         border-radius:12px;padding:14px 18px;border:1px solid rgba(66,184,177,.25);'>
      <b style='font-family:Sora,sans-serif;color:#1A2B4C;'>✅ Tamamlandı</b><br>
      <span style='font-size:13px;color:#1A2B4C;'>
        🟢 {eklendi} yeni &nbsp;·&nbsp; 🔄 {guncellendi} güncellendi
        &nbsp;·&nbsp; 🗑️ {silindi} silindi &nbsp;·&nbsp; ❌ {hatali} hata
      </span>
    </div>""", unsafe_allow_html=True)
    from datetime import datetime
    st.session_state["son_lila_import"] = datetime.now().isoformat()
    st.session_state["lila_ac"]=False
    st.session_state["students_cache_bust"] = st.session_state.get("students_cache_bust",0)+1
    st.rerun()
