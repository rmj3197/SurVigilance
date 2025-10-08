"""
Test file to check if the NZ MEDSAFE SMARS scraping is working
"""

from pathlib import Path

import pandas as pd

from SurVigilance.ui.scrapers import scrape_medsafe_sb


def test_scrape_nzsmars_real_browser(tmp_path):
    out_dir = tmp_path / "nzsmars_out"
    med = "paracetamol"
    df = scrape_medsafe_sb(
        searching_for="medicine",
        drug_vaccine=med,
        output_dir=str(out_dir),
        headless=True,
    )

    assert isinstance(df, pd.DataFrame)
    assert set(["SOC", "PT", "Count"]).issubset(set(df.columns))

    expected_csv = Path(out_dir) / f"{med}_nzsmars_adrs.csv"
    assert expected_csv.is_file(), "Expected NZSMARS CSV to be written"
