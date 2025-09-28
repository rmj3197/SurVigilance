import importlib
import os
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # pragma: no cover
    sys.path.insert(0, str(ROOT))


try:
    scrape_nzsmars_module = importlib.import_module("scrapers.scrape_nzsmars")
    scrape_medsafe_sb = scrape_nzsmars_module.scrape_medsafe_sb
except Exception as e:  # pragma: no cover
    st.set_page_config(page_title="NZ MEDSAFE Search", layout="wide")
    st.error(f"Failed to import the NZ MEDSAFE scraper: {e}")
    st.stop()


st.set_page_config(
    page_title="Data access page for NZ MEDSAFE",
    layout="wide",
    page_icon="SurVigilance/ui/assets/survigilance_sticker.ico",
)


st.session_state.setdefault("data_root", "data")
nz_dir = os.path.join(
    os.path.expanduser(st.session_state.get("data_root", "data")), "nzsmars"
)

nz_dir_display = os.path.abspath(nz_dir)


st.session_state.setdefault("selected_database", "NZ MEDSAFE")
st.session_state.setdefault("nz_drug", "Atorvastatin")
st.session_state.setdefault("nz_type", "Medicine")  # Medicine or Vaccine


heading = f"Search Page for {st.session_state['selected_database']} Database"
st.markdown(f"<h1 style='text-align: center;'>{heading}</h1>", unsafe_allow_html=True)
st.info(
    f"""
    How the NZ MEDSAFE data collection works:
    - Opens the Medsafe ADR Search, and searches the user-provided term.
    - Parses the Preferred Terms (PTs) grouped by SOC and counts across result pages.
    - Saves a CSV to `{nz_dir_display}/<term>_nzsmars_adrs.csv`.
    """
)

st.divider()


with st.form("search_form", clear_on_submit=False):
    st.text_input(
        "Please input a medicine/vaccine for which you want the data",
        key="nz_drug",
    )
    st.radio(
        "Type",
        options=["Medicine", "Vaccine"],
        key="nz_type",
        horizontal=True,
    )
    submitted = st.form_submit_button("Search")

st.divider()


progress = st.empty()  # Progress bar area
log_box = st.empty()  # Streaming logs and/or info
error_box = st.empty()  # For any errors encountered
status_box = st.empty()  # Overall status messages
table_box = st.empty()  # place where data is displayed


_progress_state = {"value": 0.0}


def streamlit_callback(event: dict) -> None:  # pragma: no cover
    """
    Simple callback used by the scraper to update the UI.

    It handles progress updates, logs, and errors in a user-friendly way.
    """
    etype = event.get("type")
    if etype == "progress":
        delta = float(event.get("delta", 0.0))
        _progress_state["value"] = min(100.0, _progress_state["value"] + delta)
        progress.progress(int(_progress_state["value"]))
    elif etype == "log":
        msg = event.get("message", "")
        log_box.info(msg)
    elif etype == "error":
        msg = event.get("message", "Unknown error")
        error_box.error(msg)
    elif etype == "done":
        status_box.success("Data Fetching Complete!")


if submitted:
    term = st.session_state["nz_drug"].strip()
    kind = st.session_state["nz_type"].strip().lower()  # medicine or vaccine
    if kind not in {"medicine", "vaccine"}:
        kind = "medicine"

    _progress_state["value"] = 0.0
    progress.progress(0)
    log_box.empty()
    error_box.empty()
    status_box.info(f"Starting data collection for: {term} ({kind})")
    table_box.empty()

    if not term:
        error_box.error("Please enter a search term.")
    else:
        try:
            results = scrape_medsafe_sb(
                searching_for=kind,
                drug_vaccine=term,
                output_dir=nz_dir,
                callback=streamlit_callback,
                headless=True,
            )
            if results is not None and not results.empty:
                table_box.dataframe(results, width="stretch")
            else:  # pragma: no cover
                table_box.info("No results returned.")
        except Exception as e:  # pragma: no cover
            error_box.error(f"Data collection failed: {e}")
            status_box.error("Data collection aborted.")


# limited support in streamlit testing to switch pages in a multipage app, causes issues
if st.button("Go Back to Homepage", width="stretch"):  # pragma: no cover
    st.switch_page("_app.py")

st.markdown(
    r"""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display: none;}
        .stAppDeployButton {visibility: hidden;}
        footer {visibility: hidden;}
        #stDecoration {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)
