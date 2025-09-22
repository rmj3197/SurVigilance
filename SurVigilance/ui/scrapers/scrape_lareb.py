"""
Scraper for LAREB using SeleniumBase.
"""

from seleniumbase import SB

import os
import warnings
from typing import Any, Callable, Optional
import pandas as pd

warnings.filterwarnings("ignore")


def scrape_lareb_sb(
    medicine: str,
    output_dir: str = "data/lareb",
    callback: Optional[Callable[[dict], None]] = None,
    headless: bool = True,
) -> pd.DataFrame:
    """
    Scrapes Preferred Terms and counts for a given medicine.

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

    Returns:
        pd.DataFrame: A dataframe with columns ["PT", "Count"].
    """

    def _emit(event_type: str, **kw: Any) -> None:  # pragma: no cover
        if callback:
            try:
                callback({"type": event_type, **kw})
            except Exception:  # pragma: no cover
                pass

    os.makedirs(output_dir, exist_ok=True)

    try:
        with SB(uc=True, headless=headless) as sb:
            _emit("log", message="Parsing lareb.nl")
            try:
                sb.open("https://www.lareb.nl/en")
            except Exception as e:  # pragma: no cover
                _emit("error", message=f"Failed to open site: {e}")
                raise

            try:
                if sb.is_element_present("input.input-search"):
                    sb.type("input.input-search", medicine)
                else:
                    sb.type('[class*="input-search"]', medicine)
            except Exception as e:  # pragma: no cover
                _emit("error", message=f"Error enountered while searching: {e}")
                raise

            try:
                sb.wait_for_element_visible(
                    'div.autocomplete-suggestion[data-index="0"]', timeout=30
                )
            except Exception as e:  # pragma: no cover
                _emit(
                    "error",
                    message=(
                        "No autocomplete suggestion appeared - the drug may not exist "
                        f"on Lareb: {medicine}. Details: {e}"
                    ),
                )

            if sb.is_element_present('div.autocomplete-suggestion[data-index="0"]'):
                sb.click('div.autocomplete-suggestion[data-index="0"]')

            try:
                sb.click("#search")
            except Exception as e:  # pragma: no cover
                _emit("error", message=f"Couldn't click search button: {e}")
                raise

            try:
                sb.wait_for_element_visible("#registrationsTab", timeout=25)
            except Exception as e:  # pragma: no cover
                _emit("error", message=f"Results area didn't load in time: {e}")
                raise

            try:
                rows = sb.find_elements('//*[@id="registrationsTab"]/table[2]/tbody/tr')
            except Exception as e:  # pragma: no cover
                _emit("error", message=f"Couldn't find table: {e}")
                raise

            expanded_texts = []
            total_rows = len(rows) if rows else 0

            for i, row in enumerate(rows, start=1):
                try:
                    sb.find_element(
                        f'//*[@id="registrationsTab"]/table[2]/tbody/tr[{i}]/td/div[1]'
                    ).click()

                    sb.sleep(1)
                    div2 = sb.find_element(
                        f'//*[@id="registrationsTab"]/table[2]/tbody/tr[{i}]/td/div[2]'
                    )

                    for _ in range(10):
                        if div2.is_displayed() and div2.text.strip():
                            break
                        sb.sleep(0.1)

                    expanded_texts.append(div2.text.strip())
                    sb.sleep(0.2)

                    if total_rows:
                        _emit("progress", delta=100.0 / total_rows)

                except Exception as e:  # pragma: no cover
                    msg = f"Row {i}: expand failed: {e}"
                    _emit("error", message=msg)
                    expanded_texts.append("")

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

            output_csv_path = os.path.join(output_dir, f"{medicine}_lareb_adrs.csv")
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
