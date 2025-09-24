"""
Scraper for VigiAccess using SeleniumBase.
"""

import os
import warnings
from typing import Any, Callable, Optional

import pandas as pd
from seleniumbase import SB

warnings.filterwarnings("ignore")


def scrape_vigiaccess_sb(
    medicine: str,
    output_dir: str = "data/vigiaccess",
    callback: Optional[Callable[[dict], None]] = None,
    headless: bool = True,
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

    Returns
    --------
    pd.DataFrame: A dataframe with columns ["ADR", "Count"].
    """

    def _emit(event_type: str, **kw: Any) -> None:  # pragma: no cover
        if callback:
            try:
                callback({"type": event_type, **kw})
            except Exception:  # pragma: no cover
                raise

    os.makedirs(output_dir, exist_ok=True)

    collected_lines = []
    MAX_GROUPS = 26

    try:
        with SB(uc=True, headless=headless) as sb:
            _emit("log", message="Parsing vigiaccess.org")
            try:
                url = "https://www.vigiaccess.org/"
                sb.activate_cdp_mode(url)
            except Exception as e:  # pragma: no cover
                _emit("error", message=f"Failed to open site: {e}")
                raise

            try:
                # sb.cdp.click(".level-left")
                sb.cdp.check_if_unchecked('//*[@id="accept-terms-and-conditions"]')
                sb.cdp.click(
                    '//*[@id="elmish-app"]/section/div/div[2]/nav/div[2]/div/button'
                )

                sb.type(".input", medicine)
                sb.click(".button")
            except Exception as e:  # pragma: no cover
                _emit("error", message=f"Search actions failed: {e}")
                raise

            try:
                sb.cdp.wait_for_element_visible("td", timeout=20)
                sb.cdp.click("td")

                sb.cdp.click_if_visible(
                    '//*[@id="elmish-app"]/div/section[1]/div/div/div[1]/div[2]/footer/button'
                )
            except Exception as e:  # pragma: no cover
                _emit("error", message=f"Failed entering results view: {e}")
                raise

            groups_xpath = '//*[@id="elmish-app"]/div/section[2]/div/div[2]/ul/li'
            try:
                sb.cdp.wait_for_element_visible(groups_xpath, timeout=20)
            except Exception as e:  # pragma: no cover
                _emit("error", message=f"Reaction groups list not found: {e}")
                raise

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

                    sb.cdp.gui_hover_element(title_span)
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

                    sb.cdp.gui_hover_element(title_span)
                    sb.cdp.click(title_span)

                except Exception as e:  # pragma: no cover
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
                raise

        df = pd.DataFrame(data_map.items(), columns=["PT", "Count"]).reset_index(
            drop=True
        )

        output_csv_path = os.path.join(output_dir, f"{medicine}_vigiaccess_adrs.csv")
        try:
            df.to_csv(output_csv_path, index=False)
            _emit("log", message=f"Data saved to: {output_csv_path}")
        except Exception as e:  # pragma: no cover
            _emit("error", message=f"Failed to save CSV: {e}")

        _emit("done")
        return df

    except Exception as e:  # pragma: no cover
        _emit("error", message=f"Fatal scraping error: {e}")
        raise
