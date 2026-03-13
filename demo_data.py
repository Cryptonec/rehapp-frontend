"""
Demo hesap için sabit mock verisi.
Tüm ID'ler gerçek API ID'leriyle çakışmaması için yüksek tutulmuştur.
  Tanılar  : 101–107
  Modüller : 201–208
  Öğrenciler: 1001–1020  (kullanıcı eklemeleri: 2000+)
  Gruplar  : 3001–3003  (kullanıcı eklemeleri: 4000+)
"""

DEMO_DIAGNOSES = [
    {"id": 101, "name": "Otizm Spektrum Bozukluğu"},
    {"id": 102, "name": "Dikkat Eksikliği Hiperaktivite Bozukluğu"},
    {"id": 103, "name": "Zihinsel Yetersizlik"},
    {"id": 104, "name": "Dil ve Konuşma Bozukluğu"},
    {"id": 105, "name": "Down Sendromu"},
    {"id": 106, "name": "Serebral Palsi"},
    {"id": 107, "name": "Öğrenme Güçlüğü"},
]

DEMO_MODULES = [
    {"id": 201, "name": "Dil ve Konuşma Terapisi"},
    {"id": 202, "name": "Özel Eğitim"},
    {"id": 203, "name": "Sosyal Beceri Eğitimi"},
    {"id": 204, "name": "Matematik Becerileri"},
    {"id": 205, "name": "Öz Bakım Becerileri"},
    {"id": 206, "name": "Motor Beceriler"},
    {"id": 207, "name": "Dikkat ve Konsantrasyon"},
    {"id": 208, "name": "Adaptif Davranış"},
]

DEMO_STUDENTS = [
    {
        "id": 1001, "name": "Ahmet Yılmaz",
        "dob": "2016-03-14", "rapor_bitis": "2025-06-30",
        "diagnoses": [{"id": 101, "name": "Otizm Spektrum Bozukluğu"}],
        "modules": [
            {"id": 201, "name": "Dil ve Konuşma Terapisi"},
            {"id": 202, "name": "Özel Eğitim"},
            {"id": 203, "name": "Sosyal Beceri Eğitimi"},
        ],
    },
    {
        "id": 1002, "name": "Elif Kaya",
        "dob": "2015-07-22", "rapor_bitis": "2025-09-15",
        "diagnoses": [{"id": 102, "name": "Dikkat Eksikliği Hiperaktivite Bozukluğu"}],
        "modules": [
            {"id": 202, "name": "Özel Eğitim"},
            {"id": 207, "name": "Dikkat ve Konsantrasyon"},
            {"id": 204, "name": "Matematik Becerileri"},
        ],
    },
    {
        "id": 1003, "name": "Mehmet Demir",
        "dob": "2017-01-05", "rapor_bitis": "2026-01-31",
        "diagnoses": [
            {"id": 101, "name": "Otizm Spektrum Bozukluğu"},
            {"id": 104, "name": "Dil ve Konuşma Bozukluğu"},
        ],
        "modules": [
            {"id": 201, "name": "Dil ve Konuşma Terapisi"},
            {"id": 203, "name": "Sosyal Beceri Eğitimi"},
            {"id": 202, "name": "Özel Eğitim"},
        ],
    },
    {
        "id": 1004, "name": "Zeynep Şahin",
        "dob": "2016-11-18", "rapor_bitis": "2025-12-31",
        "diagnoses": [{"id": 105, "name": "Down Sendromu"}],
        "modules": [
            {"id": 202, "name": "Özel Eğitim"},
            {"id": 205, "name": "Öz Bakım Becerileri"},
            {"id": 208, "name": "Adaptif Davranış"},
        ],
    },
    {
        "id": 1005, "name": "Can Arslan",
        "dob": "2015-04-30", "rapor_bitis": "2025-04-30",
        "diagnoses": [{"id": 102, "name": "Dikkat Eksikliği Hiperaktivite Bozukluğu"}],
        "modules": [
            {"id": 207, "name": "Dikkat ve Konsantrasyon"},
            {"id": 202, "name": "Özel Eğitim"},
            {"id": 204, "name": "Matematik Becerileri"},
        ],
    },
    {
        "id": 1006, "name": "Ayşe Çelik",
        "dob": "2018-02-14", "rapor_bitis": "2026-02-14",
        "diagnoses": [{"id": 104, "name": "Dil ve Konuşma Bozukluğu"}],
        "modules": [
            {"id": 201, "name": "Dil ve Konuşma Terapisi"},
            {"id": 202, "name": "Özel Eğitim"},
        ],
    },
    {
        "id": 1007, "name": "Enes Koç",
        "dob": "2016-08-25", "rapor_bitis": "2025-08-25",
        "diagnoses": [{"id": 101, "name": "Otizm Spektrum Bozukluğu"}],
        "modules": [
            {"id": 203, "name": "Sosyal Beceri Eğitimi"},
            {"id": 202, "name": "Özel Eğitim"},
            {"id": 206, "name": "Motor Beceriler"},
        ],
    },
    {
        "id": 1008, "name": "Selin Aydın",
        "dob": "2017-05-10", "rapor_bitis": "2025-11-30",
        "diagnoses": [{"id": 103, "name": "Zihinsel Yetersizlik"}],
        "modules": [
            {"id": 202, "name": "Özel Eğitim"},
            {"id": 205, "name": "Öz Bakım Becerileri"},
            {"id": 208, "name": "Adaptif Davranış"},
        ],
    },
    {
        "id": 1009, "name": "Burak Yıldız",
        "dob": "2015-12-03", "rapor_bitis": "2025-12-03",
        "diagnoses": [{"id": 107, "name": "Öğrenme Güçlüğü"}],
        "modules": [
            {"id": 202, "name": "Özel Eğitim"},
            {"id": 204, "name": "Matematik Becerileri"},
            {"id": 207, "name": "Dikkat ve Konsantrasyon"},
        ],
    },
    {
        "id": 1010, "name": "Hira Polat",
        "dob": "2018-09-17", "rapor_bitis": "2026-09-17",
        "diagnoses": [
            {"id": 101, "name": "Otizm Spektrum Bozukluğu"},
            {"id": 104, "name": "Dil ve Konuşma Bozukluğu"},
        ],
        "modules": [
            {"id": 201, "name": "Dil ve Konuşma Terapisi"},
            {"id": 202, "name": "Özel Eğitim"},
            {"id": 203, "name": "Sosyal Beceri Eğitimi"},
        ],
    },
    {
        "id": 1011, "name": "Ali Özkan",
        "dob": "2016-06-20", "rapor_bitis": "2025-06-20",
        "diagnoses": [{"id": 106, "name": "Serebral Palsi"}],
        "modules": [
            {"id": 206, "name": "Motor Beceriler"},
            {"id": 202, "name": "Özel Eğitim"},
            {"id": 205, "name": "Öz Bakım Becerileri"},
        ],
    },
    {
        "id": 1012, "name": "Nisa Güneş",
        "dob": "2017-03-08", "rapor_bitis": "2026-03-08",
        "diagnoses": [{"id": 102, "name": "Dikkat Eksikliği Hiperaktivite Bozukluğu"}],
        "modules": [
            {"id": 207, "name": "Dikkat ve Konsantrasyon"},
            {"id": 204, "name": "Matematik Becerileri"},
            {"id": 202, "name": "Özel Eğitim"},
        ],
    },
    {
        "id": 1013, "name": "Onur Taş",
        "dob": "2015-10-22", "rapor_bitis": "2025-10-22",
        "diagnoses": [{"id": 101, "name": "Otizm Spektrum Bozukluğu"}],
        "modules": [
            {"id": 203, "name": "Sosyal Beceri Eğitimi"},
            {"id": 201, "name": "Dil ve Konuşma Terapisi"},
            {"id": 202, "name": "Özel Eğitim"},
        ],
    },
    {
        "id": 1014, "name": "İrem Doğan",
        "dob": "2018-01-15", "rapor_bitis": "2026-01-15",
        "diagnoses": [{"id": 105, "name": "Down Sendromu"}],
        "modules": [
            {"id": 205, "name": "Öz Bakım Becerileri"},
            {"id": 208, "name": "Adaptif Davranış"},
            {"id": 202, "name": "Özel Eğitim"},
            {"id": 206, "name": "Motor Beceriler"},
        ],
    },
    {
        "id": 1015, "name": "Kerem Acar",
        "dob": "2016-07-04", "rapor_bitis": "2025-07-04",
        "diagnoses": [
            {"id": 107, "name": "Öğrenme Güçlüğü"},
            {"id": 102, "name": "Dikkat Eksikliği Hiperaktivite Bozukluğu"},
        ],
        "modules": [
            {"id": 202, "name": "Özel Eğitim"},
            {"id": 204, "name": "Matematik Becerileri"},
            {"id": 207, "name": "Dikkat ve Konsantrasyon"},
        ],
    },
    {
        "id": 1016, "name": "Defne Yurt",
        "dob": "2017-11-28", "rapor_bitis": "2026-05-28",
        "diagnoses": [{"id": 104, "name": "Dil ve Konuşma Bozukluğu"}],
        "modules": [
            {"id": 201, "name": "Dil ve Konuşma Terapisi"},
            {"id": 203, "name": "Sosyal Beceri Eğitimi"},
        ],
    },
    {
        "id": 1017, "name": "Emre Kılıç",
        "dob": "2015-05-19", "rapor_bitis": "2025-05-19",
        "diagnoses": [
            {"id": 103, "name": "Zihinsel Yetersizlik"},
            {"id": 106, "name": "Serebral Palsi"},
        ],
        "modules": [
            {"id": 206, "name": "Motor Beceriler"},
            {"id": 205, "name": "Öz Bakım Becerileri"},
            {"id": 202, "name": "Özel Eğitim"},
            {"id": 208, "name": "Adaptif Davranış"},
        ],
    },
    {
        "id": 1018, "name": "Sude Çetin",
        "dob": "2018-04-06", "rapor_bitis": "2026-04-06",
        "diagnoses": [{"id": 101, "name": "Otizm Spektrum Bozukluğu"}],
        "modules": [
            {"id": 202, "name": "Özel Eğitim"},
            {"id": 203, "name": "Sosyal Beceri Eğitimi"},
            {"id": 201, "name": "Dil ve Konuşma Terapisi"},
        ],
    },
    {
        "id": 1019, "name": "Baran Şen",
        "dob": "2016-09-12", "rapor_bitis": "2025-09-12",
        "diagnoses": [{"id": 102, "name": "Dikkat Eksikliği Hiperaktivite Bozukluğu"}],
        "modules": [
            {"id": 207, "name": "Dikkat ve Konsantrasyon"},
            {"id": 202, "name": "Özel Eğitim"},
        ],
    },
    {
        "id": 1020, "name": "Ece Güler",
        "dob": "2017-08-30", "rapor_bitis": "2026-08-30",
        "diagnoses": [
            {"id": 105, "name": "Down Sendromu"},
            {"id": 103, "name": "Zihinsel Yetersizlik"},
        ],
        "modules": [
            {"id": 205, "name": "Öz Bakım Becerileri"},
            {"id": 208, "name": "Adaptif Davranış"},
            {"id": 202, "name": "Özel Eğitim"},
        ],
    },
]

DEMO_SAVED_GROUPS = [
    {
        "id": 3001,
        "liste_adi": "Salı OSB Grubu",
        "ogrenciler": "Ahmet Yılmaz | Mehmet Demir | Hira Polat | Onur Taş | Sude Çetin",
        "moduller": "Dil ve Konuşma Terapisi / Özel Eğitim / Sosyal Beceri Eğitimi",
        "saat": "10:00",
        "notlar": "OSB tanılı öğrenciler – konuşma ağırlıklı",
        "created_at": "2025-03-01T09:00:00",
    },
    {
        "id": 3002,
        "liste_adi": "Perşembe DEHB Grubu",
        "ogrenciler": "Elif Kaya | Can Arslan | Nisa Güneş | Kerem Acar | Baran Şen",
        "moduller": "Dikkat ve Konsantrasyon / Matematik Becerileri / Özel Eğitim",
        "saat": "14:00",
        "notlar": "DEHB ve öğrenme güçlüğü olan öğrenciler",
        "created_at": "2025-03-03T09:00:00",
    },
    {
        "id": 3003,
        "liste_adi": "Cuma Adaptif Grup",
        "ogrenciler": "Zeynep Şahin | Selin Aydın | İrem Doğan | Ece Güler",
        "moduller": "Adaptif Davranış / Öz Bakım Becerileri / Özel Eğitim",
        "saat": "11:00",
        "notlar": "Down sendromu ve zihinsel yetersizlik grubu",
        "created_at": "2025-03-05T09:00:00",
    },
]

# Demo'da kullanıcının ekleyebileceği maksimum öğrenci sayısı
DEMO_MAX_STUDENTS = 3
