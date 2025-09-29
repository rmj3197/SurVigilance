"""
Scraper for Denmark DMA interactive ADR overviews using SeleniumBase.
"""

import os
from typing import Any, Callable, Optional

import pandas as pd
from bs4 import BeautifulSoup
from seleniumbase import SB


def _group_label(name: str) -> Optional[str]:  # pragma: no cover
    name = (name or "").strip().lower()
    second = name[1]
    if "a" <= second <= "d":
        return "a-d"
    elif "e" <= second <= "h":
        return "e-h"
    elif "i" <= second <= "l":
        return "i-l"
    elif "m" <= second <= "p":
        return "m-p"
    elif "q" <= second <= "u":
        return "q-u"
    else:
        return "v-z"


def scrape_dma_sb(
    medicine: str,
    output_dir: str = "data/dma",
    callback: Optional[Callable[[dict], None]] = None,
    headless: bool = True,
) -> pd.DataFrame:
    """
    Scrapes the reported MedDRA Preferred Terms and counts for a given medicine
    from the Danish Medicines Agency database.

    Parameters
    -----------
    medicine: str
        Drug/medicine name to search.

    output_dir: str
        Directory to save CSV (default "data/dma").

    callback : callable
        Callable to receive UI/status events, called with a dict.
        This is essential to show progress to user.

    headless: bool
        Run the browser in headless mode (default True).

    Returns
    --------
    A dataframe with columns ['PT', 'Count'].
    """

    def _emit(event_type: str, **kw: Any) -> None:
        if callback:
            try:
                callback({"type": event_type, **kw})
            except Exception:
                raise

    med = (medicine or "").strip()
    if not med:
        _emit("error", message="Medicine is required for DMA scrape")
        raise ValueError("medicine is required")

    os.makedirs(output_dir, exist_ok=True)

    steps_total = 8
    delta = 100.0 / float(steps_total)
    progress_steps = 0

    def step():  # pragma: no cover
        nonlocal progress_steps
        progress_steps += 1
        _emit("progress", delta=delta)

    try:
        with SB(uc=True, headless=headless) as sb:
            url = "https://laegemiddelstyrelsen.dk/en/sideeffects/side-effects-of-medicines/interactive-adverse-drug-reaction-overviews/"
            _emit("log", message="Opening laegemiddelstyrelsen.dk (DMA)")
            sb.activate_cdp_mode(url)

            sb.sleep(1)
            sb.click('//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]')
            sb.sleep(1)

            try:
                sb.click('//*[@id="main-content"]/div/div/div[2]/div[1]/form/div/input')
                sb.sleep(1)
            except Exception:  # pragma: no cover
                pass
            step()

            try:
                first_char = med[0].upper()
                if not ("A" <= first_char <= "Z"):
                    raise ValueError("Unsupported starting character for medicine")
                alphabet_index = ord(first_char) - ord("A") + 1
                sb.click(
                    f'//*[@id="main-content"]/div/div/div[2]/div[1]/section/div[2]/div[1]/a[{alphabet_index}]'
                )
                sb.sleep(1)
            except Exception as e:  # pragma: no cover
                _emit("error", message=f"Failed selecting alphabet: {e}")
                raise
            step()

            try:
                group = _group_label(med)
                if group:
                    sb.click(f'a[href="?letter={med[0].upper()}&subletter={group}"]')
                    sb.sleep(1)
            except Exception as e:  # pragma: no cover
                _emit("log", message=f"Skipping subgroup selection: {e}")
            step()

            drugs_table_xpath = (
                '//*[@id="main-content"]/div/div/div[2]/div[1]/section/table'
            )
            sb.wait_for_element_visible(drugs_table_xpath, timeout=30)
            sb.sleep(2)
            table_text = sb.cdp.get_text(drugs_table_xpath) or ""
            if med.lower() not in table_text.lower():
                _emit("error", message=f"Drug '{med}' not found in DMA list")
                raise RuntimeError("Drug not found in DMA list")

            sb.click(
                f"//*[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = '{med.lower()}']"
            )
            sb.sleep(5)
            step()

            tabs = sb.cdp.get_tabs()
            for tab in tabs:
                if (
                    tab.url
                ):  # the first tab needs to be closed else it is creating issues.
                    sb.cdp.switch_to_tab(tab)
                    sb.cdp.close_active_tab()
                    break
            else:
                print("No tab without a URL was found.")

            sb.wait_for_ready_state_complete()
            step()

            outer_iframe = (
                'iframe[src*="/upload/dap/dap.html?drug=./DK_EXTERNAL/NONCOMBINED/"]'
            )
            sb.wait_for_element_visible(outer_iframe, timeout=30)
            if sb.is_element_present(outer_iframe):
                with sb.frame_switch(outer_iframe):
                    try:
                        if sb.is_element_present("#button#soc_expand_all_button"):
                            sb.scroll_to("button#soc_expand_all_button")
                            sb.click_if_visible("button#soc_expand_all_button")
                    except Exception as e:  # pragma: no cover
                        _emit("log", message=f"Expand-all click issue: {e}")
                    step()

                    if sb.is_element_present("#meddra_table"):
                        table_el = sb.find_element("#meddra_table")
                        table_html = table_el.get_attribute("outerHTML")

                        soup = BeautifulSoup(table_html, "html.parser")
                        table = soup.find("table", {"id": "meddra_table"})
                        df = pd.read_html(str(table))[0]

                        df.columns = [str(c).strip() for c in df.columns]
                        df = df.dropna(axis=1, how="all")

                        if df.shape[1] >= 2:
                            pt_col = df.columns[0]
                            count_col = df.columns[-2]
                            df = df.loc[:, [pt_col, count_col]]
                            df.columns = ["PT", "Count"]
                            df = df[df["PT"].astype(str).str.contains("\\+")]
                            df["PT"] = (
                                df["PT"]
                                .astype(str)
                                .str.replace("+", "", regex=False)
                                .str.strip()
                            )
                        sb.sleep(5)
                        step()

                        df = df.reset_index(drop=True)

                        out_path = os.path.join(output_dir, f"{med}_dma_adrs.csv")
                        try:
                            df.to_csv(out_path, index=False)
                            _emit(
                                "log",
                                message=f"Data saved to: {os.path.abspath(out_path)}",
                            )
                        except Exception as e:  # pragma: no cover
                            _emit("error", message=f"Failed to save CSV: {e}")
                            raise
                        sb.sleep(5)
                        step()

                        _emit("done")
                        return df

    except Exception:  # pragma: no cover
        raise
