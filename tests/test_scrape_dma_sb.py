"""
Test file to check if the DK DMA scraping is working
"""

from pathlib import Path

import pandas as pd

from SurVigilance.ui.scrapers.scrape_dma import scrape_dma_sb


def test_scrape_dma_real_browser(tmp_path):
    out_dir = tmp_path / "dma_out"
    med = "atorvastatin"
    df = scrape_dma_sb(medicine=med, output_dir=str(out_dir), headless=True)

    assert isinstance(df, pd.DataFrame)
    assert set(["PT", "Count"]).issubset(set(df.columns))

    expected_csv = Path(out_dir) / f"{med}_dma_adrs.csv"
    assert expected_csv.is_file(), "Expected DMA CSV to be written"
