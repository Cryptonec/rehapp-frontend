"""
Tüm backend API çağrıları burada.
"""
import os
import requests
import streamlit as st
import logging

logger = logging.getLogger(__name__)
API_URL = os.environ.get("API_URL", "https://rehapp-backend.onrender.com").rstrip("/")


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


# ── Auth ─────────────────────────────────────────────────────────────────────
def login(email, password):
    return _handle(requests.post(f"{API_URL}/api/login", data={"username": email, "password": password}, timeout=60))

def register(ad, email, password):
    return _handle(requests.post(f"{API_URL}/api/register", json={"ad": ad, "email": email, "password": password}))

def get_me():
    return _handle(requests.get(f"{API_URL}/api/me", headers=_headers()))

# ── Students ──────────────────────────────────────────────────────────────────
def get_students():
    return _handle(requests.get(f"{API_URL}/api/students", headers=_headers())) or []

def create_student(payload):
    return _handle(requests.post(f"{API_URL}/api/students", json=payload, headers=_headers()))

def update_student(sid, payload):
    return _handle(requests.put(f"{API_URL}/api/students/{sid}", json=payload, headers=_headers()))

def delete_student(sid):
    return requests.delete(f"{API_URL}/api/students/{sid}", headers=_headers()).status_code == 204

# ── Diagnoses ─────────────────────────────────────────────────────────────────
def get_diagnoses():
    return _handle(requests.get(f"{API_URL}/api/diagnoses", headers=_headers())) or []

def create_diagnosis(name):
    return _handle(requests.post(f"{API_URL}/api/diagnoses", json={"name": name}, headers=_headers()))

def delete_diagnosis(did):
    return requests.delete(f"{API_URL}/api/diagnoses/{did}", headers=_headers()).status_code == 204

# ── Modules ───────────────────────────────────────────────────────────────────
def get_modules():
    return _handle(requests.get(f"{API_URL}/api/modules", headers=_headers())) or []

def create_module(name):
    return _handle(requests.post(f"{API_URL}/api/modules", json={"name": name}, headers=_headers()))

def delete_module(mid):
    return requests.delete(f"{API_URL}/api/modules/{mid}", headers=_headers()).status_code == 204

# ── Saved Groups ──────────────────────────────────────────────────────────────
def get_saved_groups():
    return _handle(requests.get(f"{API_URL}/api/saved-groups", headers=_headers())) or []

def create_saved_group(payload):
    return _handle(requests.post(f"{API_URL}/api/saved-groups", json=payload, headers=_headers()))

def patch_saved_group(gid, payload):
    return _handle(requests.patch(f"{API_URL}/api/saved-groups/{gid}", json=payload, headers=_headers()))

def delete_saved_group(gid):
    return requests.delete(f"{API_URL}/api/saved-groups/{gid}", headers=_headers()).status_code == 204

# ── BKDS SSO ─────────────────────────────────────────────────────────────────
def get_bkds_sso_url():
    return _handle(requests.get(f"{API_URL}/bkds/sso-url", headers=_headers(), timeout=15))

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
