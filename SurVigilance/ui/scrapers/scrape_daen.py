"""
Scraper for DAEN (TGA) using SeleniumBase.
"""

import os
import shutil
import time
from collections.abc import Callable
from typing import Any

import pandas as pd
from selenium.webdriver.common.keys import Keys
from seleniumbase import SB


def scrape_daen_sb(
    medicine: str,
    output_dir: str = "data/daen",
    callback: Callable[[dict], None] | None = None,
    headless: bool = True,
    fallback_wait: int = 120,
    num_retries: int = 3,
) -> pd.DataFrame:  # pragma: no cover
    """
    Scrapes the reported MedDRA Preferred Terms and counts for a given medicine
    from the Australian DAEN database.

    Parameters
    -----------
    medicine: str
        Drug/medicine name to search.

    output_dir: str
        Directory to save the Excel (.xlsx) data file (default "data/daen").

    callback: callable, optional
        Callable to receive UI/status events, called with a dict.
        This is essential to show progress to user.

    headless: bool
        Run the browser in headless mode (default True).

    fallback_wait: int
        Seconds to wait for the browser download to finish in its default
        folder before attempting to move it to `output_dir`.

    num_retries: int
        Number of retries for data scraping after which error is thrown (default 3).

    Returns
    --------
    A dataFrame of the downloaded data.
    """

    def _emit(event_type: str, **kw: Any) -> None:  # pragma: no cover
        if callback:
            try:
                callback({"type": event_type, **kw})
            except Exception:  # pragma: no cover
                raise  # pragma: no cover

    med = (medicine or "").strip()
    if not med:
        _emit("error", message="Medicine is required for DAEN scrape")
        raise ValueError("medicine is required")  # pragma: no cover

    os.makedirs(output_dir, exist_ok=True)

    exceptions = []
    for attempt in range(num_retries):
        try:
            if attempt > 0:
                _emit("log", message=f"Retrying... ({attempt + 1}/{num_retries})\n")

            url = "https://daen.tga.gov.au/medicines-search/"
            _emit(
                "log",
                message=f"Opening DAEN (TGA) medicines search (Attempt {attempt + 1})\n",
            )

            with SB(uc=True, headless=headless) as sb:
                sb.open(url)

                try:
                    sb.scroll_into_view("input#termsCondition")
                    sb.click_if_visible("input#termsCondition", timeout=5)
                except Exception:  # pragma: no cover
                    pass

                outer_iframe = "div#reportContainer iframe"
                sb.wait_for_element_present(outer_iframe, timeout=60)
                with sb.frame_switch(outer_iframe):
                    inner_iframe = 'iframe[name="visual-sandbox"]'
                    sb.wait_for_element_present(inner_iframe, timeout=60)
                    with sb.frame_switch(inner_iframe):
                        search_box = 'input[placeholder*="Search"]'
                        sb.wait_for_element(search_box, timeout=60)
                        sb.clear(search_box)
                        sb.type(search_box, med)
                        sb.press_keys(search_box, Keys.ENTER)

                    try:
                        sb.wait_for_element(
                            '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[34]/transform'
                        )
                        sb.sleep(10)
                        sb.scroll_into_view(
                            '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[34]/transform'
                        )

                        row = '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[34]/transform/div/div[3]/div/div/visual-modern/div/div/div[2]/div[1]/div[2]'
                        sb.click(row)
                        sb.sleep(1)

                        options_menu = '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[34]/transform/div/visual-container-header/div/div/div/visual-container-options-menu'
                        sb.click(options_menu)
                        sb.sleep(1)

                        export_btn = '//*[@id="0"]'
                        sb.click(export_btn)
                        sb.sleep(1)

                        confirm_btn = '//*[@id="mat-mdc-dialog-0"]/div/div/export-data-dialog/mat-dialog-actions/button[1]'
                        sb.click(confirm_btn)
                    except Exception as e:  # pragma: no cover
                        _emit("log", message=f"Export initiation failed: {e}")
                        raise  # pragma: no cover

                    sb.sleep(5)

                try:
                    stray_dir = os.path.join(os.getcwd(), "downloaded_files")
                    os.makedirs(output_dir, exist_ok=True)

                    end_time = time.time() + max(0, int(fallback_wait))
                    last_candidate = None
                    while time.time() < end_time:
                        if os.path.isdir(stray_dir):
                            entries = [
                                os.path.join(stray_dir, f)
                                for f in os.listdir(stray_dir)
                                if not f.endswith(".crdownload")
                                and not f.startswith(".")
                            ]
                            if entries:
                                entries.sort(
                                    key=lambda p: os.path.getmtime(p), reverse=True
                                )
                                last_candidate = entries[0]
                                break
                        time.sleep(1)

                    if not last_candidate or not os.path.isfile(last_candidate):
                        _emit(
                            "error",
                            message=(
                                "No completed download detected in 'downloaded_files' within "
                                f"{fallback_wait}s."
                            ),
                        )
                        raise RuntimeError(
                            "DAEN export file not detected"
                        )  # pragma: no cover

                    base_name = os.path.basename(last_candidate)
                    _root, ext = os.path.splitext(base_name)
                    if not ext:
                        ext = ".xlsx"
                    target_name = f"{med}_daen_export{ext}"
                    target_path = os.path.join(output_dir, target_name)

                    if os.path.isfile(target_path):
                        try:
                            os.remove(last_candidate)
                        except Exception:
                            raise  # pragma: no cover
                    else:
                        shutil.move(last_candidate, target_path)

                    _emit("download_complete", path=target_path, filename=target_name)

                    try:
                        # The DAEN export is expected to be an Excel .xlsx file.
                        df = pd.read_excel(target_path, engine="openpyxl")
                        return df
                    except Exception as e:  # pragma: no cover
                        _emit("log", message=f"Failed to read exported file: {e}")
                        raise  # pragma: no cover

                except Exception:  # pragma: no cover
                    raise  # pragma: no cover
        except Exception as e:
            exceptions.append(e)
            _emit("log", message=f"Attempt {attempt + 1} failed with error: {e}.\n")
            time.sleep(2)
            continue

    _emit(
        "error",
        message=(
            f"All {num_retries} attempt(s) to scrape data for {medicine} failed. "
            "Please check the following:\n"
            "1. Ensure you have a stable internet connection.\n"
            "2. Verify that 'https://daen.tga.gov.au/medicines-search/' opens correctly in your Chrome browser.\n"
            "3. If these steps do not resolve the issue, please wait a while and retry. \n"
            "If problems persist, contact the developer at https://github.com/rmj3197/SurVigilance/issues "
            "for assistance.\n\n"
        ),
    )
    if exceptions:
        raise exceptions[-1]
