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
    csv_path = Path(out_dir) / f"{med}_vigiaccess_adrs.csv"

    # Basic checks
    assert isinstance(df, pd.DataFrame)
    assert {"PT", "Count"}.issubset(df.columns)
    assert df.shape[0] > 0

    # Count column type and validity
    assert pd.api.types.is_integer_dtype(df["Count"])
    assert (df["Count"] >= 0).all()

    # CSV persisted and matches dataframe
    assert csv_path.is_file(), "Expected VigiAccess CSV to be written"
    csv_df = pd.read_csv(csv_path)
    pd.testing.assert_frame_equal(
        df.reset_index(drop=True), csv_df.reset_index(drop=True)
    )
