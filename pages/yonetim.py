import streamlit as st
import api_client as api


def show():
    st.header("⚙️ Yönetim")

    is_demo = api.is_demo_mode()
    if is_demo:
        st.info("🎭 Demo hesapta tanı ve modüller salt-okunurdur. Ekleme veya silme yapılamaz.")

    col1, col2 = st.columns(2)

    # ── Tanılar ─────────────────────────────────────────────────────────────
    with col1:
        st.subheader("Tanılar")
        diags = api.get_diagnoses()
        for d in diags:
            c1, c2 = st.columns([4, 1])
            c1.write(d["name"])
            if not is_demo:
                if c2.button("🗑", key=f"del_diag_{d['id']}"):
                    if api.delete_diagnosis(d["id"]):
                        st.success("Tanı silindi")
                        st.rerun()

        if not is_demo:
            with st.form("new_diag", clear_on_submit=True):
                name = st.text_input("Yeni tanı adı")
                if st.form_submit_button("Ekle"):
                    if name.strip():
                        api.create_diagnosis(name.strip())
                        st.rerun()

    # ── Modüller ─────────────────────────────────────────────────────────────
    with col2:
        st.subheader("Modüller")
        mods = api.get_modules()
        for m in mods:
            c1, c2 = st.columns([4, 1])
            c1.write(m["name"])
            if not is_demo:
                if c2.button("🗑", key=f"del_mod_{m['id']}"):
                    if api.delete_module(m["id"]):
                        st.success("Modül silindi")
                        st.rerun()

        if not is_demo:
            with st.form("new_mod", clear_on_submit=True):
                name = st.text_input("Yeni modül adı")
                if st.form_submit_button("Ekle"):
                    if name.strip():
                        api.create_module(name.strip())
                        st.rerun()
