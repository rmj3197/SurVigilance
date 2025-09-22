"""
Test file to test if the download_file function using requests module works
"""

import os

from SurVigilance.ui.scrapers import download_file


def test_download_file_saves_content(tmp_path):
    url = "https://fis.fda.gov/content/Exports/aers_ascii_2005q1.zip"
    out_dir = tmp_path / "faers"

    path = download_file(url=url, download_dir=str(out_dir))
    assert os.path.isfile(path), "Downloaded file path should exist"
    assert os.path.getsize(path) > 0, "Downloaded file should not be empty"
