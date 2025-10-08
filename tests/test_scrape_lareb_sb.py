"""
Test file to check if the Lareb scraping is working
"""

from pathlib import Path

import pandas as pd

from SurVigilance.ui.scrapers import scrape_lareb_sb


def test_scrape_lareb_real_browser(tmp_path):
    out_dir = tmp_path / "lareb_out"
    med = "paracetamol"
    df = scrape_lareb_sb(medicine=med, output_dir=str(out_dir), headless=True)

    assert isinstance(df, pd.DataFrame)
    # Columns should be present even if no results are found
    assert set(["PT", "Count"]).issubset(set(df.columns))

    # CSV persisted
    expected_csv = Path(out_dir) / f"{med}_lareb_adrs.csv"
    assert expected_csv.is_file(), "Expected Lareb CSV to be written"
