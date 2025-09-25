import importlib
import os
import re
import sys
from pathlib import Path
from typing import Optional

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # pragma: no cover
    sys.path.insert(0, str(ROOT))


# Use importlib to import functions needed
try:
    scrape_faers_module = importlib.import_module("scrapers.scrape_faers")
    scrape_faers_sb = scrape_faers_module.scrape_faers_sb
    download_file = scrape_faers_module.download_file

    mapping_module = importlib.import_module("scrapers.faers_links")
    faers_ascii_url = mapping_module.faers_ascii_url

    QUARTER_MONTHS = mapping_module.QUARTER_MONTHS
    QUARTER_LABELS = mapping_module.QUARTER_LABELS
except Exception as e:  # pragma: no cover
    st.error(f"Failed to import the FAERS scraper: {e}")
    st.stop()


st.set_page_config(
    page_title="Data access page for FAERS",
    layout="wide",
    page_icon="SurVigilance/ui/assets/survigilance_sticker.ico",
)


st.session_state.setdefault(
    "data_root", "data"
)  # Where we keep downloaded data by default
faers_dir = os.path.join(
    os.path.expanduser(st.session_state["data_root"]), "faers"
)  # Subfolder for FAERS
faers_dir_display = os.path.abspath(faers_dir)


st.session_state.setdefault("selected_database", "FAERS")


heading = f"Download Page for {st.session_state['selected_database']} Database"
st.markdown(f"<h1 style='text-align: center;'>{heading}</h1>", unsafe_allow_html=True)
st.info(
    f"""
    How the FAERS data collection works:
    - Parses the FDA FAERS website [https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html](https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html) for available quarters per year.
    - User selects the quarters to download the data, and initiates download using download button.
    - ZIP ASCII Files for selected quarters are saved under `{faers_dir}/`.
    """
)
st.divider()


fetch = st.button("List all FAERS years and available quarters", width="stretch")

st.divider()


progress = st.empty()  # Progress bar area
log_box = st.empty()  # Streaming logs and/or info
error_box = st.empty()  # For any errors encountered
status_box = st.empty()  # Overall status messages
checkboxes_box = st.empty()  # Place where the quarter selection checkboxes live


st.session_state.setdefault(
    "faers_df", None
)  # Holds the dataframe of available year/quarter rows


_progress_state = {"value": 0.0}  # Track progress across events in a simple dict


def streamlit_callback(event: dict) -> None:  # pragma: no cover
    """Simple callback used by the scraper to update the UI.

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


if fetch:
    # Reset UI areas and start the scraping process to list years and quarters.
    _progress_state["value"] = 0.0
    progress.progress(0)
    log_box.empty()
    error_box.empty()
    status_box.info("Parsing the FAERS webpage")
    checkboxes_box.empty()

    try:
        df = scrape_faers_sb(
            output_dir=faers_dir, headless=True, callback=streamlit_callback
        )

        try:
            new_count = df.attrs.get("faers_years_new_count")
            old_count = df.attrs.get("faers_years_old_count")
            if isinstance(new_count, int) and isinstance(old_count, int):
                log_box.info(f"Found data for {new_count + old_count} years.")
        except Exception:  # pragma: no cover
            raise

        if df is not None and not df.empty:
            st.session_state["faers_df"] = df
        else:
            st.session_state["faers_df"] = None

    except Exception as e:  # pragma: no cover
        error_box.error(f"Data collection failed: {e}")
        status_box.error("Data collection aborted.")


df = st.session_state.get("faers_df")  # Dataframe of year/quarter rows discovered above
if df is not None:
    with checkboxes_box.container():
        st.subheader(
            "Select Quarters by Year"
        )  # Let the user pick quarters to download

        base_df = df[["Year", "Quarter"]].copy()
        base_df["Year"] = base_df["Year"].astype(str)
        base_df["Quarter"] = base_df["Quarter"].astype(str)

        year_to_quarters = {}
        for y in sorted(base_df["Year"].unique(), reverse=True):
            qs = base_df.loc[base_df["Year"] == y, "Quarter"].tolist()[::-1]
            year_to_quarters[str(y)] = qs

        sel_key = "faers_selected_quarters"
        if sel_key not in st.session_state:
            st.session_state[sel_key] = {}

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("Select All Quarters"):
                st.session_state[sel_key] = {
                    y: set(qs) for y, qs in year_to_quarters.items()
                }
        with c2:
            if st.button("Clear All"):
                st.session_state[sel_key] = {y: set() for y in year_to_quarters.keys()}

        # Start from existing selections and update as the user clicks checkboxes
        updated = {
            y: set(st.session_state[sel_key].get(y, set()))
            for y in year_to_quarters.keys()
        }

        for y in year_to_quarters.keys():
            st.markdown(f"**{y}**")
            q_cols = st.columns(4)
            for idx, q in enumerate(year_to_quarters[y]):
                col = q_cols[idx % len(q_cols)]
                q_key = f"faers_q_{y}_{q.replace(' ', '_').replace('/', '_').replace('-', '_')}"
                with col:
                    checked = q in updated[y]
                    is_checked = st.checkbox(q, value=checked, key=q_key)
                if is_checked:
                    updated[y].add(q)
                else:
                    updated[y].discard(q)
            st.markdown("")

        st.session_state[sel_key] = updated  # Save back the latest selections

        # show whih quarters are selected each year to user.
        summary_parts = []
        for y in sorted(updated.keys(), reverse=True):
            if updated[y]:
                summary_parts.append(f"{y}: [" + ", ".join(sorted(updated[y])) + "]")
        if summary_parts:
            st.info("Selected " + "; ".join(summary_parts))
        else:
            st.info("No quarters selected yet.")

        # Turn the selection dict into a flat list of (year, quarter_label)
        selected_list = []
        for y, qs in updated.items():
            for q in qs:
                selected_list.append((str(y), str(q)))

        if selected_list:
            # Trying to convert a label like "Jan-Mar" into Q1.
            def _infer_quarter_number(label: str) -> Optional[int]:
                try:
                    label_lower = (label or "").lower()

                    m = re.search(r"\bq\s*([1-4])\b", label_lower)
                    if m:
                        return int(m.group(1))

                    for qnum, qlab in QUARTER_LABELS.items():
                        if qlab.lower() in label_lower:
                            return int(qnum)

                except Exception:  # pragma: no cover
                    raise
                return None

            # Build a list of objects containing year, quarter, and the URL to download
            selections_with_urls = []
            for y, qlabel in selected_list:
                try:
                    qnum = _infer_quarter_number(qlabel)
                    if qnum is None:
                        continue
                    year_int = int(str(y).strip())
                    display_url = faers_ascii_url(
                        year_int, qnum
                    )  # Expected ASCII ZIP URL
                    filename = (
                        display_url.split("/")[-1] or f"faers_{year_int}_q{qnum}.zip"
                    )
                    selections_with_urls.append(
                        {
                            "year": year_int,
                            "quarter": qnum,
                            "label": str(qlabel),
                            "url": display_url,
                            "filename": filename,
                        }
                    )
                except Exception:  # pragma: no cover
                    raise

            if selections_with_urls:
                st.divider()
                st.subheader(
                    "Download Selected FAERS ASCII ZIPs"
                )  # Download chosen files
                st.caption(f"Downloaded data will be saved to `{faers_dir_display}`.")

                for item in selections_with_urls:
                    y = item["year"]
                    label = item["label"]
                    fname = item["filename"]
                    st.markdown(
                        f"- {y} - {label} - `{fname}`"
                    )  # Show what will be downloaded

                download_clicked = st.button(
                    f"Download {len(selections_with_urls)} file(s)",
                    width="stretch",
                )  # Start the download process

                download_status_area = st.empty()  # Per-file progress & logs
                download_overall_status = st.empty()  # Overall success/failure summary

                if download_clicked:
                    successes = []  # Paths of files that were downloaded
                    failures = []  # Any (filename, error) pairs that failed

                    with download_status_area.container():
                        for item in selections_with_urls:
                            url = item["url"]
                            fname = item["filename"]

                            with st.status(
                                f"Preparing {fname}", expanded=True
                            ) as st_status:
                                pbar = st.progress(0)  # Progress for this single file

                                def per_file_callback(
                                    evt: dict,
                                ) -> None:  # pragma: no cover
                                    # Handle per-file download progress/logs and errors.
                                    et = evt.get("type")
                                    if et == "download_start":
                                        st_status.update(
                                            label=f"Downloading {evt.get('filename', fname)}",
                                            state="running",
                                        )
                                    elif et == "download_progress":
                                        pct = evt.get("percent")
                                        if isinstance(pct, int):
                                            pbar.progress(max(0, min(100, pct)))
                                    elif et == "download_complete":
                                        pbar.progress(100)
                                        st_status.update(
                                            label=f"Downloaded {fname}",
                                            state="complete",
                                        )
                                    elif et == "error":
                                        st_status.update(
                                            label=f"Failed {fname}", state="error"
                                        )
                                        error_box.error(
                                            f"{fname}: {evt.get('message')}"
                                        )
                                    elif et == "log":
                                        st_status.write(evt.get("message", ""))

                                try:
                                    path = download_file(
                                        url=url,
                                        download_dir=faers_dir,
                                        callback=per_file_callback,
                                    )
                                    successes.append(path)
                                except Exception as _e:  # pragma: no cover
                                    failures.append((fname, str(_e)))

                    with download_overall_status.container():
                        if successes:
                            st.success(
                                f"Downloaded {len(successes)} file(s) to {faers_dir_display}"
                            )
                            try:
                                st.toast(
                                    "FAERS download(s) complete"
                                )  # Small confirmation after download is complete
                            except Exception:  # pragma: no cover
                                raise
                        if failures:  # pragma: no cover
                            st.error(f"Failed {len(failures)} file(s)")
                            for fname, msg in failures:
                                st.error(f"{fname}: {msg}")

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
