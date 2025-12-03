"""
Scraper for NZ MEDSAFE (Suspected Medicine Adverse Reaction Search (SMARS)) using SeleniumBase.
"""

import os
import time
import warnings
from collections.abc import Callable
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup
from seleniumbase import SB

warnings.filterwarnings("ignore")


def scrape_medsafe_sb(
    searching_for: str,
    drug_vaccine: str,
    output_dir: str = "data/nzmedsafe",
    callback: Callable[[dict], None] | None = None,
    headless: bool = True,
    num_retries: int = 5,
) -> pd.DataFrame:
    """
    Scrapes NZ Medsafe database for a given medicine or vaccine, for System Organ Class (SOC), PTs and associated count.

    Parameters
    -----------
    searching_for : str
        Either "medicine" or "vaccine".

    drug_vaccine : str
        The drug or vaccine name to search for.

    output_dir : str
        Directory to save CSV (default "data/nzmedsafe").

    callback : callable
        Callable to receive UI/status events, called with a dict.
        This is essential to show progress to user.

    headless : bool
        Run the browser headless (default True).

    num_retries: int
        Number of retries for data scraping after which error is thrown (default 5).

    Returns
    --------
    A dataframe with columns ["SOC", "PT", "Count"].
    """

    def _emit(event_type: str, **kw: Any) -> None:  # pragma: no cover
        if callback:
            try:
                callback({"type": event_type, **kw})
            except Exception:  # pragma: no cover
                raise  # pragma: no cover

    def parse_table(html: str):
        soup = BeautifulSoup(html, "html.parser")
        headers = [th.get_text(strip=True) for th in soup.find_all("th")]
        data, current_soc = [], None
        for row in soup.find_all("tr")[1:]:  # skip header
            cols = row.find_all("td")
            if len(cols) == 3:
                current_soc = cols[0].get_text(strip=True)
                reaction = cols[1].get_text(strip=True)
                reports = cols[2].get_text(strip=True)
            elif len(cols) == 2:
                reaction = cols[0].get_text(strip=True)
                reports = cols[1].get_text(strip=True)
            else:
                continue
            data.append(
                {headers[0]: current_soc, headers[1]: reaction, headers[2]: reports}
            )
        return data, headers

    os.makedirs(output_dir, exist_ok=True)

    exceptions = []
    for attempt in range(num_retries):
        try:
            if attempt > 0:
                _emit("log", message=f"Retrying... ({attempt + 1}/{num_retries})\n")

            url = "https://www.medsafe.govt.nz/Projects/B1/ADRSearch.asp"

            with SB(uc=True, headless=headless) as sb:
                _emit(
                    "log", message=f"Parsing medsafe.govt.nz (Attempt {attempt + 1})\n"
                )
                sb.activate_cdp_mode(url)

                sb.wait_for_ready_state_complete()

                try:
                    if sb.cdp.is_element_present('//*[@id="Accept"]'):
                        sb.cdp.click('//*[@id="Accept"]')
                        sb.sleep(2)
                        sb.wait_for_ready_state_complete()
                except Exception as e:  # pragma: no cover
                    _emit("log", message=f"Cookie/terms click skipped or failed: {e}")

                # Select medicine type
                try:
                    search_type = (searching_for or "medicine").strip().lower()
                    if search_type == "vaccine":
                        sb.cdp.select_if_unselected(
                            '//*[@id="MainContent_MedicineType_0"]'
                        )
                        sb.wait_for_ready_state_complete()
                    else:
                        sb.cdp.select_if_unselected(
                            '//*[@id="MainContent_MedicineType_1"]'
                        )
                        sb.wait_for_ready_state_complete()
                    sb.sleep(5)
                except Exception as e:  # pragma: no cover
                    _emit("log", message=f"Failed setting medicine type: {e}")
                    raise  # pragma: no cover

                # Search text
                try:
                    if sb.cdp.is_element_visible('//*[@id="MainContent_TextToFind"]'):
                        sb.cdp.type(
                            '//*[@id="MainContent_TextToFind"]', str(drug_vaccine)
                        )
                        sb.sleep(1.5)
                        sb.cdp.click('//*[@id="MainContent_ButtonFind"]')
                        sb.sleep(2.0)
                        sb.wait_for_ready_state_complete()
                except Exception as e:  # pragma: no cover
                    _emit("error", message=f"Failed typing/searching for term: {e}")
                    raise  # pragma: no cover

                # Check for site error message in case of no ingredient match
                try:
                    if sb.cdp.is_element_present('//*[@id="MainContent_LabelErrors"]'):
                        msg = sb.cdp.get_text('//*[@id="MainContent_LabelErrors"]')
                        if (msg or "").strip():
                            _emit("error", message=msg)
                            raise RuntimeError(msg)  # pragma: no cover
                except Exception:  # pragma: no cover
                    raise  # pragma: no cover

                # Choose summary report type
                try:
                    sb.cdp.select_if_unselected('//*[@id="MainContent_ReportType_1"]')
                    sb.cdp.click('//*[@id="MainContent_ButtonSearch"]')
                    sb.sleep(1)
                    sb.wait_for_ready_state_complete()
                except Exception as e:  # pragma: no cover
                    _emit("error", message=f"Failed to initiate results search: {e}")
                    raise  # pragma: no cover

                # Find number of pages
                num_pages = 1
                try:
                    pager_table_xpath = (
                        '//*[@id="MainContent_GridSummary"]/tbody/tr[last()]/td/table'
                    )
                    if sb.cdp.is_element_present(pager_table_xpath):
                        table_el = sb.cdp.find_element(pager_table_xpath)
                        row_el = table_el.query_selector(
                            "tbody > tr"
                        ) or table_el.query_selector("tr")
                        num_pages = max(1, len(row_el.query_selector_all("td")))
                except Exception:  # pragma: no cover
                    num_pages = 1

                _emit("log", message=f"Pages detected: {num_pages}")

                data_rows = []

                def scrape_current_page():
                    table = sb.cdp.find_element(
                        '//*[@id="MainContent_GridSummary"]/tbody'
                    )
                    r = table.get_attribute("outerHTML")
                    page_rows, _headers = parse_table(r)
                    return page_rows

                # Progress per page
                delta = 100.0 / float(max(1, num_pages))

                for page in range(1, num_pages + 1):
                    try:
                        if page > 1:
                            sb.cdp.click(
                                f'//*[@id="MainContent_GridSummary"]/tbody/tr[last()]/td/table/tbody/tr/td[{page}]/a'
                            )
                            sb.sleep(0.8)
                            sb.wait_for_ready_state_complete()
                        data_rows.extend(scrape_current_page())
                        _emit("progress", delta=delta)
                    except Exception as e:  # pragma: no cover
                        _emit(
                            "log", message=f"Page {page}: failed to collect rows: {e}"
                        )

                df = pd.DataFrame(data_rows)
                if not df.empty:
                    cols = list(df.columns)
                    rename_map = {}
                    if len(cols) >= 1:
                        rename_map[cols[0]] = "SOC"
                    if len(cols) >= 2:
                        rename_map[cols[1]] = "PT"
                    if len(cols) >= 3:
                        rename_map[cols[2]] = "Count"
                    df = df.rename(columns=rename_map)
                    # Coerce Count to int if possible
                    if "Count" in df.columns:
                        try:
                            df["Count"] = (
                                df["Count"]
                                .astype(str)
                                .str.replace(",", "", regex=False)
                                .astype(int)
                            )
                        except Exception:  # pragma: no cover
                            pass

                out_path = os.path.join(output_dir, f"{drug_vaccine}_nzsmars_adrs.csv")
                try:
                    df.to_csv(out_path, index=False)
                    _emit("log", message=f"Data saved to: {os.path.abspath(out_path)}")
                except Exception as e:  # pragma: no cover
                    _emit("error", message=f"Failed to save CSV: {e}")

                _emit("done")
                return df
        except Exception as e:  # pragma: no cover
            exceptions.append(e)
            _emit("log", message=f"Attempt {attempt + 1} failed.\n")
            time.sleep(20)
            continue

    _emit(
        "error",
        message=(
            f"All {num_retries} attempt(s) to scrape data for {drug_vaccine} failed. "
            "Please check the following:\n"
            "1. Ensure you have a stable internet connection.\n"
            "2. Verify that 'https://www.medsafe.govt.nz/Projects/B1/ADRSearch.asp' opens correctly in your Chrome browser.\n"
            "3. If these steps do not resolve the issue, please wait a while and retry. \n"
            "If problems persist, contact the developer at https://github.com/rmj3197/SurVigilance/issues "
            "for assistance.\n\n"
        ),
    )

    raise RuntimeError(
        f"All {num_retries} attempt(s) to scrape data for {drug_vaccine} failed. "
        "Please check the following:\n"
        "1. Ensure you have a stable internet connection.\n"
        "2. Verify that 'https://www.medsafe.govt.nz/Projects/B1/ADRSearch.asp' opens correctly in your Chrome browser.\n"
        "3. If these steps do not resolve the issue, please wait a while and retry. \n"
        "If problems persist, contact the developer at https://github.com/rmj3197/SurVigilance/issues "
        "for assistance.\n\n"
    )
