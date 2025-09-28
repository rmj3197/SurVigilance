"""
Test file to check if the AU DAEN scraping is working
"""

from pathlib import Path

from SurVigilance.ui.scrapers import scrape_daen_sb


def test_scrape_daen_real_browser(tmp_path):
    out_dir = tmp_path / "daen_out"
    med = "paracetamol"
    result_path = scrape_daen_sb(medicine=med, output_dir=str(out_dir), headless=True)

    p = Path(result_path)
    assert p.is_file()
    assert p.parent == out_dir

    files = [f for f in out_dir.iterdir() if f.is_file() and not f.name.startswith(".")]
    assert files, "Expected at least one downloaded file in the output directory"

    expected_prefix = f"{med}_daen_export".lower()
    assert any(f.name.lower().startswith(expected_prefix) for f in files)
    assert p.name.lower().startswith(expected_prefix)
