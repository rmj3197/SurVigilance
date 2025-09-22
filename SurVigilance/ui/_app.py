"""
This script is the entry point of the streamlit application.
"""

import os
import platform
import shutil
import subprocess
import time

import streamlit as st

st.set_page_config(
    page_title="SurVigilance: The Pharmacovigilance Data Mart", layout="wide"
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


st.subheader("Storage")

st.session_state.setdefault("data_root", "data")


current_root = st.session_state.get("data_root", "data")
data_root_input = st.text_input(
    "Data folder",
    help="Folder where downloads and CSVs are saved. Defaults to 'data'.",
    value=current_root,
    key="data_root_input",
)

st.session_state["data_root"] = data_root_input or "data"

# need to take out the visual directory picker from testing, as CI tools would fail.
if st.button("Select Data Folder", width="stretch"):  # pragma: no cover

    def pick_directory():
        system = platform.system()

        if system == "Darwin":  # Handles the data directory picker for macOS
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
                path = (result.stdout or "").strip()
                return path or None
            except Exception:
                return None

        if system == "Windows":
            try:
                # Powershell script for directory picker is taken from https://stackoverflow.com/questions/25690038/how-do-i-properly-use-the-folderbrowserdialog-in-powershell
                ps_script = (
                    "Add-Type -AssemblyName System.Windows.Forms; "
                    "$foldername = New-Object System.Windows.Forms.FolderBrowserDialog; "
                    "$foldername.Description = 'Please select data folder'; "
                    "$foldername.ShowNewFolderButton = $true; "
                    "if ($foldername.ShowDialog() -eq OK) { "
                    "  [Console]::Out.Write($foldername.SelectedPath) "
                    "}"
                )
                # -Noprofile is used as customizations to poweshell are not loaded. See https://stackoverflow.com/questions/74471387/why-is-noprofile-pwsh-parameter-considered-safer
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_script],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                path = (result.stdout or "").strip()
                return path or None
            except Exception:
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
                    path = (result.stdout or "").strip()
                    return path or None
                except Exception:
                    return None

        return None

    folder = pick_directory()
    if folder:
        st.session_state["data_root"] = folder
        st.toast("Data folder updated")
        st.rerun()
    else:
        st.warning("Folder picker unavailable here. Please type the path manually.")

try:
    resolved = os.path.abspath(
        os.path.expanduser(st.session_state.get("data_root", "data"))
    )
    st.caption(f"Saving under: `{resolved}`")
except Exception:
    pass

st.subheader("Please select a Database to Search")


# Organize the datasets in a 2 x 2 grid like fashion
row1 = st.columns(2)
row2 = st.columns(2)


with row1[0]:
    if st.button("**VigiAccess**", key="vigiaccess", width="stretch"):
        st.success("WHO VigiAccess selected")
        time.sleep(1)

        database_currently_searching = "VIGIACCESS"
        st.session_state["selected_database"] = database_currently_searching
        st.switch_page("pages/search_page_vigiaccess.py")


with row1[1]:
    if st.button("**FAERS**", key="faers", width="stretch"):
        st.success("FAERS selected")
        time.sleep(1)

        database_currently_searching = "FAERS"
        st.session_state["selected_database"] = database_currently_searching
        st.switch_page("pages/search_page_faers.py")

with row2[0]:
    if st.button("**VAERS**", key="vaers", width="stretch"):
        st.success("VAERS selected")
        time.sleep(1)

        database_currently_searching = "VAERS"
        st.session_state["selected_database"] = database_currently_searching
        st.switch_page("pages/search_page_vaers.py")

with row2[1]:
    if st.button("**LAREB**", key="lareb", width="stretch"):
        st.success("LAREB selected")
        time.sleep(1)

        database_currently_searching = "LAREB"
        st.session_state["selected_database"] = database_currently_searching
        st.switch_page("pages/search_page_lareb.py")
