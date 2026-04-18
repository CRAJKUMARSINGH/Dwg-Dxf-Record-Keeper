import streamlit as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANUAL = ROOT / "docs" / "USER_MANUAL.md"

st.set_page_config(
    page_title="Dwg-Dxf-Record-Keeper — Manual",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("Dwg-Dxf-Record-Keeper")
st.caption("User manual (from repo `docs/USER_MANUAL.md`)")

if not MANUAL.is_file():
    st.error("Could not find `docs/USER_MANUAL.md` at repository root.")
    st.stop()

text = MANUAL.read_text(encoding="utf-8")
st.markdown(text)
