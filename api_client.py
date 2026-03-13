"""
Tüm backend API çağrıları burada.
Frontend hiçbir zaman doğrudan DB'ye bağlanmaz.

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
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _handle(resp: requests.Response):
    """Response'u döndür; hata varsa Streamlit'e göster."""
    try:
        resp.raise_for_status()
        return resp.json() if resp.content else None
    except requests.HTTPError as e:
        detail = ""
        try:
            detail = resp.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        logger.error("API hata %s – %s", resp.status_code, detail)
        st.error(f"Hata ({resp.status_code}): {detail}")
        return None


def is_demo_mode() -> bool:
    return bool(st.session_state.get("is_demo"))


def _demo_init():
    """Demo session state değerlerini başlat (ilk çağrıda)."""
    if "demo_students" not in st.session_state:
        st.session_state["demo_students"] = []
    if "demo_saved_groups" not in st.session_state:
        st.session_state["demo_saved_groups"] = []
    if "demo_next_student_id" not in st.session_state:
        st.session_state["demo_next_student_id"] = 2000
    if "demo_next_group_id" not in st.session_state:
        st.session_state["demo_next_group_id"] = 4000


# ── Auth ────────────────────────────────────────────────────────────────────

def login(email: str, password: str):
    resp = requests.post(
        f"{API_URL}/api/login",
        data={"username": email, "password": password},
    )
    return _handle(resp)


def register(ad: str, email: str, password: str):
    resp = requests.post(
        f"{API_URL}/api/register",
        json={"ad": ad, "email": email, "password": password},
    )
    return _handle(resp)


def get_me():
    resp = requests.get(f"{API_URL}/api/me", headers=_headers())
    return _handle(resp)


# ── Students ─────────────────────────────────────────────────────────────────

def get_students():
    if is_demo_mode():
        _demo_init()
        from demo_data import DEMO_STUDENTS
        return DEMO_STUDENTS + st.session_state["demo_students"]
    resp = requests.get(f"{API_URL}/api/students", headers=_headers())
    return _handle(resp) or []


def create_student(payload: dict):
    if is_demo_mode():
        _demo_init()
        from demo_data import DEMO_MAX_STUDENTS, DEMO_DIAGNOSES, DEMO_MODULES
        user_count = len(st.session_state["demo_students"])
        if user_count >= DEMO_MAX_STUDENTS:
            st.warning(
                f"Demo hesapta en fazla {DEMO_MAX_STUDENTS} öğrenci ekleyebilirsiniz."
            )
            return None
        # ID ve ilişki nesnelerini oluştur
        new_id = st.session_state["demo_next_student_id"]
        st.session_state["demo_next_student_id"] += 1

        diag_map = {d["id"]: d for d in DEMO_DIAGNOSES}
        mod_map  = {m["id"]: m for m in DEMO_MODULES}

        student = {
            "id": new_id,
            "name": payload.get("name", ""),
            "dob": payload.get("dob"),
            "rapor_bitis": payload.get("rapor_bitis"),
            "diagnoses": [diag_map[i] for i in payload.get("diagnosis_ids", []) if i in diag_map],
            "modules":   [mod_map[i]  for i in payload.get("module_ids", [])    if i in mod_map],
        }
        st.session_state["demo_students"].append(student)
        return student
    resp = requests.post(f"{API_URL}/api/students", json=payload, headers=_headers())
    return _handle(resp)


def update_student(student_id: int, payload: dict):
    if is_demo_mode():
        _demo_init()
        from demo_data import DEMO_DIAGNOSES, DEMO_MODULES
        students = st.session_state["demo_students"]
        for i, s in enumerate(students):
            if s["id"] == student_id:
                diag_map = {d["id"]: d for d in DEMO_DIAGNOSES}
                mod_map  = {m["id"]: m for m in DEMO_MODULES}
                students[i] = {
                    **s,
                    "name": payload.get("name", s["name"]),
                    "dob": payload.get("dob", s["dob"]),
                    "rapor_bitis": payload.get("rapor_bitis", s["rapor_bitis"]),
                    "diagnoses": [diag_map[i] for i in payload.get("diagnosis_ids", []) if i in diag_map],
                    "modules":   [mod_map[i]  for i in payload.get("module_ids", [])    if i in mod_map],
                }
                return students[i]
        # Demo öğrenciler (1001-1020) salt-okunur
        st.info("Demo öğrenciler düzenlenemez. Yalnızca kendinizin eklediği öğrencileri güncelleyebilirsiniz.")
        return None
    resp = requests.put(f"{API_URL}/api/students/{student_id}", json=payload, headers=_headers())
    return _handle(resp)


def delete_student(student_id: int):
    if is_demo_mode():
        _demo_init()
        before = len(st.session_state["demo_students"])
        st.session_state["demo_students"] = [
            s for s in st.session_state["demo_students"] if s["id"] != student_id
        ]
        if len(st.session_state["demo_students"]) < before:
            return True
        st.info("Demo öğrenciler silinemez. Yalnızca kendinizin eklediği öğrencileri silebilirsiniz.")
        return False
    resp = requests.delete(f"{API_URL}/api/students/{student_id}", headers=_headers())
    return resp.status_code == 204


# ── Diagnoses ────────────────────────────────────────────────────────────────

def get_diagnoses():
    if is_demo_mode():
        from demo_data import DEMO_DIAGNOSES
        return DEMO_DIAGNOSES
    resp = requests.get(f"{API_URL}/api/diagnoses", headers=_headers())
    return _handle(resp) or []


def create_diagnosis(name: str):
    if is_demo_mode():
        st.info("Demo hesapta tanı eklenemez.")
        return None
    resp = requests.post(f"{API_URL}/api/diagnoses", json={"name": name}, headers=_headers())
    return _handle(resp)


def delete_diagnosis(diagnosis_id: int):
    if is_demo_mode():
        st.info("Demo hesapta tanı silinemez.")
        return False
    resp = requests.delete(f"{API_URL}/api/diagnoses/{diagnosis_id}", headers=_headers())
    return resp.status_code == 204


# ── Modules ──────────────────────────────────────────────────────────────────

def get_modules():
    if is_demo_mode():
        from demo_data import DEMO_MODULES
        return DEMO_MODULES
    resp = requests.get(f"{API_URL}/api/modules", headers=_headers())
    return _handle(resp) or []


def create_module(name: str):
    if is_demo_mode():
        st.info("Demo hesapta modül eklenemez.")
        return None
    resp = requests.post(f"{API_URL}/api/modules", json={"name": name}, headers=_headers())
    return _handle(resp)


def delete_module(module_id: int):
    if is_demo_mode():
        st.info("Demo hesapta modül silinemez.")
        return False
    resp = requests.delete(f"{API_URL}/api/modules/{module_id}", headers=_headers())
    return resp.status_code == 204


# ── Saved Groups ──────────────────────────────────────────────────────────────

def get_saved_groups():
    if is_demo_mode():
        _demo_init()
        from demo_data import DEMO_SAVED_GROUPS
        return DEMO_SAVED_GROUPS + st.session_state["demo_saved_groups"]
    resp = requests.get(f"{API_URL}/api/saved-groups", headers=_headers())
    return _handle(resp) or []


def create_saved_group(payload: dict):
    if is_demo_mode():
        _demo_init()
        new_id = st.session_state["demo_next_group_id"]
        st.session_state["demo_next_group_id"] += 1
        group = {
            "id": new_id,
            "liste_adi": payload.get("liste_adi", ""),
            "ogrenciler": payload.get("ogrenciler", ""),
            "moduller": payload.get("moduller", ""),
            "saat": payload.get("saat"),
            "notlar": payload.get("notlar"),
            "created_at": "2026-01-01T00:00:00",
        }
        st.session_state["demo_saved_groups"].append(group)
        return group
    resp = requests.post(f"{API_URL}/api/saved-groups", json=payload, headers=_headers())
    return _handle(resp)


def patch_saved_group(group_id: int, payload: dict):
    if is_demo_mode():
        _demo_init()
        groups = st.session_state["demo_saved_groups"]
        for i, g in enumerate(groups):
            if g["id"] == group_id:
                groups[i] = {**g, **payload}
                return groups[i]
        st.info("Demo gruplar düzenlenemez. Yalnızca kendinizin oluşturduğu grupları güncelleyebilirsiniz.")
        return None
    resp = requests.patch(f"{API_URL}/api/saved-groups/{group_id}", json=payload, headers=_headers())
    return _handle(resp)


def delete_saved_group(group_id: int):
    if is_demo_mode():
        _demo_init()
        before = len(st.session_state["demo_saved_groups"])
        st.session_state["demo_saved_groups"] = [
            g for g in st.session_state["demo_saved_groups"] if g["id"] != group_id
        ]
        if len(st.session_state["demo_saved_groups"]) < before:
            return True
        st.info("Demo gruplar silinemez. Yalnızca kendinizin oluşturduğu grupları silebilirsiniz.")
        return False
    resp = requests.delete(f"{API_URL}/api/saved-groups/{group_id}", headers=_headers())
    return resp.status_code == 204
