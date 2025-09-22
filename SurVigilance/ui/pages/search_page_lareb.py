import streamlit as st
import importlib
import os

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    scrape_lareb_module = importlib.import_module("scrapers.scrape_lareb")
    scrape_lareb_sb = scrape_lareb_module.scrape_lareb_sb
except Exception as e:
    st.set_page_config(page_title="Search Page", layout="wide")
    st.error(f"Failed to import the scraper: {e}")
    st.stop()


st.set_page_config(page_title="Search Page", layout="wide")


st.session_state.setdefault("data_root", "data")
lareb_dir = os.path.join(
    os.path.expanduser(st.session_state.get("data_root", "data")), "lareb"
)


st.session_state.setdefault("selected_database", "Lareb")
st.session_state.setdefault("lareb_drug", "Atorvastatin")


heading = f"Search Page for {st.session_state['selected_database']} Database"
st.markdown(f"<h1 style='text-align: center;'>{heading}</h1>", unsafe_allow_html=True)
st.info(
    f"""
    How the Lareb data collection works:
    - Opens [lareb.nl](https://www.lareb.nl/en) and searches the drug name the user provided.
    - Extracts Preferred Terms (PT) and counts. 
    - Saves a CSV to `{lareb_dir}/<drug>_lareb_adrs.csv`.
    """
)
st.divider()

with st.form("search_form", clear_on_submit=False):
    st.text_input(
        "Please input a drug for which you want the data",
        key="lareb_drug",
    )
    submitted = st.form_submit_button("Search")

st.divider()


progress = st.empty()
log_box = st.empty()
error_box = st.empty()
status_box = st.empty()
table_box = st.empty()


_progress_state = {"value": 0.0}


def streamlit_callback(event: dict) -> None:
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
    drug = st.session_state["lareb_drug"].strip()

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
            results = scrape_lareb_sb(
                medicine=drug,
                output_dir=lareb_dir,
                callback=streamlit_callback,
                headless=True,
            )
            if results is not None and not results.empty:
                table_box.dataframe(results, width="stretch")
            else:
                table_box.info("No results returned.")
        except Exception as e:
            error_box.error(f"Data collection failed: {e}")
            status_box.error("Data collection aborted.")


if st.button("Go Back to Homepage", width="stretch"):
    st.switch_page("_app.py")
