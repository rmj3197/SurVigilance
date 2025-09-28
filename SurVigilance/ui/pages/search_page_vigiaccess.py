import importlib
import os
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # pragma: no cover
    sys.path.insert(0, str(ROOT))


try:
    scrape_vigiaccess_module = importlib.import_module("scrapers.scrape_vigiaccess")
    scrape_vigiaccess_sb = scrape_vigiaccess_module.scrape_vigiaccess_sb
except Exception as e:  # pragma: no cover
    st.set_page_config(page_title="WHO VigiAccess Search", layout="wide")
    st.error(f"Failed to import the WHO VigiAccess scraper: {e}")
    st.stop()


st.set_page_config(
    page_title="Data access page for WHO VigiAccess",
    layout="wide",
    page_icon="SurVigilance/ui/assets/survigilance_sticker.ico",
)


st.session_state.setdefault("data_root", "data")
vigi_dir = os.path.join(
    os.path.expanduser(st.session_state.get("data_root", "data")), "vigiaccess"
)

vigi_dir_display = os.path.abspath(vigi_dir)


st.session_state.setdefault("selected_database", "WHO VigiAccess")
st.session_state.setdefault("vigi_drug", "Atorvastatin")


heading = f"Search Page for {st.session_state['selected_database']} Database"
st.markdown(f"<h1 style='text-align: center;'>{heading}</h1>", unsafe_allow_html=True)
st.info(
    f"""
    How the WHO VigiAccess data collection works:
    - Opens [vigiaccess.org](https://www.vigiaccess.org/), and searches the drug name the user provided.
    - Parses the Preferred Terms (PTs) and their corresponding counts.
    - Saves a CSV to `{vigi_dir_display}/<drug>_vigiaccess_adrs.csv`.
    """
)

st.divider()


with st.form("search_form", clear_on_submit=False):
    st.text_input(
        "Please input a drug for which you want the data",
        key="vigi_drug",
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
    drug = st.session_state["vigi_drug"].strip()

    _progress_state["value"] = 0.0
    progress.progress(0)
    log_box.empty()
    error_box.empty()
    status_box.info(f"Starting data collection for: {drug}")
    table_box.empty()

    if not drug:
        error_box.error("Please enter a drug name.")
    else:
        try:
            results = scrape_vigiaccess_sb(
                medicine=drug,
                output_dir=vigi_dir,
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

# not limited support in streamlit testing to switch pages in a multipage app, causes issues
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
