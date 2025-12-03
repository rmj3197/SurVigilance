"""
This script is the entry point of the Streamlit application.
"""

import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

import streamlit as st

from SurVigilance.ui.scrapers import check_all_scraper_sites

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # pragma: no cover
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="SurVigilance: The Pharmacovigilance Data Mart",
    layout="wide",
    page_icon="SurVigilance/ui/assets/survigilance_sticker.ico",
)


st.markdown(
    "<h1 style='text-align: center;'>SurVigilance: The Pharmacovigilance Data Mart</h1>",
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div style="text-align: center; font-size:16px;">
    This application is designed to access and collect data from various safety databases located across the globe.  
    The primary focus of this application is to provide an unified interface to researchers to access data on adverse 
    events that may be associated the usage of pharmaceutical drugs or vaccines.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

with st.spinner("Checking connectivity to data sources..."):
    connectivity_expander = st.expander(
        "Connectivity Check", expanded=True
    )  # Expanded to show details by default
    with connectivity_expander:
        all_sites_ok, all_messages = check_all_scraper_sites(
            st_object=connectivity_expander
        )  # Passing st_object for direct writing to expander


if not all_sites_ok:
    st.error(
        "One or more of the data source sites are unreachable. There might be functionality issues due to this. "
        "Please make sure your internet connectivity is working and try again."
    )

st.subheader("Storage")


def pick_directory():  # pragma: no cover
    system = platform.system()
    if system == "Darwin":
        try:
            # subprocess executes directory picker in command line using AppleScript
            # Directory picker references used from https://developer.apple.com/library/archive/documentation/LanguagesUtilities/Conceptual/MacAutomationScriptingGuide/PromptforaFileorFolder.html
            result = subprocess.run(
                [
                    "osascript",
                    "-e",
                    'POSIX path of (choose folder with prompt "Please select data folder")',
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            return (result.stdout or "").strip() or None
        except Exception:  # pragma: no cover
            return None
    if system == "Windows":
        try:
            # PowerShell script for directory picker is taken from https://stackoverflow.com/questions/25690038/how-do-i-properly-use-the-folderbrowserdialog-in-powershell
            ps_script = (
                "Add-Type -AssemblyName System.Windows.Forms; "
                "$foldername = New-Object System.Windows.Forms.FolderBrowserDialog; "
                "$foldername.Description = 'Please select data folder'; "
                "$foldername.ShowNewFolderButton = $true; "
                "if ($foldername.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { "
                "  [Console]::Out.Write($foldername.SelectedPath) "
                "}"
            )
            # -NoProfile is used as customizations to PowerShell are not loaded. See https://stackoverflow.com/questions/74471387/why-is-noprofile-pwsh-parameter-considered-safer
            # Single Threaded Apartment (-STA) is needed for folder picker to work.
            result = subprocess.run(
                ["powershell", "-NoProfile", "-STA", "-Command", ps_script],
                capture_output=True,
                text=True,
                check=False,
            )
            return (result.stdout or "").strip() or None
        except Exception:  # pragma: no cover
            return None
    if system == "Linux":
        # Linux directory picker is taken from - https://askubuntu.com/questions/488350/how-do-i-prompt-users-with-a-gui-dialog-box-to-choose-file-directory-path-via-t
        zenity = shutil.which("zenity")
        if zenity:
            try:
                result = subprocess.run(
                    [
                        zenity,
                        "--file-selection",
                        "--directory",
                        "--title=Please select data folder",
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                return (result.stdout or "").strip() or None
            except Exception:
                return None
    return None


def update_data_folder():
    """Callback to open folder picker and update session state."""
    folder_path = pick_directory()
    if folder_path:
        st.session_state.data_root = folder_path
    else:
        st.toast("Folder selection cancelled.")


st.session_state.setdefault("data_root", "data")


st.text_input(
    "Data folder",
    help="Folder where downloads and CSVs are saved. Defaults to 'data'.",
    key="data_root",
)

st.button("Select Data Folder", on_click=update_data_folder, width="stretch")

try:
    resolved = os.path.abspath(os.path.expanduser(st.session_state.data_root))
    st.caption(f"Saving under: `{resolved}`")
except Exception:  # pragma: no cover
    raise  # pragma: no cover


st.subheader("Please select a Database to Search")

row1 = st.columns(2)
row2 = st.columns(2)
row3 = st.columns(2)
row4 = st.columns(2)


with row1[0]:
    if st.button("**AU DAEN**", key="daen", width="stretch"):
        st.success("AU DAEN selected")
        time.sleep(1)

        database_currently_searching = "AU DAEN"
        st.session_state["selected_database"] = database_currently_searching
        st.switch_page("pages/search_page_daen.py")

with row1[1]:
    if st.button("**DK DMA**", key="dma", width="stretch"):
        st.success("DK DMA selected")
        time.sleep(1)

        database_currently_searching = "DK DMA"
        st.session_state["selected_database"] = database_currently_searching
        st.switch_page("pages/search_page_dma.py")

with row2[0]:
    if st.button("**NL Lareb**", key="lareb", width="stretch"):
        st.success("NL Lareb selected")
        time.sleep(1)

        database_currently_searching = "NL LAREB"
        st.session_state["selected_database"] = database_currently_searching
        st.switch_page("pages/search_page_lareb.py")

with row2[1]:
    if st.button("**NZ MEDSAFE**", key="nzsmars", width="stretch"):
        st.success("NZ MEDSAFE selected")
        time.sleep(1)

        database_currently_searching = "NZ MEDSAFE"
        st.session_state["selected_database"] = database_currently_searching
        st.switch_page("pages/search_page_nzsmars.py")

with row3[0]:
    if st.button("**USA FAERS**", key="faers", width="stretch"):
        st.success("USA FAERS selected")
        time.sleep(1)

        database_currently_searching = "USA FAERS"
        st.session_state["selected_database"] = database_currently_searching
        st.switch_page("pages/search_page_faers.py")

with row3[1]:
    if st.button("**USA VAERS**", key="vaers", width="stretch"):
        st.success("USA VAERS selected")
        time.sleep(1)

        database_currently_searching = "USA VAERS"
        st.session_state["selected_database"] = database_currently_searching
        st.switch_page("pages/search_page_vaers.py")

with row4[0]:
    if st.button("**WHO VigiAccess**", key="vigiaccess", width="stretch"):
        st.success("WHO VigiAccess selected")
        time.sleep(1)

        database_currently_searching = "WHO VIGIACCESS"
        st.session_state["selected_database"] = database_currently_searching
        st.switch_page("pages/search_page_vigiaccess.py")

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
