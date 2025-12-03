"""
Scraper for FAERS using SeleniumBase.
"""

import os
import time
import warnings
from collections.abc import Callable
from typing import Any
from urllib.parse import urlparse

import pandas as pd
import requests
from seleniumbase import SB

warnings.filterwarnings("ignore")


def scrape_faers_sb(
    output_dir: str = "data/faers",
    headless: bool = True,
    callback: Callable[[dict], None] | None = None,
    num_retries: int = 5,
) -> pd.DataFrame:
    """
    Scrapes all available years and associated quarters from the FAERS
    website for which data is available.

    Parameters
    -----------
    output_dir: Directory to save CSV (default "data/faers").

    headless: bool
        Run the browser in headless mode (default True).

    callback : callable
        Callable to receive UI/status events, called with a dict.
        This is essential to show progress to user.

    Returns
    --------
    A DataFrame with columns ["Year", "Quarter"], representing the
    quarters in each year for which data is available.
    """

    def _emit(event_type: str, **kw: Any) -> None:  # pragma: no cover
        if callback:
            try:
                callback({"type": event_type, **kw})
            except Exception:  # pragma: no cover
                raise  # pragma: no cover

    os.makedirs(output_dir, exist_ok=True)

    url = "https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html"

    exceptions = []
    for attempt in range(num_retries):
        try:
            if attempt > 0:
                _emit(
                    "log",
                    message=f"Retrying... ({attempt + 1}/{num_retries})\n",
                )

            q_new = {}
            q_old = {}

            with SB(uc=True, headless=headless) as sb:
                _emit(
                    "log",
                    message=(f"Parsing FAERS website " f"(Attempt {attempt + 1})\n"),
                )
                try:
                    sb.activate_cdp_mode(url)
                except Exception as e:  # pragma: no cover
                    _emit("error", message=f"Failed to open site: {e}")
                    raise  # pragma: no cover

                sb.cdp.wait_for_element_visible("#accordion", timeout=30)
                sb.cdp.click("#accordion")

                year_elems1 = sb.cdp.find_elements(
                    "#accordion h4 a, #accordion .panel-title a"
                )
                years_new = [
                    e.text.strip() for e in year_elems1 if e.text and e.text.strip()
                ]
                delta_new = 50.0 / max(1, len(years_new))

                for i, year in enumerate(years_new, start=1):
                    try:
                        if i != 1:
                            sb.cdp.click(f'//*[@id="accordion"]/div[{i}]/div[1]/h4/a')
                            sb.sleep(0.4)

                        tbody_xpath = f'//*[@id="collapse{year}"]/div/div/table/tbody'
                        sb.cdp.wait_for_element_visible(tbody_xpath, timeout=30)
                        tbody = sb.cdp.find_element(tbody_xpath)
                        rows = tbody.query_selector_all("tr")
                        first_col = []
                        for row in rows:
                            tds = row.query_selector_all("td")
                            if not tds:
                                continue
                            cell = (tds[0].text or "").strip()
                            if cell and "ASCII" not in cell and "XML" not in cell:
                                first_col.append(cell)
                        q_new[year] = first_col
                        _emit("progress", delta=delta_new)
                    except Exception:  # pragma: no cover
                        raise  # pragma: no cover

                older_btn = '//*[@id="older_accordion"]/div/div[1]/h4/a'
                sb.cdp.wait_for_element_visible(older_btn, timeout=30)
                sb.cdp.click(older_btn)
                sb.sleep(0.6)

                years_xpath = '//*[@id="older_accordion_years"]//h4/a'
                sb.cdp.wait_for_element_visible(years_xpath, timeout=30)
                elements = sb.cdp.find_elements(years_xpath)
                years_old = [
                    el.text.strip() for el in elements if el.text and el.text.strip()
                ]
                delta_old = 50.0 / max(1, len(years_old))

                for i, year in enumerate(years_old, start=1):
                    try:
                        if i != 1:
                            sb.cdp.click(
                                f'//*[@id="older_accordion_years"]/div[{i}]/div[1]/h4/a'
                            )
                            sb.sleep(0.4)

                        collapse_id = (
                            f"collapse{year}-2" if year == "2012" else f"collapse{year}"
                        )
                        tbody_xpath = f'//*[@id="{collapse_id}"]/div/div/table/tbody'
                        sb.cdp.wait_for_element_visible(tbody_xpath, timeout=30)
                        tbody = sb.cdp.find_element(tbody_xpath)
                        rows = tbody.query_selector_all("tr")
                        first_col2 = []
                        for row in rows:
                            tds = row.query_selector_all("td")
                            if not tds:
                                continue
                            cell = (tds[0].text or "").strip()
                            if cell and "ASCII" not in cell and "XML" not in cell:
                                first_col2.append(cell)
                        q_old[year] = first_col2
                        _emit("progress", delta=delta_old)
                    except Exception:  # pragma: no cover
                        raise  # pragma: no cover

            merged = {}
            for y, qs in q_new.items():
                merged[y] = list(qs)
            for y, qs in q_old.items():
                if y in merged:
                    merged[y].extend(q for q in qs if q not in merged[y])
                else:
                    merged[y] = list(qs)

            rows = []
            for year, quarters in merged.items():
                for q in quarters:
                    rows.append({"Year": year, "Quarter": q})

            df = pd.DataFrame(rows, columns=["Year", "Quarter"]).reset_index(drop=True)

            if not df.empty and "Quarter" in df.columns:
                df["Quarter"] = (
                    df["Quarter"]
                    .astype(str)
                    .str.replace(r"(?i)\s*posted on.*$", "", regex=True)
                    .str.strip()
                )

            output_csv_path = os.path.join(output_dir, "faers_available_quarters.csv")
            df.to_csv(output_csv_path, index=False)

            try:
                df.attrs["faers_years_new_count"] = len(years_new)
                df.attrs["faers_years_old_count"] = len(years_old)
            except Exception:  # pragma: no cover
                raise  # pragma: no cover

            _emit(
                "log",
                message=f"Data saved to: {os.path.abspath(output_csv_path)}",
            )
            _emit("done")
            return df

        except Exception as e:  # pragma: no cover
            exceptions.append(e)
            _emit("log", message=f"Attempt {attempt + 1} failed with error: {e}.\n")
            time.sleep(20)
            continue

    _emit(
        "error",
        message=(
            f"All {num_retries} attempt(s) to scrape data failed. "
            "Please check the following:\n"
            "1. Ensure you have a stable internet connection.\n"
            "2. Verify that 'https://fis.fda.gov/' opens correctly in your browser.\n"
            "3. If these steps do not resolve the issue, please wait a while and retry. \n"
            "If problems persist, contact the developer at https://github.com/rmj3197/SurVigilance/issues "
            "for assistance.\n\n"
        ),
    )
    if exceptions:
        raise exceptions[-1]


def download_file(
    url: str,
    download_dir: str = "data/faers",
    timeout: int = 600,
    callback: Callable[[dict], None] | None = None,
    num_retries: int = 5,
) -> str:
    """
    Save a file from a direct link using requests module.

    Parameters
    -----------
    url: str
        Direct URL to the file.

    download_dir: str
        Directory where the file should be saved.

    timeout: int
        Max seconds to wait for the download (default 600s or 10 mins).

    callback: callable, optional
        Callable to receive UI/status events, called with a dict.
        This is essential to show progress to user.

    num_retries: int
        Number of retries for data scraping after which error is thrown (default 5).

    Returns
    --------
    Full path to the saved file as a string.
    """

    os.makedirs(download_dir, exist_ok=True)

    def _emit(evt: dict) -> None:
        if callback:
            try:
                callback(evt)
            except Exception:  # pragma: no cover
                raise  # pragma: no cover

    u = str(url)

    parsed = urlparse(u)
    filename = os.path.basename(parsed.path) or "downloaded_file"

    exceptions = []
    for attempt in range(num_retries):
        try:
            if attempt > 0:
                _emit(
                    {
                        "type": "log",
                        "message": f"Retrying download... ({attempt + 1}/{num_retries})\n",
                    }
                )

            with requests.get(u, stream=True, timeout=timeout) as r:
                r.raise_for_status()

                file_path = os.path.join(download_dir, filename)

                try:
                    total_bytes = int(
                        r.headers.get("Content-Length")
                        or r.headers.get("content-length")
                        or 0
                    )
                except Exception:  # pragma: no cover
                    total_bytes = 0

                _emit(
                    {
                        "type": "download_start",
                        "url": u,
                        "filename": filename,
                        "total_bytes": total_bytes,
                    }
                )

                downloaded = 0
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if not chunk:
                            continue
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_bytes > 0:
                            percent = int(downloaded * 100 / max(1, total_bytes))
                        else:
                            percent = None
                        _emit(
                            {
                                "type": "download_progress",
                                "downloaded_bytes": downloaded,
                                "total_bytes": total_bytes,
                                "percent": percent,
                                "filename": filename,
                            }
                        )

            _emit(
                {"type": "download_complete", "path": file_path, "filename": filename}
            )
            return file_path

        except Exception as e:  # pragma: no cover
            exceptions.append(e)
            _emit(
                {
                    "type": "error",
                    "message": f"Download attempt {attempt + 1} failed: {e}",
                    "url": u,
                }
            )
            time.sleep(20)  # Wait before retrying
            continue

    _emit(
        {
            "type": "error",
            "message": (
                f"All {num_retries} attempt(s) to download {url} failed. "
                "Please check your internet connection and the URL."
            ),
            "url": u,
        }
    )
    if exceptions:
        raise exceptions[-1]
