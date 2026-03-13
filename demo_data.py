"""
Demo hesap için sabit mock verisi.
Tanı ve modül isimleri uygulamanın gerçek TANI_MODUL_MAP'iyle birebir eşleşir.

  Tanılar  : ID 101–107
  Modüller : ID 201–213
  Öğrenciler: ID 1001–1020  (kullanıcının eklemeleri: 2000+)
  Gruplar  : ID 3001–3003   (kullanıcının eklemeleri: 4000+)
"""

# ── Gerçek program isimleri ────────────────────────────────────────────────────
_OSB  = "Otizm Spektrum Bozukluğu Olan Bireyler İçin Destek Eğitim Programı"
_ZY   = "Zihinsel Yetersizliği Olan Bireyler İçin Destek Eğitim Programı"
_OGB  = "Öğrenme Güçlüğü Olan Bireyler İçin Destek Eğitim Programı"
_DKB  = "Dil ve Konuşma Bozukluğu Olan Bireyler İçin Destek Eğitim Programı"
_BY   = "Bedensel Yetersizliği Olan Bireyler İçin Destek Eğitim Programı"
_IY   = "İşitme Yetersizliği Olan Bireyler İçin Destek Eğitim Programı"

DEMO_DIAGNOSES = [
    {"id": 101, "name": _OSB},
    {"id": 102, "name": _ZY},
    {"id": 103, "name": _OGB},
    {"id": 104, "name": _DKB},
    {"id": 105, "name": _BY},
    {"id": 106, "name": _IY},
    {"id": 107, "name": "Görme Yetersizliği Olan Bireyler İçin Destek Eğitim Programı"},
]

DEMO_MODULES = [
    {"id": 201, "name": "Birey ve Çevre"},
    {"id": 202, "name": "Dil, İletişim ve Oyun"},
    {"id": 203, "name": "Erken Matematik"},
    {"id": 204, "name": "Günlük Yaşam Becerileri"},
    {"id": 205, "name": "Matematik"},
    {"id": 206, "name": "Okuma ve Yazma"},
    {"id": 207, "name": "Sosyal Beceriler"},
    {"id": 208, "name": "Toplumsal Yaşam Becerileri"},
    {"id": 209, "name": "Dil ve İletişim"},
    {"id": 210, "name": "Sosyal Etkileşim"},
    {"id": 211, "name": "Sosyal İletişim"},
    {"id": 212, "name": "Günlük Yaşam Aktiviteleri"},
    {"id": 213, "name": "Dil"},
]

# Kısa yardımcı referanslar
def _d(iid): return next(x for x in DEMO_DIAGNOSES if x["id"] == iid)
def _m(iid): return next(x for x in DEMO_MODULES    if x["id"] == iid)

DEMO_STUDENTS = [
    # ── OSB grubu ──────────────────────────────────────────────────────────
    {
        "id": 1001, "name": "Ahmet Yılmaz",
        "dob": "2016-03-14", "rapor_bitis": "2026-06-30",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(101)],
        "modules": [_m(202), _m(203), _m(207)],
    },
    {
        "id": 1002, "name": "Hira Polat",
        "dob": "2017-09-17", "rapor_bitis": "2026-09-17",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(101)],
        "modules": [_m(202), _m(203), _m(207), _m(204)],
    },
    {
        "id": 1003, "name": "Onur Taş",
        "dob": "2016-10-22", "rapor_bitis": "2026-03-15",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(101)],
        "modules": [_m(202), _m(203), _m(207), _m(201)],
    },
    {
        "id": 1004, "name": "Sude Çetin",
        "dob": "2017-04-06", "rapor_bitis": "2026-04-06",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(101)],
        "modules": [_m(202), _m(203), _m(207), _m(206)],
    },
    {
        "id": 1005, "name": "Mehmet Demir",
        "dob": "2016-01-05", "rapor_bitis": "2026-01-31",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(101)],
        "modules": [_m(202), _m(204), _m(207), _m(208)],
    },
    {
        "id": 1006, "name": "Enes Koç",
        "dob": "2015-08-25", "rapor_bitis": "2025-08-25",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(101)],
        "modules": [_m(201), _m(202), _m(205), _m(207)],
    },
    # ── ZY grubu ───────────────────────────────────────────────────────────
    {
        "id": 1007, "name": "Zeynep Şahin",
        "dob": "2015-11-18", "rapor_bitis": "2025-12-31",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(102)],
        "modules": [_m(201), _m(202), _m(203), _m(204), _m(207)],
    },
    {
        "id": 1008, "name": "Selin Aydın",
        "dob": "2016-05-10", "rapor_bitis": "2025-11-30",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(102)],
        "modules": [_m(201), _m(202), _m(204), _m(207), _m(208)],
    },
    {
        "id": 1009, "name": "İrem Doğan",
        "dob": "2016-01-15", "rapor_bitis": "2026-01-15",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(102)],
        "modules": [_m(201), _m(202), _m(203), _m(207)],
    },
    {
        "id": 1010, "name": "Ece Güler",
        "dob": "2017-08-30", "rapor_bitis": "2026-08-30",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(102)],
        "modules": [_m(202), _m(204), _m(207), _m(208)],
    },
    # ── ÖGB grubu ──────────────────────────────────────────────────────────
    {
        "id": 1011, "name": "Burak Yıldız",
        "dob": "2016-12-03", "rapor_bitis": "2025-12-03",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(103)],
        "modules": [_m(203), _m(205), _m(206), _m(210)],
    },
    {
        "id": 1012, "name": "Nisa Güneş",
        "dob": "2015-03-08", "rapor_bitis": "2026-03-08",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(103)],
        "modules": [_m(203), _m(205), _m(206), _m(209)],
    },
    {
        "id": 1013, "name": "Kerem Acar",
        "dob": "2016-07-04", "rapor_bitis": "2025-07-04",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(103)],
        "modules": [_m(203), _m(205), _m(206), _m(210)],
    },
    {
        "id": 1014, "name": "Elif Kaya",
        "dob": "2017-07-22", "rapor_bitis": "2026-09-15",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(103)],
        "modules": [_m(203), _m(205), _m(209), _m(210)],
    },
    # ── DKB grubu ──────────────────────────────────────────────────────────
    {
        "id": 1015, "name": "Ayşe Çelik",
        "dob": "2017-02-14", "rapor_bitis": "2026-02-14",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(104)],
        "modules": [_m(213)],
    },
    {
        "id": 1016, "name": "Defne Yurt",
        "dob": "2016-11-28", "rapor_bitis": "2026-05-28",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(104)],
        "modules": [_m(213)],
    },
    # ── BY grubu ───────────────────────────────────────────────────────────
    {
        "id": 1017, "name": "Ali Özkan",
        "dob": "2015-06-20", "rapor_bitis": "2025-06-20",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(105)],
        "modules": [_m(212)],
    },
    {
        "id": 1018, "name": "Emre Kılıç",
        "dob": "2016-05-19", "rapor_bitis": "2026-05-19",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(105)],
        "modules": [_m(212)],
    },
    # ── İY grubu ───────────────────────────────────────────────────────────
    {
        "id": 1019, "name": "Baran Şen",
        "dob": "2015-09-12", "rapor_bitis": "2025-09-12",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(106)],
        "modules": [_m(203), _m(205), _m(206), _m(211)],
    },
    {
        "id": 1020, "name": "Can Arslan",
        "dob": "2016-04-30", "rapor_bitis": "2026-04-30",
        "created_at": "2025-09-01T08:00:00",
        "diagnoses": [_d(106)],
        "modules": [_m(203), _m(205), _m(211)],
    },
]

DEMO_SAVED_GROUPS = [
    {
        "id": 3001,
        "liste_adi": "Salı OSB Grubu",
        "ogrenciler": "Ahmet Yılmaz | Hira Polat | Onur Taş | Sude Çetin",
        "moduller": "Dil, İletişim ve Oyun / Erken Matematik / Sosyal Beceriler",
        "saat": "10:00",
        "notlar": "OSB tanılı öğrenciler — iletişim ağırlıklı",
        "created_at": "2025-10-01T09:00:00",
    },
    {
        "id": 3002,
        "liste_adi": "Perşembe ZY Grubu",
        "ogrenciler": "Zeynep Şahin | Selin Aydın | İrem Doğan",
        "moduller": "Birey ve Çevre / Dil, İletişim ve Oyun / Sosyal Beceriler",
        "saat": "14:00",
        "notlar": "Zihinsel yetersizlik grubu",
        "created_at": "2025-10-03T09:00:00",
    },
    {
        "id": 3003,
        "liste_adi": "Cuma ÖGB Grubu",
        "ogrenciler": "Burak Yıldız | Nisa Güneş | Elif Kaya",
        "moduller": "Erken Matematik / Matematik / Okuma ve Yazma",
        "saat": "11:00",
        "notlar": "Öğrenme güçlüğü grubu",
        "created_at": "2025-10-05T09:00:00",
    },
]

# Demo'da kullanıcının ekleyebileceği maksimum öğrenci sayısı
DEMO_MAX_STUDENTS = 3
