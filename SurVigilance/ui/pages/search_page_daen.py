import importlib
import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # pragma: no cover
    sys.path.insert(0, str(ROOT))


try:
    scrape_daen_module = importlib.import_module("scrapers.scrape_daen")
    scrape_daen_sb = scrape_daen_module.scrape_daen_sb
except Exception as e:  # pragma: no cover
    st.set_page_config(page_title="AU DAEN Search", layout="wide")
    st.error(f"Failed to import the AU DAEN scraper: {e}")
    st.stop()


st.set_page_config(
    page_title="Data access page for AU DAEN",
    layout="wide",
    page_icon="SurVigilance/ui/assets/survigilance_sticker.ico",
)


st.session_state.setdefault("data_root", "data")
daen_dir = os.path.join(
    os.path.expanduser(st.session_state.get("data_root", "data")), "daen"
)

daen_dir_display = os.path.abspath(daen_dir)


st.session_state.setdefault("selected_database", "AU DAEN")
st.session_state.setdefault("daen_drug", "Paracetamol")


heading = f"Search Page for {st.session_state['selected_database']} Database"
st.markdown(f"<h1 style='text-align: center;'>{heading}</h1>", unsafe_allow_html=True)
st.info(
    f"""
    How the AU DAEN data collection works:
    - Opens the DAEN medicines (https://daen.tga.gov.au/medicines-search/) search and searches for the provided drug/vaccine.
    - Initiates an export of the data with MedDRA Preferred Terms (PTs) and associated counts.
    - Saves the downloaded file to `{daen_dir_display}/<medicine>_daen_export.ext`.
    """
)

st.divider()


with st.form("search_form", clear_on_submit=False):
    st.text_input(
        "Please input a medicine for which you want the data",
        key="daen_drug",
    )
    submitted = st.form_submit_button("Search")

st.divider()


log_box = st.empty()  # Streaming logs and/or info
error_box = st.empty()  # For any errors encountered
status_box = st.empty()  # Overall status messages
download_box = st.empty()  # For download link/button feedback

_last_download = {"path": None, "filename": None}


def streamlit_callback(event: dict) -> None:  # pragma: no cover
    """
    Simple callback used by the scraper to update the UI.

    It handles progress updates, logs, errors, and download completion.
    """
    etype = event.get("type")
    if etype == "log":
        msg = event.get("message", "")
        log_box.info(msg)
    elif etype == "error":
        msg = event.get("message", "Unknown error")
        error_box.error(msg)
    elif etype == "download_complete":
        path = event.get("path")
        fname = event.get("filename")
        _last_download["path"] = path
        _last_download["filename"] = fname
        status_box.success("Data Fetching Complete!")
        if path and os.path.isfile(path):
            try:
                with open(path, "rb") as f:
                    data = f.read()
                download_box.download_button(
                    label=f"Download {fname}",
                    data=data,
                    file_name=fname or os.path.basename(path),
                    mime="text/csv",
                    key="daen_download_button",
                )
            except Exception as e:
                download_box.info(
                    f"File saved to: {os.path.abspath(path)} (download button unavailable: {e})"
                )
        else:
            download_box.info(
                "Export saved, but file not found to attach a download button."
            )
    elif etype == "done":
        status_box.success("Data Fetching Complete!")


if submitted:
    med = st.session_state["daen_drug"].strip()

    log_box.empty()
    error_box.empty()
    download_box.empty()
    status_box.info(f"Starting data collection for: {med}")

    if not med:
        error_box.error("Please enter a medicine name.")
    else:
        try:
            result_df = scrape_daen_sb(
                medicine=med,
                output_dir=daen_dir,
                callback=streamlit_callback,
                headless=True,
            )
            if isinstance(result_df, pd.DataFrame):
                download_box.info(
                    f"Data collected: {len(result_df)} rows, {len(result_df.columns)} columns."
                )
            else:  # pragma: no cover
                download_box.info("Data collected.")
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
