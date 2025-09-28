"""
Downloader for VAERS yearly ZIPs.
"""

import os
import shutil
from typing import Any, Callable, Optional

import requests
from seleniumbase import SB


def vaers_intermediate_url(year: int) -> str:  # pragma: no cover
    return f"https://vaers.hhs.gov/eSubDownload/index.jsp?fn={year}VAERSData.zip"


def download_vaers_zip_sb(
    year: int,
    download_dir: str = "data/vaers",
    timeout: int = 600,
    callback: Optional[Callable[[dict], None]] = None,
    headless: bool = False,
    fallback_wait: int = 120,
) -> str:  # pragma: no cover
    """
    Navigate the VAERS intermediate page, solve CAPTCHA, and download the ZIP.

    Parameters
    -----------
    year: int
        Year of the VAERS data

    download_dir: str
        Directory to save the ZIP (default "data/vaers")

    timeout: int
        Max seconds for the file download request (default 600s or 10 mins).

    callback: callable, optional
        Callable to receive UI/status events, called with a dict.
        This is essential to show progress to user.

    headless: bool
        Run the browser in headless mode (default True).

    fallback_wait: Seconds to wait for a browser-initiated download to
        complete in browser default folder if the "Download File" button
        isn't found in time.

    Returns
    --------
    The full path of the downloaded ZIP file.
    """

    def _emit(event_type: str, **kw: Any) -> None:  # pragma: no cover
        if callback:
            try:
                callback({"type": event_type, **kw})
            except Exception:  # pragma: no cover
                raise

    os.makedirs(download_dir, exist_ok=True)

    url = vaers_intermediate_url(int(year))
    _emit("log", message=f"Opening VAERS page for {year}")

    with SB(uc=True, headless=headless) as sb:
        sb.activate_cdp_mode(url)

        try:
            sb.uc_gui_click_captcha()
            _emit("log", message="Attempted CAPTCHA solve.")
        except Exception:  # pragma: no cover
            raise

        download_xpath = "//*[self::a or self::button][contains(., 'Download File')]"
        try:
            sb.cdp.wait_for_element_visible(download_xpath, timeout=60)
        except Exception:  # pragma: no cover

            try:
                stray_dir = os.path.join(os.getcwd(), "downloaded_files")
                stray_name = f"{year}VAERSData.zip"
                stray_path = os.path.join(stray_dir, stray_name)
                partial_path = stray_path + ".crdownload"
                _emit(
                    "log",
                    message=(
                        "'Download File' control not detected in 60s. "
                        f"Waiting up to {fallback_wait}s for a browser-initiated download."
                    ),
                )

                import time

                end_time = time.time() + max(0, int(fallback_wait))
                while time.time() < end_time:
                    if os.path.isfile(stray_path) and not os.path.isfile(partial_path):
                        os.makedirs(download_dir, exist_ok=True)
                        target_path = os.path.join(download_dir, stray_name)
                        try:
                            if os.path.isfile(target_path):
                                os.remove(stray_path)
                            else:
                                shutil.move(stray_path, target_path)
                        except Exception:  # pragma: no cover
                            raise
                        if os.path.isfile(target_path):
                            _emit(
                                "download_complete",
                                path=target_path,
                                filename=stray_name,
                            )
                            return target_path
                    time.sleep(1)
            except Exception:  # pragma: no cover
                raise

        try:
            elem = sb.cdp.find_element(download_xpath)
        except Exception:  # pragma: no cover
            elem = None
        href = None
        if elem is not None:
            try:
                href = elem.get_attribute("href")
            except Exception:  # pragma: no cover
                href = None

        if not href and elem is not None:
            try:
                sb.cdp.click(download_xpath)
                sb.sleep(1.0)
                href = sb.cdp.get_current_url()
            except Exception:  # pragma: no cover
                href = None

        if not href:
            _emit("error", message="Unable to determine download URL after clicking.")
            raise RuntimeError("Could not resolve direct download URL for VAERS zip")

        sess = requests.Session()
        try:
            ua = sb.cdp.execute_script("return navigator.userAgent") or ""
            if isinstance(ua, str) and ua:
                sess.headers.update({"User-Agent": ua})
        except Exception:  # pragma: no cover
            raise

        try:
            for c in sb.cdp.driver.get_cookies():
                try:
                    sess.cookies.set(
                        c.get("name"),
                        c.get("value"),
                        domain=c.get("domain"),
                        path=c.get("path"),
                    )
                except Exception:  # pragma: no cover
                    raise
        except Exception:  # pragma: no cover
            raise

        _emit("log", message="Starting VAERS data download")
        with sess.get(href, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            filename = f"{year}VAERSData.zip"
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
                "download_start",
                url=href,
                filename=filename,
                total_bytes=total_bytes,
            )

            downloaded = 0
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=18192):
                    if not chunk:
                        continue
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_bytes > 0:
                        try:
                            percent = int(downloaded * 100 / max(1, total_bytes))
                            _emit(
                                "download_progress",
                                downloaded_bytes=downloaded,
                                total_bytes=total_bytes,
                                percent=percent,
                            )
                        except Exception:  # pragma: no cover
                            raise

        _emit("download_complete", path=file_path, filename=filename)

        try:
            stray_dir = os.path.join(os.getcwd(), "downloaded_files")
            stray_name = f"{year}VAERSData.zip"
            stray_path = os.path.join(stray_dir, stray_name)
            target_path = os.path.join(download_dir, stray_name)
            if os.path.isfile(stray_path):

                if os.path.isfile(target_path):
                    try:
                        os.remove(stray_path)
                    except Exception:  # pragma: no cover
                        raise
                else:
                    os.makedirs(download_dir, exist_ok=True)
                    shutil.move(stray_path, target_path)

                    file_path = target_path
        except Exception:  # pragma: no cover
            raise

        return file_path
