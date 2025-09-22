"""
Test file to check if the VigiAccess scraping is working
"""

from pathlib import Path

import pandas as pd

from SurVigilance.ui.scrapers.scrape_vigiaccess import scrape_vigiaccess_sb


def test_scrape_vigiaccess_real_browser(tmp_path):
    out_dir = tmp_path / "vigi_out"
    med = "aspirin"
    df = scrape_vigiaccess_sb(medicine=med, output_dir=str(out_dir), headless=True)

    assert isinstance(df, pd.DataFrame)
    # Site content changes, but should usually have some rows
    assert set(["PT", "Count"]).issubset(df.columns)

    # CSV persisted
    expected_csv = Path(out_dir) / f"{med}_vigiaccess_adrs.csv"
    assert expected_csv.is_file(), "Expected VigiAccess CSV to be written"
