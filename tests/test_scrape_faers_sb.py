"""
Test file to check if the FAERS scraping is working
"""

import re
from pathlib import Path

import pandas as pd

from SurVigilance.ui.scrapers.scrape_faers import scrape_faers_sb


def test_scrape_faers_sb_real_browser(tmp_path):
    out_dir = tmp_path / "faers_out"
    df = scrape_faers_sb(output_dir=str(out_dir), headless=True)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty, "FAERS scraping should yield at least one (Year, Quarter)"
    assert set(["Year", "Quarter"]).issubset(df.columns)

    sample_quarters = df["Quarter"].astype(str).head(10).tolist()
    assert any(
        re.search(r"\bQ\s*[1-4]\b", q, flags=re.I) or "-" in q for q in sample_quarters
    )

    expected_csv = Path(out_dir) / "faers_available_quarters.csv"
    assert expected_csv.is_file(), "Expected FAERS availability CSV to be written"
