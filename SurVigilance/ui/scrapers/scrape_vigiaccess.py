"""
Scraper for VigiAccess using SeleniumBase.
"""

import os
import time
import warnings
from collections.abc import Callable
from typing import Any

import pandas as pd
from seleniumbase import SB

warnings.filterwarnings("ignore")


def scrape_vigiaccess_sb(
    medicine: str,
    output_dir: str = "data/vigiaccess",
    callback: Callable[[dict], None] | None = None,
    headless: bool = True,
    num_retries: int = 5,
) -> pd.DataFrame:
    """
    Scrapes the reported MedDRA Preferred Terms and counts for a given medicine from VigiAccess.

    Parameters
    -----------
    medicine : str
        Drug/medicine name to search.

    output_dir : str
        Directory to save CSV (default "data/vigiaccess").

    callback : callable
        Callable to receive UI/status events, called with a dict.
        This is essential to show progress to user.

    headless: bool
        Run the browser in headless mode (default True).

    num_retries: int
        Number of retries for data scraping after which error is thrown (default 5).

    Returns
    --------
    pd.DataFrame: A dataframe with columns ["PT", "Count"].
    """

    def extract_clean_text(text_list: list[str]) -> list[str]:  # pragma: no cover
        cleaned = []
        for text in text_list:
            clean_str = "".join(
                char for char in text if char.isalnum() or char.isspace()
            )
            cleaned.append(clean_str.strip().lower())
        return cleaned

    def _emit(event_type: str, **kw: Any) -> None:  # pragma: no cover
        if callback:
            try:
                callback({"type": event_type, **kw})
            except Exception:  # pragma: no cover
                raise  # pragma: no cover

    os.makedirs(output_dir, exist_ok=True)

    collected_lines = []
    MAX_GROUPS = 26

    exceptions = []
    for attempt in range(num_retries):
        try:
            if attempt > 0:
                _emit("log", message=f"Retrying... ({attempt + 1}/{num_retries})\n")

            with SB(uc=True, headless=headless) as sb:
                _emit(
                    "log", message=f"Parsing vigiaccess.org (Attempt {attempt + 1})\n"
                )
                try:
                    url = "https://www.vigiaccess.org/"
                    sb.activate_cdp_mode(url)
                    sb.sleep(0.5)
                except Exception as e:  # pragma: no cover
                    exceptions.append(e)
                    _emit("error", message=f"Failed to open site: {e}")
                    raise  # pragma: no cover

                try:
                    # sb.cdp.click(".level-left")
                    sb.cdp.scroll_into_view('//*[@id="elmish-app"]/footer')
                    if sb.is_element_visible(
                        '//*[@id="elmish-app"]/section/div/div[2]/nav/div[1]/div'
                    ):
                        sb.cdp.click(
                            '//*[@id="elmish-app"]/section/div/div[2]/nav/div[1]/div/label'
                        )
                    sb.sleep(0.5)
                    sb.cdp.click(
                        '//*[@id="elmish-app"]/section/div/div[2]/nav/div[2]/div/button'
                    )
                    sb.sleep(0.5)

                    if sb.is_element_visible(".input"):
                        sb.type(".input", medicine)
                    sb.sleep(0.5)
                    sb.click(".button")
                    sb.sleep(1)
                except Exception as e:  # pragma: no cover
                    exceptions.append(e)
                    _emit("log", message=f"Search actions failed: {e}")
                    raise  # pragma: no cover

                try:
                    sb.cdp.wait_for_element_visible("td", timeout=20)
                    rows = sb.find_elements("tr")
                    row_text_list = [row.text for row in rows]
                    results = extract_clean_text(row_text_list)
                    try:
                        index = results.index(medicine.lower())
                    except ValueError:
                        index = 0  # Default to the first index if no match is found

                    sb.cdp.scroll_into_view(
                        f'//*[@id="elmish-app"]/div/section[1]/div/div/div[1]/div[2]/section/table/tbody/tr[{index + 1}]/td'
                    )
                    sb.cdp.click(
                        f'//*[@id="elmish-app"]/div/section[1]/div/div/div[1]/div[2]/section/table/tbody/tr[{index + 1}]/td'
                    )

                    sb.sleep(1.5)

                    sb.cdp.click_if_visible(
                        '//*[@id="elmish-app"]/div/section[1]/div/div/div[1]/div[2]/footer/button'
                    )
                    sb.sleep(1.5)
                except Exception as e:  # pragma: no cover
                    exceptions.append(e)
                    _emit("error", message=f"Failed entering results view: {e}")
                    raise  # pragma: no cover

                groups_xpath = '//*[@id="elmish-app"]/div/section[2]/div/div[2]/ul/li'
                try:
                    sb.cdp.wait_for_element_visible(groups_xpath, timeout=20)
                    sb.sleep(0.5)
                except Exception as e:  # pragma: no cover
                    exceptions.append(e)
                    _emit("error", message=f"Reaction groups list not found: {e}")
                    raise  # pragma: no cover

                try:
                    group_items = sb.cdp.find_elements(groups_xpath)
                    total_groups = len(group_items)
                    if total_groups == 0:
                        _emit("log", message="No reaction groups found.")
                except Exception:  # pragma: no cover
                    total_groups = 0

                for i in range(1, MAX_GROUPS + 1):
                    try:
                        title_span = f'//*[@id="elmish-app"]/div/section[2]/div/div[2]/ul/li[{i}]/span[1]'
                        expander_span = f'//*[@id="elmish-app"]/div/section[2]/div/div[2]/ul/li[{i}]/span[2]'

                        if not sb.cdp.is_element_present(title_span):
                            continue

                        # sb.cdp.gui_hover_element(title_span)
                        sb.cdp.click(expander_span)

                        sb.sleep(0.5)

                        while sb.cdp.is_element_visible(
                            'xpath=//*[contains(text(), "Load more...")]'
                        ):
                            sb.cdp.click('//*[contains(text(), "Load more...")]')
                            sb.sleep(0.5)

                        entries_xpath = (
                            '//*[@id="elmish-app"]/div/section[2]/div/div[2]/ul/ul/li'
                        )
                        if sb.cdp.is_element_visible(entries_xpath):
                            entries = sb.cdp.find_elements(entries_xpath)
                            for el in entries:
                                txt = (el.text or "").strip()
                                if txt:
                                    collected_lines.append(txt)

                        # sb.cdp.gui_hover_element(title_span)
                        sb.cdp.click(title_span)
                        sb.sleep(0.5)

                    except Exception as e:  # pragma: no cover
                        exceptions.append(e)
                        _emit("log", message=f"Group {i}: skipping due to error: {e}")

                    _emit("progress", delta=100.0 / MAX_GROUPS)

            data_map = {}
            for raw in collected_lines:
                line = raw.encode("ascii", "ignore").decode().strip()
                if not line or "(" not in line or ")" not in line:
                    continue
                try:
                    adr = line.rsplit("(", 1)[0].strip()
                    count = int(line.rsplit("(", 1)[1].split(")")[0])
                    data_map[adr] = count
                except Exception:  # pragma: no cover
                    raise  # pragma: no cover

            df = pd.DataFrame(data_map.items(), columns=["PT", "Count"]).reset_index(
                drop=True
            )

            output_csv_path = os.path.join(
                output_dir, f"{medicine}_vigiaccess_adrs.csv"
            )
            try:
                df.to_csv(output_csv_path, index=False)
                _emit(
                    "log", message=f"Data saved to: {os.path.abspath(output_csv_path)}"
                )
            except Exception as e:  # pragma: no cover
                _emit("error", message=f"Failed to save CSV: {e}")

            _emit("done")
            return df

            exceptions.append(e)
            _emit("log", message=f"Attempt {attempt + 1} failed.\n")
            time.sleep(20)
            continue

    _emit(
        "error",
        message=(
            f"All {num_retries} attempt(s) to scrape data for {medicine} failed. "
            "Please check the following:\n"
            "1. Ensure you have a stable internet connection.\n"
            "2. Verify that 'https://www.vigiaccess.org/' opens correctly in your Chrome browser.\n"
            "3. If these steps do not resolve the issue, please wait a while and retry. \n"
            "If problems persist, contact the developer at https://github.com/rmj3197/SurVigilance/issues "
            "for assistance.\n\n"
        ),
    )

    raise RuntimeError(
        f"All {num_retries} attempt(s) to scrape data for {medicine} failed. "
        "Please check the following:\n"
        "1. Ensure you have a stable internet connection.\n"
        "2. Verify that 'https://www.vigiaccess.org/' opens correctly in your Chrome browser.\n"
        "3. If these steps do not resolve the issue, please wait a while and retry. \n"
        "If problems persist, contact the developer at https://github.com/rmj3197/SurVigilance/issues "
        "for assistance.\n\n"
    )
