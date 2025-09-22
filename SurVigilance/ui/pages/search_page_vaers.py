import streamlit as st
import importlib
import os

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


try:
    vaers_module = importlib.import_module("scrapers.scrape_vaers")
    download_vaers_zip_sb = vaers_module.download_vaers_zip_sb
except Exception:
    download_vaers_zip_sb = None


st.set_page_config(page_title="VAERS", layout="wide")


st.session_state.setdefault("data_root", "data")
vaers_dir = os.path.join(
    os.path.expanduser(st.session_state.get("data_root", "data")), "vaers"
)


st.session_state.setdefault("selected_database", "VAERS")
st.session_state.setdefault("vaers_selected_years", set())

st.session_state.setdefault("_vaers_downloading", False)
st.session_state.setdefault("_vaers_total_files", 0)
st.session_state.setdefault("_vaers_completed_files", 0)
st.session_state.setdefault("_vaers_current_file_percent", 0)


heading = f"Download Page for {st.session_state['selected_database']} Database"
st.markdown(f"<h1 style='text-align: center;'>{heading}</h1>", unsafe_allow_html=True)
st.info(
    f"""
    How the VAERS data collection works:
    - Parses the VAERS yearly download page and lists all available years.
    - Shows the user a browser windows for attempting GUI CAPTCHA click for selected years for which data is to be downloaded.
    - Waits for the "Download File" control and captures the real file URL.
    - Reuses browser cookies in a requests session to stream the ZIP download.
    - One ZIP per selected year is saved to `{vaers_dir}/`.
    """
)

st.divider()

st.subheader("Select Years")
st.caption("Choose one or more years (1990-2025).")


years = list(range(2025, 1989, -1))


c1, c2 = st.columns([1, 1])
with c1:
    if st.button("Select All Years", width="stretch"):
        st.session_state["vaers_selected_years"] = set(map(str, years))
with c2:
    if st.button("Clear All", width="stretch"):
        st.session_state["vaers_selected_years"] = set()


num_cols = 6
cols = st.columns(num_cols)

selected = set(st.session_state.get("vaers_selected_years", set()))

for idx, y in enumerate(years):
    col = cols[idx % num_cols]
    key = f"vaers_year_{y}"
    with col:
        checked = str(y) in selected
        is_checked = st.checkbox(str(y), value=checked, key=key)
    if is_checked:
        selected.add(str(y))
    else:
        selected.discard(str(y))


st.session_state["vaers_selected_years"] = selected


st.divider()
if selected:
    st.info("Selected years: " + ", ".join(sorted(selected, reverse=True)))
else:
    st.info("No years selected yet.")


def vaers_zip_url(year: int) -> str:
    return f"https://vaers.hhs.gov/eSubDownload/index.jsp?fn={year}VAERSData.zip"


if selected:
    st.divider()
    st.subheader("Download Selected VAERS Zips")
    st.caption(f"Downloads are saved to `{vaers_dir}`.")

    selected_years_sorted = [int(y) for y in sorted(selected, reverse=True)]
    for y in selected_years_sorted:
        st.markdown(f"- {y} - `{y}VAERSData.zip`")

    total_files = len(selected_years_sorted)
    if (
        st.session_state.get("_vaers_downloading")
        and st.session_state.get("_vaers_total_files", 0) > 0
    ):
        completed = st.session_state.get("_vaers_completed_files", 0)
        current_pct = st.session_state.get("_vaers_current_file_percent", 0)
        overall_pct = int(
            (
                (completed + (current_pct / 100.0))
                / max(1, st.session_state["_vaers_total_files"])
            )
            * 100
        )
        btn_label = f"Downloading data {overall_pct}%"
        st.button(btn_label, width="stretch", disabled=True)
        st.progress(overall_pct)
        triggered = False
    else:
        btn_label = f"Download {total_files} file(s)"
        triggered = st.button(btn_label, width="stretch")

    if triggered:

        st.session_state["_vaers_downloading"] = True
        st.session_state["_vaers_total_files"] = total_files
        st.session_state["_vaers_completed_files"] = 0
        st.session_state["_vaers_current_file_percent"] = 0
        st.button("Downloading data", width="stretch", disabled=True)
        overall_bar = st.progress(0)
        successes = []
        failures = []

        for y in selected_years_sorted:
            fname = f"{y}VAERSData.zip"
            with st.status(f"Preparing {fname}...", expanded=True) as st_status:
                pbar = st.progress(0)
                st.session_state["_vaers_download_progress"] = 0
                try:

                    def cb(evt: dict) -> None:
                        et = evt.get("type")
                        if et == "download_start":
                            st_status.update(
                                label=f"Downloading {fname}...", state="running"
                            )
                            st.session_state["_vaers_current_file_percent"] = 0
                        elif et == "download_progress":
                            try:
                                pct = int(evt.get("percent", 0))
                            except Exception:
                                pct = st.session_state.get(
                                    "_vaers_download_progress", 0
                                )
                            pbar.progress(max(0, min(100, pct)))

                            st.session_state["_vaers_current_file_percent"] = max(
                                0, min(100, int(pct))
                            )

                            completed = st.session_state.get(
                                "_vaers_completed_files", 0
                            )
                            overall_pct = int(
                                (
                                    (
                                        completed
                                        + (
                                            st.session_state[
                                                "_vaers_current_file_percent"
                                            ]
                                            / 100.0
                                        )
                                    )
                                    / max(1, st.session_state["_vaers_total_files"])
                                )
                                * 100
                            )
                            overall_bar.progress(overall_pct)
                        elif et == "download_complete":
                            pbar.progress(100)
                            st.session_state["_vaers_current_file_percent"] = 100
                            completed = st.session_state.get(
                                "_vaers_completed_files", 0
                            )
                            overall_pct = int(
                                (
                                    (completed + 1)
                                    / max(1, st.session_state["_vaers_total_files"])
                                )
                                * 100
                            )
                            overall_bar.progress(min(100, overall_pct))

                    path = download_vaers_zip_sb(
                        y,
                        download_dir=vaers_dir,
                        timeout=600,
                        callback=cb,
                        headless=False,
                    )

                    pbar.progress(100)
                    st_status.update(label=f"Downloaded {fname}", state="complete")
                    successes.append(path)

                    st.session_state["_vaers_completed_files"] = (
                        int(st.session_state.get("_vaers_completed_files", 0)) + 1
                    )
                    st.session_state["_vaers_current_file_percent"] = 0
                except Exception as e:
                    st_status.update(label=f"Failed {fname}", state="error")
                    st.error(f"{fname}: {e}")
                    failures.append((fname, str(e)))
                finally:

                    pct = st.session_state.get("_vaers_download_progress", 0)
                    pbar.progress(max(0, min(100, int(pct))))

        if successes:
            st.success(f"Downloaded {len(successes)} file(s) to {vaers_dir}")
            try:
                st.toast("VAERS download(s) complete")
            except Exception:
                pass
            try:
                overall_bar.progress(100)
            except Exception:
                pass
        if failures:
            st.error(f"Failed {len(failures)} file(s)")
            for fname, msg in failures:
                st.error(f"{fname}: {msg}")

        st.session_state["_vaers_downloading"] = False


if st.button("Go Back to Homepage", width="stretch"):
    st.switch_page("_app.py")
