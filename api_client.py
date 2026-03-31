"""
Tüm backend API çağrıları burada.

Demo mod:  st.session_state["is_demo"] == True olduğunda
           gerçek API'ye istek atılmaz; mock veriler döner.
"""
import os
import requests
import streamlit as st
import logging

logger = logging.getLogger(__name__)
API_URL = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")


def _headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _handle(resp: requests.Response):
    try:
        resp.raise_for_status()
        return resp.json() if resp.content else None
    except requests.HTTPError as e:
        detail = ""
        try:
            detail = resp.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        st.error(f"Hata ({resp.status_code}): {detail}")
        return None


def is_demo_mode() -> bool:
    return bool(st.session_state.get("is_demo"))


def _demo_init():
    """Demo session state değerlerini ilk çağrıda başlat."""
    if "demo_students" not in st.session_state:
        st.session_state["demo_students"] = []
    if "demo_saved_groups" not in st.session_state:
        st.session_state["demo_saved_groups"] = []
    if "demo_next_student_id" not in st.session_state:
        st.session_state["demo_next_student_id"] = 2000
    if "demo_next_group_id" not in st.session_state:
        st.session_state["demo_next_group_id"] = 4000


# ── Auth ─────────────────────────────────────────────────────────────────────
def login(email, password):
    return _handle(requests.post(f"{API_URL}/api/login", data={"username": email, "password": password}, timeout=70))

def register(ad, email, password):
    return _handle(requests.post(f"{API_URL}/api/register", json={"ad": ad, "email": email, "password": password}))

def get_me():
    if is_demo_mode():
        return {"kurum_id": -1, "kurum_ad": "Demo Kurumu"}
    return _handle(requests.get(f"{API_URL}/api/me", headers=_headers()))

def forgot_password(email):
    return _handle(requests.post(f"{API_URL}/api/forgot-password", json={"email": email}))

def reset_password(token, new_password):
    return _handle(requests.post(f"{API_URL}/api/reset-password",
                                 json={"token": token, "new_password": new_password}))

# ── Students ──────────────────────────────────────────────────────────────────
def get_students():
    if is_demo_mode():
        _demo_init()
        from demo_data import DEMO_STUDENTS
        all_students = DEMO_STUDENTS + st.session_state["demo_students"]
        return [{**s, "name": s["name"].upper()} for s in all_students]
    return _handle(requests.get(f"{API_URL}/api/students", headers=_headers())) or []

def create_student(payload):
    if is_demo_mode():
        _demo_init()
        from demo_data import DEMO_MAX_STUDENTS, DEMO_DIAGNOSES, DEMO_MODULES
        user_count = len(st.session_state["demo_students"])
        if user_count >= DEMO_MAX_STUDENTS:
            st.warning(f"Demo hesapta en fazla {DEMO_MAX_STUDENTS} öğrenci ekleyebilirsiniz.")
            return None
        new_id   = st.session_state["demo_next_student_id"]
        st.session_state["demo_next_student_id"] += 1
        diag_map = {d["id"]: d for d in DEMO_DIAGNOSES}
        mod_map  = {m["id"]: m for m in DEMO_MODULES}
        from datetime import datetime
        student = {
            "id":          new_id,
            "name":        payload.get("name", ""),
            "dob":         payload.get("dob"),
            "rapor_bitis": payload.get("rapor_bitis"),
            "diagnoses":   [diag_map[i] for i in payload.get("diagnosis_ids", []) if i in diag_map],
            "modules":     [mod_map[i]  for i in payload.get("module_ids",    []) if i in mod_map],
            "created_at":  datetime.now().isoformat(),
        }
        st.session_state["demo_students"].append(student)
        st.session_state["students_cache_bust"] = st.session_state.get("students_cache_bust", 0) + 1
        return student
    return _handle(requests.post(f"{API_URL}/api/students", json=payload, headers=_headers()))

def update_student(sid, payload):
    if is_demo_mode():
        _demo_init()
        from demo_data import DEMO_DIAGNOSES, DEMO_MODULES
        students = st.session_state["demo_students"]
        for i, s in enumerate(students):
            if s["id"] == sid:
                diag_map = {d["id"]: d for d in DEMO_DIAGNOSES}
                mod_map  = {m["id"]: m for m in DEMO_MODULES}
                students[i] = {
                    **s,
                    "name":        payload.get("name", s["name"]),
                    "dob":         payload.get("dob", s["dob"]),
                    "rapor_bitis": payload.get("rapor_bitis", s["rapor_bitis"]),
                    "diagnoses":   [diag_map[i] for i in payload.get("diagnosis_ids", []) if i in diag_map],
                    "modules":     [mod_map[i]  for i in payload.get("module_ids",    []) if i in mod_map],
                }
                st.session_state["students_cache_bust"] = st.session_state.get("students_cache_bust", 0) + 1
                return students[i]
        st.info("Demo öğrenciler düzenlenemez. Yalnızca kendi eklediğiniz öğrencileri güncelleyebilirsiniz.")
        return None
    return _handle(requests.put(f"{API_URL}/api/students/{sid}", json=payload, headers=_headers()))

def delete_student(sid):
    if is_demo_mode():
        _demo_init()
        before = len(st.session_state["demo_students"])
        st.session_state["demo_students"] = [
            s for s in st.session_state["demo_students"] if s["id"] != sid
        ]
        if len(st.session_state["demo_students"]) < before:
            st.session_state["students_cache_bust"] = st.session_state.get("students_cache_bust", 0) + 1
            return True
        st.info("Demo öğrenciler silinemez. Yalnızca kendi eklediğiniz öğrencileri silebilirsiniz.")
        return False
    return requests.delete(f"{API_URL}/api/students/{sid}", headers=_headers()).status_code == 204

# ── Diagnoses ─────────────────────────────────────────────────────────────────
def get_diagnoses():
    if is_demo_mode():
        from demo_data import DEMO_DIAGNOSES
        return DEMO_DIAGNOSES
    return _handle(requests.get(f"{API_URL}/api/diagnoses", headers=_headers())) or []

def create_diagnosis(name):
    if is_demo_mode():
        return None
    return _handle(requests.post(f"{API_URL}/api/diagnoses", json={"name": name}, headers=_headers()))

def delete_diagnosis(did):
    if is_demo_mode():
        return False
    return requests.delete(f"{API_URL}/api/diagnoses/{did}", headers=_headers()).status_code == 204

# ── Modules ───────────────────────────────────────────────────────────────────
def get_modules():
    if is_demo_mode():
        from demo_data import DEMO_MODULES
        return DEMO_MODULES
    return _handle(requests.get(f"{API_URL}/api/modules", headers=_headers())) or []

def create_module(name):
    if is_demo_mode():
        return None
    return _handle(requests.post(f"{API_URL}/api/modules", json={"name": name}, headers=_headers()))

def delete_module(mid):
    if is_demo_mode():
        return False
    return requests.delete(f"{API_URL}/api/modules/{mid}", headers=_headers()).status_code == 204

# ── Saved Groups ──────────────────────────────────────────────────────────────
def get_saved_groups():
    if is_demo_mode():
        _demo_init()
        from demo_data import DEMO_SAVED_GROUPS
        return DEMO_SAVED_GROUPS + st.session_state["demo_saved_groups"]
    return _handle(requests.get(f"{API_URL}/api/saved-groups", headers=_headers())) or []

def create_saved_group(payload):
    if is_demo_mode():
        _demo_init()
        new_id = st.session_state["demo_next_group_id"]
        st.session_state["demo_next_group_id"] += 1
        group = {
            "id":         new_id,
            "liste_adi":  payload.get("liste_adi", ""),
            "ogrenciler": payload.get("ogrenciler", ""),
            "moduller":   payload.get("moduller", ""),
            "saat":       payload.get("saat"),
            "notlar":     payload.get("notlar"),
            "created_at": "2026-01-01T00:00:00",
        }
        st.session_state["demo_saved_groups"].append(group)
        return group
    return _handle(requests.post(f"{API_URL}/api/saved-groups", json=payload, headers=_headers()))

def patch_saved_group(gid, payload):
    if is_demo_mode():
        _demo_init()
        groups = st.session_state["demo_saved_groups"]
        for i, g in enumerate(groups):
            if g["id"] == gid:
                groups[i] = {**g, **payload}
                return groups[i]
        st.info("Demo gruplar düzenlenemez. Yalnızca kendi oluşturduğunuz grupları güncelleyebilirsiniz.")
        return None
    return _handle(requests.patch(f"{API_URL}/api/saved-groups/{gid}", json=payload, headers=_headers()))

def delete_saved_group(gid):
    if is_demo_mode():
        _demo_init()
        before = len(st.session_state["demo_saved_groups"])
        st.session_state["demo_saved_groups"] = [
            g for g in st.session_state["demo_saved_groups"] if g["id"] != gid
        ]
        if len(st.session_state["demo_saved_groups"]) < before:
            return True
        st.info("Demo gruplar silinemez. Yalnızca kendi oluşturduğunuz grupları silebilirsiniz.")
        return False
    return requests.delete(f"{API_URL}/api/saved-groups/{gid}", headers=_headers()).status_code == 204

# ── Admin ─────────────────────────────────────────────────────────────────────
def admin_get_kurumlar():
    candidates = [
        f"{API_URL}/api/admin/kurumlar",
        f"{API_URL}/api/admin/kurumlar/",
        f"{API_URL}/api/admin/institutions",
    ]
    for url in candidates:
        resp = requests.get(url, headers=_headers())
        if resp.status_code == 404:
            continue
        data = _handle(resp)
        if data is None:
            return []
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("items", "results", "data", "kurumlar", "institutions"):
                if isinstance(data.get(key), list):
                    return data.get(key)
        st.error("Kurum listesi yanıt formatı beklenenden farklı.")
        return []
    st.error("Kurum listesi endpoint'i bulunamadı.")
    return []

def admin_onayla(kurum_id):
    return _handle(requests.post(f"{API_URL}/api/admin/kurumlar/{kurum_id}/onayla", headers=_headers()))

def admin_pasif(kurum_id):
    return _handle(requests.post(f"{API_URL}/api/admin/kurumlar/{kurum_id}/pasif", headers=_headers()))

def admin_resend_onay_mail(kurum_id):
    return _handle(requests.post(f"{API_URL}/api/admin/kurumlar/{kurum_id}/onayla", headers=_headers()))

def admin_sil_kurum(kurum_id):
    try:
        r = requests.delete(f"{API_URL}/api/admin/kurumlar/{kurum_id}", headers=_headers())
        return r.status_code == 200
    except Exception:
        return False
