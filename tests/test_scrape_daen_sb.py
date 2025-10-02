"""
Test file to check if the AU DAEN scraping is working
"""

import pandas as pd

from SurVigilance.ui.scrapers import scrape_daen_sb


def test_scrape_daen_real_browser(tmp_path):
    out_dir = tmp_path / "daen_out"
    med = "paracetamol"
    result_df = scrape_daen_sb(medicine=med, output_dir=str(out_dir), headless=True)
    assert isinstance(result_df, pd.DataFrame)
