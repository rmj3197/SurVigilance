import pytest

from SurVigilance.ui.scrapers.faers_links import faers_ascii_url


def test_faers_ascii_url_modern_years():
    # Years >= 2013 use the FAERS prefix
    assert (
        faers_ascii_url(2013, 1)
        == "https://fis.fda.gov/content/Exports/faers_ascii_2013q1.zip"
    )
    assert (
        faers_ascii_url(2020, 4)
        == "https://fis.fda.gov/content/Exports/faers_ascii_2020q4.zip"
    )


def test_faers_ascii_url_2012_transition():
    # Q4 2012 uses FAERS; earlier quarters use AERS
    assert (
        faers_ascii_url(2012, 4)
        == "https://fis.fda.gov/content/Exports/faers_ascii_2012q4.zip"
    )
    assert (
        faers_ascii_url(2012, 3)
        == "https://fis.fda.gov/content/Exports/aers_ascii_2012q3.zip"
    )


def test_faers_ascii_url_older_years():
    assert (
        faers_ascii_url(2004, 4)
        == "https://fis.fda.gov/content/Exports/aers_ascii_2004q4.zip"
    )


def test_faers_ascii_url_rejects_invalid_quarter():
    invalid_quarters = [0, 5, -1, 999]
    for bad_q in invalid_quarters:
        with pytest.raises(ValueError):
            faers_ascii_url(2020, bad_q)
