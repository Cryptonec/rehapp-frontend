"""
Tüm backend API çağrıları burada.
Frontend hiçbir zaman doğrudan DB'ye bağlanmaz.
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
    resp = requests.get(f"{API_URL}/api/students", headers=_headers())
    return _handle(resp) or []


def create_student(payload: dict):
    resp = requests.post(f"{API_URL}/api/students", json=payload, headers=_headers())
    return _handle(resp)


def update_student(student_id: int, payload: dict):
    resp = requests.put(f"{API_URL}/api/students/{student_id}", json=payload, headers=_headers())
    return _handle(resp)


def delete_student(student_id: int):
    resp = requests.delete(f"{API_URL}/api/students/{student_id}", headers=_headers())
    return resp.status_code == 204


# ── Diagnoses ────────────────────────────────────────────────────────────────

def get_diagnoses():
    resp = requests.get(f"{API_URL}/api/diagnoses", headers=_headers())
    return _handle(resp) or []


def create_diagnosis(name: str):
    resp = requests.post(f"{API_URL}/api/diagnoses", json={"name": name}, headers=_headers())
    return _handle(resp)


def delete_diagnosis(diagnosis_id: int):
    resp = requests.delete(f"{API_URL}/api/diagnoses/{diagnosis_id}", headers=_headers())
    return resp.status_code == 204


# ── Modules ──────────────────────────────────────────────────────────────────

def get_modules():
    resp = requests.get(f"{API_URL}/api/modules", headers=_headers())
    return _handle(resp) or []


def create_module(name: str):
    resp = requests.post(f"{API_URL}/api/modules", json={"name": name}, headers=_headers())
    return _handle(resp)


def delete_module(module_id: int):
    resp = requests.delete(f"{API_URL}/api/modules/{module_id}", headers=_headers())
    return resp.status_code == 204


# ── Saved Groups ──────────────────────────────────────────────────────────────

def get_saved_groups():
    resp = requests.get(f"{API_URL}/api/saved-groups", headers=_headers())
    return _handle(resp) or []


def create_saved_group(payload: dict):
    resp = requests.post(f"{API_URL}/api/saved-groups", json=payload, headers=_headers())
    return _handle(resp)


def patch_saved_group(group_id: int, payload: dict):
    resp = requests.patch(f"{API_URL}/api/saved-groups/{group_id}", json=payload, headers=_headers())
    return _handle(resp)


def delete_saved_group(group_id: int):
    resp = requests.delete(f"{API_URL}/api/saved-groups/{group_id}", headers=_headers())
    return resp.status_code == 204
