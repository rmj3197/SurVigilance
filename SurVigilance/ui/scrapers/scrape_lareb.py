"""
Scraper for LAREB using SeleniumBase.
"""

import os
import time
import warnings
from collections.abc import Callable
from typing import Any

import pandas as pd
from seleniumbase import SB

warnings.filterwarnings("ignore")


def scrape_lareb_sb(
    medicine: str,
    output_dir: str = "data/lareb",
    callback: Callable[[dict], None] | None = None,
    headless: bool = True,
    num_retries: int = 3,
) -> pd.DataFrame:
    """
    Scrapes the reported MedDRA Preferred Terms and counts for a given medicine from Lareb.

    Parameters
    -----------
    medicine : str
        Drug/medicine name to search.

    output_dir : str
        Directory to save CSV (default "data/lareb").

    callback : callable
        Callable to receive UI/status events, called with a dict.
        This is essential to show progress to user.

    headless: bool
        Run the browser in headless mode (default True).

    num_retries: int
        Number of retries for data scraping after which error is thrown (default 3).

    Returns
    --------
    A dataframe with columns ["PT", "Count"].
    """

    def _emit(event_type: str, **kw: Any) -> None:
        if callback:
            try:
                callback({"type": event_type, **kw})
            except Exception:
                raise  # pragma: no cover

    med = (medicine or "").strip()
    if not med:
        _emit("error", message="Medicine is required for Lareb scrape")
        raise ValueError("medicine is required")  # pragma: no cover

    os.makedirs(output_dir, exist_ok=True)

    exceptions = []
    for attempt in range(num_retries):
        try:
            if attempt > 0:
                _emit("log", message=f"Retrying... ({attempt + 1}/{num_retries})\n")

            with SB(uc=True, headless=headless) as sb:
                _emit("log", message=f"Parsing lareb.nl (Attempt {attempt+1})\n")
                try:
                    url = "https://www.lareb.nl/en"
                    sb.activate_cdp_mode(url)
                    sb.sleep(2)
                except Exception as e:  # pragma: no cover
                    _emit("error", message=f"Failed to open site: {e}")
                    raise  # pragma: no cover

                try:
                    sb.sleep(1)
                    sb.scroll_into_view("input.input-search")
                    sb.sleep(1)
                    if sb.cdp.is_element_present("input.input-search"):
                        sb.cdp.type("input.input-search", med)
                    else:
                        sb.cdp.type('[class*="input-search"]', med)
                    sb.sleep(2)
                except Exception as e:  # pragma: no cover
                    _emit("log", message=f"Error encountered while searching: {e}")
                    raise  # pragma: no cover

                try:
                    sb.sleep(2)
                    sb.cdp.wait_for_element_visible(
                        'div.autocomplete-suggestion[data-index="0"]', timeout=30
                    )
                except Exception as e:  # pragma: no cover
                    _emit(
                        "error",
                        message=(
                            "No autocomplete suggestion appeared - the drug may not exist "
                            f"on Lareb: {med}. Details: {e}"
                        ),
                    )

                if sb.cdp.is_element_present(
                    'div.autocomplete-suggestion[data-index="0"]'
                ):
                    sb.sleep(1)
                    sb.cdp.click_if_visible(
                        'div.autocomplete-suggestion[data-index="0"]'
                    )
                    sb.sleep(2)

                try:
                    sb.sleep(1.5)
                    sb.cdp.click("#search")
                    sb.sleep(3)
                except Exception as e:  # pragma: no cover
                    _emit("error", message=f"Couldn't click search button: {e}")
                    raise  # pragma: no cover

                try:
                    sb.cdp.wait_for_element_visible("#registrationsTab", timeout=600)
                    sb.sleep(1.5)
                    sb.cdp.wait_for_element_visible(
                        "#registrationsTab tbody tr", timeout=600
                    )
                    rows = sb.cdp.find_elements("#registrationsTab tbody tr")
                    sb.sleep(2)
                except Exception as e:  # pragma: no cover
                    _emit("error", message=f"Couldn't find table: {e}")
                    raise  # pragma: no cover

                expanded_texts = []
                total_rows = len(rows) if rows else 0

                for i, row in enumerate(rows, start=1):
                    try:
                        sb.sleep(1)
                        expander = row.query_selector("td > div:nth-of-type(1)")
                        if expander:
                            expander.click()
                            sb.sleep(1.5)

                        details = row.query_selector("td > div:nth-of-type(2)")
                        if details:
                            for _ in range(10):
                                if details.text.strip():
                                    break
                                sb.sleep(0.3)

                            expanded_texts.append(details.text.strip())
                        else:
                            expanded_texts.append("")

                        if total_rows:
                            _emit("progress", delta=100.0 / total_rows)

                    except Exception as e:  # pragma: no cover
                        msg = f"Row {i}: expand failed: {e}"
                        _emit("error", message=msg)
                        expanded_texts.append("")

                sb.sleep(2)

                data = []
                for idx, text_block in enumerate(expanded_texts):
                    if not text_block:
                        continue
                    for line in text_block.split("\n"):
                        try:
                            condition, count = line.rsplit(":", 1)
                            data.append(
                                {"PT": condition.strip(), "Count": int(count.strip())}
                            )
                        except ValueError:  # pragma: no cover
                            _emit(
                                "log",
                                message=f"Skipping malformed line in group {idx + 1}: {line}",
                            )

                df = pd.DataFrame(data).reset_index(drop=True)

                target_name = f"{med}_lareb_adrs.csv"
                output_csv_path = os.path.join(output_dir, target_name)
                try:
                    sb.sleep(1)
                    df.to_csv(output_csv_path, index=False)
                    _emit(
                        "log",
                        message=f"Data saved to: {os.path.abspath(output_csv_path)}",
                    )
                    _emit(
                        "download_complete",
                        path=output_csv_path,
                        filename=target_name,
                    )
                except Exception as e:  # pragma: no cover
                    _emit("error", message=f"Failed to save CSV: {e}")

                _emit("done")
                return df
        except Exception as e:
            exceptions.append(e)
            _emit("log", message=f"Attempt {attempt + 1} failed.\n")
            time.sleep(2)
            continue

    _emit(
        "error",
        message=(
            f"All {num_retries} attempt(s) to scrape data for {medicine} failed. "
            "Please check the following:\n"
            "1. Ensure you have a stable internet connection.\n"
            "2. Verify that 'https://www.lareb.nl/en' opens correctly in your Chrome browser.\n"
            "3. If these steps do not resolve the issue, please wait a while and retry. \n"
            "If problems persist, contact the developer at https://github.com/rmj3197/SurVigilance/issues "
            "for assistance.\n\n"
        ),
    )
    if exceptions:
        raise exceptions[-1]
