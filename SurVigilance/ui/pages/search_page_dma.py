import importlib
import os
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # pragma: no cover
    sys.path.insert(0, str(ROOT))


try:
    scrape_dma_module = importlib.import_module("scrapers.scrape_dma")
    scrape_dma_sb = scrape_dma_module.scrape_dma_sb
except Exception as e:  # pragma: no cover
    st.set_page_config(page_title="DK DMA Search", layout="wide")
    st.error(f"Failed to import the DK DMA scraper: {e}")
    st.stop()


st.set_page_config(
    page_title="Data access page for DK DMA",
    layout="wide",
    page_icon="SurVigilance/ui/assets/survigilance_sticker.ico",
)


st.session_state.setdefault("data_root", "data")
dma_dir = os.path.join(
    os.path.expanduser(st.session_state.get("data_root", "data")), "dma"
)

dma_dir_display = os.path.abspath(dma_dir)


st.session_state.setdefault("selected_database", "DK DMA")
st.session_state.setdefault("dma_drug", "Paracetamol")
st.session_state.setdefault("dma_log_messages", [])


heading = f"Search Page for {st.session_state['selected_database']} Database"
st.markdown(f"<h1 style='text-align: center;'>{heading}</h1>", unsafe_allow_html=True)
st.info(
    f"""
    How the DK DMA data collection works:
    - Opens the Danish Medicines Agency database (https://laegemiddelstyrelsen.dk/sideeffects/side-effects-of-medicines/interactive-adverse-drug-reaction-overviews/.aspx) and searches for provided the medicine or vaccine.
    - Extracts the MedDRA Preferred Terms (PTs) and counts associated with the drug/vaccine.
    - Saves a CSV to `{dma_dir_display}/<medicine>_dma_adrs.csv`.
    """
)

st.divider()


with st.form("search_form", clear_on_submit=False):
    st.text_input(
        "Please input a medicine for which you want the data",
        key="dma_drug",
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
        st.session_state.dma_log_messages.append(("log", msg))
    elif etype == "error":
        msg = event.get("message", "Unknown error")
        st.session_state.dma_log_messages.append(("error", msg))

    if etype in ("log", "error"):
        with log_box.container():
            for mtype, m in st.session_state.dma_log_messages:
                if mtype == "log":
                    st.info(m)
                else:
                    st.error(m)

    elif etype == "done":
        status_box.success("Data Fetching Complete!")


if submitted:
    med = st.session_state["dma_drug"].strip()

    st.session_state.dma_log_messages = []
    _progress_state["value"] = 0.0
    progress.progress(0)
    log_box.empty()
    error_box.empty()
    status_box.empty()
    table_box.empty()

    if not med:
        error_box.error("Please enter a medicine name.")
    else:
        msg = f"Starting data collection for: {med}"
        st.session_state.dma_log_messages.append(("log", msg))
        with log_box.container():
            st.info(msg)
        try:
            results = scrape_dma_sb(
                medicine=med,
                output_dir=dma_dir,
                callback=streamlit_callback,
                headless=True,
                num_retries=st.session_state.get("num_retries", 5),
            )
            if results is not None and not results.empty:
                results = results.reset_index(drop=True)
                table_box.dataframe(results, width="stretch")
            else:  # pragma: no cover
                table_box.info("No results returned.")
        except Exception:  # pragma: no cover
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
