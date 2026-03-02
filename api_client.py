"""
Tüm backend API çağrıları burada.
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


# ── Auth ─────────────────────────────────────────────────────────────────────
def login(email, password):
    return _handle(requests.post(f"{API_URL}/api/login", data={"username": email, "password": password}))

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

# ── Admin ─────────────────────────────────────────────────────────────────────
def _admin_resource_paths():
    return [
        "kurumlar",
        "kurum",
        "institutions",
        "institution",
        "organizations",
        "orgs",
    ]


def _admin_list_paths(resource):
    return [
        f"{API_URL}/api/admin/{resource}",
        f"{API_URL}/api/admin/{resource}/",
        f"{API_URL}/api/admin/{resource}/list",
    ]


def _parse_kurum_list(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("items", "results", "data", "kurumlar", "institutions", "organizations"):
            value = data.get(key)
            if isinstance(value, list):
                return value
    return None


def admin_get_kurumlar():
    for resource in _admin_resource_paths():
        for url in _admin_list_paths(resource):
            resp = requests.get(url, headers=_headers())
            if resp.status_code == 404:
                continue

            data = _handle(resp)
            if data is None:
                return []

            kurumlar = _parse_kurum_list(data)
            if kurumlar is not None:
                return kurumlar

            st.error("Kurum listesi yanıt formatı beklenenden farklı.")
            return []

    logger.warning("Admin kurum listesi endpoint'i bulunamadı.")
    return []


def _admin_action_urls(resource, kurum_id, action_suffix):
    return [
        f"{API_URL}/api/admin/{resource}/{kurum_id}/{action_suffix}",
        f"{API_URL}/api/admin/{resource}/{action_suffix}/{kurum_id}",
        f"{API_URL}/api/admin/{action_suffix}/{resource}/{kurum_id}",
    ]


def _admin_action_post(kurum_id, action_suffixes):
    last_error = None
    for resource in _admin_resource_paths():
        for action_suffix in action_suffixes:
            for url in _admin_action_urls(resource, kurum_id, action_suffix):
                resp = requests.post(url, headers=_headers())
                if resp.status_code == 404:
                    continue
                if 200 <= resp.status_code < 300:
                    return resp.json() if resp.content else {"ok": True}
                last_error = resp
                break
            if last_error is not None:
                break
        if last_error is not None:
            break

    if last_error is not None:
        return _handle(last_error)

    st.error("Admin işlemi için uygun endpoint bulunamadı.")
    return None


def admin_onayla(kurum_id):
    return _admin_action_post(kurum_id, ("onayla", "approve", "activate"))


def admin_pasif(kurum_id):
    return _admin_action_post(kurum_id, ("pasif", "deactivate", "disable"))


def admin_resend_onay_mail(kurum_id):
    """
    Bekleyen kurum için onay/e-posta bildirimi tekrar tetikler.
    Backend sürümleri arasında endpoint adı değişebildiği için
    birkaç olası route'u sırayla dener.
    """
    return _admin_action_post(
        kurum_id,
        ("resend-onay-mail", "resend", "resend-email", "resend-approval-mail", "resend-approval"),
    )
